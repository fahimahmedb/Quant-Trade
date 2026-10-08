import datetime as dt
import json
import math
import os
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(__file__))
import run_f2 as r  # noqa: E402


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


CLOSE0 = dt.datetime(2025, 9, 1, 12, 0, tzinfo=dt.timezone.utc)


def market(i, close=None, result="yes", **kw):
    close = close or CLOSE0 + dt.timedelta(days=i)
    m = {"ticker": f"T{i}", "event_ticker": f"E{i}", "market_type": "binary", "result": result,
         "open_time": iso(close - dt.timedelta(days=5)), "close_time": iso(close),
         "settlement_ts": iso(close + dt.timedelta(hours=1)), "volume_fp": "5000.00", "can_close_early": False}
    m.update(kw)
    return m


def candle(close, bid=0.90, ask=0.92, oi="2000.00", end_off_h=24.0):
    end = int((close - dt.timedelta(hours=end_off_h)).timestamp())
    q = lambda v: {"open": str(v), "low": str(v), "high": str(v), "close": (None if v is None else str(v))}
    return {"end_period_ts": end, "yes_bid": q(bid), "yes_ask": q(ask), "price": {}, "volume": "10.00", "open_interest": oi}


def build(tmp, ms, candles, cats=None, fees=None):
    os.makedirs(os.path.join(tmp, "candles"), exist_ok=True)
    with open(os.path.join(tmp, "markets.jsonl"), "w") as f:
        for m in ms:
            f.write(json.dumps(m) + "\n")
    for t, body in candles.items():
        json.dump({"candlesticks": body}, open(os.path.join(tmp, "candles", t + ".json"), "w"))
    json.dump({m["event_ticker"]: "S" + m["event_ticker"] for m in ms}, open(os.path.join(tmp, "event_series.json"), "w"))
    json.dump(cats or {"S" + m["event_ticker"]: "Politics" for m in ms}, open(os.path.join(tmp, "series_category.json"), "w"))
    json.dump(fees or {"default_multiplier": 1.0, "changes": []}, open(os.path.join(tmp, "fee_table.json"), "w"))


class Units(unittest.TestCase):
    def test_fee_rounding(self):
        self.assertEqual(r.ceil_cent(0.07 * 0.99 * 0.01), 0.01)   # cent ceiling at 99c
        self.assertAlmostEqual(r.ceil6(0.07 * 0.95 * 0.05), 0.003325)
        self.assertLess(r.ceil6(0.07 * 0.95 * 0.05), r.ceil_cent(0.07 * 0.95 * 0.05))

    def test_signal_candle_window(self):
        c0 = CLOSE0
        ok = candle(c0, end_off_h=24.0)
        edge_hi = candle(c0, end_off_h=24.0)             # == T-24h included
        edge_lo = candle(c0, end_off_h=25.0)             # == T-25h excluded
        self.assertIsNotNone(r.signal_candle({"candlesticks": [ok]}, c0))
        self.assertIsNone(r.signal_candle({"candlesticks": [edge_lo]}, c0))
        self.assertIsNone(r.signal_candle({"candlesticks": [ok, edge_hi]}, c0))     # two candles
        self.assertIsNone(r.signal_candle({"candlesticks": [candle(c0, end_off_h=23.0)]}, c0))  # after T-24h
        with self.assertRaises(r.FormatError):
            r.signal_candle({}, c0)

    def test_rule_sides_and_returns(self):
        m = market(1, result="yes")
        why, rec = r.evaluate_market(m, candle(CLOSE0 + dt.timedelta(days=1), bid=0.88, ask=0.90), {}, "Politics")
        self.assertIsNone(why)
        self.assertEqual(rec["side"], "yes")
        fee = r.ceil6(0.07 * 0.9 * 0.1)
        self.assertAlmostEqual(rec["net"], (1 - 0.9 - fee) / (0.9 + fee))
        # NO side: yes bid 0.08, ask 0.10 -> ask_no = 0.92
        why, rec = r.evaluate_market(market(1, result="no"), candle(CLOSE0 + dt.timedelta(days=1), bid=0.08, ask=0.10), {}, "x")
        self.assertEqual(rec["side"], "no")
        self.assertAlmostEqual(rec["price"], 0.92)
        self.assertGreater(rec["net"], 0)
        why, _ = r.evaluate_market(market(1), candle(CLOSE0 + dt.timedelta(days=1), bid=0.40, ask=0.45), {}, "x")
        self.assertEqual(why, "no_signal")
        why, _ = r.evaluate_market(market(1), candle(CLOSE0 + dt.timedelta(days=1), bid=0.60, ask=0.95), {}, "x")
        self.assertEqual(why, "spread")

    def test_99c_loses_even_when_winning(self):
        m = market(1, result="yes")
        _, rec = r.evaluate_market(m, candle(CLOSE0 + dt.timedelta(days=1), bid=0.98, ask=0.99), {}, "x")
        self.assertLessEqual(rec["net_stress"], 1e-12)    # cent-ceil fee wipes the 1c payoff: a win returns 0
        self.assertGreater(rec["net"], -1e-3)     # unrounded fee barely nonnegative-ish

    def test_fee_table_multiplier(self):
        t = {"default_multiplier": 1.0, "changes": [["2025-08-01T00:00:00Z", 0.5]]}
        self.assertEqual(r.fee_mult(t, dt.datetime(2025, 7, 1, tzinfo=dt.timezone.utc)), 1.0)
        self.assertEqual(r.fee_mult(t, dt.datetime(2025, 9, 1, tzinfo=dt.timezone.utc)), 0.5)

    def test_cluster_stat_matches_manual(self):
        rows = [("a", 0.1, 0.1), ("a", -0.1, -0.1), ("b", 0.2, 0.2), ("c", 0.0, 0.0)]
        s = r.cluster_stat(rows)
        mu = 0.05
        cl = {"a": -0.10, "b": 0.15, "c": -0.05}
        se = math.sqrt(3 / 2 * sum(v * v for v in cl.values())) / 4
        self.assertAlmostEqual(s["se"], se)
        self.assertAlmostEqual(s["mean"], mu)

    def test_classify(self):
        p = {"n_clusters": 300, "t": 3.0, "se": 0.004, "mean": 0.012}
        self.assertEqual(r.classify(p, {"mean": 0.001}), "CONFIRMED")
        self.assertEqual(r.classify(p, {"mean": -0.001}), "INCONCLUSIVE_UNDERPOWERED")
        low = {"n_clusters": 300, "t": 0.1, "se": 0.004, "mean": 0.0005}
        self.assertEqual(r.classify(low, {"mean": 0.0}), "NOT_CONFIRMED_EXCLUDES_+1.0%")
        few = {"n_clusters": 100, "t": 5.0, "se": 0.001, "mean": 0.05}
        self.assertEqual(r.classify(few, {"mean": 0.05}), "INCONCLUSIVE_UNDERPOWERED")
        self.assertAlmostEqual(r.Z_GATE, 2.128045, places=5)


