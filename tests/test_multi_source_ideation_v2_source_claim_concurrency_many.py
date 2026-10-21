from __future__ import annotations
import threading
import unittest
from research.research_os.multi_source_ideation_hardening import SourceClaimLedger

class SourceClaimConcurrencyManyTests(unittest.TestCase):
    def test_many_policies_same_source_yield_one_owner_per_context(self):
        l=SourceClaimLedger(); results=[]; policies=("SYSTEMATIC_COVERAGE","INFORMATION_VALUE","DIVERGENT_EXPLORATION")
        def run(p):
            try: l.claim(source_identity="s",context_snapshot_hash="h",policy_kind=p); results.append("OK")
            except ValueError: results.append("BLOCKED")
        ts=[threading.Thread(target=run,args=(p,)) for p in policies]
        for t in ts:t.start()
        for t in ts:t.join()
        self.assertEqual(results.count("OK"),1); self.assertEqual(results.count("BLOCKED"),2)

if __name__ == "__main__": unittest.main()
