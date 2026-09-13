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
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.book.ledger import Ledger
from quant.clock import QuantSystem
from quant.dataplane.panel import PricePanel
from quant.dataplane.registry import DatasetRecord, DatasetRegistry
from quant.dataplane.validation import validate_panel
from quant.desk.desk import CapitalDesk
from quant.desk.execution import ExecutionModel
from quant.desk.risk import RiskLimits, evaluate as evaluate_risk
from quant.events import EventLog
from quant.factory.evaluate import falsify, required_t_statistic, summarize, walk_forward
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


def fixture_panel(sessions: int = 400, seed: float = 0.17) -> PricePanel:
    """Deterministic synthetic bars. Not market data and never presented as such."""
    rows = []
    level = {symbol: 100.0 for symbol in UNIVERSE + [BENCHMARK]}
    for index in range(sessions):
        year, remainder = 2020 + (index // 360), index % 360
        date = f"{year}-{(remainder // 30) + 1:02d}-{(remainder % 30) + 1:02d}"
        for position, symbol in enumerate(UNIVERSE + [BENCHMARK]):
            wave = math.sin((index + position * 7) * seed) * 0.01
            drift = 0.0003 if symbol == BENCHMARK else 0.0002
            level[symbol] *= 1.0 + wave + drift
            price = level[symbol]
            rows.append({"date": date, "symbol": symbol, "open": price * 0.999,
                         "high": price * 1.004, "low": price * 0.996, "close": price,
                         "adj_close": price, "volume": 5_000_000.0})
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

    def test_signal_does_not_earn_the_return_of_its_own_session(self):
        """A shock on session t must not be tradable in session t."""
        panel = fixture_panel(sessions=200)
        dates = panel.aligned_dates(UNIVERSE)
        spec = fixture_spec(lookback_days=1)
        window = panel.split({"A": 0.5, "B": 0.5}, symbols=UNIVERSE)["B"]
        rows = walk_forward(panel, spec, window, cost_bps=0.0)
        for row in rows:
            self.assertLess(row["signal_date"], row["return_date"])
            self.assertEqual(dates[dates.index(row["signal_date"]) + 1], row["return_date"])


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
            ledger.apply_fill("AAA", 100, 50.0, 5.0, "2025-01-02", "S1")
            recovered = Ledger(path)
            self.assertEqual(recovered.positions["AAA"].quantity, 100)
            self.assertAlmostEqual(recovered.state.cash, 1_000_000 - 5_000 - 5.0)

    def test_realized_pnl_on_closing_a_long_and_covering_a_short(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / "book.json", initial_capital=1_000_000)
            ledger.apply_fill("AAA", 100, 50.0, 0.0, "2025-01-02", "S1")
            ledger.apply_fill("AAA", -100, 60.0, 0.0, "2025-01-03", "S1")
            self.assertAlmostEqual(ledger.state.realized_pnl, 1_000.0)
            ledger.apply_fill("BBB", -100, 50.0, 0.0, "2025-01-03", "S1")
            ledger.apply_fill("BBB", 100, 40.0, 0.0, "2025-01-04", "S1")
            self.assertAlmostEqual(ledger.state.realized_pnl, 2_000.0)
            self.assertEqual(ledger.open_positions(), [])

    def test_bankroll_and_nav_history_survive_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "book.json"
            first = Ledger(path, initial_capital=500_000)
            first.apply_fill("AAA", 100, 50.0, 1.0, "2025-01-02", "S1")
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
            ledger.apply_fill("AAA", 10, 10.0, 1.0, "2025-01-02", "S1")
            ledger.apply_fill("BBB", 10, 10.0, 2.0, "2025-01-02", "S2")
            self.assertAlmostEqual(ledger.state.attribution["S1"]["costs"], 1.0)
            self.assertAlmostEqual(ledger.state.attribution["S2"]["costs"], 2.0)


class RiskTests(unittest.TestCase):
    def make_ledger(self, directory, **kwargs):
        return Ledger(Path(directory) / "book.json", initial_capital=1_000_000, **kwargs)

    def test_net_exposure_breach_is_vetoed(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.make_ledger(directory)
            verdict = evaluate_risk(ledger, {"AAA": 400_000.0}, RiskLimits())
            self.assertFalse(verdict["approved"])
            self.assertTrue(any("net exposure" in reason for reason in verdict["vetoes"]))

    def test_neutral_rebalance_that_closes_a_dropped_leg_is_approved(self):
        """Regression: legs targeted at zero must not be scored as retained."""
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.make_ledger(directory)
            ledger.apply_fill("CCC", 2_000, 100.0, 0.0, "2025-01-02", "S1")
            ledger.mark_to_market("2025-01-02", {"CCC": 100.0})
            target = {"AAA": 100_000.0, "BBB": -100_000.0, "CCC": 0.0}
            verdict = evaluate_risk(ledger, target, RiskLimits())
            self.assertTrue(verdict["approved"], verdict["vetoes"])
            self.assertAlmostEqual(verdict["net_ratio"], 0.0, places=6)

    def test_drawdown_throttles_then_halts(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.make_ledger(directory)
            ledger.state.peak_nav = 1_000_000
            ledger.state.cash = 880_000
            self.assertTrue(evaluate_risk(ledger, {}, RiskLimits())["throttled"])
            ledger.state.cash = 750_000
            self.assertFalse(evaluate_risk(ledger, {}, RiskLimits())["approved"])


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
                         if definition.desk.get("evaluation_track")}
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
        definition.desk["evaluation_track"] = True
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
            definition.desk.update({"evaluation_track": True, "booked": 10})
            strategies.upsert(definition)
            assessments = store.assess_rejections(strategies, ledger)
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
            definition.desk.update({"evaluation_track": True, "booked": 10})
            strategies.upsert(definition)
            self.assertEqual(store.assess_rejections(strategies, ledger)[0]["verdict"],
                             "FALSE_REJECT")

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


if __name__ == "__main__":
    unittest.main()
