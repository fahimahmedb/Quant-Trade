from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import DurableProposalLedger

class LedgerForbiddenTests(unittest.TestCase):
    def test_queue_semantic_keys_are_forbidden(self):
        for key in ("lease","lease_owner","heartbeat","worker_owner","retry_at","scheduler_state"):
            with self.subTest(key=key):
                with self.assertRaises(ValueError): DurableProposalLedger().persist({"proposal_id":"p",key:"x"})

if __name__ == "__main__": unittest.main()
