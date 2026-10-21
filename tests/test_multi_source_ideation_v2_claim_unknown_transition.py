from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import SourceClaimLedger

class ClaimUnknownTransitionTests(unittest.TestCase):
    def test_unknown_claim_id_and_invalid_target_fail(self):
        ledger=SourceClaimLedger()
        with self.assertRaises(ValueError): ledger.transition("missing","READY")
        with self.assertRaises(KeyError): ledger.transition("missing","RELEASED")

if __name__ == "__main__": unittest.main()
