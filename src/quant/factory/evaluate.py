"""Walk-forward evaluation and adversarial falsification.

``QUANT_NORTH_STAR.md`` section 7 lists what must be ruled out before a
profitable curve may be called edge: passive beta, look-ahead, survivorship,
multiple-testing luck, unrealistic costs, stale information and concentration.
Every check here exists to answer one of those, and the checks are declared
before the test runs.
"""

from __future__ import annotations

import math
import statistics
from statistics import NormalDist
from typing import Any, Callable

from ..dataplane.panel import PricePanel, Window
from .signals import StrategySpec, should_rebalance, weights_for


#: Family-wise error rate the factory is willing to accept across every
#: expression tested against one dataset version.
FAMILY_WISE_ALPHA = 0.05
TRADING_DAYS = 252


def walk_forward(panel: PricePanel, spec: StrategySpec, window: Window,
                 cost_bps: float,
                 weights_fn: Callable[[PricePanel, StrategySpec, str],
                                      dict[str, float]] = weights_for
                 ) -> list[dict[str, Any]]:
    """Run the strategy session by session inside ``window``.

    One causal timeline, identical to the desk's:

    ``information through close(t) -> decision after close(t) ->
    entry at open(t+1) -> exit at open(t+2)``

    The return interval therefore *starts* at the first moment an order could
    have executed. Measuring from close(t) instead would credit the overnight
    gap between the decision and the earliest possible fill, which the desk can
    never capture, and would make every published metric describe a strategy
    the system cannot run.

    The panel is truncated at the window end before anything is computed, so a
    future bar is not merely unused, it is unreachable.

    ``weights_fn`` lets a second signal family run through this same timeline and
    the same turnover accounting instead of getting its own loop. Reimplementing
    the rebalance and cost path per family is how two families end up being
    compared on two different sets of rules.
    """
    visible = panel.restrict(end=window.end)
    dates = visible.aligned_dates(spec.universe)
    rows: list[dict[str, Any]] = []
    held: dict[str, float] = {}
    last_rebalance: int | None = None
    for index in range(len(dates) - 2):
        date, entry_date, exit_date = dates[index], dates[index + 1], dates[index + 2]
        # A row belongs to a research window only when the complete executable
        # interval belongs to it.  Merely containing the signal date lets the
        # final signal borrow entry/exit prices from the next (holdout) window.
        if not (window.contains(date) and window.contains(entry_date)
                and window.contains(exit_date)):
            continue
        target = weights_fn(visible, spec, date)
        drift = sum(abs(target.get(symbol, 0.0) - held.get(symbol, 0.0))
                    for symbol in set(target) | set(held))
        sessions_held = None if last_rebalance is None else len(rows) - last_rebalance
        turnover = 0.0
        if target and should_rebalance(sessions_held, drift, spec):
            held, turnover, last_rebalance = target, drift, len(rows)
        gross = 0.0
        for symbol, weight in held.items():
            entry = visible.adjusted(entry_date, symbol, "open")
            if entry <= 0:
                continue
            gross += weight * (visible.adjusted(exit_date, symbol, "open") / entry - 1.0)
        cost = turnover * cost_bps / 10_000.0
        rows.append({"signal_date": date, "entry_date": entry_date, "exit_date": exit_date,
                     "gross_return": gross, "cost": cost, "net_return": gross - cost,
                     "turnover": turnover, "positions": len(held), "weights": dict(held)})
    return rows


def _max_drawdown(returns: list[float]) -> float:
    equity, peak, worst = 1.0, 1.0, 0.0
    for value in returns:
        equity *= 1.0 + value
        peak = max(peak, equity)
        worst = min(worst, equity / peak - 1.0)
    return worst


def _beta(strategy: list[float], market: list[float]) -> float:
    if len(strategy) < 3:
        return 0.0
    variance = statistics.variance(market)
    if variance <= 0:
        return 0.0
    mean_s, mean_m = statistics.fmean(strategy), statistics.fmean(market)
    covariance = sum((a - mean_s) * (b - mean_m) for a, b in zip(strategy, market)) / (
        len(strategy) - 1)
    return covariance / variance


def compound(returns: list[float]) -> float:
    total = 1.0
    for value in returns:
        total *= 1.0 + value
    return total - 1.0


