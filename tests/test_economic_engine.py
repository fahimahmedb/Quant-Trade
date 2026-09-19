import unittest

from quant.economics import CostInput, Decision, EconomicEngine, EconomicInputs, ModelParameter


def parameter(name, value, unit="currency", source="predeclared-model"):
    return ModelParameter(name, value, unit, source, "2026-09-18", "v1")


def case(**changes):
    costs = tuple(CostInput(parameter(name, 1.0), 1.0) for name in sorted(EconomicEngine.REQUIRED_COSTS))
    values = dict(
        assessment_id="EA-1", effect_id="effect-1", effect_version="v1",
        expected_gross_effect=0.02, effect_uncertainty=0.005,
        requested_exposure=1000.0, executable_capacity=1000.0,
        capacity_source=parameter("capacity", 1000.0), costs=costs,
        economic_margin_rate=parameter("economic_margin", 0.001, "return"),
        min_net_value=parameter("minimum_net_value", 1.0), mode="SHADOW",
    )
    values.update(changes)
    return EconomicInputs(**values)


class EconomicEngineTest(unittest.TestCase):
    def setUp(self):
        self.engine = EconomicEngine()

    def test_positive_effect_continues_only_after_all_friction_and_uncertainty(self):
        result = self.engine.assess(case())
        self.assertEqual(result.decision, Decision.CONTINUE)
        self.assertEqual(result.expected_net_value, 6.0)
        self.assertEqual(result.forward_cost, 8.0)

    def test_statistically_positive_but_economically_dominated_is_killed(self):
        expensive = tuple(
            CostInput(parameter(name, 3.0), 3.0) for name in sorted(EconomicEngine.REQUIRED_COSTS)
        )
        result = self.engine.assess(case(costs=expensive))
        self.assertEqual(result.decision, Decision.KILL)
        self.assertIn("ECONOMICALLY_DOMINATED_AFTER_FRICTIONS", result.reason_codes)

    def test_no_capacity_is_no_trade_not_false_economic_rejection(self):
        result = self.engine.assess(case(executable_capacity=0.0))
        self.assertEqual(result.decision, Decision.NO_TRADE)
        self.assertEqual(result.reason_codes, ("NO_EXECUTABLE_CAPACITY", "CAPACITY_CLIPPED"))

    def test_capacity_clipping_recomputes_value_instead_of_haircut_afterward(self):
        result = self.engine.assess(case(executable_capacity=500.0))
        self.assertEqual(result.executable_exposure, 500.0)
        self.assertEqual(result.gross_value, 10.0)
        self.assertIn("CAPACITY_CLIPPED", result.reason_codes)

    def test_missing_friction_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "friction schema mismatch"):
            self.engine.assess(case(costs=case().costs[:-1]))

    def test_weak_provenance_fails_closed(self):
        bad = parameter("capacity", 1000.0, source="")
        with self.assertRaisesRegex(ValueError, "incomplete provenance"):
            self.engine.assess(case(capacity_source=bad))

    def test_real_capital_is_structurally_refused(self):
        with self.assertRaisesRegex(ValueError, "no real-capital authority"):
            self.engine.assess(case(mode="REAL"))

    def test_fingerprint_is_order_independent_but_version_sensitive(self):
        first = self.engine.assess(case())
        reverse = self.engine.assess(case(costs=tuple(reversed(case().costs))))
        changed = self.engine.assess(case(effect_version="v2"))
        self.assertEqual(first.input_fingerprint, reverse.input_fingerprint)
        self.assertNotEqual(first.input_fingerprint, changed.input_fingerprint)


if __name__ == "__main__":
    unittest.main()
