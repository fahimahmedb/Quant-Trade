"""Prospectively bound EDGAR business calendar for P0 reconciliation.

A missing daily-index response cannot be used to infer a holiday: doing so would
turn a source outage into false source-normal silence.  The dates here come from
the SEC's published EDGAR calendar and are acquisition-critical code, so any
change is fingerprinted and requires an explicit deployment event.

Only years explicitly bound here are authoritative.  Reconciliation fails
closed before entering an unbound year.
"""

from __future__ import annotations

from datetime import date
from typing import Final


class EdgarCalendarUnbound(RuntimeError):
    """No prospectively frozen SEC calendar exists for the requested year."""


EDGAR_CALENDAR_SOURCES: Final[tuple[dict[str, str], ...]] = (
    {
        "url": "https://www.sec.gov/submit-filings/filer-support-resources/edgar-calendar",
        "title": "SEC.gov | EDGAR Calendar",
        "reviewed_or_updated": "2026-04-28",
        "consulted_at_utc": "2026-09-20",
    },
)

# Dates on which the official SEC EDGAR calendar says the system will not
# receive, process, or accept filings in 2026.
EDGAR_CLOSED_DATES_BY_YEAR: Final[dict[int, frozenset[date]]] = {
    2026: frozenset({
        date(2026, 1, 1),
        date(2026, 1, 19),
        date(2026, 2, 16),
        date(2026, 5, 25),
        date(2026, 6, 19),
        date(2026, 7, 3),
        date(2026, 9, 7),
        date(2026, 10, 12),
        date(2026, 11, 11),
        date(2026, 11, 26),
        date(2026, 12, 25),
    }),
}


def edgar_closed_dates(year: int) -> frozenset[date]:
    """Return the frozen official closures for one explicitly bound year."""
    try:
        return EDGAR_CLOSED_DATES_BY_YEAR[year]
    except KeyError:
        raise EdgarCalendarUnbound(
            f"EDGAR_CALENDAR_YEAR_UNBOUND:{year}") from None


def is_edgar_business_day(day: date) -> bool:
    """Whether a date is eligible to have a normal EDGAR daily index."""
    closed = edgar_closed_dates(day.year)
    return day.weekday() < 5 and day not in closed
