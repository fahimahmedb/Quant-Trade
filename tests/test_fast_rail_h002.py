"""Fast rail H-002: HL vs dYdX funding spread with a hysteresis exit."""

from __future__ import annotations

import importlib.util
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.dataplane.panel import PricePanel, Window  # noqa: E402
from quant.factory.evaluate import walk_forward  # noqa: E402
from quant.factory.lanes import (PERP_HL_DYDX_DATASET, lane_definitions,  # noqa: E402
                                 perp_lane_definitions)
from quant.factory.signals import (DAYS_PER_YEAR, FUNDING_SPREAD_HOLD,  # noqa: E402
                                   StrategySpec, _trailing_carry, funding_venues,
                                   weights_for)


def _builder():
    spec = importlib.util.spec_from_file_location(
        "build_hl_dydx", ROOT / "scripts" / "build_hl_dydx_funding_dataset.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _legacy_weights(panel: PricePanel, spec: StrategySpec, asof: str) -> dict[str, float]:
    """Verbatim copy of funding_spread_weights before H-002 (venues hard-coded)."""
    first, second = ("HL", "BY")
    coins = sorted({s.split(".", 1)[1] for s in spec.universe if s.startswith(first + ".")}
                   & {s.split(".", 1)[1] for s in spec.universe if s.startswith(second + ".")})
    candidates = []
    for coin in coins:
        a, b = f"{first}.{coin}", f"{second}.{coin}"
        if not (panel.has(asof, a) and panel.has(asof, b)):
            continue
        if panel.feature(asof, a, "price_proxy") or panel.feature(asof, b, "price_proxy"):
            continue
        carry_a = _trailing_carry(panel, a, asof, spec.lookback_days or 3)
        carry_b = _trailing_carry(panel, b, asof, spec.lookback_days or 3)
        if carry_a is None or carry_b is None:
            continue
        spread = (carry_a - carry_b) * DAYS_PER_YEAR
        if abs(spread) >= spec.min_abs_score:
            candidates.append((abs(spread), coin, a, b, spread))
    candidates.sort(reverse=True)
    limit = max(1, int(round(spec.gross_exposure / (2 * spec.max_weight)))) if spec.max_weight else 0
    weights: dict[str, float] = {}
    for _, coin, a, b, spread in candidates[:limit]:
        side = 1.0 if spread > 0 else -1.0
        weights[a] = -side * spec.max_weight
        weights[b] = side * spec.max_weight
    if not weights:
        present = next((s for s in spec.universe if panel.has(asof, s)), None)
        return {present: 0.0} if present else {}
    return weights


def _day(index: int) -> str:
    return f"2024-{1 + index // 28:02d}-{1 + index % 28:02d}"


def _panel(venues: tuple[str, str], coins: list[str], days: int, carry,
           proxy=lambda venue, coin, i: False, missing=lambda venue, coin, i: False
           ) -> PricePanel:
    rows = []
    for i in range(days):
        for coin in coins + ["BTC"]:
            for venue in venues:
                if missing(venue, coin, i):
                    continue
                row = {"date": _day(i), "symbol": f"{venue}.{coin}", "open": 100.0,
                       "high": 100.0, "low": 100.0, "close": 100.0, "adj_close": 100.0,
                       "volume": 1e7, "carry_rate": carry(venue, coin, i)}
                if proxy(venue, coin, i):
                    row["price_proxy"] = 1.0
                rows.append(row)
    return PricePanel(rows)


def _wiggle(venue: str, coin: str, i: int) -> float:
    """Deterministic, sign-changing funding with spreads straddling thresholds."""
    base = 0.004 if venue == "HL" else 0.0008
    return base * math.sin(i / (3.0 + len(coin)) + (0.7 if venue != "HL" else 0.0))


def _hold_spec(universe, threshold=0.5, lookback=3, max_weight=0.05):
    return StrategySpec(family=FUNDING_SPREAD_HOLD, universe=universe, lookback_days=lookback,
                        direction=1, min_abs_score=threshold, max_weight=max_weight,
                        gross_exposure=1.0, holding_days=1, no_trade_band=0.02,
                        dataset_id=PERP_HL_DYDX_DATASET, calendar_symbol="HL.BTC")


class VenueMappingTest(unittest.TestCase):
    def test_venues_read_from_universe(self):
        self.assertEqual(funding_venues(["HL.BTC", "DX.BTC", "HL.ETH"]), ("DX", "HL"))
        self.assertEqual(funding_venues(["BY.BTC", "HL.BTC"]), ("BY", "HL"))
        with self.assertRaises(ValueError):
            funding_venues(["HL.BTC", "DX.BTC", "BY.BTC"])

    def test_lane_is_the_preregistered_grid(self):
        universe = ["DX.BTC", "DX.ETH", "HL.BTC", "HL.ETH"]
        lane = lane_definitions(universe, PERP_HL_DYDX_DATASET)[
            "perp_funding_spread_hl_dydx_hold"]
        self.assertEqual(sorted((s.min_abs_score, s.lookback_days) for s in lane["grid"]),
                         sorted((e, l) for e in (0.25, 0.5, 1.0) for l in (3, 7)))
        self.assertTrue(all(s.family == FUNDING_SPREAD_HOLD for s in lane["grid"]))
        self.assertEqual((lane["prior_trials"], lane["cost_bps"], lane["benchmark"],
                          lane["pristine_after"]), (44, 6.0, "HL.BTC", "2026-09-25"))
        self.assertEqual(lane["compliance"], perp_lane_definitions(
            universe, "x")["perp_funding_spread"]["compliance"])

    def test_dx_symbols_trade_against_hl_symbols(self):
        panel = _panel(("HL", "DX"), ["ETH"], 10,
                       lambda v, c, i: 0.005 if (v, c) == ("HL", "ETH") else 0.0)
        weights = weights_for(panel, _hold_spec(panel.symbols), _day(5))
        self.assertEqual(weights, {"HL.ETH": -0.05, "DX.ETH": 0.05})


class FundingSignTest(unittest.TestCase):
    def _collect(self, hl: float, dx: float) -> tuple[dict, float]:
        panel = _panel(("HL", "DX"), ["ETH"], 20,
                       lambda v, c, i: (hl if v == "HL" else dx) if c == "ETH" else 0.0)
        spec = _hold_spec(panel.symbols)
        rows = walk_forward(panel, spec, Window("W", _day(5), _day(19)), 0.0)
        held = [row for row in rows if row["weights"].get("HL.ETH")]
        return held[-1]["weights"], held[-1]["gross_return"]

    def test_short_the_venue_charging_longs_more_collects_the_spread(self):
        for hl, dx in ((0.006, 0.001), (-0.002, 0.004), (0.001, 0.007)):
            weights, gross = self._collect(hl, dx)
            if hl > dx:
                self.assertLess(weights["HL.ETH"], 0)
                self.assertGreater(weights["DX.ETH"], 0)
            else:
                self.assertGreater(weights["HL.ETH"], 0)
                self.assertLess(weights["DX.ETH"], 0)
            # flat prices: the session's gross is exactly w * |carry difference|
            self.assertAlmostEqual(gross, 0.05 * abs(hl - dx), places=12)


class HysteresisTest(unittest.TestCase):
    def test_enter_at_threshold_hold_to_half_then_exit(self):
        # DX pays 0; HL annualised spread path (lookback 1): below, above E,
        # between E/2 and E (held), below E/2 (exit), between (stays flat).
        path = [0.2, 0.6, 0.4, 0.3, 0.2, 0.4, 0.6, -0.4, -0.6, -0.3, -0.2]
        panel = _panel(("HL", "DX"), ["ETH"], len(path),
                       lambda v, c, i: path[i] / DAYS_PER_YEAR
                       if (v, c) == ("HL", "ETH") else 0.0)
        spec = _hold_spec(panel.symbols, threshold=0.5, lookback=1)
        held = [weights_for(panel, spec, _day(i)).get("HL.ETH", 0.0) for i in range(len(path))]
        self.assertEqual(held, [0.0, -0.05, -0.05, -0.05, 0.0, 0.0, -0.05, 0.0, 0.05, 0.05, 0.0])

    def test_state_is_causal_under_truncation(self):
        panel = _panel(("HL", "DX"), ["ETH", "SOL", "XRP"], 120, _wiggle,
                       missing=lambda v, c, i: (c, v, i) in {("SOL", "DX", 40), ("XRP", "HL", 77)})
        for threshold, lookback in ((0.25, 3), (0.5, 7), (1.0, 3)):
            spec = _hold_spec(panel.symbols, threshold, lookback, max_weight=0.25)
            flips = 0
            previous = None
            for i in range(0, 120):
                day = _day(i)
                full = weights_for(panel, spec, day)
                cut = weights_for(panel.restrict(end=day), spec, day)
                self.assertEqual(full, cut, (threshold, lookback, day))
                flips += full != previous
                previous = full
            self.assertGreater(flips, 3)     # the fixture actually exercises entries/exits

    def test_missing_leg_resets_the_hold(self):
        path = [0.6, 0.4, 0.4, 0.4]
        panel = _panel(("HL", "DX"), ["ETH"], 4,
                       lambda v, c, i: path[i] / DAYS_PER_YEAR
                       if (v, c) == ("HL", "ETH") else 0.0,
                       missing=lambda v, c, i: (v, c, i) == ("DX", "ETH", 2))
        spec = _hold_spec(panel.symbols, threshold=0.5, lookback=1)
        held = [weights_for(panel, spec, _day(i)).get("HL.ETH", 0.0) for i in range(4)]
        self.assertEqual(held, [-0.05, -0.05, 0.0, 0.0])


class LegacyUnchangedTest(unittest.TestCase):
    def test_hl_vs_bybit_weights_identical_on_synthetic_panel(self):
        panel = _panel(("HL", "BY"), ["ETH", "SOL", "XRP", "DOGE"], 90, _wiggle,
                       proxy=lambda v, c, i: c == "XRP" and v == "BY" and i % 5 == 0,
                       missing=lambda v, c, i: c == "DOGE" and i in (30, 31))
        for threshold in (0.2, 0.5):
            spec = perp_lane_definitions(panel.symbols, "perp_funding_pairs_daily")[
                "perp_funding_spread"]["grid"][0]
            spec = StrategySpec(**{**spec.to_dict(), "min_abs_score": threshold,
                                   "max_weight": 0.25})
            for i in range(90):
                self.assertEqual(weights_for(panel, spec, _day(i)),
                                 _legacy_weights(panel, spec, _day(i)))

    def test_hl_vs_bybit_weights_identical_on_committed_dataset(self):
        path = ROOT / "data" / "datasets" / "perp_funding_pairs_daily.csv.gz"
        if not path.exists():
            self.skipTest("committed perp dataset absent")
        panel = PricePanel.load(path)
        for spec in perp_lane_definitions(panel.symbols, "perp_funding_pairs_daily")[
                "perp_funding_spread"]["grid"]:
            for day in panel.dates[20::37]:
                self.assertEqual(weights_for(panel, spec, day),
                                 _legacy_weights(panel, spec, day))

    def test_legacy_label_unchanged(self):
        spec = perp_lane_definitions(["HL.BTC", "BY.BTC"], "p")["perp_funding_spread"]["grid"][0]
        self.assertEqual(spec.label, "funding_spread_l3_z0.2_w0.05_g1_b0.02")


class BuilderTest(unittest.TestCase):
    def setUp(self):
        self.builder = _builder()

    def test_incomplete_funding_day_is_dropped(self):
        prints = {"2024-01-01": {f"{h:02d}": 0.00001 for h in range(24)},
                  "2024-01-02": {f"{h:02d}": 0.00001 for h in range(21)},
                  "2024-01-03": {f"{h:02d}": 0.00001 for h in range(22)}}
        carry = self.builder._complete(prints)
        self.assertEqual(sorted(carry), ["2024-01-01", "2024-01-03"])
        self.assertAlmostEqual(carry["2024-01-01"], 0.00024)

    def test_raw_parsing_venue_mapping_and_day_bucketing(self):
        import datetime as dt
        days = 64
        start = dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc)
        ms = int(start.timestamp() * 1000)
        # HL misses two hourly prints on day 10 (22 prints kept) and three on
        # day 20 (21 prints: dropped); dYdX is complete except day 30 (dropped).
        hl_hours = [h for h in range(days * 24)
                    if h not in (10 * 24 + 3, 10 * 24 + 4, 20 * 24, 20 * 24 + 1, 20 * 24 + 2)]
        hl_funding = [[{"coin": "ETH", "fundingRate": "0.00001", "premium": "0",
                        "time": ms + h * 3_600_000 + 50} for h in hl_hours]]
        dx_funding = [{"historicalFunding": [
            {"ticker": "ETH-USD", "rate": "-0.00002", "price": "1",
             "effectiveAt": (start + dt.timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%S.100Z")}
            for h in range(days * 24) if not (30 * 24 <= h < 30 * 24 + 5)]}]
        hl_candles = [[{"t": ms + d * 86_400_000, "c": "2000", "v": "10"} for d in range(days)]]
        dx_candles = [{"candles": [{"startedAt": (start + dt.timedelta(days=d)).strftime(
            "%Y-%m-%dT00:00:00.000Z"), "close": "2001", "usdVolume": "5000"}
            for d in range(days)]}]
        raw = {"hl_funding_ETH.json.gz": hl_funding, "dx_funding_ETH.json.gz": dx_funding,
               "hl_candles_ETH.json.gz": hl_candles, "dx_candles_ETH.json.gz": dx_candles}
        self.builder.load_pages = lambda name: raw[name]
        rows, symbols = self.builder.build_rows(["ETH"])
        self.assertEqual(symbols, ["HL.ETH", "DX.ETH"])
        dates = sorted({row["date"] for row in rows})
        self.assertEqual(len(dates), days - 2)
        for dropped in (20, 30):
            self.assertNotIn((start + dt.timedelta(days=dropped)).date().isoformat(), dates)
        by_key = {(row["date"], row["symbol"]): row for row in rows}
        day10 = (start + dt.timedelta(days=10)).date().isoformat()
        self.assertAlmostEqual(by_key[(day10, "HL.ETH")]["carry_rate"], 22 * 0.00001)
        self.assertAlmostEqual(by_key[("2024-01-01", "DX.ETH")]["carry_rate"], -24 * 0.00002)
        self.assertEqual(by_key[("2024-01-01", "HL.ETH")]["volume"], 20000.0)
        self.assertEqual(by_key[("2024-01-01", "DX.ETH")]["close"], 2001.0)
        self.assertEqual(by_key[("2024-01-01", "DX.ETH")]["open"], 2001.0)


if __name__ == "__main__":
    unittest.main()
