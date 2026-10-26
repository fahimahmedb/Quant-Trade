from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import intake


class SeedBoundaryTests(unittest.TestCase):
    def test_seed_can_enter_discovery_synthesis_but_is_not_proposal_admission(self):
        got=intake(artifact={"artifact_kind":"IDEATION_SEED","context_snapshot_hash":"h"},memory_check={},duplicate={},implementability={},current_context_hash="h")
        self.assertEqual(got["decision"],"NEEDS_DISCOVERY_SYNTHESIS")
        self.assertTrue(got["eligible_for_discovery"])
        self.assertNotEqual(got["decision"],"ELIGIBLE_FOR_DISCOVERY")


if __name__ == "__main__": unittest.main()
