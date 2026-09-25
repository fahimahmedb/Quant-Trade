"""Applying collected feeds: forward-only appends, seam rebasing, schedule checks.

Fixtures are synthetic; they are never evidence.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from quant.dataplane.adapters import DataUnavailable
from quant.dataplane.feeds import (daily_funding, daily_marks, etf_forward_rows,
                                   merged_fomc_days, perp_forward_rows, read_latest)
from quant.dataplane.panel import PricePanel


def _bar(day, symbol, close, adj, **extra):
    """A committed panel row."""
    return {"date": day, "symbol": symbol, "open": close, "high": close, "low": close,
            "close": close, "adj_close": adj, "volume": 100, **extra}


def _feed(day, symbol, close, adj):
    """A feed record as read_latest returns it (observed after the close)."""
    return {**_bar(day, symbol, close, adj), "_observed_at": f"{day}T23:30:00+00:00"}


class EtfForwardTests(unittest.TestCase):
    def setUp(self):
        self.committed = PricePanel([_bar("2026-09-10", s, 100, 90) for s in ("A", "B")]
                                    + [_bar("2026-09-11", s, 101, 91) for s in ("A", "B")])

    def test_rebased_at_the_seam_and_history_untouched(self):
        # the feed's basis was restated (a dividend): seam adj is 95.95 instead of 91
        feed = {f"{d}|{s}": _feed(d, s, c, a) for s in ("A", "B") for d, c, a in
                (("2026-09-11", 101, 95.95), ("2026-09-14", 102, 96.9))}
        rows, info = etf_forward_rows(self.committed, feed, ["A", "B"])
        self.assertEqual(info, {})
        self.assertEqual({r["date"] for r in rows}, {"2026-09-14"})
        row = next(r for r in rows if r["symbol"] == "A")
        self.assertAlmostEqual(row["adj_close"] / 91, 96.9 / 95.95)   # return preserved

    def test_no_bridge_across_a_gap_or_an_incomplete_session(self):
        no_seam = {"2026-09-14|A": _feed("2026-09-14", "A", 102, 96),
                   "2026-09-14|B": _feed("2026-09-14", "B", 102, 96)}
        rows, info = etf_forward_rows(self.committed, no_seam, ["A", "B"])
        self.assertEqual(rows, [])
        self.assertIn("seam", info["blocked"])
        partial = {f"{d}|{s}": _feed(d, s, 101, 91) for s in ("A", "B") for d in ("2026-09-11",)}
        partial["2026-09-14|A"] = _feed("2026-09-14", "A", 102, 92)      # B missing
        partial["2026-09-15|A"] = _feed("2026-09-15", "A", 103, 93)
        partial["2026-09-15|B"] = _feed("2026-09-15", "B", 103, 93)
        rows, info = etf_forward_rows(self.committed, partial, ["A", "B"])
        self.assertEqual(rows, [])
        self.assertEqual(info, {"blocked_at": "2026-09-14", "missing_symbols": ["B"]})

    def test_intraday_observation_is_not_final(self):
        feed = {f"{d}|{s}": _feed(d, s, 101, 91) for s in ("A", "B") for d in ("2026-09-11",)}
        for s_ in ("A", "B"):
            early = _feed("2026-09-14", s_, 102, 92)
            early["_observed_at"] = "2026-09-14T15:00:00+00:00"     # during the session
            feed[f"2026-09-14|{s_}"] = early
        rows, info = etf_forward_rows(self.committed, feed, ["A", "B"])
        self.assertEqual(rows, [])

    def test_latest_restatement_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "s.jsonl"
            lines = [{"key": "k", "observed_at": "t1", "record": {"v": 1}},
                     {"key": "k#restated@t2", "observed_at": "t2", "record": {"v": 2}}]
            path.write_text("\n".join(json.dumps(line) for line in lines) + "\n{broken")
            self.assertEqual(read_latest(path), {"k": {"v": 2, "_observed_at": "t2"}})


class FomcMergeTests(unittest.TestCase):
    def test_adds_future_dates_and_refuses_contradictions(self):
        committed = ["2026-07-29", "2026-09-16", "2026-10-28"]
        feed = {d: {"decision_date": d} for d in ("2026-07-29", "2026-09-16", "2026-11-04",
                                                   "2027-01-27")}
        merged = merged_fomc_days(committed, feed, as_of="2026-09-25")
        # a future meeting moved (10-28 -> 11-04) is replaced, not kept as a phantom
        self.assertEqual(merged, ["2026-07-29", "2026-09-16", "2026-11-04", "2027-01-27"])
        wrong = {d: {"decision_date": d} for d in ("2026-07-29", "2026-09-17")}
        with self.assertRaises(DataUnavailable):
            merged_fomc_days(committed, wrong, as_of="2026-09-25")


class PerpForwardTests(unittest.TestCase):
    def test_days_complete_only_after_they_end_and_with_the_implied_count(self):
        from datetime import datetime, timezone
        base = 1_790_000_000_000 - (1_790_000_000_000 % 86_400_000)      # a UTC midnight
        day = datetime.fromtimestamp(base / 1000, tz=timezone.utc).date().isoformat()
        end = datetime.fromtimestamp(base / 1000 + 86_400 + 7_200, tz=timezone.utc).isoformat()
        early = datetime.fromtimestamp(base / 1000 + 43_200, tz=timezone.utc).isoformat()
        hl = [{"venue": "HYPERLIQUID", "coin": "ETH", "time_ms": base + h * 3_600_000 + 37,
               "rate": 0.00001, "_observed_at": end} for h in range(0, 24)]   # 00:00..23:00
        by = [{"venue": "BYBIT", "coin": "ETH", "time_ms": base + h * 8 * 3_600_000,
               "rate": 0.0001, "_observed_at": end} for h in (1, 2, 3)]       # 08, 16, 24:00
        four_hourly = [{"venue": "OKX", "coin": "ETH", "time_ms": base + h * 4 * 3_600_000,
                        "rate": 0.1, "_observed_at": end} for h in (1, 2, 3)]  # half a day
        funding = daily_funding(hl + by + four_hourly)
        self.assertAlmostEqual(funding[("HL", "ETH", day)], 24 * 0.00001)
        self.assertAlmostEqual(funding[("BY", "ETH", day)], 3 * 0.0001)
        self.assertNotIn(("OK", "ETH", day), funding)       # 3 of 6 four-hourly settlements
        unfinished = daily_funding([{**item, "_observed_at": early} for item in hl])
        self.assertEqual(unfinished, {})

    def test_close_is_the_first_snapshot_after_midnight_and_proxies_are_refused(self):
        marks = daily_marks([("2026-09-24T18|ETH", {"mark": 1.0, "day_notional_volume": 1}),
                             ("2026-09-25T06|ETH", {"mark": 3.0, "day_notional_volume": 3}),
                             ("2026-09-25T00|ETH", {"mark": 2.0, "day_notional_volume": 2})])
        self.assertEqual(marks, {("ETH", "2026-09-24"): (2.0, 2)})
        committed = PricePanel([_bar("2026-09-23", "HL.ETH", 1, 1),
                                _bar("2026-09-23", "BY.ETH", 1, 1)])
        funding = {("HL", "ETH", "2026-09-24"): 0.001, ("BY", "ETH", "2026-09-24"): 0.002}
        rows = perp_forward_rows(committed, funding, marks)
        self.assertEqual([r["symbol"] for r in rows], ["HL.ETH"])


class SyncGuardTests(unittest.TestCase):
    def test_a_gap_or_invalid_extension_writes_nothing(self):
        from quant.dataplane.ingest import _append_if_valid
        from quant.dataplane.registry import DatasetRecord, DatasetRegistry
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            panel = PricePanel([_bar("2025-05-15", "HL.BTC", 1, 1)])
            record = DatasetRecord(dataset_id="x", source="fixture", adapter="fixture",
                                   path="data/datasets/x.csv.gz",
                                   point_in_time={"min_rows_per_symbol": 1})
            registry = DatasetRegistry(root / "reg.json", root)
            late = [_bar("2026-09-24", "HL.BTC", 2, 2)]
            verdict = _append_if_valid(registry, record, panel, late, ["HL.BTC"], root,
                                       "2025-05-16")
            self.assertIn("gap", verdict["blocked"])
            self.assertFalse((root / "data/datasets/x.csv.gz").exists())
            nxt = [_bar("2025-05-16", "HL.BTC", 2, 2)]
            verdict = _append_if_valid(registry, record, panel, nxt, ["HL.BTC", "BY.BTC"], root,
                                       "2025-05-16")
            self.assertIn("fails validation", verdict["blocked"])
            self.assertFalse((root / "data/datasets/x.csv.gz").exists())


if __name__ == "__main__":
    unittest.main()
