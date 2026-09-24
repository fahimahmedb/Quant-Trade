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
from quant.factory.lanes import (FUTURES_BROAD_DATASET, FUTURES_BROAD_PRIOR_TRIALS,
                                 FUTURES_DATASET, FUTURES_PRIOR_TRIALS, FUTURES_PRISTINE_AFTER,
                                 baseline_spec, lane_definitions)
from quant.factory.signals import (BASELINE_FAMILY, TREND_FAMILY, StrategySpec,
                                   time_series_weights, weights_for)
from quant.paths import QuantPaths


def _weekdays(start_year: int, count: int) -> list[str]:  # noqa: D401
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
            panel, provenance = build_futures_panel(source, ["A", "B", "C"], start="2000-01-01",
                                                    cost_feature=True)
        a = [panel.price(date, "A") for date in dates]
        # ordinary day: +1 point on a 100-point contract
        self.assertAlmostEqual(a[1] / a[0] - 1.0, 1.0 / 100.0, places=9)
        # roll day: the index carries the market move only; the roll cost (two
        # half-spreads of 0.5 on the old price) is a separate feature, so a short
        # position can never be credited with it
        self.assertAlmostEqual(a[10] / a[9] - 1.0, 1.0 / 109.0, places=9)
        self.assertAlmostEqual(panel.feature(dates[10], "A", "roll_cost"), 2 * 0.5 / 109.0)
        self.assertIsNone(panel.feature(dates[9], "A", "roll_cost"))
        self.assertAlmostEqual(panel.feature(dates[0], "A", "cost_bps"),
                               0.5 / 100.0 * 10_000.0)
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


class RollCostTests(unittest.TestCase):
    def test_roll_on_a_non_session_day_is_charged_on_the_next_session(self):
        import datetime as dt
        days, day = [], dt.date(2021, 1, 4)          # a Monday
        while len(days) < 12:
            days.append(day.isoformat())
            day += dt.timedelta(days=1)             # includes a Saturday and Sunday
        rows = [(d, 100.0, 100.0, "20210300" if i < 5 else "20210600", "", "")
                for i, d in enumerate(days)]
        with tempfile.TemporaryDirectory() as tmp:
            source = _write_source(Path(tmp), {"A": rows}, spreads={"A": 0.5})
            panel, _ = build_futures_panel(source, ["A"], start="2000-01-01",
                                           calendar_symbol="A")
        self.assertNotIn(days[5], panel.dates)       # Saturday: no session
        self.assertNotIn(days[6], panel.dates)       # Sunday: no session
        self.assertAlmostEqual(panel.feature(days[7], "A", "roll_cost"), 2 * 0.5 / 100.0)

    def test_research_charges_roll_on_absolute_weight(self):
        rows = []
        dates = _weekdays(2015, 600)
        for i, d in enumerate(dates):
            for symbol, drift in (("L", 0.001), ("S", -0.001)):
                level = 100.0 * (1 + drift) ** i
                row = {"date": d, "symbol": symbol, "open": level, "high": level,
                       "low": level, "close": level, "adj_close": level, "volume": 0}
                if i % 20 == 0:
                    row["roll_cost"] = 0.01
                rows.append(row)
        panel = PricePanel(rows)
        from quant.dataplane.panel import Window
        spec = _ts_spec(["L", "S"], trend=1.0, carry=0.0)
        window = Window("W", dates[300], dates[-1])
        charged = walk_forward(panel, spec, window, 0.0)
        free = walk_forward(PricePanel([{k: v for k, v in r.items() if k != "roll_cost"}
                                        for r in rows]), spec, window, 0.0)
        extra = [a["cost"] - b["cost"] for a, b in zip(charged, free)]
        paid = [(row, e) for row, e in zip(charged, extra) if e > 0]
        self.assertTrue(paid)
        for row, e in paid:
            self.assertTrue(any(w < 0 for w in row["weights"].values()))
            self.assertAlmostEqual(e, sum(abs(w) for w in row["weights"].values()) * 0.01)


