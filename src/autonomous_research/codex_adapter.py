"""Durable, model-neutral bridge between ResearchCampaign and Codex via GitHub."""

from __future__ import annotations

import errno
import fcntl
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Protocol

from .runtime import ResearchTask

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_MARKER_RE = {
    "dispatch": re.compile(r"<!--\s*QUANT_CODEX_DISPATCH\s+(\{.*?\})\s*-->", re.DOTALL),
    "result": re.compile(r"<!--\s*QUANT_CODEX_RESULT\s+(\{.*?\})\s*-->", re.DOTALL),
    "review_request": re.compile(r"<!--\s*QUANT_CODEX_REVIEW_REQUEST\s+(\{.*?\})\s*-->", re.DOTALL),
    "review": re.compile(r"<!--\s*QUANT_CODEX_REVIEW\s+(\{.*?\})\s*-->", re.DOTALL),
}
_TERMINAL = {"DONE", "HARD_BOUNDARY", "PARKED_NO_DELTA", "BLOCKED_EXTERNAL"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _append_receipt(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(_canonical_json(value) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _marker(kind: str, payload: dict[str, Any]) -> str:
    label = {
        "dispatch": "QUANT_CODEX_DISPATCH",
        "result": "QUANT_CODEX_RESULT",
        "review_request": "QUANT_CODEX_REVIEW_REQUEST",
        "review": "QUANT_CODEX_REVIEW",
    }[kind]
    return f"<!-- {label} {_canonical_json(payload)} -->"


def _parse_markers(kind: str, comments: list[dict[str, Any]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Parse only the canonical, first-line control envelope.

    Human-facing text below that envelope is untrusted data.  In particular, it
    may contain prompts or examples which look exactly like control markers.
    """
    parsed: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for comment in comments:
        body = str(comment.get("body") or "")
        first_line = body.splitlines()[0].strip() if body.splitlines() else ""
        match = _MARKER_RE[kind].fullmatch(first_line)
        if match is None:
            continue
        try:
            payload = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            parsed.append((comment, payload))
    return parsed


def _dispatch_id(task_id: str, expected_head_sha: str, attempt: int) -> str:
    material = f"{task_id}\0{expected_head_sha}\0{attempt}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


@dataclass
class OrchestrationConfig:
    root: Path
    repository: str
    issue_number: int
    target_branch: str
    builder_mention: str = "@codex"
    reviewer_mention: str = "@codex"
    poll_seconds: float = 15.0
    max_poll_seconds: float = 120.0
    max_no_delta_cycles: int = 240
    max_dispatch_attempts: int = 12
    max_review_attempts: int = 3
    allowed_result_authors: tuple[str, ...] = ("chatgpt-codex-connector[bot]",)
    allowed_review_authors: tuple[str, ...] = ("chatgpt-codex-connector[bot]",)

    @property
    def state_dir(self) -> Path:
        return self.root / "runtime" / "codex_orchestration"


@dataclass
class OrchestrationState:
    task_id: str
    expected_head_sha: str
    repository: str = ""
    issue_number: int = 0
    target_branch: str = ""
    current_prompt: str = ""
    attempt: int = 1
    dispatch_id: str = ""
    status: str = "READY"
    result_sha: str | None = None
    review_attempt: int = 0
    no_delta_cycles: int = 0
    last_observation_digest: str | None = None
    last_decision: dict[str, Any] | None = None
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)

    @classmethod
    def load_or_create(cls, path: Path, task_id: str, expected_head_sha: str,
                       current_prompt: str, repository: str, issue_number: int,
                       target_branch: str) -> "OrchestrationState":
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            subject = (repository, int(issue_number), target_branch)
            persisted_subject = (
                payload.get("repository"), payload.get("issue_number"), payload.get("target_branch"))
            if persisted_subject != subject:
                raise ValueError(
                    "durable orchestration state GitHub subject mismatch; "
                    "explicit reconciliation or a new task/state namespace is required")
            state = cls(**payload)
            if state.task_id != task_id:
                raise ValueError("durable orchestration state belongs to another task")
            return state
        state = cls(
            task_id=task_id, expected_head_sha=expected_head_sha, current_prompt=current_prompt,
            repository=repository, issue_number=int(issue_number), target_branch=target_branch)
        state.dispatch_id = _dispatch_id(task_id, expected_head_sha, 1)
        return state


class IssueClient(Protocol):
    def branch_head(self, branch: str) -> str: ...
    def comments(self) -> list[dict[str, Any]]: ...
    def post_comment(self, body: str) -> dict[str, Any]: ...
    def ci_state(self, sha: str) -> str: ...


class GitHubIssueClient:
    """Least-privilege GitHub REST client used by the VM sidecar."""

    def __init__(self, repository: str, issue_number: int, token: str,
                 api_url: str = "https://api.github.com"):
        if "/" not in repository:
            raise ValueError("repository must be owner/name")
        self.repository = repository
        self.issue_number = int(issue_number)
        self.token = token
        self.api_url = api_url.rstrip("/")

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None,
                 accept: str = "application/vnd.github+json") -> Any:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.api_url}{path}",
            data=data,
            method=method,
            headers={
                "Accept": accept,
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "quant-trade-gpt-oss-orchestrator",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API {method} {path} -> {exc.code}: {body[:500]}") from exc
        return json.loads(raw.decode("utf-8")) if raw else None

    def branch_head(self, branch: str) -> str:
        encoded = urllib.parse.quote(branch, safe="/")
        payload = self._request("GET", f"/repos/{self.repository}/git/ref/heads/{encoded}")
        return str(payload["object"]["sha"])

    def comments(self) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        page = 1
        while True:
            payload = self._request(
                "GET",
                f"/repos/{self.repository}/issues/{self.issue_number}/comments?per_page=100&page={page}",
            )
            batch = [{
                "id": item.get("id"),
                "body": item.get("body") or "",
                "author": (item.get("user") or {}).get("login"),
                "created_at": item.get("created_at"),
            } for item in payload]
            output.extend(batch)
            if len(batch) < 100:
                return output
            page += 1

    def post_comment(self, body: str) -> dict[str, Any]:
        payload = self._request(
            "POST", f"/repos/{self.repository}/issues/{self.issue_number}/comments", {"body": body})
        return {"id": payload.get("id"), "body": payload.get("body") or "",
                "author": (payload.get("user") or {}).get("login"),
                "created_at": payload.get("created_at")}

    def ci_state(self, sha: str) -> str:
        checks = self._request(
            "GET", f"/repos/{self.repository}/commits/{sha}/check-runs?per_page=100",
            accept="application/vnd.github+json").get("check_runs", [])
        combined = self._request("GET", f"/repos/{self.repository}/commits/{sha}/status")
        statuses = combined.get("statuses", [])
        failure_conclusions = {"failure", "cancelled", "timed_out", "action_required", "startup_failure"}
        if any(check.get("conclusion") in failure_conclusions for check in checks):
            return "FAIL"
        if combined.get("state") == "failure" or any(item.get("state") == "failure" for item in statuses):
            return "FAIL"
        if any(check.get("status") != "completed" for check in checks):
            return "PENDING"
        if combined.get("state") == "pending" or any(item.get("state") == "pending" for item in statuses):
            return "PENDING"
        check_success = bool(checks) and all(
            check.get("conclusion") in {"success", "neutral", "skipped"} for check in checks)
        status_success = bool(statuses) and combined.get("state") == "success"
        return "PASS" if (check_success or status_success) else "PENDING"


DecisionFunction = Callable[[dict[str, Any]], dict[str, Any]]


class CodexOrchestrationWorker:
    """A restart-safe state machine that delegates bounded work to Codex."""

    def __init__(self, config: OrchestrationConfig, client: IssueClient,
                 decide: DecisionFunction, sleeper: Callable[[float], None] = time.sleep):
        self.config = config
        self.client = client
        self.decide = decide
        self.sleeper = sleeper

    def _paths(self, task_id: str) -> tuple[Path, Path, Path]:
        safe = hashlib.sha256(task_id.encode("utf-8")).hexdigest()[:24]
        base = self.config.state_dir / safe
        return base.with_suffix(".json"), base.with_suffix(".receipts.jsonl"), base.with_suffix(".lock")

    @contextmanager
    def _lock(self, task_id: str):
        _, _, lock_path = self._paths(task_id)
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with lock_path.open("a+") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def _load(self, task: ResearchTask) -> tuple[OrchestrationState, Path, Path]:
        expected = str(task.metadata.get("expected_head_sha") or "")
        if not _SHA_RE.fullmatch(expected):
            raise ValueError("task.metadata.expected_head_sha must be a lowercase 40-character SHA")
        current_prompt = str(task.metadata.get("codex_prompt") or "").strip()
        if not current_prompt:
            raise ValueError("task.metadata.codex_prompt is required")
        state_path, receipt_path, _ = self._paths(task.task_id)
        state = OrchestrationState.load_or_create(
            state_path, task.task_id, expected, current_prompt, self.config.repository,
            self.config.issue_number, self.config.target_branch)
        return state, state_path, receipt_path

    def _persist(self, state: OrchestrationState, state_path: Path, receipt_path: Path,
                 event: str, details: dict[str, Any] | None = None) -> None:
        state.updated_at = _utc_now()
        _atomic_json(state_path, asdict(state))
        _append_receipt(receipt_path, {
            "at": state.updated_at,
            "event": event,
            "task_id": state.task_id,
            "dispatch_id": state.dispatch_id,
            "attempt": state.attempt,
            "expected_head_sha": state.expected_head_sha,
            "result_sha": state.result_sha,
            "status": state.status,
            "details": details or {},
        })

    @staticmethod
    def _hard_boundary(task: ResearchTask) -> str | None:
        authority = task.metadata.get("authority") or {}
        forbidden = {
            "real_capital_authorized": authority.get("real_capital_authorized"),
            "live_trading_authorized": authority.get("live_trading_authorized"),
            "scientific_unblinding_authorized": authority.get("scientific_unblinding_authorized"),
            "frozen_protocol_redefinition_authorized": authority.get("frozen_protocol_redefinition_authorized"),
            "irreversible_external_mutation_authorized": authority.get("irreversible_external_mutation_authorized"),
        }
        active = [name for name, value in forbidden.items() if value is True]
        return ", ".join(active) if active else None

    def _dispatch_payload(self, task: ResearchTask, state: OrchestrationState) -> dict[str, Any]:
        return {
            "task_id": task.task_id,
            "dispatch_id": state.dispatch_id,
            "attempt": state.attempt,
            "expected_head_sha": state.expected_head_sha,
        }

    def _dispatch_body(self, task: ResearchTask, state: OrchestrationState) -> str:
        payload = self._dispatch_payload(task, state)
        prompt = state.current_prompt
        contract = dict(payload)
        contract["result_sha"] = "<40-lowercase-hex-sha>"
        contract["result_branch"] = self.config.target_branch
        return (
            f"{_marker('dispatch', payload)}\n"
            f"{self.config.builder_mention}\\n\\n"
            "BOUNDED CODEX DISPATCH — work only inside the supplied task and expected-head fence.\\n\\n"
            f"{prompt}\\n\\n"
            "When, and only when, the bounded result is remotely durable, append this exact machine-readable "
            "marker with result_sha replaced by the exact remote candidate SHA:\\n"
            f"`{_marker('result', contract)}`\\n"
            "Do not claim CI or independent review in that marker; the orchestrator verifies those separately."
        )

    def _review_body(self, state: OrchestrationState) -> str:
        payload = {
            "task_id": state.task_id,
            "dispatch_id": state.dispatch_id,
            "review_attempt": state.review_attempt,
            "result_sha": state.result_sha,
        }
        contract = dict(payload)
        contract["verdict"] = "<PASS|REQUEST_CHANGES|UNKNOWN>"
        return (
            f"{_marker('review_request', payload)}\n"
            f"{self.config.reviewer_mention}\\n\\n"
            "FRESH-CONTEXT INDEPENDENT REVIEW. Inspect the exact candidate SHA and primary evidence; "
            "do not modify implementation. Return PASS only if the bounded claim is independently supported.\\n"
            f"Return exactly one marker: `{_marker('review', contract)}`"
        )

    def _valid_result(self, comments: list[dict[str, Any]], state: OrchestrationState) -> str | None:
        for comment, payload in reversed(_parse_markers("result", comments)):
            author = str(comment.get("author") or "")
            if self.config.allowed_result_authors and author not in self.config.allowed_result_authors:
                continue
            result_sha = str(payload.get("result_sha") or "")
            if (payload.get("task_id") == state.task_id
                    and payload.get("dispatch_id") == state.dispatch_id
                    and payload.get("attempt") == state.attempt
                    and payload.get("expected_head_sha") == state.expected_head_sha
                    and payload.get("result_branch") == self.config.target_branch
                    and _SHA_RE.fullmatch(result_sha)
                    and self.client.branch_head(self.config.target_branch) == result_sha):
                return result_sha
        return None

    def _ensure_review_request(self, state: OrchestrationState, state_path: Path,
                               receipt_path: Path, comments: list[dict[str, Any]]) -> None:
        request = {
            "task_id": state.task_id,
            "dispatch_id": state.dispatch_id,
            "review_attempt": state.review_attempt,
            "result_sha": state.result_sha,
        }
        if not self._has_marker("review_request", comments, request):
            self.client.post_comment(self._review_body(state))
            self._persist(state, state_path, receipt_path, "INDEPENDENT_REVIEW_REQUESTED", request)

    def _valid_review(self, comments: list[dict[str, Any]], state: OrchestrationState) -> str | None:
        for comment, payload in reversed(_parse_markers("review", comments)):
            author = str(comment.get("author") or "")
            if self.config.allowed_review_authors and author not in self.config.allowed_review_authors:
                continue
            if (payload.get("task_id") == state.task_id
                    and payload.get("dispatch_id") == state.dispatch_id
                    and payload.get("review_attempt") == state.review_attempt
                    and payload.get("result_sha") == state.result_sha
                    and payload.get("verdict") in {"PASS", "REQUEST_CHANGES", "UNKNOWN"}):
                return str(payload["verdict"])
        return None

    def _has_marker(self, kind: str, comments: list[dict[str, Any]],
                    expected: dict[str, Any]) -> bool:
        for _, payload in _parse_markers(kind, comments):
            if all(payload.get(key) == value for key, value in expected.items()):
                return True
        return False

    def _decision(self, event: str, state: OrchestrationState,
                  evidence: dict[str, Any]) -> dict[str, Any]:
        context = {
            "event": event,
            "state": asdict(state),
            "evidence": evidence,
            "allowed_actions": ["CONTINUE", "DONE", "PARK", "ADOPT_CURRENT_HEAD"],
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
        return decision

    def _apply_decision(self, task: ResearchTask, state: OrchestrationState,
                        state_path: Path, receipt_path: Path, decision: dict[str, Any],
                        fallback_head: str | None = None) -> dict[str, Any] | None:
        action = str(decision.get("action") or "").upper()
        reason = str(decision.get("reason") or action)
        if action == "DONE":
            state.status = "DONE"
            self._persist(state, state_path, receipt_path, "TERMINAL_DONE", {"reason": reason})
            return {"ticket_id": task.task_id, "outcome": "DONE", "lesson": reason,
                    "next_action_hint": decision.get("next_action")}
        if action == "PARK":
            state.status = "PARKED_NO_DELTA"
            self._persist(state, state_path, receipt_path, "TERMINAL_PARK", {"reason": reason})
            return {"ticket_id": task.task_id, "outcome": "PARKED_NO_DELTA", "lesson": reason,
                    "next_action_hint": decision.get("next_action")}
        if action == "ADOPT_CURRENT_HEAD":
            candidate = str(decision.get("expected_head_sha") or fallback_head or "")
            if not _SHA_RE.fullmatch(candidate):
                raise ValueError("ADOPT_CURRENT_HEAD requires a valid expected_head_sha")
            state.expected_head_sha = candidate
            state.attempt += 1
            state.dispatch_id = _dispatch_id(state.task_id, candidate, state.attempt)
            state.result_sha = None
            state.review_attempt = 0
            state.no_delta_cycles = 0
            state.status = "READY"
            self._persist(state, state_path, receipt_path, "HEAD_RECONCILED", {"reason": reason})
            return None
        if action == "CONTINUE":
            if state.attempt >= self.config.max_dispatch_attempts:
                state.status = "BLOCKED_EXTERNAL"
                self._persist(state, state_path, receipt_path, "DISPATCH_LIMIT_REACHED")
                return {"ticket_id": task.task_id, "outcome": "BLOCKED_EXTERNAL",
                        "lesson": "bounded dispatch-attempt limit reached",
                        "next_action_hint": "inspect durable receipts before any new authority"}
            prompt = str(decision.get("prompt") or "").strip()
            if not prompt:
                raise ValueError("CONTINUE requires a non-empty prompt")
            candidate = str(decision.get("expected_head_sha") or state.result_sha or fallback_head or "")
            if not _SHA_RE.fullmatch(candidate):
                raise ValueError("CONTINUE requires a valid expected_head_sha")
            state.current_prompt = prompt
            state.expected_head_sha = candidate
            state.attempt += 1
            state.dispatch_id = _dispatch_id(state.task_id, candidate, state.attempt)
            state.result_sha = None
            state.review_attempt = 0
            state.no_delta_cycles = 0
            state.status = "READY"
            self._persist(state, state_path, receipt_path, "CONTINUE_AUTHORIZED", {"reason": reason})
            return None
        raise ValueError(f"unsupported decision action: {action or '<empty>'}")

    def _observe_digest(self, state: OrchestrationState, comments: list[dict[str, Any]],
                        extra: dict[str, Any]) -> str:
        relevant = []
        for comment in comments:
            body = str(comment.get("body") or "")
            if "QUANT_CODEX_" in body:
                relevant.append({"id": comment.get("id"), "body": body, "author": comment.get("author")})
        payload = {"state": state.status, "relevant_comments": relevant[-50:], **extra}
        return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()

    def _no_delta(self, task: ResearchTask, state: OrchestrationState, state_path: Path,
                  receipt_path: Path, digest: str) -> dict[str, Any] | None:
        if state.last_observation_digest == digest:
            state.no_delta_cycles += 1
        else:
            state.last_observation_digest = digest
            state.no_delta_cycles = 0
        if state.no_delta_cycles >= self.config.max_no_delta_cycles:
            state.status = "PARKED_NO_DELTA"
            self._persist(state, state_path, receipt_path, "MATERIAL_INFORMATION_DELTA_EXHAUSTED")
            return {"ticket_id": task.task_id, "outcome": "PARKED_NO_DELTA",
                    "lesson": "no material information delta within the bounded polling envelope",
                    "next_action_hint": "resume only on a new external event or explicit new evidence"}
        self._persist(state, state_path, receipt_path, "NO_MATERIAL_DELTA",
                      {"no_delta_cycles": state.no_delta_cycles})
        return None

    def step(self, task: ResearchTask) -> dict[str, Any]:
        with self._lock(task.task_id):
            state, state_path, receipt_path = self._load(task)
            if state.status in _TERMINAL:
                return {"terminal": True, "result": {
                    "ticket_id": task.task_id, "outcome": state.status,
                    "lesson": "recovered durable terminal orchestration state",
                    "next_action_hint": None}}
            boundary = self._hard_boundary(task)
            if boundary:
                state.status = "HARD_BOUNDARY"
                self._persist(state, state_path, receipt_path, "HARD_BOUNDARY",
                              {"forbidden_authority": boundary})
                return {"terminal": True, "result": {
                    "ticket_id": task.task_id, "outcome": "HARD_BOUNDARY",
                    "lesson": f"non-delegable boundary requested: {boundary}",
                    "next_action_hint": "obtain separate explicit authority before crossing the boundary"}}

            comments = self.client.comments()
            if state.status == "READY":
                current_head = self.client.branch_head(self.config.target_branch)
                if current_head != state.expected_head_sha:
                    decision = self._decision(
                        "STALE_HEAD", state,
                        {"expected_head_sha": state.expected_head_sha, "current_head_sha": current_head})
                    result = self._apply_decision(
                        task, state, state_path, receipt_path, decision, fallback_head=current_head)
                    return {"terminal": result is not None, "result": result}
                payload = self._dispatch_payload(task, state)
                if not self._has_marker("dispatch", comments, payload):
                    self.client.post_comment(self._dispatch_body(task, state))
                    self._persist(state, state_path, receipt_path, "CODEX_DISPATCH_POSTED", payload)
                else:
                    self._persist(state, state_path, receipt_path, "CODEX_DISPATCH_DEDUPED", payload)
                state.status = "WAITING_RESULT"
                state.no_delta_cycles = 0
                self._persist(state, state_path, receipt_path, "WAITING_RESULT")
                return {"terminal": False, "result": None}

            if state.status == "WAITING_RESULT":
                result_sha = self._valid_result(comments, state)
                if result_sha:
                    state.result_sha = result_sha
                    state.status = "WAITING_CI"
                    state.no_delta_cycles = 0
                    self._persist(state, state_path, receipt_path, "RESULT_CAUSALLY_BOUND",
                                  {"result_sha": result_sha})
                    return {"terminal": False, "result": None}
                digest = self._observe_digest(state, comments, {})
                result = self._no_delta(task, state, state_path, receipt_path, digest)
                return {"terminal": result is not None, "result": result}

            if state.status == "WAITING_CI":
                assert state.result_sha is not None
                current_head = self.client.branch_head(self.config.target_branch)
                if current_head != state.result_sha:
                    decision = self._decision(
                        "STALE_HEAD", state,
                        {"expected_head_sha": state.result_sha, "current_head_sha": current_head})
                    result = self._apply_decision(
                        task, state, state_path, receipt_path, decision, fallback_head=current_head)
                    return {"terminal": result is not None, "result": result}
                ci = self.client.ci_state(state.result_sha)
                if ci == "PASS":
                    state.status = "WAITING_REVIEW"
                    state.review_attempt = 1
                    state.no_delta_cycles = 0
                    self._persist(state, state_path, receipt_path, "CI_EXACT_HEAD_PASS",
                                  {"result_sha": state.result_sha})
                    comments = self.client.comments()
                    self._ensure_review_request(state, state_path, receipt_path, comments)
                    return {"terminal": False, "result": None}
                if ci == "FAIL":
                    decision = self._decision("CI_FAIL", state, {"result_sha": state.result_sha})
                    result = self._apply_decision(task, state, state_path, receipt_path, decision)
                    return {"terminal": result is not None, "result": result}
                digest = self._observe_digest(state, comments, {"ci": ci, "result_sha": state.result_sha})
                result = self._no_delta(task, state, state_path, receipt_path, digest)
                return {"terminal": result is not None, "result": result}

            if state.status == "WAITING_REVIEW":
                assert state.result_sha is not None
                current_head = self.client.branch_head(self.config.target_branch)
                if current_head != state.result_sha:
                    decision = self._decision(
                        "STALE_HEAD", state,
                        {"expected_head_sha": state.result_sha, "current_head_sha": current_head})
                    result = self._apply_decision(
                        task, state, state_path, receipt_path, decision, fallback_head=current_head)
                    return {"terminal": result is not None, "result": result}
                self._ensure_review_request(state, state_path, receipt_path, comments)
                comments = self.client.comments()
                verdict = self._valid_review(comments, state)
                if verdict == "UNKNOWN" and state.review_attempt < self.config.max_review_attempts:
                    state.review_attempt += 1
                    state.no_delta_cycles = 0
                    self._persist(state, state_path, receipt_path, "REVIEW_UNKNOWN_RETRY",
                                  {"review_attempt": state.review_attempt})
                    comments = self.client.comments()
                    self._ensure_review_request(state, state_path, receipt_path, comments)
                    return {"terminal": False, "result": None}
                if verdict in {"PASS", "REQUEST_CHANGES", "UNKNOWN"}:
                    # Re-read immediately before qualification/decision: the branch
                    # may have advanced while the review comments were fetched.
                    current_head = self.client.branch_head(self.config.target_branch)
                    if current_head != state.result_sha:
                        decision = self._decision(
                            "STALE_HEAD", state,
                            {"expected_head_sha": state.result_sha,
                             "current_head_sha": current_head})
                        result = self._apply_decision(
                            task, state, state_path, receipt_path, decision,
                            fallback_head=current_head)
                        return {"terminal": result is not None, "result": result}
                    event = {
                        "PASS": "QUALIFIED_RESULT",
                        "REQUEST_CHANGES": "REVIEW_REQUEST_CHANGES",
                        "UNKNOWN": "REVIEW_UNKNOWN_EXHAUSTED",
                    }[verdict]
                    decision = self._decision(
                        event, state, {"result_sha": state.result_sha, "review_verdict": verdict})
                    result = self._apply_decision(task, state, state_path, receipt_path, decision)
                    return {"terminal": result is not None, "result": result}
                digest = self._observe_digest(
                    state, comments, {"result_sha": state.result_sha,
                                      "review_attempt": state.review_attempt})
                result = self._no_delta(task, state, state_path, receipt_path, digest)
                return {"terminal": result is not None, "result": result}

            raise RuntimeError(f"unknown orchestration state: {state.status}")

    def __call__(self, task: ResearchTask) -> dict[str, Any]:
        while True:
            outcome = self.step(task)
            if outcome["terminal"]:
                return outcome["result"]
            state_path, _, _ = self._paths(task.task_id)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            delay = min(
                self.config.poll_seconds * (2 ** min(int(state.get("no_delta_cycles", 0)), 3)),
                self.config.max_poll_seconds,
            )
            self.sleeper(delay)
