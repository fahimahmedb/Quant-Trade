"""Canonical CI bridge for the fixed Mega-A Research Intelligence contract tests.

The canonical GitHub Actions gate invokes this module explicitly. Mega-A implementation
tests live beside Research OS under ``research/research_os/tests``; this bridge deliberately
loads only the nine test modules introduced by Mega-A and therefore does not alter the V1
``unittest discover -s tests`` proof inventory used by STATE.md.

Most Mega-A modules use unittest.TestCase directly. ``test_research_intelligence.py``
contains zero-argument pytest-style functions; those are wrapped as FunctionTestCase so the
canonical unittest gate proves those adversarial contracts too, without adding a pytest
dependency or creating another workflow.
"""
from __future__ import annotations

import importlib.util
import inspect
import sys
import unittest
from pathlib import Path
from types import ModuleType

_REPO_ROOT = Path(__file__).resolve().parents[1]
_MEGA_A_TEST_FILES = (
    "research/research_os/tests/test_archaeology.py",
    "research/research_os/tests/test_memory_archaeology_bridge.py",
    "research/research_os/tests/test_scientific_memory.py",
    "research/research_os/tests/test_research_intelligence.py",
    "research/research_os/tests/test_research_refill_policy.py",
    "research/research_os/tests/test_scientific_memory_feedback.py",
    "research/research_os/tests/test_research_action_planner.py",
    "research/research_os/tests/test_legacy_memory_compatibility.py",
    "research/research_os/tests/test_research_chain.py",
)


def _load_module(relative_path: str, index: int) -> ModuleType:
    path = _REPO_ROOT / relative_path
    if not path.is_file():
        raise AssertionError(f"Mega-A contract test module missing: {relative_path}")
    module_name = f"_mega_a_contract_{index}_{path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load Mega-A contract test module: {relative_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_tests(loader: unittest.TestLoader, standard_tests: unittest.TestSuite, pattern: str | None) -> unittest.TestSuite:
    del pattern
    suite = unittest.TestSuite()
    suite.addTests(standard_tests)
    for index, relative_path in enumerate(_MEGA_A_TEST_FILES):
        module = _load_module(relative_path, index)
        suite.addTests(loader.loadTestsFromModule(module))
        for name, value in sorted(vars(module).items()):
            if not name.startswith("test_") or not inspect.isfunction(value):
                continue
            if inspect.signature(value).parameters:
                raise AssertionError(
                    f"Mega-A free test requires unsupported fixtures: {relative_path}::{name}"
                )
            suite.addTest(unittest.FunctionTestCase(value, description=f"{relative_path}::{name}"))
    return suite


class MegaAContractBridgeShapeTests(unittest.TestCase):
    def test_bridge_scope_is_fixed_and_all_sources_exist(self):
        self.assertEqual(len(_MEGA_A_TEST_FILES), 9)
        self.assertEqual(len(set(_MEGA_A_TEST_FILES)), len(_MEGA_A_TEST_FILES))
        for relative_path in _MEGA_A_TEST_FILES:
            self.assertTrue((_REPO_ROOT / relative_path).is_file(), relative_path)


if __name__ == "__main__":
    unittest.main()
