from __future__ import annotations

import importlib
import unittest


class IdeationModuleImportTests(unittest.TestCase):
    def test_all_new_modules_import_from_repository_root(self):
        for name in (
            "research.research_os.multi_source_ideation",
            "research.research_os.multi_source_ideation_bindings",
            "research.research_os.multi_source_ideation_hardening",
            "research.research_os.ideation_cycle",
        ):
            with self.subTest(name=name): self.assertIsNotNone(importlib.import_module(name))


if __name__ == "__main__": unittest.main()