class BroadUniverseTests(unittest.TestCase):
    def test_scale_glitch_excludes_instrument_and_is_recorded(self):
        dates = _weekdays(2020, 30)
        good = [(d, 100.0 + i * 0.1, 100.0 + i * 0.1, "20200300", "", "")
                for i, d in enumerate(dates)]
        bad = [(d, 10.0 if i == 12 else 100.0, 10.0 if i == 12 else 100.0, "20200300", "", "")
               for i, d in enumerate(dates)]
        with tempfile.TemporaryDirectory() as tmp:
            source = _write_source(Path(tmp), {"GOOD": good, "BAD": bad})
            panel, provenance = build_futures_panel(source, ["GOOD", "BAD"],
                                                    start="2000-01-01")
        self.assertEqual(panel.symbols, ["GOOD"])
        self.assertEqual(provenance["excluded_for_data_quality"], {"BAD": [dates[12]]})
        self.assertEqual(provenance["universe"], ["GOOD"])

    def test_calendar_symbol_gives_staggered_entry(self):
        dates = _weekdays(2020, 30)
        anchor = [(d, 100.0, 100.0, "20200300", "", "") for d in dates]
        late = [(d, 50.0, 50.0, "20200300", "", "") for d in dates[20:]]
        with tempfile.TemporaryDirectory() as tmp:
            source = _write_source(Path(tmp), {"REF": anchor, "LATE": late})
            panel, _ = build_futures_panel(source, ["REF", "LATE"], start="2000-01-01",
                                           calendar_symbol="REF")
        self.assertEqual(panel.dates_for("REF"), dates)
        self.assertEqual(panel.dates_for("LATE"), dates[20:])

    def test_selection_rule_is_mechanical(self):
        dates = _weekdays(2019, 1400)  # runs past BROAD_LIVE_AFTER
        rows = [(d, 100.0, 100.0, "20200300", "", "") for d in dates]
        with tempfile.TemporaryDirectory() as tmp:
            source = _write_source(Path(tmp), {"GOLD": rows, "GOLD_micro": rows,
                                               "SHORT": rows[-100:]})
            from quant.dataplane.futures import select_broad_universe
            # fixture asset class is "Test": nothing qualifies until it is a declared class
            self.assertEqual(select_broad_universe(source, start="2000-01-01"), [])
            config = source / "data" / "futures" / "csvconfig" / "instrumentconfig.csv"
            config.write_text(config.read_text().replace(",Test,", ",Metals,"))
            self.assertEqual(select_broad_universe(source, start="2000-01-01"), ["GOLD"])

    def test_staggered_breadth_counts_only_eligible_instruments(self):
        universe = ["A", "B", "C", "D"]
        panel = _synthetic_panel(universe)
        aligned = _ts_spec(universe)
        staggered = StrategySpec(**{**aligned.to_dict(), "calendar_symbol": "A",
                                    "universe": universe + ["LISTED_LATER"]})
        date = panel.dates[-1]
        a, b = time_series_weights(panel, aligned, date), time_series_weights(panel, staggered, date)
        for symbol in a:
            self.assertAlmostEqual(a[symbol], b[symbol], places=12)

    def test_walk_forward_on_calendar_symbol_skips_unlisted(self):
        universe = ["A", "B"]
        panel = _synthetic_panel(universe, sessions=500)
        rows = [{"date": d, "symbol": s, **bar, **panel.features.get((d, s), {})}
                for (d, s), bar in panel.bars.items() if not (s == "B" and d < panel.dates[300])]
        staggered = PricePanel(rows)
        from quant.dataplane.panel import Window
        spec = StrategySpec(**{**_ts_spec(universe).to_dict(), "calendar_symbol": "A"})
        window = Window("W", staggered.dates[260], staggered.dates[-1])
        out = walk_forward(staggered, spec, window, 4.0)
        self.assertEqual(len(out), len([d for d in staggered.dates if window.contains(d)]) - 2)
        early = [row for row in out if row["signal_date"] < staggered.dates[300]]
        self.assertTrue(all("B" not in row["weights"] for row in early))


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
        self.assertEqual(lane["prior_trials"], FUTURES_PRIOR_TRIALS)
        self.assertEqual(lane["pristine_after"], FUTURES_PRISTINE_AFTER)
        self.assertNotIn("xs_daily_relative_value", lanes)
        broad = lane_definitions(["A"], FUTURES_BROAD_DATASET)
        # prior trials are a dataset fact: every lane declares the same number
        self.assertEqual({lane["prior_trials"] for lane in broad.values()},
                         {FUTURES_BROAD_PRIOR_TRIALS})

    def test_prior_trials_are_reserved_once_per_dataset(self):
        from quant.factory.strategies import StrategyRegistry
        with tempfile.TemporaryDirectory() as tmp:
            registry = StrategyRegistry(Path(tmp) / "s.json")
            for lane in ("a", "b"):
                registry.record_trials("ds@x", 17, experiment_key="ds@x:prior-trials")
                total = registry.record_trials("ds@x", 3, experiment_key=f"ds@x:{lane}")
            self.assertEqual(total, 17 + 3 + 3)


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



