from __future__ import annotations

import inspect
import unittest

from research.research_os import ideation_cycle, multi_source_ideation, multi_source_ideation_hardening


class NoScientificConsumptionTests(unittest.TestCase):
    def test_no_function_claims_scientific_consumption_true(self):
        text="\n".join(inspect.getsource(m) for m in (ideation_cycle,multi_source_ideation,multi_source_ideation_hardening))
        self.assertNotIn('"scientifically_consumed": True',text)
        self.assertNotIn("'scientifically_consumed': True",text)


if __name__ == "__main__": unittest.main()
