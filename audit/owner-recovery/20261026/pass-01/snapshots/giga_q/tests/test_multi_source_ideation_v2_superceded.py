from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import qualify_for_discovery

class SupersededMemoryTests(unittest.TestCase):
    def test_superseded_memory_blocks_direct_discovery_eligibility(self):
        got=qualify_for_discovery(proposal={"artifact_kind":"IDEA_PROPOSAL","context_snapshot_hash":"h"},context_snapshot_hash="h",memory={"classification":"SUPERSEDED"},duplicate={"classification":"DISTINCT"},implementability={"admissible":True})
        self.assertEqual(got["decision"],"NOT_ELIGIBLE")

if __name__ == "__main__": unittest.main()
