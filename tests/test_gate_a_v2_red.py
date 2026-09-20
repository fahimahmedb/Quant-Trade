"""Independent Gate-A-v2 red-team discriminants.

These tests live only on the audit branch.  They deliberately assert the
property the frozen candidate must prove, so a failure is evidence against the
candidate rather than a request to mutate it.
"""

from __future__ import annotations

import unittest
from datetime import date

from quant.dataplane.sec.audit import audit_observation_window
from tests.test_sec_form4_capture import RodageFalsificationTests, build_feed


class GateAV2ReconciliationAuditRed(unittest.TestCase):
    def _qualifying_case(self):
        case = RodageFalsificationTests()
        case.setUp()
        self.addCleanup(case.doCleanups)
        return case

    def test_due_reconciliation_cannot_be_omitted_while_audit_stays_accountable(self):
        """Normal 60s discovery polls must not hide an omitted daily reconciliation.

        Start Friday 2026-09-18 12:00 UTC.  Friday's EDGAR day settles exactly
        44 elapsed hours later (22:00 ET close + 30h).  We keep satisfying every
        discovery poll obligation at the real 60s cadence but deliberately omit
        reconciliation.  At the end the source-calendar obligation is due, so a
        retrospective audit that claims complete acquisition accountability must
        fail rather than infer "nothing else was due" from the scheduler journal.
        """
        case = self._qualifying_case()
        empty_feed = build_feed([], entries=[])
        collector = case.qualifying_collector(
            case.fixture_router(atom=empty_feed),
        )
        collector.record_service_start()
        collector.poll()
        self.assertTrue(audit_observation_window(collector)["accountable"])

        for _ in range(44 * 60):
            case.timebase.advance(60)
            collector.poll()

        self.assertEqual(collector.reconciliation_due(), date(2026, 9, 18))
        self.assertNotIn("2026-09-18", collector.state.reconciled_days)

        report = audit_observation_window(collector)
        self.assertFalse(
            report["accountable"],
            "a due source-calendar reconciliation was omitted, but sec-audit "
            "reported accountable=True because reconciliation obligations are "
            "not independently derived from the calendar",
        )


if __name__ == "__main__":
    unittest.main()
