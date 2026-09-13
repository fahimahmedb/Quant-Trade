"""Tests for the Quant System V1 planes.

Where a test needs prices it uses a deterministic synthetic fixture. The
fixture is generated in-process, is never registered as a market dataset and
never reaches a ledger with capital authority: it exists to prove the machinery,
not to produce evidence about markets.
"""

import math
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.book.ledger import BackwardInTime, Ledger
from quant.clock import QuantSystem, Timer
from quant.dataplane.panel import PricePanel
from quant.dataplane.registry import DatasetRecord, DatasetRegistry
from quant.dataplane.validation import validate_panel
from quant.desk.desk import CapitalDesk
from quant.desk.execution import ExecutionModel
from quant.desk.journal import DeskJournal
from quant.desk.risk import RiskLimits, evaluate as evaluate_risk, verify_final
from quant.events import EventLog
from quant.factory.evaluate import (compound, falsify, required_t_statistic,
                                    summarize, walk_forward)
from quant.factory.lanes import WINDOWS
from quant.factory.signals import (StrategySpec, cross_sectional_scores, should_rebalance,
                                   target_weights, weights_for)
from quant.factory.strategies import StrategyDefinition, StrategyRegistry
from quant.factory.workers import research_panel
from quant.learning.store import BuildTask, LearningStore
from quant.paths import QuantPaths
from quant.state import ComponentRegistry
from quant.status.brief import build_chief_brief
from quant.status.render import render_status

UNIVERSE = ["AAA", "BBB", "CCC", "DDD"]
BENCHMARK = "SPY"


