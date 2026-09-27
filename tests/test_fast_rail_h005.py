"""Offline adversarial tests for fast-rail H-005 (fade new Hyperliquid listings).

All numbers below are INVENTED FIXTURES, not market data.
"""
from __future__ import annotations

import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from research.fast_rail.h005 import analysis as A  # noqa: E402

D0 = dt.date(2024, 1, 1)


def fixture_candles(start: dt.date, opens: list[float], n: int = 10, v: float = 1e6):
    """Invented daily candles: close = next open; last close = last open * 0.9."""
    rows = []
    for i, o in enumerate(opens):
        day = start + dt.timedelta(days=i)
        t = A.day_ms(day)
        c = opens[i + 1] if i + 1 < len(opens) else o * 0.9
        rows.append({"t": t, "T": t + A.DAY_MS - 1, "o": str(o), "c": str(c), "v": str(v), "n": n})
    return A.parse_candles(rows)


class H005Tests(unittest.TestCase):
    def setUp(self):
        self.btc = fixture_candles(D0 - dt.timedelta(days=10), [100.0] * 120)

    def test_entry_never_uses_listing_day_candle(self):
        # FIXTURE: listing-day open 1000 (hype spike), day L+1 open 50.
        alt = fixture_candles(D0, [1000.0, 50.0] + [50.0] * 20)
        ev = {"coin": "FAKE", "listing_day": D0, "delisted": False}
        r = A.event_returns(ev, alt, [], self.btc, [], 7)
        self.assertAlmostEqual(r["gross_short"], 0.0)  # entered at 50, not 1000
        w = A.window(alt, D0, 7, False)
        self.assertEqual(A.day_of(w["t0"]), D0 + dt.timedelta(days=1))
        self.assertEqual(A.day_of(w["t1"]), D0 + dt.timedelta(days=8))

    def test_missing_entry_candle_is_not_substituted(self):
        alt = fixture_candles(D0, [10.0] * 20)
        del alt[1]  # no candle on L+1
        self.assertIsNone(A.window(alt, D0, 7, False))

    def test_delisting_before_exit_uses_last_close_without_fill(self):
        # FIXTURE: 5 candles then delisted; last close = 8 * 0.9 = 7.2.
        alt = fixture_candles(D0, [10.0, 10.0, 9.0, 8.5, 8.0])
        w = A.window(alt, D0, 30, delisted=True)
        self.assertEqual(w["exit_kind"], "delisted_last_close")
        self.assertAlmostEqual(w["p1"], 7.2)
        self.assertEqual(len(w["hold"]), 4)  # only real candles, no synthesised days
        ev = {"coin": "GONE", "listing_day": D0, "delisted": True}
        r = A.event_returns(ev, alt, [], self.btc, [], 30)
        self.assertAlmostEqual(r["gross_short"], 1 - 7.2 / 10.0)
        # Same series NOT delisted: window runs past horizon -> incomplete, not filled.
        self.assertIsNone(A.window(alt, D0, 30, delisted=False))

    def test_funding_sign_short_receives_positive(self):
        alt = fixture_candles(D0, [10.0] * 20)
        t0 = A.day_ms(D0 + dt.timedelta(days=1))
        # FIXTURE: 24 hourly rates of +0.0001 (longs pay) inside the hold, 1 outside.
        funding = [{"time": t0 + i * 3_600_000, "fundingRate": "0.0001"} for i in range(24)]
        funding.append({"time": t0 - 3_600_000, "fundingRate": "0.5"})  # before entry: ignored
        ev = {"coin": "FAKE", "listing_day": D0, "delisted": False}
        r = A.event_returns(ev, alt, funding, self.btc, [], 7)
        self.assertAlmostEqual(r["funding_short"], 0.0024)
        self.assertAlmostEqual(r["short_net"], 0.0024 - 2 * A.COST_ALT)
        neg = [{**f, "fundingRate": "-0.0001"} for f in funding[:24]]
        r2 = A.event_returns(ev, alt, neg, self.btc, [], 7)
        self.assertLess(r2["short_net"], -2 * A.COST_ALT)
        # BTC long leg PAYS positive funding.
        btc_f = [{"time": t0 + i * 3_600_000, "fundingRate": "0.0001"} for i in range(24)]
        r3 = A.event_returns(ev, alt, [], self.btc, btc_f, 7)
        self.assertAlmostEqual(r3["hedged_net"] - r3["short_net"], -0.0024 - 2 * A.COST_BTC)
        self.assertAlmostEqual(r3["short_btc_net"], 0.0024 - 2 * A.COST_BTC)

    def test_coins_present_at_data_start_excluded_and_backfill_ignored(self):
        backfill = A.parse_candles([{"t": A.day_ms(D0 - dt.timedelta(days=5)), "T": 0, "o": "1", "c": "1",
                                     "v": "0", "n": 0}]) + fixture_candles(D0 + dt.timedelta(days=3), [5.0] * 5)
        universe = {
            "OLD": fixture_candles(D0, [1.0] * 10),                        # present at venue start
            "OLD2": fixture_candles(D0, [2.0] * 10),
            "NEW": fixture_candles(D0 + dt.timedelta(days=2), [3.0] * 5),
            "BF": backfill,                                                 # zero-volume prefix then trades
        }
        events, info = A.build_events(universe, delisted=set())
        self.assertEqual(info["venue_start"], D0.isoformat())
        self.assertEqual(sorted(info["excluded_present_at_start"]), ["OLD", "OLD2"])
        self.assertEqual([e["coin"] for e in events], ["NEW", "BF"])
        self.assertEqual(events[1]["listing_day"], D0 + dt.timedelta(days=3))
        self.assertTrue(events[1]["backfill_prefix"])

    def test_split_keeps_final_15pct_untouched_and_chronological(self):
        events = [{"coin": f"C{i}", "listing_day": D0 + dt.timedelta(days=i)} for i in range(100)]
        disc, val, untouched = A.split_events(events)
        self.assertEqual((len(disc), len(val), len(untouched)), (55, 30, 15))
        self.assertLess(disc[-1]["listing_day"], val[0]["listing_day"])
        self.assertLess(val[-1]["listing_day"], untouched[0]["listing_day"])
        self.assertEqual(untouched, events[85:])

    def test_runner_never_computes_untouched(self):
        # Structural guard: the runner computes returns only on discovery + validation.
        src = (Path(__file__).resolve().parents[1] / "research/fast_rail/h005/run.py").read_text()
        self.assertIn('(("discovery", disc), ("validation", val))', src)
        self.assertNotIn("event_returns(u", src)
        self.assertIn("for e in disc + val", src)

    def test_clustered_t_is_more_conservative_for_same_week_events(self):
        # FIXTURE: 3 weeks x 4 identical same-week returns -> clustering shrinks t.
        xs = [0.10] * 4 + [-0.02] * 4 + [0.05] * 4
        weeks = [1] * 4 + [2] * 4 + [3] * 4
        self.assertLess(A.t_clustered(xs, weeks), A.t_event(xs))

    def test_top_decile_share(self):
        self.assertAlmostEqual(A.top_decile_share([1.0] * 10), 0.1)
        self.assertEqual(A.top_decile_share([-1.0, 0.5]), float("inf"))


if __name__ == "__main__":
    unittest.main()
