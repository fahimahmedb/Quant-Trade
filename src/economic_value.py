"""Dependency-free, causal economic evaluation utilities."""
from __future__ import annotations

import math
from dataclasses import dataclass


TRADING_DAYS = 252


@dataclass(frozen=True)
class Performance:
    terminal_wealth: float
    cagr: float
    annual_volatility: float
    max_drawdown: float
    turnover: float


def ewma_exposures(
    log_returns: list[float], train_size: int, lam: float = 0.94,
    target_volatility: float = 0.20, cap: float = 1.0,
) -> list[float]:
    """Return OOS exposures; return ``t`` never enters exposure ``t``."""
    if not 0 < lam < 1 or train_size < 2 or len(log_returns) <= train_size:
        raise ValueError("invalid EWMA inputs")
    train = log_returns[:train_size]
    mean = sum(train) / len(train)
    variance = sum((value - mean) ** 2 for value in train) / len(train)
    # Bring the state causally to the end of training.
    for value in train:
        variance = lam * variance + (1 - lam) * (value - mean) ** 2

    exposures = []
    for value in log_returns[train_size:]:
        forecast_vol = math.sqrt(max(variance, 1e-16) * TRADING_DAYS)
        exposures.append(min(cap, target_volatility / forecast_vol))
        variance = lam * variance + (1 - lam) * (value - mean) ** 2
    return exposures


def evaluate(simple_returns: list[float], exposures: list[float], cost_bps: float) -> Performance:
    if len(simple_returns) != len(exposures) or not simple_returns:
        raise ValueError("returns and exposures must be non-empty and aligned")
    wealth, peak, max_dd, turnover = 1.0, 1.0, 0.0, 0.0
    daily_net = []
    previous = 0.0
    for ret, exposure in zip(simple_returns, exposures):
        trade = abs(exposure - previous)
        net = exposure * ret - trade * cost_bps / 10_000
        wealth *= 1 + net
        peak = max(peak, wealth)
        max_dd = min(max_dd, wealth / peak - 1)
        turnover += trade
        daily_net.append(net)
        previous = exposure
    years = len(simple_returns) / TRADING_DAYS
    mean = sum(daily_net) / len(daily_net)
    variance = sum((x - mean) ** 2 for x in daily_net) / max(1, len(daily_net) - 1)
    return Performance(
        terminal_wealth=wealth,
        cagr=wealth ** (1 / years) - 1,
        annual_volatility=math.sqrt(variance * TRADING_DAYS),
        max_drawdown=max_dd,
        turnover=turnover,
    )