class SequentialTestTests(unittest.TestCase):
    def test_no_decision_before_minimum_and_deterministic(self):
        from quant.learning.sequential import MIN_OBSERVATIONS, sequential_test
        short = [0.01] * (MIN_OBSERVATIONS - 1)
        self.assertEqual(sequential_test(short, 1.0)["decision"], "CONTINUE")
        import random
        rng = random.Random(1)
        noise = [rng.gauss(0.002, 0.01) for _ in range(400)]
        self.assertEqual(sequential_test(noise, 1.0), sequential_test(list(noise), 1.0))

    def test_decisive_evidence_both_ways(self):
        from quant.learning.sequential import sequential_test
        import random
        rng = random.Random(5)
        good = [rng.gauss(0.004, 0.01) for _ in range(500)]     # ~6 annual Sharpe
        bad = [rng.gauss(-0.002, 0.01) for _ in range(500)]
        self.assertEqual(sequential_test(good, 1.0)["decision"], "ACCEPT_EDGE")
        self.assertEqual(sequential_test(bad, 1.0)["decision"], "REJECT_EDGE")

    def test_scale_invariance(self):
        from quant.learning.sequential import sequential_test
        import random
        rng = random.Random(9)
        values = [rng.gauss(0.001, 0.01) for _ in range(300)]
        a = sequential_test(values, 1.0)
        b = sequential_test([value * 7.5 for value in values], 1.0)
        self.assertAlmostEqual(a["log_likelihood_ratio"], b["log_likelihood_ratio"], places=9)


class SleeveAttributionTests(unittest.TestCase):
    def test_opposing_sleeves_on_one_symbol_sum_to_nav_change(self):
        from quant.book.ledger import Ledger
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "book.json", initial_capital=1_000.0)
            ledger.mark_to_market("2020-01-01", {"X": 100.0})
            ledger.apply_fill("X", 3.0, 100.0, 0.5, "2020-01-02", "LONG", "op-long")
            ledger.apply_fill("X", -1.0, 100.0, 0.25, "2020-01-02", "SHORT", "op-short")
            ledger.mark_to_market("2020-01-02", {"X": 110.0})
            pnl = ledger.sleeve_pnl()
            self.assertAlmostEqual(pnl["LONG"], 30.0 - 0.5)
            self.assertAlmostEqual(pnl["SHORT"], -10.0 - 0.25)
            nav_change = ledger.state.nav_history[-1]["nav"] - 1_000.0
            self.assertAlmostEqual(sum(pnl.values()), nav_change)
            # replaying the same operation is a no-op for sleeve P&L as well
            ledger.apply_fill("X", 3.0, 100.0, 0.5, "2020-01-02", "LONG", "op-long")
            self.assertEqual(ledger.sleeve_pnl(), pnl)
            reloaded = Ledger(Path(tmp) / "book.json")
            self.assertEqual(reloaded.sleeve_returns("LONG"),
                             [("2020-01-02", (30.0 - 0.5) / 1_000.0)])


class TimelineTests(unittest.TestCase):
    def test_jump_between_decision_and_first_fill_is_never_credited(self):
        """The forbidden interval (close t -> first executable price) dominates here."""
        universe = ["A", "B"]
        base = _synthetic_panel(universe, sessions=400)
        spec = _ts_spec(universe, trend=1.0, carry=0.0)
        signal_day = base.dates[350]
        weights = weights_for(base, spec, signal_day)
        self.assertTrue(weights)
        jump_day = base.dates[351]
        rows = []
        for (date, symbol), bar in base.bars.items():
            factor = 1.5 if date >= jump_day else 1.0     # +50% on the entry session
            rows.append({"date": date, "symbol": symbol,
                         **{k: (v * factor if k != "volume" else v) for k, v in bar.items()}})
        jumped = PricePanel(rows)
        from quant.dataplane.panel import Window
        window = Window("W", signal_day, base.dates[-1])
        first = walk_forward(jumped, spec, window, 0.0)[0]
        self.assertEqual(first["signal_date"], signal_day)
        self.assertEqual(first["entry_date"], jump_day)
        self.assertLess(abs(first["gross_return"]), 0.2)


