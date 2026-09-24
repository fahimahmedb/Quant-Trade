"""Declared research lanes.

Every expression a lane will try is declared here *before* the data is touched,
and the full grid is counted toward the multiple-testing budget. A lane that
quietly widened its search after seeing results would be buying significance,
which is the failure mode ``QUANT_NORTH_STAR.md`` section 7 names.
"""

from __future__ import annotations

from typing import Any

from .signals import BASELINE_FAMILY, TREND_FAMILY, StrategySpec


#: Point-in-time partition of the panel. SHADOW is reserved for the Capital
#: Desk and is never visible to research, so desk results are genuinely out of
#: sample with respect to every research decision.
WINDOWS = {"DISCOVERY": 0.55, "VALIDATION": 0.30, "SHADOW": 0.15}

BENCHMARK = "SPY"
COST_BPS = 5.0


def _grid(universe: list[str], dataset_id: str, lookbacks: tuple[int, ...],
          holdings: tuple[int, ...], band: float, thresholds: tuple[float, ...]
          ) -> list[StrategySpec]:
    return [StrategySpec(family="cross_sectional", universe=universe, lookback_days=lookback,
                         direction=direction, min_abs_score=threshold, holding_days=holding,
                         no_trade_band=band, dataset_id=dataset_id)
            for lookback in lookbacks for holding in holdings
            for direction in (-1, 1) for threshold in thresholds]


#: Dataset served by the futures lanes (kept literal to avoid a Data-Plane import).
FUTURES_DATASET = "futures_excess_return_daily"
FUTURES_BENCHMARK = "SP500"
#: One-way research cost for liquid futures, per unit of notional traded. The
#: futures desk execution model lands under it (see ``profiles``); roll costs
#: are already charged inside the excess-return index.
FUTURES_COST_BPS = 4.0
#: Expressions evaluated on this same data outside this registry: the
#: exploratory lab (research/deep_research_2026-09-24: 5) plus the first,
#: superseded run of this lane before the red-team fixes (3). Charged to the
#: multiple-testing budget so earlier looks are not laundered into "3 trials".
FUTURES_PRIOR_LAB_TRIALS = 5
FUTURES_PRIOR_TRIALS = FUTURES_PRIOR_LAB_TRIALS + 3
#: Every session of the committed futures history was visible to the lab
#: (red-team finding), so no historical window is pristine out-of-sample. The
#: lifecycle may only act on shadow evidence dated after this.
FUTURES_PRISTINE_AFTER = "2024-03-28"


def _ts_spec(universe: list[str], dataset_id: str, trend: float, carry: float,
             family: str = TREND_FAMILY, calendar_symbol: str = "",
             max_cost_sharpe: float = 0.0) -> StrategySpec:
    return StrategySpec(family=family, universe=universe, lookback_days=256, direction=1,
                        min_abs_score=0.0, max_weight=1.0, gross_exposure=0.0,
                        holding_days=5, no_trade_band=0.10, dataset_id=dataset_id,
                        vol_target=0.15, trend_weight=trend, carry_weight=carry,
                        diversification_multiplier=2.0, forecast_cap=2.0,
                        calendar_symbol=calendar_symbol, max_cost_sharpe=max_cost_sharpe)


def baseline_spec(spec: StrategySpec) -> StrategySpec:
    """Long-only risk parity with the same universe, sizing and rebalance rule.

    A time-series strategy that cannot beat simply holding every market at
    equal risk has not demonstrated timing skill, only exposure to the drift of
    the asset classes it trades (for example the 2002-2020 bond rally).
    """
    return _ts_spec(spec.universe, spec.dataset_id, 0.0, 0.0, family=BASELINE_FAMILY,
                    calendar_symbol=spec.calendar_symbol,
                    max_cost_sharpe=spec.max_cost_sharpe)


