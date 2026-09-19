"""``DELTA_COORDINATE_COMPATIBILITY_GATE`` — remainder contract object A.

EC1 closed what ``delta`` *means*: the deployment-weighted expected gross
SPY-relative return per unit of Form 4 capital actually deployed.  It did not
close the proof that the accounting implementation which eventually produces a
number lives on that same coordinate.

This gate is that proof, made executable.  It binds the five declarations the
remainder contract section 3 requires, refuses to guess a missing one, and
returns a mismatch rather than quietly bending the coordinate to fit whatever
data happens to exist:

    A mismatch reopens the final outcome/estimand implementation. It does not
    redefine EC1's economic coordinate to fit available data.

The gate deliberately knows nothing about realised returns. It compares
*declarations*.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .fingerprint import recipe_hash
from .states import (DELTA_COORDINATE_COMPATIBLE, DELTA_COORDINATE_MISMATCH,
                     DELTA_COORDINATE_UNRESOLVED)


#: The only aggregation shape EC1 admits: a ratio of expectations with the
#: allocation weight fixed before the outcome is known.
ALLOCATION_WEIGHTED_RATIO = "E[sum_j a_j T_j] / E[sum_j a_j]"

#: Aggregations that are *named* by EC1 section 5 as things delta is not.
REJECTED_AGGREGATIONS = {
    "UNWEIGHTED_EVENT_MEAN": "UNWEIGHTED_EVENT_MEAN_DOES_NOT_DEFINE_DEPLOYMENT_VALUE",
    "REALISED_PORTFOLIO_RETURN": "DELTA_IS_NOT_REALISED_PORTFOLIO_RETURN",
    "NET_OF_FRICTION_RETURN": "DELTA_IS_GROSS_OF_FORM4_DEPLOYMENT_FRICTIONS",
    "EXPECTED_SAMPLE_RATIO": "DELTA_IS_A_RATIO_OF_EXPECTATIONS_NOT_AN_EXPECTED_RATIO",
    "PROGRAM_ROI": "PROGRAM_COST_DOES_NOT_ENTER_MARKET_DEPLOYMENT_MEUE",
}


@dataclass(frozen=True)
class ReturnConvention:
    """One side's return accounting. Security and benchmark must agree."""

    #: e.g. "SIMPLE_SINGLE_PERIOD"; compounding/log changes the coordinate.
    return_definition: str | None = None
    #: The holding interval after final D07 / public-observability resolution.
    interval_spec: str | None = None
    #: Corporate-action and distribution treatment.
    corporate_action_convention: str | None = None
    #: Terminal / delisting treatment, jointly governed with D19.
    terminal_treatment: str | None = None

    def declared(self) -> bool:
        return all(value is not None for value in asdict(self).values())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DeltaCoordinateBinding:
    """The declarations the remainder contract requires before consumption."""

    security: ReturnConvention = field(default_factory=ReturnConvention)
    benchmark: ReturnConvention = field(default_factory=ReturnConvention)
    #: Name of the scientific benchmark. EC1: SCIENTIFIC_BENCHMARK_REMAINS_SPY.
    benchmark_symbol: str | None = None
    #: How primitive T_j are aggregated into the estimand.
    aggregation: str | None = None
    #: Identifier of the frozen allocation constructor whose weights are used.
    allocation_constructor_id: str | None = None
    #: True when the weight a_j is fixed from pre-outcome state only.
    allocation_weight_precedes_outcome: bool | None = None
    #: D19 routing reference for the terminal treatment, when one applies.
    d19_reference: str | None = None

    def to_dict(self) -> dict[str, Any]:
        document = asdict(self)
        return document


@dataclass(frozen=True)
class DeltaCoordinateVerdict:
    state: str
    reasons: tuple[str, ...]
    binding_hash: str | None

    @property
    def compatible(self) -> bool:
        return self.state == DELTA_COORDINATE_COMPATIBLE

    def to_dict(self) -> dict[str, Any]:
        return {"state": self.state, "reasons": list(self.reasons),
                "binding_hash": self.binding_hash}


def _missing(binding: DeltaCoordinateBinding) -> list[str]:
    missing: list[str] = []
    if not binding.security.declared():
        missing.append("SECURITY_RETURN_CONVENTION_UNDECLARED")
    if not binding.benchmark.declared():
        missing.append("BENCHMARK_RETURN_CONVENTION_UNDECLARED")
    if binding.benchmark_symbol is None:
        missing.append("BENCHMARK_SYMBOL_UNDECLARED")
    if binding.aggregation is None:
        missing.append("AGGREGATION_UNDECLARED")
    if binding.allocation_constructor_id is None:
        missing.append("ALLOCATION_CONSTRUCTOR_UNDECLARED")
    if binding.allocation_weight_precedes_outcome is None:
        missing.append("ALLOCATION_WEIGHT_ORDERING_UNDECLARED")
    if (binding.security.terminal_treatment is not None
            and binding.security.terminal_treatment != "NOT_APPLICABLE"
            and binding.d19_reference is None):
        missing.append("TERMINAL_TREATMENT_WITHOUT_D19_REFERENCE")
    return missing


def _mismatches(binding: DeltaCoordinateBinding) -> list[str]:
    reasons: list[str] = []
    security = binding.security
    benchmark = binding.benchmark
    if security.interval_spec != benchmark.interval_spec:
        reasons.append("BENCHMARK_INTERVAL_INCOMPATIBLE")
    if security.return_definition != benchmark.return_definition:
        reasons.append("BENCHMARK_RETURN_DEFINITION_INCOMPATIBLE")
    if security.corporate_action_convention != benchmark.corporate_action_convention:
        reasons.append("BENCHMARK_CORPORATE_ACTION_CONVENTION_INCOMPATIBLE")
    if binding.benchmark_symbol != "SPY":
        reasons.append("SCIENTIFIC_BENCHMARK_REMAINS_SPY")
    if binding.aggregation in REJECTED_AGGREGATIONS:
        reasons.append(REJECTED_AGGREGATIONS[binding.aggregation])
    elif binding.aggregation != ALLOCATION_WEIGHTED_RATIO:
        reasons.append("AGGREGATION_NOT_THE_FROZEN_ALLOCATION_WEIGHTED_RATIO")
    if binding.allocation_weight_precedes_outcome is False:
        reasons.append("ALLOCATION_WEIGHT_PRECEDES_OUTCOME")
    return reasons


def evaluate_delta_coordinate(binding: DeltaCoordinateBinding) -> DeltaCoordinateVerdict:
    """Return the gate state for one binding.

    Undeclared beats mismatched: a binding that has not said what it does yet is
    ``DELTA_COORDINATE_UNRESOLVED``, because reporting a mismatch would claim we
    inspected something that does not exist.
    """
    missing = _missing(binding)
    if missing:
        return DeltaCoordinateVerdict(DELTA_COORDINATE_UNRESOLVED, tuple(missing), None)
    reasons = _mismatches(binding)
    if reasons:
        return DeltaCoordinateVerdict(DELTA_COORDINATE_MISMATCH, tuple(reasons), None)
    return DeltaCoordinateVerdict(DELTA_COORDINATE_COMPATIBLE, (),
                                  recipe_hash(binding.to_dict()))
