"""A2/mission calendar matrix: weekday/weekend/holiday/unbound-year + 404!=holiday.

Calls the frozen calendar authority (``src/quant/dataplane/sec/calendar.py``)
and a real ``SecForm4Collector`` (via ``SyntheticEnvironment``) directly.
Cites existing discriminating tests for properties already proven; adds one
direct end-to-end check that a missing daily index on an actual business day
is never treated as a holiday.
"""

from __future__ import annotations

import json
import sys
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quant.dataplane.sec.calendar import (  # noqa: E402
    EdgarCalendarUnbound, edgar_closed_dates, is_edgar_business_day)
from quant.dataplane.sec.collector import DAILY_INDEX_UNAVAILABLE  # noqa: E402

from common.evidence import EvidenceRecord, Report, git_head_sha  # noqa: E402
from common.synthetic import SyntheticEnvironment, daily_index_router, empty_atom_feed  # noqa: E402


def _test_exists(dotted_name: str) -> bool:
    try:
        suite = unittest.TestLoader().loadTestsFromName(dotted_name)
    except (ImportError, AttributeError):
        return False
    return suite.countTestCases() >= 1


CITATIONS = {
    "weekend_never_reconciliation_target": (
        "tests.test_p0_continuity_compression.CalendarBoundaryCompressionTests"
        ".test_friday_weekend_monday_reconciliation_boundary",),
    "known_federal_holiday_not_reconciliation_target": (
        "tests.test_p0_continuity_compression.CalendarBoundaryCompressionTests"
        ".test_known_sec_federal_holiday_is_not_a_reconciliation_target",),
    "unbound_calendar_year_fails_closed": (
        "tests.test_p0_continuity_compression.CalendarBoundaryCompressionTests"
        ".test_unbound_calendar_year_fails_closed",),
    "business_day_independent_of_http_outcome": (
        "tests.test_p0_continuity_compression.CalendarBoundaryCompressionTests"
        ".test_business_day_stays_business_day_independent_of_http_outcome",),
    "dst_spring_boundary": (
        "tests.test_p0_continuity_compression.CalendarBoundaryCompressionTests"
        ".test_spring_dst_does_not_shorten_30_elapsed_hours",),
    "dst_fall_boundary": (
        "tests.test_p0_continuity_compression.CalendarBoundaryCompressionTests"
        ".test_fall_dst_does_not_lengthen_30_elapsed_hours",),
}


def _cite(report: Report, exact_sha: str, name: str) -> None:
    citations = CITATIONS[name]
    missing = [dotted for dotted in citations if not _test_exists(dotted)]
    defect = "MISSING_PROOF" if missing else "NON_ISSUE"
    detail = f"cited {citations}" + (f"; stale: {missing}" if missing else "")
    report.add(EvidenceRecord(
        property_name=f"calendar:{name}", classification="FACT" if not missing else "CLAIM",
        defect_class=defect, domain="REPOSITORY", exact_sha=exact_sha, detail=detail,
        reproduce_command=f"PYTHONPATH=src python3 -m unittest {citations[0]} -v"))


