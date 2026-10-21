from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation_hardening import DurableProposalLedger


class LedgerCollisionTests(unittest.TestCase):
    def test_same_proposal_id_cannot_be_rewritten(self):
        ledger=DurableProposalLedger(); ledger.persist({"proposal_id":"p","status":"ELIGIBLE_FOR_DISCOVERY","x":1})
        with self.assertRaises(ValueError): ledger.persist({"proposal_id":"p","status":"ELIGIBLE_FOR_DISCOVERY","x":2})


if __name__ == "__main__": unittest.main()
