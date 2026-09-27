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
    #: listing_fade only: when set, a long leg in this symbol offsets the
    #: short notional one for one. Omitted from ``to_dict`` while empty so
    #: every earlier lane keeps its grid hash (and trial accounting).
    hedge_symbol: str = ""

    def to_dict(self) -> dict[str, Any]:
        document = asdict(self)
        if not document["hedge_symbol"]:
            del document["hedge_symbol"]
        return document

    @property
    def label(self) -> str:
        if self.family in CALENDAR_FAMILIES:
            return f"{self.family}_x{self.gross_exposure:g}_h{self.holding_days}"
        if self.family == LISTING_FADE:
            return (f"listing_fade_n{self.lookback_days}"
                    + (f"_hedge_{self.hedge_symbol}" if self.hedge_symbol else "_unhedged")
                    + f"_w{self.max_weight:g}_g{self.gross_exposure:g}")
        if self.family in ("funding_spread", "funding_spread_hold"):
            return (f"{self.family}_l{self.lookback_days}_z{self.min_abs_score:g}"
                    f"_w{self.max_weight:g}_g{self.gross_exposure:g}_b{self.no_trade_band:g}")
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
    if spec.family in CALENDAR_FAMILIES:
        return calendar_weights(panel, spec, asof)
    if spec.family in FUNDING_FAMILIES:
        return funding_spread_weights(panel, spec, asof)
    if spec.family == LISTING_FADE:
        return listing_fade_weights(panel, spec, asof)
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


# ---------------------------------------------------------------------------
# Calendar effects (flows known in advance)
# ---------------------------------------------------------------------------
#
# These families always return an explicit target, including an explicit zero
# when flat, so the shared rebalance rule closes the position on schedule
# instead of reading "no signal" as "keep holding". Every input is a feature on
# the ``asof`` row (sessions until the next scheduled FOMC decision, sessions
# left in the month) or a price at or before ``asof``.

FOMC_OVERNIGHT = "calendar_fomc_overnight"
FOMC_BASELINE = "calendar_overnight_always"
MONTH_END = "calendar_month_end_rebalance"
MONTH_END_BASELINE = "calendar_month_end_long"
CALENDAR_FAMILIES = frozenset({FOMC_OVERNIGHT, FOMC_BASELINE, MONTH_END, MONTH_END_BASELINE})
#: Symbols the calendar families trade (see ``dataplane.calendar_legs``).
OVERNIGHT_LEG = "SPY_ON"
EQUITY, BONDS = "SPY", "TLT"
#: Hold the last two sessions of the month: decide with two sessions left.
MONTH_END_DECISION_SESSIONS_LEFT = 2


def _month_to_date(panel: PricePanel, symbol: str, asof: str) -> float | None:
    dates = [day for day in panel.dates_for(symbol) if day <= asof]
    before = [day for day in dates if day[:7] < asof[:7]]
    if not before or not panel.has(asof, symbol):
        return None
    start = panel.price(before[-1], symbol)
    return panel.price(asof, symbol) / start - 1.0 if start > 0 else None


def calendar_weights(panel: PricePanel, spec: StrategySpec, asof: str) -> dict[str, float]:
    if not panel.has(asof, EQUITY):
        return {}
    exposure = spec.gross_exposure or 1.0
    if spec.family in (FOMC_OVERNIGHT, FOMC_BASELINE):
        # Entry at the next fill (MOC on the session before the decision day),
        # exit one session later (MOO on the decision day).
        due = panel.feature(asof, EQUITY, "fomc_in_sessions") == 2.0
        on = due or spec.family == FOMC_BASELINE
        return {OVERNIGHT_LEG: exposure if on else 0.0}
    left = panel.feature(asof, EQUITY, "sessions_left_in_month")
    if left != MONTH_END_DECISION_SESSIONS_LEFT:
        return {EQUITY: 0.0}
    if spec.family == MONTH_END_BASELINE:
        return {EQUITY: exposure}
    equity, bonds = _month_to_date(panel, EQUITY, asof), _month_to_date(panel, BONDS, asof)
    if equity is None or bonds is None or equity == bonds:
        return {EQUITY: 0.0}
    # Fixed-weight balanced funds sell the month's winner and buy the loser at
    # month end (Harvey, Mazzoleni & Melone 2025): lean against equities when
    # they outperformed bonds month to date, with them when they lagged.
    return {EQUITY: -exposure if equity > bonds else exposure}


