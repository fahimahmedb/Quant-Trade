from __future__ import annotations
import unittest
from research.research_os.ideation_cycle import proposal_disposition

class DispositionReviewTests(unittest.TestCase):
    def test_review_required_disposition_stays_closed(self):
        d=proposal_disposition(proposal_id="p",intake_decision={"decision":"REVIEW_REQUIRED","eligible_for_discovery":False},lineage={},duplicate={"classification":"UNKNOWN"},implementability={})
        self.assertFalse(d["eligible_for_discovery"]); self.assertFalse(d["operational_admission"])

if __name__ == "__main__": unittest.main()
