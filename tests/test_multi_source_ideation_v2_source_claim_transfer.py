from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import SourceClaimLedger

class ClaimTransferTests(unittest.TestCase):
    def test_transfer_is_terminal_and_not_operational_admission(self):
        l=SourceClaimLedger(); c=l.claim(source_identity="s",context_snapshot_hash="h",policy_kind="SYSTEMATIC_COVERAGE"); t=l.transition(c["claim_id"],"TRANSFERRED")
        self.assertEqual(t["state"],"TRANSFERRED"); self.assertFalse(t["scientifically_consumed"])
        for forbidden in ("task_id","lease_id","worker_id","candidate_id"): self.assertNotIn(forbidden,t)

if __name__ == "__main__": unittest.main()