def session_date(index: int) -> str:
    year, remainder = 2020 + (index // 360), index % 360
    return f"{year}-{(remainder // 30) + 1:02d}-{(remainder % 30) + 1:02d}"


def fixture_panel(sessions: int = 400, seed: float = 0.17) -> PricePanel:
    """Deterministic synthetic bars. Not market data and never presented as such."""
    rows = []
    level = {symbol: 100.0 for symbol in UNIVERSE + [BENCHMARK]}
    for index in range(sessions):
        date = session_date(index)
        for position, symbol in enumerate(UNIVERSE + [BENCHMARK]):
            wave = math.sin((index + position * 7) * seed) * 0.01
            drift = 0.0003 if symbol == BENCHMARK else 0.0002
            level[symbol] *= 1.0 + wave + drift
            price = level[symbol]
            rows.append({"date": date, "symbol": symbol, "open": price * 0.999,
                         "high": price * 1.004, "low": price * 0.996, "close": price,
                         "adj_close": price, "volume": 5_000_000.0})
    return PricePanel(rows)


def overnight_gap_panel(sessions: int = 120) -> PricePanel:
    """Adversarial fixture: every move happens in the forbidden interval.

    Opens are identical on every session, so ``open(t+1) -> open(t+2)`` is
    exactly zero for every symbol. Closes carry a persistent cross-sectional
    ranking, so a close-to-close backtest sees a large, stable profit that lives
    entirely in the close(t) -> open(t+1) gap the desk can never trade.
    """
    drifts = {"AAA": 0.004, "BBB": 0.002, "CCC": -0.002, "DDD": -0.004, BENCHMARK: 0.0}
    rows = []
    for index in range(sessions):
        date = session_date(index)
        for symbol, drift in drifts.items():
            close = 100.0 * (1.0 + drift) ** index
            rows.append({"date": date, "symbol": symbol, "open": 100.0,
                         "high": max(100.0, close) * 1.01, "low": min(100.0, close) * 0.99,
                         "close": close, "adj_close": close, "volume": 5_000_000.0})
    return PricePanel(rows)


def fixture_spec(**overrides) -> StrategySpec:
    defaults = {"family": "cross_sectional", "universe": UNIVERSE, "lookback_days": 5,
                "direction": -1, "min_abs_score": 0.5, "dataset_id": "fixture"}
    defaults.update(overrides)
    return StrategySpec(**defaults)


class PanelTests(unittest.TestCase):
    def test_windows_are_contiguous_and_do_not_overlap(self):
        panel = fixture_panel()
        windows = panel.split(WINDOWS, symbols=UNIVERSE)
        self.assertLess(windows["DISCOVERY"].end, windows["VALIDATION"].start)
        self.assertLess(windows["VALIDATION"].end, windows["SHADOW"].start)
        self.assertEqual(windows["SHADOW"].end, panel.aligned_dates(UNIVERSE)[-1])

    def test_restrict_makes_future_bars_unreachable(self):
        panel = fixture_panel()
        cutoff = panel.dates[100]
        self.assertTrue(all(date <= cutoff for date in panel.restrict(end=cutoff).dates))

    def test_aligned_dates_exclude_partially_covered_sessions(self):
        rows = [{"date": "2024-01-01", "symbol": "AAA", "open": 1, "high": 1, "low": 1,
                 "close": 1, "adj_close": 1, "volume": 1},
                {"date": "2024-01-02", "symbol": "AAA", "open": 1, "high": 1, "low": 1,
                 "close": 1, "adj_close": 1, "volume": 1},
                {"date": "2024-01-02", "symbol": "BBB", "open": 1, "high": 1, "low": 1,
                 "close": 1, "adj_close": 1, "volume": 1}]
        panel = PricePanel(rows)
        self.assertEqual(panel.aligned_dates(["AAA", "BBB"]), ["2024-01-02"])


class LeakageTests(unittest.TestCase):
    def test_research_cannot_see_the_desk_reserved_window(self):
        panel = fixture_panel()
        visible, windows = research_panel(panel, UNIVERSE)
        self.assertLess(visible.dates[-1], windows["SHADOW"]["start"])
        self.assertEqual(visible.dates[-1], windows["VALIDATION"]["end"])

    def test_return_interval_starts_at_the_earliest_possible_fill(self):
        """Entry is the open after the decision; the return may not start earlier."""
        panel = fixture_panel(sessions=200)
        dates = panel.aligned_dates(UNIVERSE)
        spec = fixture_spec(lookback_days=1)
        window = panel.split({"A": 0.5, "B": 0.5}, symbols=UNIVERSE)["B"]
        rows = walk_forward(panel, spec, window, cost_bps=0.0)
        self.assertTrue(rows)
        for row in rows:
            self.assertLess(row["signal_date"], row["entry_date"])
            self.assertLess(row["entry_date"], row["exit_date"])
            index = dates.index(row["signal_date"])
            self.assertEqual(dates[index + 1], row["entry_date"])
            self.assertEqual(dates[index + 2], row["exit_date"])


class OvernightGapTests(unittest.TestCase):
    """Invariant 1: no return may be credited before the entry can happen."""

    def setUp(self):
        self.panel = overnight_gap_panel()
        self.spec = fixture_spec(direction=1, lookback_days=5, min_abs_score=0.5)
        self.window = self.panel.split({"A": 0.3, "B": 0.7}, symbols=UNIVERSE)["B"]
        self.rows = walk_forward(self.panel, self.spec, self.window, cost_bps=0.0)

    def test_the_fixture_really_is_adversarial(self):
        """A close-to-close reading of the same positions would look very profitable."""
        counterfactual = []
        for row in self.rows:
            earned = 0.0
            for symbol, weight in row["weights"].items():
                before = self.panel.price(row["signal_date"], symbol)
                earned += weight * (self.panel.price(row["entry_date"], symbol) / before - 1.0)
            counterfactual.append(earned)
        self.assertGreater(compound(counterfactual), 0.05,
                           "the fixture must put a large profit in the forbidden interval")

    def test_the_forbidden_interval_is_not_credited(self):
        self.assertTrue(self.rows)
        for row in self.rows:
            self.assertAlmostEqual(row["gross_return"], 0.0, places=12)
        summary = summarize(self.rows, self.panel, BENCHMARK, 0.0)
        self.assertAlmostEqual(summary["gross_return"], 0.0, places=10)

    def test_costs_can_only_make_it_worse(self):
        costed = walk_forward(self.panel, self.spec, self.window, cost_bps=5.0)
        self.assertLessEqual(summarize(costed, self.panel, BENCHMARK, 5.0)["net_return"], 0.0)


class SignalTests(unittest.TestCase):
    def test_target_weights_are_dollar_neutral_and_capped(self):
        panel = fixture_panel()
        spec = fixture_spec(max_weight=0.3)
        found = 0
        for date in panel.aligned_dates(UNIVERSE)[10:60]:
            weights = weights_for(panel, spec, date)
            if not weights:
                continue
            found += 1
            gross = sum(abs(value) for value in weights.values())
            self.assertAlmostEqual(sum(weights.values()), 0.0, places=9)
            self.assertLessEqual(max(abs(value) for value in weights.values()),
                                 spec.max_weight + 1e-9)
            self.assertGreater(gross, 0.0)
            self.assertLessEqual(gross, spec.gross_exposure + 1e-9)
        self.assertGreater(found, 0)

    def test_insufficient_history_yields_no_signal_not_a_zero_signal(self):
        panel = fixture_panel()
        first = panel.aligned_dates(UNIVERSE)[0]
        self.assertEqual(cross_sectional_scores(panel, UNIVERSE, first, 5), {})
        self.assertEqual(weights_for(panel, fixture_spec(), first), {})

    def test_direction_flips_the_side_of_the_book(self):
        scores = {"AAA": 2.0, "BBB": -2.0, "CCC": 0.6, "DDD": -0.6}
        reversal = target_weights(scores, fixture_spec(direction=-1))
        momentum = target_weights(scores, fixture_spec(direction=1))
        self.assertLess(reversal["AAA"], 0)
        self.assertGreater(momentum["AAA"], 0)

    def test_rebalance_rule_is_shared_and_respects_hold_and_band(self):
        spec = fixture_spec(holding_days=5, no_trade_band=0.05)
        self.assertTrue(should_rebalance(None, 0.0, spec))
        self.assertFalse(should_rebalance(2, 1.0, spec))
        self.assertFalse(should_rebalance(9, 0.01, spec))
        self.assertTrue(should_rebalance(9, 0.5, spec))


class FalsificationTests(unittest.TestCase):
    def test_required_significance_rises_with_the_number_of_expressions_tried(self):
        self.assertLess(required_t_statistic(1), required_t_statistic(10))
        self.assertLess(required_t_statistic(10), required_t_statistic(100))
        self.assertAlmostEqual(required_t_statistic(1), 1.959963, places=4)

    def test_a_cost_destroyed_strategy_is_rejected_with_a_named_reason(self):
        rows = [{"signal_date": f"d{index}", "return_date": f"d{index + 1}",
                 "gross_return": 0.001, "cost": 0.002, "net_return": -0.001,
                 "turnover": 2.0, "positions": 4, "weights": {}} for index in range(200)]
        panel = fixture_panel()
        summary = {
            "observations": 200, "active_observations": 200, "cost_bps": 5.0,
            "net_return": -0.2, "gross_return": 0.2, "market_return_same_window": 0.1,
            "market_beta": 0.0, "beta_explained_return": 0.0, "t_statistic": -5.0,
            "annual_turnover": 500.0}
        verdict = falsify(rows, summary, panel, BENCHMARK, fixture_spec(), trials=24)
        self.assertFalse(verdict["passed"])
        self.assertEqual(verdict["decision"], "REJECT_RESEARCH")
        self.assertIn("net_profitable_after_modeled_costs", verdict["failed_tests"])

    def test_beta_attribution_is_always_reported(self):
        panel = fixture_panel(sessions=300)
        window = panel.split({"A": 0.5, "B": 0.5}, symbols=UNIVERSE)["B"]
        rows = walk_forward(panel, fixture_spec(), window, 5.0)
        summary = summarize(rows, panel, BENCHMARK, 5.0)
        verdict = falsify(rows, summary, panel, BENCHMARK, fixture_spec(), trials=4)
        self.assertIn("market_beta", verdict["beta_attribution"])
        self.assertIn("return_explained_by_beta", verdict["beta_attribution"])


class LedgerTests(unittest.TestCase):
    def test_fill_is_durable_before_the_next_mark(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "book.json"
            ledger = Ledger(path, initial_capital=1_000_000)
            ledger.apply_fill("AAA", 100, 50.0, 5.0, "2025-01-02", "S1", "op-1")
            recovered = Ledger(path)
            self.assertEqual(recovered.sleeves["S1"]["AAA"].quantity, 100)
            self.assertAlmostEqual(recovered.state.cash, 1_000_000 - 5_000 - 5.0)

    def test_realized_pnl_on_closing_a_long_and_covering_a_short(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / "book.json", initial_capital=1_000_000)
            ledger.apply_fill("AAA", 100, 50.0, 0.0, "2025-01-02", "S1", "a1")
            ledger.apply_fill("AAA", -100, 60.0, 0.0, "2025-01-03", "S1", "a2")
            self.assertAlmostEqual(ledger.state.realized_pnl, 1_000.0)
            ledger.apply_fill("BBB", -100, 50.0, 0.0, "2025-01-03", "S1", "b1")
            ledger.apply_fill("BBB", 100, 40.0, 0.0, "2025-01-04", "S1", "b2")
            self.assertAlmostEqual(ledger.state.realized_pnl, 2_000.0)
            self.assertEqual(ledger.open_positions(), [])

    def test_bankroll_and_nav_history_survive_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "book.json"
            first = Ledger(path, initial_capital=500_000)
            first.apply_fill("AAA", 100, 50.0, 1.0, "2025-01-02", "S1", "op-1")
            first.mark_to_market("2025-01-02", {"AAA": 50.0})
            first.mark_to_market("2025-01-03", {"AAA": 55.0})
            nav = first.nav
            second = Ledger(path)
            self.assertAlmostEqual(second.nav, nav)
            self.assertEqual(len(second.state.nav_history), 2)
            self.assertEqual(second.state.initial_capital, 500_000)
            self.assertEqual(second.state.inception_date, "2025-01-02")

    def test_attribution_is_kept_per_strategy(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / "book.json")
            ledger.apply_fill("AAA", 10, 10.0, 1.0, "2025-01-02", "S1", "op-1")
            ledger.apply_fill("BBB", 10, 10.0, 2.0, "2025-01-02", "S2", "op-2")
            self.assertAlmostEqual(ledger.state.attribution["S1"]["costs"], 1.0)
            self.assertAlmostEqual(ledger.state.attribution["S2"]["costs"], 2.0)

    def test_marking_may_not_move_backward_in_time(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / "book.json")
            ledger.mark_to_market("2025-01-03", {})
            with self.assertRaises(BackwardInTime):
                ledger.mark_to_market("2025-01-02", {})

    def test_repeating_a_mark_restates_it_instead_of_adding_a_session(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / "book.json")
            ledger.apply_fill("AAA", 100, 50.0, 0.0, "2025-01-02", "S1", "op-1")
            ledger.mark_to_market("2025-01-02", {"AAA": 50.0})
            ledger.mark_to_market("2025-01-02", {"AAA": 60.0})
            self.assertEqual(ledger.state.sessions, 1)
            self.assertEqual(len(ledger.state.nav_history), 1)
            self.assertAlmostEqual(ledger.state.nav_history[-1]["nav"], ledger.nav)


class SleeveTests(unittest.TestCase):
    """Invariant 3: several strategies may hold the same instrument."""

    def make(self, directory):
        return Ledger(Path(directory) / "book.json", initial_capital=1_000_000)

    def test_two_strategies_hold_opposing_exposure_without_corrupting_attribution(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.make(directory)
            ledger.apply_fill("AAA", 100, 50.0, 1.0, "2025-01-02", "LONG", "l-1")
            ledger.apply_fill("AAA", -60, 50.0, 2.0, "2025-01-02", "SHORT", "s-1")
            ledger.mark_to_market("2025-01-02", {"AAA": 50.0})

            self.assertAlmostEqual(ledger.sleeve_exposures("LONG")["AAA"], 5_000.0)
            self.assertAlmostEqual(ledger.sleeve_exposures("SHORT")["AAA"], -3_000.0)
            self.assertAlmostEqual(ledger.symbol_exposures()["AAA"], 2_000.0)

            aggregate = ledger.aggregate_positions()
            self.assertEqual(len(aggregate), 1)
            self.assertAlmostEqual(aggregate[0]["quantity"], 40.0)
            self.assertEqual(aggregate[0]["strategies"], ["LONG", "SHORT"])
            self.assertAlmostEqual(ledger.state.attribution["LONG"]["costs"], 1.0)
            self.assertAlmostEqual(ledger.state.attribution["SHORT"]["costs"], 2.0)

    def test_one_strategy_exiting_leaves_the_other_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.make(directory)
            ledger.apply_fill("AAA", 100, 50.0, 0.0, "2025-01-02", "LONG", "l-1")
            ledger.apply_fill("AAA", -60, 50.0, 0.0, "2025-01-02", "SHORT", "s-1")
            ledger.apply_fill("AAA", 60, 55.0, 0.0, "2025-01-03", "SHORT", "s-2")
            self.assertEqual(ledger.sleeve_exposures("SHORT"), {})
            self.assertAlmostEqual(ledger.sleeves["LONG"]["AAA"].quantity, 100)
            self.assertAlmostEqual(ledger.state.attribution["SHORT"]["realized_pnl"], -300.0)
            self.assertAlmostEqual(ledger.state.attribution["LONG"]["realized_pnl"], 0.0)

    def test_sleeves_survive_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "book.json"
            ledger = Ledger(path, initial_capital=1_000_000)
            ledger.apply_fill("AAA", 100, 50.0, 0.0, "2025-01-02", "LONG", "l-1")
            ledger.apply_fill("AAA", -60, 50.0, 0.0, "2025-01-02", "SHORT", "s-1")
            recovered = Ledger(path)
            self.assertAlmostEqual(recovered.sleeves["LONG"]["AAA"].quantity, 100)
            self.assertAlmostEqual(recovered.sleeves["SHORT"]["AAA"].quantity, -60)


class IdempotenceTests(unittest.TestCase):
    """Invariant 2: crash plus replay must equal the uninterrupted run."""

    def test_replaying_an_operation_id_changes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "book.json"
            ledger = Ledger(path, initial_capital=1_000_000)
            ledger.apply_fill("AAA", 100, 50.0, 5.0, "2025-01-02", "S1", "op-1")
            before = (ledger.state.cash, ledger.state.fills, ledger.state.fees_paid,
                      ledger.sleeves["S1"]["AAA"].quantity)

            replayed = Ledger(path).apply_fill("AAA", 100, 50.0, 5.0, "2025-01-02",
                                               "S1", "op-1")
            after = Ledger(path)
            self.assertTrue(replayed["replayed"])
            self.assertEqual((after.state.cash, after.state.fills, after.state.fees_paid,
                              after.sleeves["S1"]["AAA"].quantity), before)

    def test_journal_resumes_a_pending_plan_rather_than_re_deciding(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = DeskJournal(Path(directory) / "journal.json")
            journal.begin("OPP-1", "S1", "2025-01-02", {"opportunity_id": "OPP-1"}, [{"x": 1}])
            reopened = DeskJournal(Path(directory) / "journal.json")
            self.assertIsNotNone(reopened.pending_plan("OPP-1"))
            self.assertFalse(reopened.is_processed("OPP-1"))
            reopened.commit("OPP-1", "S1", "BOOKED", "2025-01-02", True)
            final = DeskJournal(Path(directory) / "journal.json")
            self.assertIsNone(final.pending_plan("OPP-1"))
            self.assertTrue(final.is_processed("OPP-1"))
            self.assertEqual(final.stats_for("S1")["booked"], 1)


class RiskTests(unittest.TestCase):
    """Invariant 5: approval must describe the state that will be simulated."""

    def make_ledger(self, directory, **kwargs):
        return Ledger(Path(directory) / "book.json", initial_capital=1_000_000, **kwargs)

    def test_net_exposure_breach_is_vetoed(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.make_ledger(directory)
            verdict = evaluate_risk(ledger, "S1", {"AAA": 400_000.0}, RiskLimits())
            self.assertFalse(verdict["approved"])
            self.assertTrue(any("net exposure" in reason for reason in verdict["vetoes"]))

    def test_neutral_rebalance_that_closes_a_dropped_leg_is_approved(self):
        """Legs targeted at zero must not be scored as retained."""
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.make_ledger(directory)
            ledger.apply_fill("CCC", 2_000, 100.0, 0.0, "2025-01-02", "S1", "op-1")
            ledger.mark_to_market("2025-01-02", {"CCC": 100.0})
            target = {"AAA": 100_000.0, "BBB": -100_000.0, "CCC": 0.0}
            verdict = evaluate_risk(ledger, "S1", target, RiskLimits())
            self.assertTrue(verdict["approved"], verdict["vetoes"])
            self.assertAlmostEqual(verdict["net_ratio"], 0.0, places=6)

    def test_a_strategy_is_not_charged_twice_for_its_own_sleeve(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.make_ledger(directory)
            ledger.apply_fill("AAA", 2_000, 100.0, 0.0, "2025-01-02", "S1", "op-1")
            ledger.apply_fill("BBB", -2_000, 100.0, 0.0, "2025-01-02", "S1", "op-2")
            ledger.mark_to_market("2025-01-02", {"AAA": 100.0, "BBB": 100.0})
            # Re-proposing exactly what it already holds is a no-op portfolio.
            verdict = evaluate_risk(ledger, "S1", {"AAA": 200_000.0, "BBB": -200_000.0},
                                    RiskLimits())
            self.assertTrue(verdict["approved"], verdict["vetoes"])
            self.assertAlmostEqual(verdict["gross_ratio"], 0.4, places=6)

    def test_scaling_is_validated_on_the_scaled_portfolio(self):
        """Regression: existing exposure plus a proposal that must be scaled."""
        limits = RiskLimits(max_gross_ratio=1.0, max_net_ratio=1.0, max_symbol_ratio=1.0)
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.make_ledger(directory)
            ledger.apply_fill("AAA", 6_000, 100.0, 0.0, "2025-01-02", "OTHER", "op-1")
            ledger.mark_to_market("2025-01-02", {"AAA": 100.0})
            verdict = evaluate_risk(ledger, "S1", {"BBB": 900_000.0}, limits)
            self.assertTrue(verdict["throttled"])
            self.assertGreater(verdict["pre_scale"]["gross_ratio"], limits.max_gross_ratio)
            # The approved portfolio, not the proposed one, is inside the limit.
            self.assertLessEqual(verdict["gross_ratio"], limits.max_gross_ratio + 1e-9)
            self.assertTrue(verdict["approved"])
            applied = verify_final(ledger, "S1", verdict["scaled_target"], limits)
            self.assertTrue(applied["approved"], applied["vetoes"])

    def test_scaling_that_cannot_satisfy_a_hard_limit_is_vetoed(self):
        """Scaling reduces gross but cannot fix a breach caused by another sleeve."""
        limits = RiskLimits(max_gross_ratio=5.0, max_net_ratio=0.10, max_symbol_ratio=1.0)
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.make_ledger(directory)
            ledger.apply_fill("AAA", 5_000, 100.0, 0.0, "2025-01-02", "OTHER", "op-1")
            ledger.mark_to_market("2025-01-02", {"AAA": 100.0})
            verdict = evaluate_risk(ledger, "S1", {"BBB": 10_000.0}, limits)
            self.assertFalse(verdict["approved"])
            self.assertTrue(any("net exposure" in reason for reason in verdict["vetoes"]))

    def test_verify_final_rejects_a_truncated_execution_that_breaches_a_limit(self):
        limits = RiskLimits(max_net_ratio=0.05)
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.make_ledger(directory)
            approved = {"AAA": 100_000.0, "BBB": -100_000.0}
            self.assertTrue(evaluate_risk(ledger, "S1", approved, limits)["approved"])
            # Capacity truncation removed the short leg; the executed book is not neutral.
            executed = {"AAA": 100_000.0, "BBB": -1_000.0}
            self.assertFalse(verify_final(ledger, "S1", executed, limits)["approved"])

    def test_drawdown_throttles_then_halts(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.make_ledger(directory)
            ledger.state.peak_nav = 1_000_000
            ledger.state.cash = 880_000
            self.assertTrue(evaluate_risk(ledger, "S1", {}, RiskLimits())["throttled"])
            ledger.state.cash = 750_000
            self.assertFalse(evaluate_risk(ledger, "S1", {}, RiskLimits())["approved"])


class ExecutionTests(unittest.TestCase):
    def test_fill_happens_at_the_next_session_and_pays_the_spread(self):
        panel = fixture_panel(sessions=60)
        dates = panel.aligned_dates(UNIVERSE)
        model = ExecutionModel()
        buy = model.fill(panel, "AAA", 100, dates[30], dates[31])
        sell = model.fill(panel, "AAA", -100, dates[30], dates[31])
        self.assertEqual(buy["execution_date"], dates[31])
        self.assertGreater(buy["fill_price"], buy["reference_price"])
        self.assertLess(sell["fill_price"], sell["reference_price"])
        self.assertGreater(buy["commission"], 0)

    def test_order_is_truncated_to_a_plausible_share_of_volume(self):
        panel = fixture_panel(sessions=60)
        dates = panel.aligned_dates(UNIVERSE)
        model = ExecutionModel(max_participation=0.01)
        fill = model.fill(panel, "AAA", 10_000_000, dates[30], dates[31])
        self.assertTrue(fill["capacity_truncated"])
        self.assertLess(abs(fill["quantity"]), 10_000_000)


class SystemTests(unittest.TestCase):
    """End-to-end behaviour of the Control Plane over a fixture dataset."""

    def build(self, directory, sessions=400):
        root = Path(directory)
        panel = fixture_panel(sessions=sessions)
        target = root / "data" / "datasets" / "fixture.csv"
        panel.write(target)
        paths = QuantPaths(root).ensure()
        registry = DatasetRegistry(paths.dataset_registry, root)
        record = DatasetRecord(dataset_id="fixture", source="synthetic test fixture",
                               adapter="fixture", path="data/datasets/fixture.csv")
        record.symbols = panel.symbols
        record.rows = len(panel.bars)
        record.first_date, record.last_date = panel.dates[0], panel.dates[-1]
        record.validation = validate_panel(panel, UNIVERSE)
        registry.register(record)
        registry.refresh_availability()
        return root

    def system(self, root):
        return QuantSystem(root, universe=UNIVERSE, dataset_id="fixture")

    def test_boot_run_and_restart_preserve_one_continuous_system(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.build(directory)
            first = self.system(root)
            first.boot()
            first.run()
            sessions, ticks = first.state.desk_sessions, first.state.ticks
            cursor, nav = first.state.desk_cursor, first.desk.evaluation.nav
            self.assertGreater(sessions, 0)

            restarted = self.system(root)
            boot = restarted.boot()
            self.assertEqual(boot["boot"], 2)
            self.assertEqual(restarted.state.desk_cursor, cursor)
            self.assertEqual(restarted.state.desk_sessions, sessions)
            self.assertAlmostEqual(restarted.desk.evaluation.nav, nav, places=6)
            self.assertEqual(restarted.tick(), "IDLE")
            self.assertGreater(restarted.state.ticks, ticks)
            self.assertEqual(restarted.state.desk_sessions, sessions,
                             "a restart must not replay sessions already booked")

    def test_idle_is_not_finished(self):
        with tempfile.TemporaryDirectory() as directory:
            system = self.system(self.build(directory))
            system.boot()
            system.run()
            self.assertEqual(system.state.status, "IDLE")
            self.assertNotEqual(system.state.status, "STOPPED")
            self.assertTrue(system.state.next_action)
            self.assertEqual(system.components.get("CONTROL").state, "IDLE")

    def test_blocked_dependency_is_named_and_unblocks_when_data_arrives(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            QuantPaths(root).ensure()
            system = self.system(root)          # no dataset registered yet
            system.boot()
            research = [task for task in system.queue.tasks.values()
                        if task.worker == "research_lane"]
            self.assertTrue(research)
            self.assertTrue(all(task.status == "BLOCKED" for task in research))
            self.assertTrue(all("fixture" in (task.blocked_reason or "") for task in research))
            self.assertEqual(system.tick(), "IDLE")

            self.build(directory)               # the dependency arrives
            resumed = self.system(root)
            boot = resumed.boot()
            self.assertTrue(boot["unblocked"])
            self.assertEqual(resumed.tick(), "RESEARCH")

    def test_a_worker_fault_is_recorded_without_killing_the_system(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.build(directory)
            system = self.system(root)
            system.boot()
            import quant.clock as clock_module
            original = clock_module.run_lane
            clock_module.run_lane = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
            failed = system.queue.next_due().task_id
            try:
                self.assertEqual(system.tick(), "FAULT")
            finally:
                clock_module.run_lane = original
            self.assertTrue(system.state.faults)
            self.assertEqual(system.components.get("RESEARCH").state, "FAULT")
            self.assertTrue(any(alert["code"] == "COMPONENT_FAULT"
                                for alert in system.health()))
            self.assertEqual(system.queue.tasks[failed].status, "FAILED")
            # The system stays alive and the failed task is retried on a fresh boot.
            self.assertIn(system.tick(), {"SESSION", "RESEARCH", "IDLE"})
            restarted = self.system(root)
            self.assertIn(failed, restarted.boot()["recovered"])
            self.assertEqual(restarted.queue.tasks[failed].status, "PENDING")
            self.assertEqual(restarted.tick(), "RESEARCH")

    def test_interrupted_work_is_requeued_on_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.build(directory)
            system = self.system(root)
            system.boot()
            task = system.queue.next_due()
            task.status = "RUNNING"
            system.queue.save()
            restarted = self.system(root)
            boot = restarted.boot()
            self.assertIn(task.task_id, boot["recovered"])
            self.assertEqual(restarted.queue.tasks[task.task_id].status, "PENDING")

    def test_identical_work_on_unchanged_data_is_not_repeated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.build(directory)
            system = self.system(root)
            system.boot()
            self.assertEqual(system.tick(), "RESEARCH")
            runs = system.state.research_runs
            task = next(task for task in system.queue.tasks.values()
                        if task.status == "COMPLETED")
            trials = dict(system.strategies.trials)
            task.status = "PENDING"
            system.queue.save()
            system.tick()
            self.assertEqual(system.state.research_runs, runs,
                             "the same test on the same fingerprint must not re-run")
            self.assertEqual(system.strategies.trials, trials,
                             "a skipped repeat must not inflate the trial count")
            self.assertEqual(system.queue.tasks[task.task_id].status, "COMPLETED")

    def test_new_data_makes_the_same_question_worth_asking_again(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.build(directory)
            system = self.system(root)
            system.boot()
            self.assertEqual(system.tick(), "RESEARCH")
            runs = system.state.research_runs
            task = next(task for task in system.queue.tasks.values()
                        if task.status == "COMPLETED")
            task.status = "PENDING"
            system.queue.save()
            self.build(directory, sessions=430)          # the dataset moves on
            system.datasets.refresh_availability()
            system._panel = None
            system.tick()
            self.assertEqual(system.state.research_runs, runs + 1)

    def test_pause_survives_restart_until_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.build(directory)
            system = self.system(root)
            system.boot()
            system.pause("maintenance")
            restarted = self.system(root)
            self.assertEqual(restarted.tick(), "PAUSED")
            restarted.resume()
            self.assertNotEqual(restarted.tick(), "PAUSED")

    def test_untradable_strategies_never_reach_the_capital_ledger(self):
        with tempfile.TemporaryDirectory() as directory:
            system = self.system(self.build(directory))
            system.boot()
            system.run()
            tradable = {definition.strategy_id for definition
                        in system.strategies.strategies.values() if definition.tradable}
            touched = set(system.desk.capital.state.attribution)
            self.assertTrue(touched <= tradable,
                            f"untradable strategies reached the capital ledger: "
                            f"{touched - tradable}")
            evaluated = {definition.strategy_id for definition
                         in system.strategies.strategies.values()
                         if definition.evaluation_track}
            self.assertTrue(set(system.desk.evaluation.state.attribution) <= evaluated)
            self.assertGreater(system.desk.capital.state.sessions, 0,
                               "the book marks every session even when flat")

    def test_status_and_brief_render_from_the_same_persistent_state(self):
        with tempfile.TemporaryDirectory() as directory:
            system = self.system(self.build(directory))
            system.boot()
            system.run()
            snapshot = system.snapshot()
            surface = render_status(snapshot)
            brief = build_chief_brief(snapshot)
            self.assertIn("QUANT SYSTEM V1", surface)
            self.assertIn(f"{snapshot['book']['nav']:,.2f}", surface)
            self.assertIn("# Chief Brief", brief)
            self.assertIn(snapshot["data"]["datasets"]["fixture"]["fingerprint"], brief)


class DeskRoutingTests(unittest.TestCase):
    def test_a_tradable_strategy_books_into_the_capital_ledger(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = QuantPaths(root).ensure()
            panel = fixture_panel(sessions=120)
            panel.write(root / "data" / "datasets" / "fixture.csv")
            registry = DatasetRegistry(paths.dataset_registry, root)
            record = DatasetRecord(dataset_id="fixture", source="fixture", adapter="fixture",
                                   path="data/datasets/fixture.csv")
            registry.register(record)
            registry.refresh_availability()
            strategies = StrategyRegistry(paths.strategies)
            definition = StrategyDefinition(
                strategy_id="STR-TEST", version=1, lane="test",
                spec=fixture_spec().to_dict())
            definition.transition("VALIDATED", "fixture")
            definition.transition("SHADOW", "fixture")
            strategies.upsert(definition)
            desk = CapitalDesk(paths, strategies, registry, EventLog(paths.events),
                               ComponentRegistry(paths.components))
            dates = panel.aligned_dates(UNIVERSE)
            booked = 0
            for index in range(20, 40):
                summary = desk.run_session(panel, dates[index], dates[index + 1])
                booked += sum(1 for ticket in summary["tickets"]
                              if ticket["status"] == "BOOKED")
            self.assertGreater(booked, 0)
            self.assertGreater(desk.capital.state.fills, 0)
            self.assertEqual(desk.evaluation.state.fills, 0)

    def test_every_stage_of_a_booked_ticket_is_traced(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = QuantPaths(root).ensure()
            panel = fixture_panel(sessions=120)
            panel.write(root / "data" / "datasets" / "fixture.csv")
            registry = DatasetRegistry(paths.dataset_registry, root)
            registry.register(DatasetRecord(dataset_id="fixture", source="fixture",
                                            adapter="fixture",
                                            path="data/datasets/fixture.csv"))
            registry.refresh_availability()
            strategies = StrategyRegistry(paths.strategies)
            definition = StrategyDefinition(strategy_id="STR-TEST", version=1, lane="test",
                                            spec=fixture_spec().to_dict())
            definition.transition("VALIDATED", "fixture")
            definition.transition("SHADOW", "fixture")
            strategies.upsert(definition)
            desk = CapitalDesk(paths, strategies, registry, EventLog(paths.events),
                               ComponentRegistry(paths.components))
            dates = panel.aligned_dates(UNIVERSE)
            traced = None
            for index in range(20, 40):
                for ticket in desk.run_session(panel, dates[index], dates[index + 1])["tickets"]:
                    if ticket["status"] == "BOOKED":
                        traced = ticket
                        break
                if traced:
                    break
            self.assertIsNotNone(traced)
            self.assertEqual([entry["stage"] for entry in traced["stage_trace"]],
                             ["SCAN", "VET", "SIZE", "RISK", "FILLS", "BOOK"])
            for entry in traced["stage_trace"]:
                self.assertTrue(entry["reason"])


class LifecycleTests(unittest.TestCase):
    def test_lifecycle_transitions_are_restrictive(self):
        definition = StrategyDefinition(strategy_id="S", version=1, lane="l",
                                        spec=fixture_spec().to_dict())
        with self.assertRaises(ValueError):
            definition.transition("ACTIVE_SHADOW", "skipping validation")
        definition.transition("VALIDATED", "evidence")
        definition.transition("SHADOW", "probe")
        self.assertTrue(definition.tradable)
        definition.transition("RETIRED", "decayed")
        self.assertFalse(definition.tradable)
        self.assertEqual(definition.retirement_reason, "decayed")

    def test_evaluation_track_is_sized_but_not_tradable(self):
        definition = StrategyDefinition(strategy_id="S", version=1, lane="l",
                                        spec=fixture_spec().to_dict())
        definition.evaluation_track = True
        self.assertFalse(definition.tradable)
        self.assertGreater(definition.capital_fraction, 0.0)

    def test_trial_counter_accumulates_across_lanes(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = StrategyRegistry(Path(directory) / "strategies.json")
            self.assertEqual(registry.record_trials("d@f", 24), 24)
            self.assertEqual(registry.record_trials("d@f", 12), 36)
            reopened = StrategyRegistry(Path(directory) / "strategies.json")
            self.assertEqual(reopened.trial_count("d@f"), 36)


class LearningTests(unittest.TestCase):
    def test_a_losing_rejection_is_scored_as_a_true_reject(self):
        with tempfile.TemporaryDirectory() as directory:
            store = LearningStore(Path(directory) / "learning.json")
            ledger = Ledger(Path(directory) / "evaluation.json", authority="EVALUATION",
                            initial_capital=1_000_000)
            ledger.state.attribution["S1"] = {"realized_pnl": -50_000.0, "costs": 1_000.0,
                                              "fills": 10, "notional": 1.0}
            strategies = StrategyRegistry(Path(directory) / "strategies.json")
            definition = StrategyDefinition(strategy_id="S1", version=1, lane="l",
                                            spec=fixture_spec().to_dict())
            definition.evaluation_track = True
            strategies.upsert(definition)
            assessments = store.assess_rejections(
                strategies, ledger, lambda _: {"booked": 10, "sessions": 10})
            self.assertEqual(assessments[0]["verdict"], "TRUE_REJECT")
            self.assertEqual(store.decision_quality["true_rejects"], 1)

    def test_a_profitable_rejection_is_scored_as_a_false_reject(self):
        with tempfile.TemporaryDirectory() as directory:
            store = LearningStore(Path(directory) / "learning.json")
            ledger = Ledger(Path(directory) / "evaluation.json", authority="EVALUATION",
                            initial_capital=1_000_000)
            ledger.state.attribution["S1"] = {"realized_pnl": 80_000.0, "costs": 1_000.0,
                                              "fills": 10, "notional": 1.0}
            strategies = StrategyRegistry(Path(directory) / "strategies.json")
            definition = StrategyDefinition(strategy_id="S1", version=1, lane="l",
                                            spec=fixture_spec().to_dict())
            definition.evaluation_track = True
            strategies.upsert(definition)
            self.assertEqual(store.assess_rejections(
                strategies, ledger, lambda _: {"booked": 10})[0]["verdict"], "FALSE_REJECT")

    def test_build_tasks_capture_capability_gaps_once(self):
        with tempfile.TemporaryDirectory() as directory:
            store = LearningStore(Path(directory) / "learning.json")
            task = BuildTask("B1", "options panel", "no chains", ["DATA"], "ingest", 5.0)
            store.raise_build_task(task)
            store.raise_build_task(task)
            self.assertEqual(len(store.open_build_tasks()), 1)


class SchemaTests(unittest.TestCase):
    def test_committed_schemas_match_the_dataclasses(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import generate_schemas
        import json
        for name, schema in generate_schemas.generate().items():
            path = ROOT / "schemas" / f"{name}.schema.json"
            self.assertTrue(path.exists(), f"{name} schema is missing")
            self.assertEqual(json.loads(path.read_text()), schema,
                             f"{name}.schema.json is stale; run "
                             f"python3 scripts/generate_schemas.py")


class DataPlaneTests(unittest.TestCase):
    def test_validation_rejects_a_panel_with_a_missing_symbol(self):
        panel = fixture_panel(sessions=300)
        result = validate_panel(panel, UNIVERSE + ["MISSING"])
        self.assertFalse(result["passed"])
        self.assertTrue(any("absent" in problem for problem in result["problems"]))

    def test_changed_bytes_produce_a_new_fingerprint_and_availability(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "data" / "datasets" / "fixture.csv"
            fixture_panel(sessions=300).write(target)
            registry = DatasetRegistry(root / "registry.json", root)
            registry.register(DatasetRecord(dataset_id="fixture", source="fixture",
                                            adapter="fixture",
                                            path="data/datasets/fixture.csv"))
            registry.refresh_availability()
            original = registry.get("fixture").fingerprint
            self.assertEqual(registry.missing_for(["fixture"]), [])
            fixture_panel(sessions=310).write(target)
            self.assertTrue(registry.refresh_availability())
            self.assertNotEqual(registry.get("fixture").fingerprint, original)
            target.unlink()
            registry.refresh_availability()
            self.assertEqual(registry.get("fixture").availability, "MISSING")
            self.assertEqual(registry.missing_for(["fixture"]), ["fixture"])


class FakeTimer:
    """Deterministic clock. Records waits instead of performing them."""

    def __init__(self):
        self.slept: list[float] = []
        self._now = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def now(self):
        return self._now

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self._now += timedelta(seconds=seconds)


def shadow_desk(root: Path, panel: PricePanel, strategy_id: str = "STR-TEST",
                **spec_overrides):
    """A desk with one tradable strategy over a fixture panel."""
    paths = QuantPaths(root).ensure()
    panel.write(root / "data" / "datasets" / "fixture.csv")
    registry = DatasetRegistry(paths.dataset_registry, root)
    registry.register(DatasetRecord(dataset_id="fixture", source="fixture",
                                    adapter="fixture", path="data/datasets/fixture.csv"))
    registry.refresh_availability()
    strategies = StrategyRegistry(paths.strategies)
    if strategy_id not in strategies.strategies:
        definition = StrategyDefinition(strategy_id=strategy_id, version=1, lane="test",
                                        spec=fixture_spec(**spec_overrides).to_dict())
        definition.transition("VALIDATED", "fixture")
        definition.transition("SHADOW", "fixture")
        strategies.upsert(definition)
    return CapitalDesk(paths, strategies, registry, EventLog(paths.events),
                       ComponentRegistry(paths.components))


def ledger_fingerprint(ledger: Ledger) -> dict:
    """Everything the mission requires to be identical after a crash."""
    return {"cash": round(ledger.state.cash, 6), "nav": round(ledger.nav, 6),
            "fills": ledger.state.fills, "sessions": ledger.state.sessions,
            "realized": round(ledger.state.realized_pnl, 6),
            "fees": round(ledger.state.fees_paid, 6),
            "nav_points": len(ledger.state.nav_history),
            "last_session": ledger.state.last_session_date,
            "sleeves": {strategy: {symbol: round(position.quantity, 6)
                                   for symbol, position in holdings.items()}
                        for strategy, holdings in sorted(ledger.sleeves.items())},
            "attribution": {key: {name: round(value, 6) for name, value in sorted(item.items())}
                            for key, item in sorted(ledger.state.attribution.items())}}


class CrashRecoveryTests(unittest.TestCase):
    """Invariant 2, end to end: crash + restart + replay == uninterrupted."""

    SESSIONS = 12

    def run_sessions(self, root: Path, panel: PricePanel, dates: list[str],
                     crash_on: str | None = None) -> Ledger:
        desk = shadow_desk(root, panel)
        for index, date in enumerate(dates):
            next_date = dates[index + 1] if index + 1 < len(dates) else None
            if date == crash_on:
                original = DeskJournal.commit
                exploded = {"done": False}

                def exploding(self, opportunity_id, *args, **kwargs):
                    # Crash after the fills are durable but before the session
                    # is committed: the dangerous boundary.
                    if not exploded["done"]:
                        exploded["done"] = True
                        raise RuntimeError("process killed mid-session")
                    return original(self, opportunity_id, *args, **kwargs)

                DeskJournal.commit = exploding
                try:
                    with self.assertRaises(RuntimeError):
                        desk.run_session(panel, date, next_date)
                finally:
                    DeskJournal.commit = original
                # The process is gone: rebuild every object from disk.
                desk = shadow_desk(root, panel)
                desk.run_session(panel, date, next_date)
            else:
                desk.run_session(panel, date, next_date)
        return desk

    def test_crash_after_durable_fills_does_not_duplicate_anything(self):
        panel = fixture_panel(sessions=90)
        dates = panel.aligned_dates(UNIVERSE)[20:20 + self.SESSIONS]
        with tempfile.TemporaryDirectory() as clean, tempfile.TemporaryDirectory() as crashed:
            expected = ledger_fingerprint(
                self.run_sessions(Path(clean), panel, dates).capital)
            actual = ledger_fingerprint(
                self.run_sessions(Path(crashed), panel, dates, crash_on=dates[5]).capital)
            self.assertEqual(actual, expected)
            self.assertGreater(expected["fills"], 0, "the run must actually trade")

    def test_the_crash_really_left_durable_state_behind(self):
        """Guards the test itself: a crash that changed nothing proves nothing."""
        panel = fixture_panel(sessions=90)
        dates = panel.aligned_dates(UNIVERSE)[20:26]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            desk = shadow_desk(root, panel)
            for index, date in enumerate(dates[:-1]):
                desk.run_session(panel, date, dates[index + 1])
            before = desk.capital.state.fills
            original = DeskJournal.commit
            DeskJournal.commit = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("killed"))
            try:
                with self.assertRaises(RuntimeError):
                    desk.run_session(panel, dates[-1], dates[-1])
            finally:
                DeskJournal.commit = original
            reopened = shadow_desk(root, panel)
            self.assertGreater(reopened.capital.state.fills, before,
                               "the crash must land after durable fills")
            self.assertTrue(reopened.journal.pending,
                            "an interrupted session must leave a pending plan")

    def test_a_resumed_session_keeps_the_original_decision(self):
        panel = fixture_panel(sessions=90)
        dates = panel.aligned_dates(UNIVERSE)[20:30]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            desk = shadow_desk(root, panel, holding_days=5, no_trade_band=0.05)
            # Sessions 1-4 sit inside the holding period; session 5 is the next
            # rebalance, so that is where an interrupted decision matters.
            for index, date in enumerate(dates[:5]):
                desk.run_session(panel, date, dates[index + 1])
            original = DeskJournal.commit
            DeskJournal.commit = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("killed"))
            try:
                with self.assertRaises(RuntimeError):
                    desk.run_session(panel, dates[5], dates[6])
            finally:
                DeskJournal.commit = original
            resumed = shadow_desk(root, panel, holding_days=5, no_trade_band=0.05)
            self.assertTrue(resumed.journal.pending, "the crash must leave a pending plan")
            summary = resumed.run_session(panel, dates[5], dates[6])
            ticket = summary["tickets"][0]
            # Re-deciding against the already-mutated Book would have seen no
            # drift and recorded NO_TRADE. The recorded intent wins.
            self.assertEqual(ticket["status"], "BOOKED")
            self.assertEqual(ticket["book_effect"]["replayed_operations"],
                             len(ticket["fills"]))
            self.assertEqual(resumed.journal.stats_for("STR-TEST")["booked"], 2)


class DeskTimelineTests(unittest.TestCase):
    """Invariant 1, desk side: the Book is marked where the orders executed."""

    def test_the_book_is_marked_on_the_execution_date(self):
        panel = fixture_panel(sessions=90)
        dates = panel.aligned_dates(UNIVERSE)
        with tempfile.TemporaryDirectory() as directory:
            desk = shadow_desk(Path(directory), panel)
            summary = desk.run_session(panel, dates[30], dates[31])
            self.assertEqual(summary["execution_date"], dates[31])
            self.assertEqual(desk.capital.state.last_session_date, dates[31])
            for ticket in summary["tickets"]:
                for fill in ticket["fills"]:
                    self.assertEqual(fill["execution_date"], dates[31])
                    self.assertEqual(fill["signal_date"], dates[30])

    def test_marks_never_run_backward_across_sessions(self):
        panel = fixture_panel(sessions=90)
        dates = panel.aligned_dates(UNIVERSE)[20:30]
        with tempfile.TemporaryDirectory() as directory:
            desk = shadow_desk(Path(directory), panel)
            marked = []
            for index, date in enumerate(dates[:-1]):
                desk.run_session(panel, date, dates[index + 1])
                marked.append(desk.capital.state.last_session_date)
            self.assertEqual(marked, sorted(marked))
            self.assertEqual(len(set(marked)), len(marked))


class LivenessTests(unittest.TestCase):
    """Invariant 4: IDLE is a waiting state, not an exit."""

    def build_dataset(self, root: Path, sessions: int = 400) -> None:
        panel = fixture_panel(sessions=sessions)
        panel.write(root / "data" / "datasets" / "fixture.csv")
        paths = QuantPaths(root).ensure()
        registry = DatasetRegistry(paths.dataset_registry, root)
        record = DatasetRecord(dataset_id="fixture", source="synthetic test fixture",
                               adapter="fixture", path="data/datasets/fixture.csv")
        record.symbols = panel.symbols
        registry.register(record)
        registry.refresh_availability()

    def test_the_clock_waits_while_idle_instead_of_exiting(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            QuantPaths(root).ensure()
            timer = FakeTimer()
            system = QuantSystem(root, universe=UNIVERSE, dataset_id="fixture", timer=timer)
            system.boot()
            entry = system.serve(poll_seconds=30.0, max_cycles=3)
            self.assertEqual(timer.slept, [30.0, 30.0, 30.0])
            self.assertEqual(system.state.waits, 3)
            self.assertEqual(system.state.status, "IDLE")
            self.assertEqual(entry["waits"], 3)
            self.assertTrue(system.state.next_action)

    def test_data_arriving_while_idle_wakes_the_system(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            QuantPaths(root).ensure()
            timer = FakeTimer()
            system = QuantSystem(root, universe=UNIVERSE, dataset_id="fixture", timer=timer)
            system.boot()
            self.assertEqual(system.tick(), "IDLE", "blocked on a missing dataset")

            waits = {"count": 0}

            def stop_when(current: QuantSystem) -> bool:
                waits["count"] += 1
                if waits["count"] == 1:
                    self.build_dataset(root)      # data arrives while the clock waits
                    return False
                return True

            entry = system.serve(poll_seconds=5.0, stop_when=stop_when)
            self.assertTrue(timer.slept, "the clock must wait rather than exit")
            self.assertGreaterEqual(entry["outcomes"].get("RESEARCH", 0), 1,
                                    "work must resume once the dependency resolves")
            self.assertGreater(system.state.research_runs, 0)

    def test_serve_respects_an_operator_pause(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            QuantPaths(root).ensure()
            timer = FakeTimer()
            system = QuantSystem(root, universe=UNIVERSE, dataset_id="fixture", timer=timer)
            system.boot()
            system.pause("maintenance")
            system.serve(poll_seconds=1.0, max_cycles=2)
            self.assertEqual(system.state.status, "PAUSED")


class WatchdogLeaseTests(unittest.TestCase):
    """Invariant 6: RUNNING is not STUCK."""

    def system(self, root: Path, timer=None) -> QuantSystem:
        QuantPaths(root).ensure()
        return QuantSystem(root, universe=UNIVERSE, dataset_id="fixture", timer=timer)

    def test_healthy_running_work_is_not_reported_stuck(self):
        with tempfile.TemporaryDirectory() as directory:
            system = self.system(Path(directory))
            system.boot()
            task = next(iter(system.queue.tasks.values()))
            task.status = "RUNNING"
            task.started_at = Timer().now().isoformat()
            task.lease_seconds = 600
            system.queue.save()
            codes = {alert["code"] for alert in system.health()}
            self.assertNotIn("WORKER_STUCK", codes)

    def test_work_whose_lease_expired_is_reported_stuck(self):
        with tempfile.TemporaryDirectory() as directory:
            system = self.system(Path(directory))
            system.boot()
            task = next(iter(system.queue.tasks.values()))
            task.status = "RUNNING"
            task.started_at = (Timer().now() - timedelta(seconds=1_200)).isoformat()
            task.lease_seconds = 600
            system.queue.save()
            alerts = [alert for alert in system.health() if alert["code"] == "WORKER_STUCK"]
            self.assertEqual(len(alerts), 1)
            self.assertIn(task.task_id, alerts[0]["detail"])

    def test_running_work_with_no_recorded_start_is_treated_as_stale(self):
        with tempfile.TemporaryDirectory() as directory:
            system = self.system(Path(directory))
            system.boot()
            task = next(iter(system.queue.tasks.values()))
            task.status = "RUNNING"
            task.started_at = None
            system.queue.save()
            self.assertIn("WORKER_STUCK", {alert["code"] for alert in system.health()})


class VersionPreservationTests(unittest.TestCase):
    def test_a_superseded_strategy_version_stays_inspectable(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = StrategyRegistry(Path(directory) / "strategies.json")
            first = StrategyDefinition(strategy_id="S", version=1, lane="l",
                                       spec=fixture_spec(lookback_days=5).to_dict(),
                                       evidence={"validation": {"net_return": 0.1}})
            registry.upsert(first)
            second = StrategyDefinition(strategy_id="S", version=2, lane="l",
                                        spec=fixture_spec(lookback_days=21).to_dict(),
                                        evidence={"validation": {"net_return": -0.2}})
            registry.upsert(second)
            reopened = StrategyRegistry(Path(directory) / "strategies.json")
            stored = reopened.get("S")
            self.assertEqual(stored.version, 2)
            self.assertEqual(len(stored.previous_versions), 1)
            self.assertEqual(stored.previous_versions[0]["version"], 1)
            self.assertEqual(stored.previous_versions[0]["spec"]["lookback_days"], 5)
            self.assertEqual(stored.previous_versions[0]["evidence"]["validation"]["net_return"],
                             0.1)


if __name__ == "__main__":
    unittest.main()
