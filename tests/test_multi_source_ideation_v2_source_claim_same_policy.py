from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import SourceClaimLedger

class SourceClaimSamePolicyTests(unittest.TestCase):
    def test_repeated_same_policy_claim_is_idempotent(self):
        l=SourceClaimLedger(); kw={"source_identity":"s","context_snapshot_hash":"h","policy_kind":"SYSTEMATIC_COVERAGE"}; a=l.claim(**kw); b=l.claim(**kw)
        self.assertEqual(a,b); self.assertEqual(len(l.snapshot()),1)

if __name__ == "__main__": unittest.main()
