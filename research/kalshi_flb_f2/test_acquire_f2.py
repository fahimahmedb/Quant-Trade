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


if __name__ == "__main__":
    unittest.main()
