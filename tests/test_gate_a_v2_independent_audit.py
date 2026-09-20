"""Independent red discriminants for the frozen Gate A v2 candidate.

These tests intentionally encode properties the candidate must satisfy to earn a
repository-side Gate A PASS.  The branch is audit-only and is rooted at the
frozen candidate SHA; production code is not modified here.
"""

from __future__ import annotations

import unittest

from quant.dataplane.sec.audit import audit_observation_window
from tests.test_sec_form4_capture import RodageFalsificationTests


class GateAV2IndependentAuditRedTests(unittest.TestCase):
    def _rodage_case(self) -> RodageFalsificationTests:
        case = RodageFalsificationTests(methodName="runTest")
        case.setUp()
        self.addCleanup(case.doCleanups)
        return case

    def test_omitted_due_daily_reconciliation_cannot_audit_accountable(self) -> None:
        """Continuous discovery polls must not hide a due reconciliation omission."""
        case = self._rodage_case()
        collector = case.qualifying_collector(case.fixture_router())
        collector.record_service_start()
        collector.poll()
        collector.drain(max_items=3)

        # Keep satisfying the discovery cadence for 44 virtual hours, but
        # deliberately never invoke reconciliation.  Starting Friday 12:00 UTC,
        # the Friday EDGAR business day becomes due exactly 44 hours later under
        # the frozen 22:00 ET close + 30 elapsed-hour rule.
        for _ in range(44 * 60):
            case.timebase.advance(60)
            collector.poll()

        self.assertIsNotNone(
            collector.reconciliation_due(),
            "the calendar must say a daily reconciliation is now due",
        )
        report = audit_observation_window(collector, now=case.timebase.now())
        self.assertFalse(
            report["accountable"],
            "an audit that derives obligations only from scheduler transitions "
            "must not silently miss an entire due action class",
        )

    def test_t0_between_ticks_preserves_pre_t0_lifecycle_and_supersession_context(self) -> None:
        """A healthy already-running service must be auditable when t0 is between ticks."""
        case = self._rodage_case()
        collector = case.qualifying_collector(case.fixture_router())
        collector.record_service_start()
        collector.poll()
        collector.drain(max_items=3)
        baseline = audit_observation_window(collector, now=case.timebase.now())
        self.assertTrue(baseline["accountable"], baseline["findings"])

        # Blue is allowed to declare a prospective t0 while the qualifying
        # service is already alive.  Put t0 halfway between 60-second ticks,
        # then execute the next normal poll.
        case.timebase.advance(30)
        t0 = case.timebase.now()
        case.timebase.advance(30)
        collector.poll()

        report = audit_observation_window(
            collector, now=case.timebase.now(), window_start=t0
        )
        self.assertTrue(
            report["accountable"],
            "window slicing must preserve the reference lifecycle and predecessor "
            f"obligation needed to validate the first in-window tick: {report['findings']}",
        )


if __name__ == "__main__":
    unittest.main()
