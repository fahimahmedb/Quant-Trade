"""Inference on the allocation-weighted effect coordinate.

EC1 section 6 is explicit about the trap: the natural estimator

    delta_hat = sum_j a_j T_j / sum_j a_j

has a *random denominator*, because event count, eligibility, overlap, capacity
and pre-outcome weights all vary.  So the variance of ``delta_hat`` is not the
variance of one primitive ``T_j`` divided by an event count
(``PRIMITIVE_RETURN_VARIANCE_IS_NOT_AGGREGATE_ESTIMATOR_VARIANCE``).

This module gives the ratio estimator a cluster-robust variance that treats the
denominator as random, and a deterministic cluster bootstrap for the cases where
the linearisation is not trusted. Clusters matter: overlapping exposures on one
issuer are not independent observations, and treating them as independent is how
a t-statistic doubles for free.

It also keeps the two thresholds apart. Statistical distinguishability from zero
and economic sufficiency against MEUE are different questions, and neither one
substitutes for the other (``STATISTICAL_SIGNIFICANCE_IS_NOT_ECONOMIC_SUFFICIENCY``).
"""

from __future__ import annotations

import math
import random
from dataclasses import asdict, dataclass, field
from statistics import NormalDist
from typing import Any, Sequence

from ..factory.evaluate import required_t_statistic


METHOD_DELTA_CLUSTERED = "DELTA_METHOD_CLUSTER_ROBUST"
METHOD_CLUSTER_BOOTSTRAP = "CLUSTER_BOOTSTRAP_PERCENTILE"

ESTIMATE_RESOLVED = "ESTIMATE_RESOLVED"
ESTIMATE_NO_EXPOSURE = "NO_DEPLOYED_EXPOSURE"
ESTIMATE_SINGLE_CLUSTER = "VARIANCE_UNIDENTIFIED_FROM_ONE_CLUSTER"


@dataclass(frozen=True)
class RatioEstimate:
    """``delta_hat`` with a variance that respects the random denominator."""

    state: str
    point: float | None
    standard_error: float | None
    lower: float | None
    upper: float | None
    confidence_level: float
    method: str
    #: Number of independent clusters the variance is identified from.
    clusters: int
    observations: int
    denominator: float
    detail: str = ""

    @property
    def resolved(self) -> bool:
        return self.state == ESTIMATE_RESOLVED and self.point is not None

    @property
    def t_statistic(self) -> float | None:
        if self.point is None or not self.standard_error:
            return None
        return self.point / self.standard_error

    def to_dict(self) -> dict[str, Any]:
        document = asdict(self)
        document["t_statistic"] = self.t_statistic
        return document


def _grouped(weights: Sequence[float], outcomes: Sequence[float],
             clusters: Sequence[Any] | None) -> dict[Any, list[int]]:
    keys = clusters if clusters is not None else range(len(weights))
    groups: dict[Any, list[int]] = {}
    for index, key in enumerate(keys):
        groups.setdefault(key, []).append(index)
    return groups


def ratio_estimate(weights: Sequence[float], outcomes: Sequence[float],
                   clusters: Sequence[Any] | None = None,
                   confidence_level: float = 0.95) -> RatioEstimate:
    """Cluster-robust delta-method estimate of the weighted ratio.

    With ``r_j = a_j (T_j - delta_hat)`` and clusters ``c``:

        Var(delta_hat) ~= sum_c ( sum_{j in c} r_j )^2 / (sum_j a_j)^2

    which is the sandwich variance for a weighted mean. It reduces to the
    familiar form when every observation is its own cluster, and it grows — as it
    should — when overlapping exposures on one issuer are correctly grouped.
    """
    if len(weights) != len(outcomes):
        raise ValueError("weights and outcomes must have the same length")
    if clusters is not None and len(clusters) != len(weights):
        raise ValueError("clusters must align with weights")
    denominator = float(sum(weights))
    if denominator <= 0:
        return RatioEstimate(ESTIMATE_NO_EXPOSURE, None, None, None, None,
                             confidence_level, METHOD_DELTA_CLUSTERED, 0, len(weights),
                             denominator, "sum of allocation weights is not positive")
    point = float(sum(weight * outcome
                      for weight, outcome in zip(weights, outcomes))) / denominator
    groups = _grouped(weights, outcomes, clusters)
    if len(groups) < 2:
        return RatioEstimate(ESTIMATE_SINGLE_CLUSTER, point, None, None, None,
                             confidence_level, METHOD_DELTA_CLUSTERED, len(groups),
                             len(weights), denominator,
                             "one cluster cannot identify a between-cluster variance")
    total = 0.0
    for indices in groups.values():
        contribution = sum(weights[index] * (outcomes[index] - point) for index in indices)
        total += contribution * contribution
    variance = total / (denominator * denominator)
    # Small-cluster correction, the usual G/(G-1) inflation.
    groups_count = len(groups)
    variance *= groups_count / (groups_count - 1)
    standard_error = math.sqrt(variance)
    z = NormalDist().inv_cdf(0.5 + confidence_level / 2.0)
    return RatioEstimate(ESTIMATE_RESOLVED, point, standard_error,
                         point - z * standard_error, point + z * standard_error,
                         confidence_level, METHOD_DELTA_CLUSTERED, groups_count,
                         len(weights), denominator)


