"""Sequential evidence on live shadow returns (t-SPRT).

A shadow track record cannot *confirm* a modest Sharpe quickly (about
(2/SR)^2 years), but a sequential probability ratio test can stop early in
either direction and tells the lifecycle when the evidence is decisive.

H0: annual Sharpe = 0        H1: annual Sharpe = ``alternative_sharpe``

The daily return scale is unknown, so returns are standardised by the running
sample deviation (a plug-in t-SPRT). The known-sigma version inflates false
acceptance to ~17-20% when volatility is misjudged by 1.5x (lab adversarial
review), which is why sigma is estimated and why no decision is allowed before
``MIN_OBSERVATIONS`` returns.

The function is pure: the same return history always yields the same verdict,
so a crash-and-replay cannot produce a different lifecycle decision.
"""

from __future__ import annotations

import math
import statistics
from typing import Any

MIN_OBSERVATIONS = 60
TRADING_DAYS = 252
ALPHA = 0.05   # P(accept H1 | H0 true)
BETA = 0.05    # P(accept H0 | H1 true)
#: Backtest Sharpe is shrunk before it becomes the live alternative
#: (post-publication / out-of-sample decay is ~1/3 to 1/2).
SHRINKAGE = 0.5
MIN_ALTERNATIVE, MAX_ALTERNATIVE = 0.5, 2.0


def alternative_sharpe(validated_sharpe: float | None) -> float:
    base = (validated_sharpe or 0.0) * SHRINKAGE
    return max(MIN_ALTERNATIVE, min(MAX_ALTERNATIVE, base))


def sequential_test(returns: list[float], sharpe_alternative: float,
                    alpha: float = ALPHA, beta: float = BETA) -> dict[str, Any]:
    upper = math.log((1.0 - beta) / alpha)
    lower = math.log(beta / (1.0 - alpha))
    n = len(returns)
    result: dict[str, Any] = {"observations": n, "alternative_sharpe": sharpe_alternative,
                              "upper_bound": upper, "lower_bound": lower,
                              "log_likelihood_ratio": 0.0, "decision": "CONTINUE"}
    if n < MIN_OBSERVATIONS:
        result["reason"] = f"fewer than {MIN_OBSERVATIONS} live returns"
        return result
    deviation = statistics.pstdev(returns)
    if deviation <= 0:
        result["reason"] = "no return variation"
        return result
    mu = sharpe_alternative / math.sqrt(TRADING_DAYS)
    mean_z = statistics.fmean(returns) / deviation
    llr = n * (mu * mean_z - mu * mu / 2.0)
    result["log_likelihood_ratio"] = llr
    # Expected sessions for the LLR to reach the accept bound if H1 is true
    # (drift mu^2/2 per session). At a Sharpe of 0.5 this is decades: the test
    # is then monitoring, not a fast kill switch, and is reported as such.
    result["expected_sessions_to_accept_if_true"] = upper / (mu * mu / 2.0)
    result["realised_sharpe"] = mean_z * math.sqrt(TRADING_DAYS)
    if llr >= upper:
        result["decision"] = "ACCEPT_EDGE"
    elif llr <= lower:
        result["decision"] = "REJECT_EDGE"
    return result


#: Event-indexed variant (SHADOW_DIRECT, TWO_SPEED_RESEARCH_PROPOSAL §4).
#: Fewest observations before any decision: the plug-in sigma is unreliable
#: on a handful of events and would inflate false acceptance.
EVENT_MIN_OBSERVATIONS = 30


def event_sequential_test(values: list[float], h1_effect_over_sigma: float, alpha: float,
                          beta: float = BETA, max_observations: int | None = None,
                          min_observations: int = EVENT_MIN_OBSERVATIONS,
                          sigma_floor: float | None = None) -> dict[str, Any]:
    """t-SPRT on one statistic per independent event, walked in event order.

    H0: mean = 0          H1: mean = ``h1_effect_over_sigma`` x sigma
    H1 is declared per observation (effect / sigma of the declared statistic),
    with no annualisation and no clamp, unlike ``alternative_sharpe``. Sigma is
    the running sample deviation (plug-in). The walk stops at the FIRST bound
    crossing after ``min_observations`` events (a monitored test decides once);
    reaching ``max_observations`` without a crossing is INCONCLUSIVE and later
    events are ignored. Pure: the same history always gives the same verdict.

    ``sigma_floor`` is the statistic's sigma DECLARED in the power calculation;
    the plug-in sigma never goes below it. Without it, rare-loss statistics
    (many small wins, few large losses: favourites, systematic NO) collapse the
    early sigma before the first loss appears and falsely accept ~12% of the
    time at alpha 2.5% (adversarial test). SHADOW_DIRECT entries must pass it,
    and it must be conservative: an underestimated floor (half the true sigma)
    brings the inflation back, so calibration may RAISE it, never lower it. For
    a binary payoff bought at price p the structural value is
    ``binary_payoff_sigma(p)``.
    """
    if h1_effect_over_sigma <= 0 or not 0 < alpha < 1 or not 0 < beta < 1:
        raise ValueError("h1 must be positive and alpha, beta in (0, 1)")
    upper = math.log((1.0 - beta) / alpha)
    lower = math.log(beta / (1.0 - alpha))
    d = h1_effect_over_sigma
    horizon = len(values) if max_observations is None else min(len(values), max_observations)
    result: dict[str, Any] = {"h1_effect_over_sigma": d, "alpha": alpha, "beta": beta,
                              "sigma_floor": sigma_floor,
                              "upper_bound": upper, "lower_bound": lower,
                              "max_observations": max_observations,
                              "expected_events_to_accept_if_true": upper / (d * d / 2.0),
                              "observations": 0, "log_likelihood_ratio": 0.0,
                              "decision": "CONTINUE"}
    total = total_sq = 0.0
    for n in range(1, horizon + 1):
        value = values[n - 1]
        total += value
        total_sq += value * value
        if n < min_observations:
            continue
        mean = total / n
        variance = max(total_sq / n - mean * mean, 0.0)
        if sigma_floor:
            variance = max(variance, sigma_floor * sigma_floor)
        if variance <= 0:
            continue
        llr = n * (d * mean / math.sqrt(variance) - d * d / 2.0)
        result.update(observations=n, log_likelihood_ratio=llr)
        if llr >= upper:
            result["decision"] = "ACCEPT_EDGE"
            return result
        if llr <= lower:
            result["decision"] = "REJECT_EDGE"
            return result
    result["observations"] = horizon
    if max_observations is not None and horizon >= max_observations:
        result["decision"] = "INCONCLUSIVE"
    return result


def shadow_direct_alpha(k: int) -> float:
    """Forward alpha of the k-th SHADOW_DIRECT entry: 0.05/(k(k+1)), sum < 0.05."""
    if k < 1:
        raise ValueError("k starts at 1 and is never decremented")
    return 0.05 / (k * (k + 1))


def binary_payoff_sigma(price: float) -> float:
    """Per-contract return sigma of a binary bought at ``price`` if fairly priced."""
    if not 0 < price < 1:
        raise ValueError("price must be in (0, 1)")
    return math.sqrt(price * (1.0 - price)) / price
