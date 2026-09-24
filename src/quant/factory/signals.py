"""Signal construction.

This module is imported by both the research backtester and the desk's SCAN
function. That is deliberate: if research evidence is produced by different
code from the code that trades, the evidence does not describe the system's
behaviour and every validation result is misleading.

All functions take an ``asof`` date and may only read bars dated ``asof`` or
earlier.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import asdict, dataclass, field
from typing import Any

from ..dataplane.panel import PricePanel


@dataclass(frozen=True)
class StrategySpec:
    """A machine-readable, executable strategy definition.

    The desk executes this object directly, so a validated strategy cannot
    drift from the thing that was validated.
    """

    family: str
    universe: list[str]
    lookback_days: int
    direction: int                  # -1 contrarian, +1 trend-following
    min_abs_score: float = 0.5
    max_weight: float = 0.25
    gross_exposure: float = 1.0
    holding_days: int = 1
    no_trade_band: float = 0.0
    dataset_id: str = ""
    # --- time-series (futures) families only; ignored by cross_sectional -----
    #: Annualised volatility targeted for the whole sleeve.
    vol_target: float = 0.0
    trend_weight: float = 0.0
    carry_weight: float = 0.0
    #: Fixed instrument-diversification multiplier (declared, never fitted).
    diversification_multiplier: float = 1.0
    forecast_cap: float = 2.0
    #: When set, sessions are the trading days of this one symbol and the
    #: universe is *staggered*: an instrument participates from the first
    #: session its own history allows, and N is the count of instruments
    #: eligible at that date (known at that date, so not hindsight). When
    #: empty, sessions are the dates on which every universe member traded.
    calendar_symbol: str = ""
    #: Carver's "speed limit": an instrument is eligible on a date only if its
    #: expected annual trading cost, in Sharpe units, is at most this value
    #: (0 disables the rule). Uses that date's own cost and volatility.
    max_cost_sharpe: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def label(self) -> str:
        if self.family in TIME_SERIES_FAMILIES:
            return (f"{self.family}_t{self.trend_weight:g}_c{self.carry_weight:g}"
                    f"_v{self.vol_target:g}_h{self.holding_days}_b{self.no_trade_band:g}"
                    + (f"_sl{self.max_cost_sharpe:g}" if self.max_cost_sharpe else ""))
        sign = "reversal" if self.direction < 0 else "momentum"
        return (f"xs_{sign}_l{self.lookback_days}_z{self.min_abs_score:g}"
                f"_h{self.holding_days}_b{self.no_trade_band:g}")


def should_rebalance(sessions_held: int | None, drift: float, spec: StrategySpec) -> bool:
    """The single rebalance rule, shared by the backtester and the desk.

    Turnover is the dominant cost in this system, so the decision that controls
    it must not be implemented twice.
    """
    if sessions_held is None:
        return True
    if sessions_held < spec.holding_days:
        return False
    return drift >= spec.no_trade_band


def cross_sectional_scores(panel: PricePanel, universe: list[str], asof: str,
                           lookback_days: int) -> dict[str, float]:
    """Cross-sectionally demeaned trailing return, scaled by its own dispersion.

    Demeaning removes the common (market) component, so the score describes
    relative performance inside the universe rather than market direction.
    Returns an empty mapping when ``asof`` has insufficient aligned history,
    which callers must treat as "no signal", never as zero signal.
    """
    dates = panel.aligned_dates(universe)
    position = panel.aligned_index(universe, asof)
    if position is None or position < lookback_days:
        return {}
    start, end = dates[position - lookback_days], dates[position]
    raw = {}
    for symbol in universe:
        before = panel.price(start, symbol)
        if before <= 0:
            return {}
        raw[symbol] = panel.price(end, symbol) / before - 1.0
    mean = statistics.fmean(raw.values())
    residual = {symbol: value - mean for symbol, value in raw.items()}
    dispersion = statistics.pstdev(residual.values())
    if dispersion <= 0:
        return {}
    return {symbol: value / dispersion for symbol, value in residual.items()}


def target_weights(scores: dict[str, float], spec: StrategySpec) -> dict[str, float]:
    """Convert scores into dollar-neutral target weights.

    Dollar neutrality is enforced by demeaning the signal after selection, so
    the book cannot quietly accumulate net market exposure and report it as
    relative-value skill.
    """
    if not scores:
        return {}
    selected = {symbol: value for symbol, value in scores.items()
                if abs(value) >= spec.min_abs_score}
    if len(selected) < 2:
        return {}
    signal = {symbol: spec.direction * value for symbol, value in selected.items()}
    offset = statistics.fmean(signal.values())
    signal = {symbol: value - offset for symbol, value in signal.items()}
    total = sum(abs(value) for value in signal.values())
    if total <= 0:
        return {}
    weights = {symbol: spec.gross_exposure * value / total for symbol, value in signal.items()}
    return _project(weights, spec.max_weight)


def _project(weights: dict[str, float], cap: float) -> dict[str, float]:
    """Enforce the per-name cap while keeping the book exactly dollar-neutral.

    Capping and re-neutralizing fight each other: subtracting the mean after a
    cap can push a capped name back over it, and rescaling afterwards does the
    same. So names that hit the cap are pinned there and the residual is spread
    only over the names that are still free, repeating until nothing violates.

    Neutrality and the cap are exact; gross exposure is whatever that allows,
    which can be slightly under target. That ordering is deliberate: neutrality
    is what isolates the residual from market beta, and the cap is a risk limit.
    Hitting a gross-exposure target exactly is worth neither of them.
    """
    free = dict(weights)
    pinned: dict[str, float] = {}
    for _ in range(len(weights) + 1):
        offset = sum(free.values()) + sum(pinned.values())
        if free:
            adjustment = offset / len(free)
            free = {symbol: value - adjustment for symbol, value in free.items()}
        violating = {symbol: math.copysign(cap, value)
                     for symbol, value in free.items() if abs(value) > cap + 1e-12}
        if not violating:
            break
        pinned.update(violating)
        free = {symbol: value for symbol, value in free.items() if symbol not in violating}
        if not free:
            break
    result = {**pinned, **free}
    if sum(abs(value) for value in result.values()) <= 0:
        return {}
    return result


def weights_for(panel: PricePanel, spec: StrategySpec, asof: str) -> dict[str, float]:
    """The complete signal path used identically by research and the desk."""
    if spec.family in TIME_SERIES_FAMILIES:
        return time_series_weights(panel, spec, asof)
    return target_weights(cross_sectional_scores(panel, spec.universe, asof,
                                                 spec.lookback_days), spec)


# ---------------------------------------------------------------------------
# Time-series trend / carry (futures)
# ---------------------------------------------------------------------------
#
# Weights are *fractions of sleeve capital* (notional / capital), signed, and
# are not dollar-neutral: these families take directional risk by design and
# are judged against a long-only risk-parity baseline instead of against zero
# beta (see ``evaluate.falsify``).
#
# Every constant below is declared from the published literature (Carver,
# "Systematic Trading", 2015: EWMAC and carry forecast scalars) rather than
# fitted on this dataset, so none of them is a hidden trial.

TREND_FAMILY = "ts_trend_carry"
BASELINE_FAMILY = "ts_long_risk_parity"
TIME_SERIES_FAMILIES = frozenset({TREND_FAMILY, BASELINE_FAMILY})

#: (fast span, slow span, scalar giving an average absolute forecast of 10)
EWMAC_RULES = ((16, 64, 3.75), (32, 128, 2.65), (64, 256, 1.91))
CARRY_SCALAR = 30.0
CARRY_SMOOTHING_SPAN = 90
VOL_SPAN = 35
#: A volatility estimate is floored at this share of its slow average, so a
#: stale or very quiet stretch cannot produce an enormous position.
VOL_FLOOR_SHARE = 0.3
VOL_SLOW_SPAN = 500
#: Sessions of history an instrument needs before it may carry a position.
WARMUP_SESSIONS = 256
#: A carry estimate not refreshed for this many sessions is dropped rather than
#: used stale (some index futures report the adjacent contract rarely).
CARRY_MAX_AGE_SESSIONS = 20
ANNUALISATION = 16.0          # sqrt(256)
MIN_WEIGHT = 1e-4
#: Declared trades per year for a blended EWMAC/carry forecast (Carver 2015,
#: ch. 12: ~5-15 for these speeds); used only by the speed-limit rule.
ASSUMED_TRADES_PER_YEAR = 10.0


def _series(panel: PricePanel, symbol: str) -> dict[str, tuple[float, float, float | None]]:
    """Per-session (annual vol, trend forecast, carry forecast) for one symbol.

    One causal pass: each value at session ``i`` is computed from sessions
    ``0..i`` only. The result is cached on the immutable panel; because every
    recursion starts at the symbol's first bar, a truncated panel (research
    windows) produces identical values on every date it shares.
    """
    key = ("ts_series", symbol)
    cached = panel.derived.get(key)
    if cached is not None:
        return cached  # type: ignore[return-value]
    dates = panel.dates_for(symbol)
    out: dict[str, tuple[float, float, float | None]] = {}
    fast = [0.0] * len(EWMAC_RULES)
    slow = [0.0] * len(EWMAC_RULES)
    variance = slow_variance = None
    carry_ewm: float | None = None
    carry_age = CARRY_MAX_AGE_SESSIONS + 1
    previous: float | None = None
    a_vol, a_slow = 2.0 / (VOL_SPAN + 1), 2.0 / (VOL_SLOW_SPAN + 1)
    a_carry = 2.0 / (CARRY_SMOOTHING_SPAN + 1)
    for index, date in enumerate(dates):
        price = panel.price(date, symbol)
        if index == 0:
            fast = [price] * len(EWMAC_RULES)
            slow = [price] * len(EWMAC_RULES)
        else:
            for position, (f_span, s_span, _) in enumerate(EWMAC_RULES):
                fast[position] += 2.0 / (f_span + 1) * (price - fast[position])
                slow[position] += 2.0 / (s_span + 1) * (price - slow[position])
        if previous is not None and previous > 0:
            ret = price / previous - 1.0
            variance = ret * ret if variance is None else variance + a_vol * (ret * ret - variance)
            slow_variance = (ret * ret if slow_variance is None
                             else slow_variance + a_slow * (ret * ret - slow_variance))
        previous = price
        raw_carry = panel.feature(date, symbol, "carry_ann")
        if raw_carry is not None and math.isfinite(raw_carry):
            carry_ewm = raw_carry if carry_ewm is None else carry_ewm + a_carry * (raw_carry - carry_ewm)
            carry_age = 0
        else:
            carry_age += 1
        if variance is None or slow_variance is None or index < WARMUP_SESSIONS:
            continue
        daily_vol = max(math.sqrt(variance), VOL_FLOOR_SHARE * math.sqrt(slow_variance))
        if daily_vol <= 0:
            continue
        trend = sum((fast[p] - slow[p]) / (price * daily_vol) * scalar
                    for p, (_, _, scalar) in enumerate(EWMAC_RULES)) / len(EWMAC_RULES) / 10.0
        carry = (carry_ewm / (daily_vol * ANNUALISATION) * CARRY_SCALAR / 10.0
                 if carry_ewm is not None and carry_age <= CARRY_MAX_AGE_SESSIONS else None)
        out[date] = (daily_vol * ANNUALISATION, trend, carry)
    panel.derived[key] = out
    return out


def live_breadth(panel: PricePanel, spec: StrategySpec, asof: str) -> int:
    """Instruments quoted on ``asof`` and past warmup, before any cost filter.

    Known at ``asof`` (listing and history length only), so using it is not
    hindsight; counting contracts the speed limit excludes keeps the survivors
    from being levered up to fill their budget.
    """
    return sum(1 for symbol in spec.universe
               if panel.has(asof, symbol) and asof in _series(panel, symbol))


def time_series_forecasts(panel: PricePanel, spec: StrategySpec,
                          asof: str) -> dict[str, dict[str, float]]:
    """Capped combined forecast and annual volatility per eligible instrument."""
    result: dict[str, dict[str, float]] = {}
    for symbol in spec.universe:
        if not panel.has(asof, symbol):
            continue
        point = _series(panel, symbol).get(asof)
        if point is None:
            continue
        annual_vol, trend, carry = point
        if spec.max_cost_sharpe > 0:
            own = panel.feature(asof, symbol, "cost_bps")
            if own is None or ASSUMED_TRADES_PER_YEAR * own / 10_000.0 / annual_vol > spec.max_cost_sharpe:
                continue  # too expensive to trade at this speed, or cost unknown
        if spec.family == BASELINE_FAMILY:
            forecast = 1.0
        else:
            weight_total = spec.trend_weight + (spec.carry_weight if carry is not None else 0.0)
            if weight_total <= 0:
                continue
            forecast = (spec.trend_weight * trend
                        + (spec.carry_weight * carry if carry is not None else 0.0)) / weight_total
        forecast = max(-spec.forecast_cap, min(spec.forecast_cap, forecast))
        result[symbol] = {"forecast": forecast, "annual_vol": annual_vol}
    return result


def time_series_weights(panel: PricePanel, spec: StrategySpec, asof: str) -> dict[str, float]:
    """Volatility-targeted notional weights: forecast x (target / instrument vol) / N x IDM.

    Aligned universe: ``N`` is the declared universe size. Staggered universe
    (``calendar_symbol``): ``N`` is ``live_breadth`` (quoted and past warmup,
    counted *before* the speed-limit filter) and the diversification
    multiplier is capped at ``sqrt(N)``, its value for N uncorrelated
    instruments, so a thin early universe is never levered to a full book.
    """
    forecasts = time_series_forecasts(panel, spec, asof)
    if not forecasts or spec.vol_target <= 0:
        return {}
    if spec.calendar_symbol:
        breadth = max(live_breadth(panel, spec, asof), 1)
        idm = min(spec.diversification_multiplier, math.sqrt(breadth))
    else:
        breadth, idm = len(spec.universe), spec.diversification_multiplier
    scale = spec.vol_target * idm / breadth
    weights = {}
    for symbol, item in forecasts.items():
        weight = item["forecast"] * scale / item["annual_vol"]
        weight = max(-spec.max_weight, min(spec.max_weight, weight))
        if abs(weight) >= MIN_WEIGHT:
            weights[symbol] = weight
    return weights
