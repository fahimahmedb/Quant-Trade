from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import SourceClaimLedger

class SourceClaimNewContextTests(unittest.TestCase):
    def test_transferred_source_in_old_context_does_not_claim_new_context(self):
        l=SourceClaimLedger(); a=l.claim(source_identity="s",context_snapshot_hash="old",policy_kind="SYSTEMATIC_COVERAGE"); l.transition(a["claim_id"],"TRANSFERRED"); b=l.claim(source_identity="s",context_snapshot_hash="new",policy_kind="DIVERGENT_EXPLORATION")
        self.assertEqual(b["state"],"HELD"); self.assertNotEqual(a["claim_id"],b["claim_id"])

if __name__ == "__main__": unittest.main()
