import math
import unittest

from src.economic_value import evaluate, ewma_exposures


class EconomicValueTests(unittest.TestCase):
    def test_forecast_is_causal(self):
        a = [0.01] * 6 + [0.50, 0.01]
        b = [0.01] * 6 + [-0.50, 0.01]
        self.assertEqual(ewma_exposures(a, 6)[0], ewma_exposures(b, 6)[0])
        self.assertNotEqual(ewma_exposures(a, 6)[1], ewma_exposures(b, 6)[1])

    def test_turnover_cost_reduces_wealth(self):
        gross = evaluate([0.01, 0.01], [1.0, 0.5], 0)
        net = evaluate([0.01, 0.01], [1.0, 0.5], 10)
        self.assertLess(net.terminal_wealth, gross.terminal_wealth)
        self.assertTrue(math.isclose(net.turnover, 1.5))

    def test_drawdown(self):
        perf = evaluate([0.10, -0.10], [1.0, 1.0], 0)
        self.assertAlmostEqual(perf.max_drawdown, -0.10)


if __name__ == "__main__":
    unittest.main()
