"""Adversarial tests for the economic engine.

These do not test that the arithmetic runs. They test that the engine *refuses*:
that an undeclared coordinate cannot be consumed, that a prudential markup cannot
hide inside expected cost, that an uncharged model risk blocks the margin, that a
cost class nobody mentioned is not a free zero, and that a statistically
significant effect with bad economics dies.
"""

from __future__ import annotations

import math
import unittest
from dataclasses import replace

import economics_fixtures as fixtures
from quant.economics import (AffineShortcutUnavailable, AuthorisedZero, CapacityLimit,
                             CostComponent, CostInputUnavailable, CostScenario, Dependence,
                             DeltaCoordinateBinding, EconomicParameter, EffectDomain,
                             EffectEstimate, EvaluationSession, InventoryFrozen,
                             JointScenarioSet, KForwardRecipe, ParameterInventory,
                             PhiInstance, PortfolioInteraction, ProvenanceBinding,
                             RecipeNotOutcomeBlind,
                             ReturnConvention, RiskClaim, RiskPartition, ThetaFeedbackViolation,
                             apply_capacity, beee, beee_affine, economic_gate,
                             evaluate_delta_coordinate, recipe_hash, solve_beee,
                             verify_dependence_declarations)
from quant.economics.capacity import (NEW_POLICY_VERSION, POLICY_SCALED_HOMOGENEOUSLY,
                                      POLICY_UNCHANGED, ExposureBudget)
from quant.economics.decision import (AUTHORITY_DEVELOPMENT_ONLY, EVIDENCE_DEVELOPMENT,
                                      EVIDENCE_FORWARD_CONFIRMATION, PAPER_SHADOW_ONLY)
from quant.economics.margin import FUNCTIONAL_FROZEN, MarginComponent, m_economic
from quant.economics.scenarios import SCENARIO_ADVERSE, SCENARIO_CENTRAL
from quant.economics.states import (BEEE_NO_ECONOMIC_ROOT, BEEE_NONMONOTONE_MAPPING,
                                    BEEE_NONUNIQUE_ROOT, BEEE_UNIQUE_ROOT, CONTINUE,
                                    DELTA_COORDINATE_COMPATIBLE, DELTA_COORDINATE_MISMATCH,
                                    DELTA_COORDINATE_UNRESOLVED, KILL,
                                    M_ECONOMIC_ENVELOPE_UNRESOLVED, NO_TRADE,
                                    PROVENANCE_CALIBRATED,
                                    PROVENANCE_VALIDATION_INDEPENDENTLY_VALIDATED,
                                    PROVENANCE_V1_ASSUMED,
                                    RECIPE_CONSUMABLE, RECIPE_INVALID, RECIPE_PROVISIONAL)
from quant.economics.theta import Q_PROVENANCE_NAIVE_ANNUALISATION


def joined(problems) -> str:
    return " | ".join(problems)


class DeltaCoordinateGateTest(unittest.TestCase):
    def test_undeclared_binding_is_unresolved_not_mismatched(self):
        verdict = evaluate_delta_coordinate(DeltaCoordinateBinding())
        self.assertEqual(verdict.state, DELTA_COORDINATE_UNRESOLVED)
        self.assertIsNone(verdict.binding_hash)

    def test_fully_declared_compatible_binding_hashes(self):
        verdict = evaluate_delta_coordinate(fixtures.coordinate_binding())
        self.assertEqual(verdict.state, DELTA_COORDINATE_COMPATIBLE)
        self.assertTrue(verdict.binding_hash.startswith("sha256:"))
        again = evaluate_delta_coordinate(fixtures.coordinate_binding())
        self.assertEqual(verdict.binding_hash, again.binding_hash)

    def test_benchmark_interval_mismatch_is_reported(self):
        binding = fixtures.coordinate_binding()
        binding = replace(binding, benchmark=replace(binding.benchmark,
                                                     interval_spec="CALENDAR_MONTH"))
        verdict = evaluate_delta_coordinate(binding)
        self.assertEqual(verdict.state, DELTA_COORDINATE_MISMATCH)
        self.assertIn("BENCHMARK_INTERVAL_INCOMPATIBLE", verdict.reasons)

    def test_substituting_the_benchmark_is_a_mismatch(self):
        binding = replace(fixtures.coordinate_binding(), benchmark_symbol="CAPITAL_OPPORTUNITY_SET")
        verdict = evaluate_delta_coordinate(binding)
        self.assertEqual(verdict.state, DELTA_COORDINATE_MISMATCH)
        self.assertIn("SCIENTIFIC_BENCHMARK_REMAINS_SPY", verdict.reasons)

    def test_unweighted_event_mean_is_named_and_refused(self):
        binding = replace(fixtures.coordinate_binding(), aggregation="UNWEIGHTED_EVENT_MEAN")
        verdict = evaluate_delta_coordinate(binding)
        self.assertEqual(verdict.state, DELTA_COORDINATE_MISMATCH)
        self.assertIn("UNWEIGHTED_EVENT_MEAN_DOES_NOT_DEFINE_DEPLOYMENT_VALUE", verdict.reasons)

    def test_terminal_treatment_needs_a_d19_reference(self):
        binding = replace(fixtures.coordinate_binding(), d19_reference=None)
        verdict = evaluate_delta_coordinate(binding)
        self.assertEqual(verdict.state, DELTA_COORDINATE_UNRESOLVED)
        self.assertIn("TERMINAL_TREATMENT_WITHOUT_D19_REFERENCE", verdict.reasons)


