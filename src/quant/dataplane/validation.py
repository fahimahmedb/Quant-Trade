"""Validation rules applied before a dataset is allowed to be AVAILABLE.

These checks exist to stop the classic silent corruptions: a symbol that stops
updating, a duplicated bar, a non-positive/non-finite price, malformed session
keys, impossible OHLC geometry, or an implausible one-day move that is really
an unadjusted split.
"""

from __future__ import annotations

from datetime import date as calendar_date
import math
from typing import Any

from .panel import PricePanel


MAX_PLAUSIBLE_DAILY_MOVE = 0.35


def validation_policy(record: Any) -> dict[str, Any]:
    """Per-dataset validation declared in its point-in-time metadata.

    A staggered universe (coins listed and delisted over time) must not be
    forced to a common history or to all-symbols-present-today: that would
    silently drop delisted instruments (survivorship). Such a dataset declares
    ``required_symbols`` (anchors that must be current) and a smaller
    ``min_rows_per_symbol``; everything else stays the default.
    """
    declared = (getattr(record, "point_in_time", None) or {})
    return {"required": declared.get("required_symbols"),
            "min_rows": int(declared.get("min_rows_per_symbol", 250))}


def validate_panel(panel: PricePanel, expected_symbols: list[str],
                   min_rows_per_symbol: int = 250) -> dict[str, Any]:
    problems: list[str] = []
    warnings: list[str] = []

    missing = [symbol for symbol in expected_symbols if symbol not in panel.symbols]
    if missing:
        problems.append(f"symbols absent from panel: {sorted(missing)}")

    if panel.duplicate_keys:
        problems.append(f"duplicate bars: {sorted(set(panel.duplicate_keys))[:5]}")

    invalid_dates: list[str] = []
    for value in panel.dates:
        try:
            calendar_date.fromisoformat(value)
        except ValueError:
            invalid_dates.append(value)
    if invalid_dates:
        problems.append(f"invalid ISO session dates: {sorted(invalid_dates)[:5]}")

    per_symbol = {symbol: sum(1 for (_, sym) in panel.bars if sym == symbol)
                  for symbol in panel.symbols}
    thin = {symbol: count for symbol, count in per_symbol.items() if count < min_rows_per_symbol}
    if thin:
        problems.append(f"symbols with fewer than {min_rows_per_symbol} bars: {sorted(thin)}")

    non_finite = [f"{date}:{symbol}:{field}"
                  for (date, symbol), bar in panel.bars.items()
                  for field, value in bar.items() if not math.isfinite(value)]
    if non_finite:
        problems.append(f"non-finite market values: {sorted(non_finite)[:5]}")

    non_positive = [f"{date}:{symbol}" for (date, symbol), bar in panel.bars.items()
                    if any(bar[field] <= 0 for field in ("open", "high", "low", "close", "adj_close"))]
    if non_positive:
        problems.append(f"non-positive prices: {sorted(non_positive)[:5]}")

    negative_volume = [f"{date}:{symbol}" for (date, symbol), bar in panel.bars.items()
                       if bar["volume"] < 0]
    if negative_volume:
        problems.append(f"negative volume: {sorted(negative_volume)[:5]}")

    # Raw execution prices must describe a possible daily bar. Adjusted close is
    # deliberately excluded because corporate-action adjustment changes scale.
    impossible_ohlc = [
        f"{date}:{symbol}" for (date, symbol), bar in panel.bars.items()
        if all(math.isfinite(bar[field]) for field in ("open", "high", "low", "close"))
        and not (bar["low"] <= min(bar["open"], bar["close"])
                 <= max(bar["open"], bar["close"]) <= bar["high"])]
    if impossible_ohlc:
        problems.append(f"impossible OHLC bars: {sorted(impossible_ohlc)[:5]}")

    # A panel can have plenty of history and still silently stop one required
    # symbol today. Alignment would merely stop advancing and make the daemon
    # look healthy-but-idle, so latest-session coverage is an availability
    # condition rather than a warning.
    if panel.dates and not missing:
        latest = panel.dates[-1]
        stale = [symbol for symbol in expected_symbols if not panel.has(latest, symbol)]
        if stale:
            problems.append(f"symbols missing latest session {latest}: {sorted(stale)}")

    aligned = panel.aligned_dates(expected_symbols) if not missing else []
    dropped = len(panel.dates) - len(aligned)
    if dropped:
        warnings.append(f"{dropped} dates are not covered by every expected symbol")

    extreme: list[str] = []
    if aligned and not non_finite:
        _, series = panel.returns(expected_symbols)
        for symbol, values in series.items():
            for value in values:
                if abs(value) > MAX_PLAUSIBLE_DAILY_MOVE:
                    extreme.append(symbol)
                    break
    if extreme:
        warnings.append(f"symbols with a daily move beyond "
                        f"{MAX_PLAUSIBLE_DAILY_MOVE:.0%}: {sorted(set(extreme))}")

    return {"passed": not problems, "problems": problems, "warnings": warnings,
            "aligned_dates": len(aligned), "rows": len(panel.bars),
            "bars_per_symbol": per_symbol}
