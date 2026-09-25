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
    return {"date": day, "symbol": symbol, "open": close, "high": close, "low": close,
            "close": close, "adj_close": adj, "volume": 100, **extra}


class EtfForwardTests(unittest.TestCase):
    def setUp(self):
        self.committed = PricePanel([_bar("2026-09-10", s, 100, 90) for s in ("A", "B")]
                                    + [_bar("2026-09-11", s, 101, 91) for s in ("A", "B")])

    def test_rebased_at_the_seam_and_history_untouched(self):
        # the feed's basis was restated (a dividend): seam adj is 95.95 instead of 91
        feed = {f"{d}|{s}": _bar(d, s, c, a) for s in ("A", "B") for d, c, a in
                (("2026-09-11", 101, 95.95), ("2026-09-14", 102, 96.9))}
        rows = etf_forward_rows(self.committed, feed, ["A", "B"])
        self.assertEqual({r["date"] for r in rows}, {"2026-09-14"})
        row = next(r for r in rows if r["symbol"] == "A")
        self.assertAlmostEqual(row["adj_close"] / 91, 96.9 / 95.95)   # return preserved

    def test_no_bridge_across_a_gap_or_an_incomplete_session(self):
        no_seam = {"2026-09-14|A": _bar("2026-09-14", "A", 102, 96),
                   "2026-09-14|B": _bar("2026-09-14", "B", 102, 96)}
        self.assertEqual(etf_forward_rows(self.committed, no_seam, ["A", "B"]), [])
        partial = {f"{d}|{s}": _bar(d, s, 101, 91) for s in ("A", "B") for d in ("2026-09-11",)}
        partial["2026-09-14|A"] = _bar("2026-09-14", "A", 102, 92)       # B missing
        partial["2026-09-15|A"] = _bar("2026-09-15", "A", 103, 93)
        partial["2026-09-15|B"] = _bar("2026-09-15", "B", 103, 93)
        self.assertEqual(etf_forward_rows(self.committed, partial, ["A", "B"]), [])

    def test_latest_restatement_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "s.jsonl"
            lines = [{"key": "k", "observed_at": "t1", "record": {"v": 1}},
                     {"key": "k#restated@t2", "observed_at": "t2", "record": {"v": 2}}]
            path.write_text("\n".join(json.dumps(line) for line in lines) + "\n{broken")
            self.assertEqual(read_latest(path), {"k": {"v": 2}})


class FomcMergeTests(unittest.TestCase):
    def test_adds_future_dates_and_refuses_contradictions(self):
        committed = ["2026-07-29", "2026-09-16"]
        feed = {d: {"decision_date": d} for d in ("2026-07-29", "2026-09-16", "2027-01-27")}
        self.assertEqual(merged_fomc_days(committed, feed)[-1], "2027-01-27")
        wrong = {d: {"decision_date": d} for d in ("2026-07-29", "2026-09-17")}
        with self.assertRaises(DataUnavailable):
            merged_fomc_days(committed, wrong)


class PerpForwardTests(unittest.TestCase):
    def test_complete_days_only_and_settlement_attribution(self):
        base = 1_790_000_000_000 - (1_790_000_000_000 % 86_400_000)      # a UTC midnight
        hl = [{"venue": "HYPERLIQUID", "coin": "ETH", "time_ms": base + h * 3_600_000,
               "rate": 0.00001} for h in range(1, 25)]                  # 01:00 .. 24:00
        by = [{"venue": "BYBIT", "coin": "ETH", "time_ms": base + h * 8 * 3_600_000,
               "rate": 0.0001} for h in (1, 2, 3)]                      # 08, 16, 24:00
        thin = [{"venue": "OKX", "coin": "ETH", "time_ms": base + 8 * 3_600_000, "rate": 0.1}]
        funding = daily_funding(hl + by + thin)
        from datetime import datetime, timezone
        day = datetime.fromtimestamp(base / 1000, tz=timezone.utc).date().isoformat()
        self.assertAlmostEqual(funding[("HL", "ETH", day)], 24 * 0.00001)
        self.assertAlmostEqual(funding[("BY", "ETH", day)], 3 * 0.0001)
        self.assertNotIn(("OK", "ETH", day), funding)                   # incomplete day
        marks = daily_marks([(f"{day}T05|ETH", {"mark": 2000.0, "day_notional_volume": 1e6}),
                             (f"{day}T23|ETH", {"mark": 2010.0, "day_notional_volume": 2e6})])
        committed = PricePanel([_bar("2020-01-01", "HL.ETH", 1, 1), _bar("2020-01-01", "BY.ETH", 1, 1)])
        rows = perp_forward_rows(committed, funding, marks)
        self.assertEqual({r["symbol"] for r in rows}, {"HL.ETH", "BY.ETH"})
        by_row = next(r for r in rows if r["symbol"] == "BY.ETH")
        self.assertEqual((by_row["close"], by_row["price_proxy"]), (2010.0, 1.0))


if __name__ == "__main__":
    unittest.main()