def cluster_bootstrap_ratio(weights: Sequence[float], outcomes: Sequence[float],
                            clusters: Sequence[Any] | None = None,
                            confidence_level: float = 0.95, draws: int = 2000,
                            seed: int = 20260919) -> RatioEstimate:
    """Percentile interval from resampling whole clusters, with a declared seed.

    The seed is part of the method: an interval that moves between runs is not a
    reproducible result.
    """
    denominator = float(sum(weights))
    if denominator <= 0:
        return RatioEstimate(ESTIMATE_NO_EXPOSURE, None, None, None, None,
                             confidence_level, METHOD_CLUSTER_BOOTSTRAP, 0, len(weights),
                             denominator, "sum of allocation weights is not positive")
    groups = _grouped(weights, outcomes, clusters)
    keys = sorted(groups, key=repr)
    point = float(sum(weight * outcome
                      for weight, outcome in zip(weights, outcomes))) / denominator
    if len(keys) < 2:
        return RatioEstimate(ESTIMATE_SINGLE_CLUSTER, point, None, None, None,
                             confidence_level, METHOD_CLUSTER_BOOTSTRAP, len(keys),
                             len(weights), denominator,
                             "one cluster cannot identify a between-cluster variance")
    generator = random.Random(seed)
    samples: list[float] = []
    for _ in range(draws):
        numerator = 0.0
        weight_total = 0.0
        for _ in keys:
            indices = groups[keys[generator.randrange(len(keys))]]
            for index in indices:
                numerator += weights[index] * outcomes[index]
                weight_total += weights[index]
        if weight_total > 0:
            samples.append(numerator / weight_total)
    if len(samples) < 2:
        return RatioEstimate(ESTIMATE_SINGLE_CLUSTER, point, None, None, None,
                             confidence_level, METHOD_CLUSTER_BOOTSTRAP, len(keys),
                             len(weights), denominator, "bootstrap produced no draws")
    samples.sort()
    tail = (1.0 - confidence_level) / 2.0
    lower = samples[max(0, int(math.floor(tail * len(samples))))]
    upper = samples[min(len(samples) - 1, int(math.ceil((1.0 - tail) * len(samples))) - 1)]
    mean = sum(samples) / len(samples)
    spread = math.sqrt(sum((value - mean) ** 2 for value in samples) / (len(samples) - 1))
    return RatioEstimate(ESTIMATE_RESOLVED, point, spread, lower, upper, confidence_level,
                         METHOD_CLUSTER_BOOTSTRAP, len(keys), len(weights), denominator,
                         f"seed={seed};draws={len(samples)}")


