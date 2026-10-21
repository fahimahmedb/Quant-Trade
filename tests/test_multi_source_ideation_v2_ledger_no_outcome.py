from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import DurableProposalLedger

class LedgerNoOutcomeTests(unittest.TestCase):
    def test_ledger_does_not_add_outcome_or_economic_fields(self):
        row={"proposal_id":"p","status":"ELIGIBLE_FOR_DISCOVERY"}; l=DurableProposalLedger(); l.persist(row); got=l.snapshot()[0]
        self.assertEqual(got,row); self.assertNotIn("economic_result",got); self.assertNotIn("scientific_verdict",got)

if __name__ == "__main__": unittest.main()
