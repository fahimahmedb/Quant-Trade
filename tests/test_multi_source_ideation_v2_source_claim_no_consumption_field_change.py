from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import SourceClaimLedger

class ClaimConsumptionFieldTests(unittest.TestCase):
    def test_all_claim_snapshots_keep_scientific_consumption_false(self):
        l=SourceClaimLedger(); a=l.claim(source_identity="a",context_snapshot_hash="h",policy_kind="SYSTEMATIC_COVERAGE"); l.transition(a["claim_id"],"TRANSFERRED"); b=l.claim(source_identity="b",context_snapshot_hash="h",policy_kind="INFORMATION_VALUE"); l.transition(b["claim_id"],"RELEASED")
        self.assertTrue(all(r["scientifically_consumed"] is False for r in l.snapshot()))

if __name__ == "__main__": unittest.main()