class ParameterInventoryTest(unittest.TestCase):
    def test_frozen_inventory_refuses_new_parameters(self):
        inventory = fixtures.parameter_inventory()
        with self.assertRaises(InventoryFrozen):
            inventory.add(fixtures.parameter_inventory(freeze=False)[fixtures.FEE_BPS])

    def test_instantiation_cannot_introduce_an_unlisted_parameter(self):
        inventory = fixtures.parameter_inventory()
        with self.assertRaises(InventoryFrozen):
            inventory.instantiate({"F4_SECRET_EXTRA_COST": (3.0, PROVENANCE_CALIBRATED)})

    def test_rule_hash_is_independent_of_central_values(self):
        inventory = fixtures.parameter_inventory()
        instantiated = inventory.instantiate(fixtures.CENTRAL_VALUES)
        self.assertEqual(recipe_hash(inventory.rule_document()),
                         recipe_hash(instantiated.rule_document()))

    def test_v1_assumed_value_without_a_margin_role_is_a_violation(self):
        parameter = EconomicParameter(
            parameter_id="F4_IMPACT", cost_component="F4_MARKET_IMPACT",
            unit="BPS", execution_regime="CONTINUOUS_INTRADAY",
            source_contract=fixtures.source_contract("impact"),
            uncertainty_role="NONE", central_provenance=PROVENANCE_V1_ASSUMED)
        self.assertIn("EXISTING_EXECUTION_PARAMETER_IS_NOT_AUTOMATIC_CALIBRATION_AUTHORITY",
                      joined(parameter.violations()))

    def test_route_a_source_minimum_does_not_transfer(self):
        contract = replace(fixtures.source_contract("x"),
                           multiple_source_rule="MINIMUM_ACROSS_SOURCES")
        self.assertIn("ROUTE_A_SOURCE_MINIMUM_DOES_NOT_TRANSFER_TO_EXPECTED_COST",
                      joined(contract.violations("p")))

    def test_outcome_bearing_evidence_class_is_refused(self):
        contract = replace(fixtures.source_contract("x"),
                           admissible_source_classes=("FORM4_TARGET_OUTCOMES",))
        self.assertIn("ENVELOPE_EVIDENCE_IS_TARGET_OUTCOME_BLIND",
                      joined(contract.violations("p")))

    def test_generic_intraday_evidence_is_not_open_calibration(self):
        parameter = EconomicParameter(
            parameter_id="F2_SPREAD", cost_component="F2_OPEN_ENTRY_CROSSING", unit="BPS",
            execution_regime="FIRST_REGULAR_SESSION_OPEN",
            source_contract=fixtures.source_contract(
                "half spread", applicability="GENERIC_INTRADAY_ALL_SESSION_POPULATION"),
            central_estimate=1.0, central_provenance=PROVENANCE_CALIBRATED,
            envelope_provenance_rule="SET")
        self.assertIn("GENERIC_INTRADAY_SPREAD_IS_NOT_AUTOMATIC_OPEN_CALIBRATION",
                      joined(parameter.violations()))


