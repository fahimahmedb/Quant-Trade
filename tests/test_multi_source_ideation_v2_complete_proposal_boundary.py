from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import qualify_for_discovery

class CompleteProposalBoundaryTests(unittest.TestCase):
    def test_complete_proposal_requires_intake_checks_before_eligibility(self):
        p={"artifact_kind":"IDEA_PROPOSAL","context_snapshot_hash":"h"}
        blocked=qualify_for_discovery(proposal=p,context_snapshot_hash="h",memory={"classification":"NO_QUALIFIED_MATCH"},duplicate={"classification":"DISTINCT"},implementability={"admissible":False})
        passed=qualify_for_discovery(proposal=p,context_snapshot_hash="h",memory={"classification":"NO_QUALIFIED_MATCH"},duplicate={"classification":"DISTINCT"},implementability={"admissible":True})
        self.assertEqual(blocked["decision"],"NOT_ELIGIBLE"); self.assertEqual(passed["decision"],"ELIGIBLE_FOR_DISCOVERY")

if __name__ == "__main__": unittest.main()
