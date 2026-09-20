"""Independent Gate-A-v2 red-team discriminant for action binding.

This file lives only on the audit branch.  It asserts a property the frozen
candidate must prove; failure is red-team evidence, not a production change.
"""

from __future__ import annotations

import unittest
from datetime import date

from quant.dataplane.sec.audit import audit_observation_window
from tests import test_sec_form4_capture as sec_capture_tests


class GateAV2AttemptActionBindingRed(unittest.TestCase):
    def _qualifying_case(self):
        case = sec_capture_tests.RodageFalsificationTests()
        case.setUp()
        self.addCleanup(case.doCleanups)
        return case

    def test_reconcile_attempt_cannot_retire_a_discovery_poll_obligation(self):
        """One obligation must be resolved by the action it actually required.

        The scheduler has an AWAITING_POLL obligation due at t+60s.  Instead of
        issuing the due discovery request, call the still-public lower-level
        reconcile primitive at exactly that deadline.  The resulting SEC request
        carries the same obligation_id, but its durable attempt_kind is
        RECONCILE.  A correct audit must reject that type mismatch rather than
        treating any request with the right id/time as proof the poll happened.
        """
        case = self._qualifying_case()
        index = b"""Description: synthetic red-team daily index
CIK|Company Name|Form Type|Date Filed|Filename
--------------------------------------------------------------------------------
320193|A|4|2026-09-17|edgar/data/320193/0000320193-26-000045.txt
789019|B|4|2026-09-17|edgar/data/789019/0000789019-26-000112.txt
1018724|C|4/A|2026-09-17|edgar/data/1018724/0001018724-26-000301.txt
"""
        collector = case.qualifying_collector(case.fixture_router(index=index))
        collector.record_service_start()
        collector.poll()
        collector.drain(max_items=3)
        baseline = audit_observation_window(collector, now=case.timebase.now())
        self.assertTrue(baseline["accountable"], baseline["findings"])

        poll_obligation = collector.state.open_obligation_id
        transition = next(
            row for row in collector.scheduler.all()
            if row.get("obligation_id") == poll_obligation
        )
        self.assertEqual(transition["state"], "AWAITING_POLL")

        case.timebase.advance(60)
        result = collector.reconcile(date(2026, 9, 17))
        self.assertTrue(result["reconciled"])

        bound_attempt = [
            row for row in collector.store.attempts()
            if row.get("obligation_id") == poll_obligation
        ][-1]
        self.assertEqual(bound_attempt["attempt_kind"], "RECONCILE")

        report = audit_observation_window(collector, now=case.timebase.now())
        self.assertFalse(
            report["accountable"],
            "sec-audit accepted a RECONCILE request as resolution of an "
            "AWAITING_POLL obligation because attempt_kind is not bound to the "
            "obligation's required action",
        )


if __name__ == "__main__":
    unittest.main()