@dataclass
class MultiplicityBudget:
    """Declared trial budget. It may grow with disclosure; it may never shrink."""

    declared_trials: int
    charged: int = 0
    history: list[str] = field(default_factory=list)

    def charge(self, trials: int, reason: str = "") -> None:
        if trials < 0:
            raise ValueError("cannot charge a negative number of trials")
        self.charged += trials
        self.history.append(f"+{trials}:{reason}")

    def widen(self, additional: int, reason: str) -> None:
        """Disclose extra trials. Widening is allowed; it raises the threshold."""
        if additional <= 0:
            raise ValueError("widening must add trials")
        self.declared_trials += additional
        self.history.append(f"widen+{additional}:{reason}")

    def narrow(self, *_args: Any, **_kwargs: Any) -> None:
        raise ValueError("MULTIPLICITY_BUDGET_CANNOT_SHRINK")

    @property
    def effective_trials(self) -> int:
        return max(self.declared_trials, self.charged)

    def threshold(self) -> float:
        return required_t_statistic(self.effective_trials)

    def violations(self) -> list[str]:
        problems: list[str] = []
        if self.charged > self.declared_trials:
            problems.append("TRIALS_CHARGED_EXCEED_DECLARED_BUDGET")
        if self.declared_trials <= 0:
            problems.append("MULTIPLICITY_BUDGET_UNDECLARED")
        return problems

    def to_dict(self) -> dict[str, Any]:
        return {"declared_trials": self.declared_trials, "charged": self.charged,
                "effective_trials": self.effective_trials, "threshold": self.threshold(),
                "history": list(self.history), "violations": self.violations()}


STATISTICALLY_DISTINGUISHABLE = "STATISTICALLY_DISTINGUISHABLE_FROM_ZERO"
STATISTICALLY_INDISTINGUISHABLE = "STATISTICALLY_INDISTINGUISHABLE_FROM_ZERO"
ECONOMICALLY_SUFFICIENT = "EFFECT_INTERVAL_ABOVE_MEUE"
ECONOMICALLY_INSUFFICIENT = "EFFECT_INTERVAL_NOT_ABOVE_MEUE"
ECONOMICALLY_DOMINATED = "EFFECT_INTERVAL_ENTIRELY_BELOW_MEUE"


@dataclass(frozen=True)
class StatisticalEconomicVerdict:
    """The two questions, answered separately and reported together."""

    statistical: str
    economic: str
    t_statistic: float | None
    threshold: float
    meue: float | None
    estimate: RatioEstimate
    violations: tuple[str, ...] = ()

    @property
    def both_satisfied(self) -> bool:
        return (self.statistical == STATISTICALLY_DISTINGUISHABLE
                and self.economic == ECONOMICALLY_SUFFICIENT and not self.violations)

    def to_dict(self) -> dict[str, Any]:
        return {"statistical": self.statistical, "economic": self.economic,
                "t_statistic": self.t_statistic, "threshold": self.threshold,
                "meue": self.meue, "estimate": self.estimate.to_dict(),
                "both_satisfied": self.both_satisfied,
                "violations": list(self.violations)}


def statistical_economic_verdict(estimate: RatioEstimate, meue: float | None,
                                 budget: MultiplicityBudget) -> StatisticalEconomicVerdict:
    """Answer both questions. Neither answer is allowed to stand in for the other."""
    problems = list(budget.violations())
    threshold = budget.threshold()
    if not estimate.resolved:
        problems.append(estimate.state)
        return StatisticalEconomicVerdict(STATISTICALLY_INDISTINGUISHABLE,
                                          ECONOMICALLY_INSUFFICIENT, None, threshold,
                                          meue, estimate, tuple(sorted(set(problems))))
    t_statistic = estimate.t_statistic
    statistical = (STATISTICALLY_DISTINGUISHABLE
                   if t_statistic is not None and abs(t_statistic) >= threshold
                   else STATISTICALLY_INDISTINGUISHABLE)
    if meue is None:
        problems.append("ECONOMIC_THRESHOLD_UNAVAILABLE")
        economic = ECONOMICALLY_INSUFFICIENT
    elif estimate.upper is not None and estimate.upper < meue:
        economic = ECONOMICALLY_DOMINATED
    elif estimate.lower is not None and estimate.lower > meue:
        economic = ECONOMICALLY_SUFFICIENT
    else:
        economic = ECONOMICALLY_INSUFFICIENT
    return StatisticalEconomicVerdict(statistical, economic, t_statistic, threshold, meue,
                                      estimate, tuple(sorted(set(problems))))
