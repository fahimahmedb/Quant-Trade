"""M4: durable Learning processed-id / payload-digest idempotence authority.

Covers the acceptance matrix from the M4 mission brief: exactly-once terminal
outcomes (NO_TRADE, VETO, BOOKED, INSUFFICIENT) surviving >200 later entries
and a restart/replay, conflicting-payload fail-closed, and
rejection-counterfactual linkage without mutating the original record.

M2 (Economic assessment persistence) and M3 (fills/Book) are assumed to exist
upstream and are not implemented here; where their exact record shape would
matter this file uses the smallest plausible stub, matching the desk/research
shapes already in the repository (``OpportunityTicket.stage_trace`` entries,
``LearningStore.record_research`` result dicts).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from quant.book.ledger import Ledger
from quant.dataplane.panel import PricePanel
from quant.desk.economic_size import (LaneEconomicAdmission, OUTCOME_BOOKED,
                                      OUTCOME_VETOED, run_lane_entry)
from quant.desk.execution import ExecutionModel
from quant.desk.opportunity import OpportunityTicket
from quant.desk.risk import RiskLimits
from quant.economics.consistency import (AdvReference, ExecutionCostModel,
                                         ResearchExecutionConsistency)
from quant.economics.decision import EffectEstimate, PortfolioInteraction
from quant.economics.journal import EconomicAssessmentJournal
from quant.economics.recipe import MEUEResult
from quant.economics.sizing import MarginSizingRule
from quant.economics.states import CLUSTERING_UNIT_O4_RESOLVED
from quant.economics.theta import Q_PROVENANCE_ALLOCATION_CONSTRUCTOR, ThetaState
from quant.factory.strategies import StrategyDefinition, StrategyRegistry
from quant.integration.econ_bridge import assess_and_admit
from quant.learning import (BOOKED, INSUFFICIENT, KILL, NO_TRADE, REJECTION_COUNTERFACTUAL,
                            RESEARCH_RESULT, RISK_VETO, LearningConflict, LearningStore)
from quant.learning.durable import ECONOMIC_ASSESSMENT, DurableOutcomeStore
from quant.paths import QuantPaths
from quant.science.effect import STRUCTURAL_INSUFFICIENT, ScientificEffectArtifact


def _outcome_payload(ticket: OpportunityTicket) -> dict:
    """The smallest semantic summary of a terminal desk ticket.

    Deliberately excludes ``created_at``/``stage_trace[*]["at"]`` wall-clock
    fields, the same way ``LearningStore._assessment_core`` strips
    ``assessed_at`` before comparing two assessments for equality: a replay
    of the identical decision must digest identically even if the replay's
    wall clock differs.
    """
    return {
        "opportunity_id": ticket.opportunity_id,
        "session_date": ticket.session_date,
        "strategy_id": ticket.strategy_id,
        "status": ticket.status,
        "stage": ticket.stage,
        "reason": ticket.reason,
        "reached": ticket.reached,
    }


def _processed_id(ticket: OpportunityTicket) -> str:
    return f"DESK:{ticket.opportunity_id}"


class DurableLearningOutcomesTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paths = QuantPaths(root=Path(self._tmp.name)).ensure()

    def _store(self) -> DurableOutcomeStore:
        return DurableOutcomeStore(self.paths.learning_outcomes)

    # --- one durable outcome per terminal status ----------------------
    def test_no_trade_produces_exactly_one_durable_outcome(self) -> None:
        ticket = OpportunityTicket(opportunity_id="OPP-1", session_date="2026-01-05",
                                   strategy_id="strat-a", lifecycle="SHADOW", ledger="CAPITAL")
        ticket.stop("SCAN", "NO_TRADE", "no symbol cleared the signal threshold")

        store = self._store()
        result = store.record(_processed_id(ticket), NO_TRADE, _outcome_payload(ticket))
        self.assertEqual(result["status"], "RECORDED")

        reloaded = DurableOutcomeStore(self.paths.learning_outcomes)
        matches = [r for r in reloaded.records if r["kind"] == NO_TRADE]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["payload"]["status"], "NO_TRADE")

    def test_risk_veto_produces_exactly_one_durable_outcome(self) -> None:
        ticket = OpportunityTicket(opportunity_id="OPP-2", session_date="2026-01-05",
                                   strategy_id="strat-a", lifecycle="SHADOW", ledger="CAPITAL")
        ticket.stop("RISK", "VETOED", "gross exposure cap breached", vetoes=["GROSS_CAP"])

        store = self._store()
        store.record(_processed_id(ticket), RISK_VETO, _outcome_payload(ticket))
        store.record(_processed_id(ticket), RISK_VETO, _outcome_payload(ticket))  # replay

        reloaded = DurableOutcomeStore(self.paths.learning_outcomes)
        matches = [r for r in reloaded.records if r["kind"] == RISK_VETO]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["payload"]["status"], "VETOED")

    def test_booked_produces_exactly_one_durable_outcome(self) -> None:
        ticket = OpportunityTicket(opportunity_id="OPP-3", session_date="2026-01-05",
                                   strategy_id="strat-a", lifecycle="SHADOW", ledger="CAPITAL")
        ticket.record("SIZE", "SIZED", "sized to target weights")
        ticket.complete("filled at open", fills=[{"symbol": "XLK", "quantity": 10.0}])

        store = self._store()
        result = store.record(_processed_id(ticket), BOOKED, _outcome_payload(ticket))
        self.assertEqual(result["status"], "RECORDED")
        replay = store.record(_processed_id(ticket), BOOKED, _outcome_payload(ticket))
        self.assertEqual(replay["status"], "NOOP")

        matches = [r for r in store.records if r["kind"] == BOOKED]
        self.assertEqual(len(matches), 1)

    def test_insufficient_produces_exactly_one_durable_outcome(self) -> None:
        # Stub of an M1/M2 science outcome: a research ticket refused for
        # want of information (STRUCTURAL_INSUFFICIENT / G < 10), not a desk
        # ticket. See src/quant/science/effect.py::STRUCTURAL_INSUFFICIENT.
        payload = {"ticket_id": "SCI-COHORT-1", "outcome": "INSUFFICIENT",
                  "reasons": ["POSITIVE_EXPOSURE_COMPONENT_COUNT_BELOW_10"]}
        store = self._store()
        store.record("SCIENCE:SCI-COHORT-1", INSUFFICIENT, payload)
        store.record("SCIENCE:SCI-COHORT-1", INSUFFICIENT, payload)  # replay, no dup

        matches = [r for r in store.records if r["kind"] == INSUFFICIENT]
        self.assertEqual(len(matches), 1)

    # --- survives >200 later entries + restart + old-id replay ---------
    def test_research_survives_200_later_lessons_and_restart_and_replay(self) -> None:
        # LearningStore.lessons is capped to the last 200 on save(); prove the
        # durable authority is not built on that structure.
        learning = LearningStore(self.paths.learning)
        durable = self._store()

        first_payload = {"ticket_id": "RSCH-0", "outcome": "VALIDATED",
                         "lesson": "lane cleared discovery"}
        first = durable.record("RESEARCH:RSCH-0", RESEARCH_RESULT, first_payload)
        self.assertEqual(first["status"], "RECORDED")

        for index in range(1, 250):
            learning.record_research(f"lane-{index}", "discovery",
                                     {"ticket_id": f"RSCH-{index}", "outcome": "REJECTED",
                                      "lesson": f"lesson {index}"})
        # The cap is applied on persistence (LearningStore.save() writes only
        # self.lessons[-200:]), so it shows up on reload from disk.
        reloaded_learning = LearningStore(self.paths.learning)
        self.assertEqual(len(reloaded_learning.lessons), 200)

        # Simulate a restart: fresh process, reload from disk.
        durable_restarted = DurableOutcomeStore(self.paths.learning_outcomes)
        self.assertTrue(durable_restarted.has("RESEARCH:RSCH-0"))

        replay = durable_restarted.record("RESEARCH:RSCH-0", RESEARCH_RESULT, first_payload)
        self.assertEqual(replay["status"], "NOOP")
        matches = [r for r in durable_restarted.records if r["processed_id"] == "RESEARCH:RSCH-0"]
        self.assertEqual(len(matches), 1)

    def test_economic_outcomes_survive_200_later_entries_and_restart_and_replay(self) -> None:
        durable = self._store()
        old_payload = {"assessment_id": "ECON-0", "outcome": "NO_TRADE",
                       "reason": "expected cost exceeded MEUE"}
        durable.record("ECON:ECON-0", NO_TRADE, old_payload)

        for index in range(1, 220):
            durable.record(f"ECON:ECON-{index}", NO_TRADE,
                           {"assessment_id": f"ECON-{index}", "outcome": "NO_TRADE",
                            "reason": "later"})
        self.assertGreater(len(durable.records), 200)

        restarted = DurableOutcomeStore(self.paths.learning_outcomes)
        self.assertEqual(len(restarted.records), len(durable.records))
        replay = restarted.record("ECON:ECON-0", NO_TRADE, old_payload)
        self.assertEqual(replay["status"], "NOOP")
        self.assertEqual(
            len([r for r in restarted.records if r["processed_id"] == "ECON:ECON-0"]), 1)

    # --- conflicting payload: fail closed -------------------------------
    def test_same_processed_id_conflicting_payload_fails_closed(self) -> None:
        store = self._store()
        store.record("DESK:OPP-9", NO_TRADE,
                     {"status": "NO_TRADE", "reason": "no signal cleared threshold"})

        with self.assertRaises(LearningConflict):
            store.record("DESK:OPP-9", BOOKED,
                         {"status": "BOOKED", "reason": "filled", "notional": 1000.0})

        # The original record must be untouched and no second record added.
        self.assertEqual(len(store.records), 1)
        self.assertEqual(store.get("DESK:OPP-9")["kind"], NO_TRADE)

        reloaded = DurableOutcomeStore(self.paths.learning_outcomes)
        self.assertEqual(len(reloaded.records), 1)
        self.assertEqual(reloaded.get("DESK:OPP-9")["kind"], NO_TRADE)

    # --- rejection counterfactual cannot mutate the original ------------
    def test_rejection_evaluation_does_not_mutate_original_decision_record(self) -> None:
        store = self._store()
        original_payload = {"status": "NO_TRADE", "strategy_id": "strat-b",
                            "reason": "risk vetoed: gross cap"}
        store.record("DESK:OPP-77", NO_TRADE, original_payload)
        original_before = store.get("DESK:OPP-77")

        # A later rejection-counterfactual evaluation gets its OWN processed
        # id and links back to the original; it must never reuse the
        # original's id to "update" it.
        evaluation_payload = {"strategy_id": "strat-b", "verdict": "FALSE_REJECT",
                              "counterfactual_pnl": 5321.12, "as_of": "2026-06-01"}
        result = store.record("REJECTION_EVAL:OPP-77:2026-06-01", REJECTION_COUNTERFACTUAL,
                              evaluation_payload, links={"decision": "DESK:OPP-77"})
        self.assertEqual(result["status"], "RECORDED")

        original_after = store.get("DESK:OPP-77")
        self.assertEqual(original_before, original_after)
        self.assertEqual(original_after["payload"], original_payload)
        self.assertEqual(len(store.records), 2)

        # A second, later evaluation is also additive, not a rewrite.
        store.record("REJECTION_EVAL:OPP-77:2026-09-01", REJECTION_COUNTERFACTUAL,
                    {**evaluation_payload, "as_of": "2026-09-01",
                     "counterfactual_pnl": 6100.0},
                    links={"decision": "DESK:OPP-77"})
        self.assertEqual(store.get("DESK:OPP-77"), original_before)

        linked = list(store.history("DESK:OPP-77"))
        # original + two linked evaluations
        self.assertEqual(len(linked), 3)
        kinds = sorted(r["kind"] for r in linked)
        self.assertEqual(kinds, sorted([NO_TRADE, REJECTION_COUNTERFACTUAL,
                                        REJECTION_COUNTERFACTUAL]))

    def test_identical_replay_is_noop_and_appends_no_duplicate(self) -> None:
        store = self._store()
        payload = {"status": "BOOKED", "notional": 500.0}
        store.record("DESK:OPP-5", BOOKED, payload)
        for _ in range(5):
            result = store.record("DESK:OPP-5", BOOKED, dict(payload))
            self.assertEqual(result["status"], "NOOP")
        self.assertEqual(len(store.records), 1)

    def test_unknown_kind_rejected(self) -> None:
        store = self._store()
        with self.assertRaises(ValueError):
            store.record("X:1", "NOT_A_REAL_KIND", {"a": 1})


# --- real end-to-end wiring: econ_bridge.assess_and_admit + economic_size ---
# (M2/M3 exist for real on this branch; these tests exercise the actual
# boundary/lane functions with ``learning=`` wired in, not just
# ``DurableOutcomeStore`` in isolation.)

def _effect_artifact(*, effect_estimate=None, reason_codes=()) -> ScientificEffectArtifact:
    return ScientificEffectArtifact(
        status="OK" if effect_estimate is not None else "REFUSED",
        reason_codes=tuple(reason_codes), protocol_id="FORM4_TEST_V1",
        protocol_hash="sha256:protocol", sample_id="SAMPLE-1", cohort_ids=("COHORT-1",),
        sample_provenance="dataset:test", allocation_constructor_id="FORM4_SLOT20_ADV20_V1",
        allocation_commitment_hashes=("sha256:a", "sha256:b"),
        component_assignments=(("EVT-1", "COMP-1"),), d19_complete=True,
        method_qualification_id="Q1", method_qualification_hash="sha256:q1",
        delta_coordinate_binding=None, delta_coordinate_hash="sha256:coord",
        evidence_label="FORWARD_CONFIRMATION" if effect_estimate is not None else "DEVELOPMENT",
        point=effect_estimate.delta_hat if effect_estimate else None,
        lower=effect_estimate.lower if effect_estimate else None,
        upper=effect_estimate.upper if effect_estimate else None,
        confidence_level=0.95, event_count=1,
        interval_method_id="WILD_CLUSTER_RADEMACHER_RATIO_V1", synthetic=False,
        effect_estimate=effect_estimate)


def _effect_estimate(delta_hat=0.05, lower=0.03, upper=0.08) -> EffectEstimate:
    return EffectEstimate(delta_hat=delta_hat, lower=lower, upper=upper, confidence_level=0.95,
                          evidence_label="FORWARD_CONFIRMATION", sample_provenance="dataset:test",
                          event_count=12, clustering_unit_provenance=CLUSTERING_UNIT_O4_RESOLVED)


def _meue_result(meue=0.02) -> MEUEResult:
    return MEUEResult(recipe_state="RECIPE_CONSUMABLE", theta_id="THETA-1", beee=None,
                      margin=None, meue=meue, recipe_hash="sha256:recipe",
                      theta_hash="sha256:theta")


def _theta() -> ThetaState:
    return ThetaState(theta_id="THETA-1", capital=10_000.0, geometry_id="G1",
                      allocation_constructor_id="FORM4_SLOT20_ADV20_V1", allocation_state_id="A1",
                      execution_policy_id="EP1", expected_deployed_exposure=5_000.0,
                      q_provenance=Q_PROVENANCE_ALLOCATION_CONSTRUCTOR,
                      evaluation_regime="ONE_CALENDAR_YEAR")


RULE = MarginSizingRule(rule_id="TEST_RULE", reference_margin=0.10, max_fraction=0.5,
                        minimum_margin=0.0)


def _lane_admission(strategy_id="S1", margin_of_safety=0.10) -> LaneEconomicAdmission:
    return LaneEconomicAdmission(assessment_id=f"ASSESS-{strategy_id}", strategy_id=strategy_id,
                                 decision="CONTINUE",
                                 capital_order_eligibility="PORTFOLIO_CONSIDERATION_ELIGIBLE",
                                 margin_of_safety=margin_of_safety, margin_rule=RULE)


def _consistency() -> ResearchExecutionConsistency:
    model = ExecutionCostModel(commission_bps=1.0, half_spread_bps=1.0,
                               impact_bps_at_full_participation=5.0, max_participation=0.05)
    return ResearchExecutionConsistency(research_one_way_cost_bps=10.0, model=model,
                                        participation_used=0.001, subject="STR-TEST")


def _panel(symbol="AAA") -> PricePanel:
    rows = []
    for date in ("2025-12-31", "2026-01-01", "2026-01-02"):
        rows.append({"date": date, "symbol": symbol, "open": 100.0, "high": 100.0,
                    "low": 100.0, "close": 100.0, "adj_close": 100.0, "volume": 5_000_000.0})
    return PricePanel(rows)


class RealEndToEndWiringTests(unittest.TestCase):
    """Exactly-one-durable-outcome, exercised through the real boundary/lane
    functions with ``learning=`` supplied, not by calling
    ``DurableOutcomeStore`` directly.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paths = QuantPaths(root=Path(self._tmp.name)).ensure()
        self.learning = DurableOutcomeStore(self.paths.learning_outcomes)

    def _seed_strategy(self, strategies: StrategyRegistry, strategy_id: str) -> None:
        definition = StrategyDefinition(strategy_id=strategy_id, version=1, lane="test", spec={})
        definition.transition("VALIDATED", "fixture")
        strategies.upsert(definition)

    def test_e2e_no_trade_produces_exactly_one_durable_outcome(self) -> None:
        journal = EconomicAssessmentJournal(self.paths.economic_assessments)
        strategies = StrategyRegistry(self.paths.strategies)
        self._seed_strategy(strategies, "STR-NOTRADE")
        # lower/upper straddle meue -> economic_gate returns NO_TRADE.
        estimate = _effect_estimate(delta_hat=0.01, lower=-0.01, upper=0.03)
        artifact = _effect_artifact(effect_estimate=estimate)
        outcome = assess_and_admit(
            journal=journal, strategies=strategies, ticket_id="TCK-NT", strategy_id="STR-NOTRADE",
            effect_artifact=artifact, meue_result=_meue_result(), theta=_theta(),
            interaction=PortfolioInteraction(overlap_fraction=0.0, residual_beta=0.0),
            learning=self.learning)
        self.assertEqual(outcome.verdict.verdict, "NO_TRADE")

        matches = [r for r in self.learning.records if r["kind"] == NO_TRADE]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["processed_id"], outcome.assessment_id)

    def test_e2e_kill_produces_exactly_one_durable_outcome(self) -> None:
        journal = EconomicAssessmentJournal(self.paths.economic_assessments)
        strategies = StrategyRegistry(self.paths.strategies)
        self._seed_strategy(strategies, "STR-KILL")
        estimate = _effect_estimate(delta_hat=0.001, lower=-0.01, upper=0.005)
        artifact = _effect_artifact(effect_estimate=estimate)
        outcome = assess_and_admit(
            journal=journal, strategies=strategies, ticket_id="TCK-KILL", strategy_id="STR-KILL",
            effect_artifact=artifact, meue_result=_meue_result(), theta=_theta(),
            interaction=PortfolioInteraction(overlap_fraction=0.0, residual_beta=0.0),
            learning=self.learning)
        self.assertEqual(outcome.verdict.verdict, "KILL")
        matches = [r for r in self.learning.records if r["kind"] == KILL]
        self.assertEqual(len(matches), 1)

    def test_e2e_insufficient_refusal_produces_exactly_one_durable_outcome(self) -> None:
        journal = EconomicAssessmentJournal(self.paths.economic_assessments)
        strategies = StrategyRegistry(self.paths.strategies)
        self._seed_strategy(strategies, "STR-INSUFF")
        # No usable effect estimate at all, with the upstream science outcome
        # STRUCTURAL_INSUFFICIENT ("INSUFFICIENT_CLUSTER_INFORMATION")
        # declared in the artifact's own reason codes -- this is the reading
        # confirmed against the real M1/M2 code: a Desk ticket never itself
        # reaches a literal INSUFFICIENT state.
        artifact = _effect_artifact(effect_estimate=None,
                                    reason_codes=(STRUCTURAL_INSUFFICIENT,))
        outcome = assess_and_admit(
            journal=journal, strategies=strategies, ticket_id="TCK-INSUFF",
            strategy_id="STR-INSUFF", effect_artifact=artifact, meue_result=_meue_result(),
            theta=_theta(),
            interaction=PortfolioInteraction(overlap_fraction=0.0, residual_beta=0.0),
            learning=self.learning)
        self.assertEqual(outcome.status, "REFUSED")
        matches = [r for r in self.learning.records if r["kind"] == INSUFFICIENT]
        self.assertEqual(len(matches), 1)
        self.assertIn(STRUCTURAL_INSUFFICIENT, matches[0]["payload"]["reason_codes"])

        # Replay: identical inputs -> NOOP, still exactly one durable record.
        assess_and_admit(
            journal=journal, strategies=strategies, ticket_id="TCK-INSUFF",
            strategy_id="STR-INSUFF", effect_artifact=artifact, meue_result=_meue_result(),
            theta=_theta(),
            interaction=PortfolioInteraction(overlap_fraction=0.0, residual_beta=0.0),
            learning=self.learning)
        matches_after = [r for r in self.learning.records if r["kind"] == INSUFFICIENT]
        self.assertEqual(len(matches_after), 1)

    def test_e2e_continue_eligible_produces_exactly_one_durable_outcome(self) -> None:
        journal = EconomicAssessmentJournal(self.paths.economic_assessments)
        strategies = StrategyRegistry(self.paths.strategies)
        self._seed_strategy(strategies, "STR-GO")
        estimate = _effect_estimate()
        artifact = _effect_artifact(effect_estimate=estimate)
        outcome = assess_and_admit(
            journal=journal, strategies=strategies, ticket_id="TCK-GO", strategy_id="STR-GO",
            effect_artifact=artifact, meue_result=_meue_result(), theta=_theta(),
            interaction=PortfolioInteraction(overlap_fraction=0.0, residual_beta=0.0),
            consistency=_consistency(), learning=self.learning)
        self.assertTrue(outcome.promoted_to_shadow)
        matches = [r for r in self.learning.records if r["kind"] == ECONOMIC_ASSESSMENT]
        self.assertEqual(len(matches), 1)

    def test_e2e_risk_veto_produces_exactly_one_durable_outcome(self) -> None:
        ledger = Ledger(self.paths.book, "test-book", "CAPITAL", 1_000_000.0)
        tight_limits = RiskLimits(min_nav_ratio=1.1)
        card = run_lane_entry(
            panel=_panel(), ledger=ledger, admission=_lane_admission(),
            target_weights={"AAA": 1.0}, current_decision_nav=1_000_000.0,
            strategy_allocation=0.5, lifecycle_capital_fraction=1.0, execution=ExecutionModel(),
            limits=tight_limits, adv_by_symbol={"AAA": AdvReference(symbol="AAA",
                                                                    value=100_000_000.0,
                                                                    state="AVAILABLE")},
            research_one_way_cost_bps=12.0, opportunity_id="OPP-VETO", signal_date="2026-01-01",
            execution_date="2026-01-02", learning=self.learning)
        self.assertEqual(card.action, OUTCOME_VETOED)
        self.assertEqual(ledger.state.fills, 0)
        matches = [r for r in self.learning.records if r["kind"] == RISK_VETO]
        self.assertEqual(len(matches), 1)

    def test_e2e_booked_produces_exactly_one_durable_outcome(self) -> None:
        ledger = Ledger(self.paths.book, "test-book", "CAPITAL", 1_000_000.0)
        card = run_lane_entry(
            panel=_panel(), ledger=ledger, admission=_lane_admission(),
            target_weights={"AAA": 1.0}, current_decision_nav=1_000_000.0,
            strategy_allocation=0.5, lifecycle_capital_fraction=1.0, execution=ExecutionModel(),
            limits=RiskLimits(max_net_ratio=1.0, max_symbol_ratio=0.30),
            adv_by_symbol={"AAA": AdvReference(symbol="AAA", value=100_000_000.0,
                                               state="AVAILABLE")},
            research_one_way_cost_bps=12.0, opportunity_id="OPP-BOOKED", signal_date="2026-01-01",
            execution_date="2026-01-02", learning=self.learning)
        self.assertEqual(card.action, OUTCOME_BOOKED)
        self.assertEqual(ledger.state.fills, 1)
        matches = [r for r in self.learning.records if r["kind"] == BOOKED]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["payload"]["book_operation_ids"], card.book_operation_ids)

        # Replay (crash + retry with the same opportunity_id) -> NOOP, still
        # exactly one durable BOOKED record and no second Ledger mutation.
        ledger2 = Ledger(self.paths.book, "test-book", "CAPITAL", 1_000_000.0)
        card2 = run_lane_entry(
            panel=_panel(), ledger=ledger2, admission=_lane_admission(),
            target_weights={"AAA": 1.0}, current_decision_nav=1_000_000.0,
            strategy_allocation=0.5, lifecycle_capital_fraction=1.0, execution=ExecutionModel(),
            limits=RiskLimits(max_net_ratio=1.0, max_symbol_ratio=0.30),
            adv_by_symbol={"AAA": AdvReference(symbol="AAA", value=100_000_000.0,
                                               state="AVAILABLE")},
            research_one_way_cost_bps=12.0, opportunity_id="OPP-BOOKED", signal_date="2026-01-01",
            execution_date="2026-01-02", learning=DurableOutcomeStore(self.paths.learning_outcomes))
        self.assertEqual(card2.action, OUTCOME_BOOKED)
        self.assertEqual(ledger2.state.fills, 1)  # replayed operation_id: no duplicate fill
        reloaded = DurableOutcomeStore(self.paths.learning_outcomes)
        matches_after = [r for r in reloaded.records if r["kind"] == BOOKED]
        self.assertEqual(len(matches_after), 1)

    def test_e2e_true_replay_survives_200_later_entries_and_restart(self) -> None:
        ledger = Ledger(self.paths.book, "test-book", "CAPITAL", 1_000_000.0)
        first = run_lane_entry(
            panel=_panel(), ledger=ledger, admission=_lane_admission(strategy_id="S-FIRST"),
            target_weights={"AAA": 1.0}, current_decision_nav=1_000_000.0,
            strategy_allocation=0.5, lifecycle_capital_fraction=1.0, execution=ExecutionModel(),
            limits=RiskLimits(max_net_ratio=1.0, max_symbol_ratio=0.30),
            adv_by_symbol={"AAA": AdvReference(symbol="AAA", value=100_000_000.0,
                                               state="AVAILABLE")},
            research_one_way_cost_bps=12.0, opportunity_id="OPP-FIRST", signal_date="2026-01-01",
            execution_date="2026-01-02", learning=self.learning)
        self.assertEqual(first.action, OUTCOME_BOOKED)

        for index in range(220):
            self.learning.record(f"FILLER:{index}", NO_TRADE,
                                 {"opportunity_id": f"FILLER-{index}", "action": "NO_TRADE"})
        self.assertGreater(len(self.learning.records), 200)

        restarted = DurableOutcomeStore(self.paths.learning_outcomes)
        # The exact processed_id ``run_lane_entry`` used is opportunity_id:phase:action.
        processed_ids = {r["processed_id"] for r in restarted.records}
        original_id = "OPP-FIRST:ENTRY:BOOKED"
        self.assertIn(original_id, processed_ids)
        matches = [r for r in restarted.records if r["processed_id"] == original_id]
        self.assertEqual(len(matches), 1)


if __name__ == "__main__":
    unittest.main()