class EndToEnd(unittest.TestCase):
    def test_pipeline_filters_and_counts(self):
        with tempfile.TemporaryDirectory() as t:
            ms, cd = [], {}
            for i in range(10):
                m = market(i, result="yes")
                ms.append(m)
                cd[m["ticker"]] = [candle(ts_close(m), bid=0.93, ask=0.95)]
            ms.append(market(20, can_close_early=True)); cd["T20"] = [candle(ts_close(ms[-1]))]
            ms.append(market(21, result="")); cd["T21"] = [candle(ts_close(ms[-1]))]
            ms.append(market(22, market_type="scalar"))
            ms.append(market(23, close=dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc)))
            ms.append(market(24, open_time=iso(CLOSE0 + dt.timedelta(days=24) - dt.timedelta(hours=3)))); cd["T24"] = [candle(ts_close(ms[-1]))]
            ms.append(market(25)); cd["T25"] = [candle(ts_close(ms[-1]), oi="10.00")]   # low OI
            ms.append(market(26)); cd["T26"] = [candle(ts_close(ms[-1]), end_off_h=23.0)]   # candle after T-24h
            build(t, ms, cd, cats={**{f"SE{i}": "Politics" for i in range(30)}, "SE22": "Politics"})
            out = r.run(t, os.path.join(t, "res", "o.json"))
            ex = out["exclusions"]
            self.assertEqual(ex["void_or_scalar_result"], 1)
            self.assertEqual(ex["not_binary"], 1)
            self.assertEqual(ex["outside_window"], 1)
            self.assertEqual(ex["open_lt_24h"], 1)
            self.assertEqual(ex["candle_count_not_one"], 1)
            self.assertEqual(out["n_primary_markets"], 10)     # early-close excluded, low OI excluded
            self.assertEqual(out["primary"]["n_events"], 10)
            self.assertEqual(out["status"], "INCONCLUSIVE_UNDERPOWERED")   # < 250 clusters
            self.assertIn("early_close_capable", out["sensitivities"])
            with self.assertRaises(FileExistsError):
                r.run(t, os.path.join(t, "res", "o.json"))

    def test_missing_field_fails_closed_without_result(self):
        with tempfile.TemporaryDirectory() as t:
            m = market(1); del m["close_time"]
            build(t, [m], {})
            p = os.path.join(t, "res", "o.json")
            with self.assertRaises(r.FormatError):
                r.run(t, p)
            self.assertFalse(os.path.exists(p))

    def test_category_sports_excluded_from_primary(self):
        with tempfile.TemporaryDirectory() as t:
            ms = [market(1), market(2)]
            cd = {m["ticker"]: [candle(ts_close(m), bid=0.93, ask=0.95)] for m in ms}
            build(t, ms, cd, cats={"SE1": "Sports", "SE2": "Politics"})
            out = r.run(t, os.path.join(t, "res", "o.json"))
            self.assertEqual(out["n_primary_markets"], 1)
            self.assertEqual(out["sensitivities"]["sports"]["base"]["n_events"], 1)

    def test_event_averaging_and_date_cluster(self):
        recs = [{"event": "E", "close": CLOSE0, "net": 0.1, "net_stress": 0.1},
                {"event": "E", "close": CLOSE0 + dt.timedelta(days=3), "net": 0.3, "net_stress": 0.3}]
        rows = r.event_level(recs, r.day_key)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], CLOSE0.date().isoformat())   # earliest close date
        self.assertAlmostEqual(rows[0][1], 0.2)


def ts_close(m):
    return r.ts(m["close_time"])


if __name__ == "__main__":
    unittest.main()
