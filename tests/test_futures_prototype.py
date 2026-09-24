"""Futures trend/carry prototype: data derivation, causality, falsification, isolation.

Synthetic inputs below are *test fixtures* shaped like the pysystemtrade files;
they are never registered as market data.
"""

from __future__ import annotations

import csv
import math
import tempfile
import unittest
from pathlib import Path

from quant.dataplane.futures import MAX_STALE_SESSIONS, build_futures_panel
from quant.dataplane.panel import PricePanel
from quant.desk.profiles import DEFAULT_PROFILE, FUTURES_PROFILE, profile_for
from quant.factory.evaluate import falsify, summarize, walk_forward
from quant.factory.lanes import (FUTURES_DATASET, FUTURES_PRIOR_LAB_TRIALS, baseline_spec,
                                 lane_definitions)
from quant.factory.signals import (BASELINE_FAMILY, TREND_FAMILY, StrategySpec,
                                   time_series_weights, weights_for)
from quant.paths import QuantPaths


def _weekdays(start_year: int, count: int) -> list[str]:
    import datetime as dt
    day, out = dt.date(start_year, 1, 1), []
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day.isoformat())
        day += dt.timedelta(days=1)
    return out


def _write_source(root: Path, series: dict[str, list[tuple[str, float, float, str, float, str]]],
                  spreads: dict[str, float] | None = None) -> Path:
    """series[symbol] = [(date, adjusted, price, price_contract, carry, carry_contract)]."""
    futures = root / "data" / "futures"
    for sub in ("adjusted_prices_csv", "multiple_prices_csv", "csvconfig"):
        (futures / sub).mkdir(parents=True, exist_ok=True)
    with (futures / "csvconfig" / "instrumentconfig.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Instrument", "Description", "Pointsize", "Currency", "AssetClass",
                         "PerBlock", "Percentage", "PerTrade", "Region"])
        for symbol in series:
            writer.writerow([symbol, symbol, 1, "USD", "Test", 0, 0, 0, "US"])
    with (futures / "csvconfig" / "spreadcosts.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Instrument", "SpreadCost"])
        for symbol in series:
            writer.writerow([symbol, (spreads or {}).get(symbol, 0.0)])
    for symbol, rows in series.items():
        with (futures / "adjusted_prices_csv" / f"{symbol}.csv").open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["DATETIME", "price"])
            for date, adjusted, *_ in rows:
                writer.writerow([f"{date} 23:00:00", adjusted])
        with (futures / "multiple_prices_csv" / f"{symbol}.csv").open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["DATETIME", "CARRY", "CARRY_CONTRACT", "PRICE", "PRICE_CONTRACT",
                             "FORWARD", "FORWARD_CONTRACT"])
            for date, _, price, contract, carry, carry_contract in rows:
                writer.writerow([f"{date} 23:00:00", carry, carry_contract, price, contract,
                                 "", carry_contract])
    return root


def _synthetic_panel(symbols: list[str], sessions: int = 700, seed: int = 3) -> PricePanel:
    import random
    rng = random.Random(seed)
    rows = []
    for index, symbol in enumerate(symbols):
        level = 100.0
        drift = (index - len(symbols) / 2) * 0.0002
        for date in _weekdays(2010, sessions):
            level *= 1.0 + drift + rng.gauss(0, 0.01)
            rows.append({"date": date, "symbol": symbol, "open": level, "high": level,
                         "low": level, "close": level, "adj_close": level, "volume": 0,
                         "carry_ann": 0.02 * (1 if index % 2 else -1)})
    return PricePanel(rows)


def _ts_spec(universe: list[str], trend: float = 0.5, carry: float = 0.5,
             family: str = TREND_FAMILY) -> StrategySpec:
    return StrategySpec(family=family, universe=universe, lookback_days=256, direction=1,
                        min_abs_score=0.0, max_weight=1.0, holding_days=5, no_trade_band=0.1,
                        vol_target=0.15, trend_weight=trend, carry_weight=carry,
                        diversification_multiplier=2.0)


