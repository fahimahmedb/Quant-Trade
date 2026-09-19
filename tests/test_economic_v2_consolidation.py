"""ECONOMIC V2 consolidation: red-to-green tests for each closed defect.

Each test class below targets one specific defect named in the ECONOMIC V2
mission and in Wave 1's own red team. These are independent of, and do not
modify, the existing Wave 1 test files
(``test_economics_engine.py``, ``test_economics_timeline_execution.py``); a
regression here is a regression in this pass's own work, never something
papered over by touching Wave 1's coverage.
"""

from __future__ import annotations

import unittest
from dataclasses import replace

import economics_fixtures as fixtures
from quant.desk.execution import ExecutionModel, RESEARCH_ONE_WAY_COST_BPS
from quant.economics import (EffectEstimate, PortfolioInteraction, economic_gate,
                             verify_research_cost_consistency)
from quant.economics.consistency import ExecutionCostModel, ResearchExecutionConsistency
from quant.economics.decision import (AUTHORITY_DEVELOPMENT_ONLY, AUTHORITY_FORWARD_CONFIRMED,
                                      EVIDENCE_DEVELOPMENT, EVIDENCE_FORWARD_CONFIRMATION)
from quant.economics.margin import FUNCTIONAL_FROZEN
from quant.economics.states import (CLUSTERING_UNIT_O4_RESOLVED, CLUSTERING_UNIT_O4_UNRESOLVED,
                                    CLUSTERING_UNIT_UNDECLARED, CONTINUE, KILL, NO_TRADE,
                                    ORDER_ELIGIBILITY_DEVELOPMENT_SIGNAL_ONLY,
                                    ORDER_ELIGIBILITY_NOT_ELIGIBLE,
                                    ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE,
                                    PROVENANCE_CALIBRATED, RECIPE_CONSUMABLE, RECIPE_PROVISIONAL)


def joined(problems) -> str:
    return " | ".join(problems)


def consumable_recipe():
    """A RECIPE_CONSUMABLE recipe: every parameter calibrated, functional frozen.

    Mirrors ``test_recipe_is_consumable_only_with_calibration_and_a_frozen_
    functional`` in ``test_economics_engine.py`` exactly, so this file never
    has to invent its own scientific constant to get a consumable recipe.
    """
    values = {key: (value, PROVENANCE_CALIBRATED)
              for key, (value, _) in fixtures.CENTRAL_VALUES.items()}
    inventory = fixtures.parameter_inventory().instantiate(values)
    return fixtures.meue_recipe(inventory=inventory, margin_functional_status=FUNCTIONAL_FROZEN)


