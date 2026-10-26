from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import side_effect_zeroes


class ZeroSideEffectTests(unittest.TestCase):
    def test_all_operational_side_effect_counters_are_zero(self):
        expected={"READY_TASKS_CREATED","CONTROL_PLANE_MUTATIONS","PRODUCERS_EXECUTED","ORACLE_MUTATIONS","SCHEDULER_MUTATIONS","CANDIDATES_CREATED"}
        got=side_effect_zeroes(); self.assertEqual(set(got),expected); self.assertTrue(all(v==0 for v in got.values()))


if __name__ == "__main__": unittest.main()
