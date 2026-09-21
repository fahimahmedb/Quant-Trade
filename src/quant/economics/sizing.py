"""Sizing and portfolio construction from the economic margin of safety.

Two rules shape this module.

First, size follows the economics. The exposure a lane receives is a declared,
monotone, outcome-blind function of how far its expected effect sits above the
economic threshold. It is not an optimum found by search: a rule tuned until the
size looked right would be the same threshold shopping the cost contract forbids,
one level down.

Second, risk approval must describe the portfolio that would actually be
simulated. A plan records the ordered transforms applied to it and hashes its
*final* state; :func:`verify_risk_approval` refuses an approval taken against an
earlier state. Approving a pre-scale portfolio and then scaling it is how a limit
gets satisfied on paper and breached in the Book.

Per-strategy sleeves stay separate throughout. Several strategies may reference
the same instrument, and the aggregate view exists for portfolio limits without
ever collapsing the attribution.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from typing import Any, Iterable, Mapping

from .fingerprint import recipe_hash


@dataclass(frozen=True)
class MarginSizingRule:
    """A declared monotone map from margin of safety to capital fraction.

    ``reference_margin`` is the margin of safety at which the rule awards
    ``max_fraction``. Both are declared before any effect estimate is seen; the
    rule is hashed with the plan so a later reader can tell whether the size was
    produced by the rule or by a preference.
    """

    rule_id: str
    #: Margin of safety, in effect-coordinate units, awarded ``max_fraction``.
    reference_margin: float
    #: Largest share of authorized capital any single lane may receive.
    max_fraction: float
    #: Below this margin the lane receives nothing, even if positive.
    minimum_margin: float = 0.0

    def violations(self) -> list[str]:
        problems: list[str] = []
        if self.reference_margin <= 0:
            problems.append(f"{self.rule_id}: REFERENCE_MARGIN_MUST_BE_POSITIVE")
        if not 0 < self.max_fraction <= 1:
            problems.append(f"{self.rule_id}: MAX_FRACTION_OUT_OF_RANGE")
        if self.minimum_margin < 0:
            problems.append(f"{self.rule_id}: MINIMUM_MARGIN_NEGATIVE")
        return problems

    def fraction(self, margin_of_safety: float) -> float:
        """Zero below the minimum, linear to ``max_fraction``, then flat."""
        if margin_of_safety <= self.minimum_margin:
            return 0.0
        scaled = (margin_of_safety - self.minimum_margin) / self.reference_margin
        return min(self.max_fraction, self.max_fraction * scaled)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SleeveTarget:
    """One strategy's target exposure in one instrument."""

    strategy_id: str
    symbol: str
    notional: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SizingPlan:
    """A target portfolio, its transform history and its final-state identity."""

    plan_id: str
    sleeves: tuple[SleeveTarget, ...]
    rule: MarginSizingRule | None = None
    #: Ordered names of every transform already applied.
    transforms: tuple[str, ...] = ()
    #: True once no further transform will be applied before simulation.
    final: bool = False

    # -- views ----------------------------------------------------------------

    def by_strategy(self) -> dict[str, dict[str, float]]:
        """Per-strategy sleeves. Attribution is never collapsed."""
        sleeves: dict[str, dict[str, float]] = {}
        for target in self.sleeves:
            bucket = sleeves.setdefault(target.strategy_id, {})
            bucket[target.symbol] = bucket.get(target.symbol, 0.0) + target.notional
        return sleeves

    def aggregate(self) -> dict[str, float]:
        """Portfolio-level exposure per instrument, for limit checks only."""
        totals: dict[str, float] = {}
        for target in self.sleeves:
            totals[target.symbol] = totals.get(target.symbol, 0.0) + target.notional
        return totals

    @property
    def gross_notional(self) -> float:
        return sum(abs(target.notional) for target in self.sleeves)

    # -- transforms -----------------------------------------------------------

    def transformed(self, name: str, sleeves: Iterable[SleeveTarget]) -> "SizingPlan":
        """Return a new plan with one more transform recorded.

        A transform on a plan already marked final is refused: the final state is
        what risk approved, and quietly changing it afterwards is the defect this
        class exists to prevent.
        """
        if self.final:
            raise ValueError(
                f"{self.plan_id}: RISK_APPROVAL_MUST_DESCRIBE_FINAL_PORTFOLIO — "
                f"transform {name!r} applied after the plan was marked final")
        return replace(self, sleeves=tuple(sleeves), transforms=self.transforms + (name,))

    def finalise(self) -> "SizingPlan":
        return replace(self, final=True)

    # -- identity -------------------------------------------------------------

    def final_state_document(self) -> dict[str, Any]:
        return {"plan_id": self.plan_id, "final": self.final,
                "transforms": list(self.transforms),
                "rule": self.rule.to_dict() if self.rule else None,
                "sleeves": sorted((target.to_dict() for target in self.sleeves),
                                  key=lambda row: (row["strategy_id"], row["symbol"]))}

    def final_state_hash(self) -> str:
        return recipe_hash(self.final_state_document())

    def to_dict(self) -> dict[str, Any]:
        document = self.final_state_document()
        document["gross_notional"] = self.gross_notional
        document["aggregate"] = dict(sorted(self.aggregate().items()))
        document["by_strategy"] = {key: dict(sorted(value.items()))
                                   for key, value in sorted(self.by_strategy().items())}
        document["final_state_hash"] = self.final_state_hash()
        return document


