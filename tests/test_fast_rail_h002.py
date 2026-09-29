"""Fast-rail H-002: Hyperliquid vs dYdX funding spread with a hysteresis exit.

Every number in these fixtures is INVENTED for the test (funding rates, prices,
venue listings). They are test fixtures, never evidence.
"""

from __future__ import annotations

import importlib.util
import random
import unittest
from datetime import date, timedelta
from pathlib import Path

from quant.dataplane.panel import PricePanel, Window
from quant.factory.evaluate import walk_forward
from quant.factory.lanes import (PERP_DYDX_DATASET, lane_definitions)
from quant.factory.signals import (DAYS_PER_YEAR, StrategySpec, funding_venues, weights_for)
from quant.factory.strategies import StrategyDefinition

ROOT = Path(__file__).resolve().parents[1]


def _builder():
    spec = importlib.util.spec_from_file_location(
        "build_perp_funding_hl_dydx", ROOT / "scripts" / "build_perp_funding_hl_dydx.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _days(count: int) -> list[str]:
    start = date(2025, 1, 1)
    return [(start + timedelta(days=offset)).isoformat() for offset in range(count)]


def _panel(days: list[str], carry: dict[str, list[float | None]],
           prices: dict[str, list[float]] | None = None) -> PricePanel:
    """INVENTED fixture panel: flat prices unless given; carry None = no bar."""
    rows = []
    for symbol, series in carry.items():
        for position, (day, rate) in enumerate(zip(days, series)):
            if rate is None:
                continue
            price = prices[symbol][position] if prices and symbol in prices else 100.0
            rows.append({"date": day, "symbol": symbol, "open": price, "high": price,
                         "low": price, "close": price, "adj_close": price, "volume": 1e7,
                         "carry_rate": rate})
    return PricePanel(rows)


def _spec(universe: list[str], entry: float = 0.5, exit_: float = 0.25,
          lookback: int = 1) -> StrategySpec:
    return StrategySpec(family="funding_spread", universe=universe, lookback_days=lookback,
                        direction=1, min_abs_score=entry, exit_abs_score=exit_,
                        max_weight=0.05, gross_exposure=1.0, holding_days=1,
                        no_trade_band=0.02, dataset_id=PERP_DYDX_DATASET,
                        calendar_symbol="HL.BTC")


def _nonzero(weights: dict[str, float]) -> dict[str, float]:
    return {symbol: value for symbol, value in weights.items() if abs(value) > 1e-12}


UNIVERSE = ["DY.BTC", "DY.X", "DY.Y", "HL.BTC", "HL.X", "HL.Y"]
#: INVENTED annualised HL-minus-dYdX spread path for coin X.
PATH = [0.0, 0.0, 0.6, 0.4, 0.3, 0.26, 0.2, 0.4, 0.6, -0.3, -0.6, 0.1]


def _path_panel(path: list[float] = PATH) -> PricePanel:
    n = len(path)
    return _panel(_days(n), {"HL.BTC": [0.0] * n, "DY.BTC": [0.0] * n,
                             "HL.X": [value / DAYS_PER_YEAR for value in path],
                             "DY.X": [0.0] * n, "HL.Y": [0.0] * n, "DY.Y": [0.0] * n})


def _random_panel(seed: int = 7, n: int = 60) -> PricePanel:
    rng = random.Random(seed)
    carry, prices = {}, {}
    for coin in ("BTC", "X", "Y", "Z"):
        level = 100.0
        for venue in ("HL", "DY"):
            carry[f"{venue}.{coin}"] = [rng.gauss(0.0, 0.004) for _ in range(n)]
        path = []
        for _ in range(n):
            level *= 1.0 + rng.gauss(0.0, 0.02)
            path.append(level)
        prices[f"HL.{coin}"] = path
        prices[f"DY.{coin}"] = [value * (1.0 + rng.gauss(0.0, 0.001)) for value in path]
    carry["DY.Z"][25] = None             # a missing dYdX day inside the history
    return _panel(_days(n), carry, prices)


class HysteresisRuleTests(unittest.TestCase):
    def test_holds_between_exit_and_entry_and_exits_below_half(self):
        panel = _path_panel()
        days = panel.dates
        held = [weights_for(panel, _spec(UNIVERSE), day).get("HL.X", 0.0) for day in days]
        # short HL (it charges longs more) while held; flip to long HL after -0.6
        expected = [0, 0, -1, -1, -1, -1, 0, 0, -1, 0, 1, 0]
        self.assertEqual([round(value / 0.05) for value in held], expected)
        stateless = [weights_for(panel, _spec(UNIVERSE, exit_=0.0), day).get("HL.X", 0.0)
                     for day in days]
        self.assertEqual([round(value / 0.05) for value in stateless],
                         [0, 0, -1, 0, 0, 0, 0, 0, -1, 0, 1, 0])

    def test_exit_above_entry_cannot_loosen_the_entry(self):
        panel = _path_panel()
        loose = [weights_for(panel, _spec(UNIVERSE, exit_=0.9), day) for day in panel.dates]
        strict = [weights_for(panel, _spec(UNIVERSE, exit_=0.0), day) for day in panel.dates]
        self.assertEqual(loose, strict)

    def test_hysteresis_is_causal(self):
        panel = _random_panel()
        spec = _spec(UNIVERSE + ["DY.Z", "HL.Z"], entry=0.8, exit_=0.4, lookback=3)
        full = {day: weights_for(panel, spec, day) for day in panel.dates}
        self.assertTrue(any(_nonzero(value) for value in full.values()))
        for cut in panel.dates[5::6]:
            truncated = panel.restrict(end=cut)
            for day in truncated.dates:
                self.assertEqual(weights_for(truncated, spec, day), full[day], (cut, day))
            # A shocked future (every later funding print reversed and inflated)
            # must not change a single past weight.
            rows = []
            for (day, symbol), bar in panel.bars.items():
                rate = panel.feature(day, symbol, "carry_rate")
                if day > cut:
                    rate = -50.0 * rate
                rows.append({"date": day, "symbol": symbol, **bar, "carry_rate": rate})
            shocked = PricePanel(rows)
            for day in truncated.dates:
                self.assertEqual(weights_for(shocked, spec, day), full[day], (cut, day))

    def test_research_weights_equal_desk_weights(self):
        panel = _random_panel(seed=11, n=80)
        spec = _spec(UNIVERSE + ["DY.Z", "HL.Z"], entry=0.8, exit_=0.4, lookback=3)
        # The Desk executes the registered spec document, not the object.
        desk_spec = StrategyDefinition(strategy_id="S", version=1, lane="l",
                                       spec=spec.to_dict(), hypothesis={}, evidence={},
                                       dataset_id=PERP_DYDX_DATASET,
                                       dataset_fingerprint=None).to_spec()
        self.assertEqual(desk_spec, spec)
        window = Window("VALIDATION", panel.dates[40], panel.dates[70])
        visible = panel.restrict(end=window.end)
        rows = walk_forward(visible, spec, window, 4.0)
        self.assertTrue(any(row["positions"] for row in rows))
        for row in rows:
            # holding_days=1 and a 0.02 band below one pair's 0.1 drift: research
            # holds exactly the target the Desk computes on its full panel.
            self.assertEqual(_nonzero(row["weights"]),
                             _nonzero(weights_for(panel, desk_spec, row["signal_date"])),
                             row["signal_date"])


class FundingFamilyTests(unittest.TestCase):
    def test_hl_vs_by_spec_serialises_and_labels_exactly_as_before(self):
        universe = ["BY.BTC", "BY.X", "HL.BTC", "HL.X"]
        spec = StrategySpec(family="funding_spread", universe=universe, lookback_days=3,
                            direction=1, min_abs_score=0.2, max_weight=0.05,
                            gross_exposure=1.0, holding_days=1, no_trade_band=0.02,
                            dataset_id="perp_funding_pairs_daily", calendar_symbol="HL.BTC")
        self.assertNotIn("exit_abs_score", spec.to_dict())
        self.assertEqual(spec.label, "funding_spread_l3_z0.2_w0.05_g1_b0.02")
        self.assertEqual(funding_venues(universe), ("HL", "BY"))
        self.assertEqual(funding_venues(["DY.X", "HL.X"]), ("HL", "DY"))
        with self.assertRaises(ValueError):
            funding_venues(["BY.X", "DY.X", "HL.X"])
        grid = lane_definitions(universe, "perp_funding_pairs_daily")["perp_funding_spread"]["grid"]
        self.assertTrue(all(item.exit_abs_score == 0.0 for item in grid))

    def test_hl_vs_by_weights_match_the_original_stateless_rule(self):
        rng = random.Random(3)
        n, coins = 30, ("BTC", "A", "B", "C")
        carry = {f"{venue}.{coin}": [rng.gauss(0.0, 0.003) for _ in range(n)]
                 for venue in ("HL", "BY") for coin in coins}
        panel = _panel(_days(n), carry)
        universe = sorted(carry)
        spec = StrategySpec(family="funding_spread", universe=universe, lookback_days=3,
                            direction=1, min_abs_score=0.5, max_weight=0.05,
                            gross_exposure=0.1, holding_days=1, no_trade_band=0.02,
                            dataset_id="perp_funding_pairs_daily", calendar_symbol="HL.BTC")
        for position, day in enumerate(panel.dates):
            # the pre-generalisation rule, restated: trailing 3-day mean, best pair only
            if position < 2:
                continue
            best = None
            for coin in coins:
                spread = sum(carry[f"HL.{coin}"][position - k] - carry[f"BY.{coin}"][position - k]
                             for k in range(3)) / 3 * DAYS_PER_YEAR
                if abs(spread) >= 0.5 and (best is None or abs(spread) > abs(best[1])):
                    best = (coin, spread)
            weights = weights_for(panel, spec, day)
            if best is None:
                self.assertFalse(_nonzero(weights))
                continue
            side = 1.0 if best[1] > 0 else -1.0
            self.assertEqual(weights, {f"HL.{best[0]}": -side * 0.05,
                                       f"BY.{best[0]}": side * 0.05})

    def test_short_leg_on_the_venue_whose_longs_pay_receives_funding(self):
        n = 8
        panel = _panel(_days(n), {"HL.BTC": [0.0] * n, "DY.BTC": [0.0] * n,
                                  "HL.X": [0.002] * n, "DY.X": [0.0005] * n})
        spec = _spec(["DY.BTC", "DY.X", "HL.BTC", "HL.X"], entry=0.25, exit_=0.125)
        weights = weights_for(panel, spec, panel.dates[3])
        self.assertEqual(weights, {"HL.X": -0.05, "DY.X": 0.05})
        rows = walk_forward(panel, spec, Window("ALL", panel.dates[0], panel.dates[-1]), 0.0)
        # flat prices: the pair earns exactly the funding difference on its notional
        for row in rows:
            self.assertAlmostEqual(row["gross_return"], 0.05 * (0.002 - 0.0005), places=12)

    def test_legs_pair_only_the_same_coin_across_the_two_venues(self):
        n = 6
        panel = _panel(_days(n), {"HL.BTC": [0.0] * n, "DY.BTC": [0.0] * n,
                                  "HL.X": [0.01] * n, "DY.X": [0.0] * n,
                                  "DY.Y": [0.02] * n, "HL.Z": [0.03] * n})
        spec = _spec(["DY.BTC", "DY.X", "DY.Y", "HL.BTC", "HL.X", "HL.Z"])
        weights = weights_for(panel, spec, panel.dates[-1])
        self.assertEqual(weights, {"HL.X": -0.05, "DY.X": 0.05})

    def test_lane_declares_the_pre_registered_grid(self):
        definition = lane_definitions(UNIVERSE, PERP_DYDX_DATASET)["perp_funding_spread_hl_dydx"]
        grid = {(spec.min_abs_score, spec.lookback_days, spec.exit_abs_score)
                for spec in definition["grid"]}
        self.assertEqual(grid, {(entry, lookback, entry / 2)
                                for entry in (0.25, 0.5, 1.0) for lookback in (1, 3)})
        self.assertEqual(len(definition["grid"]), 6)
        self.assertEqual(definition["prior_trials"], 50)  # burned: 3ujgeu 44 prior + 6 run
        self.assertEqual(definition["pristine_after"], "2026-09-27")  # first commit of the lane (invariant 6)
        self.assertEqual(definition["cost_bps"], 4.0)
        self.assertEqual(definition["benchmark"], "HL.BTC")
        self.assertTrue(all(spec.max_weight == 0.05 and spec.gross_exposure == 1.0
                            for spec in definition["grid"]))
        self.assertTrue(definition["compliance"]["cross_venue_hedge"])


class DatasetBuilderTests(unittest.TestCase):
    HOUR = 3_600_000

    def _prints(self, day: str, hours: range, rate: float = 0.0001) -> list[tuple[int, float]]:
        builder = _builder()
        base = builder.iso_ms(day + "T00:00:00Z")
        return [(base + hour * self.HOUR + 250, rate) for hour in hours]   # +250ms latency

    def test_incomplete_funding_day_is_excluded_and_nothing_is_filled(self):
        builder = _builder()
        # 2025-01-02 settlements 01:00..24:00 complete; 2025-01-03 only 21 of them
        prints = self._prints("2025-01-02", range(1, 25)) + self._prints("2025-01-03",
                                                                         range(1, 22))
        carry = builder.daily_carry(prints)
        self.assertEqual(set(carry), {"2025-01-02"})
        self.assertAlmostEqual(carry["2025-01-02"], 24 * 0.0001)
        # 22 prints is the declared minimum; a duplicated hour is counted once
        prints = self._prints("2025-01-03", range(1, 23))
        self.assertIn("2025-01-03", builder.daily_carry(prints))
        duplicated = self._prints("2025-01-03", range(1, 22)) + self._prints("2025-01-03",
                                                                             range(21, 22))
        self.assertNotIn("2025-01-03", builder.daily_carry(duplicated))

    def test_midnight_settlement_belongs_to_the_previous_day(self):
        builder = _builder()
        self.assertEqual(builder.settlement_day(builder.iso_ms("2025-01-03T00:00:00.400Z"))[0],
                         "2025-01-02")
        self.assertEqual(builder.settlement_day(builder.iso_ms("2025-01-03T01:00:00.100Z"))[0],
                         "2025-01-03")

    def test_coin_pairing_includes_delisted_and_k_contracts(self):
        builder = _builder()

        class FakeFetcher:           # INVENTED venue listings
            def get(self, url, body=None):
                if body is not None:
                    return {"universe": [{"name": "BTC"}, {"name": "kPEPE"},
                                         {"name": "OLD", "isDelisted": True},
                                         {"name": "HLONLY"}]}
                return {"markets": {"BTC-USD": {"status": "ACTIVE"},
                                    "PEPE-USD": {"status": "ACTIVE"},
                                    "OLD-USD": {"status": "FINAL_SETTLEMENT"},
                                    "DYONLY-USD": {"status": "ACTIVE"}}}

        self.assertEqual(builder.coin_pairs(FakeFetcher()),
                         [("BTC", "BTC", "BTC-USD", 1.0), ("OLD", "OLD", "OLD-USD", 1.0),
                          ("PEPE", "kPEPE", "PEPE-USD", 1000.0)])

    def test_pair_rows_align_days_and_rescale_both_legs(self):
        builder = _builder()
        days = _days(61)
        hl_bars = {day: (0.02, 5e6) for day in days}          # kPEPE-style, per 1000
        dy_bars = {day: (0.00002, 1e5) for day in days[1:]}   # one dYdX day missing
        carry = {day: 0.0001 for day in days}
        out = builder._pair_rows("PEPE", "kPEPE", "PEPE-USD", 1000.0, carry, dy_bars, carry,
                                 hl_bars, lambda line: None, "")
        rows, info = out
        self.assertEqual(info["days"], 60)
        self.assertEqual(info["price_scale_tokens"], 1e5)
        by_symbol = {(row["symbol"], row["date"]): row["close"] for row in rows}
        self.assertNotIn(("HL.PEPE", days[0]), by_symbol)
        self.assertAlmostEqual(by_symbol[("HL.PEPE", days[5])], 2.0)
        self.assertAlmostEqual(by_symbol[("DY.PEPE", days[5])], 2.0)
        self.assertIsNone(builder._pair_rows("PEPE", "kPEPE", "PEPE-USD", 1000.0, carry,
                                             dict(list(dy_bars.items())[:59]), carry, hl_bars,
                                             lambda line: None, ""))


if __name__ == "__main__":
    unittest.main()
