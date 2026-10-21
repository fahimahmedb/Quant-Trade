from __future__ import annotations
import inspect
import unittest
from research.research_os.multi_source_ideation_hardening import SourceClaimLedger

class ClaimNotProposalLedgerTests(unittest.TestCase):
    def test_source_claim_ledger_has_no_proposal_persist_api(self):
        methods={n for n,_ in inspect.getmembers(SourceClaimLedger,inspect.isfunction)}
        self.assertNotIn("persist",methods); self.assertNotIn("enqueue",methods); self.assertIn("claim",methods); self.assertIn("transition",methods)

if __name__ == "__main__": unittest.main()
