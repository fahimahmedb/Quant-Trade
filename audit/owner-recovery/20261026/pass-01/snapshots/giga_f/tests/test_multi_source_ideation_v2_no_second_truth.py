from __future__ import annotations

import inspect
import unittest

from research.research_os import multi_source_ideation_bindings


class NoSecondTruthTests(unittest.TestCase):
    def test_binding_has_no_information_value_ranking_algorithm(self):
        src=inspect.getsource(multi_source_ideation_bindings.information_value_from_research_intelligence)
        for token in ("sorted(","min(","max(","cost_units <","falsification_power >"):
            self.assertNotIn(token,src)
        self.assertIn("RESEARCH_INTELLIGENCE_REUSED_NOT_REIMPLEMENTED",src)


if __name__ == "__main__": unittest.main()
