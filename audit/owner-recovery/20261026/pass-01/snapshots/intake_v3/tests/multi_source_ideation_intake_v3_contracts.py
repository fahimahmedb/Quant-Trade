"""Canonical unittest bridge for Multi-Source Ideation Intake V3 qualification."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _REPO_ROOT / "src"
for path in (str(_REPO_ROOT), str(_SRC_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

_TEST_FILE = _REPO_ROOT / "research" / "research_os" / "tests" / "test_ideation_intake_v3.py"


def load_tests(
    loader: unittest.TestLoader,
    standard_tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    del pattern
    if not _TEST_FILE.is_file():
        raise AssertionError(f"ideation intake contract test module missing: {_TEST_FILE}")
    spec = importlib.util.spec_from_file_location("_ideation_intake_v3_contracts", _TEST_FILE)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load ideation intake V3 contract tests")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    suite = unittest.TestSuite()
    suite.addTests(standard_tests)
    suite.addTests(loader.loadTestsFromModule(module))
    return suite


class IdeationIntakeBridgeShapeTests(unittest.TestCase):
    def test_contract_test_source_exists(self):
        self.assertTrue(_TEST_FILE.is_file())


if __name__ == "__main__":
    unittest.main()
