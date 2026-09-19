"""Regime analysis that cannot be chosen after the fact.

Splitting a sample into regimes is legitimate and informative. Choosing the split
after seeing which one flatters the result is not, and the two are
indistinguishable in a report unless the partition was declared and dated first.

So a :class:`RegimePartition` carries the instant it was declared and the inputs
it was derived from, and it is refused outright if those inputs include outcomes.
The breakdown reports the pooled estimate as the headline; the per-regime numbers
are diagnostics. ``BEST_REGIME_IS_NOT_THE_RESULT``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Sequence

from .inference import RatioEstimate, ratio_estimate


POST_HOC_REFUSED = "POST_HOC_REGIME_SELECTION_REFUSED"
BEST_REGIME_IS_NOT_THE_RESULT = "BEST_REGIME_IS_NOT_THE_RESULT"

#: Input classes that would make a partition outcome-dependent.
OUTCOME_BEARING_INPUTS = {
    "TARGET_OUTCOMES", "REALISED_RETURNS", "STRATEGY_PNL", "EFFECT_ESTIMATE",
    "SUBPERIOD_PERFORMANCE",
}


def _instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class RegimePartition:
    """An ex-ante partition of the sample into declared regimes."""

    partition_id: str
    regimes: tuple[str, ...]
    #: When the partition was declared.
    declared_at: str
    #: Input classes the partition rule was built from.
    derived_from: tuple[str, ...]
    #: Assigns a regime label to one observation key (e.g. a session date).
    assign: Callable[[Any], str] | None = None

    def violations(self, outcome_observed_at: str | None = None) -> list[str]:
        problems: list[str] = []
        if len(self.regimes) < 2:
            problems.append(f"{self.partition_id}: PARTITION_NEEDS_AT_LEAST_TWO_REGIMES")
        if len(set(self.regimes)) != len(self.regimes):
            problems.append(f"{self.partition_id}: DUPLICATE_REGIME_LABEL")
        if self.assign is None:
            problems.append(f"{self.partition_id}: NO_ASSIGNMENT_RULE")
        if not self.derived_from:
            problems.append(f"{self.partition_id}: PARTITION_INPUTS_UNDECLARED")
        for source in self.derived_from:
            if source in OUTCOME_BEARING_INPUTS:
                problems.append(f"{self.partition_id}: {POST_HOC_REFUSED}:{source}")
        try:
            declared = _instant(self.declared_at)
        except ValueError:
            problems.append(f"{self.partition_id}: DECLARED_AT_NOT_ISO8601")
            return problems
        if outcome_observed_at is not None:
            if declared >= _instant(outcome_observed_at):
                problems.append(f"{self.partition_id}: {POST_HOC_REFUSED}"
                                ":DECLARED_AT_OR_AFTER_OUTCOME_OBSERVATION")
        return problems

    def to_dict(self) -> dict[str, Any]:
        document = {key: value for key, value in asdict(self).items() if key != "assign"}
        document["has_assignment_rule"] = self.assign is not None
        return document


@dataclass(frozen=True)
class RegimeBreakdown:
    """Pooled headline plus per-regime diagnostics."""

    partition_id: str
    pooled: RatioEstimate
    by_regime: dict[str, RatioEstimate]
    counts: dict[str, int]
    violations: tuple[str, ...] = ()

    @property
    def headline(self) -> RatioEstimate:
        """Always the pooled estimate. The best regime is a diagnostic."""
        return self.pooled

    def spread(self) -> float | None:
        points = [estimate.point for estimate in self.by_regime.values()
                  if estimate.point is not None]
        if len(points) < 2:
            return None
        return max(points) - min(points)

    def to_dict(self) -> dict[str, Any]:
        return {"partition_id": self.partition_id, "pooled": self.pooled.to_dict(),
                "by_regime": {key: value.to_dict()
                              for key, value in sorted(self.by_regime.items())},
                "counts": dict(sorted(self.counts.items())),
                "spread": self.spread(),
                "headline_rule": BEST_REGIME_IS_NOT_THE_RESULT,
                "violations": list(self.violations)}


def regime_breakdown(partition: RegimePartition, keys: Sequence[Any],
                     weights: Sequence[float], outcomes: Sequence[float],
                     clusters: Sequence[Any] | None = None,
                     outcome_observed_at: str | None = None) -> RegimeBreakdown:
    """Estimate pooled and per-regime, refusing a partition that fails its checks."""
    problems = partition.violations(outcome_observed_at)
    pooled = ratio_estimate(weights, outcomes, clusters)
    if problems or partition.assign is None:
        return RegimeBreakdown(partition.partition_id, pooled, {}, {},
                               tuple(sorted(set(problems))))
    buckets: dict[str, list[int]] = {}
    unknown: list[str] = []
    for index, key in enumerate(keys):
        label = partition.assign(key)
        if label not in partition.regimes:
            unknown.append(f"{partition.partition_id}: REGIME_LABEL_NOT_DECLARED:{label}")
            continue
        buckets.setdefault(label, []).append(index)
    by_regime: dict[str, RatioEstimate] = {}
    counts: dict[str, int] = {}
    for label, indices in buckets.items():
        by_regime[label] = ratio_estimate(
            [weights[index] for index in indices],
            [outcomes[index] for index in indices],
            [clusters[index] for index in indices] if clusters is not None else None)
        counts[label] = len(indices)
    return RegimeBreakdown(partition.partition_id, pooled, by_regime, counts,
                           tuple(sorted(set(unknown))))
