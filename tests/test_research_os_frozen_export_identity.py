"""Frozen exports preserve the exact validated Candidate and complete hash."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from tests import test_research_os_v2_worker_integration as worker_fixtures
from research.research_os.expansion.v2_bridge import adapt_existing_validation_to_v2
from research.research_os.expansion.v2_core import (
    V2ContractError, assert_validator_candidate_binding, build_candidate,
    build_frozen_export_intent, canonical_hash,
)
from research.research_os.expansion.v2_independence import AXES
from research.research_os.expansion.v2_pipeline import run_pre_outcome_pipeline
from research.research_os.worker_stages import StageBlocked


class FrozenExportIdentityTests(unittest.TestCase):
    def bundle(self):
        return json.loads((Path(__file__).parent / "fixtures/oracle_v2_core_fixture.json").read_text())

    def test_export_cannot_change_validated_economic_meaning(self):
        changes = {"universe": ["DIFFERENT"], "clock": "other_clock", "horizon": "300d",
                   "economic_expression": {"instrument": "other", "direction": "short"}}
        for key, value in changes.items():
            bundle = self.bundle()
            bundle["export"][key] = value
            with self.subTest(field=key), self.assertRaisesRegex(V2ContractError, "EXPORT_BINDING_MISMATCH:" + key):
                run_pre_outcome_pipeline(bundle)

    def test_export_auto_or_missing_fields_reuse_exact_candidate_facts(self):
        original = self.bundle()
        expected = run_pre_outcome_pipeline(original)
        for key in ("universe", "clock", "horizon", "economic_expression"):
            for mode in ("AUTO", None, "DELETE"):
                bundle = deepcopy(original)
                if mode == "DELETE":
                    del bundle["export"][key]
                else:
                    bundle["export"][key] = mode
                with self.subTest(field=key, mode=mode):
                    self.assertEqual(run_pre_outcome_pipeline(bundle), expected)
        self.assertEqual(original, self.bundle())

    def test_same_generation_cannot_reuse_validation_for_changed_candidate(self):
        corrupted = self.bundle()
        corrupted["validator"]["validator_hash"] = "b" * 64
        with self.assertRaisesRegex(V2ContractError, "VALIDATOR_HASH_MISMATCH"):
            run_pre_outcome_pipeline(corrupted)
        bundle = self.bundle()
        bundle["candidate"]["claim"] = "changed claim with unchanged hypothesis/generation IDs"
        with self.assertRaisesRegex(V2ContractError, "VALIDATOR_CANDIDATE_BINDING_MISMATCH"):
            run_pre_outcome_pipeline(bundle)
        for value in (None, "b" * 64, "DELETE"):
            bundle = self.bundle()
            if value == "DELETE":
                del bundle["validator"]["candidate_hash"]
            else:
                bundle["validator"]["candidate_hash"] = value
            with self.subTest(candidate_hash=value), self.assertRaisesRegex(V2ContractError, "VALIDATOR_CANDIDATE_BINDING_MISMATCH"):
                run_pre_outcome_pipeline(bundle)

    def test_bridge_records_exact_candidate_hash_without_claiming_real_independence(self):
        candidate = build_candidate(self.bundle()["candidate"])
        result = adapt_existing_validation_to_v2(
            existing_validation={"status": "PASS", "failures": []}, v2_candidate=candidate,
            validator_identity="synthetic-validator", validator_version="test",
            validator_model="test", validator_prompt_hash="p", validator_context_hash="c",
            validator_retrieval_manifest_hash="r", producer_identity_hash="producer",
            validator_state_identity_hash="validator", independence_evidence=dict.fromkeys(AXES, True),
        )
        self.assertEqual(result["candidate_hash"], candidate["candidate_hash"])
        assert_validator_candidate_binding(candidate, result)

    def test_worker_blocks_unbound_tampered_or_contradictory_validator_before_export(self):
        read = worker_fixtures.FakeSnapshot.read
        for mutation in ("missing_binding", "foreign_binding", "bad_hash", "wrong_subject", "contradictory_pass"):
            def tampered_read(snapshot, path):
                value = deepcopy(read(snapshot, path))
                if path.endswith("/validator.json.json"):
                    if mutation == "missing_binding":
                        value.pop("candidate_hash")
                    elif mutation == "foreign_binding":
                        value["candidate_hash"] = "b" * 64
                    elif mutation == "bad_hash":
                        value["validator_hash"] = "b" * 64
                    elif mutation == "wrong_subject":
                        value["generation_id"] = "different-generation"
                    else:
                        value["epistemic_blockers"] = ["SOURCE_PIT_MISSING"]
                        value["validator_hash"] = canonical_hash({k: v for k, v in value.items() if k != "validator_hash"})
                return value
            with self.subTest(mutation=mutation), patch.object(worker_fixtures.FakeSnapshot, "read", tampered_read):
                with patch("research.research_os.expansion.v2_stage_executor.build_frozen_export_intent",
                           wraps=build_frozen_export_intent) as export:
                    with self.assertRaises(StageBlocked):
                        worker_fixtures.V2WorkerIntegrationTests().test_claim_restriction_can_emit_frozen_export_intent_without_evaluation()
                    export.assert_not_called()


if __name__ == "__main__":
    unittest.main()