class KForwardRecipeTest(unittest.TestCase):
    def test_every_cost_class_must_be_modelled_or_authorised_zero(self):
        recipe = fixtures.k_forward_recipe()
        stripped = replace(recipe, authorised_zeros=recipe.authorised_zeros[:1])
        problems = joined(stripped.violations())
        self.assertIn("OMITTED_COST_IS_NOT_IMPLICIT_ZERO:F6_FINANCING_BORROW", problems)
        self.assertIn("OMITTED_COST_IS_NOT_IMPLICIT_ZERO:F7_RESIDUAL_CAPITAL_DRAG", problems)

    def test_complete_recipe_has_no_coverage_gap(self):
        self.assertEqual(fixtures.k_forward_recipe().violations(), [])

    def test_upper_quantile_estimator_is_refused(self):
        recipe = fixtures.k_forward_recipe()
        component = replace(recipe.components[0], estimator_kind="UPPER_QUANTILE")
        broken = replace(recipe, components=(component,) + recipe.components[1:])
        self.assertIn("NO_HIDDEN_CONSERVATISM_INSIDE_K_FORWARD", joined(broken.violations()))

    def test_prudential_markup_is_refused(self):
        recipe = fixtures.k_forward_recipe()
        component = replace(recipe.components[0], conservatism_markup=0.1)
        broken = replace(recipe, components=(component,) + recipe.components[1:])
        self.assertIn("NO_HIDDEN_CONSERVATISM_INSIDE_K_FORWARD", joined(broken.violations()))

    def test_program_cost_cannot_be_an_input_class(self):
        recipe = fixtures.k_forward_recipe()
        component = replace(recipe.components[0],
                            input_classes=("FROZEN_COST_PARAMETER", "PROGRAM_SUNK_COST"))
        broken = replace(recipe, components=(component,) + recipe.components[1:])
        self.assertIn("PROGRAM_COST_DOES_NOT_ENTER_MARKET_DEPLOYMENT_MEUE",
                      joined(broken.violations()))

    def test_consuming_a_parameter_outside_the_inventory_is_a_violation(self):
        recipe = fixtures.k_forward_recipe()
        component = replace(recipe.components[0], consumes=("F1_UNLISTED",))
        broken = replace(recipe, components=(component,) + recipe.components[1:])
        problems = joined(broken.parameter_violations(fixtures.parameter_inventory()))
        self.assertIn("PARAMETER_NOT_IN_FROZEN_INVENTORY:F1_UNLISTED", problems)

    def test_missing_parameter_value_raises_the_declared_failure_state(self):
        recipe = fixtures.k_forward_recipe()
        with self.assertRaises(CostInputUnavailable) as caught:
            recipe.expected_cost(0.0, fixtures.theta_state(), {})
        self.assertEqual(caught.exception.state, "K_FORWARD_PARAMETER_UNRESOLVED")

    def test_declared_dependence_is_checked_against_the_functional(self):
        recipe = fixtures.k_forward_recipe()
        liar = CostComponent(
            name="SECRETLY_DELTA_DEPENDENT", cost_class="F6_FINANCING_BORROW",
            applicability="ALWAYS", formula_statement="1000 * delta",
            functional=lambda delta, theta, params: 1000.0 * delta,
            input_classes=("FROZEN_COST_PARAMETER",))
        broken = replace(recipe, components=recipe.components + (liar,))
        problems = verify_dependence_declarations(broken, fixtures.theta_state(),
                                                 fixtures.CENTRAL_PARAMS)
        self.assertIn("SECRETLY_DELTA_DEPENDENT: DECLARED_DELTA_INDEPENDENT_BUT_VARIES",
                      joined(problems))

    def test_honest_recipe_passes_the_dependence_probe(self):
        problems = verify_dependence_declarations(fixtures.k_forward_recipe(),
                                                  fixtures.theta_state(),
                                                  fixtures.CENTRAL_PARAMS)
        self.assertEqual(problems, [])