# ---------------------------------------------------------------------------
# Cross-venue perpetual funding spread (market-neutral per coin)
# ---------------------------------------------------------------------------
#
# Universe symbols are ``<VENUE>.<COIN>`` (e.g. ``HL.ETH``, ``BY.ETH``) with a
# ``carry_rate`` feature: funding paid by longs over that session. The venue
# pair is read from the universe (exactly two venue prefixes, e.g. HL/BY or
# HL/DX). For a coin quoted on both venues, when the trailing mean funding
# difference exceeds the entry threshold (annualised), the sleeve is short the
# venue that charges longs more and long the other, one unit notional per leg,
# so price exposure cancels and the position collects the funding difference.
#
# ``funding_spread``: stateless; the pair is held while the trailing spread
# stays above the entry threshold, and the shared no-trade band limits churn.
# ``funding_spread_hold``: hysteresis; entered when |spread| >= threshold and
# held (same direction) until spread falls below threshold * FUNDING_EXIT_SHARE.
# The held state is recomputed causally from the pair's own history on every
# call (a forward recurrence over sessions <= asof), so research and the Desk
# share one pure function and no hidden state lives outside the panel.

FUNDING_SPREAD = "funding_spread"
FUNDING_SPREAD_HOLD = "funding_spread_hold"
FUNDING_FAMILIES = frozenset({FUNDING_SPREAD, FUNDING_SPREAD_HOLD})
FUNDING_EXIT_SHARE = 0.5
FUNDING_LOOKBACK = 3
DAYS_PER_YEAR = 365.0


def funding_venues(universe: list[str]) -> tuple[str, str]:
    """The two venue prefixes of a funding-spread universe, in sorted order.

    The order only names the legs: the weights are symmetric in it.
    """
    venues = sorted({symbol.split(".", 1)[0] for symbol in universe if "." in symbol})
    if len(venues) != 2:
        raise ValueError(f"a funding-spread universe needs exactly two venues, got {venues}")
    return venues[0], venues[1]


def _trailing_carry(panel: PricePanel, symbol: str, asof: str, sessions: int) -> float | None:
    key = ("carry_prefix", symbol)
    cached = panel.derived.get(key)
    if cached is None:
        dates = panel.dates_for(symbol)
        values = [panel.feature(day, symbol, "carry_rate") for day in dates]
        cached = (dates, {day: index for index, day in enumerate(dates)}, values)
        panel.derived[key] = cached
    dates, index, values = cached
    position = index.get(asof)
    if position is None or position + 1 < sessions:
        return None
    window = values[position + 1 - sessions: position + 1]
    if any(value is None for value in window):
        return None
    return sum(window) / sessions


def _pair_spread(panel: PricePanel, a: str, b: str, asof: str, lookback: int) -> float | None:
    """Annualised trailing funding spread (a minus b) at ``asof``, or None."""
    if not (panel.has(asof, a) and panel.has(asof, b)):
        return None
    if panel.feature(asof, a, "price_proxy") or panel.feature(asof, b, "price_proxy"):
        return None       # a leg valued at the other venue's price hides the hedge risk
    carry_a = _trailing_carry(panel, a, asof, lookback)
    carry_b = _trailing_carry(panel, b, asof, lookback)
    if carry_a is None or carry_b is None:
        return None
    return (carry_a - carry_b) * DAYS_PER_YEAR


def _held_direction(panel: PricePanel, a: str, b: str, asof: str, lookback: int,
                    entry: float, exit_: float) -> int:
    """Hysteresis state of pair (a, b) at ``asof``: +1/-1 held, 0 flat.

    Forward recurrence over the sessions of either leg up to ``asof``: enter
    with the spread's sign when |spread| >= entry; stay while spread *
    direction >= exit; otherwise flat. A session where the pair is not
    tradable (a leg missing, a proxy price, an incomplete lookback) resets to
    flat. It starts at the pair's first session and reads only sessions <=
    each date, so the state at a date is invariant to truncating later data.
    """
    key = ("funding_hold", a, b, lookback, entry, exit_)
    cached = panel.derived.get(key)
    if cached is None:
        cached = {}
        state = 0
        for day in sorted(set(panel.dates_for(a)) | set(panel.dates_for(b))):
            spread = _pair_spread(panel, a, b, day, lookback)
            if spread is None:
                state = 0
            elif abs(spread) >= entry:
                state = 1 if spread > 0 else -1
            elif not (state and spread * state >= exit_):
                state = 0
            cached[day] = state
        panel.derived[key] = cached
    return cached.get(asof, 0)