def futures_lane_definitions(universe: list[str], dataset_id: str) -> dict[str, dict[str, Any]]:
    return {
        "ts_trend_carry_futures": {
            "lane": "time_series_trend_carry",
            "priority": 40.0,
            "question": "Does a volatility-targeted trend and carry forecast across a "
                        "diversified futures panel earn a positive excess return, net of "
                        "costs, beyond passive risk-parity exposure to the same markets?",
            "mechanism": "Trend: slow diffusion of information and hedging/risk-transfer "
                         "flows that are price-insensitive; documented in every decade "
                         "since the 1880s. Carry: compensation for providing insurance / "
                         "inventory financing, visible in the futures curve. Breadth across "
                         "~30 weakly correlated markets is what makes either detectable.",
            "falsification": "Reject unless profitable out of sample after modelled costs "
                             "and at double those costs, profitable in both subperiods, "
                             "better risk-adjusted than long-only risk parity on the same "
                             "markets, equity beta below 0.5, unconcentrated, and "
                             "significant against a multiple-testing threshold that "
                             "includes the exploratory lab trials.",
            # Pre-registered: three expressions only, no parameter grid.
            "grid": [_ts_spec(universe, dataset_id, 1.0, 0.0),
                     _ts_spec(universe, dataset_id, 0.0, 1.0),
                     _ts_spec(universe, dataset_id, 0.5, 0.5)],
            "prior_trials": FUTURES_PRIOR_TRIALS,
            "pristine_after": FUTURES_PRISTINE_AFTER,
            "benchmark": FUTURES_BENCHMARK,
            "cost_bps": FUTURES_COST_BPS,
            "market": "diversified futures (31 contracts, 6 asset classes)",
        },
    }


#: Broad, staggered-entry futures panel (second, separately declared dataset).
FUTURES_BROAD_DATASET = "futures_excess_return_daily_broad"
#: Charged on top of the broad lane's own grid: the 5 lab expressions plus the
#: 3 expressions of the narrow lane, whose rejection motivated this one.
#: Charged once for the broad dataset: lab 5, narrow lane 3 (plus its
#: superseded run 3), the first broad run at uniform 4bp costs 3 (the audit
#: found 52 of 144 contracts cost more) and the per-instrument-cost run 3
#: (superseded by the red-team roll-cost fix).
FUTURES_BROAD_PRIOR_TRIALS = FUTURES_PRIOR_LAB_TRIALS + 3 + 3 + 3 + 3
#: Carver (2015): never spend more than about a third of a realistic Sharpe
#: (~0.4) on costs.
SPEED_LIMIT_SHARPE = 0.13


def futures_broad_lane_definitions(universe: list[str], dataset_id: str
                                   ) -> dict[str, dict[str, Any]]:
    grid = [_ts_spec(universe, dataset_id, t, c, calendar_symbol=FUTURES_BENCHMARK)
            for t, c in ((1.0, 0.0), (0.0, 1.0), (0.5, 0.5))]
    speed_limited = [_ts_spec(universe, dataset_id, t, c, calendar_symbol=FUTURES_BENCHMARK,
                              max_cost_sharpe=SPEED_LIMIT_SHARPE)
                     for t, c in ((1.0, 0.0), (0.0, 1.0), (0.5, 0.5))]
    return {
        # Declared after the cost-corrected broad lane was rejected with costs as
        # the binding constraint. Last expression family allowed on this dataset:
        # its validation window is exhausted; only forward sessions can decide.
        "ts_trend_carry_futures_broad_speed_limited": {
            "lane": "time_series_trend_carry",
            "priority": 40.5,   # runs after the lane whose diagnosis motivated it
            "question": "Does the broad trend/carry forecast survive when instruments too "
                        "expensive to trade at its speed are excluded ex ante (annual cost "
                        f"above {SPEED_LIMIT_SHARPE} Sharpe units on that date)?",
            "mechanism": "The broad lane's gross validation return was 157% but costs took "
                         "51%: breadth added expensive contracts faster than it added "
                         "independent edge. A cost-per-risk filter keeps breadth only where "
                         "it is affordable.",
            "falsification": "Identical declared tests. Charged with every earlier "
                             "expression on this data (lab 5, narrow 3, first broad run 3, "
                             "cost-corrected broad lane 3) plus its own 3. No further "
                             "expression may be tested on this dataset's history after "
                             "this one.",
            "grid": speed_limited,
            "prior_trials": FUTURES_BROAD_PRIOR_TRIALS,
            "pristine_after": FUTURES_PRISTINE_AFTER,
            "benchmark": FUTURES_BENCHMARK,
            "cost_bps": FUTURES_COST_BPS,
            "calendar": [FUTURES_BENCHMARK],
            "market": "broad futures, speed-limited (staggered entry, 6 asset classes)",
        },
        "ts_trend_carry_futures_broad": {
            "lane": "time_series_trend_carry",
            "priority": 41.0,
            "question": "Does the same pre-registered trend/carry forecast survive when "
                        "breadth is raised from 31 aligned contracts to every liquid "
                        "contract with its own history (staggered entry, from 1990)?",
            "mechanism": "Fundamental law of active management: information ratio scales "
                         "with the square root of the number of independent bets. The "
                         "narrow lane was rejected with a gross validation Sharpe near "
                         "0.3; breadth, not a new signal, is the variable changed.",
            "falsification": "Identical declared tests to the narrow lane. Declared "
                             "contamination: the exploratory lab evaluated a related "
                             "specification on this data over its full history, and the "
                             "narrow lane's rejection motivated this lane, so both are "
                             "charged to the multiple-testing budget and no window of "
                             "this dataset can be called pristine; only forward shadow "
                             "sessions after 2024-03 would be.",
            "grid": grid,
            "prior_trials": FUTURES_BROAD_PRIOR_TRIALS,
            "pristine_after": FUTURES_PRISTINE_AFTER,
            "benchmark": FUTURES_BENCHMARK,
            "cost_bps": FUTURES_COST_BPS,
            "calendar": [FUTURES_BENCHMARK],
            "market": "broad futures (staggered entry, 6 asset classes)",
        },
    }


