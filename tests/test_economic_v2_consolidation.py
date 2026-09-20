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
from quant.economics import (ADVERSE_SCENARIO_CATEGORIES, COST_CLASSES,
                             AuthorisedScenarioExclusion, AuthorisedZero, CostComponent,
                             CostScenario, Dependence, EffectEstimate, JointScenarioSet,
                             KForwardRecipe, PortfolioInteraction,
                             ProvenanceBinding, economic_gate, verify_research_cost_consistency,
                             verify_shape_declarations)
from quant.economics.scenarios import SCENARIO_ADVERSE, SCENARIO_CENTRAL
from quant.economics.consistency import ExecutionCostModel, ResearchExecutionConsistency
from quant.economics.decision import (AUTHORITY_DEVELOPMENT_ONLY, AUTHORITY_FORWARD_CONFIRMED,
                                      EVIDENCE_DEVELOPMENT, EVIDENCE_FORWARD_CONFIRMATION)
from quant.economics.frictions import (COST_SHAPE_FIXED, COST_SHAPE_PER_NOTIONAL,
                                       COST_SHAPE_SQRT_IMPACT)
from quant.economics.margin import FUNCTIONAL_FROZEN
from quant.economics.states import (CLUSTERING_UNIT_O4_RESOLVED, CLUSTERING_UNIT_O4_UNRESOLVED,
                                    CLUSTERING_UNIT_UNDECLARED, CONTINUE, KILL, NO_TRADE,
                                    ORDER_ELIGIBILITY_DEVELOPMENT_SIGNAL_ONLY,
                                    ORDER_ELIGIBILITY_NOT_ELIGIBLE,
                                    ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE,
                                    PROVENANCE_CALIBRATED,
                                    PROVENANCE_VALIDATION_INDEPENDENTLY_VALIDATED,
                                    PROVENANCE_VALIDATION_UNVALIDATED, RECIPE_CONSUMABLE,
                                    RECIPE_INVALID, RECIPE_PROVISIONAL)


def _single_component_recipe(component: CostComponent) -> KForwardRecipe:
    return KForwardRecipe(
        recipe_id="TEST_SINGLE_COMPONENT", components=(component,),
        authorised_zeros=tuple(AuthorisedZero(cost_class, "TEST_AUTHORITY", "not modelled")
                               for cost_class in COST_CLASSES if cost_class != component.cost_class))


def joined(problems) -> str:
    return " | ".join(problems)


def _fully_bound_provenance(keys) -> dict:
    return {key: ProvenanceBinding(
                version="v1", as_of="2026-09-19", authority="TEST_AUTHORITY",
                dataset_fingerprint="sha256:test-fixture-only-no-scientific-authority",
                validation_state=PROVENANCE_VALIDATION_INDEPENDENTLY_VALIDATED)
            for key in keys}


def consumable_recipe():
    """A RECIPE_CONSUMABLE recipe: every parameter calibrated and bound, functional frozen.

    Mirrors ``test_recipe_is_consumable_only_with_calibration_and_a_frozen_
    functional`` in ``test_economics_engine.py`` exactly, so this file never
    has to invent its own scientific constant to get a consumable recipe.
    """
    values = {key: (value, PROVENANCE_CALIBRATED)
              for key, (value, _) in fixtures.CENTRAL_VALUES.items()}
    inventory = fixtures.parameter_inventory().instantiate(values)
    inventory = inventory.bind_provenance(_fully_bound_provenance(values))
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


