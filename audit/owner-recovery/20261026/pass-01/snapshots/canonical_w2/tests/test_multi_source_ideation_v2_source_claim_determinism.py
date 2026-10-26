from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import SourceClaimLedger

class ClaimDeterminismTests(unittest.TestCase):
    def test_same_claim_inputs_have_same_identity_across_ledgers(self):
        kw={"source_identity":"packet:x","context_snapshot_hash":"h","policy_kind":"SYSTEMATIC_COVERAGE"}
        a=SourceClaimLedger().claim(**kw); b=SourceClaimLedger().claim(**kw)
        self.assertEqual(a["claim_id"],b["claim_id"])

if __name__ == "__main__": unittest.main()
