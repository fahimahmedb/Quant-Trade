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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def label(self) -> str:
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
    return target_weights(cross_sectional_scores(panel, spec.universe, asof,
                                                 spec.lookback_days), spec)