class CostShapeTypologyTest(unittest.TestCase):
    """Cost model types: fix the Codex weakness (self red team item 1 /
    ``W1-SELF-001``) that a computed currency cost does not prove its
    dependence on size. Each shape's claimed ratio is probed numerically.
    """

    def setUp(self):
        self.theta = fixtures.theta_state()
        self.params = dict(fixtures.CENTRAL_PARAMS)

    def test_red_undeclared_shape_is_a_hard_violation(self):
        component = CostComponent(name="X", cost_class="F1_EXPLICIT_FEES",
                                  applicability="ALWAYS",
                                  functional=lambda delta, theta, params: 1.0,
                                  formula_statement="1.0",
                                  input_classes=("FROZEN_COST_PARAMETER",))
        self.assertEqual(component.shape, "")
        self.assertIn("X: COST_SHAPE_NOT_DECLARED", component.violations())

    def test_green_correctly_labelled_fixture_recipe_passes_the_shape_probe(self):
        recipe = fixtures.k_forward_recipe()
        self.assertEqual(verify_shape_declarations(recipe, self.theta, self.params), [])

    def test_red_mislabelled_fixed_cost_that_actually_scales_is_caught(self):
        """RED: before this pass, nothing checked a FIXED claim at all."""
        component = CostComponent(
            name="MISLABELLED_FIXED", cost_class="F1_EXPLICIT_FEES",
            applicability="ALWAYS_APPLICABLE",
            functional=lambda delta, theta, params: 0.0001 * theta.expected_deployed_exposure,
            formula_statement="0.0001 * Q(theta) -- mislabelled as FIXED",
            input_classes=("EXPECTED_DEPLOYED_EXPOSURE_Q",), shape=COST_SHAPE_FIXED)
        problems = verify_shape_declarations(_single_component_recipe(component), self.theta,
                                             self.params)
        self.assertIn("MISLABELLED_FIXED: DECLARED_FIXED_BUT_VARIES_WITH_EXPOSURE", problems)

    def test_green_a_genuinely_fixed_cost_is_not_flagged(self):
        component = CostComponent(
            name="GENUINELY_FIXED", cost_class="F1_EXPLICIT_FEES",
            applicability="ALWAYS_APPLICABLE", functional=lambda delta, theta, params: 12.5,
            formula_statement="12.5 (a flat account fee)",
            input_classes=("FROZEN_COST_PARAMETER",), shape=COST_SHAPE_FIXED)
        problems = verify_shape_declarations(_single_component_recipe(component), self.theta,
                                             self.params)
        self.assertEqual(problems, [])

    def test_red_mislabelled_sqrt_impact_that_is_actually_linear_is_caught(self):
        component = CostComponent(
            name="MISLABELLED_SQRT", cost_class="F4_MARKET_IMPACT",
            applicability="ALWAYS_APPLICABLE",
            functional=lambda delta, theta, params: 0.001 * (theta.participation or 0.0),
            formula_statement="0.001 * participation -- actually linear, mislabelled sqrt",
            input_classes=("PARTICIPATION_DERIVED_FROM_THETA",),
            dependence=Dependence(participation=True), shape=COST_SHAPE_SQRT_IMPACT)
        problems = verify_shape_declarations(_single_component_recipe(component), self.theta,
                                             self.params)
        self.assertTrue(any("DECLARED_SQRT_IMPACT_BUT_RATIO" in problem for problem in problems),
                        problems)

    def test_red_mislabelled_per_notional_that_is_actually_constant_is_caught(self):
        component = CostComponent(
            name="MISLABELLED_CONSTANT", cost_class="F1_EXPLICIT_FEES",
            applicability="ALWAYS_APPLICABLE", functional=lambda delta, theta, params: 7.5,
            formula_statement="7.5 -- constant, mislabelled as per-notional",
            input_classes=("FROZEN_COST_PARAMETER",), shape=COST_SHAPE_PER_NOTIONAL)
        problems = verify_shape_declarations(_single_component_recipe(component), self.theta,
                                             self.params)
        self.assertIn("MISLABELLED_CONSTANT: DECLARED_LINEAR_IN_EXPOSURE_BUT_CONSTANT", problems)

    def test_green_recipe_evaluation_fails_closed_on_a_shape_contradiction(self):
        """End to end: MEUERecipe.evaluate() itself refuses the mislabelled recipe."""
        bad_component = CostComponent(
            name="MISLABELLED_CONSTANT", cost_class="F1_EXPLICIT_FEES",
            applicability="ALWAYS_APPLICABLE", functional=lambda delta, theta, params: 7.5,
            formula_statement="7.5", input_classes=("FROZEN_COST_PARAMETER",),
            shape=COST_SHAPE_PER_NOTIONAL)
        recipe = fixtures.meue_recipe(k_forward=_single_component_recipe(bad_component))
        result = recipe.evaluate(fixtures.theta_state())
        self.assertEqual(result.recipe_state, RECIPE_INVALID)
        self.assertTrue(any("DECLARED_LINEAR_IN_EXPOSURE_BUT_CONSTANT" in violation
                            for violation in result.violations), result.violations)


