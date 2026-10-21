from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import SourceClaimLedger

class SourceClaimTransferredTests(unittest.TestCase):
    def test_transferred_claim_blocks_other_policy_same_context(self):
        l=SourceClaimLedger(); a=l.claim(source_identity="s",context_snapshot_hash="h",policy_kind="SYSTEMATIC_COVERAGE"); l.transition(a["claim_id"],"TRANSFERRED")
        with self.assertRaises(ValueError): l.claim(source_identity="s",context_snapshot_hash="h",policy_kind="INFORMATION_VALUE")

if __name__ == "__main__": unittest.main()