class BEEERootTest(unittest.TestCase):
    def instance(self, params=None, theta=None):
        return PhiInstance(theta or fixtures.theta_state(), fixtures.k_forward_recipe(),
                          params or fixtures.CENTRAL_PARAMS, fixtures.effect_domain())

    def test_unique_root_agrees_with_the_affine_quotient(self):
        instance = self.instance()
        result = beee(instance)
        self.assertEqual(result.state, BEEE_UNIQUE_ROOT)
        self.assertAlmostEqual(result.value, beee_affine(instance), places=12)

    def test_root_is_where_phi_is_zero(self):
        instance = self.instance()
        result = beee(instance)
        self.assertLess(abs(instance.phi(result.value)), 1e-9)

    def test_no_root_on_the_declared_domain(self):
        domain = EffectDomain(lower=0.5, upper=1.0, nodes=51)
        result = solve_beee(lambda delta: 4_000_000.0 * delta - 3_929.82, domain)
        self.assertEqual(result.state, BEEE_NO_ECONOMIC_ROOT)
        self.assertIsNone(result.value)

    def test_two_roots_are_reported_as_nonunique(self):
        # Phi = -1 + 10*delta - 10*delta^2 crosses zero twice on [0, 1].
        result = solve_beee(lambda d: -1.0 + 10.0 * d - 10.0 * d * d,
                            EffectDomain(lower=0.0, upper=1.0, nodes=201))
        self.assertEqual(result.state, BEEE_NONUNIQUE_ROOT)
        self.assertEqual(result.root_count, 2)

    def test_single_crossing_of_a_decreasing_phi_is_nonmonotone(self):
        result = solve_beee(lambda d: 1.0 - 10.0 * d,
                            EffectDomain(lower=0.0, upper=1.0, nodes=201))
        self.assertEqual(result.state, BEEE_NONMONOTONE_MAPPING)
        self.assertIsNone(result.value)

    def test_affine_shortcut_refused_when_cost_depends_on_delta(self):
        recipe = fixtures.k_forward_recipe()
        component = CostComponent(
            name="DELTA_LINKED", cost_class="F6_FINANCING_BORROW", applicability="ALWAYS",
            formula_statement="5000 * delta", dependence=Dependence(delta=True),
            functional=lambda delta, theta, params: 5_000.0 * delta,
            input_classes=("FROZEN_COST_PARAMETER", "EFFECT_COORDINATE_DELTA"))
        broken = replace(recipe, components=recipe.components + (component,))
        instance = PhiInstance(fixtures.theta_state(), broken, fixtures.CENTRAL_PARAMS,
                               fixtures.effect_domain())
        with self.assertRaises(AffineShortcutUnavailable):
            beee_affine(instance)

    def test_affine_shortcut_refused_when_q_is_not_positive(self):
        theta = replace(fixtures.theta_state(), expected_deployed_exposure=0.0)
        with self.assertRaises(AffineShortcutUnavailable):
            beee_affine(self.instance(theta=theta))

    def test_undeclared_delta_dependence_still_cannot_reach_the_shortcut(self):
        recipe = fixtures.k_forward_recipe()
        liar = CostComponent(
            name="UNDECLARED_DELTA_LINK", cost_class="F6_FINANCING_BORROW",
            applicability="ALWAYS", formula_statement="5000 * delta",
            functional=lambda delta, theta, params: 5_000.0 * delta,
            input_classes=("FROZEN_COST_PARAMETER",))
        broken = replace(recipe, components=recipe.components + (liar,))
        instance = PhiInstance(fixtures.theta_state(), broken, fixtures.CENTRAL_PARAMS,
                               fixtures.effect_domain())
        with self.assertRaises(AffineShortcutUnavailable):
            beee_affine(instance)


class MarginTest(unittest.TestCase):
    def margin(self, scenarios=None, inventory=None, additional=()):
        return m_economic(fixtures.theta_state(), fixtures.k_forward_recipe(),
                          fixtures.effect_domain(), scenarios or fixtures.scenario_set(),
                          inventory or fixtures.parameter_inventory().instantiate(
                              fixtures.CENTRAL_VALUES),
                          additional)

    def test_margin_is_the_adverse_beee_increment(self):
        result = self.margin()
        self.assertTrue(result.resolved)
        central = result.beee_central.value
        adverse = result.beee_by_scenario["s_1_opening_regime_worse"].value
        self.assertAlmostEqual(result.value, adverse - central, places=12)

    def test_margin_is_labelled_a_freeze_candidate(self):
        self.assertEqual(self.margin().functional_status, "FREEZE_CANDIDATE_NOT_AUTHORITY")

    def test_uncharged_model_risk_blocks_the_margin(self):
        scenarios = fixtures.scenario_set()
        central, adverse = scenarios.scenarios
        # Adverse scenario moves the spread but forgets the impact coefficient.
        values = dict(fixtures.CENTRAL_PARAMS)
        values[fixtures.OPEN_HALF_SPREAD_BPS] = 2.0
        partial = replace(adverse, parameter_values=values)
        result = self.margin(replace(scenarios, scenarios=(central, partial)))
        self.assertEqual(result.state, M_ECONOMIC_ENVELOPE_UNRESOLVED)
        self.assertIn("UNCHARGED_MODEL_RISK:" + fixtures.IMPACT_BPS_AT_FULL_PARTICIPATION,
                      joined(result.violations))

    def test_no_adverse_scenario_means_no_envelope(self):
        scenarios = fixtures.scenario_set()
        result = self.margin(replace(scenarios, scenarios=(scenarios.scenarios[0],)))
        self.assertEqual(result.state, M_ECONOMIC_ENVELOPE_UNRESOLVED)
        self.assertIsNone(result.value)

    def test_unjustified_cartesian_worst_case_is_refused(self):
        scenarios = replace(fixtures.scenario_set(),
                            construction="UNRESTRICTED_CARTESIAN_ENDPOINTS")
        self.assertIn("NO_UNJUSTIFIED_CARTESIAN_WORST_CASE", joined(scenarios.violations()))

    def test_adverse_scenario_without_dependence_representation_is_refused(self):
        scenarios = fixtures.scenario_set()
        naked = replace(scenarios.scenarios[1], dependence_representation="")
        problems = joined(replace(scenarios,
                                  scenarios=(scenarios.scenarios[0], naked)).violations())
        self.assertIn("UNKNOWN_PARAMETER_DEPENDENCE_IS_NOT_ZERO_DEPENDENCE", problems)

    def test_favourable_scenario_cannot_masquerade_as_adverse(self):
        scenarios = fixtures.scenario_set()
        values = dict(fixtures.ADVERSE_PARAMS)
        values[fixtures.OPEN_HALF_SPREAD_BPS] = 0.5  # cheaper than central
        wrong_side = replace(scenarios.scenarios[1], parameter_values=values)
        inventory = fixtures.parameter_inventory().instantiate(fixtures.CENTRAL_VALUES)
        problems = joined(replace(scenarios, scenarios=(scenarios.scenarios[0], wrong_side))
                          .direction_violations(inventory))
        self.assertIn("M_ECONOMIC_USES_ECONOMICALLY_ADVERSE_SIDE", problems)

    def test_additional_margin_component_needs_a_non_overlap_proof(self):
        result = self.margin(additional=(MarginComponent("REGIME_SHIFT_RISK", 0.001,
                                                         provenance="fixture"),))
        self.assertIn("ADDITIONAL_MARGIN_REQUIRES_NON_OVERLAP_PROOF", joined(result.violations))

    def test_better_calibration_narrows_the_margin(self):
        """Envelope contract s5: narrower independent evidence lowers the margin."""
        wide = self.margin()
        scenarios = fixtures.scenario_set()
        tighter_values = dict(fixtures.CENTRAL_PARAMS)
        tighter_values[fixtures.OPEN_HALF_SPREAD_BPS] = 1.2
        tighter_values[fixtures.IMPACT_BPS_AT_FULL_PARTICIPATION] = 12.0
        tighter_values[fixtures.IMPACT_REFERENCE_PARTICIPATION] = 0.04
        tighter = replace(scenarios.scenarios[1], parameter_values=tighter_values)
        narrow = self.margin(replace(scenarios, scenarios=(scenarios.scenarios[0], tighter)))
        self.assertTrue(narrow.resolved)
        self.assertLess(narrow.value, wide.value)


