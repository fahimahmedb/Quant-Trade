from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation_hardening import qualify_for_discovery


class DiscoveryStopTests(unittest.TestCase):
    def test_successful_boundary_contains_no_next_operational_action(self):
        got=qualify_for_discovery(proposal={"artifact_kind":"IDEA_PROPOSAL","context_snapshot_hash":"h"},context_snapshot_hash="h",memory={"classification":"NO_QUALIFIED_MATCH"},duplicate={"classification":"DISTINCT"},implementability={"admissible":True})
        self.assertEqual(got["boundary"],"ELIGIBLE_FOR_DISCOVERY")
        for forbidden in ("task_id","candidate_id","experiment_id","oracle_task_id","lease_id","producer_id"):
            self.assertNotIn(forbidden,got)


if __name__ == "__main__": unittest.main()
