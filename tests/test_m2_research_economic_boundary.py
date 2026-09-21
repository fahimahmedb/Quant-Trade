"""M2: the Research -> Economic admission boundary.

Covers the frozen topology's explicit pre-Desk gate
(``governance/BLUE_FIRST_VERTICAL_ONE_BIG_BUILD_FROZEN_SPEC_2026-09-21.md``
section 4/5): research validation alone never promotes to SHADOW, the
boundary reports distinct fail-closed refusal reasons rather than a generic
NO_TRADE, and every assessment is idempotent-by-id and conflict-detecting.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from quant.economics.consistency import ExecutionCostModel, ResearchExecutionConsistency
from quant.economics.decision import EffectEstimate, PortfolioInteraction
from quant.economics.journal import AssessmentConflict, EconomicAssessmentJournal
from quant.economics.recipe import MEUEResult
from quant.economics.states import (
    CLUSTERING_UNIT_O4_RESOLVED,
    DELTA_COORDINATE_MISMATCH,
    DELTA_COORDINATE_UNRESOLVED,
    ORDER_ELIGIBILITY_DEVELOPMENT_SIGNAL_ONLY,
    ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE,
)
from quant.economics.theta import Q_PROVENANCE_ALLOCATION_CONSTRUCTOR, ThetaState
from quant.factory.strategies import StrategyDefinition, StrategyRegistry
from quant.integration import forward_adapter
from quant.integration.econ_bridge import ADMITTED, REFUSED, assess_and_admit
from quant.science.effect import EFFECT_UNAVAILABLE, ScientificEffectArtifact


def _artifact(*, status="OK", reason_codes=(), effect_estimate=None,
             sample_id="SAMPLE-1", protocol_hash="sha256:protocol",
             allocation_commitment_hashes=("sha256:b", "sha256:a"),
             delta_coordinate_hash="sha256:coord") -> ScientificEffectArtifact:
    return ScientificEffectArtifact(
        status=status, reason_codes=tuple(reason_codes), protocol_id="FORM4_TEST_V1",
        protocol_hash=protocol_hash, sample_id=sample_id, cohort_ids=("COHORT-1",),
        sample_provenance="dataset:test", allocation_constructor_id="FORM4_SLOT20_ADV20_V1",
        allocation_commitment_hashes=tuple(allocation_commitment_hashes),
        component_assignments=(("EVT-1", "COMP-1"),), d19_complete=True,
        method_qualification_id="Q1", method_qualification_hash="sha256:q1",
        delta_coordinate_binding=None, delta_coordinate_hash=delta_coordinate_hash,
        evidence_label="FORWARD_CONFIRMATION" if effect_estimate is not None else "DEVELOPMENT",
        point=effect_estimate.delta_hat if effect_estimate else None,
        lower=effect_estimate.lower if effect_estimate else None,
        upper=effect_estimate.upper if effect_estimate else None,
        confidence_level=0.95, event_count=1, interval_method_id="WILD_CLUSTER_RADEMACHER_RATIO_V1",
        synthetic=False, effect_estimate=effect_estimate)


def _effect_estimate(delta_hat=0.05, lower=0.02, upper=0.08,
                     clustering_unit_provenance=CLUSTERING_UNIT_O4_RESOLVED) -> EffectEstimate:
    return EffectEstimate(
        delta_hat=delta_hat, lower=lower, upper=upper, confidence_level=0.95,
        evidence_label="FORWARD_CONFIRMATION", sample_provenance="dataset:test",
        event_count=12, clustering_unit_provenance=clustering_unit_provenance)


def _meue_result(recipe_state="RECIPE_CONSUMABLE", meue=0.01) -> MEUEResult:
    return MEUEResult(recipe_state=recipe_state, theta_id="THETA-1", beee=None, margin=None,
                      meue=meue, recipe_hash="sha256:recipe", theta_hash="sha256:theta")


def _theta(capital=10_000.0, exposure=5_000.0) -> ThetaState:
    return ThetaState(theta_id="THETA-1", capital=capital, geometry_id="G1",
                      allocation_constructor_id="FORM4_SLOT20_ADV20_V1",
                      allocation_state_id="A1", execution_policy_id="EP1",
                      expected_deployed_exposure=exposure,
                      q_provenance=Q_PROVENANCE_ALLOCATION_CONSTRUCTOR,
                      evaluation_regime="ONE_CALENDAR_YEAR")


def _interaction(overlap=0.0) -> PortfolioInteraction:
    return PortfolioInteraction(overlap_fraction=overlap, residual_beta=0.0)


def _consistency() -> ResearchExecutionConsistency:
    model = ExecutionCostModel(commission_bps=1.0, half_spread_bps=1.0,
                               impact_bps_at_full_participation=5.0, max_participation=0.05)
    return ResearchExecutionConsistency(research_one_way_cost_bps=10.0, model=model,
                                        participation_used=0.001, subject="STR-TEST")


class ResearchAloneNeverActionable(unittest.TestCase):
    """Research VALIDATED alone must never become Desk-actionable."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "strategies.json"

    def test_validated_alone_is_not_actionable(self):
        registry = StrategyRegistry(self.path)
        definition = StrategyDefinition(strategy_id="STR-A", version=1, lane="test", spec={})
        definition.transition("VALIDATED", "fixture")
        registry.upsert(definition)
        self.assertFalse(definition.tradable)
        self.assertFalse(definition.evaluation_track)

    def test_research_completion_no_longer_auto_promotes_shadow(self):
        """A full research run must never leave any strategy at SHADOW."""
        from test_v1_red_team import register_fixture, research_system, run_research_only

        root = Path(self.tmp.name) / "system"
        register_fixture(root, 400)
        system = research_system(root)
        system.boot()
        run_research_only(system)

        self.assertTrue(system.strategies.strategies, "the research run produced no strategy")
        for definition in system.strategies.strategies.values():
            self.assertNotEqual(definition.lifecycle, "SHADOW",
                                "research completion must not auto-promote to SHADOW")
            self.assertFalse(definition.tradable,
                             "a strategy admitted by research alone must not be tradable")


class EconomicAdmissionBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.journal = EconomicAssessmentJournal(root / "assessments.jsonl")
        self.strategies = StrategyRegistry(root / "strategies.json")
        self._seed("STR-TEST")

    def _seed(self, strategy_id: str, lifecycle: str = "VALIDATED"):
        definition = StrategyDefinition(strategy_id=strategy_id, version=1, lane="test", spec={})
        if lifecycle != "RESEARCH":
            definition.transition("VALIDATED", "fixture")
        if lifecycle == "SHADOW":
            definition.transition("SHADOW", "fixture")
        self.strategies.upsert(definition)
        return definition

    _NO_CONSISTENCY_PASSED = object()

    def _admit(self, strategy_id="STR-TEST", ticket_id="TCK-1", artifact=None,
              meue_result=None, theta=None, interaction=None,
              consistency=_NO_CONSISTENCY_PASSED):
        if consistency is self._NO_CONSISTENCY_PASSED:
            consistency = _consistency()
        return assess_and_admit(
            journal=self.journal, strategies=self.strategies, ticket_id=ticket_id,
            strategy_id=strategy_id, effect_artifact=artifact,
            meue_result=meue_result or _meue_result(), theta=theta or _theta(),
            interaction=interaction or _interaction(), consistency=consistency)

    # --- missing / unresolved / mismatched effect coordinate ---------------

    def test_missing_effect_estimate_is_a_distinct_refusal_not_generic_no_trade(self):
        outcome = self._admit(artifact=None)
        self.assertEqual(outcome.status, REFUSED)
        self.assertEqual(outcome.reason, EFFECT_UNAVAILABLE)
        self.assertNotEqual(outcome.reason, "NO_TRADE")
        definition = self.strategies.get("STR-TEST")
        self.assertEqual(definition.lifecycle, "VALIDATED")

    def test_coordinate_unresolved_is_distinct_from_unavailable(self):
        artifact = _artifact(status="REFUSED", reason_codes=(DELTA_COORDINATE_UNRESOLVED,
                                                              EFFECT_UNAVAILABLE))
        outcome = self._admit(artifact=artifact)
        self.assertEqual(outcome.reason, DELTA_COORDINATE_UNRESOLVED)
        self.assertEqual(self.strategies.get("STR-TEST").lifecycle, "VALIDATED")

    def test_coordinate_mismatch_is_distinct_from_unresolved(self):
        artifact = _artifact(status="REFUSED", reason_codes=(DELTA_COORDINATE_MISMATCH,
                                                              EFFECT_UNAVAILABLE))
        outcome = self._admit(artifact=artifact)
        self.assertEqual(outcome.reason, DELTA_COORDINATE_MISMATCH)
        self.assertNotEqual(outcome.reason, DELTA_COORDINATE_UNRESOLVED)
        self.assertEqual(self.strategies.get("STR-TEST").lifecycle, "VALIDATED")

    # --- economic_gate outcomes ---------------------------------------------

    def test_economic_no_trade_never_promotes(self):
        # lower/upper straddle meue -> UNCERTAINTY_STRADDLES_ECONOMIC_THRESHOLD (NO_TRADE).
        estimate = _effect_estimate(delta_hat=0.01, lower=-0.01, upper=0.03)
        artifact = _artifact(effect_estimate=estimate)
        outcome = self._admit(artifact=artifact, meue_result=_meue_result(meue=0.02))
        self.assertEqual(outcome.status, REFUSED)
        self.assertEqual(outcome.verdict.verdict, "NO_TRADE")
        self.assertEqual(self.strategies.get("STR-TEST").lifecycle, "VALIDATED")

    def test_economic_kill_never_promotes(self):
        # whole interval below meue -> KILL.
        estimate = _effect_estimate(delta_hat=0.001, lower=-0.01, upper=0.005)
        artifact = _artifact(effect_estimate=estimate)
        outcome = self._admit(artifact=artifact, meue_result=_meue_result(meue=0.02))
        self.assertEqual(outcome.status, REFUSED)
        self.assertEqual(outcome.verdict.verdict, "KILL")
        self.assertEqual(self.strategies.get("STR-TEST").lifecycle, "VALIDATED")

    def test_continue_but_capital_order_ineligible_never_promotes(self):
        # CONTINUE, but no consistency check supplied -> DEVELOPMENT_SIGNAL_ONLY.
        estimate = _effect_estimate(delta_hat=0.05, lower=0.03, upper=0.08)
        artifact = _artifact(effect_estimate=estimate)
        outcome = self._admit(artifact=artifact, meue_result=_meue_result(meue=0.02),
                              consistency=None)
        self.assertEqual(outcome.verdict.verdict, "CONTINUE")
        self.assertEqual(outcome.verdict.capital_order_eligibility,
                         ORDER_ELIGIBILITY_DEVELOPMENT_SIGNAL_ONLY)
        self.assertEqual(outcome.status, REFUSED)
        self.assertFalse(outcome.promoted_to_shadow)
        self.assertEqual(self.strategies.get("STR-TEST").lifecycle, "VALIDATED")

    def test_continue_and_eligible_promotes_exactly_once(self):
        estimate = _effect_estimate(delta_hat=0.05, lower=0.03, upper=0.08)
        artifact = _artifact(effect_estimate=estimate)
        meue_result = _meue_result(meue=0.02)
        outcome = self._admit(artifact=artifact, meue_result=meue_result)
        self.assertEqual(outcome.verdict.capital_order_eligibility,
                         ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE)
        self.assertEqual(outcome.status, ADMITTED)
        self.assertTrue(outcome.promoted_to_shadow)
        definition = self.strategies.get("STR-TEST")
        self.assertEqual(definition.lifecycle, "SHADOW")
        shadow_transitions = [row for row in definition.lifecycle_history
                              if row["to"] == "SHADOW"]
        self.assertEqual(len(shadow_transitions), 1)

        # Replay: identical inputs -> no duplicate durable record, no second promotion.
        outcome2 = self._admit(artifact=artifact, meue_result=meue_result)
        self.assertEqual(outcome2.assessment_id, outcome.assessment_id)
        self.assertFalse(outcome2.promoted_to_shadow)
        definition_after = self.strategies.get("STR-TEST")
        shadow_transitions_after = [row for row in definition_after.lifecycle_history
                                    if row["to"] == "SHADOW"]
        self.assertEqual(len(shadow_transitions_after), 1)
        self.assertEqual(len(self.journal), 1)

    # --- Desk never sees a plain-VALIDATED, non-admitted strategy ----------

    def test_desk_actionable_excludes_non_admitted_strategy(self):
        estimate = _effect_estimate(delta_hat=0.01, lower=-0.01, upper=0.03)
        artifact = _artifact(effect_estimate=estimate)
        self._admit(artifact=artifact, meue_result=_meue_result(meue=0.02))  # -> NO_TRADE
        self.assertEqual(self.strategies.get("STR-TEST").lifecycle, "VALIDATED")
        desk_actionable_ids = [d.strategy_id for d in self.strategies.strategies.values()
                               if d.tradable or d.evaluation_track]
        self.assertNotIn("STR-TEST", desk_actionable_ids)

    # --- idempotent replay / conflict ---------------------------------------

    def test_replay_same_assessment_id_and_inputs_is_a_no_op(self):
        estimate = _effect_estimate(delta_hat=0.01, lower=-0.01, upper=0.03)
        artifact = _artifact(effect_estimate=estimate)
        outcome1 = self._admit(artifact=artifact, meue_result=_meue_result(meue=0.02))
        outcome2 = self._admit(artifact=artifact, meue_result=_meue_result(meue=0.02))
        self.assertEqual(outcome1.assessment_id, outcome2.assessment_id)
        self.assertEqual(len(self.journal), 1)

    def test_same_assessment_id_changed_inputs_conflicts_and_fails_closed(self):
        estimate = _effect_estimate(delta_hat=0.01, lower=-0.01, upper=0.03)
        artifact = _artifact(effect_estimate=estimate)
        self._admit(artifact=artifact, meue_result=_meue_result(meue=0.02))
        with self.assertRaises(AssessmentConflict):
            # Same forward evidence identity (same artifact) -> same assessment_id;
            # different economic inputs (theta.capital changed) -> different
            # input_fingerprint -> must conflict, not silently overwrite.
            self._admit(artifact=artifact, meue_result=_meue_result(meue=0.02),
                       theta=_theta(capital=99_999.0))
        # No promotion happened and the prior durable record is unmodified.
        self.assertEqual(self.strategies.get("STR-TEST").lifecycle, "VALIDATED")
        self.assertEqual(len(self.journal), 1)

    # --- forward evidence identity is scoped, not whole-ledger -------------

    def test_forward_evidence_identity_unaffected_by_unrelated_ledger_growth(self):
        estimate = _effect_estimate()
        artifact = _artifact(effect_estimate=estimate,
                             allocation_commitment_hashes=("sha256:b", "sha256:a"))
        identity_before = forward_adapter.derive_forward_evidence_identity(
            artifact=artifact, ticket_id="TCK-1", strategy_id="STR-TEST")
        # A whole-ledger fingerprint would change when unrelated Forward evidence
        # arrives; the artifact-scoped identity here reads only this artifact's
        # own fields, so growing an unrelated ledger cannot touch it.
        same_artifact_later = _artifact(effect_estimate=estimate,
                                        allocation_commitment_hashes=("sha256:a", "sha256:b"))
        identity_after = forward_adapter.derive_forward_evidence_identity(
            artifact=same_artifact_later, ticket_id="TCK-1", strategy_id="STR-TEST")
        self.assertEqual(identity_before, identity_after)
        self.assertEqual(forward_adapter.assessment_id_for(identity_before),
                         forward_adapter.assessment_id_for(identity_after))

    def test_forward_adapter_never_accepts_a_boolean_confirmation_flag(self):
        estimate = _effect_estimate()
        artifact = _artifact(effect_estimate=estimate)
        with self.assertRaises(TypeError):
            forward_adapter.derive_forward_evidence_identity(  # type: ignore[call-arg]
                artifact=artifact, ticket_id="TCK-1", strategy_id="STR-TEST",
                forward_confirmed=True)

    def test_already_shadow_strategy_is_not_re_promoted(self):
        self._seed("STR-SHADOW", lifecycle="SHADOW")
        estimate = _effect_estimate(delta_hat=0.05, lower=0.03, upper=0.08)
        artifact = _artifact(effect_estimate=estimate)
        outcome = self._admit(strategy_id="STR-SHADOW", artifact=artifact,
                              meue_result=_meue_result(meue=0.02))
        self.assertFalse(outcome.promoted_to_shadow)
        definition = self.strategies.get("STR-SHADOW")
        shadow_transitions = [row for row in definition.lifecycle_history
                              if row["to"] == "SHADOW"]
        self.assertEqual(len(shadow_transitions), 1)  # the original fixture transition only


if __name__ == "__main__":
    unittest.main()
