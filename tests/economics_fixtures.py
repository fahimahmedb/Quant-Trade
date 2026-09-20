"""Illustrative economic recipe used by the tests.

EVERY NUMBER IN THIS FILE IS A TEST FIXTURE WITH NO SCIENTIFIC AUTHORITY.

No Form 4 cost coefficient is asserted anywhere in ``src/quant/economics``, and
nothing here may be promoted into a calibration. The values exist so the engine's
arithmetic, failure states and refusals can be exercised; their provenance is
declared as ``ASSUMED_V1_EXECUTION_PARAMETER`` or ``CALIBRATED...`` purely to
drive the code paths that treat those classes differently.
"""

from __future__ import annotations

import math

from quant.economics import (ADVERSE_CATEGORY_BORROW_FINANCING_DETERIORATION,
                             ADVERSE_CATEGORY_CAPACITY_REDUCTION,
                             ADVERSE_CATEGORY_CORRELATED_LIQUIDITY_DETERIORATION,
                             ADVERSE_CATEGORY_EXECUTION_REGIME_MISMATCH,
                             ADVERSE_CATEGORY_SPREAD_WIDENING_WITH_IMPACT_INCREASE,
                             ALLOCATION_WEIGHTED_RATIO, AuthorisedScenarioExclusion,
                             AuthorisedZero, CostComponent,
                             CostScenario, DeltaCoordinateBinding, Dependence,
                             EconomicParameter, EffectDomain, JointScenarioSet,
                             KForwardRecipe, MEUERecipe, ParameterInventory, ReturnConvention,
                             RiskClaim, RiskPartition, SourceContract, ThetaSelectionRule,
                             ThetaState)
from quant.economics.frictions import (COST_SHAPE_PER_NOTIONAL, COST_SHAPE_SPREAD_CROSSING,
                                       COST_SHAPE_SQRT_IMPACT, SIGN_COST_POSITIVE,
                                       UNIT_ACCOUNT_CURRENCY)
from quant.economics.states import PROVENANCE_CALIBRATED, PROVENANCE_V1_ASSUMED
from quant.economics.scenarios import SCENARIO_ADVERSE, SCENARIO_CENTRAL
from quant.economics.theta import Q_PROVENANCE_ALLOCATION_CONSTRUCTOR


TEST_AUTHORITY = "TEST_FIXTURE_ONLY_NOT_A_GOVERNANCE_AUTHORITY"

FEE_BPS = "F1_EXPLICIT_FEE_BPS"
OPEN_HALF_SPREAD_BPS = "F2_OPEN_HALF_SPREAD_BPS"
IMPACT_BPS_AT_FULL_PARTICIPATION = "F4_IMPACT_BPS_AT_FULL_PARTICIPATION"
IMPACT_REFERENCE_PARTICIPATION = "F4_REFERENCE_PARTICIPATION"
EXIT_BPS = "F5_EXIT_EXECUTION_BPS"


def source_contract(estimand: str, applicability: str = "FORM4_OPEN_ENTRY_POPULATION",
                    sources: tuple[str, ...] =
                    ("EXTERNAL_MICROSTRUCTURE_LITERATURE",)) -> SourceContract:
    return SourceContract(
        economic_estimand=estimand,
        population_applicability=applicability,
        admissible_source_classes=sources,
        applicability_exclusion_rule="EXCLUDE_SOURCES_SELECTED_USING_TARGET_OUTCOMES",
        multiple_source_rule="ORDERED_APPLICABILITY_TIERS",
        source_priority_tiers=("TIER_1_OPENING_REGIME_SPECIFIC", "TIER_2_BROAD_MARKET"),
        evidence_update_rule="PREAUTHORISED_UPDATE_BEFORE_OUTCOME_EXPOSURE_ONLY",
    )


