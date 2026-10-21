from __future__ import annotations
import threading
import unittest
from research.research_os.multi_source_ideation_hardening import DurableProposalLedger

class ProposalLedgerConcurrentCollisionTests(unittest.TestCase):
    def test_concurrent_conflicting_same_identity_has_one_canonical_record(self):
        l=DurableProposalLedger(); outcomes=[]
        def run(x):
            try: l.persist({"proposal_id":"p","x":x}); outcomes.append("OK")
            except ValueError: outcomes.append("COLLISION")
        ts=[threading.Thread(target=run,args=(x,)) for x in (1,2)]
        for t in ts:t.start()
        for t in ts:t.join()
        self.assertEqual(outcomes.count("OK"),1); self.assertEqual(outcomes.count("COLLISION"),1); self.assertEqual(len(l.snapshot()),1)

if __name__ == "__main__": unittest.main()
