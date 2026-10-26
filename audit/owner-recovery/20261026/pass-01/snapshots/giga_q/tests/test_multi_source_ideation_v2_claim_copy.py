from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import SourceClaimLedger

class ClaimCopyTests(unittest.TestCase):
    def test_claim_results_are_defensive_copies(self):
        l=SourceClaimLedger(); a=l.claim(source_identity="s",context_snapshot_hash="h",policy_kind="SYSTEMATIC_COVERAGE")
        a["state"]="CORRUPTED"; self.assertEqual(l.snapshot()[0]["state"],"HELD")

if __name__ == "__main__": unittest.main()
