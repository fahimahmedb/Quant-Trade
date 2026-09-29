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


#: Anytime-valid test by betting (ORDRE 12b). Fixed in code before any data.
#: Fraction of the admissible bet range used: lambda <= AV_BET_CAP / -lower.
AV_BET_CAP = 0.9


def anytime_valid_mean_test(values: list[float], lower: float, upper: float, alpha: float,
                            beta: float, h1_mean: float, max_observations: int, *,
                            groups: list[Any] | None = None) -> dict[str, Any]:
    """Sequential test of a bounded mean by betting (Waudby-Smith & Ramdas 2023).

    ACCEPT_EDGE rejects H0: mean <= 0.   REJECT_EDGE rejects H0': mean >= ``h1_mean``.

    Two wealth processes are walked in order, one bet per ROUND (a round is one
    value, or one block of consecutive values sharing a ``groups`` key):
        K_A = prod(1 + lam_r * xbar_r)              (bets against H0)
        K_R = prod(1 + gam_r * (h1_mean - xbar_r))  (bets against H0')
    where xbar_r is the round mean. ACCEPT_EDGE at the first round where
    K_A >= 1/alpha, REJECT_EDGE where K_R >= 1/beta (REJECT wins a tie: the
    costly error is a false pass), INCONCLUSIVE once ``max_observations``
    values are consumed, CONTINUE before that. A decision is final: later values
    are never read, so appending events cannot change it.

    Guarantee (Ville's inequality; no independence, no known variance, no
    minimum sample): if every value lies in [lower, upper] and, under H0, each
    value has conditional expectation <= 0 given all values of EARLIER rounds,
    then K_A is a nonnegative supermartingale over rounds and
    P(ACCEPT_EDGE) <= alpha at any data-dependent stopping time; symmetrically
    P(REJECT_EDGE) <= beta when every conditional mean is >= ``h1_mean``.
    Dependence INSIDE a round is unrestricted. Without ``groups`` each value is
    its own round, so the condition must hold given every earlier value: a
    shock common to several matches of one evening breaks it (simulated
    rho = 0.3: false ACCEPT ~9% at alpha 2.5%). Pass the evening/batch key as
    ``groups`` whenever values can share such a shock. No bet on dependent
    values can do better: any valid multiplier of a round is bounded by one
    bet on its mean (all values at ``lower`` together is a feasible H0 law).

    Bet: truncated aGRAPA (approximate growth-rate adaptive, the paper's
    plug-in Kelly), predictable from earlier rounds only:
        lam = clip(m / (v + m^2), 0, AV_BET_CAP / -lower),  m = running mean
        gam = clip(g / (v + g^2), 0, AV_BET_CAP / (upper - h1_mean)),  g = h1 - m
    with one prior pseudo-round at h1/2 (half-way between the hypotheses) and
    variance ((upper - lower) / 2)^2, the paper's regularisation. Why: for H-001
    the Kelly bet (h1/sigma^2 ~ 1.9) lies beyond the admissible range, so the
    cap binds under H1 and a high cap buys power; 0.9 rather than 1 keeps 10%
    of wealth if a value hits ``lower`` instead of killing the test forever.
    Unlike a constant bet at the cap, aGRAPA shrinks its stake when the
    variance is larger than expected (sigma 0.1: 76% vs 64% power at 6000).

    Validation (tests/test_anytime_valid_sequential.py, seeded, alpha 0.025,
    20 000 H0 paths per scenario): false ACCEPT per evening 0.0000 in all five
    scenarios (horizon 2000 and 12 000); per match <= 0.0052 except common
    evening shocks (0.083; old t-SPRT 0.195). Under H1 (0.00475, sigma 0.05)
    per match: power 0.99, median 1254 matches (old t-SPRT 648); per evening
    with shocks: power 1.00 by 16 000, median 8159 matches, 82% by 10 000. Pure: the same values
    and groups always give the same verdict (crash-and-replay safe).
    """
    if not 0 < alpha < 1 or not 0 < beta < 1:
        raise ValueError("alpha and beta must be in (0, 1)")
    if not lower < 0 < h1_mean < upper:
        raise ValueError("need lower < 0 < h1_mean < upper")
    if isinstance(max_observations, bool) or not isinstance(max_observations, int) \
            or max_observations < 1:
        raise ValueError("max_observations must be a positive integer")
    for value in values:
        if not (math.isfinite(value) and lower <= value <= upper):
            raise ValueError(f"value {value!r} outside [{lower}, {upper}]")
    if groups is not None:
        if len(groups) != len(values):
            raise ValueError("groups must have one key per value")
        closed: set[Any] = set()
        for previous, key in zip(groups, groups[1:]):
            if key != previous:
                closed.add(previous)
                if key in closed:
                    raise ValueError(f"group {key!r} is not contiguous")
    accept_threshold = math.log(1.0 / alpha)
    reject_threshold = math.log(1.0 / beta)
    lam_cap = AV_BET_CAP / -lower
    gam_cap = AV_BET_CAP / (upper - h1_mean)
    prior_mean = h1_mean / 2.0
    prior_var = ((upper - lower) / 2.0) ** 2
    horizon = min(len(values), max_observations)
    result: dict[str, Any] = {"method": "betting_agrapa", "lower": lower, "upper": upper,
                              "alpha": alpha, "beta": beta, "h1_mean": h1_mean,
                              "bet_cap": AV_BET_CAP, "max_observations": max_observations,
                              "grouped": groups is not None,
                              "accept_log_threshold": accept_threshold,
                              "reject_log_threshold": reject_threshold,
                              "observations": 0, "rounds": 0, "log_wealth_accept": 0.0,
                              "log_wealth_reject": 0.0, "decision": "CONTINUE"}
    log_a = log_r = 0.0
    rounds = 0
    total = total_sq = 0.0          # of round means
    start = 0
    while start < horizon:
        end = start + 1
        if groups is not None:
            while end < horizon and groups[end] == groups[start]:
                end += 1
        mean = (prior_mean + total) / (rounds + 1)
        spread = total_sq - total * total / rounds if rounds else 0.0
        var = (prior_var + max(spread, 0.0)) / (rounds + 1)
        lam = min(max(mean / (var + mean * mean), 0.0), lam_cap)
        gap = h1_mean - mean
        gam = min(max(gap / (var + gap * gap), 0.0), gam_cap)
        xbar = math.fsum(values[start:end]) / (end - start)
        log_a += math.log1p(lam * xbar)
        log_r += math.log1p(gam * (h1_mean - xbar))
        rounds += 1
        total += xbar
        total_sq += xbar * xbar
        start = end
        result.update(observations=end, rounds=rounds, log_wealth_accept=log_a,
                      log_wealth_reject=log_r)
        if log_r >= reject_threshold:
            result["decision"] = "REJECT_EDGE"
            return result
        if log_a >= accept_threshold:
            result["decision"] = "ACCEPT_EDGE"
            return result
    if horizon >= max_observations:
        result["decision"] = "INCONCLUSIVE"
    return result
