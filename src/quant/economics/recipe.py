"""The assembled MEUE recipe: ``MEUE(theta) = BEEE(theta) + M_economic(theta)``.

This is the object the remainder contract section 8 asks to be hash-addressable
before ceiling visibility: the delta-coordinate binding, the parameter inventory
with its per-parameter source contracts, the ``K_forward`` expected-cost recipe,
the ``Phi`` effect domain and root rule, the joint scenario set, the margin
functional and the anti-double-counting map — all in one addressable document.

The recipe reports its own consumability rather than letting a caller decide.
``RECIPE_CONSUMABLE`` is deliberately hard to reach: it needs a compatible
coordinate, a complete cost-class cover, calibration authority on every consumed
parameter, a frozen (not candidate) margin functional and a resolved ``theta``.
Anything less produces ``RECIPE_PROVISIONAL``, which yields numbers explicitly
marked non-authoritative, or ``RECIPE_INVALID``, which yields no numbers at all.

A state enum is not a capability: this module never reports consumable authority
it cannot evidence.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .coordinate import DeltaCoordinateBinding, evaluate_delta_coordinate
from .fingerprint import recipe_hash
from .frictions import KForwardRecipe, verify_dependence_declarations
from .margin import (FUNCTIONAL_FREEZE_CANDIDATE, FUNCTIONAL_FROZEN, MarginComponent,
                     MarginResult, m_economic)
from .parameters import ParameterInventory
from .partition import RiskPartition
from .scenarios import JointScenarioSet
from .states import (DELTA_COORDINATE_COMPATIBLE, RECIPE_CONSUMABLE, RECIPE_INVALID,
                     RECIPE_PROVISIONAL)
from .theta import EvaluationSession, ThetaSelectionRule, ThetaState
from .value import BEEEResult, EffectDomain, PhiInstance, beee


@dataclass(frozen=True)
class MEUEResult:
    """One evaluation of the recipe at one ``theta``."""

    recipe_state: str
    theta_id: str
    beee: BEEEResult | None
    margin: MarginResult | None
    meue: float | None
    recipe_hash: str | None
    theta_hash: str | None
    violations: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    @property
    def consumable(self) -> bool:
        return self.recipe_state == RECIPE_CONSUMABLE and self.meue is not None

    def to_dict(self) -> dict[str, Any]:
        return {"recipe_state": self.recipe_state, "theta_id": self.theta_id,
                "beee": self.beee.to_dict() if self.beee else None,
                "margin": self.margin.to_dict() if self.margin else None,
                "meue": self.meue, "recipe_hash": self.recipe_hash,
                "theta_hash": self.theta_hash,
                "violations": list(self.violations), "notes": list(self.notes)}


@dataclass
class MEUERecipe:
    """The frozen economic recipe, assembled from its governed parts."""

    recipe_id: str
    coordinate: DeltaCoordinateBinding
    inventory: ParameterInventory
    k_forward: KForwardRecipe
    domain: EffectDomain
    scenarios: JointScenarioSet
    partition: RiskPartition
    theta_rule: ThetaSelectionRule
    margin_functional_status: str = FUNCTIONAL_FREEZE_CANDIDATE
    additional_margin: tuple[MarginComponent, ...] = ()

    # -- structural checks ----------------------------------------------------

    def structural_violations(self) -> list[str]:
        problems: list[str] = []
        verdict = evaluate_delta_coordinate(self.coordinate)
        if verdict.state != DELTA_COORDINATE_COMPATIBLE:
            problems.extend(f"{verdict.state}:{reason}" for reason in verdict.reasons)
        problems.extend(self.domain.violations())
        problems.extend(self.inventory.violations())
        problems.extend(self.k_forward.violations())
        problems.extend(self.k_forward.parameter_violations(self.inventory))
        problems.extend(self.scenarios.violations())
        problems.extend(self.scenarios.coverage_violations(self.inventory))
        problems.extend(self.scenarios.direction_violations(self.inventory))
        problems.extend(self.partition.violations())
        problems.extend(self.theta_rule.violations())
        for component in self.additional_margin:
            problems.extend(component.violations())
        if self.coordinate.allocation_constructor_id is not None:
            declared = self.coordinate.allocation_constructor_id
            if declared != self.theta_rule.rule_id and declared not in \
                    self.theta_rule.upstream_authorities:
                problems.append(
                    "ALLOCATION_CONSTRUCTOR_NOT_AN_UPSTREAM_AUTHORITY_OF_THETA_RULE")
        return problems

    def blocking_violations(self, theta: ThetaState) -> list[str]:
        """Structural problems plus anything wrong with this ``theta``."""
        problems = self.structural_violations()
        problems.extend(theta.violations())
        if not self.theta_rule.admits(theta):
            problems.append("THETA_NOT_ADMITTED_BY_FROZEN_SELECTION_RULE")
        return problems

    # -- addressability -------------------------------------------------------

    def rule_document(self) -> dict[str, Any]:
        return {
            "recipe_id": self.recipe_id,
            "coordinate": self.coordinate.to_dict(),
            "parameter_inventory": self.inventory.rule_document(),
            "k_forward": self.k_forward.rule_document(),
            "effect_domain": self.domain.to_dict(),
            "scenarios": self.scenarios.rule_document(),
            "risk_partition": self.partition.rule_document(),
            "theta_rule": self.theta_rule.to_dict(),
            "margin_functional_status": self.margin_functional_status,
            "additional_margin": [component.to_dict()
                                  for component in self.additional_margin],
        }

    def fingerprint(self) -> str:
        return recipe_hash(self.rule_document())

    # -- evaluation -----------------------------------------------------------

    def _consumability(self, theta: ThetaState) -> tuple[str, list[str]]:
        notes: list[str] = []
        consumed = {parameter_id for component in self.k_forward.components
                    for parameter_id in component.consumes}
        uncalibrated = sorted(
            parameter_id for parameter_id in consumed
            if parameter_id in self.inventory
            and not self.inventory[parameter_id].carries_calibration_authority)
        if uncalibrated:
            notes.append("EXISTING_EXECUTION_PARAMETER_IS_NOT_AUTOMATIC_CALIBRATION_AUTHORITY:"
                         + ",".join(uncalibrated))
        if self.margin_functional_status != FUNCTIONAL_FROZEN:
            notes.append("MARGIN_FUNCTIONAL_IS_A_FREEZE_CANDIDATE_NOT_AUTHORITY")
        unresolved = self.inventory.unresolved()
        if unresolved:
            notes.append("K_FORWARD_PARAMETER_UNRESOLVED:" + ",".join(unresolved))
        state = RECIPE_CONSUMABLE if not notes else RECIPE_PROVISIONAL
        return state, notes

    def evaluate(self, theta: ThetaState,
                 session: EvaluationSession | None = None) -> MEUEResult:
        """Derive ``BEEE``, ``M_economic`` and ``MEUE`` mechanically at ``theta``.

        The order is the frozen one: ``theta`` first, then cost, then margin,
        then threshold. Nothing downstream may alter ``theta``, which the
        optional :class:`EvaluationSession` enforces.
        """
        if session is not None:
            theta = session.admit(theta)
        problems = self.blocking_violations(theta)
        if problems:
            return MEUEResult(RECIPE_INVALID, theta.theta_id, None, None, None, None,
                              theta.fingerprint(), tuple(sorted(set(problems))))

        central = self.scenarios.central
        assert central is not None  # guaranteed by structural checks
        params = dict(central.parameter_values)
        instance = PhiInstance(theta, self.k_forward, params, self.domain)

        declaration_problems = verify_dependence_declarations(self.k_forward, theta, params)
        if declaration_problems:
            return MEUEResult(RECIPE_INVALID, theta.theta_id, None, None, None, None,
                              theta.fingerprint(), tuple(sorted(set(declaration_problems))))

        central_beee = beee(instance)
        margin = m_economic(theta, self.k_forward, self.domain, self.scenarios,
                            self.inventory, self.additional_margin,
                            self.margin_functional_status)
        state, notes = self._consumability(theta)
        if not central_beee.resolved or not margin.resolved:
            reasons = []
            if not central_beee.resolved:
                reasons.append(central_beee.state)
            if not margin.resolved:
                reasons.append(margin.state)
                reasons.extend(margin.violations)
            return MEUEResult(RECIPE_INVALID, theta.theta_id, central_beee, margin, None,
                              self.fingerprint(), theta.fingerprint(),
                              tuple(sorted(set(reasons))), tuple(notes))

        meue = central_beee.value + margin.value
        if session is not None:
            session.record_threshold()
        return MEUEResult(state, theta.theta_id, central_beee, margin, meue,
                          self.fingerprint(), theta.fingerprint(), (), tuple(notes))
