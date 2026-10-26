from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import qualify_for_discovery

class ConditionalNegativeTests(unittest.TestCase):
    def test_family_conditional_negative_is_not_silently_exact_suppression(self):
        got=qualify_for_discovery(proposal={"artifact_kind":"IDEA_PROPOSAL","context_snapshot_hash":"h"},context_snapshot_hash="h",memory={"classification":"KNOWN_FAMILY_CONDITIONAL_NEGATIVE"},duplicate={"classification":"DISTINCT"},implementability={"admissible":True})
        self.assertEqual(got["decision"],"ELIGIBLE_FOR_DISCOVERY")

if __name__ == "__main__": unittest.main()
