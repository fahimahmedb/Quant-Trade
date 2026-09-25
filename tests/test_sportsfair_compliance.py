"""Sharp-fair devig/CLV maths and the VET compliance gate."""

from __future__ import annotations

import unittest

from quant.desk.compliance import PROHIBITED, assess
from quant.factory.sportsfair import (binary_contract_edge, closing_line_value, devig_multiplicative,
                                      devig_power, devig_shin, expected_value)

PRICES = {"fav": 1.25, "draw": 6.0, "long": 13.0}      # ~4.4% margin, strong favourite


class DevigTests(unittest.TestCase):
    def test_all_methods_sum_to_one(self):
        for method in (devig_multiplicative, devig_power, devig_shin):
            self.assertAlmostEqual(sum(method(PRICES).values()), 1.0, places=9)

    def test_power_and_shin_shade_the_longshot_more_than_multiplicative(self):
        mult, power, shin = devig_multiplicative(PRICES), devig_power(PRICES), devig_shin(PRICES)
        self.assertLess(power["long"], mult["long"])
        self.assertLess(shin["long"], mult["long"])
        self.assertGreater(power["fav"], mult["fav"])

    def test_no_margin_is_identity(self):
        fair = {"a": 2.0, "b": 2.0}
        for method in (devig_multiplicative, devig_power, devig_shin):
            self.assertAlmostEqual(method(fair)["a"], 0.5, places=9)

    def test_invalid_prices_rejected(self):
        with self.assertRaises(ValueError):
            devig_power({"a": 1.0, "b": 3.0})


class ValueTests(unittest.TestCase):
    def test_ev_clv_and_binary_edge(self):
        self.assertAlmostEqual(expected_value(2.2, 0.5), 0.1)
        self.assertGreater(closing_line_value(1.40, PRICES, "fav"), 0.0)
        self.assertLess(closing_line_value(1.20, PRICES, "fav"), 0.0)
        kalshi = lambda p: 0.07 * p * (1 - p)
        self.assertAlmostEqual(binary_contract_edge(0.50, 0.55), 0.1)
        self.assertLess(binary_contract_edge(0.50, 0.51, kalshi), 0.0)   # fee eats the edge


class ComplianceTests(unittest.TestCase):
    def test_prohibited_practice_is_refused(self):
        verdict = assess({"compliance": {"practices": ["public_market_data", "wash_trading"]}})
        self.assertFalse(verdict["approved"])
        self.assertIn("wash_trading", PROHIBITED)

    def test_unmatched_cross_venue_hedge_is_refused(self):
        self.assertFalse(assess({"compliance": {"cross_venue_hedge": True}})["approved"])
        self.assertTrue(assess({"compliance": {"cross_venue_hedge": True,
                                               "settlement_rules_matched": True}})["approved"])

    def test_legacy_strategy_without_declaration_is_not_blocked(self):
        self.assertTrue(assess({})["approved"])


if __name__ == "__main__":
    unittest.main()
