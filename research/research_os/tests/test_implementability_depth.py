from __future__ import annotations

from copy import deepcopy
import unittest

from research.research_os.expansion.final_shape import assess_implementability


def _engine_output():
    return {
        "engine_id": "test-producer.v1",
        "candidate": {
            "hypothesis_id": "TEST-IMPLEMENTABILITY-001",
            "generation_id": "G1",
            "mechanism": "synthetic mechanism description only",
            "claim": "synthetic claim description only",
            "falsification_scope": "implementation contract only",
            "decision_map": {"if_supported": "future_test", "if_rejected": "discard"},
        },
    }


def _complete_meta():
    return {
        "source_available": True,
        "pit_feasible": True,
        "expression_feasible": True,
        "cost_model_feasible": True,
        "capacity_observable": True,
        "operational_complexity": "LOW",
        "economic_expression": {
            "instrument": "SYNTHETIC_TEST_INSTRUMENT",
            "universe": "SYNTHETIC_ELIGIBLE_UNIVERSE",
            "direction_exposure_semantics": "long one normalized unit when eligible",
            "entry_clock": "first eligible clock strictly after information availability",
            "exit_clock": "next declared evaluation clock",
            "horizon": "one declared clock interval",
            "eligibility": "instrument must be in the frozen eligible universe at entry clock",
            "position_expression": "one normalized unit; no sizing or optimization",
            "cost_model_requirements": "fees, spread, slippage and financing must be declared before test",
            "capacity_requirements": "observable liquidity/capacity input required before test",
            "data_requirements": "point-in-time universe, signal inputs and execution clocks",
            "execution_assumptions": "declared clock proxy only; no live order semantics",
            "falsification_relevant_implementation_conditions": "reject if any PIT, clock, eligibility, cost or capacity premise cannot be reconstructed",
        },
    }


class ImplementabilityDepthTests(unittest.TestCase):
    def test_fully_specified_implementability_can_pass(self):
        result = assess_implementability(_engine_output(), _complete_meta())
        self.assertEqual(result["implementability_status"], "IMPLEMENTABLE")
        self.assertEqual(result["exact_expression_status"], "PASS")
        self.assertEqual(result["exact_clock_status"], "PASS")
        self.assertEqual(result["exact_universe_status"], "PASS")
        self.assertEqual(result["blocking_reasons"], [])
        self.assertEqual(result["status"], "PASS")

    def test_missing_expression_blocks(self):
        meta = _complete_meta()
        del meta["economic_expression"]["position_expression"]
        result = assess_implementability(_engine_output(), meta)
        self.assertEqual(result["implementability_status"], "BLOCK_IMPLEMENTABILITY")
        self.assertEqual(result["exact_expression_status"], "BLOCK")
        self.assertIn("EXACT_POSITION_EXPRESSION_MISSING", result["blocking_reasons"])

    def test_missing_cost_model_blocks(self):
        meta = _complete_meta()
        meta["cost_model_feasible"] = False
        result = assess_implementability(_engine_output(), meta)
        self.assertEqual(result["implementability_status"], "BLOCK_IMPLEMENTABILITY")
        self.assertFalse(result["cost_model_feasible"])
        self.assertIn("COST_MODEL_NOT_QUALIFIED", result["blocking_reasons"])

    def test_unobservable_capacity_unknown_is_explicit_and_blocks(self):
        meta = _complete_meta()
        del meta["capacity_observable"]
        result = assess_implementability(_engine_output(), meta)
        self.assertEqual(result["capacity_observable"], "UNKNOWN")
        self.assertEqual(result["implementability_status"], "BLOCK_IMPLEMENTABILITY")
        self.assertIn("CAPACITY_OBSERVABILITY_UNKNOWN", result["blocking_reasons"])
        self.assertNotEqual(result["status"], "PASS")

    def test_missing_pit_blocks(self):
        meta = _complete_meta()
        meta["pit_feasible"] = False
        result = assess_implementability(_engine_output(), meta)
        self.assertEqual(result["implementability_status"], "BLOCK_IMPLEMENTABILITY")
        self.assertFalse(result["pit_feasible"])
        self.assertIn("PIT_NOT_QUALIFIED", result["blocking_reasons"])

    def test_candidate_is_never_mutated(self):
        output = _engine_output()
        before = deepcopy(output)
        result = assess_implementability(output, _complete_meta())
        self.assertEqual(output, before)
        self.assertFalse(result["candidate_mutated"])
        self.assertFalse(result["mechanism_rewritten"])
        self.assertFalse(result["research_decision_rewritten"])

    def test_dangerous_authority_flags_remain_false(self):
        result = assess_implementability(_engine_output(), _complete_meta())
        self.assertEqual(
            result["authority"],
            {
                "economic_experiment_authorized": False,
                "prospective_observation_authorized": False,
                "real_capital_authorized": False,
                "live_trading_authorized": False,
            },
        )
        self.assertTrue(all(result[key] is False for key in result["authority"]))

    def test_source_unavailable_is_park_not_pass(self):
        meta = _complete_meta()
        meta["source_available"] = False
        result = assess_implementability(_engine_output(), meta)
        self.assertEqual(result["implementability_status"], "PARK_IMPLEMENTABILITY")
        self.assertEqual(result["status"], "PARK_IMPLEMENTABILITY")
        self.assertIn("SOURCE_UNAVAILABLE", result["blocking_reasons"])

    def test_missing_exact_contract_never_becomes_implementable(self):
        meta = _complete_meta()
        del meta["economic_expression"]
        result = assess_implementability(_engine_output(), meta)
        self.assertEqual(result["implementability_status"], "BLOCK_IMPLEMENTABILITY")
        self.assertEqual(result["exact_expression_status"], "UNKNOWN")
        self.assertEqual(result["exact_clock_status"], "UNKNOWN")
        self.assertEqual(result["exact_universe_status"], "UNKNOWN")
        self.assertIn("EXACT_EXPRESSION_CONTRACT_MISSING", result["blocking_reasons"])


if __name__ == "__main__":
    unittest.main()
