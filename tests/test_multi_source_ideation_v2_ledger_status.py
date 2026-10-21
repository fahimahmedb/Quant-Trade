from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import DurableProposalLedger

class LedgerStatusTests(unittest.TestCase):
    def test_operational_statuses_are_forbidden_case_insensitively(self):
        for status in ("READY","ready","LEASED","running","Retry"):
            with self.subTest(status=status):
                with self.assertRaises(ValueError): DurableProposalLedger().persist({"proposal_id":"p","status":status})

if __name__ == "__main__": unittest.main()
