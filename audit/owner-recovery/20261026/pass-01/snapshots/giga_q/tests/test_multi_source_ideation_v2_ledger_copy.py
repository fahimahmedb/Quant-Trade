from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import DurableProposalLedger

class LedgerCopyTests(unittest.TestCase):
    def test_persist_and_snapshot_are_defensive_copies(self):
        row={"proposal_id":"p","nested":{"x":1}}
        l=DurableProposalLedger(); l.persist(row); row["nested"]["x"]=2
        snap=l.snapshot(); self.assertEqual(snap[0]["nested"]["x"],1)
        snap[0]["nested"]["x"]=3; self.assertEqual(l.snapshot()[0]["nested"]["x"],1)

if __name__ == "__main__": unittest.main()
