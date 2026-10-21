from __future__ import annotations
import inspect
import unittest
from research.research_os.multi_source_ideation_hardening import DurableProposalLedger

class LedgerNoClaimTests(unittest.TestCase):
    def test_proposal_ledger_has_no_claim_or_lease_api(self):
        methods={n for n,_ in inspect.getmembers(DurableProposalLedger,inspect.isfunction)}
        self.assertNotIn("claim",methods); self.assertNotIn("lease",methods); self.assertNotIn("heartbeat",methods)

if __name__ == "__main__": unittest.main()
