from __future__ import annotations
import unittest
from research.research_os.ideation_cycle import proposal_disposition

class DispositionCandidateTests(unittest.TestCase):
    def test_disposition_contains_no_candidate_or_task_identity(self):
        d=proposal_disposition(proposal_id="p",intake_decision={"decision":"ELIGIBLE_FOR_DISCOVERY","eligible_for_discovery":True},lineage={},duplicate={},implementability={"admissible":True})
        for forbidden in ("candidate_id","task_id","lease_id","experiment_id"): self.assertNotIn(forbidden,d)

if __name__ == "__main__": unittest.main()