class ProvenanceAuthenticityTest(unittest.TestCase):
    """Provenance authenticity: refuse a syntactic-only calibration claim.

    Wave 1 red team item 4 (`ExposureBudget` provenance is declared, not
    proved) and Codex's self red team item 5 (a nonempty source string can
    lie) independently named the same gap. Only ``PROVENANCE_CALIBRATED`` —
    the one class that can make a recipe ``RECIPE_CONSUMABLE`` — is held to
    the stricter bar; ``PROVENANCE_V1_ASSUMED``/``PROVENANCE_ENGINEERING_
    BOUND`` already admit they are not authoritative and are charged as model
    risk instead (unaffected here, and unaffected by this whole test class).
    """

    def setUp(self):
        self.theta = fixtures.theta_state()
        self.calibrated_values = {key: (value, PROVENANCE_CALIBRATED)
                                  for key, (value, _) in fixtures.CENTRAL_VALUES.items()}

    def test_red_a_calibrated_label_alone_is_syntactic_and_stays_provisional(self):
        """RED: before this pass, CALIBRATED + a frozen functional was enough."""
        inventory = fixtures.parameter_inventory().instantiate(self.calibrated_values)
        recipe = fixtures.meue_recipe(inventory=inventory, margin_functional_status=FUNCTIONAL_FROZEN)
        result = recipe.evaluate(self.theta)
        self.assertEqual(result.recipe_state, RECIPE_PROVISIONAL)
        self.assertIn("PROVENANCE_CLAIMS_CALIBRATION_WITHOUT_BINDING_EVIDENCE",
                      joined(result.notes))

    def test_green_binding_every_consumed_calibrated_parameter_reaches_consumable(self):
        recipe = consumable_recipe()  # already binds provenance; see helper above
        result = recipe.evaluate(self.theta)
        self.assertEqual(result.recipe_state, RECIPE_CONSUMABLE)

    def test_partial_binding_is_still_syntactic_only(self):
        """Every field matters: a binding missing just the dataset link fails closed."""
        inventory = fixtures.parameter_inventory().instantiate(self.calibrated_values)
        incomplete = {key: ProvenanceBinding(version="v1", as_of="2026-09-19",
                                             authority="TEST_AUTHORITY",
                                             validation_state=
                                             PROVENANCE_VALIDATION_INDEPENDENTLY_VALIDATED)
                     for key in self.calibrated_values}  # no dataset_fingerprint/artifact_hash
        inventory = inventory.bind_provenance(incomplete)
        recipe = fixtures.meue_recipe(inventory=inventory, margin_functional_status=FUNCTIONAL_FROZEN)
        result = recipe.evaluate(self.theta)
        self.assertEqual(result.recipe_state, RECIPE_PROVISIONAL)

    def test_unvalidated_binding_is_still_syntactic_only(self):
        inventory = fixtures.parameter_inventory().instantiate(self.calibrated_values)
        unvalidated = {key: ProvenanceBinding(version="v1", as_of="2026-09-19",
                                              authority="TEST_AUTHORITY",
                                              dataset_fingerprint="sha256:test",
                                              validation_state=PROVENANCE_VALIDATION_UNVALIDATED)
                      for key in self.calibrated_values}
        inventory = inventory.bind_provenance(unvalidated)
        recipe = fixtures.meue_recipe(inventory=inventory, margin_functional_status=FUNCTIONAL_FROZEN)
        result = recipe.evaluate(self.theta)
        self.assertEqual(result.recipe_state, RECIPE_PROVISIONAL)

    def test_garbage_validation_state_is_a_hard_structural_violation(self):
        binding = ProvenanceBinding(validation_state="NOT_A_RECOGNISED_STATE")
        self.assertIn("PARAM: PROVENANCE_VALIDATION_STATE_NOT_RECOGNISED",
                      binding.violations("PARAM"))

    def test_v1_assumed_parameters_are_never_held_to_the_binding_bar(self):
        """Only a CALIBRATED claim is authoritative enough to need proving.

        The default fixture recipe mixes both provenance classes (FEE_BPS/
        EXIT_BPS calibrated, the rest V1_ASSUMED), so both notes legitimately
        fire together; what matters is that the V1_ASSUMED-only parameters
        never appear in the *binding* note, since they were never claiming to
        be authoritative in the first place.
        """
        result = fixtures.meue_recipe().evaluate(self.theta)
        self.assertEqual(result.recipe_state, RECIPE_PROVISIONAL)
        binding_note = next(note for note in result.notes
                            if note.startswith("PROVENANCE_CLAIMS_CALIBRATION_WITHOUT_BINDING"))
        self.assertNotIn("F2_OPEN_HALF_SPREAD_BPS", binding_note)
        self.assertNotIn("F4_IMPACT_BPS_AT_FULL_PARTICIPATION", binding_note)
        self.assertNotIn("F4_REFERENCE_PARTICIPATION", binding_note)

        # An inventory with no CALIBRATED claim at all never raises the note.
        all_assumed = {key: (value, fixtures.PROVENANCE_V1_ASSUMED)
                      for key, (value, _) in fixtures.CENTRAL_VALUES.items()}
        inventory = fixtures.parameter_inventory().instantiate(all_assumed)
        recipe = fixtures.meue_recipe(inventory=inventory)
        result = recipe.evaluate(self.theta)
        self.assertNotIn("PROVENANCE_CLAIMS_CALIBRATION_WITHOUT_BINDING_EVIDENCE",
                         joined(result.notes))

    def test_bind_provenance_refuses_an_unknown_parameter(self):
        inventory = fixtures.parameter_inventory()
        with self.assertRaises(Exception):
            inventory.bind_provenance({"NOT_A_DECLARED_PARAMETER": ProvenanceBinding()})

    def test_provenance_binding_is_excluded_from_the_frozen_rule_hash(self):
        """RULE_BEFORE_VALUES: binding evidence is value-adjacent, not the rule."""
        bound = consumable_recipe()
        unbound = fixtures.meue_recipe(
            inventory=fixtures.parameter_inventory().instantiate(self.calibrated_values),
            margin_functional_status=FUNCTIONAL_FROZEN)
        self.assertEqual(bound.inventory.rule_document(), unbound.inventory.rule_document())
        self.assertEqual(bound.fingerprint(), unbound.fingerprint())


