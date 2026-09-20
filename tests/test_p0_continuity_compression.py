"""Blue P0 continuity-compression discriminants.

These tests do not claim target-host or live-source proof. They exercise the
calendar branches that a long passive P14D window was partly intended to cover,
using the production collector with its injectable timebase.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

from zoneinfo import ZoneInfo

from quant.dataplane.sec.calendar import EdgarCalendarUnbound, is_edgar_business_day
from quant.dataplane.sec.timebase import FrozenTimebase
from tests.test_sec_form4_capture import CollectorTestCase


class CalendarBoundaryCompressionTests(CollectorTestCase):
    def _collector_starting(self, when: datetime):
        self.timebase = FrozenTimebase(when)
        return self.collector(self.fixture_router())

    def test_friday_weekend_monday_reconciliation_boundary(self) -> None:
        """30h settle makes Friday due; weekend days never become targets."""
        friday = datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)
        collector = self._collector_starting(friday)

        self.assertIsNone(collector.reconciliation_due())

        # Monday 18:00 UTC => cutoff Sunday 12:00 UTC. Friday is now the
        # oldest settled business day; Saturday/Sunday are not targets.
        self.timebase.advance(78 * 60 * 60)
        self.assertEqual(collector.reconciliation_due(), date(2026, 9, 18))

        collector.state.reconciled_days.append("2026-09-18")
        collector.save()
        self.assertIsNone(
            collector.reconciliation_due(),
            "weekend dates must not become daily-index reconciliation obligations",
        )

        # Monday closes Tuesday 02:00 UTC (22:00 ET); +30 elapsed hours
        # is Wednesday 08:00 UTC, 38h after the Monday-18:00 point above.
        self.timebase.advance(38 * 60 * 60)
        self.assertEqual(collector.reconciliation_due(), date(2026, 9, 21))

    def test_settle_delay_is_measured_after_edgar_close_not_utc_date_start(self) -> None:
        """Friday is not settled until 30h after the 22:00 ET EDGAR close."""
        friday = datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)
        collector = self._collector_starting(friday)

        # On 2026-09-18 New York is UTC-4. EDGAR closes Friday at 22:00 ET,
        # i.e. Saturday 02:00 UTC. Thirty hours later is Sunday 08:00 UTC.
        self.timebase.advance((44 * 60 * 60) - 1)
        self.assertIsNone(
            collector.reconciliation_due(),
            "a calendar-date truncation must not spend the 30h settle buffer early",
        )

        self.timebase.advance(1)
        self.assertEqual(collector.reconciliation_due(), date(2026, 9, 18))

    def test_bootstrap_day_is_the_edgar_eastern_business_date(self) -> None:
        """A 01:00 UTC bootstrap still belongs to the prior EDGAR business day."""
        # 2026-09-22 01:00 UTC is 2026-09-21 21:00 EDT, one hour before close.
        start = datetime(2026, 9, 22, 1, 0, tzinfo=timezone.utc)
        collector = self._collector_starting(start)

        # Monday closes at Tuesday 02:00 UTC; +30h => Wednesday 08:00 UTC.
        self.timebase.advance((31 * 60 * 60) + 1)
        self.assertEqual(
            collector.reconciliation_due(),
            date(2026, 9, 21),
            "bootstrap source day must be derived in America/New_York, not UTC",
        )

    def test_known_sec_federal_holiday_is_not_a_reconciliation_target(self) -> None:
        """Labor Day is source-normal silence, not a missing daily index."""
        labor_day = datetime(2026, 9, 7, 12, 0, tzinfo=timezone.utc)
        collector = self._collector_starting(labor_day)

        # 44h later is Wednesday 08:00 UTC. If Monday were an ordinary EDGAR
        # business day, its 22:00 ET close + 30h settle horizon would just have
        # elapsed. The official SEC calendar says 2026-09-07 is a federal
        # holiday, so there must be no reconciliation obligation for that date.
        self.timebase.advance(44 * 60 * 60)
        self.assertIsNone(
            collector.reconciliation_due(),
            "a known SEC holiday must not be converted into DAILY_INDEX_UNAVAILABLE work",
        )

        # Tuesday 2026-09-08 is the next EDGAR business day. Its 22:00 ET close
        # + 30 elapsed hours lands at Thursday 08:00 UTC.
        self.timebase.advance(24 * 60 * 60)
        self.assertEqual(collector.reconciliation_due(), date(2026, 9, 8))

    def test_unbound_calendar_year_fails_closed(self) -> None:
        """A future year is never guessed from weekday arithmetic."""
        with self.assertRaises(EdgarCalendarUnbound):
            is_edgar_business_day(date(2027, 1, 4))

    def test_business_day_stays_business_day_independent_of_http_outcome(self) -> None:
        """Only the bound calendar, never an observed 404, defines a holiday."""
        self.assertTrue(is_edgar_business_day(date(2026, 9, 8)))
        self.assertFalse(is_edgar_business_day(date(2026, 9, 7)))

    def test_spring_dst_does_not_shorten_30_elapsed_hours(self) -> None:
        """The spring clock jump cannot spend one hour of the settle buffer."""
        start = datetime(2026, 3, 6, 12, 0, tzinfo=timezone.utc)
        collector = self._collector_starting(start)

        # Friday 22:00 EST == Saturday 03:00 UTC. +30 real hours == Sunday
        # 09:00 UTC, even though New York jumps from 01:59 to 03:00 meanwhile.
        self.timebase.advance((45 * 60 * 60) - 1)
        self.assertIsNone(collector.reconciliation_due())
        self.timebase.advance(1)
        self.assertEqual(collector.reconciliation_due(), date(2026, 3, 6))

    def test_fall_dst_does_not_lengthen_30_elapsed_hours(self) -> None:
        """The repeated fall-back hour cannot add one hour to the settle buffer."""
        start = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)
        collector = self._collector_starting(start)

        # Friday 22:00 EDT == Saturday 02:00 UTC. +30 real hours == Sunday
        # 08:00 UTC, even though New York repeats the 01:00 hour meanwhile.
        self.timebase.advance((44 * 60 * 60) - 1)
        self.assertIsNone(collector.reconciliation_due())
        self.timebase.advance(1)
        self.assertEqual(collector.reconciliation_due(), date(2026, 10, 30))

    def test_direct_reconcile_before_settlement_emits_no_request(self) -> None:
        """Manual reconciliation cannot bypass the same source-calendar gate."""
        friday = datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)
        collector = self._collector_starting(friday)
        requested_before = list(self.transport.requested)

        result = collector.reconcile_due(date(2026, 9, 18))

        self.assertFalse(result["reconciled"])
        self.assertEqual(result["result_state"], "RECONCILIATION_NOT_DUE")
        self.assertEqual(
            self.transport.requested,
            requested_before,
            "an explicit --day must not emit an early SEC request",
        )
        self.assertNotIn("2026-09-18", collector.state.reconciled_days)

    def test_cli_reconcile_before_settlement_emits_no_request(self) -> None:
        """The real sec-reconcile --day CLI must use the same due boundary."""
        import contextlib
        import importlib.util
        import io
        from types import SimpleNamespace
        from pathlib import Path

        friday = datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)
        collector = self._collector_starting(friday)
        requested_before = list(self.transport.requested)

        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location(
            "quant_cli_direct_reconcile", root / "scripts" / "quant.py")
        cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
        args = SimpleNamespace(command="sec-reconcile", day="2026-09-18")
        components = SimpleNamespace(set=lambda *args, **kwargs: None)

        with contextlib.redirect_stdout(io.StringIO()):
            rc = cli.sec_command(SimpleNamespace(sec=collector, components=components), args)

        self.assertEqual(rc, 0)
        self.assertEqual(self.transport.requested, requested_before)
        self.assertNotIn("2026-09-18", collector.state.reconciled_days)

    def test_direct_reconcile_cannot_skip_oldest_due_day(self) -> None:
        """Explicit --day cannot jump over an older due reconciliation obligation."""
        start = datetime(2026, 9, 16, 12, 0, tzinfo=timezone.utc)
        collector = self._collector_starting(start)
        self.timebase.advance(4 * 24 * 60 * 60)
        requested_before = list(self.transport.requested)

        self.assertEqual(collector.reconciliation_due(), date(2026, 9, 16))
        result = collector.reconcile_due(date(2026, 9, 17))

        self.assertEqual(result["result_state"], "RECONCILIATION_NOT_DUE")
        self.assertFalse(result["reconciled"])
        self.assertEqual(self.transport.requested, requested_before)

    def test_virtual_p14d_horizon_has_no_hidden_calendar_state(self) -> None:
        """The former 14-day horizon reduces to settled weekdays under exact logic."""
        start = datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)
        collector = self._collector_starting(start)

        self.timebase.advance(14 * 24 * 60 * 60)
        now_utc = self.timebase.now().astimezone(timezone.utc)
        edgar_tz = ZoneInfo("America/New_York")

        observed: list[date] = []
        while True:
            due = collector.reconciliation_due()
            if due is None:
                break
            observed.append(due)
            collector.state.reconciled_days.append(due.isoformat())
            collector.save()

        # Independent oracle: source date is Eastern Time and each weekday is
        # eligible only 30 real hours after its 22:00 ET close. Do not reuse
        # the production helper or the former UTC-date cutoff.
        expected: list[date] = []
        day = start.astimezone(edgar_tz).date()
        final_day = self.timebase.now().astimezone(edgar_tz).date()
        while day <= final_day:
            close_local = datetime.combine(day, time(hour=22), tzinfo=edgar_tz)
            settled_utc = close_local.astimezone(timezone.utc) + timedelta(hours=30)
            if day.weekday() < 5 and now_utc >= settled_utc:
                expected.append(day)
            day += timedelta(days=1)

        self.assertEqual(observed, expected)
        self.assertTrue(observed)
        self.assertTrue(all(day.weekday() < 5 for day in observed))
        self.assertIsNone(collector.reconciliation_due())


if __name__ == "__main__":
    import unittest
    unittest.main()
