"""Clean-epoch admission must agree across fixture, stage and real Git worker."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from research.research_os.expansion.v2_core import V2ContractError
from research.research_os.expansion.v2_pipeline import run_pre_outcome_pipeline
from research.research_os.expansion.v2_stage_executor import ACTIVE_EPOCH_PATH, V2StageExecutor
from research.research_os.worker_stages import CanonicalStageExecutor, StageBlocked
from research.research_os.tests import test_oracle_worker as git_fixtures
from tests import test_research_os_v2_worker_integration as fixtures


class EpochBlindingAdmissionTests(unittest.TestCase):
    def bundle(self):
        return json.loads((Path(__file__).parent / "fixtures/oracle_v2_core_fixture.json").read_text())

    def test_pipeline_cannot_qualify_dirty_or_unproven_epoch_before_export(self):
        for value in ("BROKEN", "CONTAMINATED", "UNKNOWN", None, "", False):
            bundle = self.bundle()
            bundle["epoch"]["contamination_status"] = value
            with self.subTest(contamination=value), patch(
                "research.research_os.expansion.v2_pipeline.build_frozen_export_intent"
            ) as export:
                with self.assertRaisesRegex(V2ContractError, "EPOCH_CONTAMINATED"):
                    run_pre_outcome_pipeline(bundle)
                export.assert_not_called()

    def test_direct_stage_requires_explicit_actor_blinding_before_base_work(self):
        fixture = fixtures.V2WorkerIntegrationTests()
        for key in ("owner_outcome_blinding_status", "supervisor_outcome_blinding_status"):
            for value in ("DELETE", None, "UNKNOWN", "OUTCOME_VIEWED", False):
                epoch = fixture.epoch()
                if value == "DELETE":
                    del epoch[key]
                else:
                    epoch[key] = value
                snapshot = fixtures.FakeSnapshot({ACTIVE_EPOCH_PATH: epoch})
                with self.subTest(actor=key, value=value), patch.object(CanonicalStageExecutor, "execute") as base:
                    with self.assertRaisesRegex(StageBlocked, "V2_EPOCH_CONTAMINATED"):
                        V2StageExecutor().execute(snapshot, {"task_id": "TEST", "task_type": "FUNDAMENTAL_RESEARCH"},
                                                  "fundamental_events", "document_or_fundamental_research",
                                                  "2026-10-20T02:00:00Z", "test-worker")
                    base.assert_not_called()

    def test_real_git_worker_rejects_contamination_before_claim_or_model_call(self):
        fixture = fixtures.V2WorkerIntegrationTests()
        self.addCleanup(fixture.doCleanups)
        harness, worker = fixture.real_worker()
        with harness.store.snapshot() as snapshot:
            epoch = snapshot.read(ACTIVE_EPOCH_PATH)
            epoch["contamination_status"] = "BROKEN"
        subprocess.run(["git", "-C", str(harness.seed), "pull", str(harness.remote), "recovery"],
                       capture_output=True, check=True)
        (harness.seed / ACTIVE_EPOCH_PATH).write_text(json.dumps(epoch))
        git_fixtures.git(harness.seed, "add", ACTIVE_EPOCH_PATH)
        git_fixtures.git(harness.seed, "commit", "-m", "synthetic owner contamination metadata")
        git_fixtures.git(harness.seed, "push", str(harness.remote), "HEAD:recovery")
        with harness.store.snapshot() as snapshot:
            before = snapshot.head
        calls_before = deepcopy(harness.model.calls)
        with self.assertRaisesRegex(StageBlocked, "V2_EPOCH_CONTAMINATED"):
            worker.wake()
        with harness.store.snapshot() as snapshot:
            self.assertEqual(snapshot.head, before)
        self.assertEqual(harness.model.calls, calls_before)

    def test_explicit_clean_blinded_fixture_keeps_exact_qualified_receipt(self):
        bundle = self.bundle()
        before = deepcopy(bundle)
        result = run_pre_outcome_pipeline(bundle)
        # CP090 attributes the first proposal; only its trial/derived receipt changes.
        proposal = bundle["trial"]["generated_proposals"][0]
        self.assertEqual(proposal["hypothesis_id"], bundle["candidate"]["hypothesis_id"])
        self.assertEqual(proposal["generation_id"], bundle["candidate"]["generation_id"])
        self.assertEqual(proposal["candidate_hash"], result["candidate_hash"])
        self.assertEqual(result["receipt_hash"], "48ec56afa0be00bcd198c38a37b49c89f2b0d00d05b7f055346e887f7b2480e8")
        self.assertEqual(bundle, before)
        for actor in ("owner_status", "supervisor_status"):
            broken = deepcopy(bundle)
            broken["blinding"][actor] = "OUTCOME_VIEWED"
            with self.subTest(actor=actor), self.assertRaisesRegex(V2ContractError, "BLINDING_INTEGRITY_BROKEN"):
                run_pre_outcome_pipeline(broken)
