"""Quant's economic engine.

Turns a scientific effect into an economic decision under the frozen Route-B
D09 contracts, mechanically and outcome-blind:

    delta coordinate gate -> parameter inventory -> K_forward expected cost
    -> Phi -> BEEE root -> joint adverse scenarios -> M_economic -> MEUE
    -> capacity and portfolio interaction -> CONTINUE / NO_TRADE / KILL

Nothing in this package reads the P0 Form-4 reservoir, asserts a numerical
Form-4 cost coefficient, or authorises real capital.
"""

from .capacity import (CapacityLimit, CapacityOutcome, ExposureBudget, NEW_POLICY_VERSION,
                       apply_capacity)
from .consistency import (ExecutionCostModel, ResearchExecutionConsistency,
                          implied_participation_ceiling, verify_research_cost_consistency)
from .coordinate import (ALLOCATION_WEIGHTED_RATIO, DeltaCoordinateBinding,
                         DeltaCoordinateVerdict, ReturnConvention,
                         evaluate_delta_coordinate)
from .decision import (EconomicVerdict, EffectEstimate, PortfolioInteraction,
                       economic_gate)
from .fingerprint import RecipeNotOutcomeBlind, canonical_json, recipe_hash
from .frictions import (COST_SHAPES, AuthorisedZero, CostComponent, CostInputUnavailable,
                        KForwardRecipe, verify_dependence_declarations,
                        verify_shape_declarations)
from .journal import (AssessmentConflict, AssessmentRecord, EconomicAssessmentJournal,
                      compute_input_fingerprint)
from .margin import MarginComponent, MarginResult, m_economic
from .opening import OpeningExecutionModel
from .parameters import (COST_CLASSES, Dependence, EconomicParameter, InventoryFrozen,
                         ParameterInventory, ProvenanceBinding, SourceContract)
from .partition import RiskClaim, RiskPartition, partition_from
from .recipe import MEUERecipe, MEUEResult
from .scenarios import (ADVERSE_CATEGORY_BORROW_FINANCING_DETERIORATION,
                        ADVERSE_CATEGORY_CAPACITY_REDUCTION,
                        ADVERSE_CATEGORY_CORRELATED_LIQUIDITY_DETERIORATION,
                        ADVERSE_CATEGORY_EXECUTION_REGIME_MISMATCH,
                        ADVERSE_CATEGORY_SPREAD_WIDENING_WITH_IMPACT_INCREASE,
                        ADVERSE_SCENARIO_CATEGORIES, AuthorisedScenarioExclusion, CostScenario,
                        JointScenarioSet)
from .sizing import (MarginSizingRule, RiskApproval, SizingPlan, SleeveTarget, combine_lanes,
                     size_lane, verify_risk_approval)
from .states import (CLUSTERING_UNIT_O4_RESOLVED, CLUSTERING_UNIT_O4_UNRESOLVED,
                     CLUSTERING_UNIT_STATES, CLUSTERING_UNIT_UNDECLARED,
                     ORDER_ELIGIBILITY_DEVELOPMENT_SIGNAL_ONLY,
                     ORDER_ELIGIBILITY_NOT_ELIGIBLE,
                     ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE,
                     ORDER_ELIGIBILITY_STATES)
from .theta import (EvaluationSession, ThetaFeedbackViolation, ThetaSelectionRule,
                    ThetaState)
from .timeline import (CausalEventLedger, EventTimeline, FrictionCharge, InformationInput,
                       NetOutcome, aggregate_allocation_weighted)
from .value import (AffineShortcutUnavailable, BEEEResult, EffectDomain, PhiInstance, beee,
                    beee_affine, solve_beee)

__all__ = ["ADVERSE_CATEGORY_BORROW_FINANCING_DETERIORATION",
    "ADVERSE_CATEGORY_CAPACITY_REDUCTION", "ADVERSE_CATEGORY_CORRELATED_LIQUIDITY_DETERIORATION",
    "ADVERSE_CATEGORY_EXECUTION_REGIME_MISMATCH",
    "ADVERSE_CATEGORY_SPREAD_WIDENING_WITH_IMPACT_INCREASE",
    "ADVERSE_SCENARIO_CATEGORIES", "ALLOCATION_WEIGHTED_RATIO",
    "AffineShortcutUnavailable", "AssessmentConflict", "AssessmentRecord",
    "AuthorisedScenarioExclusion", "AuthorisedZero",
    "BEEEResult", "COST_CLASSES", "COST_SHAPES",
    "CLUSTERING_UNIT_O4_RESOLVED", "CLUSTERING_UNIT_O4_UNRESOLVED",
    "CLUSTERING_UNIT_STATES", "CLUSTERING_UNIT_UNDECLARED",
    "CapacityLimit", "CapacityOutcome", "CausalEventLedger",
    "EconomicAssessmentJournal",
    "CostComponent", "CostInputUnavailable", "CostScenario", "DeltaCoordinateBinding",
    "DeltaCoordinateVerdict", "Dependence", "EconomicParameter", "EconomicVerdict",
    "EffectDomain", "EffectEstimate", "EvaluationSession", "EventTimeline",
    "ExecutionCostModel", "ExposureBudget", "FrictionCharge", "InformationInput",
    "InventoryFrozen", "JointScenarioSet", "KForwardRecipe", "MEUERecipe", "MEUEResult",
    "MarginComponent", "MarginResult", "MarginSizingRule", "NEW_POLICY_VERSION", "NetOutcome",
    "OpeningExecutionModel", "ORDER_ELIGIBILITY_DEVELOPMENT_SIGNAL_ONLY",
    "ORDER_ELIGIBILITY_NOT_ELIGIBLE", "ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE",
    "ORDER_ELIGIBILITY_STATES",
    "ParameterInventory", "PhiInstance", "PortfolioInteraction", "ProvenanceBinding",
    "RecipeNotOutcomeBlind", "ResearchExecutionConsistency", "ReturnConvention",
    "RiskApproval", "RiskClaim", "RiskPartition", "SizingPlan", "SleeveTarget",
    "SourceContract", "ThetaFeedbackViolation", "ThetaSelectionRule", "ThetaState",
    "aggregate_allocation_weighted", "apply_capacity", "beee", "beee_affine", "canonical_json",
    "combine_lanes", "compute_input_fingerprint", "economic_gate", "evaluate_delta_coordinate",
    "implied_participation_ceiling", "m_economic", "partition_from", "recipe_hash",
    "size_lane", "solve_beee", "verify_dependence_declarations", "verify_shape_declarations",
    "verify_research_cost_consistency", "verify_risk_approval"
]
