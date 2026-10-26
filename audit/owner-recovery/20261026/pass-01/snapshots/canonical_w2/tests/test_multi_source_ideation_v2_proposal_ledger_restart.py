from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import DurableProposalLedger

class ProposalLedgerRestartTests(unittest.TestCase):
    def test_restart_does_not_create_new_identity(self):
        row={"proposal_id":"p","status":"ELIGIBLE_FOR_DISCOVERY","context_snapshot_hash":"h"}; a=DurableProposalLedger(); self.assertEqual(a.persist(row),"p"); b=DurableProposalLedger(a.snapshot()); self.assertEqual(b.persist(row),"p")

if __name__ == "__main__": unittest.main()
