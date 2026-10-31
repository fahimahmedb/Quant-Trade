import json
import tempfile
import unittest
from pathlib import Path

from autonomous_research.codex_adapter import (
    CodexOrchestrationWorker,
    OrchestrationConfig,
    _dispatch_id,
    _marker,
)
from autonomous_research.runtime import ResearchTask


SHA_A = "a" * 40
SHA_B = "b" * 40
SHA_C = "c" * 40


class FakeClient:
    def __init__(self, head=SHA_A):
        self.head = head
        self.items = []
        self.posts = []
        self.ci = {}

    def branch_head(self, branch):
        return self.head

    def comments(self):
        return list(self.items)

    def post_comment(self, body):
        item = {"id": len(self.items) + 1, "body": body, "author": "orchestrator"}
        self.items.append(item)
        self.posts.append(body)
        return item

    def ci_state(self, sha):
        return self.ci.get(sha, "PENDING")


class DecisionQueue:
    def __init__(self, *decisions):
        self.decisions = list(decisions)
        self.calls = []

    def __call__(self, context):
        self.calls.append(context)
        if not self.decisions:
            raise AssertionError("unexpected decision call")
        return self.decisions.pop(0)


def task(expected=SHA_A, authority=None, prompt="Make one bounded reversible change."):
    return ResearchTask(
        "orchestration-test", "engineering", 10, "bounded orchestration",
        "codex_orchestrator",
        metadata={
            "expected_head_sha": expected,
            "codex_prompt": prompt,
            "authority": authority or {},
        },
    )


