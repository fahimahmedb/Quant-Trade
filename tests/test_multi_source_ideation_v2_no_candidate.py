from __future__ import annotations

import inspect
import unittest

from research.research_os import multi_source_ideation, multi_source_ideation_hardening, ideation_cycle


class NoCandidateCreationTests(unittest.TestCase):
    def test_new_modules_expose_no_candidate_constructor(self):
        for module in (multi_source_ideation,multi_source_ideation_hardening,ideation_cycle):
            names={name.lower() for name,_ in inspect.getmembers(module)}
            self.assertNotIn("candidate",names); self.assertNotIn("create_candidate",names)


if __name__ == "__main__": unittest.main()
