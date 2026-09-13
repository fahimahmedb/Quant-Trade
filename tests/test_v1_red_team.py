"""Independent V1 red-team regressions.

These tests encode causal, persistence and data-integrity invariants from the
independent reviewer mandate.  They are intentionally adversarial: every test
below was added because the reviewer could construct a concrete failure, not to
increase coverage cosmetically.
"""

from __future__ import annotations

import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quant.book.ledger import Ledger
from quant.clock import QuantSystem
from quant.dataplane.panel import PricePanel
from quant.dataplane.registry import (DatasetRecord, DatasetRegistry,
                                      fingerprint_file)
from quant.dataplane.validation import validate_panel
from quant.desk.risk import RiskLimits, verify_final
from quant.factory.strategies import StrategyDefinition, StrategyRegistry
from quant.learning.store import LearningStore
from quant.paths import QuantPaths
from quant.state import read_jsonl

from test_quant_system import (BENCHMARK, UNIVERSE, fixture_panel, fixture_spec,
                               session_date, shadow_desk)


def register_fixture(root: Path, sessions: int = 400) -> PricePanel:
    """Write/validate a deterministic test panel while preserving live var state."""
    panel = fixture_panel(sessions=sessions)
    target = root / "data" / "datasets" / "fixture.csv"
    panel.write(target)
    paths = QuantPaths(root).ensure()
    registry = DatasetRegistry(paths.dataset_registry, root)
    record = DatasetRecord(dataset_id="fixture", source="synthetic test fixture",
                           adapter="fixture", path="data/datasets/fixture.csv",
                           symbols=list(panel.symbols))
    registry.register(record)
    registry.refresh_availability()
    return panel


def research_system(root: Path) -> QuantSystem:
    return QuantSystem(root, universe=UNIVERSE, dataset_id="fixture")


def run_research_only(system: QuantSystem) -> None:
    """Run every currently due research task but stop before the first desk session."""
    for _ in range(10):
        if system.queue.next_due() is None:
            return
        outcome = system.tick()
        if outcome != "RESEARCH":
            return
    raise AssertionError("research did not quiesce")


class DecisionTimeCausalityTests(unittest.TestCase):
    def _desk_with_matching_position(self, root: Path, panel: PricePanel,
                                     decision_date: str, prior_date: str):
        desk = shadow_desk(root, panel, holding_days=1, no_trade_band=0.05)
        definition = desk.strategies.get("STR-TEST")
        decision_prices = {symbol: panel.adjusted(decision_date, symbol, "close")
                           for symbol in UNIVERSE}
        base = desk.capital.nav_at(decision_prices) * definition.capital_fraction * desk.strategy_allocation
        target = {"AAA": 0.20, "BBB": -0.20}
        for symbol, weight in target.items():
            price = decision_prices[symbol]
            desk.capital.apply_fill(symbol, base * weight / price, price, 0.0, prior_date,
                                    definition.strategy_id, f"seed-{symbol}")
        desk.journal.commit("seed-rebalance", definition.strategy_id, "BOOKED",
                            prior_date, True)
        return desk, target

    def test_open_gap_cannot_change_vet_or_size_intent(self):
        """open(t+1) is execution information, never a close(t) decision input."""
        baseline = fixture_panel(sessions=320)
        dates = baseline.aligned_dates(UNIVERSE)
        decision_date, next_date, prior_date = dates[80], dates[81], dates[78]

        altered_rows = []
        for (date, symbol), bar in baseline.bars.items():
            row = {"date": date, "symbol": symbol, **bar}
            if date == next_date and symbol == "AAA":
                row["open"] = bar["open"] * 8.0
                row["high"] = max(row["high"], row["open"])
            altered_rows.append(row)
        gapped = PricePanel(altered_rows)

        tickets = []
        allocations = []
        for panel in (baseline, gapped):
            with tempfile.TemporaryDirectory() as directory:
                desk, target = self._desk_with_matching_position(
                    Path(directory), panel, decision_date, prior_date)
                with patch("quant.desk.desk.weights_for", return_value=target):
                    summary = desk.run_session(panel, decision_date, next_date)
                ticket = summary["tickets"][0]
                tickets.append((ticket["status"], ticket["stage"], ticket["stage_trace"]))
                size = next((entry for entry in ticket["stage_trace"]
                             if entry["stage"] == "SIZE"), None)
                allocations.append(None if size is None else size["detail"]["allocation"])

        self.assertEqual(tickets[0], tickets[1],
                         "an unknown next-open gap changed the close-time decision")
        self.assertEqual(allocations[0], allocations[1],
                         "an unknown next-open gap changed close-time sizing")
        self.assertEqual(tickets[0][0], "NO_TRADE")


