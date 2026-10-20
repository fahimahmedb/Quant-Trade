"""Scientific metadata cannot qualify contradictory or untyped declarations."""
import json
from pathlib import Path
import unittest

from research.research_os.expansion.v2_core import (
    V2ContractError, build_validator_result, classify_model_pit,
)
from research.research_os.expansion.v2_pipeline import run_pre_outcome_pipeline


class ScientificClaimAdmissionTests(unittest.TestCase):
    def bundle(self):
        return json.loads((Path(__file__).parent / "fixtures/oracle_v2_core_fixture.json").read_text())

    def test_outstanding_blockers_cannot_pass_directly_or_through_export_pipeline(self):
        for blockers in (["SOURCE_PIT_MISSING"], [None], [False], [{}]):
            with self.subTest(blockers=blockers):
                bundle = self.bundle()
                bundle["validator"]["epistemic_blockers"] = blockers
                for operation in (lambda: build_validator_result(bundle["validator"]),
                                  lambda: run_pre_outcome_pipeline(bundle)):
                    with self.assertRaisesRegex(V2ContractError, "PASS_WITH_EPISTEMIC_BLOCKERS"):
                        operation()

    def test_validator_requires_attributable_subject_and_actor(self):
        for key in ("hypothesis_id", "generation_id", "validator_identity"):
            for value in (None, "", " ", False, 1, [], {}, "UNKNOWN", "UNRESOLVED"):
                with self.subTest(field=key, value=value):
                    payload = self.bundle()["validator"]
                    payload[key] = value
                    with self.assertRaisesRegex(V2ContractError, "VALIDATOR_INVALID_IDENTIFIER"):
                        build_validator_result(payload)

    def test_source_pit_requires_boolean_and_preserves_hindsight_distinction(self):
        for cutoff in ("PROVABLY_BEFORE_CUTOFF", "NOT_PROVABLE", "AFTER_CUTOFF"):
            for value in (None, "false", "true", 0, 1, [], {}, [True]):
                with self.subTest(cutoff=cutoff, source_pit=value):
                    with self.assertRaisesRegex(V2ContractError, "INVALID_SOURCE_PIT_STATUS"):
                        classify_model_pit(source_pit=value, model_knowledge_cutoff_status=cutoff)
            result = classify_model_pit(source_pit=False, model_knowledge_cutoff_status=cutoff)
            self.assertEqual(result["source_pit"], "FAIL")
            self.assertEqual(result["historical_generation_status"], "SOURCE_NOT_PIT")
        self.assertEqual(classify_model_pit(source_pit=True, model_knowledge_cutoff_status="NOT_PROVABLE"), {
            "source_pit": "PASS", "model_pit": "NOT_PROVABLE",
            "historical_generation_status": "HISTORICAL_IDEA_GENERATION_NOT_PROVABLY_PIT",
        })

    def test_valid_pass_hash_and_block_failure_state_separation_are_preserved(self):
        payload = self.bundle()["validator"]
        self.assertEqual(build_validator_result(payload)["validator_hash"],
                         "45bb2e3c401ae635867bb9b89825bda5cdd6e0624c3cd9bf5304a5fed903aeb4")
        for blockers in ([], ["SOURCE_PIT_MISSING"]):
            payload["scientific_decision"] = "BLOCK"
            payload["epistemic_blockers"] = blockers
            self.assertEqual(build_validator_result(payload)["scientific_decision"], "BLOCK")
        payload.pop("scientific_decision")
        payload["execution_state"] = "RETRYABLE_ERROR"
        self.assertNotIn("scientific_decision", build_validator_result(payload))


if __name__ == "__main__":
    unittest.main()