class PanelFeatureTests(unittest.TestCase):
    def test_gzip_roundtrip_is_byte_deterministic_and_keeps_features(self):
        panel = _synthetic_panel(["A", "B"], sessions=20)
        with tempfile.TemporaryDirectory() as tmp:
            first, second = Path(tmp) / "a.csv.gz", Path(tmp) / "b.csv.gz"
            panel.write(first)
            PricePanel.load(first).write(second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            loaded = PricePanel.load(second)
        date = panel.dates[5]
        self.assertAlmostEqual(loaded.feature(date, "B", "carry_ann"), 0.02)
        self.assertIsNone(loaded.feature(date, "B", "not_a_feature"))

    def test_restrict_carries_features_and_hides_the_future(self):
        panel = _synthetic_panel(["A"], sessions=30)
        cut = panel.dates[10]
        visible = panel.restrict(end=cut)
        self.assertEqual(visible.feature(cut, "A", "carry_ann"), -0.02)
        self.assertIsNone(visible.feature(panel.dates[11], "A", "carry_ann"))

    def test_plain_csv_bytes_are_unchanged_for_price_only_panels(self):
        rows = [{"date": "2020-01-02", "symbol": "X", "open": 1, "high": 1, "low": 1,
                 "close": 1, "adj_close": 1, "volume": 5}]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.csv"
            PricePanel(rows).write(path)
            self.assertEqual(path.read_bytes(),
                             b"date,symbol,open,high,low,close,adj_close,volume\r\n"
                             b"2020-01-02,X,1.000000,1.000000,1.000000,1.000000,1.000000,5\r\n")


class FuturesDerivationTests(unittest.TestCase):
    def test_roll_cost_carry_sign_and_stale_limit(self):
        dates = _weekdays(2020, 20)
        rows = []
        for index, date in enumerate(dates):
            contract = "20200300" if index < 10 else "20200600"
            # backwardation: the later contract is cheaper, so carry is positive
            rows.append((date, 100.0 + index, 100.0 + index, contract, 99.0 + index,
                         "20200600" if index < 10 else "20200900"))
        other = [(date, 50.0, 50.0, "20200300", "", "") for date in dates]
        # a market that stops reporting: carried forward at most MAX_STALE_SESSIONS
        gappy = [(date, 10.0, 10.0, "20200300", "", "") for date in dates[:5]]
        with tempfile.TemporaryDirectory() as tmp:
            source = _write_source(Path(tmp), {"A": rows, "B": other, "C": gappy},
                                   spreads={"A": 0.5})
            panel, provenance = build_futures_panel(source, ["A", "B", "C"], start="2000-01-01")
        a = [panel.price(date, "A") for date in dates]
        # ordinary day: +1 point on a 100-point contract
        self.assertAlmostEqual(a[1] / a[0] - 1.0, 1.0 / 100.0, places=9)
        # roll day: the same +1 point, minus two half-spreads of 0.5 on the old price
        roll_return = a[10] / a[9] - 1.0
        self.assertAlmostEqual(roll_return, 1.0 / 109.0 - 2 * 0.5 / 109.0, places=9)
        self.assertEqual(panel.feature(dates[10], "A", "roll"), 1.0)
        carry = panel.feature(dates[0], "A", "carry_ann")
        self.assertGreater(carry, 0.0)
        self.assertAlmostEqual(carry, (100.0 - 99.0) / 100.0 / 0.25, places=6)
        self.assertIsNone(panel.feature(dates[0], "B", "carry_ann"))
        stale = [date for date in dates if panel.has(date, "C")]
        self.assertEqual(len(stale), 5 + MAX_STALE_SESSIONS)
        self.assertEqual(panel.feature(stale[-1], "C", "stale"), 1.0)
        self.assertEqual(panel.price(stale[-1], "C"), panel.price(dates[4], "C"))
        self.assertIn("volume is unavailable and written as 0: execution capacity is NOT "
                      "modelled", provenance["caveats"])


class TimeSeriesSignalTests(unittest.TestCase):
    def setUp(self):
        self.universe = ["A", "B", "C", "D"]
        self.panel = _synthetic_panel(self.universe)

    def test_no_look_ahead_truncation_gives_identical_weights(self):
        spec = _ts_spec(self.universe)
        for date in self.panel.dates[300::97]:
            full = weights_for(self.panel, spec, date)
            truncated = weights_for(self.panel.restrict(end=date), spec, date)
            self.assertTrue(full)
            self.assertEqual(full.keys(), truncated.keys())
            for symbol in full:
                self.assertAlmostEqual(full[symbol], truncated[symbol], places=12)

    def test_future_shock_cannot_change_a_past_decision(self):
        spec = _ts_spec(self.universe)
        date = self.panel.dates[400]
        before = weights_for(self.panel, spec, date)
        rows = [{"date": d, "symbol": s, **bar, **self.panel.features.get((d, s), {})}
                for (d, s), bar in self.panel.bars.items()]
        for row in rows:
            if row["date"] > date:
                for field in ("open", "high", "low", "close", "adj_close"):
                    row[field] *= 3.0
        self.assertEqual(before, weights_for(PricePanel(rows), spec, date))

    def test_warmup_sizing_and_caps(self):
        spec = _ts_spec(self.universe)
        self.assertEqual(weights_for(self.panel, spec, self.panel.dates[100]), {})
        date = self.panel.dates[-1]
        weights = time_series_weights(self.panel, spec, date)
        self.assertTrue(all(abs(value) <= spec.max_weight for value in weights.values()))
        # dividing by the declared universe, not by today's survivors
        thin = _ts_spec(self.universe + ["NEVER_TRADED"])
        thin_weights = time_series_weights(self.panel, thin, date)
        for symbol, value in weights.items():
            self.assertAlmostEqual(thin_weights[symbol], value * 4 / 5, places=12)

    def test_baseline_is_long_only(self):
        spec = _ts_spec(self.universe, family=BASELINE_FAMILY)
        weights = weights_for(self.panel, spec, self.panel.dates[-1])
        self.assertEqual(set(weights), set(self.universe))
        self.assertTrue(all(value > 0 for value in weights.values()))


class FalsificationTests(unittest.TestCase):
    def test_time_series_families_must_supply_a_baseline(self):
        universe = ["A", "B", "C", "D"]
        panel = _synthetic_panel(universe)
        from quant.dataplane.panel import Window
        window = Window("V", panel.dates[300], panel.dates[-1])
        spec = _ts_spec(universe)
        rows = walk_forward(panel, spec, window, 4.0)
        summary = summarize(rows, panel, "A", 4.0)
        with self.assertRaises(ValueError):
            falsify(rows, summary, panel, "A", spec, trials=3)
        verdict = falsify(rows, summary, panel, "A", spec, trials=3,
                          baseline_rows=walk_forward(panel, baseline_spec(spec), window, 4.0))
        self.assertIn("sharpe_exceeds_long_only_risk_parity", verdict["tests"])
        self.assertIn("equity_beta_below_0_5", verdict["tests"])
        self.assertNotIn("market_beta_below_0_15", verdict["tests"])

    def test_lane_is_pre_registered_and_charges_lab_trials(self):
        lanes = lane_definitions(["A"], FUTURES_DATASET)
        (lane,) = lanes.values()
        self.assertEqual(len(lane["grid"]), 3)
        self.assertEqual(lane["prior_trials"], FUTURES_PRIOR_LAB_TRIALS)
        self.assertNotIn("xs_daily_relative_value", lanes)


class ProfileAndIsolationTests(unittest.TestCase):
    def test_profiles(self):
        self.assertIs(profile_for(FUTURES_DATASET), FUTURES_PROFILE)
        self.assertIs(profile_for("us_sector_etf_daily"), DEFAULT_PROFILE)
        limits = FUTURES_PROFILE.limits
        self.assertEqual(limits.drawdown_halt, DEFAULT_PROFILE.limits.drawdown_halt)
        self.assertEqual(limits.min_nav_ratio, DEFAULT_PROFILE.limits.min_nav_ratio)
        self.assertGreater(limits.max_net_ratio, 1.0)
        self.assertLessEqual(FUTURES_PROFILE.execution.commission_bps
                             + FUTURES_PROFILE.execution.half_spread_bps,
                             lane_definitions(["A"], FUTURES_DATASET)[
                                 "ts_trend_carry_futures"]["cost_bps"])

    def test_state_directories_are_isolated(self):
        with tempfile.TemporaryDirectory() as tmp:
            etf = QuantPaths(Path(tmp)).ensure()
            futures = QuantPaths(Path(tmp), state="var/futures").ensure()
            self.assertNotEqual(etf.book, futures.book)
            self.assertEqual(etf.datasets, futures.datasets)
            self.assertTrue(str(futures.book).startswith(str(Path(tmp) / "var" / "futures")))


if __name__ == "__main__":
    unittest.main()
