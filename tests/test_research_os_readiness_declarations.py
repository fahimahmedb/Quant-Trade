"""Falsify READY when economic declarations contain placeholders or wrong types."""
from copy import deepcopy
import unittest

from research.research_os.expansion.economic_test_readiness_v1 import economic_test_readiness, READY
from research.research_os.expansion.validation_readiness import validate_economic_test_readiness
from research.research_os.scientific_store import sha256_json
from research.research_os.tests.test_economic_readiness_integration import fixture, legacy
from research.research_os.tests.test_economic_readiness_validation import _fixture


INVALID_TEXT = (None, False, True, 0, 1.0, {}, [], "", " \t", " unknown ",
                "unavailable", "UNSPECIFIED", "NOT_ESTIMATED")


class EconomicDeclarationTests(unittest.TestCase):
    def test_composition_rejects_invalid_model_and_evidence_identifiers(self):
        for section, field, code in (("cost_assumptions", "model_id", "COST_ASSUMPTIONS_INVALID"),
                                     ("capacity_assumptions", "model_id", "CAPACITY_ASSUMPTIONS_INVALID"),
                                     ("capacity_assumptions", "evidence_ref", "CAPACITY_ASSUMPTIONS_INVALID")):
            for value in INVALID_TEXT:
                with self.subTest(section=section, field=field, value=value):
                    package = fixture()
                    package["runner_meta"]["frozen_protocol"][section][field] = value
                    before = deepcopy(package)
                    result = economic_test_readiness(package, legacy=legacy())
                    self.assertEqual(result["status"], "BLOCK")
                    self.assertIn(code, result["block_reasons"])
                    self.assertEqual(package, before)
                    self.assertTrue(all(v is False for v in result["authority"].values()))

    def test_independent_validator_checks_declared_model_identifiers(self):
        for section, code in (("cost_model", "COST_MODEL_DECLARATION_MISSING"),
                              ("capacity", "CAPACITY_DECLARATION_MISSING")):
            for value in INVALID_TEXT:
                with self.subTest(section=section, value=value):
                    bundle = _fixture()
                    bundle[section]["model_id"] = value
                    result = validate_economic_test_readiness(bundle)
                    self.assertEqual(result["status"], "BLOCK")
                    self.assertIn(code, [reason["code"] for reason in result["block_reasons"]])

    def test_independent_validator_rejects_invalid_expression_values_even_when_hashed(self):
        for value in (False, True, " ", " unavailable ", {}, []):
            with self.subTest(value=value):
                bundle = _fixture()
                expression = bundle["economic_expression"]
                expression["spec"]["entry_rule"] = value
                expression["expression_hash"] = sha256_json(expression["spec"])
                result = validate_economic_test_readiness(bundle)
                self.assertEqual(result["status"], "BLOCK")
                self.assertIn("ECONOMIC_EXPRESSION_INCOMPLETE",
                              [reason["code"] for reason in result["block_reasons"]])

    def test_valid_identifiers_zero_costs_and_structured_rules_remain_admissible(self):
        package = fixture()
        costs = package["runner_meta"]["frozen_protocol"]["cost_assumptions"]
        for key in ("fees_bps", "spread_bps", "slippage_bps", "financing_bps", "borrow_bps"):
            costs[key] = 0
        result = economic_test_readiness(package, legacy=legacy())
        self.assertEqual(result["status"], READY, result["block_reasons"])
        self.assertEqual(result["remaining_execution_blockers"], ["OWNER_AUTHORIZATION"])
        bundle = _fixture()
        expression = bundle["economic_expression"]
        expression["spec"]["entry_rule"] = {"clock_id": "frozen-clock", "relation": "AFTER_INFORMATION"}
        expression["expression_hash"] = sha256_json(expression["spec"])
        self.assertEqual(validate_economic_test_readiness(bundle)["status"], READY)

    def test_nonfinite_effective_trials_cannot_be_claimed_known(self):
        for value in (float("inf"), -float("inf"), float("nan")):
            with self.subTest(value=value):
                bundle = _fixture()
                bundle["trial_accounting"].update(effective_trials_status="KNOWN",
                                                estimated_effective_trials=value)
                result = validate_economic_test_readiness(bundle)
                self.assertEqual(result["status"], "BLOCK")
                self.assertEqual(result["checks"]["trial_accounting"]["status"], "FAIL")
                package = fixture()
                package["runner_meta"]["frozen_protocol"]["effective_trials"] = value
                result = economic_test_readiness(package, legacy=legacy())
                self.assertEqual(result["status"], "BLOCK")
                self.assertIn("TRIAL_ACCOUNTING_INVALID", result["block_reasons"])


if __name__ == "__main__":
    unittest.main()
