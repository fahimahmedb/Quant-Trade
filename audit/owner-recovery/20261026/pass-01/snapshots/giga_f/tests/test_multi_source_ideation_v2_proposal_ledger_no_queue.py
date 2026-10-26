from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import DurableProposalLedger

class ProposalLedgerNoQueueTests(unittest.TestCase):
    def test_eligible_record_is_storage_only(self):
        l=DurableProposalLedger(); l.persist({"proposal_id":"p","status":"ELIGIBLE_FOR_DISCOVERY"}); row=l.snapshot()[0]
        self.assertEqual(row["status"],"ELIGIBLE_FOR_DISCOVERY")
        for forbidden in ("lease","heartbeat","worker_owner","retry_at"): self.assertNotIn(forbidden,row)

if __name__ == "__main__": unittest.main()
