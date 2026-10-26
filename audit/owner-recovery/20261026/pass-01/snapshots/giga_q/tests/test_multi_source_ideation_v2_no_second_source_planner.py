from __future__ import annotations

import inspect
import unittest

from research.research_os import multi_source_ideation_bindings


class NoSecondSourcePlannerTests(unittest.TestCase):
    def test_systematic_binding_does_not_scan_files_or_rank_sources(self):
        src=inspect.getsource(multi_source_ideation_bindings.systematic_coverage_from_frontier).lower()
        for token in ("glob(","rglob(","listdir(","sorted(source","rank_source","score_source"):
            self.assertNotIn(token,src)
        self.assertIn("source_plan",src)


if __name__ == "__main__": unittest.main()
