from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import DurableProposalLedger

class LedgerOrderTests(unittest.TestCase):
    def test_snapshot_order_is_deterministic_by_identity(self):
        ledger=DurableProposalLedger(); ledger.persist({"proposal_id":"z","status":"REVIEW_REQUIRED"}); ledger.persist({"proposal_id":"a","status":"ELIGIBLE_FOR_DISCOVERY"})
        self.assertEqual([r["proposal_id"] for r in ledger.snapshot()],["a","z"])

if __name__ == "__main__": unittest.main()
