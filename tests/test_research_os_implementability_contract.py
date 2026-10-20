"""Reject invalid declarations before expensive experiment preparation."""
from copy import deepcopy
import unittest

from research.research_os.expansion.final_shape import assess_implementability
from research.research_os.expansion.implementability_depth import _REQUIRED_EXPRESSION_FIELDS
from research.research_os.tests.test_implementability_depth import _complete_meta, _engine_output


class ImplementabilityDeclarationTests(unittest.TestCase):
    def test_boolean_or_nonfinite_expression_declarations_cannot_pass(self):
        fields = ("entry_clock", "exit_clock", "instrument", *_REQUIRED_EXPRESSION_FIELDS)
        for field in fields:
            for value in (False, True, float("nan"), float("inf"), -float("inf")):
                with self.subTest(field=field, value=value):
                    meta = _complete_meta()
                    meta["economic_expression"][field] = value
                    if field == "exit_clock":
                        del meta["economic_expression"]["horizon"]
                    if field == "instrument":
                        del meta["economic_expression"]["universe"]
                    output = _engine_output()
                    before = deepcopy(output)
                    result = assess_implementability(output, meta)
                    self.assertEqual(result["status"], "BLOCK_IMPLEMENTABILITY")
                    self.assertTrue(result["blocking_reasons"])
                    self.assertEqual(output, before)
                    self.assertTrue(all(v is False for v in result["authority"].values()))

    def test_explicit_unknown_clock_states_are_not_exact_clocks(self):
        for value in (" unavailable ", "Unspecified", "NOT_ESTIMATED", "UNKNOWN", " "):
            with self.subTest(value=value):
                meta = _complete_meta()
                meta["economic_expression"]["entry_clock"] = value
                result = assess_implementability(_engine_output(), meta)
                self.assertEqual(result["exact_clock_status"], "BLOCK")
                self.assertIn("EXACT_ENTRY_CLOCK_MISSING", result["blocking_reasons"])

    def test_declared_fallback_universe_and_horizon_still_work(self):
        meta = _complete_meta()
        meta["economic_expression"]["instrument"] = False
        meta["economic_expression"]["exit_clock"] = "UNAVAILABLE"
        result = assess_implementability(_engine_output(), meta)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["exact_clock_status"], "PASS")
        self.assertEqual(result["exact_universe_status"], "PASS")


if __name__ == "__main__":
    unittest.main()
