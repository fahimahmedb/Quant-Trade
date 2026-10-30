"""Fail-closed policy fence around the generic Codex orchestration adapter."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .codex_adapter import (
    CodexOrchestrationWorker,
    GitHubIssueClient,
    OrchestrationState,
)


_ALLOWED_ACTIONS_BY_EVENT: dict[str, set[str]] = {
    "STALE_HEAD": {"ADOPT_CURRENT_HEAD", "PARK"},
    "CI_FAIL": {"CONTINUE", "PARK"},
    "QUALIFIED_RESULT": {"DONE", "CONTINUE", "PARK"},
    "REVIEW_REQUEST_CHANGES": {"CONTINUE", "PARK"},
    "REVIEW_UNKNOWN_EXHAUSTED": {"CONTINUE", "PARK"},
}


class FencedGitHubIssueClient(GitHubIssueClient):
    """GitHub client that proves the posting principal matches the configured actor."""

    def __init__(self, repository: str, issue_number: int, token: str,
                 expected_actor: str, api_url: str = "https://api.github.com"):
        super().__init__(repository, issue_number, token, api_url=api_url)
        actor = expected_actor.strip()
        if not actor:
            raise ValueError("expected_actor is required")
        self.expected_actor = actor

    def post_comment(self, body: str) -> dict[str, Any]:
        item = super().post_comment(body)
        actual = str(item.get("author") or "")
        if actual != self.expected_actor:
            raise RuntimeError(
                "GitHub posting identity mismatch: "
                f"configured={self.expected_actor!r} observed={actual!r}"
            )
        return item


class PolicyFencedCodexOrchestrationWorker(CodexOrchestrationWorker):
    """Restrict model decisions and trusted control markers to machine policy."""

    def __init__(self, *args, trusted_orchestrator_actor: str, **kwargs):
        super().__init__(*args, **kwargs)
        actor = trusted_orchestrator_actor.strip()
        if not actor:
            raise ValueError("trusted_orchestrator_actor is required")
        self.trusted_orchestrator_actor = actor

    def _has_marker(self, kind: str, comments: list[dict[str, Any]],
                    expected: dict[str, Any]) -> bool:
        # Dispatch/review-request markers are control-plane messages.  A third
        # party must not be able to pre-seed one and suppress the real wake.
        if kind in {"dispatch", "review_request"}:
            comments = [
                comment for comment in comments
                if str(comment.get("author") or "") == self.trusted_orchestrator_actor
            ]
        return super()._has_marker(kind, comments, expected)

    def _decision(self, event: str, state: OrchestrationState,
                  evidence: dict[str, Any]) -> dict[str, Any]:
        allowed = _ALLOWED_ACTIONS_BY_EVENT.get(event, {"PARK"})
        context = {
            "event": event,
            "state": asdict(state),
            "evidence": evidence,
            "allowed_actions": sorted(allowed),
            "hard_boundaries": [
                "real capital/live trading",
                "irreversible scientific unblinding",
                "frozen protocol/denominator/endpoint/lineage redefinition",
                "irreversible external mutation outside the authority envelope",
            ],
        }
        decision = self.decide(context)
        if not isinstance(decision, dict):
            raise ValueError("decision function must return a JSON-like object")
        state.last_decision = decision
        action = str(decision.get("action") or "").upper()
        if action not in allowed:
            # Do not let model output widen the machine policy.  Parking is a
            # bounded, reversible fail-closed terminal for Phase 1.
            return {
                "action": "PARK",
                "reason": (
                    f"machine policy rejected action {action or '<empty>'} "
                    f"for event {event}; allowed={','.join(sorted(allowed))}"
                ),
                "rejected_action": action,
            }
        return decision
