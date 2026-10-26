from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import intake


class StaleSeedTests(unittest.TestCase):
    def test_stale_seed_cannot_bypass_requalification(self):
        got=intake(artifact={"artifact_kind":"IDEATION_SEED","context_snapshot_hash":"old"},memory_check={},duplicate={},implementability={},current_context_hash="new")
        self.assertEqual(got["decision"],"STALE_REQUALIFICATION_REQUIRED"); self.assertFalse(got["eligible_for_discovery"])


if __name__ == "__main__": unittest.main()