def funding_spread_weights(panel: PricePanel, spec: StrategySpec, asof: str) -> dict[str, float]:
    first, second = funding_venues(spec.universe)
    coins = sorted({symbol.split(".", 1)[1] for symbol in spec.universe
                    if symbol.startswith(first + ".")}
                   & {symbol.split(".", 1)[1] for symbol in spec.universe
                      if symbol.startswith(second + ".")})
    lookback = spec.lookback_days or FUNDING_LOOKBACK
    hold = spec.family == FUNDING_SPREAD_HOLD
    candidates = []
    for coin in coins:
        a, b = f"{first}.{coin}", f"{second}.{coin}"
        spread = _pair_spread(panel, a, b, asof, lookback)
        if spread is None:
            continue
        if hold:
            qualifies = bool(_held_direction(panel, a, b, asof, lookback, spec.min_abs_score,
                                             spec.min_abs_score * FUNDING_EXIT_SHARE))
        else:
            qualifies = abs(spread) >= spec.min_abs_score
        if qualifies:
            candidates.append((abs(spread), coin, a, b, spread))
    candidates.sort(reverse=True)
    limit = max(1, int(round(spec.gross_exposure / (2 * spec.max_weight)))) if spec.max_weight else 0
    weights: dict[str, float] = {}
    for _, coin, a, b, spread in candidates[:limit]:
        side = 1.0 if spread > 0 else -1.0          # venue a charges longs more: short a
        weights[a] = -side * spec.max_weight
        weights[b] = side * spec.max_weight
    if not weights:
        # Nothing qualifies: an explicit flat target (one zero leg) so research
        # and the Desk close every held pair instead of reading "no signal" as
        # "keep holding". Unselected legs of a non-empty target are closed by
        # the same rule (walk_forward replaces holdings; SIZE zeroes them).
        present = next((symbol for symbol in spec.universe if panel.has(asof, symbol)), None)
        return {present: 0.0} if present else {}
    return weights


# ---------------------------------------------------------------------------
# New-listing fade (Hyperliquid perpetuals)
# ---------------------------------------------------------------------------
#
# Universe symbols are ``HL.<COIN>`` rows carrying two point-in-time features
# (``build_hl_listings_dataset``): ``listing_age_days`` = asof - first
# Hyperliquid-traded day, and ``listing_eligible`` = 1 only for coins listed
# after the API history cutoff (incumbents at history start never count).
# A coin is in its window on ``asof`` when it is quoted that day and
# 1 <= age <= N (``lookback_days``): the decision is formed on the close of the
# first full UTC day after listing, and the shared timeline fills it one full
# day later. Every in-window coin is short an equal weight, capped per name;
# with ``hedge_symbol`` set a long leg in that symbol offsets the short
# notional one for one. Nothing qualifying is an explicit flat target.

LISTING_FADE = "listing_fade"


def listing_fade_weights(panel: PricePanel, spec: StrategySpec, asof: str) -> dict[str, float]:
    window = spec.lookback_days
    shorts = []
    for symbol in spec.universe:
        if symbol in (spec.hedge_symbol, spec.calendar_symbol) or not panel.has(asof, symbol):
            continue
        if panel.feature(asof, symbol, "listing_eligible") != 1.0:
            continue
        age = panel.feature(asof, symbol, "listing_age_days")
        if age is not None and 1 <= age <= window:
            shorts.append(symbol)
    legs = 2 if spec.hedge_symbol else 1
    if not shorts or (spec.hedge_symbol and not panel.has(asof, spec.hedge_symbol)):
        anchor = spec.hedge_symbol or spec.calendar_symbol
        present = anchor if anchor and panel.has(asof, anchor) else next(
            (symbol for symbol in spec.universe if panel.has(asof, symbol)), None)
        return {present: 0.0} if present else {}
    each = min(spec.max_weight, spec.gross_exposure / (legs * len(shorts)))
    weights = {symbol: -each for symbol in sorted(shorts)}
    if spec.hedge_symbol:
        weights[spec.hedge_symbol] = each * len(shorts)
    return weights


#: Families that take directional risk by design: judged against a passive
#: baseline of the same exposure instead of against zero market beta.
DIRECTIONAL_FAMILIES = TIME_SERIES_FAMILIES | CALENDAR_FAMILIES
