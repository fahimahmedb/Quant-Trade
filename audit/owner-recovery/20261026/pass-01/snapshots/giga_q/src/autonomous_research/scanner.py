"""Dependency-free cheap scanner for lagged return dependence."""

from __future__ import annotations

import math
import statistics


def log_returns(close: list[float]) -> list[float]:
    return [math.log(close[i] / close[i - 1]) for i in range(1, len(close))]


def _correlation(x: list[float], y: list[float]) -> float:
    mx, my = statistics.mean(x), statistics.mean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    return num / den if den else 0.0


def scan_lag_dependence(close: list[float], discovery_fraction: float = 0.6) -> dict:
    returns = log_returns(close)
    cutoff = int(len(returns) * discovery_fraction)
    discovery = returns[:cutoff]
    candidates = []
    for lookback in (1, 2, 5):
        trailing = [sum(discovery[i - lookback:i]) for i in range(lookback, len(discovery))]
        rho = _correlation(trailing, discovery[lookback:])
        candidates.append({"lookback_days": lookback, "correlation": rho})
    ranked = sorted(candidates, key=lambda item: abs(item["correlation"]), reverse=True)
    return {"discovery_observations": cutoff, "candidates": ranked, "selected": ranked[0]}