def summarize(rows: list[dict[str, Any]], panel: PricePanel, benchmark: str,
              cost_bps: float) -> dict[str, Any]:
    """Descriptive statistics, including the market attribution the North Star demands."""
    if not rows:
        return {"observations": 0, "net_return": 0.0, "empty": True}
    net = [row["net_return"] for row in rows]
    gross = [row["gross_return"] for row in rows]
    # The benchmark is measured over the same executable interval, or the beta
    # attribution would compare two different clocks.
    market = [panel.adjusted(row["exit_date"], benchmark, "open")
              / panel.adjusted(row["entry_date"], benchmark, "open") - 1.0 for row in rows]
    mean, deviation = statistics.fmean(net), (statistics.stdev(net) if len(net) > 1 else 0.0)
    volatility = deviation * math.sqrt(TRADING_DAYS)
    active = sum(1 for row in rows if row["positions"] > 0)
    beta = _beta(net, market)
    return {
        "observations": len(rows), "active_observations": active,
        "first_signal_date": rows[0]["signal_date"],
        "first_entry_date": rows[0]["entry_date"], "last_exit_date": rows[-1]["exit_date"],
        "timeline": "signal at close(t); entry at open(t+1); exit at open(t+2)",
        "cost_bps": cost_bps,
        "gross_return": compound(gross), "net_return": compound(net),
        "market_return_same_window": compound(market),
        "total_costs": sum(row["cost"] for row in rows),
        "annual_mean_return": mean * TRADING_DAYS, "annual_volatility": volatility,
        "sharpe_zero_rate": (mean * TRADING_DAYS / volatility) if volatility else 0.0,
        "market_beta": beta,
        "beta_explained_return": beta * compound(market),
        "max_drawdown": _max_drawdown(net),
        "hit_rate": sum(1 for value in net if value > 0) / len(net),
        "annual_turnover": sum(row["turnover"] for row in rows) / len(rows) * TRADING_DAYS,
        "t_statistic": (mean / (deviation / math.sqrt(len(net)))) if deviation else 0.0,
    }


def required_t_statistic(trials: int) -> float:
    """Bonferroni-adjusted two-sided threshold for the number of expressions tried.

    Testing many expressions against one dataset makes an impressive-looking
    winner cheap. The threshold rises with the trial count so the factory
    cannot buy significance by searching harder.
    """
    trials = max(1, trials)
    return NormalDist().inv_cdf(1.0 - FAMILY_WISE_ALPHA / (2.0 * trials))


def falsify(rows: list[dict[str, Any]], summary: dict[str, Any], panel: PricePanel,
            benchmark: str, spec: StrategySpec, trials: int,
            stress_multiple: float = 2.0) -> dict[str, Any]:
    """Try to kill the result. ``passed`` means every declared attempt failed."""
    if not rows:
        return {"passed": False, "decision": "REJECT_RESEARCH",
                "tests": {}, "reason": "no observations produced"}
    net = [row["net_return"] for row in rows]
    stressed = [row["gross_return"] - row["turnover"] * summary["cost_bps"]
                * stress_multiple / 10_000.0 for row in rows]
    middle = len(rows) // 2
    halves = [compound(net[:middle]), compound(net[middle:])]
    positives = sorted((value for value in net if value > 0), reverse=True)
    total_positive = sum(positives)
    top_five_share = (sum(positives[:5]) / total_positive) if total_positive > 0 else 1.0
    threshold = required_t_statistic(trials)

    tests = {
        "net_profitable_after_modeled_costs": summary["net_return"] > 0,
        f"still_profitable_at_{stress_multiple:g}x_costs": compound(stressed) > 0,
        "profitable_in_both_subperiods": min(halves) > 0,
        "market_beta_below_0_15": abs(summary["market_beta"]) < 0.15,
        "top_5_days_below_half_of_gains": top_five_share < 0.5,
        "t_statistic_survives_multiple_testing": summary["t_statistic"] >= threshold,
        "at_least_100_active_observations": summary["active_observations"] >= 100,
    }
    passed = all(tests.values())
    return {
        "passed": passed,
        "decision": "VALIDATED" if passed else "REJECT_RESEARCH",
        "tests": tests,
        "failed_tests": sorted(name for name, ok in tests.items() if not ok),
        "subperiod_returns": halves,
        "net_return_at_stress_costs": compound(stressed),
        "stress_cost_bps": summary["cost_bps"] * stress_multiple,
        "top_5_day_share_of_gains": top_five_share,
        "t_statistic": summary["t_statistic"],
        "required_t_statistic": threshold,
        "expressions_tested_on_dataset": trials,
        "beta_attribution": {
            "market_beta": summary["market_beta"],
            "benchmark": benchmark,
            "benchmark_return_same_window": summary["market_return_same_window"],
            "return_explained_by_beta": summary["beta_explained_return"],
            "residual_return": summary["net_return"] - summary["beta_explained_return"]},
    }
