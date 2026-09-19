"""``M_economic`` — the conservative economic margin, derived not chosen.

The frozen structure (``D09_ROUTE_B_M_ECONOMIC_UNCERTAINTY_ENVELOPE_2026-09-17.md``)
says the margin comes from an ex-ante uncertainty envelope, never from a
percentage markup and never from looking at the resulting threshold.  The
cost/scenario contract section 9 names the candidate functional:

    M_economic(theta) = max_{s in S_cost_adverse} [ BEEE_s(theta) - BEEE_0(theta) ]_+

and is explicit that this is a **freeze candidate, not yet numerical authority**.
This module therefore computes it and labels every result with that status, so a
downstream caller cannot mistake an arithmetic result for an authorised margin.

Because the margin is a difference of two BEEE roots of the *same* frozen
``Phi``, it inherits whatever non-linearity ``Phi`` has
(``NONLINEAR_PHI_REQUIRES_COMPATIBLE_MARGIN_MAPPING``) instead of assuming the
affine ``adverse_cost / Q`` shortcut.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .frictions import KForwardRecipe
from .parameters import ParameterInventory
from .scenarios import JointScenarioSet
from .states import (M_ECONOMIC_ENVELOPE_UNRESOLVED, M_ECONOMIC_MAPPING_UNRESOLVED)
from .theta import ThetaState
from .value import BEEEResult, EffectDomain, PhiInstance, beee


#: Status of the margin functional itself. The cost/scenario contract section 9
#: offers the max-over-adverse-scenarios form as a candidate; until Blue freezes
#: it, a number produced by it is provisional by construction.
FUNCTIONAL_FREEZE_CANDIDATE = "FREEZE_CANDIDATE_NOT_AUTHORITY"
FUNCTIONAL_FROZEN = "FROZEN_MARGIN_FUNCTIONAL"

MARGIN_RESOLVED = "M_ECONOMIC_RESOLVED"


@dataclass(frozen=True)
class MarginComponent:
    """A separately admitted economic-risk class outside the cost scenarios.

    Admissible only with a proof that it does not overlap what the scenario set
    already charges (``FRICTION_AND_MARGIN_DO_NOT_DOUBLE_COUNT_SAME_RISK``).
    """

    risk_class: str
    value_in_delta_units: float
    non_overlap_proof: str = ""
    provenance: str = ""

    def violations(self) -> list[str]:
        problems: list[str] = []
        if self.value_in_delta_units < 0:
            problems.append(f"{self.risk_class}: MARGIN_COMPONENT_MUST_NOT_BE_NEGATIVE")
        if not self.non_overlap_proof:
            problems.append(f"{self.risk_class}: ADDITIONAL_MARGIN_REQUIRES_NON_OVERLAP_PROOF")
        if not self.provenance:
            problems.append(f"{self.risk_class}: MARGIN_COMPONENT_PROVENANCE_UNDECLARED")
        return problems

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MarginResult:
    state: str
    value: float | None
    beee_central: BEEEResult | None
    #: scenario_id -> BEEE under that scenario.
    beee_by_scenario: dict[str, BEEEResult] = field(default_factory=dict)
    #: scenario_id -> increment over BEEE_0, floored at zero.
    increments: dict[str, float] = field(default_factory=dict)
    binding_scenario: str | None = None
    functional_status: str = FUNCTIONAL_FREEZE_CANDIDATE
    violations: tuple[str, ...] = ()

    @property
    def resolved(self) -> bool:
        return self.state == MARGIN_RESOLVED and self.value is not None

    def to_dict(self) -> dict[str, Any]:
        return {"state": self.state, "value": self.value,
                "beee_central": self.beee_central.to_dict() if self.beee_central else None,
                "beee_by_scenario": {key: value.to_dict()
                                     for key, value in self.beee_by_scenario.items()},
                "increments": dict(self.increments),
                "binding_scenario": self.binding_scenario,
                "functional_status": self.functional_status,
                "violations": list(self.violations)}


def m_economic(theta: ThetaState, k_forward: KForwardRecipe, domain: EffectDomain,
               scenario_set: JointScenarioSet, inventory: ParameterInventory,
               additional: tuple[MarginComponent, ...] = (),
               functional_status: str = FUNCTIONAL_FREEZE_CANDIDATE) -> MarginResult:
    """Map the frozen joint uncertainty set into ``delta`` units.

    Returns a failure state rather than a number whenever the envelope or its
    mapping is not available. ``These states block consumable final MEUE
    authority. They do not authorize an arbitrary fallback margin.``
    """
    problems = list(scenario_set.violations())
    problems.extend(scenario_set.coverage_violations(inventory))
    problems.extend(scenario_set.direction_violations(inventory))
    for component in additional:
        problems.extend(component.violations())

    central = scenario_set.central
    if central is None or not scenario_set.adverse:
        return MarginResult(M_ECONOMIC_ENVELOPE_UNRESOLVED, None, None,
                            functional_status=functional_status,
                            violations=tuple(problems))
    if any(problem.startswith(M_ECONOMIC_ENVELOPE_UNRESOLVED) for problem in problems):
        return MarginResult(M_ECONOMIC_ENVELOPE_UNRESOLVED, None, None,
                            functional_status=functional_status,
                            violations=tuple(problems))

    central_beee = beee(PhiInstance(theta, k_forward, dict(central.parameter_values), domain))
    if not central_beee.resolved:
        return MarginResult(M_ECONOMIC_MAPPING_UNRESOLVED, None, central_beee,
                            functional_status=functional_status,
                            violations=tuple(problems + [
                                f"CENTRAL_SCENARIO_BEEE:{central_beee.state}"]))

    by_scenario: dict[str, BEEEResult] = {}
    increments: dict[str, float] = {}
    for scenario in scenario_set.adverse:
        result = beee(PhiInstance(theta, k_forward, dict(scenario.parameter_values), domain))
        by_scenario[scenario.scenario_id] = result
        if not result.resolved:
            problems.append(f"{scenario.scenario_id}:{result.state}")
            continue
        increments[scenario.scenario_id] = max(result.value - central_beee.value, 0.0)
        if result.value < central_beee.value:
            problems.append(
                f"{scenario.scenario_id}: ADVERSE_SCENARIO_LOWERS_BREAK_EVEN_EFFECT")

    if len(increments) != len(scenario_set.adverse):
        return MarginResult(M_ECONOMIC_MAPPING_UNRESOLVED, None, central_beee, by_scenario,
                            increments, functional_status=functional_status,
                            violations=tuple(problems))

    binding_scenario = max(increments, key=lambda key: increments[key])
    total = increments[binding_scenario] + sum(
        component.value_in_delta_units for component in additional)
    state = MARGIN_RESOLVED
    if any(problem for problem in problems
           if problem.startswith(M_ECONOMIC_ENVELOPE_UNRESOLVED)):
        state = M_ECONOMIC_ENVELOPE_UNRESOLVED
    return MarginResult(state, total if state == MARGIN_RESOLVED else None, central_beee,
                        by_scenario, increments, binding_scenario, functional_status,
                        tuple(problems))
