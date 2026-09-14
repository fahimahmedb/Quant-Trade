"""Monte Carlo power on synthetic standardized effects only."""
from __future__ import annotations

from dataclasses import dataclass
import math
import random
import statistics
from statistics import NormalDist

from .experiments import ExperimentError
from .geometry import GeometryReport


@dataclass(frozen=True)
class PowerScenario:
    standardized_effect: float
    alpha: float = 0.05
    simulations: int = 2000
    issuer_icc: float = 0.0
    seed: int = 0

    def __post_init__(self) -> None:
        if not (0.0 < self.alpha < 1.0):
            raise ExperimentError("alpha must lie in (0, 1)")
        if self.simulations <= 0:
            raise ExperimentError("simulations must be positive")
        if not (0.0 <= self.issuer_icc < 1.0):
            raise ExperimentError("issuer_icc must lie in [0, 1)")


@dataclass(frozen=True)
class PowerResult:
    estimated_power: float
    monte_carlo_se: float
    simulations: int
    n: int
    issuer_count: int
    synthetic_only: bool = True


class PowerSimulationEngine:
    """Simulate standardized synthetic measurements with optional issuer clustering."""

    def simulate(self, geometry: GeometryReport, scenario: PowerScenario) -> PowerResult:
        if geometry.n < 2:
            raise ExperimentError("power simulation requires at least two events")
        counts = list(geometry.events_per_issuer.values())
        if sum(counts) != geometry.n:
            raise ExperimentError("geometry issuer counts do not sum to N")
        rng = random.Random(scenario.seed)
        critical = NormalDist().inv_cdf(1.0 - scenario.alpha / 2.0)
        rejected = 0
        shared_scale = math.sqrt(scenario.issuer_icc)
        idio_scale = math.sqrt(1.0 - scenario.issuer_icc)

        for _ in range(scenario.simulations):
            groups: list[list[float]] = []
            for count in counts:
                shared = rng.gauss(0.0, 1.0)
                values = [
                    scenario.standardized_effect
                    + shared_scale * shared
                    + idio_scale * rng.gauss(0.0, 1.0)
                    for _ in range(count)
                ]
                groups.append(values)
            values = [value for group in groups for value in group]
            mean = statistics.fmean(values)
            se = self._standard_error(groups, mean)
            if se > 0.0 and abs(mean / se) >= critical:
                rejected += 1

        power = rejected / scenario.simulations
        mc_se = math.sqrt(power * (1.0 - power) / scenario.simulations)
        return PowerResult(
            estimated_power=power,
            monte_carlo_se=mc_se,
            simulations=scenario.simulations,
            n=geometry.n,
            issuer_count=len(counts),
        )

    @staticmethod
    def _standard_error(groups: list[list[float]], mean: float) -> float:
        n = sum(len(group) for group in groups)
        g = len(groups)
        if g > 1:
            cluster_sums = [sum(value - mean for value in group) for group in groups]
            variance = sum(value * value for value in cluster_sums) / (n * n)
            variance *= g / (g - 1)
            return math.sqrt(max(variance, 0.0))
        values = groups[0]
        if len(values) < 2:
            return 0.0
        return statistics.stdev(values) / math.sqrt(len(values))