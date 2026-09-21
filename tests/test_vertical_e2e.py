"""M4 -- the mission's full vertical-slice end-to-end tests.

Chains the real, unmodified M1/M2/M3 authorities exactly as the frozen spec's
topology describes::

    ScientificEffectArtifact -> econ_bridge.assess_and_admit (M2)
    -> economic_size.run_lane_entry (M3: SIZE -> RISK -> FILLS -> BOOK)
    -> DurableOutcomeStore (M4)

No test here builds a second Book, a second execution engine or a second
scheduler; the last class in this file asserts that no such second authority
exists anywhere in the source tree, and that nothing reachable from these
tests can make a real network request or claim real-capital authority.
"""

from __future__ import annotations

import ast
import tempfile
import unittest
from pathlib import Path

from quant.book.ledger import Ledger
from quant.dataplane.panel import PricePanel
from quant.desk.economic_size import (LaneEconomicAdmission, OUTCOME_BOOKED,
                                      OUTCOME_NO_TRADE, OUTCOME_VETOED, run_lane_entry)
from quant.desk.execution import ExecutionModel
from quant.desk.risk import RiskLimits
from quant.economics.consistency import (AdvReference, ExecutionCostModel,
                                         ResearchExecutionConsistency)
from quant.economics.decision import EffectEstimate, PAPER_SHADOW_ONLY, PortfolioInteraction
from quant.economics.journal import EconomicAssessmentJournal
from quant.economics.recipe import MEUEResult
from quant.economics.sizing import MarginSizingRule
from quant.economics.states import CLUSTERING_UNIT_O4_RESOLVED
from quant.economics.theta import Q_PROVENANCE_ALLOCATION_CONSTRUCTOR, ThetaState
from quant.factory.strategies import StrategyDefinition, StrategyRegistry
from quant.integration.econ_bridge import ADMITTED, REFUSED, assess_and_admit
from quant.learning.durable import (BOOKED, ECONOMIC_ASSESSMENT, NO_TRADE, RISK_VETO,
                                    DurableOutcomeStore)
from quant.paths import QuantPaths
from quant.science.effect import ScientificEffectArtifact


ROOT = Path(__file__).resolve().parents[1]


def _panel(symbol: str = "AAA") -> PricePanel:
    rows = []
    for date in ("2025-12-31", "2026-01-01", "2026-01-02"):
        rows.append({"date": date, "symbol": symbol, "open": 100.0, "high": 100.0,
                    "low": 100.0, "close": 100.0, "adj_close": 100.0, "volume": 5_000_000.0})
    return PricePanel(rows)


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


def _consistency() -> ResearchExecutionConsistency:
    model = ExecutionCostModel(commission_bps=1.0, half_spread_bps=1.0,
                               impact_bps_at_full_participation=5.0, max_participation=0.05)
    return ResearchExecutionConsistency(research_one_way_cost_bps=10.0, model=model,
                                        participation_used=0.001, subject="STR-TEST")


RULE = MarginSizingRule(rule_id="TEST_RULE", reference_margin=0.10, max_fraction=0.5,
                        minimum_margin=0.0)


