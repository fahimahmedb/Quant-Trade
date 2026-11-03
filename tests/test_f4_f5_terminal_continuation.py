"""Synthetic-safe F4 terminal-to-Research OS bridge tests (never invoke Codex)."""
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from research.research_os import host_wake
from research.research_os.oracle_worker import ResearchOSWorker


class TerminalBridgeTests(unittest.TestCase):
    def fixture(self, root):
        task, code_sha = "F3-SYNTHETIC", "e" * 40
        env = {
            "QUANT_CODEX_TASK_ID": task,
            "QUANT_CODEX_EXPECTED_HEAD_SHA": code_sha,
            "QUANT_CODEX_PROJECT_BRANCH": "project/canonical",
            "QUANT_CODEX_TARGET_BRANCH": "code/canonical",
            "QUANT_CODEX_ISSUE_NUMBER": "50",
            "QUANT_REPOSITORY": "synthetic/repo",
            "QUANT_CODEX_ORCHESTRATION_ROOT": str(root),
            "QUANT_CODEX_ORCHESTRATION_ENABLED": "1",
        }
        key = hashlib.sha256(task.encode()).hexdigest()[:24]
        folder = root / "runtime" / "codex_orchestration"
        folder.mkdir(parents=True)
        state_path = folder / (key + ".json")
        receipt_path = folder / (key + ".receipts.jsonl")
        dispatch_id = hashlib.sha256(f"{task}\0{code_sha}\0{1}".encode()).hexdigest()
        state = {
            "task_id": task, "expected_head_sha": code_sha, "result_sha": code_sha,
            "project_head_sha": "a" * 40, "repository": "synthetic/repo",
            "issue_number": 50, "target_branch": "code/canonical",
            "project_branch": "project/canonical", "readonly_probe": True,
            "status": "DONE", "attempt": 1, "dispatch_id": dispatch_id,
            "last_decision": {"action": "DONE"},
        }
        events = ["PROJECT_AUTHORITY_FENCED", "RESULT_CAUSALLY_BOUND",
                  "READ_ONLY_PROBE_RESULT_CONSUMED", "TERMINAL_DONE"]
        receipts = []
        for event in events:
            receipts.append({
                "task_id": task, "dispatch_id": dispatch_id, "event": event,
                "expected_head_sha": code_sha,
                "result_sha": None if event == events[0] else code_sha,
                "status": "DONE" if event == events[-1] else "WAITING_PROBE_DECISION",
                "details": {"action": "DONE", "code_promotion_authorized": False}
                           if event == events[2] else {},
            })
        state_path.write_text(json.dumps(state))
        receipt_path.write_text("".join(json.dumps(x) + "\n" for x in receipts))
        return env, state_path, receipt_path, state, receipts

    def test_terminal_execs_exactly_one_v2_research_worker(self):
        with tempfile.TemporaryDirectory() as directory:
            env, *_ = self.fixture(Path(directory))
            cause = host_wake._terminal_continuation(env)
            self.assertEqual(cause["predecessor_task_id"], env["QUANT_CODEX_TASK_ID"])
            with patch("research.research_os.host_wake._codex_environment", return_value=env), \
                 patch("research.research_os.host_wake.os.execve") as execve, \
                 patch.dict(os.environ, env):
                host_wake._exec_one("/synthetic/v2.json", "v2")
            execve.assert_called_once()
            self.assertEqual(execve.call_args.args[1][1:3],
                             ["-m", "research.research_os.oracle_worker_v2"])
            self.assertEqual(json.loads(execve.call_args.args[2]["QUANT_F4_CAUSAL_PREDECESSOR"]), cause)
            self.assertEqual(host_wake._terminal_continuation(env), cause)

    def test_terminal_rejects_stale_head_wrong_subject_and_forged_result(self):
        with tempfile.TemporaryDirectory() as directory:
            env, state_path, _, state, _ = self.fixture(Path(directory))
            with self.assertRaisesRegex(SystemExit, "HEAD"):
                host_wake._terminal_continuation(dict(env, QUANT_CODEX_EXPECTED_HEAD_SHA="f"*40))
            with self.assertRaisesRegex(SystemExit, "SUBJECT"):
                host_wake._terminal_continuation(dict(env, QUANT_REPOSITORY="wrong/repo"))
            state["result_sha"] = "b"*40
            state_path.write_text(json.dumps(state))
            with self.assertRaisesRegex(SystemExit, "HEAD"):
                host_wake._terminal_continuation(env)

    def test_unconsumed_result_fails_closed_without_any_worker(self):
        with tempfile.TemporaryDirectory() as directory:
            env, _, receipt_path, _, receipts = self.fixture(Path(directory))
            receipt_path.write_text("".join(json.dumps(x) + "\n" for x in receipts
                                            if x["event"] != "READ_ONLY_PROBE_RESULT_CONSUMED"))
            with patch("research.research_os.host_wake._codex_environment", return_value=env), \
                 patch("research.research_os.host_wake.os.execve") as execve, \
                 patch.dict(os.environ, env):
                with self.assertRaisesRegex(SystemExit, "CAUSAL_CHAIN"):
                    host_wake._exec_one("/synthetic/v2.json", "v2")
            execve.assert_not_called()

    def test_pending_task_still_routes_to_original_codex_state_machine(self):
        with tempfile.TemporaryDirectory() as directory:
            env, state_path, _, state, _ = self.fixture(Path(directory))
            state["status"] = "WAITING_RESULT"
            state_path.write_text(json.dumps(state))
            with patch("research.research_os.host_wake._codex_environment", return_value=env), \
                 patch("research.research_os.host_wake.os.execve") as execve, \
                 patch.dict(os.environ, env):
                host_wake._exec_one("/synthetic/v2.json", "v2")
            execve.assert_called_once()
            self.assertIn("gpt_oss_orchestrator.py", execve.call_args.args[1][1])

    def test_noop_research_worker_persists_predecessor_in_durable_receipt(self):
        store = Mock()
        store.repository, store.branch = "synthetic/repo", "code/canonical"
        snapshot = MagicMock()
        snapshot.head = "a" * 40
        snapshot.tasks.return_value = []
        context = MagicMock()
        context.__enter__.return_value = snapshot
        store.snapshot.return_value = context
        store.commit.return_value = "c" * 40
        worker = ResearchOSWorker(store, lane="nonexistent-lane",
                                  worker_id="synthetic-worker", release_sha="f" * 40)
        worker.continuation_cause = {"predecessor_task_id": "F3-SYNTHETIC"}
        with patch("research.research_os.oracle_worker.run_worker_preflight", return_value={}):
            result = worker.wake(mode="run")
        self.assertEqual(result["status"], "NO_ADMISSIBLE_LANE_TASK")
        self.assertEqual(result["causal_predecessor"], worker.continuation_cause)
        persisted = store.commit.call_args.args[1]
        self.assertEqual(next(iter(persisted.values()))["causal_predecessor"],
                         worker.continuation_cause)


if __name__ == "__main__":
    unittest.main()
