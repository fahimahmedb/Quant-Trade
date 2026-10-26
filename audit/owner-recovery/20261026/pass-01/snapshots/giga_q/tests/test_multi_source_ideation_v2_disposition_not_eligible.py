from __future__ import annotations
import unittest
from research.research_os.ideation_cycle import proposal_disposition

class DispositionNotEligibleTests(unittest.TestCase):
    def test_not_eligible_disposition_stays_closed(self):
        d=proposal_disposition(proposal_id="p",intake_decision={"decision":"NOT_ELIGIBLE","eligible_for_discovery":False},lineage={"classification":"KNOWN_EXACT_NEGATIVE"},duplicate={},implementability={})
        self.assertFalse(d["eligible_for_discovery"]); self.assertFalse(d["operational_admission"])

if __name__ == "__main__": unittest.main()
