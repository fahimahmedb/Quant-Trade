from __future__ import annotations
import unittest
from research.research_os.ideation_cycle import proposal_disposition

class DispositionReadyTests(unittest.TestCase):
    def test_ready_is_not_valid_passive_disposition(self):
        with self.assertRaises(ValueError): proposal_disposition(proposal_id="p",intake_decision={"decision":"READY","eligible_for_discovery":True},lineage={},duplicate={},implementability={})

if __name__ == "__main__": unittest.main()