class RiskPartitionTest(unittest.TestCase):
    def test_clean_partition_has_no_violations(self):
        self.assertEqual(fixtures.risk_partition().violations(), [])

    def test_same_risk_in_both_homes_invalidates_the_recipe(self):
        partition = RiskPartition(fixtures.risk_partition().claims + (
            RiskClaim("OPENING_LIQUIDITY_COEFFICIENT_MODEL_RISK", "K_FORWARD",
                      "also charged as an expected cost"),))
        self.assertIn("FRICTION_MARGIN_DOUBLE_COUNT:OPENING_LIQUIDITY_COEFFICIENT_MODEL_RISK",
                      joined(partition.violations()))

    def test_documented_non_overlap_decomposition_is_permitted(self):
        proof = "entry leg charged in K_forward, exit leg uncertainty charged in the margin"
        partition = RiskPartition((
            RiskClaim("SPLIT_RISK", "K_FORWARD", "entry leg", non_overlap_proof=proof),
            RiskClaim("SPLIT_RISK", "M_ECONOMIC", "exit leg", non_overlap_proof=proof),
        ))
        self.assertEqual(partition.violations(), [])

    def test_program_cost_cannot_be_claimed_at_all(self):
        partition = RiskPartition((RiskClaim("PROGRAM_TCO", "K_FORWARD", "build cost"),))
        self.assertIn("PROGRAM_COST_DOES_NOT_ENTER_MARKET_DEPLOYMENT_MEUE",
                      joined(partition.violations()))

    def test_statistical_uncertainty_is_not_an_economic_margin(self):
        partition = RiskPartition((
            RiskClaim("STATISTICAL_STANDARD_ERROR", "M_ECONOMIC", "se of delta_hat"),))
        self.assertIn("MARGIN_IS_NOT_STATISTICAL_UNCERTAINTY", joined(partition.violations()))


