from __future__ import annotations

from copy import deepcopy
from datetime import timedelta
import unittest

from continuity.wp2_binding.synthetic_binding import SINK, TASK_ID, SyntheticWP2Binding
from research.research_os.github_state import PREFIX, StateConflict
from research.research_os.oracle_worker import ResearchOSWorker
from research.research_os.scientific_store import sha256_json
from research.research_os.tests.test_experiment_runner_frozen_protocol import fixture
from research.research_os.tests import test_oracle_worker as worker_fixture
from research.research_os.worker_stages import StageBlocked


class WP2SingleLineageTests(unittest.TestCase):
    def setUp(self):
        self.harness = worker_fixture.WorkerTests(
            methodName="test_two_wakes_continue_same_task_then_completed_restart_is_noop"
        )
        self.harness.setUp()
        old = PREFIX + "tasks/RECOVER-TEST-001.json"
        task = worker_fixture.recovery_task(TASK_ID)
        with self.harness.store.snapshot() as snapshot:
            original = snapshot.read(old)
            original["status"] = "COMPLETE"
            self.harness.store.commit(
                snapshot,
                {old: original, PREFIX + f"tasks/{TASK_ID}.json": task},
                create_only=[PREFIX + f"tasks/{TASK_ID}.json"],
                message="install isolated WP2 synthetic fixture",
            )
        self.envelope, self.qualifications, self.meta = fixture()

    def tearDown(self):
        self.harness.tearDown()

    def binding(self, **kwargs):
        return SyntheticWP2Binding(self.envelope, self.qualifications, self.meta, **kwargs)

    def worker(self, binding=None, **kwargs):
        return ResearchOSWorker(
            self.harness.store,
            lane="evidence_data",
            release_sha=worker_fixture.RELEASE,
            now=lambda: self.harness.now,
            executor=binding or self.binding(),
            expected_task_id=TASK_ID,
            **kwargs,
        )

    def read(self, path):
        return self.harness.read(path)

    def test_single_lineage_publishes_one_hash_addressed_receipt(self):
        result = self.worker().wake()
        receipt = self.read("artifacts/" + TASK_ID + "/wp2/causality.json")
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(receipt["runner_subject"], receipt["evaluator_subject"])
        self.assertEqual(receipt["task_id"], TASK_ID)
        self.assertEqual(receipt["lease_generation"], 1)
        receipt_fields = {key: value for key, value in receipt.items() if key != "receipt_hash"}
        self.assertEqual(receipt["receipt_hash"], sha256_json(receipt_fields))
        worker_metadata = {
            "input_head", "preflight", "state_repository", "state_branch", "authority",
            "outcome_accessed",
        }
        worker_output = self.read(
            f"artifacts/{TASK_ID}/oracle-worker/recover_or_qualify.json"
        )
        self.assertTrue(worker_metadata <= worker_output.keys())
        self.assertTrue(worker_metadata.isdisjoint(receipt))
        self.worker().wake()
        self.assertEqual(self.harness.count_paths(f"artifacts/{TASK_ID}/wp2/"), 1)

    def test_crash_recovery_preserves_task_and_fences_stale_lease(self):
        def crash(point):
            if point == "after_claim":
                raise RuntimeError("synthetic crash")
        with self.assertRaises(RuntimeError):
            self.worker(fault=crash).wake()
        claimed = self.read(f"tasks/{TASK_ID}.json")
        self.harness.now += timedelta(seconds=601)
        result = self.worker().wake()
        receipt = self.read("artifacts/" + TASK_ID + "/wp2/causality.json")
        self.assertEqual(result["task_id"], TASK_ID)
        self.assertEqual(receipt["lease_generation"], 2)
        with self.harness.store.snapshot() as snapshot, self.assertRaises(StateConflict):
            self.worker()._verify_lease(
                snapshot, TASK_ID, 1, claimed["execution"]["session_id"], "evidence_data"
            )

    def test_wrong_task_identity_rejected(self):
        binding = self.binding()
        with self.harness.store.snapshot() as snapshot, self.assertRaisesRegex(StageBlocked, "TASK_IDENTITY"):
            binding.execute(
                snapshot, worker_fixture.recovery_task("WRONG"),
                "evidence_data", "recover_or_qualify", "now", "owner",
            )

    def test_sink_mismatch_rejected(self):
        result = self.worker(binding=self.binding(expected_sink=SINK + ".wrong")).wake()
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(self.harness.count_paths(f"artifacts/{TASK_ID}/wp2/"), 0)

    def test_runner_evaluator_subject_mismatch_rejected(self):
        binding = self.binding()
        original_verify = binding.runner.verify_bindings
        def mismatched(*args):
            result = original_verify(*args)
            result["execution_plan_hash"] = "mutated-subject"
            return result
        binding.runner.verify_bindings = mismatched
        result = self.worker(binding=binding).wake()
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(self.harness.count_paths(f"artifacts/{TASK_ID}/wp2/"), 0)

    def test_provenance_mutation_between_runner_and_evaluator_rejected(self):
        binding = self.binding()
        original_verify = binding.runner.verify_bindings
        def mutate_then_verify(plan, envelope, qualifications, runner_meta):
            runner_meta["code_hash"] = "mutated-after-plan"
            return original_verify(plan, envelope, qualifications, runner_meta)
        binding.runner.verify_bindings = mutate_then_verify
        result = self.worker(binding=binding).wake()
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(self.harness.count_paths(f"artifacts/{TASK_ID}/wp2/"), 0)

    def test_authority_membrane_violation_rejected_before_runner(self):
        task_path = PREFIX + f"tasks/{TASK_ID}.json"
        with self.harness.store.snapshot() as snapshot:
            task = snapshot.read(task_path)
            task["authority"]["live_trading_authorized"] = True
            self.harness.store.commit(snapshot, {task_path: task}, message="inject forbidden authority")
        with self.assertRaisesRegex(Exception, "AUTHORITY|authority"):
            self.worker().wake()

    def test_fixture_identity_is_deterministic(self):
        self.assertEqual(self.binding().fixture_id, self.binding().fixture_id)
        changed = deepcopy(self.meta)
        changed["seed"] = 43
        other = SyntheticWP2Binding(self.envelope, self.qualifications, changed)
        self.assertNotEqual(self.binding().fixture_id, other.fixture_id)


if __name__ == "__main__":
    unittest.main()
