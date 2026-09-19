"""Joint cost-model scenarios ``S_cost``.

``D09_ROUTE_B_COST_PARAMETER_SOURCE_AND_JOINT_SCENARIO_CONTRACT_2026-09-17.md``
section 7 is explicit that total model risk is **not**
``sum_k marginal_parameter_margin_k``.  Spread, impact, opening slippage,
liquidity and participation uncertainty share data and misspecification channels,
so the current-lineage object is a frozen set of mutually coherent joint
scenarios, with ``s_0`` the central model that instantiates ``K_forward``.

This module therefore offers no way to add marginal margins together. The only
aggregation it exposes runs over scenarios, and a scenario has to say how it
represents cross-parameter dependence before it counts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from .fingerprint import recipe_hash
from .parameters import ParameterInventory
from .states import JOINT_COST_SCENARIO_UNRESOLVED, M_ECONOMIC_ENVELOPE_UNRESOLVED


SCENARIO_CENTRAL = "CENTRAL"
SCENARIO_ADVERSE = "ADVERSE"
SCENARIO_KINDS = (SCENARIO_CENTRAL, SCENARIO_ADVERSE)

#: How the adverse set was built.
CONSTRUCTION_COHERENT_JOINT = "COHERENT_JOINT_SCENARIOS"
CONSTRUCTION_UNRESTRICTED_CARTESIAN = "UNRESTRICTED_CARTESIAN_ENDPOINTS"
CONSTRUCTIONS = (CONSTRUCTION_COHERENT_JOINT, CONSTRUCTION_UNRESTRICTED_CARTESIAN)


@dataclass(frozen=True)
class CostScenario:
    """One coherent vector of parameter/model states."""

    scenario_id: str
    kind: str
    #: parameter_id -> value under this scenario.
    parameter_values: Mapping[str, float]
    #: Why this combination is jointly defensible.
    coherence_justification: str = ""
    #: How cross-parameter dependence is represented in this scenario.
    dependence_representation: str = ""
    #: Where the scenario's values come from, per the envelope admission rule.
    provenance: str = ""

    def violations(self) -> list[str]:
        problems: list[str] = []
        if self.kind not in SCENARIO_KINDS:
            problems.append(f"{self.scenario_id}: SCENARIO_KIND_NOT_RECOGNISED")
        if not self.parameter_values:
            problems.append(f"{self.scenario_id}: SCENARIO_HAS_NO_PARAMETER_VALUES")
        if self.kind == SCENARIO_ADVERSE:
            if not self.coherence_justification:
                problems.append(f"{self.scenario_id}: ADVERSE_SCENARIO_WITHOUT_COHERENCE_"
                                "JUSTIFICATION")
            if not self.dependence_representation:
                problems.append(f"{self.scenario_id}: UNKNOWN_PARAMETER_DEPENDENCE_IS_NOT_"
                                "ZERO_DEPENDENCE")
        if not self.provenance:
            problems.append(f"{self.scenario_id}: SCENARIO_PROVENANCE_UNDECLARED")
        return problems

    def to_dict(self) -> dict[str, Any]:
        return {"scenario_id": self.scenario_id, "kind": self.kind,
                "parameter_values": dict(sorted(self.parameter_values.items())),
                "coherence_justification": self.coherence_justification,
                "dependence_representation": self.dependence_representation,
                "provenance": self.provenance}


@dataclass(frozen=True)
class JointScenarioSet:
    """``S_cost = {s_0, s_1, ..., s_m}`` with exactly one central scenario."""

    set_id: str
    scenarios: tuple[CostScenario, ...]
    construction: str = CONSTRUCTION_COHERENT_JOINT
    #: Required when the construction is an unrestricted Cartesian product.
    cartesian_justification: str | None = None
    #: How the scenario set may be updated without becoming result-driven.
    update_rule: str = ""

    # -- structure ------------------------------------------------------------

    @property
    def central(self) -> CostScenario | None:
        for scenario in self.scenarios:
            if scenario.kind == SCENARIO_CENTRAL:
                return scenario
        return None

    @property
    def adverse(self) -> tuple[CostScenario, ...]:
        return tuple(scenario for scenario in self.scenarios
                     if scenario.kind == SCENARIO_ADVERSE)

    def violations(self) -> list[str]:
        problems: list[str] = []
        identifiers = [scenario.scenario_id for scenario in self.scenarios]
        if len(set(identifiers)) != len(identifiers):
            problems.append("DUPLICATE_SCENARIO_ID")
        centrals = [s for s in self.scenarios if s.kind == SCENARIO_CENTRAL]
        if len(centrals) != 1:
            problems.append(f"{JOINT_COST_SCENARIO_UNRESOLVED}:"
                            "EXACTLY_ONE_CENTRAL_SCENARIO_REQUIRED")
        if not self.adverse:
            problems.append(f"{M_ECONOMIC_ENVELOPE_UNRESOLVED}:NO_ADVERSE_SCENARIO")
        if self.construction not in CONSTRUCTIONS:
            problems.append("SCENARIO_CONSTRUCTION_NOT_RECOGNISED")
        if (self.construction == CONSTRUCTION_UNRESTRICTED_CARTESIAN
                and not self.cartesian_justification):
            problems.append("NO_UNJUSTIFIED_CARTESIAN_WORST_CASE")
        if not self.update_rule:
            problems.append("SCENARIO_UPDATE_RULE_UNDECLARED")
        for scenario in self.scenarios:
            problems.extend(scenario.violations())
        return problems

    def coverage_violations(self, inventory: ParameterInventory) -> list[str]:
        """Every parameter lacking calibration authority must be perturbed.

        A V1-assumed or engineering-bound coefficient that no adverse scenario
        moves is an uncharged model risk, which is exactly the hole
        ``EXISTING_EXECUTION_PARAMETER_IS_NOT_AUTOMATIC_CALIBRATION_AUTHORITY``
        is meant to close.
        """
        problems: list[str] = []
        central = self.central
        if central is None:
            return [f"{JOINT_COST_SCENARIO_UNRESOLVED}:NO_CENTRAL_SCENARIO"]
        for parameter_id in inventory.requiring_model_risk():
            central_value = central.parameter_values.get(parameter_id)
            perturbed = any(
                parameter_id in scenario.parameter_values
                and scenario.parameter_values[parameter_id] != central_value
                for scenario in self.adverse)
            if not perturbed:
                problems.append(
                    f"{M_ECONOMIC_ENVELOPE_UNRESOLVED}:UNCHARGED_MODEL_RISK:{parameter_id}")
        for scenario in self.scenarios:
            unknown = sorted(set(scenario.parameter_values) - {p.parameter_id
                                                              for p in inventory})
            for parameter_id in unknown:
                problems.append(
                    f"{scenario.scenario_id}: PARAMETER_NOT_IN_FROZEN_INVENTORY:{parameter_id}")
        return problems

    def direction_violations(self, inventory: ParameterInventory) -> list[str]:
        """An adverse scenario may not move a parameter to its favourable side."""
        problems: list[str] = []
        central = self.central
        if central is None:
            return problems
        for scenario in self.adverse:
            for parameter_id, value in scenario.parameter_values.items():
                if parameter_id not in inventory:
                    continue
                central_value = central.parameter_values.get(parameter_id)
                if central_value is None or value == central_value:
                    continue
                direction = inventory[parameter_id].adverse_direction
                worse = value > central_value if direction == "HIGHER_IS_ADVERSE" \
                    else value < central_value
                if not worse:
                    problems.append(
                        f"{scenario.scenario_id}: M_ECONOMIC_USES_ECONOMICALLY_ADVERSE_SIDE:"
                        f"{parameter_id}")
        return problems

    # -- addressability -------------------------------------------------------

    def rule_document(self) -> dict[str, Any]:
        return {"set_id": self.set_id, "construction": self.construction,
                "cartesian_justification": self.cartesian_justification,
                "update_rule": self.update_rule,
                "scenarios": sorted((scenario.to_dict() for scenario in self.scenarios),
                                    key=lambda row: row["scenario_id"])}

    def fingerprint(self) -> str:
        return recipe_hash(self.rule_document())
