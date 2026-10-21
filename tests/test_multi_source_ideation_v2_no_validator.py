from __future__ import annotations

import inspect
import unittest

from research.research_os import ideation_cycle, multi_source_ideation, multi_source_ideation_bindings, multi_source_ideation_hardening


class NoValidatorAuthorityTests(unittest.TestCase):
    def test_no_validator_redteam_execution_calls(self):
        text="\n".join(inspect.getsource(m).lower() for m in (ideation_cycle,multi_source_ideation,multi_source_ideation_bindings,multi_source_ideation_hardening))
        for token in ("run_validator(","run_red_team(","scientific_verdict=", "preregister_experiment("):
            self.assertNotIn(token,text)


if __name__ == "__main__": unittest.main()
