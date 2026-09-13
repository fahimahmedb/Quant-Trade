"""Declared research lanes.

Every expression a lane will try is declared here *before* the data is touched,
and the full grid is counted toward the multiple-testing budget. A lane that
quietly widened its search after seeing results would be buying significance,
which is the failure mode ``QUANT_NORTH_STAR.md`` section 7 names.
"""

from __future__ import annotations

from typing import Any

from .signals import StrategySpec


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


def lane_definitions(universe: list[str], dataset_id: str) -> dict[str, dict[str, Any]]:
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