class RecipeProvisionalEligibilityTest(unittest.TestCase):
    """Wave 1 red team item 8.1: a provisional recipe can still CONTINUE.

    Closed not by forbidding that CONTINUE (a ruling this Builder has no
    authority to make) but by making sure nothing downstream can mistake it
    for anything beyond a development signal.
    """

    def setUp(self):
        self.theta = fixtures.theta_state()
        self.interaction = PortfolioInteraction(overlap_fraction=0.0, residual_beta=0.0)

    def estimate(self, evidence_label: str) -> EffectEstimate:
        return EffectEstimate(delta_hat=0.05, lower=0.04, upper=0.06, confidence_level=0.95,
                              evidence_label=evidence_label, sample_provenance="SYNTHETIC_FIXTURE",
                              clustering_unit_provenance=CLUSTERING_UNIT_O4_RESOLVED)

    def test_red_provisional_recipe_forward_confirmed_still_mechanically_continues(self):
        """RED: reproduce the exact red-team-flagged shape before this pass's fix.

        A provisional (uncalibrated) recipe combined with forward-confirmed
        evidence must still mechanically CONTINUE — Wave 1 designed that on
        purpose so development is not blocked pending calibration. This
        assertion is the reproduction: it would have been indistinguishable
        from an authoritative CONTINUE before this pass added a separate
        eligibility tier.
        """
        meue_result = fixtures.meue_recipe().evaluate(self.theta)
        self.assertEqual(meue_result.recipe_state, RECIPE_PROVISIONAL)
        verdict = economic_gate(self.estimate(EVIDENCE_FORWARD_CONFIRMATION), meue_result,
                                self.theta, self.interaction)
        self.assertEqual(verdict.verdict, CONTINUE)

    def test_green_provisional_recipe_is_capped_at_development_signal(self):
        """GREEN: the fix. Eligibility must not follow evidence label alone."""
        meue_result = fixtures.meue_recipe().evaluate(self.theta)
        verdict = economic_gate(self.estimate(EVIDENCE_FORWARD_CONFIRMATION), meue_result,
                                self.theta, self.interaction)
        self.assertEqual(verdict.verdict, CONTINUE)
        self.assertEqual(verdict.recipe_state, RECIPE_PROVISIONAL)
        self.assertEqual(verdict.capital_order_eligibility,
                         ORDER_ELIGIBILITY_DEVELOPMENT_SIGNAL_ONLY)
        self.assertIn("ECONOMIC_THRESHOLD_RECIPE_STATE_RECIPE_PROVISIONAL_NOT_CONSUMABLE",
                      verdict.capital_order_eligibility_reasons)

    def test_development_evidence_on_a_provisional_recipe_is_also_capped(self):
        meue_result = fixtures.meue_recipe().evaluate(self.theta)
        verdict = economic_gate(self.estimate(EVIDENCE_DEVELOPMENT), meue_result, self.theta,
                                self.interaction)
        self.assertEqual(verdict.verdict, CONTINUE)
        self.assertEqual(verdict.authority, AUTHORITY_DEVELOPMENT_ONLY)
        self.assertEqual(verdict.capital_order_eligibility,
                         ORDER_ELIGIBILITY_DEVELOPMENT_SIGNAL_ONLY)
        self.assertIn("EVIDENCE_NOT_FORWARD_CONFIRMED", verdict.capital_order_eligibility_reasons)

    def test_non_continue_verdicts_carry_recipe_state_but_no_eligibility(self):
        meue_result = fixtures.meue_recipe().evaluate(self.theta)
        tiny = replace(self.estimate(EVIDENCE_FORWARD_CONFIRMATION),
                       delta_hat=0.00001, lower=0.0, upper=0.00002)
        verdict = economic_gate(tiny, meue_result, self.theta, self.interaction)
        self.assertIn(verdict.verdict, (NO_TRADE, KILL))
        self.assertEqual(verdict.capital_order_eligibility, ORDER_ELIGIBILITY_NOT_ELIGIBLE)
        self.assertEqual(verdict.capital_order_eligibility_reasons, ())
        self.assertEqual(verdict.recipe_state, RECIPE_PROVISIONAL)

    def test_consumable_recipe_alone_is_not_enough_without_forward_confirmation(self):
        meue_result = consumable_recipe().evaluate(self.theta)
        self.assertEqual(meue_result.recipe_state, RECIPE_CONSUMABLE)
        verdict = economic_gate(self.estimate(EVIDENCE_DEVELOPMENT), meue_result, self.theta,
                                self.interaction)
        self.assertEqual(verdict.verdict, CONTINUE)
        self.assertEqual(verdict.capital_order_eligibility,
                         ORDER_ELIGIBILITY_DEVELOPMENT_SIGNAL_ONLY)

    def test_full_eligibility_requires_recipe_evidence_clustering_and_consistency_together(self):
        """The one positive case: every gate cleared at once."""
        meue_result = consumable_recipe().evaluate(self.theta)
        execution = ExecutionModel()
        model = ExecutionCostModel.from_execution_model(execution)
        consistency = verify_research_cost_consistency(
            RESEARCH_ONE_WAY_COST_BPS, model, 0.006, "FULLY_ELIGIBLE_LANE")
        self.assertTrue(consistency.consistent)
        verdict = economic_gate(self.estimate(EVIDENCE_FORWARD_CONFIRMATION), meue_result,
                                self.theta, self.interaction, consistency=consistency)
        self.assertEqual(verdict.verdict, CONTINUE)
        self.assertEqual(verdict.authority, AUTHORITY_FORWARD_CONFIRMED)
        self.assertEqual(verdict.capital_order_eligibility,
                         ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE)
        self.assertEqual(verdict.capital_order_eligibility_reasons, ())


