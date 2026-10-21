from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import qualify_for_discovery

class HardenedIntakeNoReadyTests(unittest.TestCase):
    def test_hardened_intake_never_returns_ready(self):
        got=qualify_for_discovery(proposal={"artifact_kind":"IDEA_PROPOSAL","context_snapshot_hash":"h"},context_snapshot_hash="h",memory={"classification":"NO_QUALIFIED_MATCH"},duplicate={"classification":"DISTINCT"},implementability={"admissible":True})
        self.assertEqual(got["boundary"],"ELIGIBLE_FOR_DISCOVERY"); self.assertFalse(got["ready_task_created"])

if __name__ == "__main__": unittest.main()