def parameter_inventory(freeze: bool = True) -> ParameterInventory:
    inventory = ParameterInventory("FORM4_ROUTE_B_COST_INVENTORY_TEST")
    inventory.extend([
        EconomicParameter(
            parameter_id=FEE_BPS, cost_component="F1_EXPLICIT_FEES",
            unit="BPS_OF_TRADED_NOTIONAL", execution_regime="NOT_EXECUTION_DEPENDENT",
            source_contract=source_contract("expected explicit fee per unit traded notional",
                                            applicability="BROKER_SCHEDULE_POPULATION"),
            envelope_provenance_rule="PUBLISHED_SCHEDULE_RANGE"),
        EconomicParameter(
            parameter_id=OPEN_HALF_SPREAD_BPS, cost_component="F2_OPEN_ENTRY_CROSSING",
            unit="BPS_OF_ENTRY_NOTIONAL", execution_regime="FIRST_REGULAR_SESSION_OPEN",
            source_contract=source_contract(
                "expected half-spread paid crossing at the first authorized open",
                applicability="FIRST_OPEN_AFTER_PUBLIC_OBSERVABILITY"),
            envelope_provenance_rule="OPENING_REGIME_SPECIFIC_PLAUSIBLE_SET"),
        EconomicParameter(
            parameter_id=IMPACT_BPS_AT_FULL_PARTICIPATION, cost_component="F4_MARKET_IMPACT",
            unit="BPS_OF_ENTRY_NOTIONAL_AT_REFERENCE_PARTICIPATION",
            execution_regime="FIRST_REGULAR_SESSION_OPEN",
            dependence=Dependence(liquidity=True, participation=True),
            source_contract=source_contract(
                "expected impact at the reference participation rate",
                applicability="FIRST_OPEN_AFTER_PUBLIC_OBSERVABILITY"),
            envelope_provenance_rule="OPENING_REGIME_SPECIFIC_PLAUSIBLE_SET"),
        EconomicParameter(
            parameter_id=IMPACT_REFERENCE_PARTICIPATION, cost_component="F4_MARKET_IMPACT",
            unit="FRACTION_OF_ADV", execution_regime="FIRST_REGULAR_SESSION_OPEN",
            dependence=Dependence(liquidity=True, participation=True),
            source_contract=source_contract(
                "participation rate at which the impact coefficient is expressed",
                applicability="FIRST_OPEN_AFTER_PUBLIC_OBSERVABILITY"),
            envelope_provenance_rule="OPENING_REGIME_SPECIFIC_PLAUSIBLE_SET",
            # A thinner reference book is the adverse side here: lowering the
            # reference participation raises modelled impact.
            adverse_direction="LOWER_IS_ADVERSE"),
        EconomicParameter(
            parameter_id=EXIT_BPS, cost_component="F5_EXIT_EXECUTION",
            unit="BPS_OF_EXIT_NOTIONAL", execution_regime="AUTHORIZED_EXIT_REGIME",
            source_contract=source_contract("expected round-trip exit execution loss",
                                            applicability="AUTHORIZED_EXIT_POPULATION"),
            envelope_provenance_rule="EXIT_REGIME_PLAUSIBLE_SET"),
    ])
    if freeze:
        inventory.freeze()
    return inventory


#: Central values. Fixture only: the two opening-regime coefficients carry
#: ``ASSUMED_V1_EXECUTION_PARAMETER`` provenance precisely so the engine has to
#: charge their model risk in ``M_economic``.
CENTRAL_VALUES = {
    FEE_BPS: (0.5, PROVENANCE_CALIBRATED),
    OPEN_HALF_SPREAD_BPS: (1.0, PROVENANCE_V1_ASSUMED),
    IMPACT_BPS_AT_FULL_PARTICIPATION: (10.0, PROVENANCE_V1_ASSUMED),
    IMPACT_REFERENCE_PARTICIPATION: (0.05, PROVENANCE_V1_ASSUMED),
    EXIT_BPS: (1.5, PROVENANCE_CALIBRATED),
}

CENTRAL_PARAMS = {key: value for key, (value, _) in CENTRAL_VALUES.items()}
ADVERSE_PARAMS = dict(CENTRAL_PARAMS)
ADVERSE_PARAMS[OPEN_HALF_SPREAD_BPS] = 2.0
ADVERSE_PARAMS[IMPACT_BPS_AT_FULL_PARTICIPATION] = 20.0
ADVERSE_PARAMS[IMPACT_REFERENCE_PARTICIPATION] = 0.025


def _fees(delta, theta, params):
    # Entry plus exit turnover, both at the deployed exposure.
    return params[FEE_BPS] / 10_000.0 * 2.0 * theta.expected_deployed_exposure


def _crossing(delta, theta, params):
    return params[OPEN_HALF_SPREAD_BPS] / 10_000.0 * theta.expected_deployed_exposure


def _impact(delta, theta, params):
    participation = theta.participation or 0.0
    reference = params[IMPACT_REFERENCE_PARTICIPATION]
    if reference <= 0:
        return 0.0
    shape = math.sqrt(min(participation, 1.0) / reference)
    return (params[IMPACT_BPS_AT_FULL_PARTICIPATION] * shape / 10_000.0
            * theta.expected_deployed_exposure)


def _exit(delta, theta, params):
    return params[EXIT_BPS] / 10_000.0 * theta.expected_deployed_exposure