class RecipeAssemblyTest(unittest.TestCase):
    def test_meue_is_beee_plus_margin(self):
        result = fixtures.meue_recipe().evaluate(fixtures.theta_state())
        self.assertAlmostEqual(result.meue, result.beee.value + result.margin.value, places=12)

    def test_uncalibrated_inputs_keep_the_recipe_provisional(self):
        result = fixtures.meue_recipe().evaluate(fixtures.theta_state())
        self.assertEqual(result.recipe_state, RECIPE_PROVISIONAL)
        self.assertIn("EXISTING_EXECUTION_PARAMETER_IS_NOT_AUTOMATIC_CALIBRATION_AUTHORITY",
                      joined(result.notes))
        self.assertFalse(result.consumable)

    def test_recipe_is_consumable_only_with_calibration_and_a_frozen_functional(self):
        values = {key: (value, PROVENANCE_CALIBRATED)
                  for key, (value, _) in fixtures.CENTRAL_VALUES.items()}
        inventory = fixtures.parameter_inventory().instantiate(values)
        # A CALIBRATED label alone is syntactic; see
        # test_economic_v2_consolidation.py::ProvenanceAuthenticityTest for the
        # dedicated coverage of what happens when this binding is withheld.
        inventory = inventory.bind_provenance({
            key: ProvenanceBinding(version="v1", as_of="2026-09-19",
                                   authority="TEST_AUTHORITY",
                                   dataset_fingerprint="sha256:test-fixture-only",
                                   validation_state=PROVENANCE_VALIDATION_INDEPENDENTLY_VALIDATED)
            for key in values})
        recipe = fixtures.meue_recipe(inventory=inventory,
                                      margin_functional_status=FUNCTIONAL_FROZEN)
        result = recipe.evaluate(fixtures.theta_state())
        self.assertEqual(result.recipe_state, RECIPE_CONSUMABLE)
        self.assertTrue(result.consumable)

    def test_evaluation_is_deterministic_and_idempotent(self):
        recipe = fixtures.meue_recipe()
        first = recipe.evaluate(fixtures.theta_state())
        second = recipe.evaluate(fixtures.theta_state())
        self.assertEqual(first.to_dict(), second.to_dict())

    def test_recipe_hash_is_stable_and_value_independent(self):
        base = fixtures.meue_recipe()
        other = fixtures.meue_recipe(
            inventory=fixtures.parameter_inventory().instantiate(fixtures.CENTRAL_VALUES))
        self.assertEqual(base.fingerprint(), other.fingerprint())

    def test_structural_defect_yields_no_numbers_at_all(self):
        recipe = fixtures.meue_recipe(
            coordinate=replace(fixtures.coordinate_binding(), benchmark_symbol="QQQ"))
        result = recipe.evaluate(fixtures.theta_state())
        self.assertEqual(result.recipe_state, RECIPE_INVALID)
        self.assertIsNone(result.meue)
        self.assertIn("SCIENTIFIC_BENCHMARK_REMAINS_SPY", joined(result.violations))

    def test_recipe_document_refuses_to_embed_an_outcome(self):
        with self.assertRaises(RecipeNotOutcomeBlind):
            recipe_hash({"recipe_id": "x", "nested": {"delta_hat": 0.02}})

    def test_naive_q_provenance_is_refused(self):
        theta = replace(fixtures.theta_state(), q_provenance=Q_PROVENANCE_NAIVE_ANNUALISATION)
        result = fixtures.meue_recipe().evaluate(theta)
        self.assertEqual(result.recipe_state, RECIPE_INVALID)
        self.assertIn("Q_IS_NEVER_NAIVE_CAPITAL_TIMES_EVENT_COUNT", joined(result.violations))


class ThetaOrderingTest(unittest.TestCase):
    def test_size_search_after_a_threshold_is_refused(self):
        recipe = fixtures.meue_recipe()
        session = EvaluationSession("SESSION_1", recipe.theta_rule)
        recipe.evaluate(fixtures.theta_state(), session)
        self.assertEqual(session.thresholds_observed, 1)
        bigger = fixtures.theta_state(theta_id="THETA_BIGGER", capital=5_000_000.0,
                                     q=20_000_000.0)
        with self.assertRaises(ThetaFeedbackViolation) as caught:
            session.admit(bigger)
        self.assertIn("NO_SIZE_SEARCH_TO_MAKE_MEUE_ATTAINABLE", str(caught.exception))

    def test_predeclared_scenarios_may_both_be_evaluated(self):
        rule = fixtures.theta_rule(scenarios=("THETA_TEST", "THETA_BIGGER"))
        recipe = fixtures.meue_recipe(theta_rule=rule)
        session = EvaluationSession("SESSION_2", rule)
        first = recipe.evaluate(fixtures.theta_state(), session)
        second = recipe.evaluate(
            fixtures.theta_state(theta_id="THETA_BIGGER", capital=2_000_000.0,
                                 q=8_000_000.0), session)
        self.assertIsNotNone(first.meue)
        self.assertIsNotNone(second.meue)

    def test_an_undeclared_scenario_is_not_admitted(self):
        rule = fixtures.theta_rule(scenarios=("THETA_TEST",))
        session = EvaluationSession("SESSION_3", rule)
        with self.assertRaises(ThetaFeedbackViolation):
            session.admit(fixtures.theta_state(theta_id="THETA_OTHER"))


