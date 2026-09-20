"""Gate A v3 primitive-level red discriminants.

These tests are intentionally added before production fixes. Each test keeps
calling the primitive or durable authority surface named in its own test name.
Do not redirect these tests to a safer wrapper to obtain green.
"""

from __future__ import annotations

from datetime import date
import unittest

from quant.dataplane.sec.audit import (
    RESOLVED_BY_ATTEMPT,
    UNEXPLAINED,
    _obligations_from,
    _resolve_attempts,
    audit_observation_window,
)
from quant.dataplane.sec.store import SecStorageFailure
from quant.state import append_jsonl, read_jsonl, write_json
from tests import test_sec_form4_capture as sec_capture_tests


class GateAV3PrimitiveRedTests(unittest.TestCase):
    def _case(self):
        case = sec_capture_tests.RodageFalsificationTests(methodName="runTest")
        case.setUp()
        self.addCleanup(case.doCleanups)
        return case

    def _qualifying_baseline(self):
        case = self._case()
        collector = case.qualifying_collector(case.fixture_router())
        collector.record_service_start()
        collector.poll()
        collector.drain(max_items=3)
        report = audit_observation_window(collector, now=case.timebase.now())
        self.assertTrue(report["accountable"], report["findings"])
        return case, collector

    def test_direct_reconcile_before_settlement_emits_no_request(self):
        """public reconcile() itself must enforce the source-calendar boundary."""
        case = self._case()
        collector = case.collector(case.fixture_router())
        requested_before = list(case.transport.requested)

        result = collector.reconcile(date(2026, 9, 18))

        self.assertFalse(result["reconciled"])
        self.assertEqual(result["result_state"], "RECONCILIATION_NOT_DUE")
        self.assertEqual(
            case.transport.requested,
            requested_before,
            "direct reconcile() emitted an early SEC request",
        )

    def test_direct_poll_from_unattested_process_invalidates_qualifying_window(self):
        """direct collector.poll() must not outrank qualifying mutation authority."""
        case, collector = self._qualifying_baseline()

        case.timebase.advance(10)
        collector.lifecycle["qualifying_service_mode"] = False
        collector.lifecycle["lifecycle_cause"] = "LIFECYCLE_CAUSE_UNATTESTED"
        collector.lifecycle["service_managed"] = False
        collector.poll()

        report = audit_observation_window(collector, now=case.timebase.now())
        self.assertFalse(
            report["accountable"],
            "direct collector.poll() from an unattested process silently "
            "superseded qualifying work",
        )

    def test_direct_drain_from_unattested_process_invalidates_qualifying_window(self):
        """direct collector.drain() must share the qualifying authority boundary."""
        case = self._case()
        collector = case.qualifying_collector(case.fixture_router())
        collector.record_service_start()
        collector.poll()
        baseline = audit_observation_window(collector, now=case.timebase.now())
        self.assertTrue(baseline["accountable"], baseline["findings"])
        self.assertTrue(collector.state.pending_tasks)

        collector.lifecycle["qualifying_service_mode"] = False
        collector.lifecycle["lifecycle_cause"] = "LIFECYCLE_CAUSE_UNATTESTED"
        collector.lifecycle["service_managed"] = False
        collector.drain(max_items=1)

        report = audit_observation_window(collector, now=case.timebase.now())
        self.assertFalse(
            report["accountable"],
            "direct collector.drain() from an unattested process mutated "
            "qualifying state without durable intervention provenance",
        )

    def test_omitted_due_daily_reconciliation_cannot_audit_accountable(self):
        """Discovery cadence cannot hide an omitted, independently due reconciliation."""
        case, collector = self._qualifying_baseline()

        # Compress wall-clock cost without weakening the v2 accounting path:
        # each poll is 180s after its 60s due time, exactly the audit tolerance.
        # The virtual interval remains 44h and the primitive remains poll().
        for _ in range(44 * 15):
            case.timebase.advance(240)
            collector.poll()

        due = collector.reconciliation_due()
        self.assertIsNotNone(due, "the source calendar must say reconciliation is due")
        report = audit_observation_window(collector, now=case.timebase.now())
        self.assertFalse(
            report["accountable"],
            "Clock can omit the entire reconciliation action class while the "
            f"proof layer still passes; due={due}, findings={report['findings']}",
        )

    def test_reconcile_attempt_cannot_retire_discovery_poll_obligation(self):
        """The audit matcher must bind obligation identity and required action kind."""
        due = "2026-09-18T12:01:00+00:00"
        transitions = [{
            "transition_id": "T-POLL",
            "recorded_at_utc": "2026-09-18T12:00:00+00:00",
            "state": "AWAITING_POLL",
            "cause": "POLL_COMPLETED",
            "next_due_at_utc": due,
            "acquisition_critical_fingerprint": "sha256:" + "1" * 64,
            "obligation_id": "OB-POLL",
            "required_action_kind": "DISCOVERY",
        }]
        obligations, missing = _obligations_from(transitions)
        self.assertEqual(missing, [])
        wrong = [{
            "attempt_id": "A-WRONG",
            "attempt_kind": "RECONCILE",
            "obligation_id": "OB-POLL",
            "request_attempted_at_utc": due,
        }]
        _resolve_attempts(obligations, wrong, tolerance=180.0)
        self.assertEqual(
            obligations[0].status,
            UNEXPLAINED,
            "a RECONCILE attempt retired an obligation requiring DISCOVERY",
        )

        right = [{
            "attempt_id": "A-RIGHT",
            "attempt_kind": "DISCOVERY",
            "obligation_id": "OB-POLL",
            "request_attempted_at_utc": due,
        }]
        _resolve_attempts(obligations, right, tolerance=180.0)
        self.assertEqual(obligations[0].status, RESOLVED_BY_ATTEMPT)

    def test_missing_referenced_raw_object_fails_verification_and_audit(self):
        """Deleting a durably referenced raw object must be detectable."""
        case, collector = self._qualifying_baseline()
        object_id = collector.store.raw_manifest()[0]["raw_object_sha256"]
        collector.store.object_path(object_id).unlink()

        broken = collector.store.verify_objects()
        report = audit_observation_window(collector, now=case.timebase.now())
        self.assertIn(
            object_id,
            broken,
            f"verify_objects() ignored a missing durable reference; audit={report}",
        )
        self.assertFalse(
            report["accountable"],
            "retrospective audit ignored a missing referenced raw object",
        )

    def test_stopped_supervisor_with_pending_obligation_is_not_accountable(self):
        """Terminal supervisor evidence must override historical launch evidence."""
        case, collector = self._qualifying_baseline()
        lifecycle = collector.lifecycle
        append_jsonl(collector.paths.sec / "supervisor_events.jsonl", {
            "event": "CHILD_EXIT_OBSERVED",
            "recorded_at_utc": case.timebase.now_iso(),
            "supervisor_id": lifecycle.get("supervisor_id"),
            "child_boot_id": lifecycle.get("boot_id"),
            "fingerprint": collector.fingerprint,
            "exit_code": 0,
            "stopped_by_supervisor": True,
            "unexpected_termination": False,
        })
        write_json(collector.paths.sec / "supervisor_state.json", {
            "schema": "p0_supervisor/v2",
            "supervisor_id": lifecycle.get("supervisor_id"),
            "child_boot_id": lifecycle.get("boot_id"),
            "supervisor_invocation_id": lifecycle.get("service_invocation_id"),
            "lifecycle_cause": lifecycle.get("lifecycle_cause"),
            "fingerprint": collector.fingerprint,
            "supervisor_running": False,
            "service_managed": True,
            "qualifying_mode": True,
            "deployment_authority_nonce": lifecycle.get("launch_authority_nonce"),
            "last_child_exit_code": 0,
            "last_child_exit_at_utc": case.timebase.now_iso(),
            "supervisor_exited_at_utc": case.timebase.now_iso(),
        })

        report = audit_observation_window(collector, now=case.timebase.now())
        self.assertTrue(report["obligations_pending"])
        self.assertFalse(
            report["accountable"],
            "historical launch evidence hid the durable terminal supervisor state",
        )

    def test_t0_between_ticks_preserves_pre_t0_baseline_lifecycle(self):
        """Structural validation must retain the lifecycle active immediately before t0."""
        case, collector = self._qualifying_baseline()

        case.timebase.advance(30)
        t0 = case.timebase.now()
        case.timebase.advance(30)
        collector.poll()

        report = audit_observation_window(
            collector, now=case.timebase.now(), window_start=t0
        )
        self.assertTrue(
            report["accountable"],
            "pre-t0 baseline lifecycle was discarded by structural validation: "
            f"{report['findings']}",
        )

    def test_direct_fingerprint_rematerialization_is_not_silent(self):
        """materialize_fingerprint() must reject or provenance a qualifying mutation."""
        case, collector = self._qualifying_baseline()
        before_rows = list(read_jsonl(collector.paths.sec_lifecycle))
        before_bytes = collector.paths.sec_fingerprint.read_bytes()
        collector.paths.sec_fingerprint.unlink()
        case.timebase.advance(1)

        try:
            collector.materialize_fingerprint()
        except (SecStorageFailure, PermissionError):
            return

        after_rows = list(read_jsonl(collector.paths.sec_lifecycle))
        after_bytes = collector.paths.sec_fingerprint.read_bytes()
        report = audit_observation_window(collector, now=case.timebase.now())
        self.assertNotEqual(before_bytes, after_bytes)
        self.assertGreater(
            len(after_rows),
            len(before_rows),
            "direct fingerprint rematerialization mutated qualifying state "
            "without durable intervention provenance",
        )
        self.assertFalse(report["accountable"])

    def test_direct_clear_cooldown_is_rejected_or_provenanced(self):
        """SecTrafficBudget.clear_cooldown() cannot silently mutate qualifying state."""
        case, collector = self._qualifying_baseline()
        collector.budget.enter_cooldown(300.0, "synthetic_gate_a_v3")
        before = collector.budget.load().to_dict()
        before_rows = list(read_jsonl(collector.paths.sec_lifecycle))

        try:
            collector.budget.clear_cooldown()
        except (SecStorageFailure, PermissionError, RuntimeError):
            return

        after = collector.budget.load().to_dict()
        after_rows = list(read_jsonl(collector.paths.sec_lifecycle))
        changed = after != before
        self.assertTrue(changed, "test setup expected clear_cooldown() to mutate state")
        self.assertGreater(
            len(after_rows),
            len(before_rows),
            "direct clear_cooldown() changed durable budget state without provenance",
        )
        report = audit_observation_window(collector, now=case.timebase.now())
        self.assertFalse(report["accountable"])


if __name__ == "__main__":
    unittest.main()
