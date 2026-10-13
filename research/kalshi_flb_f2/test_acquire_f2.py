import datetime as dt
import hashlib
import os
import sys
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(__file__))
import acquire_f2 as a  # noqa: E402


def mk(i, st="2025-09-01T12:00:00Z", mtype="binary", hours=48, **kw):
    close = a.parse_t(st) - dt.timedelta(hours=1)
    m = {"ticker": f"T{i}", "event_ticker": f"E{i}", "market_type": mtype, "result": "yes", "volume_fp": "9",
         "open_time": (close - dt.timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "close_time": close.strftime("%Y-%m-%dT%H:%M:%SZ"), "settlement_ts": st, "can_close_early": False}
    m.update(kw)
    return m


class T(unittest.TestCase):
    def test_blind_filter_counts_and_no_outcome_fields(self):
        ms = [mk(1), mk(2, mtype="scalar"), mk(3, st="2024-01-01T00:00:00Z"), mk(4, hours=3), mk(5, settlement_ts=None),
              mk(6, st="2026-08-01T00:00:00Z")]
        rows, c = a.blind_filter(ms)
        self.assertEqual(c, {"input": 6, "no_settlement": 1, "outside_window": 2, "not_binary": 1, "open_lt_24h": 1, "kept": 1})
        self.assertEqual(set(rows[0]), set(a.BLIND_FIELDS))
        self.assertNotIn("result", rows[0])
        self.assertNotIn("volume_fp", rows[0])

    def test_window_boundaries(self):
        rows, _ = a.blind_filter([mk(1, st="2025-05-01T00:00:00Z"), mk(2, st="2026-07-31T23:59:59Z")])
        self.assertEqual(len(rows), 2)

    def test_candle_params(self):
        p = a.candle_params("2025-09-01T12:00:00Z")
        t = a.parse_t("2025-09-01T12:00:00Z")
        self.assertEqual(p["end_ts"], int(t.timestamp()) - 24 * 3600)
        self.assertEqual(p["start_ts"], int(t.timestamp()) - 25 * 3600 + 1)
        self.assertEqual(p["period_interval"], 60)

    def test_subsample_rule_keeps_event_together_and_is_deterministic(self):
        rows = [{"event_ticker": f"E{i // 3}"} for i in range(300)]
        keep = a.subsample_events(rows)
        evs = {r["event_ticker"] for r in keep}
        for e in evs:
            self.assertEqual(sum(1 for r in keep if r["event_ticker"] == e), 3)
        self.assertEqual(keep, a.subsample_events(rows))
        e0 = "E0"
        self.assertEqual(e0 in evs, hashlib.sha256(e0.encode("utf-8")).digest()[0] < 0x80)

    def test_projected_hours(self):
        self.assertAlmostEqual(a.projected_hours(90000, 5000, 100), (95102) / 5 / 3600)


class Stages(unittest.TestCase):
    def fake(self, pages):
        it = iter(pages)

        def f(path, params=None, tolerate=False):
            if path == "/historical/cutoff":
                return "u", b"{}", {"market_settled_ts": "2026-08-09T00:00:00Z"}
            if path == "/historical/markets":
                body = next(it)
                import json as j
                return "u", j.dumps(body).encode(), body
            if path.endswith("/candlesticks"):
                import json as j
                b = {"candlesticks": [{"end_period_ts": 1, "yes_bid": {"close": "0.9"}, "yes_ask": {"close": "0.92"}, "open_interest": "5"}]}
                return "u", j.dumps(b).encode(), b
            if path.startswith("/events/"):
                import json as j
                b = {"event": {"event_ticker": path.split("/")[-1], "series_ticker": "SER"}}
                return "u", j.dumps(b).encode(), b
            if path == "/series/SER":
                import json as j
                b = {"series": {"ticker": "SER", "category": "Politics"}}
                return "u", j.dumps(b).encode(), b
            if path == "/series/fee_changes":
                import json as j
                b = {"series_fee_change_arr": [{"id": "1", "series_ticker": "SER", "fee_type": "quadratic",
                                                 "fee_multiplier": 1.0, "scheduled_ts": "2025-01-01T00:00:00Z"}]}
                return "u", j.dumps(b).encode(), b
            raise AssertionError(path)
        return f

    def test_duplicate_tickers_dropped_and_counted(self):
        import tempfile
        pages = [{"markets": [mk(1), mk(1)], "cursor": "c"}, {"markets": [mk(1), mk(2)], "cursor": ""}]
        with tempfile.TemporaryDirectory() as t:
            c = a.stage_list(os.path.join(t, "o"), fetch=self.fake(pages))
            self.assertEqual(c["kept"], 4)
            self.assertEqual(len(a.read_manifest_rows(os.path.join(t, "o"))), 2)

    def test_cutoff_move_aborts(self):
        import tempfile, json as j
        base = self.fake([{"markets": [mk(1)], "cursor": ""}])
        calls = {"n": 0}

        def f(path, params=None, tolerate=False):
            if path == "/historical/cutoff":
                calls["n"] += 1
                return "u", b"{}", {"market_settled_ts": f"2026-08-0{calls['n']}T00:00:00Z"}
            return base(path, params)
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(RuntimeError):
                a.stage_list(os.path.join(t, "o"), fetch=f)

    def test_candle_resume_validates_and_backfills(self):
        import tempfile
        pages = [{"markets": [mk(1), mk(2)], "cursor": ""}]
        with tempfile.TemporaryDirectory() as t:
            out = os.path.join(t, "o")
            f = self.fake(pages)
            a.stage_list(out, fetch=f)
            os.makedirs(f"{out}/raw/candles")
            open(f"{out}/raw/candles/T1.json", "w").write('{"candlestic')   # truncated by a crash
            self.assertEqual(a.stage_candles(out, fetch=f), 2)              # corrupt file refetched
            os.remove(f"{out}/candles_manifest.jsonl")
            self.assertEqual(a.stage_candles(out, fetch=f), 0)              # valid files back-filled, not refetched
            self.assertTrue(os.path.exists(f"{out}/candles_manifest.jsonl"))

    def test_atomic_save_no_tmp_left(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            a.save_once(os.path.join(t, "x", "y.json"), b"{}")
            self.assertEqual(os.listdir(os.path.join(t, "x")), ["y.json"])
            with self.assertRaises(FileExistsError):
                a.save_once(os.path.join(t, "x", "y.json"), b"{}")
            self.assertEqual(os.listdir(os.path.join(t, "x")), ["y.json"])

    def test_full_offline_pipeline(self):
        import tempfile, json as j
        pages = [{"markets": [mk(1), mk(2, mtype="scalar")], "cursor": "c1"}, {"markets": [mk(3)], "cursor": ""}]
        with tempfile.TemporaryDirectory() as t:
            out, an = os.path.join(t, "o"), os.path.join(t, "a")
            f = self.fake(pages)
            counts = a.stage_list(out, fetch=f)
            self.assertEqual(counts["kept"], 2)
            self.assertEqual(a.stage_candles(out, fetch=f), 2)
            self.assertEqual(a.stage_candles(out, fetch=f), 0)        # resumable / idempotent
            meta = a.stage_meta(out, fetch=f)
            self.assertEqual(meta["series"], 1)
            self.assertEqual(a.stage_assemble(out, an), 2)
            with open(os.path.join(an, "fee_table.json")) as fh:
                self.assertEqual(j.load(fh)["series"]["SER"][0][2], "quadratic")
            with open(os.path.join(out, "blinded_manifest.jsonl")) as fh:
                self.assertNotIn("result", fh.read())
            # the harness accepts the assembled directory (fail-closed schema check)
            import run_f2
            self.assertEqual(len(run_f2.load(an)[0]), 2)


if __name__ == "__main__":
    unittest.main()
