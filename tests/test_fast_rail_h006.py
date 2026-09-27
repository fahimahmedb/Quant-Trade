"""H-006 Hyperliquid new-listing fade: causality, eligibility, survivorship, funding sign."""

from __future__ import annotations

import datetime as dt
import gzip
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.dataplane.panel import PricePanel, Window  # noqa: E402
from quant.factory.evaluate import walk_forward  # noqa: E402
from quant.factory.lanes import (HL_LISTINGS_DATASET, lane_definitions,  # noqa: E402
                                 lane_definitions as _lanes)
from quant.factory.signals import LISTING_FADE, StrategySpec, weights_for  # noqa: E402

DATASET = ROOT / "data" / "datasets" / f"{HL_LISTINGS_DATASET}.csv.gz"
RAW = ROOT / "data" / "raw" / "fast_rail" / "h006"


def _builder():
    spec = importlib.util.spec_from_file_location(
        "build_hl_listings_dataset", ROOT / "scripts" / "build_hl_listings_dataset.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _day(start: str, offset: int) -> str:
    return (dt.date.fromisoformat(start) + dt.timedelta(days=offset)).isoformat()


def _panel(listings: dict[str, tuple[int, int]], days: int = 60, carry: float = 0.0,
           drift: float = 0.0) -> PricePanel:
    """HL.BTC every day; each coin from its listing offset, (offset, eligible)."""
    rows = []
    for index in range(days):
        date = _day("2024-01-01", index)
        rows.append({"date": date, "symbol": "HL.BTC", "open": 100.0, "high": 100.0,
                     "low": 100.0, "close": 100.0, "adj_close": 100.0, "volume": 1e9,
                     "carry_rate": 0.0})
        for coin, (listed, eligible) in listings.items():
            age = index - listed
            if age < 1:          # listing day itself is partial: no row
                continue
            price = 10.0 * (1.0 + drift) ** age
            rows.append({"date": date, "symbol": coin, "open": price, "high": price,
                         "low": price, "close": price, "adj_close": price, "volume": 1e7,
                         "carry_rate": carry, "listing_age_days": float(age),
                         "listing_eligible": float(eligible)})
    return PricePanel(rows)


def _spec(hold: int = 7, hedge: str = "", universe=("HL.BTC", "HL.NEW", "HL.OLD", "HL.LATE")):
    return StrategySpec(family=LISTING_FADE, universe=list(universe), lookback_days=hold,
                        direction=-1, min_abs_score=0.0, max_weight=0.10, gross_exposure=1.0,
                        holding_days=1, no_trade_band=0.0, dataset_id=HL_LISTINGS_DATASET,
                        calendar_symbol="HL.BTC", hedge_symbol=hedge)


class ListingFadeSignalTests(unittest.TestCase):
    def setUp(self):
        self.panel = _panel({"HL.NEW": (5, 1), "HL.OLD": (0, 0), "HL.LATE": (20, 1)})

    def test_truncating_after_d_never_changes_weights_at_d(self):
        for hedge in ("", "HL.BTC"):
            spec = _spec(14, hedge)
            for date in self.panel.dates_for("HL.BTC"):
                truncated = self.panel.restrict(end=date)
                self.assertEqual(weights_for(self.panel, spec, date),
                                 weights_for(truncated, spec, date), (hedge, date))

    def test_window_starts_first_full_day_and_lasts_n_sessions(self):
        spec = _spec(7)
        shorted = [date for date in self.panel.dates_for("HL.BTC")
                   if weights_for(self.panel, spec, date).get("HL.NEW", 0.0) < 0]
        self.assertEqual(shorted, [_day("2024-01-01", 5 + k) for k in range(1, 8)])

    def test_pre_cutoff_coin_never_traded(self):
        for hold in (7, 14, 30):
            for hedge in ("", "HL.BTC"):
                spec = _spec(hold, hedge)
                for date in self.panel.dates_for("HL.BTC"):
                    self.assertNotIn("HL.OLD", {s for s, w in
                                                weights_for(self.panel, spec, date).items() if w})
                rows = walk_forward(self.panel, spec, Window("ALL", self.panel.dates[0],
                                                            self.panel.dates[-1]), 10.0)
                self.assertFalse(any(row["weights"].get("HL.OLD") for row in rows))

    def test_flat_target_when_no_coin_in_window(self):
        spec = _spec(7, "HL.BTC")
        self.assertEqual(weights_for(self.panel, spec, "2024-01-02"), {"HL.BTC": 0.0})
        self.assertEqual(weights_for(self.panel, _spec(7), "2024-01-02"), {"HL.BTC": 0.0})
        rows = walk_forward(self.panel, spec, Window("ALL", self.panel.dates[0],
                                                    self.panel.dates[-1]), 10.0)
        after = [row for row in rows if "2024-01-14" <= row["signal_date"] < "2024-01-21"]
        self.assertTrue(after)
        self.assertTrue(all(row["positions"] == 0 for row in after))

    def test_equal_weight_capped_and_hedge_equal_notional(self):
        panel = _panel({f"HL.C{i}": (3, 1) for i in range(12)})
        universe = ["HL.BTC"] + [f"HL.C{i}" for i in range(12)]
        unhedged = weights_for(panel, _spec(7, universe=universe), "2024-01-06")
        self.assertEqual(len(unhedged), 12)
        self.assertAlmostEqual(sum(unhedged.values()), -1.0)
        hedged = weights_for(panel, _spec(7, "HL.BTC", universe), "2024-01-06")
        self.assertAlmostEqual(hedged["HL.BTC"], -sum(w for s, w in hedged.items()
                                                      if s != "HL.BTC"))
        self.assertAlmostEqual(sum(abs(w) for w in hedged.values()), 1.0)
        few = weights_for(panel, _spec(7, universe=universe[:3]), "2024-01-06")
        self.assertEqual(set(few.values()), {-0.10})

    def test_short_receives_positive_funding(self):
        panel = _panel({"HL.NEW": (2, 1)}, carry=0.001)
        rows = walk_forward(panel, _spec(7, universe=["HL.BTC", "HL.NEW"]),
                            Window("ALL", panel.dates[0], panel.dates[-1]), 0.0)
        held = [row for row in rows if row["weights"].get("HL.NEW")]
        self.assertEqual(len(held), 7)
        for row in held:
            self.assertAlmostEqual(row["gross_return"], 0.10 * 0.001)

    def test_short_profits_from_decline(self):
        panel = _panel({"HL.NEW": (2, 1)}, drift=-0.01)
        rows = walk_forward(panel, _spec(7, universe=["HL.BTC", "HL.NEW"]),
                            Window("ALL", panel.dates[0], panel.dates[-1]), 0.0)
        self.assertTrue(all(row["gross_return"] > 0 for row in rows if row["positions"]))

    def test_lane_grid_is_the_registered_one(self):
        definition = _lanes(["HL.BTC"], HL_LISTINGS_DATASET)["hl_listing_fade"]
        grid = [(spec.lookback_days, spec.hedge_symbol) for spec in definition["grid"]]
        self.assertEqual(sorted(grid), sorted((n, h) for n in (7, 14, 30) for h in ("", "HL.BTC")))
        self.assertEqual(definition["prior_trials"], 0)
        self.assertEqual(definition["cost_bps"], 10.0)
        self.assertEqual(definition["benchmark"], "HL.BTC")
        self.assertEqual(definition["pristine_after"], "2026-09-25")
        from quant.desk.compliance import assess
        self.assertTrue(assess({"compliance": definition["compliance"]})["approved"])

    def test_spec_without_hedge_keeps_earlier_grid_hashes(self):
        # Adding hedge_symbol must not change any earlier lane's spec document.
        spec = lane_definitions(["SPY", "TLT", "SPY_ON"], "us_calendar_legs_daily")
        for definition in spec.values():
            for item in definition["grid"]:
                self.assertNotIn("hedge_symbol", item.to_dict())
                self.assertEqual(StrategySpec(**item.to_dict()), item)


class ListingDatasetTests(unittest.TestCase):
    def test_builder_eligibility_and_funding_filter(self):
        builder = _builder()
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp)

            def put(name, payload):
                path = raw / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(gzip.compress(json.dumps(payload).encode()))

            put("meta.json.gz", {"universe": [{"name": "BTC"}, {"name": "OLD"},
                                              {"name": "NEW", "isDelisted": True}]})
            for coin, first in (("BTC", "2023-03-01"), ("OLD", "2023-05-20"),
                                ("NEW", "2024-02-01")):
                start = builder._ms(first)
                candles = [{"t": start - builder.DAY_MS, "c": "1", "v": "0", "n": 0}]
                candles += [{"t": start + k * builder.DAY_MS, "c": "2", "v": "5", "n": 9}
                            for k in range(5)]
                put(f"candles/{coin}.json.gz", candles)
                funding = [{"time": start + k * builder.DAY_MS + h * 3_600_000 + 7,
                            "fundingRate": "0.0001"}
                           for k in range(5) for h in range(24 if k else 10)]
                put(f"funding/{coin}/0000.json.gz", funding)
            rows, symbols, listings = builder.build(raw)
        by = {(row["symbol"], row["date"]): row for row in rows}
        self.assertTrue(listings["NEW"]["delisted"])
        self.assertIn("HL.NEW", symbols)
        self.assertFalse(listings["OLD"]["eligible"])
        self.assertTrue(listings["NEW"]["eligible"])
        self.assertNotIn(("HL.NEW", "2024-02-01"), by)       # 10 prints: dropped
        first = by[("HL.NEW", "2024-02-02")]
        self.assertEqual(first["listing_age_days"], 1.0)
        self.assertEqual(first["listing_eligible"], 1.0)
        self.assertAlmostEqual(first["carry_rate"], 24 * 0.0001)
        self.assertEqual(by[("HL.OLD", "2023-05-21")]["listing_eligible"], 0.0)
        self.assertNotIn(("HL.BTC", "2023-02-28"), by)       # zero-trade backfill

    @unittest.skipUnless(DATASET.exists(), "hl_listings_daily not built")
    def test_committed_dataset_includes_delisted_coins(self):
        listings = json.loads((RAW / "listings.json").read_text())
        delisted = sorted(f"HL.{coin}" for coin, item in listings.items()
                          if item["delisted"] and item["eligible"] and item["rows"])
        self.assertGreaterEqual(len(delisted), 10)
        panel = PricePanel.load(DATASET)
        self.assertTrue(set(delisted) <= set(panel.symbols))
        meta = json.loads((DATASET.parent / f"{HL_LISTINGS_DATASET}.csv.meta.json").read_text())
        self.assertTrue(set(delisted) <= set(meta["expected_symbols"]))

    @unittest.skipUnless(DATASET.exists(), "hl_listings_daily not built")
    def test_committed_dataset_listing_features_are_consistent(self):
        panel = PricePanel.load(DATASET)
        for symbol in panel.symbols:
            if symbol == "HL.BTC":
                continue
            dates = panel.dates_for(symbol)
            listed = {(dt.date.fromisoformat(day)
                       - dt.timedelta(days=int(panel.feature(day, symbol, "listing_age_days"))))
                      for day in dates}
            self.assertEqual(len(listed), 1, symbol)
            eligible = {panel.feature(day, symbol, "listing_eligible") for day in dates}
            self.assertEqual(len(eligible), 1, symbol)
            self.assertEqual(eligible.pop() == 1.0,
                             min(listed).isoformat() >= _builder().ELIGIBLE_FROM, symbol)


if __name__ == "__main__":
    unittest.main()
