from __future__ import annotations

import unittest
from unittest.mock import patch

from research.research_os.expansion.validation_v2 import (
    _trial_accounting_identity_matches_candidate,
    validator_economic_readiness_v3,
)


class TrialAccountingIdentityBindingTests(unittest.TestCase):
    def test_legacy_accounting_without_lineage_remains_compatible(self):
        bundle = {
            "candidate": {"hypothesis_id": "H-1", "generation_id": "G-1"},
            "trial_accounting": {
                "observed_attempt_count": 0,
                "effective_trials_status": "UNKNOWN",
                "estimated_effective_trials": None,
            },
        }
        ok, _ = _trial_accounting_identity_matches_candidate(bundle)
        self.assertTrue(ok)

    def test_enriched_accounting_must_match_candidate_identity(self):
        bundle = {
            "candidate": {"hypothesis_id": "H-1", "generation_id": "G-1"},
            "trial_accounting": {
                "hypothesis_id": "H-1",
                "generation_id": "G-1",
            },
        }
        ok, _ = _trial_accounting_identity_matches_candidate(bundle)
        self.assertTrue(ok)

        bundle["trial_accounting"]["generation_id"] = "G-OTHER"
        ok, detail = _trial_accounting_identity_matches_candidate(bundle)
        self.assertFalse(ok)
        self.assertIn("exactly match", detail)

    def test_partial_enriched_identity_is_fail_closed(self):
        bundle = {
            "candidate": {"hypothesis_id": "H-1", "generation_id": "G-1"},
            "trial_accounting": {"hypothesis_id": "H-1"},
        }
        ok, detail = _trial_accounting_identity_matches_candidate(bundle)
        self.assertFalse(ok)
        self.assertIn("together", detail)

    def test_primary_validator_blocks_lineage_drift(self):
        bundle = {
            "candidate": {"hypothesis_id": "H-1", "generation_id": "G-1"},
            "trial_accounting": {
                "hypothesis_id": "H-OTHER",
                "generation_id": "G-1",
            },
        }
        core_receipt = {
            "status": "READY_FOR_AUTHORIZED_ECONOMIC_TEST",
            "ready_for_authorized_economic_test": True,
            "claim_ceiling": "READY_FOR_AUTHORIZED_ECONOMIC_TEST",
            "checks": {
                "trial_accounting": {
                    "status": "PASS",
                    "reason_code": None,
                    "detail": "numeric accounting valid",
                }
            },
            "block_reasons": [],
        }
        with patch(
            "research.research_os.expansion.validation_readiness.validate_economic_test_readiness",
            return_value=core_receipt,
        ):
            receipt = validator_economic_readiness_v3(readiness_bundle=bundle)

        self.assertEqual(receipt["status"], "BLOCK")
        self.assertFalse(receipt["ready_for_authorized_economic_test"])
        self.assertEqual(receipt["checks"]["trial_accounting"]["status"], "FAIL")
        self.assertEqual(
            receipt["checks"]["trial_accounting"]["reason_code"],
            "TRIAL_ACCOUNTING_INVALID",
        )
        self.assertEqual(receipt["claim_ceiling"], "BLOCKED_PRE_OUTCOME")
        self.assertEqual(receipt["block_reasons"][0]["check"], "trial_accounting")


if __name__ == "__main__":
    unittest.main()