class Econ001FailClosedTest(unittest.TestCase):
    """ECON-001: research cost vs. modelled execution cost.

    Wave 1 already wrote an independent discriminating test
    (``ResearchExecutionConsistencyTest`` in
    ``test_economics_timeline_execution.py``) against the real shipped
    constants and already wired an optional ``consistency`` check into
    ``economic_gate``. What was still open: the check is optional, so nothing
    stopped a caller from getting a verdict without ever running it. This
    class (a) independently re-derives the defect's numbers from the raw
    constants with no dependency on ``ExecutionCostModel`` at all, as a
    cross-check on Wave 1's own reproduction, and (b) closes the fail-open gap
    at the capital-eligibility layer, without touching either constant.
    """

    def test_red_independent_rederivation_of_the_6_5_bps_understatement(self):
        """Re-derive the defect by hand, independent of ``consistency.py``.

        This does not import ``ExecutionCostModel`` or
        ``implied_participation_ceiling`` at all, so it cannot be fooled by a
        bug shared between the production check and its own test.
        """
        execution = ExecutionModel()
        research_cost = RESEARCH_ONE_WAY_COST_BPS
        # one_way_cost(p) = commission + half_spread + impact_at_full * sqrt(p / p_max)
        modelled_at_max = (execution.commission_bps + execution.half_spread_bps
                           + execution.impact_bps_at_full_participation
                           * (execution.max_participation / execution.max_participation) ** 0.5)
        self.assertAlmostEqual(modelled_at_max, 11.5, places=9)
        self.assertAlmostEqual(modelled_at_max - research_cost, 6.5, places=9)

        # p* solves commission + half_spread + impact_at_full*sqrt(p*/p_max) = research_cost
        fixed = execution.commission_bps + execution.half_spread_bps
        headroom = research_cost - fixed
        shape = headroom / execution.impact_bps_at_full_participation
        ceiling = execution.max_participation * shape * shape
        self.assertAlmostEqual(ceiling, 0.006125, places=9)
        self.assertLess(ceiling, execution.max_participation)

    def test_green_missing_consistency_check_fails_closed_on_eligibility(self):
        """GREEN: no consistency check run => never portfolio-eligible.

        A lane that never had its research/execution cost consistency
        verified must not reach ``PORTFOLIO_CONSIDERATION_ELIGIBLE`` even when
        every other gate (consumable recipe, forward-confirmed evidence,
        resolved clustering unit) is satisfied. This is the ``fail closed``
        the mission asks for on ECON-001, without inventing or moving either
        constant.
        """
        theta = fixtures.theta_state()
        meue_result = consumable_recipe().evaluate(theta)
        estimate = EffectEstimate(delta_hat=0.05, lower=0.04, upper=0.06, confidence_level=0.95,
                                  evidence_label=EVIDENCE_FORWARD_CONFIRMATION,
                                  sample_provenance="SYNTHETIC_FIXTURE",
                                  clustering_unit_provenance=CLUSTERING_UNIT_O4_RESOLVED)
        verdict = economic_gate(estimate, meue_result, theta,
                                PortfolioInteraction(0.0, residual_beta=0.0))
        self.assertEqual(verdict.verdict, CONTINUE)
        self.assertEqual(verdict.capital_order_eligibility,
                         ORDER_ELIGIBILITY_DEVELOPMENT_SIGNAL_ONLY)
        self.assertIn("RESEARCH_EXECUTION_CONSISTENCY_NOT_VERIFIED",
                      verdict.capital_order_eligibility_reasons)

    def test_green_violated_consistency_also_fails_closed_on_eligibility(self):
        theta = fixtures.theta_state()
        meue_result = consumable_recipe().evaluate(theta)
        execution = ExecutionModel()
        model = ExecutionCostModel.from_execution_model(execution)
        violating = verify_research_cost_consistency(
            RESEARCH_ONE_WAY_COST_BPS, model, execution.max_participation, "AT_MAX_SIZE")
        self.assertFalse(violating.consistent)
        estimate = EffectEstimate(delta_hat=0.05, lower=0.04, upper=0.06, confidence_level=0.95,
                                  evidence_label=EVIDENCE_FORWARD_CONFIRMATION,
                                  sample_provenance="SYNTHETIC_FIXTURE",
                                  clustering_unit_provenance=CLUSTERING_UNIT_O4_RESOLVED)
        verdict = economic_gate(estimate, meue_result, theta,
                                PortfolioInteraction(0.0, residual_beta=0.0),
                                consistency=violating)
        # The mechanical verdict is already NO_TRADE (Wave 1 behaviour,
        # unchanged): an inconsistent research/execution cost is a blocking
        # input defect, not merely an eligibility cap.
        self.assertEqual(verdict.verdict, NO_TRADE)
        self.assertEqual(verdict.capital_order_eligibility, ORDER_ELIGIBILITY_NOT_ELIGIBLE)

    def test_no_new_scientific_constant_was_introduced(self):
        """This pass must not silently move either ECON-001 constant."""
        execution = ExecutionModel()
        self.assertEqual(RESEARCH_ONE_WAY_COST_BPS, 5.0)
        self.assertEqual(execution.max_participation, 0.05)
        self.assertEqual(execution.impact_bps_at_full_participation, 10.0)


