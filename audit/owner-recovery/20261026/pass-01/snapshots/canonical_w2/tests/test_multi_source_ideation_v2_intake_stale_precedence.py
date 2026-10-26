from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import qualify_for_discovery

class StalePrecedenceTests(unittest.TestCase):
    def test_staleness_precedes_duplicate_or_memory_judgement(self):
        got=qualify_for_discovery(proposal={"artifact_kind":"IDEA_PROPOSAL","context_snapshot_hash":"old"},context_snapshot_hash="new",memory={"classification":"KNOWN_EXACT_NEGATIVE"},duplicate={"classification":"EXACT_DUPLICATE"},implementability={"admissible":False})
        self.assertEqual(got["decision"],"STALE_REQUALIFICATION_REQUIRED")

if __name__ == "__main__": unittest.main()