def k_forward_recipe() -> KForwardRecipe:
    return KForwardRecipe(
        recipe_id="K_FORWARD_FORM4_ROUTE_B_TEST",
        components=(
            CostComponent(
                name="EXPLICIT_FEES", cost_class="F1_EXPLICIT_FEES",
                unit=UNIT_ACCOUNT_CURRENCY, sign_convention=SIGN_COST_POSITIVE,
                applicability="ALWAYS_APPLICABLE_ON_ENTRY_AND_EXIT",
                functional=_fees,
                formula_statement="fee_bps/1e4 * 2 * Q(theta)",
                input_classes=("FROZEN_COST_PARAMETER", "EXPECTED_DEPLOYED_EXPOSURE_Q"),
                consumes=(FEE_BPS,), shape=COST_SHAPE_PER_NOTIONAL),
            CostComponent(
                name="OPEN_ENTRY_CROSSING", cost_class="F2_OPEN_ENTRY_CROSSING",
                applicability="FIRST_AUTHORIZED_REGULAR_SESSION_OPEN",
                functional=_crossing,
                formula_statement="half_spread_bps/1e4 * Q(theta)",
                input_classes=("FROZEN_COST_PARAMETER", "EXPECTED_DEPLOYED_EXPOSURE_Q"),
                consumes=(OPEN_HALF_SPREAD_BPS,), shape=COST_SHAPE_SPREAD_CROSSING),
            CostComponent(
                name="MARKET_IMPACT", cost_class="F4_MARKET_IMPACT",
                applicability="FIRST_AUTHORIZED_REGULAR_SESSION_OPEN_WITH_POSITIVE_"
                              "PARTICIPATION",
                functional=_impact,
                formula_statement="impact_bps/1e4 * sqrt(participation/reference) * Q(theta)",
                input_classes=("FROZEN_COST_PARAMETER", "PARTICIPATION_DERIVED_FROM_THETA",
                               "PERMITTED_LIQUIDITY_REFERENCE",
                               "EXPECTED_DEPLOYED_EXPOSURE_Q"),
                consumes=(IMPACT_BPS_AT_FULL_PARTICIPATION, IMPACT_REFERENCE_PARTICIPATION),
                dependence=Dependence(liquidity=True, participation=True),
                shape=COST_SHAPE_SQRT_IMPACT),
            CostComponent(
                name="EXIT_EXECUTION", cost_class="F5_EXIT_EXECUTION",
                applicability="AUTHORIZED_EXIT_CONVENTION",
                functional=_exit,
                formula_statement="exit_bps/1e4 * Q(theta)",
                input_classes=("FROZEN_COST_PARAMETER", "EXPECTED_DEPLOYED_EXPOSURE_Q"),
                consumes=(EXIT_BPS,), shape=COST_SHAPE_SPREAD_CROSSING),
        ),
        authorised_zeros=(
            AuthorisedZero("F3_OPEN_ENTRY_SLIPPAGE", TEST_AUTHORITY,
                           "fixture: opening slippage beyond the crossing term is not "
                           "separately modelled in this test recipe"),
            AuthorisedZero("F6_FINANCING_BORROW", TEST_AUTHORITY,
                           "fixture: unlevered long-only exposure, no borrow"),
            AuthorisedZero("F7_RESIDUAL_CAPITAL_DRAG", TEST_AUTHORITY,
                           "fixture: residual capital drag not admitted by this accounting "
                           "convention"),
        ))


def coordinate_binding() -> DeltaCoordinateBinding:
    convention = ReturnConvention(
        return_definition="SIMPLE_SINGLE_PERIOD",
        interval_spec="FIRST_AUTHORIZED_OPEN_TO_AUTHORIZED_EXIT_CLOSE",
        corporate_action_convention="TOTAL_RETURN_ADJUSTED_FOR_SPLITS_AND_DISTRIBUTIONS",
        terminal_treatment="DELISTING_AT_LAST_AUTHORIZED_PRICE")
    return DeltaCoordinateBinding(
        security=convention, benchmark=convention, benchmark_symbol="SPY",
        aggregation=ALLOCATION_WEIGHTED_RATIO,
        allocation_constructor_id="A_CONSTRUCTOR_TEST",
        allocation_weight_precedes_outcome=True,
        d19_reference="governance/D19_ADVERSE_TREATMENT_SPEC_DEPENDENCY.md")


def theta_state(theta_id: str = "THETA_TEST", capital: float = 1_000_000.0,
                q: float = 4_000_000.0, participation: float = 0.02) -> ThetaState:
    return ThetaState(
        theta_id=theta_id, capital=capital, geometry_id="G_TEST",
        allocation_constructor_id="A_CONSTRUCTOR_TEST",
        allocation_state_id="PRE_OUTCOME_STATE_TEST",
        execution_policy_id="FIRST_OPEN_ENTRY_AUTHORIZED_EXIT",
        expected_deployed_exposure=q,
        q_provenance=Q_PROVENANCE_ALLOCATION_CONSTRUCTOR,
        liquidity_reference=50_000_000.0, participation=participation,
        evaluation_regime="ONE_CALENDAR_YEAR")


