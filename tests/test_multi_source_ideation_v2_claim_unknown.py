from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import SourceClaimLedger

class ClaimUnknownTests(unittest.TestCase):
    def test_invalid_policy_and_empty_identity_fail(self):
        ledger=SourceClaimLedger()
        for kwargs in ({"source_identity":"","context_snapshot_hash":"h","policy_kind":"SYSTEMATIC_COVERAGE"},{"source_identity":"s","context_snapshot_hash":"","policy_kind":"SYSTEMATIC_COVERAGE"},{"source_identity":"s","context_snapshot_hash":"h","policy_kind":"UNKNOWN"}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError): ledger.claim(**kwargs)

if __name__ == "__main__": unittest.main()
