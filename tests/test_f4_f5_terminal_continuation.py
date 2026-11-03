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
        events = ["PROJECT_AUTHORITY_FENCED", "CODEX_DISPATCH_POSTED",
                  "RESULT_CAUSALLY_BOUND", "READ_ONLY_PROBE_RESULT_CONSUMED",
                  "TERMINAL_DONE"]
        receipts = []
        for event in events:
            receipts.append({
                "task_id": task, "dispatch_id": dispatch_id, "event": event,
                "expected_head_sha": code_sha,
                "result_sha": None if event in events[:2] else code_sha,
                "status": "DONE" if event == events[-1] else "WAITING_PROBE_DECISION",
                "details": {"action": "DONE", "code_promotion_authorized": False}
                           if event == events[3] else {},
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

    def test_missing_dispatch_receipt_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            env, _, receipt_path, _, receipts = self.fixture(Path(directory))
            receipt_path.write_text("".join(json.dumps(x) + "\n" for x in receipts
                                            if x["event"] != "CODEX_DISPATCH_POSTED"))
            with self.assertRaisesRegex(SystemExit, "CAUSAL_CHAIN"):
                host_wake._terminal_continuation(env)

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


    def test_f5_isolated_git_terminal_successor_memory_restart_and_fencing(self):
        """One synthetic predecessor -> local Git Research OS lifecycle; no GitHub push."""
        from research.research_os.tests.test_oracle_worker import WorkerTests, LocalStore, RELEASE
        from research.research_os.github_state import PREFIX, StateConflict
        from research.research_os.oracle_worker_v2 import V2ResearchOSWorker
        from research.research_os.worker_stages import CanonicalStageExecutor

        with tempfile.TemporaryDirectory() as directory:
            env, *_ = self.fixture(Path(directory))
            cause = host_wake._terminal_continuation(env)
            harness = WorkerTests(methodName="test_two_wakes_continue_same_task_then_completed_restart_is_noop")
            harness.setUp()
            try:
                next_task_id = "RECOVER-TEST-001"
                self.assertNotEqual(cause["predecessor_task_id"], next_task_id)

                # V2 selection/fencing with the existing non-economic Legacy recovery executor;
                # V2 scientific epoch-stage qualification remains a separate gate.
                def successor(store):
                    worker = V2ResearchOSWorker(
                        store, lane="evidence_data", worker_id="f5-local-git",
                        release_sha=RELEASE, now=lambda: harness.now,
                        executor=CanonicalStageExecutor(harness.model))
                    worker.continuation_cause = cause
                    return worker

                first = successor(harness.store).wake(mode="run")
                self.assertEqual((first["task_id"], first["stage"], first["status"]),
                                 (next_task_id, "recover_or_qualify", "READY"))
                self.assertEqual(first["causal_predecessor"], cause)

                # A new Git cache and worker must continue the same durable task.
                restarted_store = LocalStore(harness.root / "f5-resume-cache", harness.remote)
                second_worker = successor(restarted_store)
                second = second_worker.wake(mode="run")
                self.assertEqual((second["task_id"], second["stage"], second["status"]),
                                 (next_task_id, "provenance_check", "COMPLETE"))
                self.assertNotEqual(first["session_id"], second["session_id"])
                self.assertEqual(second["causal_predecessor"], cause)

                # Yet another cold cache must not duplicate either execution.
                cold_store = LocalStore(harness.root / "f5-terminal-cache", harness.remote)
                terminal = successor(cold_store).wake(mode="run")
                self.assertEqual(terminal["status"], "NO_ADMISSIBLE_LANE_TASK")
                self.assertEqual(terminal["causal_predecessor"], cause)

                with cold_store.snapshot() as snapshot:
                    task = snapshot.read(PREFIX + "tasks/" + next_task_id + ".json")
                    self.assertEqual(task["status"], "COMPLETE")
                    self.assertEqual(task["lease"]["generation"], 2)
                    self.assertEqual(len(task["execution"]["completed_stages"]), 2)
                    self.assertEqual(task["completion"]["result"], "COMPLETE")
                    receipt_paths = sorted(p for p in snapshot.blobs if p.startswith(
                        PREFIX + "receipts/" + next_task_id + "/"))
                    self.assertEqual(len(receipt_paths), 2)
                    for receipt_path in receipt_paths:
                        receipt = snapshot.read(receipt_path)
                        self.assertEqual(receipt["causal_predecessor"], cause)
                        self.assertEqual(receipt["task_id"], next_task_id)
                        for artifact in receipt["artifacts"]:
                            self.assertIsInstance(snapshot.read(artifact), dict)
                    self.assertIn(task["completion"]["receipt"], receipt_paths)
                    noops = [
                        snapshot.read(path) for path in snapshot.blobs
                        if path.startswith(PREFIX + "runtime/worker_wakes/") and path.endswith(".json")
                    ]
                    self.assertTrue(any(
                        receipt.get("status") == "NO_ADMISSIBLE_LANE_TASK"
                        and receipt.get("causal_predecessor") == cause
                        for receipt in noops))
                    # An earlier generation cannot write after the terminal result.
                    with self.assertRaises(StateConflict):
                        second_worker._verify_lease(
                            snapshot, next_task_id, 1, first["session_id"], "evidence_data")

                # The real local Git ref lease must reject a write against a stale HEAD.
                old_store = LocalStore(harness.root / "f5-old-cache", harness.remote)
                competing = LocalStore(harness.root / "f5-competing-cache", harness.remote)
                with old_store.snapshot() as stale:
                    with competing.snapshot() as current:
                        winner = PREFIX + "runtime/worker_wakes/f5-head-winner.json"
                        competing.commit(
                            current, {winner: {"synthetic_only": True}},
                            create_only=[winner], message="synthetic F5 concurrent winner")
                    loser = PREFIX + "runtime/worker_wakes/f5-head-loser.json"
                    with self.assertRaises(StateConflict):
                        old_store.commit(
                            stale, {loser: {"synthetic_only": True}},
                            create_only=[loser], message="synthetic F5 stale loser")
            finally:
                harness.tearDown()


if __name__ == "__main__":
    unittest.main()