class JointAdverseScenarioCategoryTest(unittest.TestCase):
    """Joint adverse scenarios: refuse an absent authority, name none myself.

    Mission item 6: harden S_cost/M_economic against correlated liquidity
    deterioration, spread widening + impact increase, borrow/financing
    deterioration, capacity reduction, execution regime mismatch — without
    choosing which numerical scenarios are authoritative (Blue's call).
    """

    def test_red_bare_scenario_set_has_uncovered_categories(self):
        """RED: before this pass, nothing checked category coverage at all."""
        bare = JointScenarioSet(
            set_id="BARE", update_rule="ANY_RULE",
            scenarios=(CostScenario("s_0", SCENARIO_CENTRAL, {"X": 1.0}, provenance="T"),
                      CostScenario("s_1", SCENARIO_ADVERSE, {"X": 2.0},
                                  coherence_justification="j", dependence_representation="d",
                                  provenance="T")))
        problems = bare.category_coverage_violations()
        self.assertEqual(len(problems), len(ADVERSE_SCENARIO_CATEGORIES))
        for category in ADVERSE_SCENARIO_CATEGORIES:
            self.assertIn(f"JOINT_ADVERSE_CATEGORY_NOT_ADDRESSED:{category}", problems)

    def test_green_fixture_scenario_set_addresses_or_excludes_every_category(self):
        self.assertEqual(fixtures.scenario_set().category_coverage_violations(), [])

    def test_green_default_recipe_carries_the_category_gap_note_until_fixed(self):
        """The fixture itself is fully covered, so evaluate() on the plain
        default recipe carries no category gap note (unlike the calibration/
        provenance notes, which fire for unrelated reasons on this fixture).
        """
        result = fixtures.meue_recipe().evaluate(fixtures.theta_state())
        self.assertNotIn("JOINT_ADVERSE_SCENARIO_CATEGORY_GAP", joined(result.notes))

    def test_a_scenario_set_missing_one_category_is_caught(self):
        incomplete = replace(fixtures.scenario_set(),
                             category_exclusions=fixtures.scenario_set().category_exclusions[:1])
        problems = incomplete.category_coverage_violations()
        self.assertIn(
            f"JOINT_ADVERSE_CATEGORY_NOT_ADDRESSED:"
            f"{fixtures.scenario_set().category_exclusions[1].category}", problems)

    def test_exclusion_without_authority_is_refused(self):
        exclusion = AuthorisedScenarioExclusion("CAPACITY_REDUCTION", "", "no reason given")
        self.assertIn("CAPACITY_REDUCTION: EXCLUSION_REQUIRES_EXPLICIT_AUTHORITY",
                      exclusion.violations())

    def test_addressed_and_excluded_at_once_is_a_contradiction(self):
        category = "CAPACITY_REDUCTION"
        contradictory = JointScenarioSet(
            set_id="X", update_rule="R",
            scenarios=(CostScenario("s_0", SCENARIO_CENTRAL, {"X": 1.0}, provenance="T"),
                      CostScenario("s_1", SCENARIO_ADVERSE, {"X": 2.0},
                                  coherence_justification="j", dependence_representation="d",
                                  provenance="T", categories=(category,))),
            category_exclusions=(AuthorisedScenarioExclusion(category, "AUTH", "reason"),))
        self.assertIn(f"{category}: CATEGORY_BOTH_ADDRESSED_AND_EXCLUDED",
                      contradictory.category_coverage_violations())

    def test_unrecognised_category_on_a_scenario_is_a_hard_violation(self):
        scenario = CostScenario("s_1", SCENARIO_ADVERSE, {"X": 2.0}, coherence_justification="j",
                                dependence_representation="d", provenance="T",
                                categories=("NOT_A_REAL_CATEGORY",))
        self.assertIn("s_1: ADVERSE_CATEGORY_NOT_IN_NAMED_TAXONOMY:NOT_A_REAL_CATEGORY",
                      scenario.violations())

    def test_this_pass_named_no_authoritative_numerical_scenario(self):
        """This pass builds the mechanism only; it asserts no scenario values."""
        for scenario in fixtures.scenario_set().scenarios:
            self.assertEqual(scenario.provenance, fixtures.TEST_AUTHORITY)


if __name__ == "__main__":
    unittest.main()
