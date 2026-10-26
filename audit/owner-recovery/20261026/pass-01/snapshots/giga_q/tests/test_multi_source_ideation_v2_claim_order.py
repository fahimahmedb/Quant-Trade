from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import SourceClaimLedger

class ClaimOrderTests(unittest.TestCase):
    def test_claim_snapshot_is_deterministic(self):
        ledger=SourceClaimLedger(); ledger.claim(source_identity="z",context_snapshot_hash="h",policy_kind="SYSTEMATIC_COVERAGE"); ledger.claim(source_identity="a",context_snapshot_hash="h",policy_kind="INFORMATION_VALUE")
        self.assertEqual([r["source_identity"] for r in ledger.snapshot()],["a","z"])

if __name__ == "__main__": unittest.main()
