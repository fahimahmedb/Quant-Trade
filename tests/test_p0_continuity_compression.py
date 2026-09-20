"""Blue P0 continuity-compression discriminants.

These tests do not claim target-host or live-source proof. They exercise the
calendar branches that a long passive P14D window was partly intended to cover,
using the production collector with its injectable timebase.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

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

        # Tuesday 18:00 UTC => cutoff Monday 12:00 UTC. Monday is now settled.
        self.timebase.advance(24 * 60 * 60)
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

    def test_virtual_p14d_horizon_has_no_hidden_calendar_state(self) -> None:
        """The former 14-day horizon reduces to settled weekdays under exact logic."""
        start = datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)
        collector = self._collector_starting(start)

        self.timebase.advance(14 * 24 * 60 * 60)
        cutoff = (self.timebase.now() - timedelta(hours=30)).date()

        observed: list[date] = []
        while True:
            due = collector.reconciliation_due()
            if due is None:
                break
            observed.append(due)
            collector.state.reconciled_days.append(due.isoformat())
            collector.save()

        expected: list[date] = []
        day = start.date()
        while day <= cutoff:
            if day.weekday() < 5:
                expected.append(day)
            day += timedelta(days=1)

        self.assertEqual(observed, expected)
        self.assertTrue(observed)
        self.assertTrue(all(day.weekday() < 5 for day in observed))
        self.assertIsNone(collector.reconciliation_due())


if __name__ == "__main__":
    import unittest
    unittest.main()