@dataclass(frozen=True)
class LaneSizeResult:
    """M3 SIZE authority — the one place ``FINAL_SIZE`` is computed.

    Frozen spec (``governance/BLUE_ONE_BIG_BUILD_PRESTAGE_2026-09-21.md`` §2.3,
    restated in the frozen build spec §5)::

        available_lane_capital = current_decision_NAV * strategy_allocation
        economic_margin_notional = MarginSizingRule(...)
        desk_lifecycle_cap_notional = available_lane_capital * definition.capital_fraction
        FINAL_SIZE = min(economic_margin_notional, desk_lifecycle_cap_notional)

    Economic owns opportunity sizing; the lifecycle capital fraction is only a
    ceiling. Because :meth:`MarginSizingRule.fraction` is clamped to
    ``[0, max_fraction]``, ``economic_margin_notional`` is never negative, so
    the lifecycle cap can only ever *reduce* ``FINAL_SIZE``, never manufacture
    size the economic margin did not authorize: a zero economic margin makes
    ``FINAL_SIZE`` zero regardless of how large the lifecycle fraction is.
    """

    strategy_id: str
    available_lane_capital: float
    margin_of_safety: float
    economic_fraction: float
    economic_margin_notional: float
    lifecycle_capital_fraction: float
    desk_lifecycle_cap_notional: float
    final_size_notional: float
    reason_codes: tuple[str, ...] = ()

    @property
    def zero_size(self) -> bool:
        return self.final_size_notional <= 0.0

    @property
    def lifecycle_cap_binding(self) -> bool:
        """True when the lifecycle ceiling, not the economic margin, decided size."""
        return self.desk_lifecycle_cap_notional < self.economic_margin_notional

    def to_dict(self) -> dict[str, Any]:
        document = asdict(self)
        document["reason_codes"] = list(self.reason_codes)
        document["zero_size"] = self.zero_size
        document["lifecycle_cap_binding"] = self.lifecycle_cap_binding
        return document