def lane_definitions(universe: list[str], dataset_id: str) -> dict[str, dict[str, Any]]:
    if dataset_id == FUTURES_DATASET:
        return futures_lane_definitions(universe, dataset_id)
    if dataset_id == FUTURES_BROAD_DATASET:
        return futures_broad_lane_definitions(universe, dataset_id)
    return {
        "xs_daily_relative_value": {
            "lane": "statistical_arbitrage",
            "priority": 29.0,
            "question": "Do cross-sectional sector dislocations revert or persist over "
                        "one to twenty-one sessions, net of costs?",
            "mechanism": "Sector ETFs share one dominant market factor. Demeaning the "
                         "trailing return isolates the residual, so a dollar-neutral "
                         "spread expresses relative mispricing rather than market "
                         "direction. Liquidity demand may push residuals too far "
                         "(reversal) or information may diffuse slowly (momentum).",
            "falsification": "Reject unless the out-of-sample window is profitable after "
                             "modelled costs and at double those costs, profitable in "
                             "both subperiods, beta-neutral, unconcentrated, and "
                             "significant against a multiple-testing-adjusted threshold.",
            "grid": _grid(universe, dataset_id, (1, 2, 3, 5, 10, 21), (1,), 0.0, (0.5, 1.0)),
        },
        "xs_execution_aware_relative_value": {
            "lane": "statistical_arbitrage",
            "priority": 31.0,
            "question": "If the daily expression is destroyed by turnover, does the same "
                        "residual survive once the holding period and a no-trade band "
                        "cut turnover by an order of magnitude?",
            "mechanism": "Identical residual signal. The change is structural rather "
                         "than a parameter re-roll: the strategy is only allowed to "
                         "trade every N sessions and only when the target has drifted "
                         "past a band, which attacks the diagnosed cost mechanism "
                         "instead of searching for a luckier signal.",
            "falsification": "Same adversarial bar, against a stricter multiple-testing "
                             "threshold because these expressions are additional trials "
                             "on a dataset that has already been searched.",
            "grid": _grid(universe, dataset_id, (21, 42, 63), (5, 21), 0.05, (0.5,)),
        },
    }


#: A lane may promote a successor only when the evidence says the diagnosed
#: mechanism is the one the successor attacks. This is not a fixed pipeline: an
#: expression that failed because the signal itself was absent promotes nothing.
FOLLOWUP = {"xs_daily_relative_value": "xs_execution_aware_relative_value"}