def _classify_dates(report: Report, exact_sha: str) -> None:
    samples = {
        "ordinary_weekday": date(2026, 9, 22),   # Tuesday
        "friday": date(2026, 9, 18),
        "saturday": date(2026, 9, 19),
        "sunday": date(2026, 9, 20),
        "monday": date(2026, 9, 21),
        "known_2026_thanksgiving_holiday": date(2026, 11, 26),
    }
    expected_business = {
        "ordinary_weekday": True, "friday": True, "saturday": False,
        "sunday": False, "monday": True, "known_2026_thanksgiving_holiday": False,
    }
    for label, day in samples.items():
        actual = is_edgar_business_day(day)
        ok = actual == expected_business[label]
        report.add(EvidenceRecord(
            property_name=f"calendar:date_classification:{label}",
            classification="FACT", defect_class="NON_ISSUE" if ok else "REAL_DEFECT",
            domain="REPOSITORY", exact_sha=exact_sha,
            detail=f"{day.isoformat()} ({day.strftime('%A')}) is_edgar_business_day={actual}",
            reproduce_command=(
                "PYTHONPATH=src python3 -c \""
                f"from quant.dataplane.sec.calendar import is_edgar_business_day; "
                f"from datetime import date; "
                f"print(is_edgar_business_day(date({day.year},{day.month},{day.day})))\"")))

    holidays_2026 = sorted(edgar_closed_dates(2026))
    report.body["edgar_closed_dates_2026"] = [d.isoformat() for d in holidays_2026]
    report.add(EvidenceRecord(
        property_name="calendar:2026_closure_count", classification="FACT",
        defect_class="NON_ISSUE", domain="REPOSITORY", exact_sha=exact_sha,
        detail=f"{len(holidays_2026)} official 2026 EDGAR closures bound"))

    try:
        edgar_closed_dates(2027)
        unbound_fails_closed = False
    except EdgarCalendarUnbound:
        unbound_fails_closed = True
    report.add(EvidenceRecord(
        property_name="calendar:unbound_future_year_fails_closed", classification="FACT",
        defect_class="NON_ISSUE" if unbound_fails_closed else "REAL_DEFECT",
        domain="REPOSITORY", exact_sha=exact_sha,
        detail=f"edgar_closed_dates(2027) raised EdgarCalendarUnbound={unbound_fails_closed}"))


def _404_is_never_a_holiday(report: Report, exact_sha: str) -> None:
    """A business-day daily-index 404 must open DAILY_INDEX_UNAVAILABLE, never
    be treated as source-normal silence or as reconciled/coverage-complete."""
    business_day = date(2026, 9, 22)  # ordinary Tuesday, ordinary business day
    assert is_edgar_business_day(business_day)
    start = datetime(2026, 9, 21, 12, 0, 0, tzinfo=timezone.utc)  # Monday noon
    settled_instant = datetime(2026, 9, 24, 4, 0, 0, tzinfo=timezone.utc)  # past 30h settle

    with SyntheticEnvironment(start=start) as env:
        atom = empty_atom_feed()
        handler = daily_index_router(atom, index_body=None, index_status=404)
        collector, _transport = env.collector(handler)
        collector.poll()  # bootstraps state.bootstrap_started_at_utc
        env.timebase.advance((settled_instant - env.timebase.now()).total_seconds())

        due = collector.reconciliation_due()
        outcome = collector.reconcile(due) if due is not None else None
        gap_kinds = sorted({gap["kind"] for gap in collector.state.open_gaps})
        reconciled = business_day.isoformat() in collector.state.reconciled_days
        classified_as_holiday = due is None  # would mean the 404 suppressed the obligation

        defect = "NON_ISSUE"
        if classified_as_holiday or reconciled or DAILY_INDEX_UNAVAILABLE not in gap_kinds:
            defect = "REAL_DEFECT"
        report.add(EvidenceRecord(
            property_name="calendar:business_day_404_is_never_a_holiday",
            classification="FACT", defect_class=defect, domain="REPOSITORY",
            exact_sha=exact_sha,
            detail=(f"due={due} outcome_result_state={(outcome or {}).get('result_state')} "
                    f"gap_kinds={gap_kinds} reconciled={reconciled}"),
            reproduce_command=(
                "PYTHONPATH=. python3 -m tools.p0_qualification.gate_a.calendar_matrix")))


def run(exact_sha: str | None = None) -> dict:
    exact_sha = exact_sha or git_head_sha()
    report = Report(gate="GATE_A_CALENDAR_MATRIX", exact_sha=exact_sha)
    _classify_dates(report, exact_sha)
    for name in CITATIONS:
        _cite(report, exact_sha, name)
    _404_is_never_a_holiday(report, exact_sha)
    return report.write(REPO_ROOT / "tools" / "p0_qualification" / "evidence" / "gate_a"
                        / "calendar_matrix.json")


if __name__ == "__main__":
    result = run()
    print(json.dumps({"gate": result["gate"], "records": len(result["records"]),
                      "report_digest": result["report_digest"]}, indent=2))
