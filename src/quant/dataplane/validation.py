"""Validation rules applied before a dataset is allowed to be AVAILABLE.

These checks exist to stop the classic silent corruptions: a symbol that stops
updating, a duplicated bar, a non-positive price, an impossible one-day move
that is really an unadjusted split.
"""

from __future__ import annotations

from typing import Any

from .panel import PricePanel


MAX_PLAUSIBLE_DAILY_MOVE = 0.35


def validate_panel(panel: PricePanel, expected_symbols: list[str],
                   min_rows_per_symbol: int = 250) -> dict[str, Any]:
    problems: list[str] = []
    warnings: list[str] = []

    missing = [symbol for symbol in expected_symbols if symbol not in panel.symbols]
    if missing:
        problems.append(f"symbols absent from panel: {sorted(missing)}")

    per_symbol = {symbol: sum(1 for (_, sym) in panel.bars if sym == symbol)
                  for symbol in panel.symbols}
    thin = {symbol: count for symbol, count in per_symbol.items() if count < min_rows_per_symbol}
    if thin:
        problems.append(f"symbols with fewer than {min_rows_per_symbol} bars: {sorted(thin)}")

    non_positive = [f"{date}:{symbol}" for (date, symbol), bar in panel.bars.items()
                    if bar["adj_close"] <= 0 or bar["close"] <= 0]
    if non_positive:
        problems.append(f"non-positive prices: {sorted(non_positive)[:5]}")

    inconsistent = [f"{date}:{symbol}" for (date, symbol), bar in panel.bars.items()
                    if not (bar["low"] <= bar["close"] <= bar["high"])]
    if inconsistent:
        warnings.append(f"bars where close sits outside the low/high range: {len(inconsistent)}")

    aligned = panel.aligned_dates(expected_symbols) if not missing else []
    dropped = len(panel.dates) - len(aligned)
    if dropped:
        warnings.append(f"{dropped} dates are not covered by every expected symbol")

    extreme: list[str] = []
    if aligned:
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
