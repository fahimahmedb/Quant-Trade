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
from .coordinate import (ALLOCATION_WEIGHTED_RATIO, DeltaCoordinateBinding,
                         DeltaCoordinateVerdict, ReturnConvention,
                         evaluate_delta_coordinate)
from .decision import (EconomicVerdict, EffectEstimate, PortfolioInteraction,
                       economic_gate)
from .fingerprint import RecipeNotOutcomeBlind, canonical_json, recipe_hash
from .frictions import (AuthorisedZero, CostComponent, CostInputUnavailable, KForwardRecipe,
                        verify_dependence_declarations)
from .margin import MarginComponent, MarginResult, m_economic
from .parameters import (COST_CLASSES, Dependence, EconomicParameter, InventoryFrozen,
                         ParameterInventory, SourceContract)
from .partition import RiskClaim, RiskPartition, partition_from
from .recipe import MEUERecipe, MEUEResult
from .scenarios import CostScenario, JointScenarioSet
from .theta import (EvaluationSession, ThetaFeedbackViolation, ThetaSelectionRule,
                    ThetaState)
from .value import (AffineShortcutUnavailable, BEEEResult, EffectDomain, PhiInstance, beee,
                    beee_affine, solve_beee)

__all__ = [
    "ALLOCATION_WEIGHTED_RATIO", "AffineShortcutUnavailable", "AuthorisedZero", "BEEEResult",
    "COST_CLASSES", "CapacityLimit", "CapacityOutcome", "CostComponent",
    "CostInputUnavailable", "CostScenario", "DeltaCoordinateBinding",
    "DeltaCoordinateVerdict", "Dependence", "EconomicParameter", "EconomicVerdict",
    "EffectDomain", "EffectEstimate", "EvaluationSession", "ExposureBudget",
    "InventoryFrozen", "JointScenarioSet", "KForwardRecipe", "MEUERecipe", "MEUEResult",
    "MarginComponent", "MarginResult", "NEW_POLICY_VERSION", "ParameterInventory",
    "PhiInstance", "PortfolioInteraction", "RecipeNotOutcomeBlind", "ReturnConvention",
    "RiskClaim", "RiskPartition", "SourceContract", "ThetaFeedbackViolation",
    "ThetaSelectionRule", "ThetaState", "apply_capacity", "beee", "beee_affine",
    "canonical_json", "economic_gate", "evaluate_delta_coordinate", "m_economic",
    "partition_from", "recipe_hash", "solve_beee", "verify_dependence_declarations",
]