def compute_final_size(strategy_id: str, rule: MarginSizingRule, margin_of_safety: float,
                       current_decision_nav: float, strategy_allocation: float,
                       lifecycle_capital_fraction: float) -> LaneSizeResult:
    """Compute ``FINAL_SIZE`` for one lane at one decision instant.

    Fails closed to zero size (never to a fabricated positive size) on any
    out-of-range input, and records why. A negative ``current_decision_nav``
    or an allocation/fraction outside ``[0, 1]`` are input defects, not
    reasons to guess: they are clamped toward zero and reported, so the
    caller sees ``SIZE_*`` reason codes rather than a silently wrong number.
    """
    reasons: list[str] = []
    nav = current_decision_nav
    if nav < 0:
        reasons.append("SIZE_NEGATIVE_DECISION_NAV")
        nav = 0.0
    allocation = strategy_allocation
    if not 0.0 <= allocation <= 1.0:
        reasons.append("SIZE_STRATEGY_ALLOCATION_OUT_OF_RANGE")
        allocation = min(max(allocation, 0.0), 1.0)
    lifecycle_fraction = lifecycle_capital_fraction
    if not 0.0 <= lifecycle_fraction <= 1.0:
        reasons.append("SIZE_LIFECYCLE_CAPITAL_FRACTION_OUT_OF_RANGE")
        lifecycle_fraction = min(max(lifecycle_fraction, 0.0), 1.0)

    available_lane_capital = nav * allocation
    economic_fraction = rule.fraction(margin_of_safety)
    economic_margin_notional = available_lane_capital * economic_fraction
    desk_lifecycle_cap_notional = available_lane_capital * lifecycle_fraction
    final_size = min(economic_margin_notional, desk_lifecycle_cap_notional)

    if economic_margin_notional <= 0.0:
        reasons.append("SIZE_ZERO_ECONOMIC_MARGIN")
    elif final_size <= 0.0:
        reasons.append("SIZE_LIFECYCLE_CAP_YIELDED_ZERO")

    return LaneSizeResult(
        strategy_id=strategy_id, available_lane_capital=available_lane_capital,
        margin_of_safety=margin_of_safety, economic_fraction=economic_fraction,
        economic_margin_notional=economic_margin_notional,
        lifecycle_capital_fraction=lifecycle_fraction,
        desk_lifecycle_cap_notional=desk_lifecycle_cap_notional,
        final_size_notional=max(final_size, 0.0), reason_codes=tuple(reasons))


@dataclass(frozen=True)
class RiskApproval:
    """An approval bound to the exact portfolio state it examined."""

    approved: bool
    state_hash: str
    approver: str
    reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"approved": self.approved, "state_hash": self.state_hash,
                "approver": self.approver, "reasons": list(self.reasons)}


def verify_risk_approval(plan: SizingPlan, approval: RiskApproval) -> list[str]:
    """Refuse an approval that describes a state other than the final plan."""
    problems: list[str] = []
    if not plan.final:
        problems.append(f"{plan.plan_id}: PLAN_NOT_MARKED_FINAL")
    if approval.state_hash != plan.final_state_hash():
        problems.append(f"{plan.plan_id}: RISK_APPROVAL_MUST_DESCRIBE_FINAL_PORTFOLIO")
    if not approval.approved:
        problems.append(f"{plan.plan_id}: RISK_APPROVAL_WITHHELD")
    return problems


def size_lane(plan_id: str, rule: MarginSizingRule, margin_of_safety: float,
              capital: float, weights: Mapping[str, float],
              strategy_id: str) -> SizingPlan:
    """Build the pre-transform plan for one lane from its margin of safety.

    ``weights`` are the lane's relative exposures; they are scaled, never
    reshaped, so the relative weights that define the scientific policy survive
    (EC1: ``RELATIVE_WEIGHT_CHANGE_IS_NEW_POLICY_VERSION``).
    """
    fraction = rule.fraction(margin_of_safety)
    notional = capital * fraction
    total = sum(abs(weight) for weight in weights.values())
    sleeves = tuple(
        SleeveTarget(strategy_id, symbol, notional * weight / total)
        for symbol, weight in sorted(weights.items())) if total > 0 else ()
    return SizingPlan(plan_id=plan_id, sleeves=sleeves, rule=rule,
                      transforms=("MARGIN_SIZING",))


def combine_lanes(plan_id: str, plans: Iterable[SizingPlan]) -> SizingPlan:
    """Merge lane plans into one portfolio plan, keeping every sleeve distinct."""
    sleeves: list[SleeveTarget] = []
    transforms: list[str] = []
    for plan in plans:
        sleeves.extend(plan.sleeves)
        transforms.append(f"MERGE:{plan.plan_id}")
    return SizingPlan(plan_id=plan_id, sleeves=tuple(sleeves),
                      transforms=tuple(transforms))
