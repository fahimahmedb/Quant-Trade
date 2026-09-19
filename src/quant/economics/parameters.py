"""The frozen economic-parameter inventory.

``D09_ROUTE_B_M_ECONOMIC_UNCERTAINTY_ENVELOPE_2026-09-17.md`` section 7 requires
every economic parameter to exist in a registry *before* any candidate numerical
value is inspected, and
``D09_ROUTE_B_COST_PARAMETER_SOURCE_AND_JOINT_SCENARIO_CONTRACT_2026-09-17.md``
section 2 requires each one to carry its own source contract rather than inherit
a global label such as ``USE_MICROSTRUCTURE_LITERATURE``.

This module makes both executable:

* a parameter that is not in the inventory cannot be added after the inventory
  is frozen, so a missing cost cannot be inserted because a threshold turned out
  inconvenient;
* a parameter whose central value has no calibration authority (for example a
  coefficient that merely exists in the V1 execution model) is *required* to
  carry a model-risk role, which is how
  ``EXISTING_EXECUTION_PARAMETER_IS_NOT_AUTOMATIC_CALIBRATION_AUTHORITY`` stops
  being a sentence in a document and starts failing a check.

No numerical Form 4 cost value is asserted anywhere in this package. Central
estimates are inputs supplied by whoever holds the authority to supply them.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from typing import Any, Iterable, Iterator, Mapping

from .fingerprint import recipe_hash
from .states import (HOME_K_FORWARD, HOME_M_ECONOMIC, K_FORWARD_PARAMETER_UNRESOLVED,
                     PARAMETER_UNRESOLVED, PROVENANCE_CLASSES,
                     PROVENANCE_REQUIRING_MODEL_RISK, PROVENANCE_UNAVAILABLE,
                     SOURCE_SET_NONCOMMENSURABLE)


#: Cost classes named by the source/joint-scenario contract section 4. The
#: inventory is closed over these: a new class is a governed version event.
COST_CLASSES = (
    "F1_EXPLICIT_FEES",
    "F2_OPEN_ENTRY_CROSSING",
    "F3_OPEN_ENTRY_SLIPPAGE",
    "F4_MARKET_IMPACT",
    "F5_EXIT_EXECUTION",
    "F6_FINANCING_BORROW",
    "F7_RESIDUAL_CAPITAL_DRAG",
)

#: Multiple-source procedures the contract section 3 permits. Each is a
#: predeclared deterministic procedure.
PERMITTED_MULTIPLE_SOURCE_RULES = (
    "ORDERED_APPLICABILITY_TIERS",
    "PARAMETER_SPECIFIC_META_ESTIMATOR",
    "JOINTLY_CALIBRATED_DATASET",
    "NONCOMMENSURABLE_FAILS_TO_PARAMETER_UNRESOLVED",
)

#: Procedures the contract forbids by name. ``MINIMUM_ACROSS_SOURCES`` is the
#: retired Route-A rule; the rest are result-driven selection.
FORBIDDEN_MULTIPLE_SOURCE_RULES = {
    "MINIMUM_ACROSS_SOURCES": "ROUTE_A_SOURCE_MINIMUM_DOES_NOT_TRANSFER_TO_EXPECTED_COST",
    "MAXIMUM_ACROSS_SOURCES": "NO_HIDDEN_CONSERVATISM_INSIDE_K_FORWARD",
    "MOST_FAVOURABLE_MEUE": "NO_RESULT_DRIVEN_SOURCE_SELECTION",
    "MOST_CONVENIENT_STUDY": "NO_RESULT_DRIVEN_SOURCE_SELECTION",
    "ANALYST_CHOICE_AT_INSTANTIATION": "NO_RESULT_DRIVEN_SOURCE_SELECTION",
}

#: Evidence classes the envelope contract section 3 admits once specified.
ADMISSIBLE_EVIDENCE_CLASSES = (
    "EXTERNAL_MICROSTRUCTURE_LITERATURE",
    "BROAD_MARKET_EXECUTION_DATA_NOT_SELECTED_ON_TARGET_OUTCOMES",
    "INDEPENDENTLY_CALIBRATED_NON_TARGET_EXECUTION_RECORDS",
    "ENGINEERING_PLAUSIBILITY_BOUND_WITH_GOVERNANCE_STATUS",
)

#: Evidence classes that would break ``ENVELOPE_EVIDENCE_IS_TARGET_OUTCOME_BLIND``.
FORBIDDEN_EVIDENCE_CLASSES = {
    "FORM4_TARGET_OUTCOMES": "ENVELOPE_EVIDENCE_IS_TARGET_OUTCOME_BLIND",
    "D05_CEILING_VALUES": "ENVELOPE_EVIDENCE_IS_TARGET_OUTCOME_BLIND",
    "RESULTING_MEUE_MAGNITUDE": "MEUE_RESULT_CANNOT_TUNE_ITS_OWN_MARGIN",
    "THRESHOLD_REASONABLENESS": "THRESHOLD_REASONABLENESS_IS_NOT_CALIBRATION_EVIDENCE",
}

#: Execution regimes. The envelope contract section 6 forbids silently reusing a
#: generic intraday calibration for the authorized first-open entry.
EXECUTION_REGIMES = (
    "OPENING_AUCTION",
    "FIRST_REGULAR_SESSION_OPEN",
    "CONTINUOUS_INTRADAY",
    "AUTHORIZED_EXIT_REGIME",
    "FINANCING_OVERNIGHT",
    "NOT_EXECUTION_DEPENDENT",
)

#: Regimes for which generic intraday evidence is not automatically admissible.
OPENING_REGIMES = ("OPENING_AUCTION", "FIRST_REGULAR_SESSION_OPEN")

#: The economically adverse side of a parameter's plausible set.
ADVERSE_DIRECTIONS = ("HIGHER_IS_ADVERSE", "LOWER_IS_ADVERSE")


@dataclass(frozen=True)
class Dependence:
    """Whether an expected value may vary with each part of ``theta``.

    Declared, then *checked* against the functional (see
    :func:`quant.economics.frictions.verify_dependence_declarations`). A
    declaration nobody verifies is a comment.
    """

    delta: bool = False
    capital: bool = False
    geometry: bool = False
    liquidity: bool = False
    allocation_state: bool = False
    participation: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SourceContract:
    """Per-parameter source governance (cost/source contract section 2)."""

    economic_estimand: str
    population_applicability: str
    admissible_source_classes: tuple[str, ...]
    applicability_exclusion_rule: str
    multiple_source_rule: str
    evidence_update_rule: str
    failure_state: str = PARAMETER_UNRESOLVED
    source_priority_tiers: tuple[str, ...] = ()

    def violations(self, parameter_id: str) -> list[str]:
        problems: list[str] = []
        if self.multiple_source_rule in FORBIDDEN_MULTIPLE_SOURCE_RULES:
            problems.append(
                f"{parameter_id}: {FORBIDDEN_MULTIPLE_SOURCE_RULES[self.multiple_source_rule]}")
        elif self.multiple_source_rule not in PERMITTED_MULTIPLE_SOURCE_RULES:
            problems.append(f"{parameter_id}: MULTIPLE_SOURCE_RULE_NOT_PREDECLARED")
        if (self.multiple_source_rule == "ORDERED_APPLICABILITY_TIERS"
                and not self.source_priority_tiers):
            problems.append(f"{parameter_id}: ORDERED_TIER_RULE_WITHOUT_TIERS")
        if not self.admissible_source_classes:
            problems.append(f"{parameter_id}: NO_ADMISSIBLE_SOURCE_CLASS_DECLARED")
        for source_class in self.admissible_source_classes:
            if source_class in FORBIDDEN_EVIDENCE_CLASSES:
                problems.append(
                    f"{parameter_id}: {FORBIDDEN_EVIDENCE_CLASSES[source_class]}")
            elif source_class not in ADMISSIBLE_EVIDENCE_CLASSES:
                problems.append(f"{parameter_id}: SOURCE_CLASS_NOT_ADMITTED:{source_class}")
        if self.failure_state not in (PARAMETER_UNRESOLVED, K_FORWARD_PARAMETER_UNRESOLVED,
                                      SOURCE_SET_NONCOMMENSURABLE):
            problems.append(f"{parameter_id}: FAILURE_STATE_NOT_RECOGNISED")
        if not self.applicability_exclusion_rule:
            problems.append(f"{parameter_id}: NO_APPLICABILITY_EXCLUSION_RULE")
        if not self.evidence_update_rule:
            problems.append(f"{parameter_id}: NO_EVIDENCE_UPDATE_RULE")
        return problems

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EconomicParameter:
    """One row of the frozen inventory (envelope contract section 7)."""

    parameter_id: str
    cost_component: str
    unit: str
    execution_regime: str
    source_contract: SourceContract
    #: ``K_FORWARD`` when the central value enters expected cost, else ``NONE``.
    expected_value_role: str = HOME_K_FORWARD
    #: ``M_ECONOMIC`` when this parameter's uncertainty feeds the margin.
    uncertainty_role: str = HOME_M_ECONOMIC
    dependence: Dependence = field(default_factory=Dependence)
    #: The central/expected value ``p_k^E``. ``None`` means unresolved, never zero.
    central_estimate: float | None = None
    central_provenance: str = PROVENANCE_UNAVAILABLE
    #: How the plausible set ``U_k`` is constructed. Required when the parameter
    #: has a margin role.
    envelope_provenance_rule: str | None = None
    #: Which side of ``U_k`` is economically adverse. Model error is not assumed
    #: symmetric (``M_ECONOMIC_MUST_RESPECT_ASYMMETRIC_MODEL_RISK``), so the
    #: adverse side has to be named rather than inferred at evaluation time.
    adverse_direction: str = "HIGHER_IS_ADVERSE"

    def violations(self) -> list[str]:
        problems = list(self.source_contract.violations(self.parameter_id))
        if self.cost_component not in COST_CLASSES:
            problems.append(f"{self.parameter_id}: COST_CLASS_NOT_IN_FROZEN_INVENTORY")
        if self.execution_regime not in EXECUTION_REGIMES:
            problems.append(f"{self.parameter_id}: EXECUTION_REGIME_NOT_DECLARED")
        if self.central_provenance not in PROVENANCE_CLASSES:
            problems.append(f"{self.parameter_id}: PROVENANCE_CLASS_NOT_RECOGNISED")
        if self.expected_value_role not in (HOME_K_FORWARD, "NONE"):
            problems.append(f"{self.parameter_id}: EXPECTED_VALUE_ROLE_NOT_RECOGNISED")
        if self.uncertainty_role not in (HOME_M_ECONOMIC, "NONE"):
            problems.append(f"{self.parameter_id}: UNCERTAINTY_ROLE_NOT_RECOGNISED")
        if not self.unit:
            problems.append(f"{self.parameter_id}: UNIT_UNDECLARED")
        # A value with no calibration authority may still be consumed, but only
        # with its model risk charged in M_economic. Friction partition s9.
        if (self.central_provenance in PROVENANCE_REQUIRING_MODEL_RISK
                and self.uncertainty_role != HOME_M_ECONOMIC):
            problems.append(
                f"{self.parameter_id}: EXISTING_EXECUTION_PARAMETER_IS_NOT_AUTOMATIC"
                "_CALIBRATION_AUTHORITY")
        if self.uncertainty_role == HOME_M_ECONOMIC and not self.envelope_provenance_rule:
            problems.append(f"{self.parameter_id}: ENVELOPE_PROVENANCE_RULE_UNDECLARED")
        if self.adverse_direction not in ADVERSE_DIRECTIONS:
            problems.append(f"{self.parameter_id}: ADVERSE_DIRECTION_NOT_DECLARED")
        # Generic intraday evidence is not automatic opening-regime calibration.
        if (self.execution_regime in OPENING_REGIMES
                and self.central_provenance != PROVENANCE_UNAVAILABLE
                and "GENERIC_INTRADAY" in (self.source_contract.population_applicability or "")):
            problems.append(
                f"{self.parameter_id}: GENERIC_INTRADAY_SPREAD_IS_NOT_AUTOMATIC_OPEN_CALIBRATION")
        return problems

    @property
    def resolved(self) -> bool:
        """True when the central value may be consumed by ``K_forward``."""
        if self.expected_value_role != HOME_K_FORWARD:
            return True
        return (self.central_estimate is not None
                and self.central_provenance != PROVENANCE_UNAVAILABLE)

    @property
    def carries_calibration_authority(self) -> bool:
        from .states import PROVENANCE_CALIBRATED
        return self.central_provenance == PROVENANCE_CALIBRATED

    def to_dict(self) -> dict[str, Any]:
        document = asdict(self)
        document["source_contract"] = self.source_contract.to_dict()
        document["dependence"] = self.dependence.to_dict()
        return document


class InventoryFrozen(RuntimeError):
    """A parameter was added after the inventory was frozen."""


class ParameterInventory:
    """Ordered, freezable registry of economic parameters.

    Freezing is the executable form of ``PARAMETER_SOURCE_RULE_PRECEDES_CANDIDATE
    _VALUES``: after the rule is hashed, a new parameter cannot appear, and a
    central value may only be supplied through :meth:`instantiate`, which keeps
    the frozen rule hash unchanged.
    """

    def __init__(self, inventory_id: str) -> None:
        self.inventory_id = inventory_id
        self._parameters: dict[str, EconomicParameter] = {}
        self._frozen_hash: str | None = None

    # -- construction ---------------------------------------------------------

    def add(self, parameter: EconomicParameter) -> "ParameterInventory":
        if self._frozen_hash is not None:
            raise InventoryFrozen(
                f"inventory {self.inventory_id} is frozen; {parameter.parameter_id} cannot be "
                "inserted without a governed version consequence")
        if parameter.parameter_id in self._parameters:
            raise ValueError(f"duplicate parameter id: {parameter.parameter_id}")
        self._parameters[parameter.parameter_id] = parameter
        return self

    def extend(self, parameters: Iterable[EconomicParameter]) -> "ParameterInventory":
        for parameter in parameters:
            self.add(parameter)
        return self

    # -- the rule, separated from the values -----------------------------------

    def rule_document(self) -> dict[str, Any]:
        """The parameter *rules* with every central value stripped out.

        This is what gets hashed before values are inspected.
        """
        rows = []
        for parameter in self._parameters.values():
            document = parameter.to_dict()
            document.pop("central_estimate", None)
            document.pop("central_provenance", None)
            rows.append(document)
        return {"inventory_id": self.inventory_id,
                "parameters": sorted(rows, key=lambda row: row["parameter_id"])}

    def freeze(self) -> str:
        """Hash the rule and refuse further structural change."""
        problems = self.violations()
        if problems:
            raise ValueError("cannot freeze an inventory with rule violations: "
                             + "; ".join(problems))
        self._frozen_hash = recipe_hash(self.rule_document())
        return self._frozen_hash

    @property
    def frozen_hash(self) -> str | None:
        return self._frozen_hash

    def instantiate(self, values: Mapping[str, tuple[float, str]]) -> "ParameterInventory":
        """Return a copy carrying central values, keeping the frozen rule hash.

        ``values`` maps ``parameter_id -> (central_estimate, provenance)``. A key
        that is not already in the inventory is refused: that is the insertion
        the contract forbids.
        """
        unknown = sorted(set(values) - set(self._parameters))
        if unknown:
            raise InventoryFrozen(
                "cannot instantiate parameters absent from the frozen inventory: "
                + ", ".join(unknown))
        clone = ParameterInventory(self.inventory_id)
        for parameter_id, parameter in self._parameters.items():
            if parameter_id in values:
                estimate, provenance = values[parameter_id]
                parameter = replace(parameter, central_estimate=estimate,
                                    central_provenance=provenance)
            clone._parameters[parameter_id] = parameter
        clone._frozen_hash = self._frozen_hash
        return clone

    # -- inspection -----------------------------------------------------------

    def violations(self) -> list[str]:
        problems: list[str] = []
        for parameter in self._parameters.values():
            problems.extend(parameter.violations())
        return problems

    def unresolved(self) -> list[str]:
        return sorted(parameter.parameter_id for parameter in self._parameters.values()
                      if not parameter.resolved)

    def requiring_model_risk(self) -> list[str]:
        return sorted(parameter.parameter_id for parameter in self._parameters.values()
                      if parameter.central_provenance in PROVENANCE_REQUIRING_MODEL_RISK)

    def central_values(self) -> dict[str, float]:
        return {parameter.parameter_id: parameter.central_estimate
                for parameter in self._parameters.values()
                if parameter.central_estimate is not None}

    def declared_classes(self) -> set[str]:
        return {parameter.cost_component for parameter in self._parameters.values()}

    def __contains__(self, parameter_id: object) -> bool:
        return parameter_id in self._parameters

    def __getitem__(self, parameter_id: str) -> EconomicParameter:
        return self._parameters[parameter_id]

    def __iter__(self) -> Iterator[EconomicParameter]:
        return iter(self._parameters.values())

    def __len__(self) -> int:
        return len(self._parameters)
