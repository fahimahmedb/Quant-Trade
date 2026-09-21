"""Capacity as a first-order economic object, not a footnote.

Two distinct things happen when a policy is too large for the liquidity it
trades:

1. less capital is deployed than intended, which changes ``Q(theta)`` and
   therefore the gross economic contribution;
2. if the clipping is uneven across names, the *relative* weights change, and
   EC1 section 4 is unambiguous about what that means —
   ``CAPACITY_CLIPPING_THAT_CHANGES_RELATIVE_WEIGHTS_IS_NEW_POLICY_VERSION``.
   The estimand moved. A claim confirmed on the unclipped weights does not
   transfer to the clipped ones.

Most systems record (1) and quietly ignore (2). This module reports both, and
refuses to report a clipped allocation as the same scientific policy.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from .theta import Q_PROVENANCE_ALLOCATION_CONSTRUCTOR


#: Consequence of capacity clipping for the scientific claim.
POLICY_UNCHANGED = "POLICY_UNCHANGED"
POLICY_SCALED_HOMOGENEOUSLY = "POLICY_SCALED_HOMOGENEOUSLY"
NEW_POLICY_VERSION = "CAPACITY_CLIPPING_THAT_CHANGES_RELATIVE_WEIGHTS_IS_NEW_POLICY_VERSION"

#: Where a liquidity reference came from. A reference selected using Form 4
#: outcomes would contaminate the recipe, so provenance is mandatory.
LIQUIDITY_PROVENANCE_CLASSES = (
    "PERMITTED_PRE_OUTCOME_PANEL_LOOKBACK",
    "EXTERNAL_REFERENCE_NOT_SELECTED_ON_TARGET_OUTCOMES",
    "ENGINEERING_PLAUSIBILITY_BOUND_WITH_GOVERNANCE_STATUS",
)


@dataclass(frozen=True)
class CapacityLimit:
    """The deployable notional ceiling for one name."""

    symbol: str
    #: Average daily traded notional, from a permitted pre-outcome lookback.
    adv_notional: float
    #: Maximum share of that notional the policy may take.
    max_participation: float
    provenance: str
    #: Last date of the lookback. Must not reach past the decision date.
    as_of: str | None = None

    def violations(self) -> list[str]:
        problems: list[str] = []
        if self.adv_notional < 0:
            problems.append(f"{self.symbol}: ADV_NOTIONAL_NEGATIVE")
        if not 0 < self.max_participation <= 1:
            problems.append(f"{self.symbol}: PARTICIPATION_LIMIT_OUT_OF_RANGE")
        if self.provenance not in LIQUIDITY_PROVENANCE_CLASSES:
            problems.append(f"{self.symbol}: LIQUIDITY_PROVENANCE_NOT_ADMITTED")
        return problems

    @property
    def ceiling(self) -> float:
        return self.adv_notional * self.max_participation

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CapacityOutcome:
    """What the policy could actually deploy, and what that did to the claim."""

    requested: dict[str, float]
    granted: dict[str, float]
    binding: tuple[str, ...]
    policy_consequence: str
    #: Scale factor when the clipping happened to be homogeneous.
    homogeneous_scale: float | None = None
    violations: tuple[str, ...] = ()

    @property
    def requested_total(self) -> float:
        return sum(abs(value) for value in self.requested.values())

    @property
    def granted_total(self) -> float:
        return sum(abs(value) for value in self.granted.values())

    @property
    def truncated_total(self) -> float:
        return self.requested_total - self.granted_total

    @property
    def relative_weights_preserved(self) -> bool:
        return self.policy_consequence in (POLICY_UNCHANGED, POLICY_SCALED_HOMOGENEOUSLY)

    def to_dict(self) -> dict[str, Any]:
        return {"requested": dict(sorted(self.requested.items())),
                "granted": dict(sorted(self.granted.items())),
                "binding": list(self.binding),
                "policy_consequence": self.policy_consequence,
                "homogeneous_scale": self.homogeneous_scale,
                "requested_total": self.requested_total,
                "granted_total": self.granted_total,
                "truncated_total": self.truncated_total,
                "relative_weights_preserved": self.relative_weights_preserved,
                "violations": list(self.violations)}


def apply_capacity(requested: Mapping[str, float], schedule: Mapping[str, CapacityLimit],
                   tolerance: float = 1e-9) -> CapacityOutcome:
    """Clip a requested allocation to capacity and classify the consequence.

    A name with no capacity limit is *not* treated as unlimited: absence of a
    liquidity reference is a missing input, recorded as a violation, and the name
    is granted nothing. Presuming infinite liquidity where nobody measured it is
    the single most flattering assumption available in a paper system.
    """
    problems: list[str] = []
    granted: dict[str, float] = {}
    binding: list[str] = []
    for symbol, notional in requested.items():
        limit = schedule.get(symbol)
        if limit is None:
            problems.append(f"{symbol}: NO_LIQUIDITY_REFERENCE_IS_NOT_UNLIMITED_CAPACITY")
            granted[symbol] = 0.0
            binding.append(symbol)
            continue
        problems.extend(limit.violations())
        ceiling = limit.ceiling
        magnitude = abs(notional)
        if magnitude > ceiling + tolerance:
            binding.append(symbol)
            sign = 1.0 if notional >= 0 else -1.0
            granted[symbol] = sign * ceiling
        else:
            granted[symbol] = float(notional)

    consequence = _classify(requested, granted, tolerance)
    scale = None
    if consequence == POLICY_SCALED_HOMOGENEOUSLY:
        requested_total = sum(abs(value) for value in requested.values())
        scale = (sum(abs(value) for value in granted.values()) / requested_total
                 if requested_total > 0 else None)
    return CapacityOutcome(dict(requested), granted, tuple(binding), consequence, scale,
                           tuple(sorted(set(problems))))


def _classify(requested: Mapping[str, float], granted: Mapping[str, float],
              tolerance: float) -> str:
    """Unchanged, homogeneously scaled, or a new scientific policy version."""
    ratios: list[float] = []
    for symbol, notional in requested.items():
        if abs(notional) <= tolerance:
            continue
        ratios.append(abs(granted.get(symbol, 0.0)) / abs(notional))
    if not ratios:
        return POLICY_UNCHANGED
    if all(abs(ratio - 1.0) <= tolerance for ratio in ratios):
        return POLICY_UNCHANGED
    if max(ratios) - min(ratios) <= tolerance:
        # One positive scalar lambda applies to every weight: EC1 section 4
        # leaves the effect coordinate unchanged.
        return POLICY_SCALED_HOMOGENEOUSLY
    return NEW_POLICY_VERSION


@dataclass(frozen=True)
class ExposureBudget:
    """``Q(theta)`` built from the allocation policy and capacity, with provenance.

    EC1 section 7: ``Q(theta)`` must reflect the frozen allocation/overlap/
    capital-saturation semantics and is never replaced by naive
    ``C * event_count`` annualisation. So Q is summed from per-event granted
    exposures, and the provenance says so.
    """

    #: One entry per expected event in the evaluation regime: granted notional.
    granted_by_event: tuple[float, ...]
    evaluation_regime: str
    overlap_treatment: str
    #: True when any event's exposure was capacity-clipped.
    any_clipping: bool = False
    #: True when clipping changed relative weights anywhere.
    policy_version_changed: bool = False

    @property
    def q(self) -> float:
        return float(sum(self.granted_by_event))

    @property
    def provenance(self) -> str:
        return Q_PROVENANCE_ALLOCATION_CONSTRUCTOR

    def violations(self) -> list[str]:
        problems: list[str] = []
        if not self.overlap_treatment:
            problems.append("OVERLAP_TREATMENT_UNDECLARED")
        if self.evaluation_regime in ("", "UNDECLARED"):
            problems.append("EVALUATION_REGIME_UNDECLARED")
        if self.policy_version_changed:
            problems.append(NEW_POLICY_VERSION)
        if any(value < 0 for value in self.granted_by_event):
            problems.append("GRANTED_EXPOSURE_NEGATIVE")
        return problems

    def to_dict(self) -> dict[str, Any]:
        return {"event_count": len(self.granted_by_event), "q": self.q,
                "evaluation_regime": self.evaluation_regime,
                "overlap_treatment": self.overlap_treatment,
                "any_clipping": self.any_clipping,
                "policy_version_changed": self.policy_version_changed,
                "q_provenance": self.provenance}