def theta_rule(scenarios: tuple[str, ...] = ()) -> ThetaSelectionRule:
    return ThetaSelectionRule(
        rule_id="THETA_SELECTION_TEST",
        upstream_authorities=("D07_GEOMETRY", "A_CONSTRUCTOR_TEST", "C_CLAIM_DOMAIN"),
        capital_selection_rule="SINGLE_AUTHORIZED_CAPITAL_POINT_INSIDE_C_CLAIM",
        liquidity_inputs=("PERMITTED_PRE_OUTCOME_PANEL_LOOKBACK",),
        declared_scenarios=scenarios,
        multiplicity_semantics="PREDECLARED_SCENARIOS_REPORTED_JOINTLY"
        if len(scenarios) > 1 else None)


def scenario_set() -> JointScenarioSet:
    return JointScenarioSet(
        set_id="S_COST_TEST",
        construction="COHERENT_JOINT_SCENARIOS",
        update_rule="UPDATE_ONLY_UNDER_PREAUTHORISED_EVIDENCE_RULE_BEFORE_OUTCOME_EXPOSURE",
        scenarios=(
            CostScenario("s_0", SCENARIO_CENTRAL, dict(CENTRAL_PARAMS),
                         provenance=TEST_AUTHORITY),
            CostScenario(
                "s_1_opening_regime_worse", SCENARIO_ADVERSE, dict(ADVERSE_PARAMS),
                coherence_justification="a thinner opening book widens the crossing cost and "
                                        "steepens impact together; they are not independent",
                dependence_representation="SHARED_OPENING_LIQUIDITY_FACTOR_MOVES_BOTH_"
                                          "COEFFICIENTS_AND_THE_REFERENCE_PARTICIPATION",
                provenance=TEST_AUTHORITY,
                # Honest labelling, not decoration: the halved reference
                # participation in ADVERSE_PARAMS *is* a liquidity/capacity
                # reduction, jointly with the widened spread/impact.
                categories=(ADVERSE_CATEGORY_CORRELATED_LIQUIDITY_DETERIORATION,
                           ADVERSE_CATEGORY_SPREAD_WIDENING_WITH_IMPACT_INCREASE,
                           ADVERSE_CATEGORY_CAPACITY_REDUCTION)),
        ),
        category_exclusions=(
            AuthorisedScenarioExclusion(
                ADVERSE_CATEGORY_BORROW_FINANCING_DETERIORATION, TEST_AUTHORITY,
                "fixture: unlevered long-only exposure, no borrow or financing modelled "
                "(see this recipe's F6_FINANCING_BORROW authorised zero)"),
            AuthorisedScenarioExclusion(
                ADVERSE_CATEGORY_EXECUTION_REGIME_MISMATCH, TEST_AUTHORITY,
                "fixture: one execution policy id declared throughout with no "
                "regime-switching authority exercised"),
        ))


def risk_partition() -> RiskPartition:
    return RiskPartition((
        RiskClaim("EXPLICIT_FEE_EXPECTED_COST", "K_FORWARD", "expected broker fees"),
        RiskClaim("OPEN_CROSSING_EXPECTED_COST", "K_FORWARD",
                  "expected half-spread at the authorized open"),
        RiskClaim("IMPACT_EXPECTED_COST", "K_FORWARD",
                  "expected impact at the reference participation"),
        RiskClaim("EXIT_EXPECTED_COST", "K_FORWARD", "expected exit execution loss"),
        RiskClaim("OPENING_LIQUIDITY_COEFFICIENT_MODEL_RISK", "M_ECONOMIC",
                  "uncertainty that the opening crossing and impact coefficients are "
                  "materially worse than their central estimates"),
    ))


def effect_domain() -> EffectDomain:
    return EffectDomain(lower=-0.05, upper=0.05, nodes=401)


def meue_recipe(**overrides) -> MEUERecipe:
    inventory = parameter_inventory().instantiate(CENTRAL_VALUES)
    fields = dict(
        recipe_id="MEUE_RECIPE_TEST",
        coordinate=coordinate_binding(),
        inventory=inventory,
        k_forward=k_forward_recipe(),
        domain=effect_domain(),
        scenarios=scenario_set(),
        partition=risk_partition(),
        theta_rule=theta_rule(),
    )
    fields.update(overrides)
    return MEUERecipe(**fields)
