"""Event-indexed t-SPRT for SHADOW_DIRECT (adversarial)."""

from __future__ import annotations

import random
import unittest

from quant.learning.sequential import (binary_payoff_sigma, event_sequential_test, sequential_test,
                                      shadow_direct_alpha)


def _simulate(mean: float, sims: int, n: int, h1: float, alpha: float, seed: int) -> dict:
    rng = random.Random(seed)
    counts = {"ACCEPT_EDGE": 0, "REJECT_EDGE": 0, "INCONCLUSIVE": 0, "CONTINUE": 0}
    for _ in range(sims):
        values = [rng.gauss(mean, 1.0) * 0.04 for _ in range(n)]   # any scale: plug-in sigma
        counts[event_sequential_test(values, h1, alpha, max_observations=n)["decision"]] += 1
    return counts


class EventSequentialTests(unittest.TestCase):
    def test_false_acceptance_under_h0_is_at_most_alpha(self):
        for h1, alpha in ((0.5, shadow_direct_alpha(1)), (0.25, shadow_direct_alpha(2))):
            counts = _simulate(0.0, 2000, 400, h1, alpha, seed=20260929)
            self.assertLessEqual(counts["ACCEPT_EDGE"] / 2000, alpha, (h1, alpha, counts))

    def test_rare_loss_statistic_needs_the_declared_sigma_floor(self):
        # Fairly priced favourite bought at 0.90: 90% small wins, 10% total losses.
        def draws(seed):
            rng = random.Random(seed)
            return [[(1 / 9 if rng.random() < 0.9 else -1.0) for _ in range(400)]
                    for _ in range(2000)]
        alpha = shadow_direct_alpha(1)
        naive = sum(event_sequential_test(v, 0.5, alpha, max_observations=400)["decision"]
                    == "ACCEPT_EDGE" for v in draws(1)) / 2000
        floored = sum(event_sequential_test(v, 0.5, alpha, max_observations=400,
                                            sigma_floor=binary_payoff_sigma(0.9))["decision"]
                      == "ACCEPT_EDGE" for v in draws(1)) / 2000
        self.assertGreater(naive, 2 * alpha)          # the failure mode is real
        self.assertLessEqual(floored, alpha)          # the declared floor repairs it

    def test_power_under_h1(self):
        counts = _simulate(0.5, 500, 400, 0.5, shadow_direct_alpha(1), seed=7)
        self.assertGreater(counts["ACCEPT_EDGE"] / 500, 0.9, counts)

    def test_replay_is_identical_and_stops_at_first_crossing(self):
        rng = random.Random(3)
        values = [rng.gauss(0.6, 1.0) for _ in range(500)]
        first = event_sequential_test(values, 0.5, 0.025)
        self.assertEqual(first, event_sequential_test(list(values), 0.5, 0.025))
        self.assertEqual(first["decision"], "ACCEPT_EDGE")
        # Appending later events never changes a decision already reached.
        self.assertEqual(first, event_sequential_test(values + [-50.0] * 100, 0.5, 0.025))

    def test_horizon_without_crossing_is_inconclusive(self):
        values = [0.01 * (1 if i % 2 else -1) + 0.001 for i in range(80)]
        verdict = event_sequential_test(values, 0.05, 0.025, max_observations=60)
        self.assertEqual(verdict["decision"], "INCONCLUSIVE")
        self.assertEqual(verdict["observations"], 60)

    def test_no_decision_before_min_observations_and_input_validation(self):
        self.assertEqual(event_sequential_test([1.0, 1.1] * 10, 0.5, 0.025)["decision"], "CONTINUE")
        with self.assertRaises(ValueError):
            event_sequential_test([0.1] * 50, 0.0, 0.025)
        with self.assertRaises(ValueError):
            shadow_direct_alpha(0)

    def test_alpha_schedule_sums_below_five_percent(self):
        self.assertAlmostEqual(shadow_direct_alpha(1), 0.025)
        self.assertLess(sum(shadow_direct_alpha(k) for k in range(1, 10_000)), 0.05)

    def test_existing_daily_test_is_unchanged(self):
        rng = random.Random(11)
        returns = [rng.gauss(0.0005, 0.01) for _ in range(300)]
        verdict = sequential_test(returns, 0.5)
        self.assertEqual(set(verdict) >= {"decision", "log_likelihood_ratio"}, True)
        self.assertEqual(verdict["alternative_sharpe"], 0.5)


if __name__ == "__main__":
    unittest.main()
