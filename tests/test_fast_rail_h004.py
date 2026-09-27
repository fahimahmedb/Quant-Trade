"""H-004: Kalshi weather maker-side settlement P&L — pure-logic tests.

All numbers below are INVENTED toy values for testing, not market data.
"""

import math
import unittest
from fractions import Fraction

from quant.factory import kalshi_maker as km


class MakerPnlSign(unittest.TestCase):
    def test_taker_bought_yes(self):
        # maker sold YES at 30c
        self.assertEqual(km.maker_pnl_cents("yes", 30, yes_won=False), 30)
        self.assertEqual(km.maker_pnl_cents("yes", 30, yes_won=True), -70)

    def test_taker_bought_no(self):
        # maker bought YES at 30c
        self.assertEqual(km.maker_pnl_cents("no", 30, yes_won=True), 70)
        self.assertEqual(km.maker_pnl_cents("no", 30, yes_won=False), -30)

    def test_zero_sum_with_taker(self):
        for side in ("yes", "no"):
            for won in (True, False):
                taker = (100 * won - 40) if side == "yes" else (100 * (not won) - 60)
                self.assertEqual(km.maker_pnl_cents(side, 40, won), -taker)

    def test_bad_inputs(self):
        with self.assertRaises(ValueError):
            km.maker_pnl_cents("buy", 30, True)
        with self.assertRaises(ValueError):
            km.maker_pnl_cents("yes", 0, True)


class MakerFee(unittest.TestCase):
    def test_rounds_up_to_cent(self):
        # 0.0175 * 1 * 0.5 * 0.5 = $0.004375 -> 1 cent
        self.assertEqual(km.maker_fee_cents(1, 50), 1)
        # 0.0175 * 100 * 0.5 * 0.5 = $0.4375 -> 44 cents
        self.assertEqual(km.maker_fee_cents(100, 50), 44)
        # tiny fee at an extreme price still costs a full cent
        self.assertEqual(km.maker_fee_cents(1, 1), 1)

    def test_exact_cent_not_bumped(self):
        # 0.0175 * 800 * 0.5 * 0.5 = $3.50 exactly -> 350 cents
        self.assertEqual(km.maker_fee_cents(800, 50), 350)

    def test_fractional_count_and_symmetry(self):
        self.assertEqual(km.maker_fee_cents("3.10", 20), math.ceil(Fraction(175, 10000) * Fraction(31, 10) * 20 * 80 / 100))
        self.assertEqual(km.maker_fee_cents(37, 23), km.maker_fee_cents(37, 77))

    def test_price_parsing(self):
        self.assertEqual(km.price_cents("0.0700"), 7)
        with self.assertRaises(ValueError):
            km.price_cents("0.0750")


class Eligibility(unittest.TestCase):
    CLOSE = "2026-07-16T04:59:00Z"

    def test_after_close_excluded(self):
        self.assertTrue(km.trade_is_eligible("2026-07-16T04:58:59.123456Z", self.CLOSE, "yes", False))
        self.assertTrue(km.trade_is_eligible("2026-07-16T04:59:00Z", self.CLOSE, "no", False))
        self.assertFalse(km.trade_is_eligible("2026-07-16T04:59:00.5Z", self.CLOSE, "yes", False))

    def test_unsettled_excluded(self):
        for result in ("", "void", "scalar", None):
            self.assertFalse(km.trade_is_eligible("2026-07-15T12:00:00Z", self.CLOSE, result, False))

    def test_block_trade_excluded(self):
        self.assertFalse(km.trade_is_eligible("2026-07-15T12:00:00Z", self.CLOSE, "yes", True))

    def test_event_date(self):
        self.assertEqual(str(km.event_date("KXHIGHNY-26JUL15")), "2026-07-15")
        self.assertEqual(str(km.event_date("KXBTCD-25SEP1517")), "2025-09-15")


class ClusteredStats(unittest.TestCase):
    def test_toy_cluster_se(self):
        # INVENTED toy example: three markets.
        # market a: pnl 10 over 10 contracts; b: -2 over 4; c: 8 over 6.
        clusters = [km.Cluster("a", 10, 10), km.Cluster("b", -2, 4), km.Cluster("c", 8, 6)]
        out = km.clustered_mean(clusters)
        mean = 16 / 20
        resid = [10 - mean * 10, -2 - mean * 4, 8 - mean * 6]  # 2, -5.2, 3.2
        se = math.sqrt(3 / 2 * sum(r * r for r in resid)) / 20
        self.assertAlmostEqual(out["mean"], 0.8)
        self.assertAlmostEqual(out["se"], se)
        self.assertAlmostEqual(out["t"], 0.8 / se)
        self.assertEqual(out["clusters"], 3)

    def test_clustering_widens_se_for_correlated_trades(self):
        # INVENTED: identical trades duplicated inside one market add no information.
        one = km.clustered_mean([km.Cluster("a", 5, 1), km.Cluster("b", -3, 1), km.Cluster("c", 4, 1)])
        dup = km.clustered_mean([km.Cluster("a", 50, 10), km.Cluster("b", -30, 10), km.Cluster("c", 40, 10)])
        self.assertAlmostEqual(one["t"], dup["t"])

    def test_aggregate_and_top_share(self):
        rows = [{"ticker": "a", "net_pnl_cents": "6", "contracts": "2"},
                {"ticker": "a", "net_pnl_cents": "4", "contracts": "3"},
                {"ticker": "b", "net_pnl_cents": "-5", "contracts": "5"}]
        cl = km.aggregate(rows, "ticker")
        self.assertEqual([(c.key, c.pnl, c.contracts) for c in cl], [("a", 10.0, 5.0), ("b", -5.0, 5.0)])
        self.assertAlmostEqual(km.top_share(cl), 2.0)  # top market = 10 of total 5
        self.assertEqual(km.top_share([km.Cluster("x", -1, 1)]), float("inf"))


if __name__ == "__main__":
    unittest.main()
