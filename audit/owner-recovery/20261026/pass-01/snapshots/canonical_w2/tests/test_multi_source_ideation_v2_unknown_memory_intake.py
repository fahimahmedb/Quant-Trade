from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import qualify_for_discovery

class UnknownMemoryIntakeTests(unittest.TestCase):
    def test_unknown_memory_does_not_become_known_negative(self):
        got=qualify_for_discovery(proposal={"artifact_kind":"IDEA_PROPOSAL","context_snapshot_hash":"h"},context_snapshot_hash="h",memory={"classification":"UNKNOWN"},duplicate={"classification":"DISTINCT"},implementability={"admissible":True})
        self.assertEqual(got["decision"],"ELIGIBLE_FOR_DISCOVERY")
        self.assertTrue(got["eligible_for_discovery"])

if __name__ == "__main__": unittest.main()
