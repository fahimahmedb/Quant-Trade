from __future__ import annotations
import unittest
from research.research_os.ideation_cycle import proposal_disposition

class DispositionStaleTests(unittest.TestCase):
    def test_stale_disposition_remains_ineligible(self):
        d=proposal_disposition(proposal_id="p",intake_decision={"decision":"STALE_REQUALIFICATION_REQUIRED","eligible_for_discovery":False},lineage={},duplicate={},implementability={})
        self.assertFalse(d["eligible_for_discovery"]); self.assertFalse(d["operational_admission"])

if __name__ == "__main__": unittest.main()
