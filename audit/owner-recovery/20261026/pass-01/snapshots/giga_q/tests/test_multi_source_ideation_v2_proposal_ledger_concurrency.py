from __future__ import annotations
import threading
import unittest
from research.research_os.multi_source_ideation_hardening import DurableProposalLedger

class ProposalLedgerConcurrencyTests(unittest.TestCase):
    def test_concurrent_identical_persist_is_idempotent(self):
        l=DurableProposalLedger(); row={"proposal_id":"p","status":"ELIGIBLE_FOR_DISCOVERY"}; errors=[]
        def run():
            try: l.persist(row)
            except Exception as e: errors.append(e)
        ts=[threading.Thread(target=run) for _ in range(8)]
        for t in ts:t.start()
        for t in ts:t.join()
        self.assertEqual(errors,[]); self.assertEqual(len(l.snapshot()),1)

if __name__ == "__main__": unittest.main()
