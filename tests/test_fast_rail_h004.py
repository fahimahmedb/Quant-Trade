"""Offline adversarial tests for fast-rail H-004 (Kalshi maker P&L measurement).

All fixture numbers are INVENTED for testing and are not market data.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import sys
import unittest
from pathlib import Path

_DIR = Path(__file__).resolve().parents[1] / "research" / "fast_rail" / "h004"
sys.path.insert(0, str(_DIR))
_spec = importlib.util.spec_from_file_location("h004_analysis", _DIR / "h004.py")
h = importlib.util.module_from_spec(_spec)
sys.modules["h004_analysis"] = h
_spec.loader.exec_module(h)
import h004_config as config  # noqa: E402

P = h.Print


class MarkoutReference(unittest.TestCase):
    def test_never_uses_prints_before_t_plus_300(self):
        # INVENTED: prints at +0, +100, +299.999 are extreme and must be ignored.
        ps = [P(0, 0.50, 1, "yes"), P(100, 0.99, 50, "no"), P(299.999, 0.01, 50, "yes"),
              P(300, 0.60, 2, "yes"), P(450, 0.70, 2, "no"), P(600, 0.05, 99, "no")]
        ref = h.markout_reference(ps, [p.t for p in ps], 0)
        self.assertAlmostEqual(ref, 0.65)  # only [300, 600): 0.60 and 0.70, equal weights

    def test_window_excludes_t_plus_600(self):
        ps = [P(0, 0.50, 1, "yes"), P(600, 0.90, 1, "no")]
        self.assertIsNone(h.markout_reference(ps, [p.t for p in ps], 0))

    def test_no_filling_when_no_later_print(self):
        u = h.Unit("KXHIGHNY", "weather", dt.date(2026, 1, 1))
        h.process_market(u, [P(0, 0.40, 10, "no"), P(50, 0.45, 10, "yes")], None)
        self.assertIsNone(u.per_contract("markout"))
        self.assertIsNone(u.per_contract("settlement"))  # unknown result: no settlement P&L either

    def test_prior_mid_is_strictly_causal(self):
        ps = [P(0, 0.40, 1, "no"), P(10, 0.44, 1, "yes"), P(20, 0.99, 1, "yes"), P(20, 0.01, 1, "no")]
        self.assertAlmostEqual(h.prior_mid(ps, 2), 0.42)


class MakerSign(unittest.TestCase):
    def test_taker_buys_yes_maker_short_yes(self):
        # taker bought YES at 0.30, settles NO -> maker (sold YES) earns 0.30
        self.assertAlmostEqual(h.maker_pnl(0.30, 0.0, "yes"), 0.30)
        self.assertAlmostEqual(h.maker_pnl(0.30, 1.0, "yes"), -0.70)

    def test_taker_sells_yes_maker_long_yes(self):
        self.assertAlmostEqual(h.maker_pnl(0.30, 1.0, "no"), 0.70)
        self.assertAlmostEqual(h.maker_pnl(0.30, 0.0, "no"), -0.30)

    def test_fee_is_subtracted_and_doubles(self):
        u = h.Unit("KXHIGHNY", "weather", dt.date(2026, 1, 1))
        h.process_market(u, [P(0, 0.50, 4, "yes")], "no")
        fee = config.MAKER_FEE_RATE * 0.25
        self.assertAlmostEqual(u.per_contract("settlement", 0.0), 0.50)
        self.assertAlmostEqual(u.per_contract("settlement"), 0.50 - fee)
        self.assertAlmostEqual(u.per_contract("settlement", 2.0), 0.50 - 2 * fee)


class Clustering(unittest.TestCase):
    def test_event_day_is_one_contract_weighted_unit(self):
        d = dt.date(2025, 10, 2)
        markets = [
            {"series": "KXHIGHNY", "ticker": "A", "event_date": d.isoformat(), "result": "yes"},
            {"series": "KXHIGHNY", "ticker": "B", "event_date": d.isoformat(), "result": "no"},
            {"series": "KXINX", "ticker": "C", "event_date": d.isoformat(), "result": "no"},
        ]
        trades = {"A": [P(0, 0.80, 1, "no")],         # maker +0.20 x1
                  "B": [P(0, 0.10, 3, "no")],         # maker -0.10 x3
                  "C": [P(0, 0.50, 1, "yes")]}
        units = h.build_units(markets, trades, {d})
        self.assertEqual(len(units), 2)  # one per (series, date), not per market or print
        ny = next(u for u in units if u.series == "KXHIGHNY")
        self.assertAlmostEqual(ny.per_contract("settlement", 0.0), (0.20 - 0.30) / 4)
        stats = h.evaluate(units, "weather", "settlement")
        self.assertEqual(stats["n"], 1)


class Splits(unittest.TestCase):
    def test_untouched_final_15_percent_never_processed(self):
        dates = config.sampled_dates()
        disc, val, untouched = h.split_dates(dates)
        self.assertEqual(len(disc) + len(val) + len(untouched), len(set(dates)))
        self.assertLess(max(disc), min(val))
        self.assertLess(max(val), min(untouched))
        self.assertAlmostEqual(len(untouched) / len(dates), 0.15, delta=0.02)
        u_day = untouched[0]
        markets = [{"series": "KXHIGHNY", "ticker": "X", "event_date": u_day.isoformat(), "result": "no"}]
        trades = {"X": [P(0, 0.99, 1e6, "yes")]}  # INVENTED huge outlier on an untouched date
        self.assertEqual(h.build_units(markets, trades, set(disc) | set(val)), [])

    def test_top_decile_share_and_halves(self):
        units = []
        for i, pnl in enumerate([0.01] * 9 + [1.0]):
            u = h.Unit("KXHIGHNY", "weather", dt.date(2026, 1, 1) + dt.timedelta(days=i))
            u.add("settlement", 1.0, pnl, 0.0, 0.5)
            units.append(u)
        stats = h.evaluate(units, "weather", "settlement")
        self.assertGreater(stats["top_decile_share"], 0.5)  # concentrated -> must fail the criterion
        self.assertEqual(len(stats["half_means_c"]), 2)


if __name__ == "__main__":
    unittest.main()