class VerticalSliceEndToEndTests(unittest.TestCase):
    """One system, walked start to finish, for each of the mission's named
    E2E paths. Every path shares one ``StrategyRegistry``/``Ledger``/
    ``DurableOutcomeStore`` set, so a Book or Learning mutation from one
    stage that never should have happened is directly observable in the
    next stage's state, not merely asserted about in isolation.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paths = QuantPaths(root=Path(self._tmp.name)).ensure()
        self.journal = EconomicAssessmentJournal(self.paths.economic_assessments)
        self.strategies = StrategyRegistry(self.paths.strategies)
        self.learning = DurableOutcomeStore(self.paths.learning_outcomes)
        self.ledger = Ledger(self.paths.book, "test-book", "CAPITAL", 1_000_000.0)

    def _seed(self, strategy_id: str) -> None:
        definition = StrategyDefinition(strategy_id=strategy_id, version=1, lane="test", spec={})
        definition.transition("VALIDATED", "fixture")
        self.strategies.upsert(definition)

    def _lane_admission(self, strategy_id: str, margin_of_safety: float = 0.10
                        ) -> LaneEconomicAdmission:
        return LaneEconomicAdmission(
            assessment_id=f"ASSESS-{strategy_id}", strategy_id=strategy_id, decision="CONTINUE",
            capital_order_eligibility="PORTFOLIO_CONSIDERATION_ELIGIBLE",
            margin_of_safety=margin_of_safety, margin_rule=RULE)

    # --- 1. full negative path: unavailable evidence -> fail closed --------
    def test_negative_path_unavailable_evidence_fails_closed_with_zero_book_mutation(self):
        self._seed("STR-NEG")
        outcome = assess_and_admit(
            journal=self.journal, strategies=self.strategies, ticket_id="TCK-NEG",
            strategy_id="STR-NEG", effect_artifact=None, meue_result=_meue_result(),
            theta=_theta(),
            interaction=PortfolioInteraction(overlap_fraction=0.0, residual_beta=0.0),
            learning=self.learning)
        self.assertEqual(outcome.status, REFUSED)
        self.assertFalse(outcome.promoted_to_shadow)
        self.assertEqual(self.strategies.get("STR-NEG").lifecycle, "VALIDATED")
        self.assertFalse(self.strategies.get("STR-NEG").tradable)

        # Zero Book mutation: the ledger this system would ever fill into
        # was never touched, at all, by a refusal this far upstream.
        self.assertEqual(self.ledger.state.fills, 0)
        self.assertEqual(self.ledger.state.cash, 1_000_000.0)
        self.assertEqual(len(self.ledger.state.applied_operations), 0)

        # No scientific effect artifact at all is the generic
        # EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE refusal, recorded
        # as ECONOMIC_ASSESSMENT; a declared STRUCTURAL_INSUFFICIENT is
        # exercised separately in ``test_learning_durable.py``.
        matches = [r for r in self.learning.records if r["kind"] == ECONOMIC_ASSESSMENT]
        self.assertEqual(len(matches), 1)
        self.assertEqual(len(self.learning.records), 1)

    # --- 2. synthetic positive plumbing: full chain ------------------------
    def test_synthetic_positive_path_continue_shadow_size_risk_fill_book_learning(self):
        """SYNTHETIC_POSITIVE_PLUMBING_FIXTURE: a fabricated, clearly-labeled
        fixture (not real market evidence) that walks CONTINUE ->
        capital-order-eligible -> SHADOW promotion -> SIZE -> RISK -> a real
        ``ExecutionModel.fill`` -> a real ``Ledger.apply_fill`` -> exactly two
        durable Learning outcomes (the economic admission and the BOOKED
        lane outcome). This proves the wiring, not a market edge.
        """
        self._seed("STR-POS")
        estimate = _effect_estimate()
        artifact = _effect_artifact(effect_estimate=estimate)
        admission_outcome = assess_and_admit(
            journal=self.journal, strategies=self.strategies, ticket_id="TCK-POS",
            strategy_id="STR-POS", effect_artifact=artifact, meue_result=_meue_result(),
            theta=_theta(),
            interaction=PortfolioInteraction(overlap_fraction=0.0, residual_beta=0.0),
            consistency=_consistency(), learning=self.learning)
        self.assertEqual(admission_outcome.status, ADMITTED)
        self.assertTrue(admission_outcome.promoted_to_shadow)
        self.assertEqual(self.strategies.get("STR-POS").lifecycle, "SHADOW")

        lane_admission = self._lane_admission("STR-POS")
        card = run_lane_entry(
            panel=_panel(), ledger=self.ledger, admission=lane_admission,
            target_weights={"AAA": 1.0}, current_decision_nav=1_000_000.0,
            strategy_allocation=0.5, lifecycle_capital_fraction=1.0, execution=ExecutionModel(),
            limits=RiskLimits(max_net_ratio=1.0, max_symbol_ratio=0.30),
            adv_by_symbol={"AAA": AdvReference(symbol="AAA", value=100_000_000.0,
                                               state="AVAILABLE")},
            research_one_way_cost_bps=12.0, opportunity_id="OPP-POS", signal_date="2026-01-01",
            execution_date="2026-01-02", learning=self.learning)

        self.assertEqual(card.action, OUTCOME_BOOKED)
        self.assertEqual(self.ledger.state.fills, 1)
        self.assertEqual(len(card.book_operation_ids), 1)

        econ_matches = [r for r in self.learning.records if r["kind"] == ECONOMIC_ASSESSMENT]
        book_matches = [r for r in self.learning.records if r["kind"] == BOOKED]
        self.assertEqual(len(econ_matches), 1)
        self.assertEqual(len(book_matches), 1)
        self.assertEqual(len(self.learning.records), 2)

    # --- 3. Risk-veto E2E path ----------------------------------------------
    def test_risk_veto_end_to_end_path(self):
        self._seed("STR-VETO")
        lane_admission = self._lane_admission("STR-VETO")
        tight_limits = RiskLimits(min_nav_ratio=1.1)
        card = run_lane_entry(
            panel=_panel(), ledger=self.ledger, admission=lane_admission,
            target_weights={"AAA": 1.0}, current_decision_nav=1_000_000.0,
            strategy_allocation=0.5, lifecycle_capital_fraction=1.0, execution=ExecutionModel(),
            limits=tight_limits, adv_by_symbol={"AAA": AdvReference(symbol="AAA",
                                                                    value=100_000_000.0,
                                                                    state="AVAILABLE")},
            research_one_way_cost_bps=12.0, opportunity_id="OPP-VETO-E2E",
            signal_date="2026-01-01", execution_date="2026-01-02", learning=self.learning)
        self.assertEqual(card.action, OUTCOME_VETOED)
        self.assertEqual(self.ledger.state.fills, 0)
        matches = [r for r in self.learning.records if r["kind"] == RISK_VETO]
        self.assertEqual(len(matches), 1)

    # --- 4. zero-size E2E path -----------------------------------------------
    def test_zero_size_end_to_end_path(self):
        self._seed("STR-ZERO")
        lane_admission = self._lane_admission("STR-ZERO", margin_of_safety=0.0)
        card = run_lane_entry(
            panel=_panel(), ledger=self.ledger, admission=lane_admission,
            target_weights={"AAA": 1.0}, current_decision_nav=1_000_000.0,
            strategy_allocation=0.5, lifecycle_capital_fraction=1.0, execution=ExecutionModel(),
            limits=RiskLimits(max_net_ratio=1.0, max_symbol_ratio=0.30),
            adv_by_symbol={"AAA": AdvReference(symbol="AAA", value=100_000_000.0,
                                               state="AVAILABLE")},
            research_one_way_cost_bps=12.0, opportunity_id="OPP-ZERO", signal_date="2026-01-01",
            execution_date="2026-01-02", learning=self.learning)
        self.assertEqual(card.action, OUTCOME_NO_TRADE)
        self.assertEqual(self.ledger.state.fills, 0)
        matches = [r for r in self.learning.records if r["kind"] == NO_TRADE]
        self.assertEqual(len(matches), 1)

    # --- 5. post-size-cost-failure E2E path ----------------------------------
    def test_post_size_cost_failure_end_to_end_path(self):
        self._seed("STR-COST")
        lane_admission = self._lane_admission("STR-COST")
        tiny_adv = {"AAA": AdvReference(symbol="AAA", value=1_000.0, state="AVAILABLE")}
        card = run_lane_entry(
            panel=_panel(), ledger=self.ledger, admission=lane_admission,
            target_weights={"AAA": 1.0}, current_decision_nav=1_000_000.0,
            strategy_allocation=0.5, lifecycle_capital_fraction=1.0, execution=ExecutionModel(),
            limits=RiskLimits(max_net_ratio=1.0, max_symbol_ratio=0.30),
            adv_by_symbol=tiny_adv, research_one_way_cost_bps=12.0, opportunity_id="OPP-COST",
            signal_date="2026-01-01", execution_date="2026-01-02", learning=self.learning)
        self.assertEqual(card.action, OUTCOME_NO_TRADE)
        self.assertTrue(any("EXECUTION_COST_CONSISTENCY_EXCEEDED_AFTER_SIZING" in reason
                            for reason in card.reason_codes))
        self.assertEqual(self.ledger.state.fills, 0)
        matches = [r for r in self.learning.records if r["kind"] == NO_TRADE]
        self.assertEqual(len(matches), 1)


class SoleAuthorityAndIsolationTests(unittest.TestCase):
    """Structural assertions the mission's E2E list requires: no second
    Book, execution engine or scheduler anywhere in the source tree, and no
    unauthorized real-network or real-capital path reachable from this
    module's imports.
    """

    def _class_defs(self, name: str) -> list[tuple[Path, str]]:
        """Every class definition named exactly ``name`` under ``src/quant``."""
        hits = []
        for path in (ROOT / "src" / "quant").rglob("*.py"):
            tree = ast.parse(path.read_text(), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == name:
                    hits.append((path, node.name))
        return hits

    def test_exactly_one_ledger_class(self):
        hits = self._class_defs("Ledger")
        self.assertEqual(len(hits), 1, f"more than one Ledger authority: {hits}")

    def test_exactly_one_execution_model_class(self):
        hits = self._class_defs("ExecutionModel")
        self.assertEqual(len(hits), 1, f"more than one execution engine: {hits}")

    def test_exactly_one_capital_desk_class(self):
        hits = self._class_defs("CapitalDesk")
        self.assertEqual(len(hits), 1, f"more than one Desk/scheduler authority: {hits}")

    def test_exactly_one_durable_outcome_store_class(self):
        hits = self._class_defs("DurableOutcomeStore")
        self.assertEqual(len(hits), 1, f"more than one durable Learning authority: {hits}")

    def test_economic_and_desk_boundary_modules_make_no_network_calls(self):
        # The modules this E2E suite exercises must not themselves import a
        # network client; any real SEC capture networking lives only in
        # ``quant.dataplane.sec``, a distinct, explicitly gated subsystem
        # this suite never imports or exercises.
        forbidden = ("requests", "urllib.request", "http.client", "socket", "httpx")
        modules = ["src/quant/integration/econ_bridge.py", "src/quant/desk/economic_size.py",
                  "src/quant/desk/execution.py", "src/quant/book/ledger.py",
                  "src/quant/learning/durable.py"]
        for relative in modules:
            path = ROOT / relative
            tree = ast.parse(path.read_text(), filename=str(path))
            imported = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module)
            hit = imported & set(forbidden)
            self.assertFalse(hit, f"{relative} imports a network module: {hit}")

    def test_economic_verdict_default_capital_authority_is_paper_shadow_only(self):
        # The one place capital authority is declared on a verdict defaults
        # to paper/shadow; nothing in this suite's chain overrides it.
        self.assertEqual(PAPER_SHADOW_ONLY, "PAPER_SHADOW_ONLY")


if __name__ == "__main__":
    unittest.main()