class ClusteringUnitO4DependencyTest(unittest.TestCase):
    """Wave 1 red team item 3: the clustering unit is an O4 consequence.

    Scope discipline: this does not modify ``quant.science`` (a distinct
    writer domain per the Wave 1 Builder allocation proposal). It only makes
    sure the economics engine cannot treat an undeclared or O4-unresolved
    clustering unit as equivalent to a resolved one when deciding eligibility.
    """

    def setUp(self):
        self.theta = fixtures.theta_state()
        self.interaction = PortfolioInteraction(overlap_fraction=0.0, residual_beta=0.0)
        self.meue_result = consumable_recipe().evaluate(self.theta)
        execution = ExecutionModel()
        model = ExecutionCostModel.from_execution_model(execution)
        self.consistency = verify_research_cost_consistency(
            RESEARCH_ONE_WAY_COST_BPS, model, 0.006, "LANE")

    def estimate(self, clustering_unit_provenance: str) -> EffectEstimate:
        return EffectEstimate(delta_hat=0.05, lower=0.04, upper=0.06, confidence_level=0.95,
                              evidence_label=EVIDENCE_FORWARD_CONFIRMATION,
                              sample_provenance="SYNTHETIC_FIXTURE",
                              clustering_unit_provenance=clustering_unit_provenance)

    def test_red_undeclared_clustering_unit_defaults_silently_today(self):
        """RED: the default value existed before this pass gave it teeth."""
        estimate = self.estimate(CLUSTERING_UNIT_UNDECLARED)
        self.assertEqual(estimate.violations(), [])  # undeclared is not a hard input defect

    def test_green_undeclared_clustering_unit_caps_eligibility(self):
        verdict = economic_gate(self.estimate(CLUSTERING_UNIT_UNDECLARED), self.meue_result,
                                self.theta, self.interaction, consistency=self.consistency)
        self.assertEqual(verdict.verdict, CONTINUE)
        self.assertEqual(verdict.capital_order_eligibility,
                         ORDER_ELIGIBILITY_DEVELOPMENT_SIGNAL_ONLY)
        self.assertIn("CLUSTERING_UNIT_PROVENANCE_UNDECLARED",
                      verdict.capital_order_eligibility_reasons)

    def test_green_o4_unresolved_clustering_unit_caps_eligibility(self):
        verdict = economic_gate(self.estimate(CLUSTERING_UNIT_O4_UNRESOLVED), self.meue_result,
                                self.theta, self.interaction, consistency=self.consistency)
        self.assertEqual(verdict.verdict, CONTINUE)
        self.assertEqual(verdict.capital_order_eligibility,
                         ORDER_ELIGIBILITY_DEVELOPMENT_SIGNAL_ONLY)
        self.assertIn("CLUSTERING_UNIT_DEPENDS_ON_UNFROZEN_D07_O4",
                      verdict.capital_order_eligibility_reasons)

    def test_green_o4_resolved_clustering_unit_does_not_cap_eligibility(self):
        verdict = economic_gate(self.estimate(CLUSTERING_UNIT_O4_RESOLVED), self.meue_result,
                                self.theta, self.interaction, consistency=self.consistency)
        self.assertEqual(verdict.verdict, CONTINUE)
        self.assertEqual(verdict.capital_order_eligibility,
                         ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE)

    def test_garbage_clustering_provenance_is_a_hard_input_defect(self):
        estimate = self.estimate("NOT_A_RECOGNISED_STATE")
        self.assertIn("CLUSTERING_UNIT_PROVENANCE_NOT_RECOGNISED", estimate.violations())
        verdict = economic_gate(estimate, self.meue_result, self.theta, self.interaction,
                                consistency=self.consistency)
        self.assertEqual(verdict.verdict, NO_TRADE)
        self.assertEqual(verdict.reason, "BLOCKING_INPUT_DEFECT")


if __name__ == "__main__":
    unittest.main()
