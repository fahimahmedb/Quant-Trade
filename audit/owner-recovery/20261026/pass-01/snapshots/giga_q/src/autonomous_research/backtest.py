"""Dependency-free causal walk-forward test and adversarial diagnostics."""

from __future__ import annotations

import math
import statistics

from .scanner import log_returns


def reversal_backtest(close: list[float], lookback: int, test_start: int,
                      cost_bps: float = 5.0) -> list[dict]:
    returns = [0.0] + log_returns(close)
    raw, prior_position = [0.0] * len(close), 0.0
    out = []
    for t in range(lookback, len(close)):
        trailing = sum(returns[t - lookback + 1:t + 1])
        history = [sum(returns[j - lookback + 1:j + 1]) for j in range(lookback, t)]
        if len(history) >= 60:
            scale = statistics.stdev(history)
            raw[t] = -1.0 if trailing > scale else (1.0 if trailing < -scale else 0.0)
        position = raw[t - 1] if t else 0.0
        turnover = abs(position - prior_position)
        if t >= test_start:
            out.append({"index": t, "return": returns[t], "position": position,
                        "turnover": turnover,
                        "strategy_return": position * returns[t] - turnover * cost_bps / 10000})
        prior_position = position
    return out


def metrics(rows: list[dict]) -> dict:
    pnl = [row["strategy_return"] for row in rows]
    market = [row["return"] for row in rows]
    mp, mm = statistics.mean(pnl), statistics.mean(market)
    cov = sum((p - mp) * (m - mm) for p, m in zip(pnl, market)) / (len(rows) - 1)
    var_market = statistics.variance(market)
    vol = statistics.stdev(pnl) * math.sqrt(252)
    return {"observations": len(rows), "active_observations": sum(r["position"] != 0 for r in rows),
            "annual_mean_return": mp * 252, "annual_volatility": vol,
            "sharpe_zero_rate": mp * 252 / vol if vol else 0.0,
            "market_beta": cov / var_market if var_market else 0.0,
            "turnover": sum(r["turnover"] for r in rows), "net_return": sum(pnl)}


def validate(rows: list[dict], result: dict) -> dict:
    pnl10 = [r["position"] * r["return"] - r["turnover"] * 0.001 for r in rows]
    middle = len(rows) // 2
    halves = [sum(r["strategy_return"] for r in rows[:middle]),
              sum(r["strategy_return"] for r in rows[middle:])]
    top_share = sum(sorted((r["strategy_return"] for r in rows), reverse=True)[:5]) / sum(
        r["strategy_return"] for r in rows) if result["net_return"] > 0 else None
    checks = {"profitable_at_10_bps": sum(pnl10) > 0, "profitable_in_both_halves": min(halves) > 0,
              "absolute_beta_below_0_25": abs(result["market_beta"]) < 0.25,
              "top_5_share_below_0_5": top_share is None or top_share < 0.5}
    passed = result["net_return"] > 0 and all(checks.values())
    return {"passed": passed, "decision": "VALIDATED_FOR_PAPER" if passed else "REJECT_RESEARCH",
            "net_return_at_10_bps": sum(pnl10), "oos_half_returns": halves,
            "top_5_profit_share": top_share, "tests": checks}
