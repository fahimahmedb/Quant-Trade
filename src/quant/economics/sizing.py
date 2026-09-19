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