class FinalStateRiskTests(unittest.TestCase):
    def test_futures_limits_bind_on_the_final_scaled_portfolio(self):
        from quant.book.ledger import Ledger
        from quant.desk.risk import evaluate
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "book.json", initial_capital=1_000_000.0)
            prices = {f"S{i}": 100.0 for i in range(12)}
            hedged = {f"S{i}": (500_000.0 if i % 2 else -500_000.0) for i in range(12)}
            verdict = evaluate(ledger, "STR", hedged, FUTURES_PROFILE.limits, prices)
            # all long: scaling for gross still leaves net above the directional cap
            one_way = evaluate(ledger, "STR", {k: abs(v) for k, v in hedged.items()},
                               FUTURES_PROFILE.limits, prices)
        self.assertTrue(verdict["approved"])
        self.assertLess(verdict["scale"], 1.0)
        self.assertAlmostEqual(verdict["gross_ratio"], FUTURES_PROFILE.limits.max_gross_ratio,
                               places=6)
        self.assertFalse(one_way["approved"])
        self.assertTrue(any("net exposure" in veto for veto in one_way["vetoes"]))


class FuturesInstanceRestartTests(unittest.TestCase):
    """Whole-instance replay on a synthetic fixture (never reported as evidence)."""

    UNIVERSE = ["A", "B", "C", "D"]

    def _root(self, tmp: Path) -> Path:
        from quant.dataplane.registry import DatasetRecord
        from quant.state import write_json
        panel = _synthetic_panel(self.UNIVERSE, sessions=1000, seed=11)
        path = tmp / "data" / "datasets" / f"{FUTURES_DATASET}.csv.gz"
        panel.write(path)
        record = DatasetRecord(dataset_id=FUTURES_DATASET, source="synthetic test fixture",
                               adapter="fixture", path=f"data/datasets/{FUTURES_DATASET}.csv.gz",
                               symbols=panel.symbols)
        write_json(path.with_suffix(".meta.json"),
                   record.to_dict() | {"expected_symbols": self.UNIVERSE})
        return tmp

    def _system(self, root: Path):
        from quant.clock import QuantSystem
        return QuantSystem(root, universe=self.UNIVERSE, dataset_id=FUTURES_DATASET,
                           state_dir="var/futures")

    def _economic_state(self, root: Path) -> dict:
        import json
        state = root / "var" / "futures"
        book = json.loads((state / "book.json").read_text())
        evaluation = json.loads((state / "evaluation_ledger.json").read_text())
        strategies = json.loads((state / "strategies.json").read_text())
        strip = lambda ledger: {k: ledger[k] for k in ("cash", "fills", "fees_paid",
                                                      "realized_pnl", "sessions", "sleeves",
                                                      "attribution", "applied_operations")}
        return {"book": strip(book), "evaluation": strip(evaluation),
                "nav": [(p["date"], round(p["nav"], 6)) for p in evaluation["nav_history"]],
                "lifecycle": {k: (v["lifecycle"], v["shadow"].get("sequential", {}).get("history"))
                              for k, v in strategies["strategies"].items()}}

    def test_interrupted_run_replays_to_the_same_economic_state(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            straight = self._root(Path(a))
            system = self._system(straight)
            system.boot()
            system.run()
            self.assertEqual(system.state.status, "IDLE")
            self.assertGreater(system.state.desk_sessions, 100)
            self.assertFalse((straight / "var" / "book.json").exists(),
                             "the futures instance must not create ETF state")

            broken = self._root(Path(b))
            for ticks in (1, 7, 40):          # stop, rebuild from disk, continue
                system = self._system(broken)
                system.boot()
                system.run(max_ticks=ticks)
            system = self._system(broken)
            system.boot()
            system.run()
            self.assertEqual(self._economic_state(straight), self._economic_state(broken))



class LifecycleRedTeamTests(unittest.TestCase):
    """Runtime red-team findings: retired sleeves, tampered snapshots, orphans."""

    UNIVERSE = ["A", "B", "C", "D"]

    def _system(self, root: Path):
        return FuturesInstanceRestartTests._system(self, root)

    def _root(self, tmp: Path) -> Path:
        return FuturesInstanceRestartTests._root(self, tmp)

    def _tradable(self, system, lifecycle: str = "SHADOW"):
        from quant.factory.strategies import StrategyDefinition
        spec = _ts_spec(self.UNIVERSE)
        spec = StrategySpec(**{**spec.to_dict(), "dataset_id": FUTURES_DATASET})
        definition = StrategyDefinition(strategy_id="STR-TEST-TS", version=1,
                                        lane="time_series_trend_carry", spec=spec.to_dict(),
                                        dataset_id=FUTURES_DATASET)
        definition.transition("VALIDATED", "fixture")
        definition.transition("SHADOW", "fixture")
        system.strategies.upsert(definition)
        return definition

    def test_retired_capital_sleeve_is_liquidated_once_and_restart_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(Path(tmp))
            system = self._system(root)
            system.boot()
            system.run(max_ticks=2)                  # research
            self._tradable(system)
            system.run(max_ticks=30)
            self.assertTrue(system.desk.capital.sleeves.get("STR-TEST-TS"))
            held = sum(abs(p.quantity) for p in system.desk.capital.sleeves["STR-TEST-TS"].values())
            self.assertGreater(held, 0)
            definition = system.strategies.get("STR-TEST-TS")
            definition.transition("RETIRED", "fixture: evidence rejected the edge")
            system.strategies.upsert(definition)
            self.assertTrue(system.desk.liquidating(definition))
            system.run(max_ticks=1)                  # one session: the exit
            restarted = self._system(root)           # rebuild from disk mid-life
            restarted.boot()
            restarted.run(max_ticks=5)
            sleeve = restarted.desk.capital.sleeves.get("STR-TEST-TS", {})
            self.assertTrue(all(abs(p.quantity) <= 1e-9 for p in sleeve.values()))
            self.assertFalse(restarted.desk.liquidating(restarted.strategies.get("STR-TEST-TS")))
            self.assertNotIn("STR-TEST-TS", [d.strategy_id for d in restarted.desk.actionable()])
            import json
            tickets = [json.loads(line) for line in
                       (root / "var" / "futures" / "opportunities.jsonl").read_text().splitlines()
                       if "STR-TEST-TS" in line]
            exits = [t for t in tickets if any(stage.get("verdict") == "LIQUIDATE"
                                              for stage in t.get("stage_trace", []))]
            self.assertEqual(len([t for t in exits if t["status"] == "BOOKED"]), 1)

    def test_review_moves_lifecycle_only_on_pristine_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(Path(tmp))
            system = self._system(root)
            system.boot()
            system.run(max_ticks=2)
            definition = self._tradable(system)
            dates = system.panel().dates
            # everything the fixture holds is "seen history": no transition allowed
            definition.evidence["pristine_after"] = dates[-1]
            system.strategies.upsert(definition)
            system.run()
            after = system.strategies.get("STR-TEST-TS")
            self.assertEqual(after.lifecycle, "SHADOW")
            review = after.shadow["sequential"]
            self.assertEqual(review["pristine_sessions"], 0)
            self.assertIn("monitoring_including_seen_history", review)
            self.assertGreater(after.shadow["sessions"], 50)
            self.assertLessEqual(after.shadow["max_drawdown"], 0.0)
            self.assertGreater(after.shadow["costs"], 0.0)

    def test_tampered_snapshot_is_not_registered_available(self):
        import gzip
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(Path(tmp))
            path = root / "data" / "datasets" / f"{FUTURES_DATASET}.csv.gz"
            from quant.dataplane.registry import fingerprint_file
            from quant.state import read_json, write_json
            meta = path.with_suffix(".meta.json")
            write_json(meta, read_json(meta) | {"fingerprint": fingerprint_file(path)})
            text = gzip.decompress(path.read_bytes()).decode()
            lines = text.split("\r\n")
            parts = lines[500].split(",")
            parts[6] = f"{float(parts[6]) * 1.01:.6f}"     # one adj_close changed by 1%
            lines[500] = ",".join(parts)
            path.write_bytes(gzip.compress("\r\n".join(lines).encode(), mtime=0))
            system = self._system(root)
            system.boot()
            record = system.datasets.get(FUTURES_DATASET)
            self.assertEqual(record.availability, "INVALID")
            self.assertTrue(any("committed sidecar" in problem
                                for problem in record.validation["problems"]))

    def test_orphaned_staging_files_are_swept_only_when_old(self):
        import os
        import time
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(Path(tmp))
            system = self._system(root)
            system.boot()
            old = system.paths.var / ".desk_journal.json.abc123"
            fresh = system.paths.var / ".book.json.def456"
            old.write_text("{}")
            fresh.write_text("{}")
            past = time.time() - 3600
            os.utime(old, (past, past))
            self._system(root).boot()
            self.assertFalse(old.exists())
            self.assertTrue(fresh.exists())


if __name__ == "__main__":
    unittest.main()
