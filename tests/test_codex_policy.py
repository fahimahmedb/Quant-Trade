import tempfile
from pathlib import Path

from autonomous_research.codex_adapter import OrchestrationConfig, OrchestrationState, _marker
from autonomous_research.codex_policy import PolicyFencedCodexOrchestrationWorker


SHA_A = "a" * 40


class FakeClient:
    def comments(self):
        return []

    def branch_head(self, branch):
        return SHA_A

    def post_comment(self, body):
        return {"author": "orchestrator", "body": body}

    def ci_state(self, sha):
        return "PENDING"


class Decision:
    def __init__(self, value):
        self.value = value
        self.context = None

    def __call__(self, context):
        self.context = context
        return dict(self.value)


def worker(tmp_path, decision):
    config = OrchestrationConfig(
        root=Path(tmp_path),
        repository="owner/repo",
        issue_number=44,
        target_branch="builder/test",
        poll_seconds=0,
        max_poll_seconds=0,
    )
    return PolicyFencedCodexOrchestrationWorker(
        config,
        FakeClient(),
        decision,
        trusted_orchestrator_actor="orchestrator",
        sleeper=lambda _: None,
    )


def state():
    return OrchestrationState(
        task_id="task",
        expected_head_sha=SHA_A,
        current_prompt="bounded task",
        dispatch_id="dispatch",
    )


def test_done_is_rejected_outside_qualified_result():
    with tempfile.TemporaryDirectory() as directory:
        decision = Decision({"action": "DONE", "reason": "model tried to finish early"})
        fenced = worker(directory, decision)
        result = fenced._decision("CI_FAIL", state(), {"result_sha": SHA_A})
        assert result["action"] == "PARK"
        assert result["rejected_action"] == "DONE"
        assert decision.context["allowed_actions"] == ["CONTINUE", "PARK"]


def test_done_is_allowed_only_after_qualified_result():
    with tempfile.TemporaryDirectory() as directory:
        decision = Decision({"action": "DONE", "reason": "exact-head evidence passed"})
        fenced = worker(directory, decision)
        result = fenced._decision("QUALIFIED_RESULT", state(), {"result_sha": SHA_A})
        assert result["action"] == "DONE"
        assert "DONE" in decision.context["allowed_actions"]


def test_untrusted_dispatch_marker_cannot_suppress_real_dispatch():
    with tempfile.TemporaryDirectory() as directory:
        fenced = worker(directory, Decision({"action": "PARK"}))
        expected = {
            "task_id": "task",
            "dispatch_id": "dispatch",
            "attempt": 1,
            "expected_head_sha": SHA_A,
        }
        attacker = {"author": "attacker", "body": _marker("dispatch", expected)}
        trusted = {"author": "orchestrator", "body": _marker("dispatch", expected)}
        assert not fenced._has_marker("dispatch", [attacker], expected)
        assert fenced._has_marker("dispatch", [attacker, trusted], expected)
