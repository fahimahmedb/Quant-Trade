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
#: Expressions of this lane evaluated on this same data *before* the lane was
#: declared (exploratory lab, research/deep_research_2026-09-24). They are
#: charged to the multiple-testing budget so the lab's look at the data is not
#: laundered into a "3-trial" result.
FUTURES_PRIOR_LAB_TRIALS = 5


def _ts_spec(universe: list[str], dataset_id: str, trend: float, carry: float,
             family: str = TREND_FAMILY) -> StrategySpec:
    return StrategySpec(family=family, universe=universe, lookback_days=256, direction=1,
                        min_abs_score=0.0, max_weight=1.0, gross_exposure=0.0,
                        holding_days=5, no_trade_band=0.10, dataset_id=dataset_id,
                        vol_target=0.15, trend_weight=trend, carry_weight=carry,
                        diversification_multiplier=2.0, forecast_cap=2.0)


def baseline_spec(spec: StrategySpec) -> StrategySpec:
    """Long-only risk parity with the same universe, sizing and rebalance rule.

    A time-series strategy that cannot beat simply holding every market at
    equal risk has not demonstrated timing skill, only exposure to the drift of
    the asset classes it trades (for example the 2002-2020 bond rally).
    """
    return _ts_spec(spec.universe, spec.dataset_id, 0.0, 0.0, family=BASELINE_FAMILY)


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
            "prior_trials": FUTURES_PRIOR_LAB_TRIALS,
            "benchmark": FUTURES_BENCHMARK,
            "cost_bps": FUTURES_COST_BPS,
            "market": "diversified futures (31 contracts, 6 asset classes)",
        },
    }


def lane_definitions(universe: list[str], dataset_id: str) -> dict[str, dict[str, Any]]:
    if dataset_id == FUTURES_DATASET:
        return futures_lane_definitions(universe, dataset_id)
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
