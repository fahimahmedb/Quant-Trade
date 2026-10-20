"""Adversarial admission checks; no Evaluation store or transport is accessed."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from research.research_os.expansion.v2_core import (
    ALLOWED_REVERSE_MESSAGES, V2ContractError, build_evaluation_ingest_receipt,
    canonical_hash, classify_model_pit, validate_reverse_message,
)
from research.research_os.expansion.v2_pipeline import run_pre_outcome_pipeline


class EvaluationMembraneAdmissionTests(unittest.TestCase):
    def bundle(self):
        return json.loads((Path(__file__).parent / "fixtures/oracle_v2_core_fixture.json").read_text())

    def receipt(self):
        return build_evaluation_ingest_receipt(export_bundle_hash="a" * 64)

    def test_each_technical_receipt_kind_is_accepted_for_its_expected_bundle(self):
        for kind in ALLOWED_REVERSE_MESSAGES:
            receipt = build_evaluation_ingest_receipt(export_bundle_hash="a" * 64, message=kind)
            validate_reverse_message(receipt, expected_export_bundle_hash="a" * 64)
            self.assertEqual(set(receipt), {"event_type", "message", "export_bundle_hash", "receipt_hash"})
            self.assertEqual(receipt, build_evaluation_ingest_receipt(export_bundle_hash="a" * 64, message=kind))

    def test_missing_extra_or_outcome_fields_cannot_cross_reverse_interface(self):
        for key in self.receipt():
            receipt = self.receipt()
            del receipt[key]
            with self.subTest(missing=key), self.assertRaises(V2ContractError):
                validate_reverse_message(receipt)
        for key in ("evaluation_summary", "completion", "retry", "blocker", "metrics", "rank"):
            receipt = self.receipt()
            receipt[key] = "synthetic forbidden side payload"
            receipt["receipt_hash"] = canonical_hash({k: v for k, v in receipt.items() if k != "receipt_hash"})
            with self.subTest(extra=key), self.assertRaises(V2ContractError):
                validate_reverse_message(receipt)
        for malformed in (None, [], "EXPORT_ACCEPTED", {"message": []}):
            with self.subTest(malformed=malformed), self.assertRaises(V2ContractError):
                validate_reverse_message(malformed)

    def test_export_references_are_sha256_values_not_structured_side_payloads(self):
        for value in (None, "", "a" * 63, "x" * 64, "A" * 64, True, 1, [], {"summary": "synthetic"}):
            with self.subTest(value=value):
                with self.assertRaisesRegex(V2ContractError, "INVALID_EXPORT_BUNDLE_HASH"):
                    build_evaluation_ingest_receipt(export_bundle_hash=value)
                receipt = self.receipt()
                receipt["export_bundle_hash"] = value
                with self.assertRaisesRegex(V2ContractError, "INVALID_EXPORT_BUNDLE_HASH"):
                    validate_reverse_message(receipt)

    def test_receipt_event_and_self_hash_cannot_be_tampered_with(self):
        for key, value in (("event_type", "EVALUATION_COMPLETE"), ("receipt_hash", None),
                           ("receipt_hash", "b" * 64), ("message", "INTEGRITY_FAILURE"),
                           ("export_bundle_hash", "b" * 64)):
            receipt = self.receipt()
            receipt[key] = value
            with self.subTest(field=key, value=value), self.assertRaises(V2ContractError):
                validate_reverse_message(receipt)

    def test_valid_foreign_receipt_cannot_acknowledge_the_expected_export(self):
        receipt = build_evaluation_ingest_receipt(export_bundle_hash="b" * 64)
        with self.assertRaisesRegex(V2ContractError, "EXPORT_BINDING_MISMATCH"):
            validate_reverse_message(receipt, expected_export_bundle_hash="a" * 64)
        for value in ("", "x" * 64, 1, {}):
            with self.subTest(expected=value), self.assertRaisesRegex(V2ContractError, "INVALID_EXPECTED"):
                validate_reverse_message(receipt, expected_export_bundle_hash=value)

    def test_pipeline_checks_receipt_binding_even_when_receipt_self_hash_is_valid(self):
        foreign = self.receipt()
        with patch("research.research_os.expansion.v2_pipeline.build_evaluation_ingest_receipt", return_value=foreign):
            with self.assertRaisesRegex(V2ContractError, "EXPORT_BINDING_MISMATCH"):
                run_pre_outcome_pipeline(self.bundle())

    def test_pipeline_does_not_coerce_unqualified_proof_flags_to_true(self):
        for key in ("validator_independence_qualified", "feedback_lineage_qualified", "bounded_orchestration_qualified"):
            for value in (False, None, "false", "true", 0, 1, [], {}, [True]):
                bundle = self.bundle()
                bundle[key] = value
                with self.subTest(proof=key, value=value), self.assertRaisesRegex(V2ContractError, "V2_QUALIFICATION_BLOCKED"):
                    run_pre_outcome_pipeline(bundle)

    def test_pipeline_requires_coherent_source_model_classification_without_hindsight_upgrade(self):
        invalid = (None, "false", {}, {"source_pit": True},
                   {"source_pit": "PASS", "model_pit": []},
                   {"source_pit": "PASS", "model_pit": "NOT_PROVABLE", "historical_generation_status": "SOURCE_AND_MODEL_PIT"},
                   classify_model_pit(source_pit=False, model_knowledge_cutoff_status="NOT_PROVABLE"))
        for declaration in invalid:
            bundle = self.bundle()
            bundle["leakage_classification"] = declaration
            with self.subTest(declaration=declaration), self.assertRaises(V2ContractError):
                run_pre_outcome_pipeline(bundle)
        for cutoff in ("PROVABLY_BEFORE_CUTOFF", "NOT_PROVABLE", "AFTER_CUTOFF"):
            bundle = self.bundle()
            bundle["leakage_classification"] = classify_model_pit(source_pit=True, model_knowledge_cutoff_status=cutoff)
            result = run_pre_outcome_pipeline(bundle)
            self.assertEqual(result["status"], "READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY")
            self.assertTrue(all(value is False for value in result["authority"].values()))
            self.assertFalse(result["outcome_accessed"])


if __name__ == "__main__":
    unittest.main()
