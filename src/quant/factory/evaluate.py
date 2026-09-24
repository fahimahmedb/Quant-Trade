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
from typing import Any

from ..dataplane.panel import PricePanel, Window
from .signals import TIME_SERIES_FAMILIES, StrategySpec, should_rebalance, weights_for


#: Family-wise error rate the factory is willing to accept across every
#: expression tested against one dataset version.
FAMILY_WISE_ALPHA = 0.05
TRADING_DAYS = 252


def walk_forward(panel: PricePanel, spec: StrategySpec, window: Window,
                 cost_bps: float) -> list[dict[str, Any]]:
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
    """
    visible = panel.restrict(end=window.end)
    dates = visible.aligned_dates(session_symbols(spec))
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
        target = weights_for(visible, spec, date)
        drift = sum(abs(target.get(symbol, 0.0) - held.get(symbol, 0.0))
                    for symbol in set(target) | set(held))
        sessions_held = None if last_rebalance is None else len(rows) - last_rebalance
        turnover = 0.0
        cost = 0.0
        if target and should_rebalance(sessions_held, drift, spec):
            cost = _rebalance_cost(visible, date, target, held, drift, cost_bps)
            held, turnover, last_rebalance = target, drift, len(rows)
        gross = 0.0
        for symbol, weight in held.items():
            if not (visible.has(entry_date, symbol) and visible.has(exit_date, symbol)):
                continue  # staggered universe only: no executable interval
            # Rolling the contract is paid by longs and shorts alike.
            cost += abs(weight) * (visible.feature(exit_date, symbol, "roll_cost") or 0.0)
            entry = visible.adjusted(entry_date, symbol, "open")
            if entry <= 0:
                continue
            gross += weight * (visible.adjusted(exit_date, symbol, "open") / entry - 1.0)
        rows.append({"signal_date": date, "entry_date": entry_date, "exit_date": exit_date,
                     "gross_return": gross, "cost": cost, "net_return": gross - cost,
                     "turnover": turnover, "positions": len(held), "weights": dict(held)})
    return rows


def _rebalance_cost(panel: PricePanel, date: str, target: dict[str, float],
                    held: dict[str, float], drift: float, cost_bps: float) -> float:
    """Cost of one rebalance as a fraction of capital.

    When the panel carries an instrument's own one-way cost (``cost_bps``
    feature), each traded unit pays the larger of that and the declared
    research cost, so an illiquid contract is never researched at a liquid
    one's price. Without the feature this is exactly ``drift * cost_bps``.
    """
    owned = {symbol: panel.feature(date, symbol, "cost_bps")
             for symbol in set(target) | set(held) if panel.has(date, symbol)}
    if not any(value is not None for value in owned.values()):
        return drift * cost_bps / 10_000.0
    total = 0.0
    for symbol in set(target) | set(held):
        traded = abs(target.get(symbol, 0.0) - held.get(symbol, 0.0))
        total += traded * max(cost_bps, owned.get(symbol) or 0.0)
    return total / 10_000.0


def session_symbols(spec: StrategySpec) -> list[str]:
    """Symbols whose common trading days define the strategy's sessions."""
    return [spec.calendar_symbol] if spec.calendar_symbol else list(spec.universe)


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


#: Directional families may carry equity beta, but not enough to be a disguised
#: equity index position.
TIME_SERIES_MAX_EQUITY_BETA = 0.5


def _sharpe(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    deviation = statistics.stdev(values)
    return statistics.fmean(values) / deviation * math.sqrt(TRADING_DAYS) if deviation else 0.0


def _alpha_t(strategy: list[dict[str, Any]], baseline: list[dict[str, Any]]) -> float:
    """t-statistic of the intercept of strategy on baseline daily net returns."""
    by_date = {row["signal_date"]: row["net_return"] for row in baseline}
    pairs = [(row["net_return"], by_date[row["signal_date"]])
             for row in strategy if row["signal_date"] in by_date]
    n = len(pairs)
    if n < 30:
        return 0.0
    ys, xs = [p[0] for p in pairs], [p[1] for p in pairs]
    mean_x, mean_y = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mean_x) ** 2 for x in xs)
    beta = sum((x - mean_x) * (y - mean_y) for x, y in pairs) / sxx if sxx else 0.0
    alpha = mean_y - beta * mean_x
    residual = [y - alpha - beta * x for y, x in pairs]
    sigma2 = sum(value * value for value in residual) / (n - 2)
    se = math.sqrt(sigma2 * (1.0 / n + (mean_x ** 2 / sxx if sxx else 0.0)))
    return alpha / se if se else 0.0


#: Timing skill must show up as alpha over the passive baseline, not merely as
#: a higher point-estimate Sharpe (red-team finding: a weak baseline made the
#: point comparison pass trivially).
BASELINE_ALPHA_T = 2.0


def falsify(rows: list[dict[str, Any]], summary: dict[str, Any], panel: PricePanel,
            benchmark: str, spec: StrategySpec, trials: int,
            stress_multiple: float = 2.0,
            baseline_rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Try to kill the result. ``passed`` means every declared attempt failed.

    Relative-value families must be market-neutral. Time-series families are
    directional by construction, so neutrality is the wrong test; instead they
    must beat a long-only risk-parity baseline on the same markets and
    interval (``baseline_rows``, required for them) and keep equity beta below
    ``TIME_SERIES_MAX_EQUITY_BETA``.
    """
    if not rows:
        return {"passed": False, "decision": "REJECT_RESEARCH",
                "tests": {}, "reason": "no observations produced"}
    net = [row["net_return"] for row in rows]
    stressed = [row["gross_return"] - row["cost"] * stress_multiple for row in rows]
    middle = len(rows) // 2
    halves = [compound(net[:middle]), compound(net[middle:])]
    positives = sorted((value for value in net if value > 0), reverse=True)
    total_positive = sum(positives)
    top_five_share = (sum(positives[:5]) / total_positive) if total_positive > 0 else 1.0
    threshold = required_t_statistic(trials)

    time_series = spec.family in TIME_SERIES_FAMILIES
    baseline_sharpe = None
    baseline_alpha_t = None
    if time_series:
        if not baseline_rows:
            raise ValueError("time-series falsification requires baseline rows")
        baseline_sharpe = _sharpe([row["net_return"] for row in baseline_rows])
        baseline_alpha_t = _alpha_t(rows, baseline_rows)
        exposure_tests = {
            "sharpe_exceeds_long_only_risk_parity": _sharpe(net) > baseline_sharpe,
            "alpha_over_long_only_risk_parity_t_above_2": baseline_alpha_t >= BASELINE_ALPHA_T,
            "equity_beta_below_0_5": abs(summary["market_beta"]) < TIME_SERIES_MAX_EQUITY_BETA,
        }
    else:
        exposure_tests = {"market_beta_below_0_15": abs(summary["market_beta"]) < 0.15}
    tests = {
        "net_profitable_after_modeled_costs": summary["net_return"] > 0,
        f"still_profitable_at_{stress_multiple:g}x_costs": compound(stressed) > 0,
        "profitable_in_both_subperiods": min(halves) > 0,
        **exposure_tests,
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
        "strategy_sharpe": _sharpe(net),
        "baseline_sharpe": baseline_sharpe,
        "baseline_alpha_t": baseline_alpha_t if time_series else None,
        "beta_attribution": {
            "market_beta": summary["market_beta"],
            "benchmark": benchmark,
            "benchmark_return_same_window": summary["market_return_same_window"],
            "return_explained_by_beta": summary["beta_explained_return"],
            "residual_return": summary["net_return"] - summary["beta_explained_return"]},
    }
