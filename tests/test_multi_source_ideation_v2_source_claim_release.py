from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import SourceClaimLedger

class SourceClaimReleaseTests(unittest.TestCase):
    def test_release_permits_new_policy_claim_but_not_scientific_consumption(self):
        l=SourceClaimLedger(); a=l.claim(source_identity="s",context_snapshot_hash="h",policy_kind="SYSTEMATIC_COVERAGE"); l.transition(a["claim_id"],"RELEASED"); b=l.claim(source_identity="s",context_snapshot_hash="h",policy_kind="INFORMATION_VALUE")
        self.assertEqual(b["policy_kind"],"INFORMATION_VALUE"); self.assertFalse(b["scientifically_consumed"])

if __name__ == "__main__": unittest.main()
