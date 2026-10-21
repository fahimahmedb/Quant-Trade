from __future__ import annotations
import inspect
import unittest
from research.research_os import multi_source_ideation_bindings

class NoRiRecomputeTests(unittest.TestCase):
    def test_policy_b_does_not_compute_cost_or_falsification_ranking(self):
        src=inspect.getsource(multi_source_ideation_bindings.information_value_from_research_intelligence).lower()
        for token in ("cost_units +","cost_units -","falsification_power +","sorted(","min(","max("):
            self.assertNotIn(token,src)

if __name__ == "__main__": unittest.main()