class CapacityTest(unittest.TestCase):
    def schedule(self, ceilings):
        return {symbol: CapacityLimit(symbol, adv, 0.05,
                                      "PERMITTED_PRE_OUTCOME_PANEL_LOOKBACK", "2026-09-18")
                for symbol, adv in ceilings.items()}

    def test_no_clipping_leaves_the_policy_unchanged(self):
        outcome = apply_capacity({"AAA": 10_000.0}, self.schedule({"AAA": 10_000_000.0}))
        self.assertEqual(outcome.policy_consequence, POLICY_UNCHANGED)
        self.assertEqual(outcome.truncated_total, 0.0)

    def test_homogeneous_clipping_preserves_relative_weights(self):
        outcome = apply_capacity({"AAA": 100_000.0, "BBB": 200_000.0},
                                 self.schedule({"AAA": 1_000_000.0, "BBB": 2_000_000.0}))
        self.assertEqual(outcome.policy_consequence, POLICY_SCALED_HOMOGENEOUSLY)
        self.assertTrue(outcome.relative_weights_preserved)
        self.assertAlmostEqual(outcome.homogeneous_scale, 0.5, places=12)

    def test_uneven_clipping_is_a_new_policy_version(self):
        outcome = apply_capacity({"AAA": 100_000.0, "BBB": 100_000.0},
                                 self.schedule({"AAA": 100_000_000.0, "BBB": 1_000_000.0}))
        self.assertEqual(outcome.policy_consequence, NEW_POLICY_VERSION)
        self.assertFalse(outcome.relative_weights_preserved)

    def test_missing_liquidity_reference_is_not_unlimited_capacity(self):
        outcome = apply_capacity({"AAA": 100_000.0}, {})
        self.assertEqual(outcome.granted["AAA"], 0.0)
        self.assertIn("NO_LIQUIDITY_REFERENCE_IS_NOT_UNLIMITED_CAPACITY",
                      joined(outcome.violations))

    def test_exposure_budget_reports_its_provenance_and_clipping(self):
        budget = ExposureBudget((100_000.0,) * 40, "ONE_CALENDAR_YEAR",
                                "NON_OVERLAPPING_BY_CONSTRUCTION")
        self.assertEqual(budget.q, 4_000_000.0)
        self.assertEqual(budget.provenance, "FROZEN_ALLOCATION_CONSTRUCTOR")
        self.assertEqual(budget.violations(), [])

    def test_exposure_budget_surfaces_a_policy_version_change(self):
        budget = ExposureBudget((100_000.0, 50_000.0), "ONE_CALENDAR_YEAR", "OVERLAP_CAPPED",
                                any_clipping=True, policy_version_changed=True)
        self.assertIn(NEW_POLICY_VERSION, joined(budget.violations()))


