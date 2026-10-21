from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation_hardening import SourceClaimLedger


class SourceClaimReuseTests(unittest.TestCase):
    def test_released_source_can_be_reclaimed_without_scientific_consumption(self):
        ledger=SourceClaimLedger()
        first=ledger.claim(source_identity="packet:a",context_snapshot_hash="h",policy_kind="SYSTEMATIC_COVERAGE")
        ledger.transition(first["claim_id"],"RELEASED")
        second=ledger.claim(source_identity="packet:a",context_snapshot_hash="h",policy_kind="DIVERGENT_EXPLORATION")
        self.assertEqual(second["state"],"HELD"); self.assertFalse(second["scientifically_consumed"])
        self.assertNotEqual(first["claim_id"],second["claim_id"])

    def test_transferred_source_cannot_be_reclaimed_in_same_context(self):
        ledger=SourceClaimLedger()
        first=ledger.claim(source_identity="packet:a",context_snapshot_hash="h",policy_kind="SYSTEMATIC_COVERAGE")
        ledger.transition(first["claim_id"],"TRANSFERRED")
        with self.assertRaises(ValueError): ledger.claim(source_identity="packet:a",context_snapshot_hash="h",policy_kind="DIVERGENT_EXPLORATION")


if __name__ == "__main__": unittest.main()
