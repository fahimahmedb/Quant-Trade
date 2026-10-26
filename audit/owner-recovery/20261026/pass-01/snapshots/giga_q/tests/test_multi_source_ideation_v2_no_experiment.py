from __future__ import annotations

import inspect
import unittest

from research.research_os import multi_source_ideation, multi_source_ideation_hardening, ideation_cycle


class NoExperimentCreationTests(unittest.TestCase):
    def test_new_modules_expose_no_experiment_or_verdict_constructor(self):
        for module in (multi_source_ideation,multi_source_ideation_hardening,ideation_cycle):
            names={name.lower() for name,_ in inspect.getmembers(module)}
            for forbidden in ("experiment","validator","red_team","scientific_verdict","economic_identity"):
                self.assertNotIn(forbidden,names)


if __name__ == "__main__": unittest.main()
