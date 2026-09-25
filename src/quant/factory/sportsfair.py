"""Fair value from a sharp bookmaker and closing-line value (CLV).

The best-supported betting edge (lab: 69k football matches, t~4) is not a
model: it is the sharp book's price, with its margin removed, used as fair
value against a softer or slower venue. The margin-removal ("devig") method
decides the sign of the result: multiplicative devig ignores the
favourite-longshot bias and manufactures fake longshot edges, so the default
here is the power method, with Shin's model as the alternative.

CLV (price taken vs. fair price at the close) predicted realised ROI about 1:1
in the lab and becomes informative in weeks, long before P&L; it is the metric
a sports/prediction-market sleeve is promoted or killed on.
"""

from __future__ import annotations

import math
from typing import Callable


def _implied(prices: dict[str, float]) -> dict[str, float]:
    if not prices or any(price <= 1.0 for price in prices.values()):
        raise ValueError("decimal prices must all exceed 1.0")
    return {name: 1.0 / price for name, price in prices.items()}


def devig_multiplicative(prices: dict[str, float]) -> dict[str, float]:
    implied = _implied(prices)
    total = sum(implied.values())
    return {name: value / total for name, value in implied.items()}


def devig_power(prices: dict[str, float]) -> dict[str, float]:
    """p_i = (1/o_i)^k with k chosen so the probabilities sum to one."""
    implied = _implied(prices)
    low, high = 0.5, 3.0
    for _ in range(100):
        k = (low + high) / 2.0
        if sum(value ** k for value in implied.values()) > 1.0:
            low = k
        else:
            high = k
    k = (low + high) / 2.0
    return {name: value ** k for name, value in implied.items()}


def devig_shin(prices: dict[str, float]) -> dict[str, float]:
    """Shin (1993): margin attributed to a share z of insider money."""
    implied = _implied(prices)
    booksum = sum(implied.values())

    def probabilities(z: float) -> dict[str, float]:
        return {name: (math.sqrt(z * z + 4 * (1 - z) * value * value / booksum) - z)
                / (2 * (1 - z)) for name, value in implied.items()}

    low, high = 0.0, 0.5
    for _ in range(100):
        z = (low + high) / 2.0
        if sum(probabilities(z).values()) > 1.0:
            low = z
        else:
            high = z
    return probabilities((low + high) / 2.0)


DEVIG: dict[str, Callable[[dict[str, float]], dict[str, float]]] = {
    "power": devig_power, "shin": devig_shin, "multiplicative": devig_multiplicative}


def expected_value(price: float, fair_probability: float) -> float:
    """Expected return per unit staked at decimal ``price``."""
    return price * fair_probability - 1.0


def closing_line_value(price_taken: float, closing_prices: dict[str, float], outcome: str,
                       method: str = "power") -> float:
    """CLV of a bet: price taken against the devigged closing fair price."""
    fair = DEVIG[method](closing_prices)[outcome]
    return expected_value(price_taken, fair)


def binary_contract_edge(ask: float, fair_probability: float,
                         fee: Callable[[float], float] | None = None) -> float:
    """Expected return per dollar of buying a $1 binary contract at ``ask``.

    ``fee(price)`` is the per-contract taker fee (Kalshi: 0.07*p*(1-p);
    Polymarket: rate*p*(1-p) by category).
    """
    cost = ask + (fee(ask) if fee else 0.0)
    return (fair_probability - cost) / cost
