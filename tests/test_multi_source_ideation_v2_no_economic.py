from __future__ import annotations

import inspect
import unittest

from research.research_os import ideation_cycle, multi_source_ideation, multi_source_ideation_bindings, multi_source_ideation_hardening


class NoEconomicAuthorityTests(unittest.TestCase):
    def test_no_economic_result_creation_api(self):
        text="\n".join(inspect.getsource(m).lower() for m in (ideation_cycle,multi_source_ideation,multi_source_ideation_bindings,multi_source_ideation_hardening))
        for token in ("expected_return =","realized_return =","portfolio_weight =","economic_experiment_authorized=true","prospective_observation_authorized=true"):
            self.assertNotIn(token,text)


if __name__ == "__main__": unittest.main()
