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
