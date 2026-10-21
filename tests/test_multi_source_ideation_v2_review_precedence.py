from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import qualify_for_discovery

class ReviewPrecedenceTests(unittest.TestCase):
    def test_unknown_duplicate_requires_review_when_other_gates_pass(self):
        got=qualify_for_discovery(proposal={"artifact_kind":"IDEA_PROPOSAL","context_snapshot_hash":"h"},context_snapshot_hash="h",memory={"classification":"NO_QUALIFIED_MATCH"},duplicate={"classification":"REVIEW_REQUIRED"},implementability={"admissible":True})
        self.assertEqual(got["decision"],"REVIEW_REQUIRED"); self.assertFalse(got["eligible_for_discovery"])

if __name__ == "__main__": unittest.main()