class FrozenResearchTests(unittest.TestCase):
    def test_append_extends_shadow_without_recycling_frozen_research(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            register_fixture(root, 400)
            system = research_system(root)
            system.boot()
            run_research_only(system)

            runs = system.state.research_runs
            lessons = len(system.learning.lessons)
            trials = dict(system.strategies.trials)
            versions = {key: value.version for key, value in system.strategies.strategies.items()}
            shadow_start = system.shadow_window().start
            old_shadow_end = system.shadow_window().end

            register_fixture(root, 430)  # append-only: the frozen cohort bytes are unchanged
            resumed = research_system(root)
            resumed.boot()

            self.assertEqual(resumed.state.research_runs, runs)
            self.assertEqual(len(resumed.learning.lessons), lessons)
            self.assertEqual(resumed.strategies.trials, trials)
            self.assertEqual({key: value.version for key, value in resumed.strategies.strategies.items()},
                             versions)
            self.assertFalse(any(task.status == "PENDING" and task.worker == "research_lane"
                                 for task in resumed.queue.tasks.values()),
                             "append-only shadow data bought a fresh historical experiment")
            self.assertEqual(resumed.shadow_window().start, shadow_start,
                             "the frozen validation boundary moved after an append")
            self.assertGreater(resumed.shadow_window().end, old_shadow_end,
                               "new bars should extend forward shadow evidence")

    def test_historical_rewrite_blocks_lineage_instead_of_buying_an_experiment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            panel = register_fixture(root, 400)
            system = research_system(root)
            system.boot()
            run_research_only(system)
            runs = system.state.research_runs
            trials = dict(system.strategies.trials)
            lessons = len(system.learning.lessons)

            # Rewrite one bar well inside the frozen research cohort.
            target_date = panel.aligned_dates(UNIVERSE)[50]
            rows = []
            for (date, symbol), bar in panel.bars.items():
                row = {"date": date, "symbol": symbol, **bar}
                if date == target_date and symbol == "AAA":
                    row["close"] *= 1.02
                    row["adj_close"] *= 1.02
                    row["high"] = max(row["high"], row["close"])
                rows.append(row)
            rewritten = PricePanel(rows)
            rewritten.write(root / "data" / "datasets" / "fixture.csv")
            registry = DatasetRegistry(QuantPaths(root).ensure().dataset_registry, root)
            registry.refresh_availability()

            resumed = research_system(root)
            resumed.boot()
            research_tasks = [task for task in resumed.queue.tasks.values()
                              if task.worker == "research_lane"]
            self.assertTrue(research_tasks)
            self.assertTrue(all(task.status == "BLOCKED" for task in research_tasks),
                            "a frozen-cohort rewrite must be a durable review boundary")
            self.assertEqual(resumed.state.research_runs, runs)
            self.assertEqual(resumed.strategies.trials, trials)
            self.assertEqual(len(resumed.learning.lessons), lessons)


class ResearchTransactionTests(unittest.TestCase):
    def test_crash_after_research_persistence_replays_without_duplicate_science(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            register_fixture(root, 400)
            system = research_system(root)
            system.boot()
            task = system.queue.next_due()
            self.assertIsNotNone(task)

            original = LearningStore.record_research
            with patch.object(LearningStore, "record_research",
                              side_effect=RuntimeError("killed after research persistence")):
                with self.assertRaises(RuntimeError):
                    system.tick()

            # run_lane has already persisted scientific output; the control transaction has not.
            self.assertTrue(StrategyRegistry(QuantPaths(root).strategies).strategies)

            resumed = research_system(root)
            boot = resumed.boot()
            self.assertIn(task.task_id, boot["recovered"],
                          "the incomplete research transaction became falsely terminal")
            self.assertEqual(resumed.tick(), "RESEARCH")

            memory = list(read_jsonl(QuantPaths(root).research_memory))
            ticket_ids = [row["ticket_id"] for row in memory]
            self.assertEqual(len(ticket_ids), len(set(ticket_ids)),
                             "crash/retry duplicated research memory")
            self.assertTrue(all(definition.version == 1
                                for definition in resumed.strategies.strategies.values()),
                            "crash/retry manufactured a new strategy version")
            research_lessons = [row for row in resumed.learning.lessons
                                if row.get("source") == "RESEARCH"]
            self.assertEqual(len(research_lessons), len({row["ticket_id"]
                                                         for row in research_lessons}))
            self.assertEqual(resumed.state.research_runs, 1)
            LearningStore.record_research = original


class FinalRiskBasisTests(unittest.TestCase):
    def test_final_risk_values_old_and_new_quantity_on_one_price_vector(self):
        panel = fixture_panel(sessions=320)
        dates = panel.aligned_dates(UNIVERSE)
        decision_date, next_date = dates[80], dates[81]
        with tempfile.TemporaryDirectory() as directory:
            desk = shadow_desk(Path(directory), panel, holding_days=1, no_trade_band=0.0)
            definition = desk.strategies.get("STR-TEST")
            open_price = panel.adjusted(next_date, "AAA", "open")
            desk.capital.apply_fill("AAA", 500.0, open_price, 0.0, dates[79],
                                    definition.strategy_id, "seed")
            captured = {}
            from quant.desk import desk as desk_module
            original = desk_module.verify_final

            def checking(ledger, strategy_id, executed_notional, limits, prices=None, **kwargs):
                captured["executed"] = dict(executed_notional)
                captured["prices"] = dict(prices or {})
                captured["before_quantities"] = {
                    symbol: position.quantity
                    for symbol, position in ledger.sleeves.get(strategy_id, {}).items()
                    if position.quantity}
                verdict = original(ledger, strategy_id, executed_notional, limits, prices, **kwargs)
                captured["verdict"] = verdict
                return verdict

            target = {"AAA": 0.20, "BBB": -0.20}
            with patch("quant.desk.desk.weights_for", return_value=target), \
                    patch("quant.desk.desk.verify_final", side_effect=checking):
                summary = desk.run_session(panel, decision_date, next_date)
            ticket = summary["tickets"][0]
            self.assertTrue(ticket["fills"], "fixture must actually execute")
            deltas = {}
            for fill in ticket["fills"]:
                deltas[fill["symbol"]] = deltas.get(fill["symbol"], 0.0) + fill["quantity"]
            symbols = set(captured["before_quantities"]) | set(deltas)
            expected = {}
            for symbol in symbols:
                quantity = captured["before_quantities"].get(symbol, 0.0) + deltas.get(symbol, 0.0)
                if abs(quantity) > 1e-9:
                    expected[symbol] = quantity * captured["prices"][symbol]
            self.assertEqual(set(captured["executed"]), set(expected))
            for symbol, value in expected.items():
                self.assertAlmostEqual(captured["executed"][symbol], value, places=6,
                                       msg=f"{symbol} mixed open and fill price bases")

    def test_final_risk_nav_includes_fill_commissions(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / "book.json", initial_capital=1_000_000)
            ledger.state.cash = 500_001.0
            limits = RiskLimits(min_nav_ratio=0.50, max_net_ratio=1.0,
                                max_gross_ratio=5.0, max_symbol_ratio=1.0)
            self.assertTrue(verify_final(ledger, "S", {}, limits)["approved"])
            charged = verify_final(ledger, "S", {}, limits, nav_adjustment=-2.0)
            self.assertFalse(charged["approved"],
                             "final risk ignored commissions that the Book will deduct")
            self.assertAlmostEqual(charged["nav"], 499_999.0)


class ForwardDeskTests(unittest.TestCase):
    def test_last_close_is_not_consumed_until_an_execution_session_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            panel = register_fixture(root, 400)
            system = research_system(root)
            system.boot()
            system.run()
            dates = [date for date in panel.aligned_dates(UNIVERSE)
                     if system.shadow_window().contains(date)]
            self.assertGreater(len(dates), 2)
            self.assertEqual(system.state.desk_cursor, dates[-2])
            self.assertEqual(system.desk.capital.state.last_session_date, dates[-1])
            blocked_last = [row for row in read_jsonl(system.paths.opportunities)
                            if row["status"] == "BLOCKED"
                            and "no later session" in row.get("reason", "")]
            self.assertFalse(blocked_last,
                             "the terminal close was permanently consumed as a blocked decision")

            prior_last = dates[-1]
            register_fixture(root, 401)
            resumed = research_system(root)
            resumed.boot()
            next_session = resumed._next_desk_session()
            self.assertIsNotNone(next_session)
            self.assertEqual(next_session[0], prior_last,
                             "the previously terminal close was skipped after new data arrived")
            self.assertEqual(resumed.tick(), "SESSION")
            self.assertEqual(resumed.state.desk_cursor, prior_last)


class DataPlaneAdversarialTests(unittest.TestCase):
    def test_registry_cannot_trust_stale_validation_that_matches_new_fingerprint(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            register_fixture(root, 300)
            paths = QuantPaths(root).ensure()
            live = DatasetRegistry(paths.dataset_registry, root)

            target = root / "data" / "datasets" / "fixture.csv"
            target.write_text("date,symbol,open,high,low,close,adj_close,volume\nBROKEN\n",
                              encoding="utf-8")
            forged = DatasetRecord(dataset_id="fixture", source="synthetic test fixture",
                                   adapter="fixture", path="data/datasets/fixture.csv",
                                   symbols=list(UNIVERSE) + [BENCHMARK],
                                   fingerprint=fingerprint_file(target), availability="AVAILABLE",
                                   validation={"passed": True, "problems": [], "warnings": []})
            DatasetRegistry(paths.dataset_registry, root).register(forged)

            live.reload()
            live.refresh_availability()
            self.assertEqual(live.get("fixture").availability, "INVALID",
                             "matching fresh bytes to stale registry metadata bypassed validation")

    def test_symbol_missing_from_latest_session_is_invalid_not_merely_a_warning(self):
        panel = fixture_panel(sessions=300)
        last = panel.dates[-1]
        rows = [{"date": date, "symbol": symbol, **bar}
                for (date, symbol), bar in panel.bars.items()
                if not (date == last and symbol == "BBB")]
        verdict = validate_panel(PricePanel(rows), UNIVERSE)
        self.assertFalse(verdict["passed"])
        self.assertTrue(any("latest" in problem for problem in verdict["problems"]))

    def test_duplicate_and_nonfinite_bars_cannot_become_available(self):
        panel = fixture_panel(sessions=300)
        rows = [{"date": date, "symbol": symbol, **bar}
                for (date, symbol), bar in panel.bars.items()]
        duplicate = dict(rows[0])
        duplicate["close"] *= 1.01
        duplicate["adj_close"] *= 1.01
        duplicate["high"] = max(duplicate["high"], duplicate["close"])
        duplicate_panel = PricePanel(rows + [duplicate])
        self.assertFalse(validate_panel(duplicate_panel, UNIVERSE)["passed"])

        bad = [dict(row) for row in rows]
        bad[10]["adj_close"] = math.nan
        self.assertFalse(validate_panel(PricePanel(bad), UNIVERSE)["passed"])


class LearningRefreshTests(unittest.TestCase):
    def test_decision_quality_updates_on_new_evidence_but_not_identical_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            system = research_system(root)
            definition = StrategyDefinition("REJECTED", 1, "test", fixture_spec().to_dict())
            definition.evaluation_track = True
            system.strategies.upsert(definition)
            ledger = system.desk.evaluation
            ledger.apply_fill("AAA", 100.0, 100.0, 0.0, "2025-01-02",
                              definition.strategy_id, "seed")
            ledger.mark_to_market("2025-01-02", {"AAA": 100.0})
            system.desk.journal.commit("opp", definition.strategy_id, "BOOKED",
                                       "2025-01-02", True)
            system.state.desk_sessions = 1

            self.assertTrue(system._assess_decision_quality())
            first = system.learning.decision_quality["counterfactual_pnl"]
            ledger.mark_to_market("2025-01-03", {"AAA": 200.0})
            self.assertTrue(system._assess_decision_quality(),
                            "new forward P&L did not refresh rejection quality")
            second = system.learning.decision_quality["counterfactual_pnl"]
            self.assertNotEqual(first, second)
            self.assertFalse(system._assess_decision_quality(),
                             "identical evidence self-reinforced the learning state")


if __name__ == "__main__":
    unittest.main()
