"""Calendar-effect panel: session-leg instruments and exchange calendars.

Two published calendar effects need executions the Desk's single timeline
(decide after close(t), fill at open(t+1)) cannot express directly:

* FOMC eve: buy at the close before a scheduled decision day, sell at that
  day's open (Lucca-Moench 2015; still +18bp/t 3.6 on SPY 2016-2026 in the lab);
* anything else that holds only the overnight leg.

Instead of a second execution path, this module derives a **session-leg
instrument** ``SPY_ON`` whose index moves only overnight::

    ON_open(d) = ON_close(d) = ON(d)      ON(d+1) = ON(d) * open(d+1) / close(d)

Holding ``SPY_ON`` from open(d) to open(d+1) earns exactly SPY's close(d) ->
open(d+1) return, i.e. the economic position "buy SPY market-on-close on d,
sell market-on-open on d+1". A Desk fill "at open(d)" of SPY_ON is that MOC
order, placed during session d from a decision taken after close(d-1), so the
timeline stays causal. Each round trip still pays two fills in the Book, which
is the true cost of the MOC/MOO pair.

Exchange sessions ahead of ``asof`` are needed to know that "the session after
next is an FOMC day". NYSE holidays are published years in advance, so the
calendar below is rule-based and known ex ante; it is not read from prices.
"""

from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from .panel import PricePanel

CALENDAR_DATASET = "us_calendar_legs_daily"
OVERNIGHT_SUFFIX = "_ON"
CALENDAR_BASE = ["SPY", "TLT"]
FOMC_FILE = "data/calendars/fomc_scheduled.csv"


# --- NYSE sessions (rule-based, known in advance) ------------------------------
def _easter(year: int) -> date:
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def _observed(day: date) -> date:
    if day.weekday() == 5:
        return day - timedelta(days=1)
    if day.weekday() == 6:
        return day + timedelta(days=1)
    return day


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    first = date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    return first + timedelta(days=offset + 7 * (n - 1))


def _last_weekday(year: int, month: int, weekday: int) -> date:
    last = date(year + (month == 12), month % 12 + 1, 1) - timedelta(days=1)
    return last - timedelta(days=(last.weekday() - weekday) % 7)


#: One-off closures that no rule predicts (national days of mourning).
SPECIAL_CLOSURES = {date(2018, 12, 5), date(2025, 1, 9)}


def nyse_holidays(year: int) -> set[date]:
    days = {
        _nth_weekday(year, 1, 0, 3),               # Martin Luther King Jr. Day
        _nth_weekday(year, 2, 0, 3),               # Washington's Birthday
        _easter(year) - timedelta(days=2),         # Good Friday
        _last_weekday(year, 5, 0),                 # Memorial Day
        _observed(date(year, 7, 4)),
        _nth_weekday(year, 9, 0, 1),               # Labor Day
        _nth_weekday(year, 11, 3, 4),              # Thanksgiving
        _observed(date(year, 12, 25)),
    }
    new_year = date(year, 1, 1)
    if new_year.weekday() != 5:                    # a Saturday New Year is not moved back
        days.add(_observed(new_year))
    if year >= 2022:
        days.add(_observed(date(year, 6, 19)))     # Juneteenth
    return {day for day in days if day.year == year} | {
        day for day in SPECIAL_CLOSURES if day.year == year}


def is_session(day: date) -> bool:
    return day.weekday() < 5 and day not in nyse_holidays(day.year)


def next_sessions(asof: str, count: int) -> list[str]:
    day, out = date.fromisoformat(asof), []
    while len(out) < count:
        day += timedelta(days=1)
        if is_session(day):
            out.append(day.isoformat())
    return out


def sessions_left_in_month(asof: str) -> int:
    """Sessions after ``asof`` that are still in ``asof``'s month."""
    day, month, left = date.fromisoformat(asof), date.fromisoformat(asof).month, 0
    while True:
        day += timedelta(days=1)
        if day.month != month:
            return left
        if is_session(day):
            left += 1


# --- FOMC schedule --------------------------------------------------------------
def load_fomc_days(root: Path) -> list[str]:
    path = root / FOMC_FILE
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return sorted(row["decision_date"] for row in csv.DictReader(handle))


# --- derived panel ----------------------------------------------------------------
#: Farther than this, "sessions until the next FOMC decision" is left empty.
FOMC_HORIZON = 30


def calendar_features(day: str, fomc_days: list[str]) -> dict[str, float]:
    """Point-in-time calendar facts for session ``day`` (all known in advance)."""
    features = {"sessions_left_in_month": float(sessions_left_in_month(day))}
    upcoming = [item for item in fomc_days if item > day]
    if upcoming:
        ahead = next_sessions(day, FOMC_HORIZON)
        if upcoming[0] in ahead:
            features["fomc_in_sessions"] = float(ahead.index(upcoming[0]) + 1)
    return features


def build_calendar_panel(source: PricePanel, base: list[str] | None = None,
                         fomc_days: list[str] | None = None
                         ) -> tuple[PricePanel, dict[str, Any]]:
    """Copy the base symbols, add overnight-leg indexes and calendar features."""
    base = list(base or CALENDAR_BASE)
    fomc_days = sorted(fomc_days or [])
    feature_cache: dict[str, dict[str, float]] = {}
    rows = []
    for symbol in base:
        level, previous_close = 100.0, None
        for day in source.dates_for(symbol):
            bar = source.bars[(day, symbol)]
            if day not in feature_cache:
                feature_cache[day] = calendar_features(day, fomc_days)
            features = feature_cache[day]
            rows.append({"date": day, "symbol": symbol, **bar, **features})
            open_adjusted = source.adjusted(day, symbol, "open")
            close_adjusted = bar["adj_close"]
            if previous_close is not None and previous_close > 0 and open_adjusted > 0:
                level *= open_adjusted / previous_close
            previous_close = close_adjusted
            rows.append({"date": day, "symbol": symbol + OVERNIGHT_SUFFIX, "open": level,
                         "high": level, "low": level, "close": level, "adj_close": level,
                         "volume": bar["volume"], **features})
    provenance = {
        "derivation": "base symbols copied; <SYMBOL>_ON is an overnight-leg index: "
                      "ON(d+1) = ON(d) * adj_open(d+1) / adj_close(d), flat intraday",
        "caveats": [
            "open prices are consolidated opening prints, not executable MOO fills",
            "the overnight leg includes ex-dividend gaps through the adjusted basis",
            "holding <SYMBOL>_ON from open(d) to open(d+1) represents a MOC buy on d and "
            "a MOO sell on d+1; the Book charges both fills",
        ],
    }
    return PricePanel(rows), provenance