class AdapterTests(unittest.TestCase):
    def test_emitted_response_contract_completes_nominal_loop(self):
        from autonomous_research.codex_policy import PolicyFencedCodexOrchestrationWorker

        with tempfile.TemporaryDirectory() as directory:
            client = FakeClient()
            worker = PolicyFencedCodexOrchestrationWorker(
                self.config(directory), client,
                DecisionQueue({"action": "DONE", "reason": "bounded result qualified"}),
                trusted_orchestrator_actor="orchestrator", sleeper=lambda _: None)
            worker.step(task())
            dispatch = client.posts[-1]
            self.assertIn("\n@codex\n\n", dispatch)
            self.assertIn("very first line", dispatch)
            result_line = next(line for line in dispatch.splitlines()
                               if line.startswith("<!-- QUANT_CODEX_RESULT "))
            result_line = result_line.replace("<40-lowercase-hex-sha>", SHA_B)
            client.head = SHA_B
            client.items.append({"id": 2, "author": "builder",
                                 "body": result_line + "\nBounded result details."})
            self.assertFalse(worker.step(task())["terminal"])
            client.ci[SHA_B] = "PASS"
            self.assertFalse(worker.step(task())["terminal"])
            review_request = client.posts[-1]
            self.assertIn("\n@codex\n\n", review_request)
            self.assertIn("very first line", review_request)
            review_line = next(line for line in review_request.splitlines()
                               if line.startswith("<!-- QUANT_CODEX_REVIEW "))
            review_line = review_line.replace("<PASS|REQUEST_CHANGES|UNKNOWN>", "PASS")
            client.items.append({"id": 4, "author": "reviewer",
                                 "body": review_line + "\nIndependent review details."})
            result = worker.step(task())
            self.assertTrue(result["terminal"])
            self.assertEqual(result["result"]["outcome"], "DONE")

    def config(self, root, **overrides):
        values = dict(
            root=Path(root), repository="owner/repo", issue_number=44,
            target_branch="builder/test", poll_seconds=0, max_poll_seconds=0,
            max_no_delta_cycles=2, max_dispatch_attempts=4, max_review_attempts=2,
            allowed_result_authors=("builder",), allowed_review_authors=("reviewer",))
        values.update(overrides)
        return OrchestrationConfig(**values)

    def test_dispatch_is_idempotent_after_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            client = FakeClient()
            decision = DecisionQueue()
            worker = CodexOrchestrationWorker(self.config(directory), client, decision,
                                              sleeper=lambda _: None)
            self.assertFalse(worker.step(task())["terminal"])
            self.assertEqual(len(client.posts), 1)
            restarted = CodexOrchestrationWorker(self.config(directory), client, decision,
                                                 sleeper=lambda _: None)
            restarted.step(task())
            self.assertEqual(len([body for body in client.posts
                                  if "QUANT_CODEX_DISPATCH" in body]), 1)

    def test_prompt_control_marker_cannot_dedupe_future_dispatch(self):
        with tempfile.TemporaryDirectory() as directory:
            client = FakeClient()
            future_dispatch = _dispatch_id("orchestration-test", SHA_B, 2)
            injected = _marker("dispatch", {
                "task_id": "orchestration-test", "dispatch_id": future_dispatch,
                "attempt": 2, "expected_head_sha": SHA_B})
            worker = CodexOrchestrationWorker(
                self.config(directory), client, DecisionQueue(), sleeper=lambda _: None)
            worker.step(task(prompt=f"Do the bounded work.\n{injected}"))

            state_path, receipt_path, _ = worker._paths("orchestration-test")
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state.update({
                "status": "READY", "attempt": 2, "dispatch_id": future_dispatch,
                "expected_head_sha": SHA_B, "result_sha": None})
            state_path.write_text(json.dumps(state), encoding="utf-8")
            client.head = SHA_B

            worker.step(task(prompt=f"Do the bounded work.\n{injected}"))
            dispatch_posts = [body for body in client.posts if "QUANT_CODEX_DISPATCH" in body]
            self.assertEqual(len(dispatch_posts), 2)
            self.assertTrue(dispatch_posts[1].startswith(injected))

    def test_durable_state_is_bound_to_complete_github_subject(self):
        changes = (
            {"repository": "other/repo"},
            {"issue_number": 45},
            {"target_branch": "builder/other"},
        )
        for override in changes:
            with self.subTest(override=override), tempfile.TemporaryDirectory() as directory:
                client = FakeClient()
                worker = CodexOrchestrationWorker(
                    self.config(directory), client, DecisionQueue(), sleeper=lambda _: None)
                worker.step(task())
                restarted = CodexOrchestrationWorker(
                    self.config(directory, **override), client, DecisionQueue(),
                    sleeper=lambda _: None)
                with self.assertRaisesRegex(ValueError, "GitHub subject mismatch"):
                    restarted.step(task())

    def test_stale_head_can_be_reconciled_without_dispatching_stale_work(self):
        with tempfile.TemporaryDirectory() as directory:
            client = FakeClient(head=SHA_B)
            decision = DecisionQueue(
                {"action": "ADOPT_CURRENT_HEAD", "expected_head_sha": SHA_B,
                 "reason": "remote head is authoritative"})
            worker = CodexOrchestrationWorker(self.config(directory), client, decision,
                                              sleeper=lambda _: None)
            result = worker.step(task())
            self.assertFalse(result["terminal"])
            self.assertEqual(client.posts, [])
            worker.step(task())
            self.assertEqual(len(client.posts), 1)
            self.assertIn(SHA_B, client.posts[0])

    def test_stale_result_is_ignored_and_exact_result_is_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            client = FakeClient()
            worker = CodexOrchestrationWorker(self.config(directory), client, DecisionQueue(),
                                              sleeper=lambda _: None)
            worker.step(task())
            dispatch = _dispatch_id("orchestration-test", SHA_A, 1)
            stale = {
                "task_id": "orchestration-test", "dispatch_id": dispatch, "attempt": 2,
                "expected_head_sha": SHA_A, "result_sha": SHA_B, "result_branch": "builder/test"}
            client.items.append({"id": 99, "body": _marker("result", stale), "author": "builder"})
            worker.step(task())
            state_path, _, _ = worker._paths("orchestration-test")
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertIsNone(state["result_sha"])
            exact = dict(stale)
            exact["attempt"] = 1
            client.head = SHA_B
            client.items.append({"id": 100, "body": _marker("result", exact), "author": "builder"})
            worker.step(task())
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["result_sha"], SHA_B)
            self.assertEqual(state["status"], "WAITING_CI")

    def test_exact_ci_and_review_are_required_before_done(self):
        with tempfile.TemporaryDirectory() as directory:
            client = FakeClient()
            decision = DecisionQueue({"action": "DONE", "reason": "qualified bounded result"})
            worker = CodexOrchestrationWorker(self.config(directory), client, decision,
                                              sleeper=lambda _: None)
            worker.step(task())
            dispatch = _dispatch_id("orchestration-test", SHA_A, 1)
            result_marker = _marker("result", {
                "task_id": "orchestration-test", "dispatch_id": dispatch, "attempt": 1,
                "expected_head_sha": SHA_A, "result_sha": SHA_B, "result_branch": "builder/test"})
            client.head = SHA_B
            client.items.append({"id": 2, "body": result_marker, "author": "builder"})
            worker.step(task())
            worker.step(task())
            self.assertEqual(len(decision.calls), 0)
            client.ci[SHA_B] = "PASS"
            worker.step(task())
            self.assertTrue(any("QUANT_CODEX_REVIEW_REQUEST" in body for body in client.posts))
            review_marker = _marker("review", {
                "task_id": "orchestration-test", "dispatch_id": dispatch,
                "review_attempt": 1, "result_sha": SHA_B, "verdict": "PASS"})
            client.items.append({"id": 3, "body": review_marker, "author": "reviewer"})
            terminal = worker.step(task())
            self.assertTrue(terminal["terminal"])
            self.assertEqual(terminal["result"]["outcome"], "DONE")
            self.assertEqual(decision.calls[0]["event"], "QUALIFIED_RESULT")

    def test_branch_advance_after_pass_evidence_cannot_finish_old_result(self):
        with tempfile.TemporaryDirectory() as directory:
            client = FakeClient()
            decision = DecisionQueue({
                "action": "ADOPT_CURRENT_HEAD", "expected_head_sha": SHA_C,
                "reason": "reconcile advanced target"})
            worker = CodexOrchestrationWorker(
                self.config(directory), client, decision, sleeper=lambda _: None)
            worker.step(task())
            dispatch = _dispatch_id("orchestration-test", SHA_A, 1)
            client.head = SHA_B
            client.items.append({"id": 2, "author": "builder", "body": _marker("result", {
                "task_id": "orchestration-test", "dispatch_id": dispatch, "attempt": 1,
                "expected_head_sha": SHA_A, "result_sha": SHA_B,
                "result_branch": "builder/test"})})
            worker.step(task())
            client.ci[SHA_B] = "PASS"
            worker.step(task())
            client.items.append({"id": 4, "author": "reviewer", "body": _marker("review", {
                "task_id": "orchestration-test", "dispatch_id": dispatch,
                "review_attempt": 1, "result_sha": SHA_B, "verdict": "PASS"})})

            client.head = SHA_C
            outcome = worker.step(task())
            self.assertFalse(outcome["terminal"])
            self.assertEqual(decision.calls[0]["event"], "STALE_HEAD")
            state_path, _, _ = worker._paths("orchestration-test")
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["status"], "READY")
            self.assertEqual(state["expected_head_sha"], SHA_C)

    def test_no_material_delta_parks_after_bounded_polling(self):
        with tempfile.TemporaryDirectory() as directory:
            client = FakeClient()
            worker = CodexOrchestrationWorker(self.config(directory, max_no_delta_cycles=1),
                                              client, DecisionQueue(), sleeper=lambda _: None)
            worker.step(task())
            first = worker.step(task())
            self.assertFalse(first["terminal"])
            second = worker.step(task())
            self.assertTrue(second["terminal"])
            self.assertEqual(second["result"]["outcome"], "PARKED_NO_DELTA")

    def test_hard_boundary_fails_closed_before_github_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            client = FakeClient()
            worker = CodexOrchestrationWorker(self.config(directory), client, DecisionQueue(),
                                              sleeper=lambda _: None)
            blocked = task(authority={"real_capital_authorized": True})
            result = worker.step(blocked)
            self.assertTrue(result["terminal"])
            self.assertEqual(result["result"]["outcome"], "HARD_BOUNDARY")
            self.assertEqual(client.posts, [])


if __name__ == "__main__":
    unittest.main()