class EconomicGateTest(unittest.TestCase):
    def setUp(self):
        self.recipe = fixtures.meue_recipe()
        self.theta = fixtures.theta_state()
        self.meue_result = self.recipe.evaluate(self.theta)
        self.clean_interaction = PortfolioInteraction(overlap_fraction=0.0, residual_beta=0.0,
                                                     correlation_to_book=0.1)

    def estimate(self, delta, half_width=0.0005, label=EVIDENCE_DEVELOPMENT, p_value=None):
        return EffectEstimate(delta_hat=delta, lower=delta - half_width,
                              upper=delta + half_width, confidence_level=0.95,
                              evidence_label=label, sample_provenance="SYNTHETIC_FIXTURE",
                              event_count=400, p_value=p_value)

    def test_effect_interval_above_the_threshold_continues(self):
        verdict = economic_gate(self.estimate(0.01), self.meue_result, self.theta,
                                self.clean_interaction)
        self.assertEqual(verdict.verdict, CONTINUE)
        self.assertGreater(verdict.margin_of_safety, 0.0)

    def test_significant_but_uneconomic_effect_is_killed(self):
        """A tiny p-value cannot rescue an effect below the economic threshold."""
        verdict = economic_gate(self.estimate(0.0005, half_width=0.00005, p_value=1e-9),
                                self.meue_result, self.theta, self.clean_interaction)
        self.assertEqual(verdict.verdict, KILL)
        self.assertEqual(verdict.reason, "ECONOMICALLY_DOMINATED_ACROSS_WHOLE_INTERVAL")
        self.assertLess(verdict.upper_incremental, verdict.meue)

    def test_uncertainty_straddling_the_threshold_is_no_trade(self):
        meue = self.meue_result.meue
        verdict = economic_gate(self.estimate(meue, half_width=0.002), self.meue_result,
                                self.theta, self.clean_interaction)
        self.assertEqual(verdict.verdict, NO_TRADE)
        self.assertEqual(verdict.reason, "UNCERTAINTY_STRADDLES_ECONOMIC_THRESHOLD")

    def test_undeclared_residual_beta_blocks_the_lane(self):
        verdict = economic_gate(self.estimate(0.05), self.meue_result, self.theta,
                                PortfolioInteraction(0.0, residual_beta=None))
        self.assertEqual(verdict.verdict, NO_TRADE)
        self.assertIn("RESIDUAL_BETA_UNDECLARED_HIDDEN_MARKET_EXPOSURE",
                      joined(verdict.violations))

    def test_portfolio_overlap_reduces_the_incremental_effect(self):
        overlapped = PortfolioInteraction(overlap_fraction=0.75, residual_beta=0.0)
        verdict = economic_gate(self.estimate(0.01), self.meue_result, self.theta, overlapped)
        self.assertAlmostEqual(verdict.delta_incremental, 0.0025, places=12)

    def test_overlap_can_turn_a_continue_into_a_kill(self):
        standalone = economic_gate(self.estimate(0.004, half_width=0.0005), self.meue_result,
                                   self.theta, self.clean_interaction)
        self.assertEqual(standalone.verdict, CONTINUE)
        overlapped = economic_gate(self.estimate(0.004, half_width=0.0005), self.meue_result,
                                   self.theta,
                                   PortfolioInteraction(0.9, residual_beta=0.0))
        self.assertEqual(overlapped.verdict, KILL)

    def test_capacity_driven_policy_change_blocks_the_decision(self):
        outcome = apply_capacity(
            {"AAA": 100_000.0, "BBB": 100_000.0},
            {"AAA": CapacityLimit("AAA", 100_000_000.0, 0.05,
                                  "PERMITTED_PRE_OUTCOME_PANEL_LOOKBACK"),
             "BBB": CapacityLimit("BBB", 1_000_000.0, 0.05,
                                  "PERMITTED_PRE_OUTCOME_PANEL_LOOKBACK")})
        verdict = economic_gate(self.estimate(0.05), self.meue_result, self.theta,
                                self.clean_interaction, outcome)
        self.assertEqual(verdict.verdict, NO_TRADE)
        self.assertEqual(verdict.reason, NEW_POLICY_VERSION)

    def test_zero_exposure_cannot_produce_a_trade(self):
        theta = replace(self.theta, expected_deployed_exposure=0.0)
        verdict = economic_gate(self.estimate(0.05), self.meue_result, theta,
                                self.clean_interaction)
        self.assertEqual(verdict.verdict, NO_TRADE)
        self.assertEqual(verdict.reason, "NO_DEPLOYABLE_EXPOSURE")

    def test_historical_evidence_never_claims_forward_confirmation(self):
        verdict = economic_gate(self.estimate(0.01), self.meue_result, self.theta,
                                self.clean_interaction)
        self.assertEqual(verdict.authority, AUTHORITY_DEVELOPMENT_ONLY)

    def test_no_verdict_authorises_real_capital(self):
        for delta in (0.0001, 0.01, 0.1):
            verdict = economic_gate(self.estimate(delta), self.meue_result, self.theta,
                                    self.clean_interaction)
            self.assertEqual(verdict.capital_authority, PAPER_SHADOW_ONLY)

    def test_invalid_recipe_produces_no_trade_not_an_exception(self):
        broken = fixtures.meue_recipe(
            coordinate=replace(fixtures.coordinate_binding(), benchmark_symbol="QQQ"))
        verdict = economic_gate(self.estimate(0.05), broken.evaluate(self.theta), self.theta,
                                self.clean_interaction)
        self.assertEqual(verdict.verdict, NO_TRADE)
        self.assertEqual(verdict.reason, "ECONOMIC_RECIPE_NOT_EVALUABLE")

    def test_chain_records_every_stage(self):
        verdict = economic_gate(self.estimate(0.01), self.meue_result, self.theta,
                                self.clean_interaction)
        stages = [step["step"] for step in verdict.chain]
        self.assertEqual(stages, ["SCIENTIFIC_EFFECT", "ECONOMIC_THRESHOLD",
                                  "EXECUTABLE_EXPOSURE", "PORTFOLIO_INTERACTION",
                                  "NET_EXPECTED_VALUE"])

    def test_net_expected_value_is_gross_minus_expected_forward_cost(self):
        verdict = economic_gate(self.estimate(0.01), self.meue_result, self.theta,
                                self.clean_interaction)
        expected_cost = self.theta.expected_deployed_exposure * self.meue_result.beee.value
        self.assertAlmostEqual(verdict.net_expected_value,
                               self.theta.expected_deployed_exposure * 0.01 - expected_cost,
                               places=6)

    def test_estimator_off_the_frozen_coordinate_is_refused(self):
        estimate = replace(self.estimate(0.05), estimator_form="UNWEIGHTED_EVENT_MEAN")
        verdict = economic_gate(estimate, self.meue_result, self.theta, self.clean_interaction)
        self.assertEqual(verdict.verdict, NO_TRADE)
        self.assertIn("ESTIMATOR_NOT_ON_FROZEN_EFFECT_COORDINATE", joined(verdict.violations))


if __name__ == "__main__":
    unittest.main()
