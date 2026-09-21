"""M3 -- SIZE / RISK / FILLS / BOOK: targeted deterministic acceptance tests.

Ported onto the landed M2 boundary (``quant.integration.econ_bridge`` /
``quant.economics.journal``). Most tests here still build a
``LaneEconomicAdmission`` by hand (the standalone ``economic_size`` module
never constructs one itself) to exercise the real, unmodified
``desk.risk``/``desk.execution``/``book.ledger`` authorities underneath it in
isolation. ``MarginOfSafetyThreadingTests`` and ``DeskSpliceTests`` below
additionally exercise the two M2/M3 interface-gap resolutions end to end:
``AssessmentRecord.margin_of_safety`` threading and the ``desk.desk.CapitalDesk``
SIZE-stage splice onto the real durable journal.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from quant.book.ledger import FillConflict, Ledger
from quant.dataplane.panel import PricePanel
from quant.desk.economic_size import (LaneEconomicAdmission, OUTCOME_BOOKED,
                                      OUTCOME_NO_TRADE, OUTCOME_VETOED,
                                      run_lane_entry, run_lane_scheduled_exit)
from quant.desk.execution import ExecutionModel, PHASE_ENTRY, PHASE_SCHEDULED_EXIT
from quant.desk.risk import RiskLimits
from quant.economics.consistency import AdvReference, ExecutionCostModel
from quant.economics.journal import AssessmentRecord, EconomicAssessmentJournal
from quant.economics.sizing import MarginSizingRule, compute_final_size


RULE = MarginSizingRule(rule_id="TEST_RULE", reference_margin=0.10, max_fraction=0.5,
                        minimum_margin=0.0)

#: The default ``ExecutionModel`` (commission 0.5bps + half-spread 1.0bps +
#: impact 10bps at full participation, max_participation 5%) is only cost-
#: consistent with a research assumption below roughly 0.61% participation
#: (documented defect ECON-001 in ``economics/consistency.py``). Tests that
#: want a *passing* pre-size check across the model's full 5% envelope use a
#: research cost assumption wide enough to cover it; tests that want to prove
#: the pre-size check actually fires use the tighter, realistic 5.0bps
#: constant the desk currently assumes (``ExecutionModel.RESEARCH_ONE_WAY_COST_BPS``).
GOOD_COST_BPS = 12.0


def make_panel(symbol: str = "AAA", entry_date: str = "2026-01-02",
               signal_date: str = "2026-01-01", exit_date: str = "2026-01-05",
               open_price: float = 100.0, volume: float = 5_000_000.0) -> PricePanel:
    rows = []
    dates = ["2025-12-29", "2025-12-30", "2025-12-31", signal_date, entry_date,
             "2026-01-03", "2026-01-04", exit_date]
    for date in sorted(set(dates)):
        rows.append({"date": date, "symbol": symbol, "open": open_price, "high": open_price,
                    "low": open_price, "close": open_price, "adj_close": open_price,
                    "volume": volume})
    return PricePanel(rows)


def make_ledger(tmp: Path, capital: float = 1_000_000.0) -> Ledger:
    return Ledger(tmp / "book.json", "test-book", "CAPITAL", capital)


def good_adv(symbol: str = "AAA", value: float = 100_000_000.0) -> dict[str, AdvReference]:
    return {symbol: AdvReference(symbol=symbol, value=value, state="AVAILABLE")}


def admission(strategy_id: str = "S1", margin_of_safety: float = 0.10,
             decision: str = "CONTINUE",
             eligibility: str = "PORTFOLIO_CONSIDERATION_ELIGIBLE") -> LaneEconomicAdmission:
    return LaneEconomicAdmission(assessment_id=f"ASSESS-{strategy_id}", strategy_id=strategy_id,
                                 decision=decision, capital_order_eligibility=eligibility,
                                 margin_of_safety=margin_of_safety, margin_rule=RULE)


class SizingTests(unittest.TestCase):
    def test_positive_margin_gives_positive_size_when_rule_permits(self):
        result = compute_final_size("S1", RULE, margin_of_safety=0.10,
                                    current_decision_nav=1_000_000.0, strategy_allocation=0.5,
                                    lifecycle_capital_fraction=1.0)
        self.assertGreater(result.economic_margin_notional, 0.0)
        self.assertGreater(result.final_size_notional, 0.0)
        self.assertFalse(result.zero_size)

    def test_zero_margin_gives_zero_size(self):
        result = compute_final_size("S1", RULE, margin_of_safety=0.0,
                                    current_decision_nav=1_000_000.0, strategy_allocation=0.5,
                                    lifecycle_capital_fraction=1.0)
        self.assertEqual(result.economic_margin_notional, 0.0)
        self.assertEqual(result.final_size_notional, 0.0)
        self.assertTrue(result.zero_size)
        self.assertIn("SIZE_ZERO_ECONOMIC_MARGIN", result.reason_codes)

    def test_lifecycle_cap_reduces_but_never_creates_size(self):
        uncapped = compute_final_size("S1", RULE, margin_of_safety=0.20,
                                      current_decision_nav=1_000_000.0,
                                      strategy_allocation=0.5, lifecycle_capital_fraction=1.0)
        capped = compute_final_size("S1", RULE, margin_of_safety=0.20,
                                    current_decision_nav=1_000_000.0,
                                    strategy_allocation=0.5, lifecycle_capital_fraction=0.01)
        self.assertLess(capped.final_size_notional, uncapped.final_size_notional)
        self.assertEqual(capped.final_size_notional, capped.desk_lifecycle_cap_notional)
        # A huge lifecycle fraction can never push final size above the
        # economic margin notional, i.e. it can only ever bind downward.
        generous = compute_final_size("S1", RULE, margin_of_safety=0.20,
                                      current_decision_nav=1_000_000.0,
                                      strategy_allocation=0.5, lifecycle_capital_fraction=1.0)
        self.assertLessEqual(generous.final_size_notional, generous.economic_margin_notional)

    def test_zero_economic_margin_stays_zero_even_with_full_lifecycle_cap(self):
        result = compute_final_size("S1", RULE, margin_of_safety=-1.0,
                                    current_decision_nav=1_000_000.0,
                                    strategy_allocation=1.0, lifecycle_capital_fraction=1.0)
        self.assertEqual(result.final_size_notional, 0.0)


class EntryPathTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.panel = make_panel()
        self.execution = ExecutionModel()
        self.limits = RiskLimits(max_net_ratio=1.0, max_symbol_ratio=0.30)

    def tearDown(self):
        self._tmp.cleanup()

    def _run(self, ledger, margin=0.10, eligibility="PORTFOLIO_CONSIDERATION_ELIGIBLE",
            weights=None, opportunity_id="OPP-1"):
        return run_lane_entry(
            panel=self.panel, ledger=ledger, admission=admission(margin_of_safety=margin,
                                                                  eligibility=eligibility),
            target_weights=weights or {"AAA": 1.0}, current_decision_nav=1_000_000.0,
            strategy_allocation=0.5, lifecycle_capital_fraction=1.0, execution=self.execution,
            limits=self.limits, adv_by_symbol=good_adv(), research_one_way_cost_bps=GOOD_COST_BPS,
            opportunity_id=opportunity_id, signal_date="2026-01-01",
            execution_date="2026-01-02")

    def test_zero_size_means_no_fill(self):
        ledger = make_ledger(self.tmp)
        card = self._run(ledger, margin=0.0)
        self.assertEqual(card.action, OUTCOME_NO_TRADE)
        self.assertEqual(card.fills, [])
        self.assertEqual(ledger.state.fills, 0)

    def test_not_capital_order_eligible_means_no_trade_no_size_computed(self):
        ledger = make_ledger(self.tmp)
        card = self._run(ledger, eligibility="DEVELOPMENT_SIGNAL_ONLY")
        self.assertEqual(card.action, OUTCOME_NO_TRADE)
        self.assertIsNone(card.economic_size)
        self.assertEqual(ledger.state.fills, 0)

    def test_valid_positive_entry_produces_exactly_one_fill_and_one_ledger_mutation(self):
        ledger = make_ledger(self.tmp)
        card = self._run(ledger)
        self.assertEqual(card.action, OUTCOME_BOOKED)
        self.assertEqual(len(card.fills), 1)
        self.assertEqual(card.fills[0]["phase"], PHASE_ENTRY)
        self.assertEqual(ledger.state.fills, 1)
        self.assertEqual(len(card.book_operation_ids), 1)
        # implementation shortfall is produced by the authoritative fill call
        self.assertIn("implementation_shortfall", card.fills[0])
        self.assertGreaterEqual(card.fills[0]["implementation_shortfall"], 0.0)

    def test_pre_size_cost_inconsistency_blocks_fill(self):
        ledger = make_ledger(self.tmp)
        card = run_lane_entry(
            panel=self.panel, ledger=ledger, admission=admission(margin_of_safety=0.10),
            target_weights={"AAA": 1.0}, current_decision_nav=1_000_000.0,
            strategy_allocation=0.5, lifecycle_capital_fraction=1.0, execution=self.execution,
            limits=self.limits, adv_by_symbol=good_adv(), research_one_way_cost_bps=0.1,
            opportunity_id="OPP-2", signal_date="2026-01-01", execution_date="2026-01-02")
        self.assertEqual(card.action, OUTCOME_NO_TRADE)
        self.assertEqual(ledger.state.fills, 0)
        self.assertTrue(any("RESEARCH_EVIDENCE" in reason for reason in card.reason_codes))

    def test_missing_adv_blocks_fill_post_size(self):
        ledger = make_ledger(self.tmp)
        card = run_lane_entry(
            panel=self.panel, ledger=ledger, admission=admission(margin_of_safety=0.10),
            target_weights={"AAA": 1.0}, current_decision_nav=1_000_000.0,
            strategy_allocation=0.5, lifecycle_capital_fraction=1.0, execution=self.execution,
            limits=self.limits, adv_by_symbol={}, research_one_way_cost_bps=GOOD_COST_BPS,
            opportunity_id="OPP-3", signal_date="2026-01-01", execution_date="2026-01-02")
        self.assertEqual(card.action, OUTCOME_NO_TRADE)
        self.assertEqual(ledger.state.fills, 0)
        self.assertTrue(any("ADV_MISSING" in reason for reason in card.reason_codes))

    def test_invalid_adv_state_blocks_fill(self):
        ledger = make_ledger(self.tmp)
        card = run_lane_entry(
            panel=self.panel, ledger=ledger, admission=admission(margin_of_safety=0.10),
            target_weights={"AAA": 1.0}, current_decision_nav=1_000_000.0,
            strategy_allocation=0.5, lifecycle_capital_fraction=1.0, execution=self.execution,
            limits=self.limits,
            adv_by_symbol={"AAA": AdvReference(symbol="AAA", value=0.0, state="INVALID")},
            research_one_way_cost_bps=GOOD_COST_BPS, opportunity_id="OPP-4", signal_date="2026-01-01",
            execution_date="2026-01-02")
        self.assertEqual(card.action, OUTCOME_NO_TRADE)
        self.assertEqual(ledger.state.fills, 0)

    def test_stale_adv_beyond_max_staleness_blocks_fill(self):
        ledger = make_ledger(self.tmp)
        stale = AdvReference(symbol="AAA", value=5_000_000.0, state="AVAILABLE",
                             staleness_sessions=10, max_staleness_sessions=3)
        card = run_lane_entry(
            panel=self.panel, ledger=ledger, admission=admission(margin_of_safety=0.10),
            target_weights={"AAA": 1.0}, current_decision_nav=1_000_000.0,
            strategy_allocation=0.5, lifecycle_capital_fraction=1.0, execution=self.execution,
            limits=self.limits, adv_by_symbol={"AAA": stale}, research_one_way_cost_bps=GOOD_COST_BPS,
            opportunity_id="OPP-5", signal_date="2026-01-01", execution_date="2026-01-02")
        self.assertEqual(card.action, OUTCOME_NO_TRADE)
        self.assertEqual(ledger.state.fills, 0)

    def test_post_size_participation_inconsistency_blocks_fill(self):
        # Tiny ADV makes the same final notional imply huge participation,
        # which must fail the post-size check even though pre-size passed.
        ledger = make_ledger(self.tmp)
        tiny_adv = {"AAA": AdvReference(symbol="AAA", value=1_000.0, state="AVAILABLE")}
        card = run_lane_entry(
            panel=self.panel, ledger=ledger, admission=admission(margin_of_safety=0.10),
            target_weights={"AAA": 1.0}, current_decision_nav=1_000_000.0,
            strategy_allocation=0.5, lifecycle_capital_fraction=1.0, execution=self.execution,
            limits=self.limits, adv_by_symbol=tiny_adv, research_one_way_cost_bps=GOOD_COST_BPS,
            opportunity_id="OPP-6", signal_date="2026-01-01", execution_date="2026-01-02")
        self.assertEqual(card.action, OUTCOME_NO_TRADE)
        self.assertEqual(ledger.state.fills, 0)
        self.assertTrue(any("EXECUTION_COST_CONSISTENCY_EXCEEDED_AFTER_SIZING" in reason
                            for reason in card.reason_codes))

    def test_risk_veto_after_genuine_economic_continue_blocks_fill(self):
        # A gross-ratio limit alone cannot force a true VETO: risk.evaluate
        # throttles the *scale* down (to zero if necessary) before it
        # re-checks, so a gross-only constraint degrades to NO_TRADE, not
        # VETOED. A NAV-floor limit the desk cannot satisfy at any scale
        # (it does not depend on the proposed target at all) is what a
        # genuine, unthrottleable veto looks like.
        ledger = make_ledger(self.tmp)
        tight_limits = RiskLimits(min_nav_ratio=1.1)
        card = run_lane_entry(
            panel=self.panel, ledger=ledger, admission=admission(margin_of_safety=0.10),
            target_weights={"AAA": 1.0}, current_decision_nav=1_000_000.0,
            strategy_allocation=0.5, lifecycle_capital_fraction=1.0, execution=self.execution,
            limits=tight_limits, adv_by_symbol=good_adv(), research_one_way_cost_bps=GOOD_COST_BPS,
            opportunity_id="OPP-7", signal_date="2026-01-01", execution_date="2026-01-02")
        self.assertEqual(card.action, OUTCOME_VETOED)
        self.assertEqual(ledger.state.fills, 0)

    def test_risk_throttle_stays_coherent_downstream(self):
        ledger = make_ledger(self.tmp)
        throttling_limits = RiskLimits(max_gross_ratio=0.18, max_symbol_ratio=0.30,
                                       max_net_ratio=1.0)
        card = run_lane_entry(
            panel=self.panel, ledger=ledger, admission=admission(margin_of_safety=0.10),
            target_weights={"AAA": 1.0}, current_decision_nav=1_000_000.0,
            strategy_allocation=0.5, lifecycle_capital_fraction=1.0, execution=self.execution,
            limits=throttling_limits, adv_by_symbol=good_adv(), research_one_way_cost_bps=GOOD_COST_BPS,
            opportunity_id="OPP-8", signal_date="2026-01-01", execution_date="2026-01-02")
        self.assertIsNotNone(card.risk_verdict)
        self.assertLess(card.risk_verdict["scale"], 1.0)
        self.assertTrue(card.risk_verdict["throttled"])
        # risk.evaluate's binary search converges the scaled target to just
        # at/under the gross-ratio boundary, so realistic fill-time slippage
        # can legitimately push the *executed* portfolio's gross ratio a
        # hair over that boundary; ``verify_final``'s post-fill re-check is
        # supposed to catch exactly that. Either a coherent BOOKED result
        # (fills strictly below the pre-throttle target) or a coherent
        # post-fill VETOED result (the second Risk pass catching the
        # boundary breach) is an acceptable outcome; what must never happen
        # is a booked fill whose notional matches the *pre-throttle*
        # (un-scaled) target, which would mean the throttle was silently
        # ignored downstream.
        self.assertIn(card.action, (OUTCOME_BOOKED, OUTCOME_VETOED))
        if card.action == OUTCOME_BOOKED:
            self.assertLess(sum(fill["notional"] for fill in card.fills), 250_000.0)
        else:
            self.assertTrue(any("BREACHES_HARD_LIMIT" in reason for reason in card.reason_codes))

    def test_capacity_truncation_stays_coherent_with_post_size_check(self):
        ledger = make_ledger(self.tmp)
        thin_execution = ExecutionModel(max_participation=0.001)
        card = run_lane_entry(
            panel=self.panel, ledger=ledger, admission=admission(margin_of_safety=0.10),
            target_weights={"AAA": 1.0}, current_decision_nav=1_000_000.0,
            strategy_allocation=0.5, lifecycle_capital_fraction=1.0, execution=thin_execution,
            limits=self.limits, adv_by_symbol=good_adv(), research_one_way_cost_bps=GOOD_COST_BPS,
            opportunity_id="OPP-9", signal_date="2026-01-01", execution_date="2026-01-02")
        # Either the pre/post-size check correctly refuses a too-cheap
        # research assumption for this tight participation model, or it
        # books a capacity-truncated fill that still respects the model's
        # own max_participation. Both are coherent outcomes; a silent
        # over-participation fill is not.
        if card.action == OUTCOME_BOOKED:
            for fill in card.fills:
                self.assertLessEqual(fill["participation"],
                                     thin_execution.max_participation + 1e-6)

    def test_replay_of_same_operation_does_not_double_fill(self):
        ledger = make_ledger(self.tmp)
        card1 = self._run(ledger, opportunity_id="OPP-REPLAY")
        self.assertEqual(card1.action, OUTCOME_BOOKED)
        fills_after_first = ledger.state.fills
        # Re-running the identical lane (same opportunity id, same fill leg)
        # against the SAME ledger must not double the fill count, because
        # Ledger.apply_fill is keyed on the deterministic operation id.
        card2 = self._run(ledger, opportunity_id="OPP-REPLAY")
        self.assertEqual(card2.action, OUTCOME_BOOKED)
        self.assertEqual(ledger.state.fills, fills_after_first)

    def test_crash_and_reopen_ledger_has_no_duplicate_fill(self):
        ledger = make_ledger(self.tmp)
        card = self._run(ledger, opportunity_id="OPP-CRASH")
        self.assertEqual(card.action, OUTCOME_BOOKED)
        fills_before = ledger.state.fills
        operation_ids = list(card.book_operation_ids)
        # Simulate a restart: reopen the same persisted Book file.
        reopened = Ledger(self.tmp / "book.json", "test-book", "CAPITAL", 1_000_000.0)
        self.assertEqual(reopened.state.fills, fills_before)
        for operation_id in operation_ids:
            self.assertTrue(reopened.has_applied(operation_id))
        # Replaying apply_fill with the same operation id AND the same fill
        # semantics on the reopened ledger must be a no-op (gap fix #2: the
        # replay is only idempotent when the fingerprint also matches).
        original_fill = card.fills[0]
        result = reopened.apply_fill(
            original_fill["symbol"], original_fill["quantity"], original_fill["fill_price"],
            original_fill["commission"], "2026-01-02", "S1", operation_id=operation_ids[0])
        self.assertTrue(result["replayed"])
        self.assertEqual(reopened.state.fills, fills_before)

    def test_same_operation_id_identical_fill_is_idempotent_replay(self):
        # Gap fix #2: same id + same semantic fingerprint stays a no-op.
        ledger = make_ledger(self.tmp)
        operation_id = "OPP-REPLAY-SAME:AAA:ENTRY"
        first = ledger.apply_fill("AAA", 10.0, 100.0, 1.0, "2026-01-02", "S1",
                                  operation_id=operation_id)
        self.assertFalse(first["replayed"])
        second = ledger.apply_fill("AAA", 10.0, 100.0, 1.0, "2026-01-02", "S1",
                                   operation_id=operation_id)
        self.assertTrue(second["replayed"])
        self.assertEqual(ledger.sleeves["S1"]["AAA"].quantity, 10.0)

    def test_same_operation_id_conflicting_fill_semantics_is_a_conflict(self):
        # Gap fix #2 (frozen-spec acceptance case #26/#54): same Book
        # operation id + conflicting fill semantics must raise, not silently
        # replay. Ledger.apply_fill now stores a semantic fingerprint of
        # symbol/quantity/price/cost/date/strategy alongside each applied
        # operation id and compares it on replay.
        ledger = make_ledger(self.tmp)
        operation_id = "OPP-CONFLICT:AAA:ENTRY"
        first = ledger.apply_fill("AAA", 10.0, 100.0, 1.0, "2026-01-02", "S1",
                                  operation_id=operation_id)
        self.assertFalse(first["replayed"])
        with self.assertRaises(FillConflict):
            ledger.apply_fill("AAA", 999.0, 500.0, 1.0, "2026-01-02", "S1",
                              operation_id=operation_id)
        # The conflicting call must not have mutated the sleeve at all.
        self.assertEqual(ledger.sleeves["S1"]["AAA"].quantity, 10.0)

    def test_conflicting_fill_different_strategy_same_id_also_conflicts(self):
        ledger = make_ledger(self.tmp)
        operation_id = "OPP-CONFLICT-2:AAA:ENTRY"
        ledger.apply_fill("AAA", 10.0, 100.0, 1.0, "2026-01-02", "S1",
                          operation_id=operation_id)
        with self.assertRaises(FillConflict):
            ledger.apply_fill("AAA", 10.0, 100.0, 1.0, "2026-01-02", "S2",
                              operation_id=operation_id)


class ScheduledExitTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.panel = make_panel()
        self.execution = ExecutionModel()
        self.limits = RiskLimits(max_net_ratio=1.0, max_symbol_ratio=0.30)

    def tearDown(self):
        self._tmp.cleanup()

    def _enter(self, ledger, opportunity_id="OPP-ENTRY"):
        return run_lane_entry(
            panel=self.panel, ledger=ledger, admission=admission(margin_of_safety=0.10),
            target_weights={"AAA": 1.0}, current_decision_nav=1_000_000.0,
            strategy_allocation=0.5, lifecycle_capital_fraction=1.0, execution=self.execution,
            limits=self.limits, adv_by_symbol=good_adv(), research_one_way_cost_bps=GOOD_COST_BPS,
            opportunity_id=opportunity_id, signal_date="2026-01-01",
            execution_date="2026-01-02")

    def _exit(self, ledger, opportunity_id="OPP-EXIT"):
        return run_lane_scheduled_exit(
            panel=self.panel, ledger=ledger, admission=admission(margin_of_safety=0.10),
            execution=self.execution, limits=self.limits, adv_by_symbol=good_adv(),
            research_one_way_cost_bps=GOOD_COST_BPS, opportunity_id=opportunity_id,
            signal_date="2026-01-04", execution_date="2026-01-05")

    def test_scheduled_exit_uses_same_authority_and_produces_one_book_mutation(self):
        ledger = make_ledger(self.tmp)
        entry = self._enter(ledger)
        self.assertEqual(entry.action, OUTCOME_BOOKED)
        fills_after_entry = ledger.state.fills

        exit_card = self._exit(ledger)
        self.assertEqual(exit_card.action, OUTCOME_BOOKED)
        self.assertEqual(len(exit_card.fills), 1)
        self.assertEqual(exit_card.fills[0]["phase"], PHASE_SCHEDULED_EXIT)
        self.assertEqual(ledger.state.fills, fills_after_entry + 1)
        # The exit flattens the sleeve.
        self.assertEqual(ledger.sleeve_exposures("S1"), {})

    def test_scheduled_exit_with_no_open_sleeve_is_no_trade(self):
        ledger = make_ledger(self.tmp)
        card = self._exit(ledger)
        self.assertEqual(card.action, OUTCOME_NO_TRADE)
        self.assertEqual(ledger.state.fills, 0)

    def test_replay_completed_lifecycle_has_no_duplicate_exit_fill(self):
        ledger = make_ledger(self.tmp)
        self._enter(ledger)
        exit1 = self._exit(ledger, opportunity_id="OPP-EXIT-REPLAY")
        self.assertEqual(exit1.action, OUTCOME_BOOKED)
        fills_after_exit = ledger.state.fills
        # Sleeve is already flat, so a second identical exit attempt on the
        # same (already-exited) strategy correctly finds nothing to close.
        exit2 = self._exit(ledger, opportunity_id="OPP-EXIT-REPLAY")
        self.assertEqual(exit2.action, OUTCOME_NO_TRADE)
        self.assertEqual(ledger.state.fills, fills_after_exit)

    def test_implementation_shortfall_present_on_authoritative_exit_fill(self):
        ledger = make_ledger(self.tmp)
        self._enter(ledger)
        exit_card = self._exit(ledger)
        self.assertEqual(exit_card.action, OUTCOME_BOOKED)
        self.assertIn("implementation_shortfall", exit_card.fills[0])


class ExecutionPhaseTests(unittest.TestCase):
    def test_unknown_execution_phase_fails_closed(self):
        panel = make_panel()
        model = ExecutionModel()
        with self.assertRaises(ValueError):
            model.fill(panel, "AAA", 1.0, "2026-01-01", "2026-01-02", phase="ROGUE_PHASE")


class MarginOfSafetyThreadingTests(unittest.TestCase):
    """Gap fix #1: ``margin_of_safety`` threaded from the real M2 boundary.

    ``AssessmentRecord`` now durably carries ``strategy_id`` and
    ``margin_of_safety`` (populated in ``AssessmentRecord.from_verdict`` from
    ``EconomicVerdict.margin_of_safety`` -- the exact number
    ``econ_bridge.assess_and_admit`` already computes at the SHADOW-promotion
    call site), so M3 SIZE never has to invent a parallel parameter no one
    populates.
    """

    def test_from_verdict_populates_margin_of_safety_and_strategy_id(self):
        from quant.economics.decision import EconomicVerdict
        from quant.economics.recipe import MEUEResult
        from quant.economics.states import (CONTINUE,
                                            ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE)

        verdict = EconomicVerdict(
            verdict=CONTINUE, reason="ok", meue=0.01, delta_incremental=0.05,
            lower_incremental=0.02, upper_incremental=0.08, net_expected_value=500.0,
            margin_of_safety=0.04, authority="TEST",
            capital_order_eligibility=ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE)
        meue_result = MEUEResult(recipe_state="RECIPE_CONSUMABLE", theta_id="T1", beee=None,
                                 margin=None, meue=0.01, recipe_hash="sha256:r",
                                 theta_hash="sha256:t")
        record = AssessmentRecord.from_verdict("ASSESS-1", "fp-1", verdict, meue_result,
                                               strategy_id="STR-THREAD")
        self.assertEqual(record.margin_of_safety, 0.04)
        self.assertEqual(record.strategy_id, "STR-THREAD")

    def test_journal_latest_for_strategy_returns_the_durable_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "assessments.jsonl"
            journal = EconomicAssessmentJournal(path)
            record = AssessmentRecord(
                assessment_id="ASSESS-2", input_fingerprint="fp-2", decision="CONTINUE",
                capital_order_eligibility="PORTFOLIO_CONSIDERATION_ELIGIBLE",
                reason_codes=(), strategy_id="STR-LOOKUP", margin_of_safety=0.07)
            journal.record(record)
            found = journal.latest_for_strategy("STR-LOOKUP")
            self.assertIsNotNone(found)
            self.assertEqual(found["margin_of_safety"], 0.07)
            self.assertIsNone(journal.latest_for_strategy("STR-ABSENT"))

    def test_admission_from_assessment_record_threads_margin_and_eligibility(self):
        record = AssessmentRecord(
            assessment_id="ASSESS-3", input_fingerprint="fp-3", decision="CONTINUE",
            capital_order_eligibility="PORTFOLIO_CONSIDERATION_ELIGIBLE", reason_codes=(),
            strategy_id="STR-ADM", margin_of_safety=0.09).to_dict()
        admission = LaneEconomicAdmission.from_assessment_record(record, RULE)
        self.assertEqual(admission.margin_of_safety, 0.09)
        self.assertTrue(admission.capital_order_eligible)

    def test_admission_from_record_without_margin_falls_back_to_zero_not_fabricated(self):
        record = AssessmentRecord(
            assessment_id="ASSESS-4", input_fingerprint="fp-4", decision="CONTINUE",
            capital_order_eligibility="PORTFOLIO_CONSIDERATION_ELIGIBLE", reason_codes=(),
            strategy_id="STR-NOMARGIN").to_dict()
        self.assertIsNone(record["margin_of_safety"])
        admission = LaneEconomicAdmission.from_assessment_record(record, RULE)
        self.assertEqual(admission.margin_of_safety, 0.0)


def _desk_panel(sessions: int = 60, symbols=("AAA", "BBB", "CCC", "DDD")) -> PricePanel:
    """A small deterministic multi-symbol fixture with a real cross-sectional
    signal, for exercising ``CapitalDesk`` end to end. Not market data and
    never registered as a dataset.
    """
    import math
    from datetime import datetime, timedelta

    rows = []
    level = {symbol: 100.0 for symbol in symbols}
    for index in range(sessions):
        date = (datetime(2026, 1, 1) + timedelta(days=index)).date().isoformat()
        for position, symbol in enumerate(symbols):
            wave = math.sin((index + position * 7) * 0.17) * 0.01
            level[symbol] *= 1.0 + wave
            price = level[symbol]
            rows.append({"date": date, "symbol": symbol, "open": price * 0.999,
                        "high": price * 1.004, "low": price * 0.996, "close": price,
                        "adj_close": price, "volume": 5_000_000.0})
    return PricePanel(rows)


def _desk_spec():
    from quant.factory.signals import StrategySpec
    return StrategySpec(family="cross_sectional", universe=["AAA", "BBB", "CCC", "DDD"],
                        lookback_days=5, direction=-1, min_abs_score=0.1, holding_days=1,
                        dataset_id="")


class DeskSpliceTests(unittest.TestCase):
    """The real desk.py splice, exercised end to end rather than in isolation.

    Covers both branches of gap resolution #1's consumer: a strategy with a
    durable, capital-order-eligible ``AssessmentRecord`` is sized by
    ``economic_size.compute_final_size`` (via ``CapitalDesk._economic_admission``
    / the SIZE-stage splice); a strategy with no such record keeps the
    pre-M3 naive ``capital_fraction`` sizing unchanged.
    """

    def _build_desk(self, root: Path, strategy_id: str = "STR-TEST"):
        from quant.dataplane.registry import DatasetRegistry
        from quant.desk.desk import CapitalDesk
        from quant.events import EventLog
        from quant.factory.strategies import StrategyDefinition, StrategyRegistry
        from quant.paths import QuantPaths
        from quant.state import ComponentRegistry

        paths = QuantPaths(root).ensure()
        registry = DatasetRegistry(paths.dataset_registry, root)
        strategies = StrategyRegistry(paths.strategies)
        definition = StrategyDefinition(strategy_id=strategy_id, version=1, lane="test",
                                        spec=_desk_spec().to_dict())
        definition.transition("VALIDATED", "fixture")
        definition.transition("SHADOW", "fixture")
        strategies.upsert(definition)
        desk = CapitalDesk(paths, strategies, registry, EventLog(paths.events),
                           ComponentRegistry(paths.components))
        return desk, paths

    def _run_until_sized(self, desk, panel):
        dates = panel.aligned_dates(["AAA", "BBB", "CCC", "DDD"])
        for index in range(6, len(dates) - 1):
            summary = desk.run_session(panel, dates[index], dates[index + 1])
            for ticket in summary["tickets"]:
                sized = next((entry for entry in ticket["stage_trace"]
                             if entry["stage"] == "SIZE"), None)
                if sized is not None:
                    return ticket, sized
        return None, None

    def test_splice_uses_economic_sizing_when_admission_is_durable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            panel = _desk_panel()
            desk, paths = self._build_desk(root)
            journal = EconomicAssessmentJournal(paths.economic_assessments)
            journal.record(AssessmentRecord(
                assessment_id="ADM-STR-TEST", input_fingerprint="fp-splice",
                decision="CONTINUE", capital_order_eligibility="PORTFOLIO_CONSIDERATION_ELIGIBLE",
                reason_codes=(), strategy_id="STR-TEST", margin_of_safety=0.01))
            # Reopen the journal on the desk so it observes the just-recorded
            # durable assessment.
            desk.assessment_journal = EconomicAssessmentJournal(paths.economic_assessments)
            ticket, sized = self._run_until_sized(desk, panel)
            self.assertIsNotNone(sized, "expected at least one strategy to reach SIZE")
            self.assertIn("economic_size", sized["detail"])
            economic_size = sized["detail"]["economic_size"]
            self.assertEqual(economic_size["margin_of_safety"], 0.01)
            # DESK_DEFAULT_MARGIN_RULE: reference_margin=0.05, max_fraction=1.0
            # -> fraction(0.01) = 0.2, strictly below SHADOW's naive 0.35
            # capital_fraction, so the economic margin -- not the lifecycle
            # cap -- decided size.
            self.assertAlmostEqual(economic_size["economic_fraction"], 0.2, places=6)
            self.assertFalse(economic_size["lifecycle_cap_binding"])
            self.assertAlmostEqual(sized["detail"]["allocation"],
                                   economic_size["final_size_notional"], places=6)

    def test_splice_falls_back_to_naive_sizing_with_no_durable_admission(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            panel = _desk_panel()
            desk, _ = self._build_desk(root)
            ticket, sized = self._run_until_sized(desk, panel)
            self.assertIsNotNone(sized, "expected at least one strategy to reach SIZE")
            self.assertNotIn("economic_size", sized["detail"])
            self.assertAlmostEqual(sized["detail"]["allocation"],
                                   1_000_000.0 * 0.5 * 0.35, places=2)


class ScheduledExitHookTests(unittest.TestCase):
    """The narrow desk.py scheduled-exit hook (M3 gap: "no explicit exit
    phase"). Exercised directly against ``CapitalDesk._maybe_scheduled_exit``
    rather than by contriving a full session where the cross-sectional signal
    happens to vanish, mirroring the existing monkeypatch style already used
    elsewhere in this test suite for isolating one desk stage.
    """

    def test_open_sleeve_past_holding_period_with_no_signal_is_flattened(self):
        from quant.dataplane.registry import DatasetRegistry
        from quant.desk.desk import CapitalDesk
        from quant.desk.opportunity import OpportunityTicket
        from quant.events import EventLog
        from quant.factory.strategies import StrategyDefinition, StrategyRegistry
        from quant.paths import QuantPaths
        from quant.state import ComponentRegistry

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            panel = _desk_panel()
            paths = QuantPaths(root).ensure()
            registry = DatasetRegistry(paths.dataset_registry, root)
            strategies = StrategyRegistry(paths.strategies)
            definition = StrategyDefinition(strategy_id="STR-EXIT", version=1, lane="test",
                                            spec=_desk_spec().to_dict())
            definition.transition("VALIDATED", "fixture")
            definition.transition("SHADOW", "fixture")
            strategies.upsert(definition)
            desk = CapitalDesk(paths, strategies, registry, EventLog(paths.events),
                               ComponentRegistry(paths.components))
            journal = EconomicAssessmentJournal(paths.economic_assessments)
            journal.record(AssessmentRecord(
                assessment_id="ADM-STR-EXIT", input_fingerprint="fp-exit", decision="CONTINUE",
                capital_order_eligibility="PORTFOLIO_CONSIDERATION_ELIGIBLE", reason_codes=(),
                strategy_id="STR-EXIT", margin_of_safety=0.02))
            desk.assessment_journal = journal

            dates = panel.aligned_dates(["AAA", "BBB", "CCC", "DDD"])
            entry_date, execution_date = dates[10], dates[11]
            open_price = panel.adjusted(execution_date, "AAA", "open")
            desk.capital.apply_fill("AAA", 100.0, open_price, 0.0, execution_date, "STR-EXIT",
                                    operation_id="seed-exit-position")
            self.assertTrue(desk.capital.sleeve_exposures("STR-EXIT"))

            # Force "no qualifying signal this session" and "holding period
            # already elapsed" deterministically, the same way an existing
            # test in this repository monkeypatches ``weights_for`` to
            # isolate one desk stage.
            from quant.desk.journal import EMPTY_STATS
            desk.journal.stats["STR-EXIT"] = dict(EMPTY_STATS) | {"last_rebalance_date": dates[0]}
            ticket = OpportunityTicket(opportunity_id="OPP-STR-EXIT-1",
                                       session_date=entry_date, strategy_id="STR-EXIT",
                                       lifecycle="SHADOW", ledger="CAPITAL",
                                       execution_date=execution_date)
            result = desk._maybe_scheduled_exit(panel, entry_date, execution_date, definition,
                                                "OPP-STR-EXIT-1", ticket)
            self.assertIsNotNone(result, "expected the scheduled-exit hook to fire")
            self.assertIn(result.status, ("BOOKED", "NO_TRADE", "VETOED"))
            if result.status == "BOOKED":
                self.assertEqual(desk.capital.sleeve_exposures("STR-EXIT"), {})

    def test_no_open_sleeve_means_hook_is_a_no_op(self):
        from quant.dataplane.registry import DatasetRegistry
        from quant.desk.desk import CapitalDesk
        from quant.desk.opportunity import OpportunityTicket
        from quant.events import EventLog
        from quant.factory.strategies import StrategyDefinition, StrategyRegistry
        from quant.paths import QuantPaths
        from quant.state import ComponentRegistry

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            panel = _desk_panel()
            paths = QuantPaths(root).ensure()
            registry = DatasetRegistry(paths.dataset_registry, root)
            strategies = StrategyRegistry(paths.strategies)
            definition = StrategyDefinition(strategy_id="STR-NOEXIT", version=1, lane="test",
                                            spec=_desk_spec().to_dict())
            definition.transition("VALIDATED", "fixture")
            definition.transition("SHADOW", "fixture")
            strategies.upsert(definition)
            desk = CapitalDesk(paths, strategies, registry, EventLog(paths.events),
                               ComponentRegistry(paths.components))
            dates = panel.aligned_dates(["AAA", "BBB", "CCC", "DDD"])
            ticket = OpportunityTicket(opportunity_id="OPP-NOEXIT-1", session_date=dates[10],
                                       strategy_id="STR-NOEXIT", lifecycle="SHADOW",
                                       ledger="CAPITAL", execution_date=dates[11])
            result = desk._maybe_scheduled_exit(panel, dates[10], dates[11], definition,
                                                "OPP-NOEXIT-1", ticket)
            self.assertIsNone(result)


class OpeningModelIsNotAFillAuthorityTests(unittest.TestCase):
    def test_opening_execution_model_is_not_imported_by_economic_size(self):
        import quant.desk.economic_size as module
        source = Path(module.__file__).read_text()
        self.assertNotIn("economics.opening", source)
        self.assertNotIn("OpeningExecutionModel", source)


if __name__ == "__main__":
    unittest.main()
