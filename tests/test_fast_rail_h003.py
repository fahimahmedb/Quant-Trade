"""Adversarial offline tests for H-003 (Kalshi favourite-longshot NO buyer).

All numbers below are INVENTED fixtures, not market data.
"""

import importlib.util
import os
import unittest

_PATH = os.path.join(os.path.dirname(__file__), "..", "research", "fast_rail", "h003", "analyze.py")
_spec = importlib.util.spec_from_file_location("h003_analyze", _PATH)
h003 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h003)

H = 3600


def market(ticker, event, close_ts, result, candles, series="S1"):  # invented
    return {"ticker": ticker, "event_ticker": event, "series": series, "close_ts": close_ts,
            "result": result, "candles": candles}


class CandleSelection(unittest.TestCase):
    def test_never_uses_candle_closing_after_entry(self):
        entry = 100 * H
        # invented: the candle closing one second after entry is very cheap and must be ignored
        candles = [[entry - 2 * H, 0.30, 0.32, 5, 50], [entry + 1, 0.01, 0.02, 5, 50],
                   [entry + H, 0.01, 0.02, 5, 50]]
        chosen = h003.select_candle(candles, entry)
        self.assertEqual(chosen[0], entry - 2 * H)
        self.assertIsNone(h003.no_entry_price(chosen, 0.05))

    def test_candle_closing_exactly_at_entry_is_allowed(self):
        entry = 100 * H
        candles = [[entry, 0.03, 0.05, 1, 10]]  # invented
        self.assertEqual(h003.select_candle(candles, entry)[0], entry)

    def test_only_future_candles_means_no_trade(self):
        entry = 100 * H
        self.assertIsNone(h003.select_candle([[entry + H, 0.02, 0.03, 1, 1]], entry))

    def test_stale_candle_rejected(self):
        entry = 100 * H
        self.assertIsNone(h003.select_candle([[entry - 25 * H, 0.02, 0.03, 1, 1]], entry))

    def test_event_returns_ignore_post_entry_candle(self):
        close = 200 * H
        # invented: only quote before T-1h is expensive (0.5), a cheap quote appears after entry
        m = market("A", "E", close, "no", [[close - 3 * H, 0.50, 0.52, 10, 10],
                                          [close - H + 60, 0.02, 0.03, 10, 10]])
        rows = h003.event_returns([h003.group_events([m])["E"]], 0.05, 1)
        self.assertEqual(rows, [])


class MissingBid(unittest.TestCase):
    def test_missing_or_zero_bid_is_no_trade(self):
        for candle in ([0, None, 0.03, 1, 1], [0, 0.0, 0.03, 1, 1], [0, 0.02, None, 1, 1],
                       [0, 0.02, 1.0, 1, 1], [0, 0.05, 0.04, 1, 1]):  # invented
            self.assertIsNone(h003.no_entry_price(candle, 0.20), candle)

    def test_mid_rule_and_no_ask_price(self):
        self.assertAlmostEqual(h003.no_entry_price([0, 0.04, 0.06, 1, 1], 0.05), 0.96)
        self.assertIsNone(h003.no_entry_price([0, 0.05, 0.07, 1, 1], 0.05))  # mid 0.06 > 0.05


class Fees(unittest.TestCase):
    def test_fee_rounds_up_per_contract(self):
        self.assertEqual(h003.kalshi_taker_fee(0.97, 1), 0.01)  # 0.07*.97*.03=0.0020 -> 0.01
        self.assertEqual(h003.kalshi_taker_fee(0.50, 1), 0.02)  # 0.0175 -> 0.02
        self.assertEqual(h003.kalshi_taker_fee(0.90, 1), 0.01)  # 0.0063 -> 0.01

    def test_contract_net(self):
        self.assertAlmostEqual(h003.contract_net(0.97, "no"), (1 - 0.98) / 0.98)
        self.assertAlmostEqual(h003.contract_net(0.97, "yes"), -1.0)
        self.assertAlmostEqual(h003.contract_net(0.97, "no", 2.0), (1 - 0.99) / 0.99)


class Aggregation(unittest.TestCase):
    def test_event_is_one_unit_equal_weight(self):
        close = 500 * H
        cheap = [[close - 2 * H, 0.03, 0.05, 100, 1000]]  # invented: mid 0.04, NO ask 0.97
        ms = [market("A1", "EA", close, "no", cheap), market("A2", "EA", close, "no", cheap),
              market("A3", "EA", close, "yes", cheap),
              market("B1", "EB", close + H, "no", cheap)]
        rows = h003.event_returns(sorted(h003.group_events(ms).values(), key=lambda e: e["close_ts"]), 0.05, 1)
        self.assertEqual([r["event_ticker"] for r in rows], ["EA", "EB"])
        win, loss = (1 - 0.98) / 0.98, -1.0
        self.assertAlmostEqual(rows[0]["net"], (2 * win + loss) / 3)
        self.assertEqual(rows[0]["n_contracts"], 3)
        self.assertAlmostEqual(rows[1]["net"], win)
        # capacity: min(10% of 24h volume=10, OI=1000) contracts * 0.97 per contract
        self.assertAlmostEqual(rows[1]["deployable_usd"], 10 * 0.97)


class Split(unittest.TestCase):
    def test_last_15pct_never_returned(self):
        ms = [market(f"M{i}", f"E{i:03d}", 1000 * H + i * H, "no", []) for i in range(100)]  # invented
        events = h003.group_events(list(reversed(ms)))
        disc, val, n_hold = h003.split_events(events)
        self.assertEqual((len(disc), len(val), n_hold), (55, 30, 15))
        seen = {e["event_ticker"] for e in disc + val}
        self.assertTrue(all(f"E{i:03d}" not in seen for i in range(85, 100)))
        self.assertLess(max(e["close_ts"] for e in disc), min(e["close_ts"] for e in val))

    def test_main_never_evaluates_holdout(self):
        calls = []
        orig = h003.event_returns

        def spy(events, *a, **k):
            calls.extend(e["event_ticker"] for e in events)
            return orig(events, *a, **k)

        close = 1000 * H
        ms = [market(f"M{i}", f"E{i:03d}", close + i * H, "no", [[close + i * H - 2 * H, 0.03, 0.05, 10, 10]])
              for i in range(40)]  # invented
        h003.event_returns, h003.load = spy, (lambda path=None: ms)
        orig_here = h003.HERE
        h003.HERE = os.path.join(os.path.dirname(__file__), "..", "var")
        os.makedirs(h003.HERE, exist_ok=True)
        try:
            import contextlib
            import io
            with contextlib.redirect_stdout(io.StringIO()):
                h003.main()
        finally:
            h003.event_returns, h003.HERE = orig, orig_here
            h003.load = _loader
        holdout = {f"E{i:03d}" for i in range(34, 40)}  # int(40*0.85)=34
        self.assertTrue(calls)
        self.assertFalse(holdout & set(calls))


_loader = h003.load

if __name__ == "__main__":
    unittest.main()
