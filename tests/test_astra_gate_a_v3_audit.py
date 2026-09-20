"""Independent Astra Gate A v3 audit reproductions.

Audit-only. Not part of the frozen candidate's own proof; these are Astra's
independent replay/attack evidence against candidate
2da079d8ad75c69eb3fc2990c512735cb4bdc02b. Nothing here modifies production
code. Where a probe found a real gap, the test documents what was and was not
actually reachable end-to-end, rather than asserting a conclusion the
reproduction does not support.
"""

from __future__ import annotations

import unittest

from quant.dataplane.sec.audit import audit_observation_window
from quant.dataplane.sec.collector import SecForm4Collector
from quant.dataplane.sec.budget import SecTrafficBudget
from quant.dataplane.sec.supervisor import AUTOMATIC_RESTART_AFTER_FAILURE
from quant.state import read_jsonl
from tests import test_sec_form4_capture as sec_capture_tests


class B2IndependentReplayTests(unittest.TestCase):
    """B2_OFFLINE_AUDIT_AUTHORITY: replay beyond the single canonical regression."""

    def _qualifying(self):
        case = sec_capture_tests.RodageFalsificationTests(methodName="runTest")
        case.setUp()
        self.addCleanup(case.doCleanups)
        collector = case.qualifying_collector(case.fixture_router())
        collector.record_service_start()
        collector.poll()
        collector.drain(max_items=3)
        self.assertTrue(audit_observation_window(collector)["accountable"])
        return case, collector

    def test_corrupted_authority_tail_fails_closed_under_offline_identity(self):
        """A tampered (not just missing) CHILD_LAUNCH_AUTHORIZED record must fail closed."""
        import json
        case, collector = self._qualifying()
        path = collector.paths.sec / "supervisor_events.jsonl"
        rows = list(read_jsonl(path))
        rows[-1]["fingerprint"] = "sha256:" + "0" * 64
        path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
        collector.lifecycle["qualifying_service_mode"] = False  # simulated offline auditor
        report = audit_observation_window(collector, now=case.timebase.now())
        self.assertIn("LIFECYCLE_EXTERNAL_AUTHORITY_MISMATCH", report["findings"])
        self.assertFalse(report["accountable"])

    def test_missing_deployment_authority_consumption_fails_closed(self):
        case, collector = self._qualifying()
        path = collector.paths.sec / "deployment_authorities.jsonl"
        self.assertTrue(path.exists())
        path.unlink()
        collector.lifecycle["qualifying_service_mode"] = False
        report = audit_observation_window(collector, now=case.timebase.now())
        self.assertIn("DEPLOYMENT_AUTHORITY_CONSUMPTION_MISSING", report["findings"])
        self.assertFalse(report["accountable"])

    def test_forged_automatic_restart_without_genuine_witness_fails_closed(self):
        case = sec_capture_tests.RodageFalsificationTests(methodName="runTest")
        case.setUp()
        self.addCleanup(case.doCleanups)
        router = case.fixture_router()
        first = case.qualifying_collector(router)
        first.record_service_start()
        first.poll()
        forged_restart = case.qualifying_collector(
            router, cause=AUTOMATIC_RESTART_AFTER_FAILURE, boot_id="boot-q2",
            witnessed_child_failure=False)
        forged_restart.record_service_start()
        report = audit_observation_window(forged_restart, now=case.timebase.now())
        self.assertIn("AUTOMATIC_RESTART_WITNESS_MISSING", report["findings"])
        self.assertFalse(report["accountable"])


class NewSurfaceProbeTests(unittest.TestCase):
    """Section-7 style probes. Neither reproduced an end-to-end false PASS, but
    each documents a real, narrow property of the candidate worth recording."""

    def test_disabled_lane_poll_still_emits_a_request_but_window_is_caught(self):
        """collector.poll() does not itself check state.enabled.

        A disabled lane's poll() still performs a live discovery request; this is
        NOT gated at the primitive. The window is nonetheless caught by the
        retrospective audit, because any DISABLED transition inside the audited
        window is unconditionally non-accountable. This is reported as an
        operational/design observation (primitive does not refuse; the audit
        catches it after the fact at the WINDOW level), not as a Gate A false
        pass, because accountable remained False end-to-end.
        """
        case = sec_capture_tests.RodageFalsificationTests(methodName="runTest")
        case.setUp()
        self.addCleanup(case.doCleanups)
        collector = case.qualifying_collector(case.fixture_router())
        collector.record_service_start()
        collector.poll()
        collector.disable("operator paused the lane")
        requested_before = len(collector.transport.requested)

        outcome = collector.poll()

        self.assertGreater(
            len(collector.transport.requested), requested_before,
            "poll() is not expected to be gated by state.enabled at the primitive; "
            "if this assertion ever fails, the primitive itself started refusing "
            "and the window-level ACQUISITION_DISABLED_DURING_WINDOW catch below "
            "would need re-verification against the new behaviour.")
        self.assertIsNotNone(outcome)
        report = audit_observation_window(collector, now=case.timebase.now())
        self.assertIn("ACQUISITION_DISABLED_DURING_WINDOW", report["findings"])
        self.assertFalse(
            report["accountable"],
            "a disabled-lane request must not be able to produce a clean window")

    def test_forged_qualifying_config_can_share_fingerprint_without_service_managed(self):
        """acquisition_critical_fingerprint does not bind service_managed/invocation_id.

        A process that forges QUALIFYING_MODE + matching poll/unit-digest
        environment (but is not actually launched by a recognised service
        manager) can obtain the SAME acquisition-critical fingerprint as the
        real qualifying service, even though its own lifecycle_provenance()
        correctly reports qualifying_service_mode=False (service_managed is
        false). This narrows the value of ACQUISITION_FINGERPRINT_CHANGED /
        ACTIVE_FINGERPRINT_DIFFERS_FROM_JOURNAL as a way to distinguish an
        unattested process from the real one by fingerprint alone.

        This probe does NOT demonstrate an end-to-end false accountable=True:
        in this reproduction the rogue's own scheduler activity collides with
        the real collector's obligation chain (OBLIGATION_SUPERSEDED_MORE_THAN_ONCE),
        so the window still fails closed. Recorded as MISSING_PROOF that a
        scenario avoiding that collision (e.g. the rogue's activity fully
        precedes the very first record_service_start() on a brand-new durable
        state directory) could still produce a false pass; Astra did not find
        one, but the fingerprint-blind-spot itself is a verified FACT.
        """
        case = sec_capture_tests.RodageFalsificationTests(methodName="runTest")
        case.setUp()
        self.addCleanup(case.doCleanups)
        router = case.fixture_router()
        qualifying = case.qualifying_collector(router)

        forged_env = {
            "QUANT_SEC_LIFECYCLE_CAUSE": "DEPLOYMENT_RESTART",
            "QUANT_SEC_QUALIFYING_MODE": "1",
            "QUANT_SEC_SERVICE_POLL_SECONDS": "60.0",
            "QUANT_SEC_EFFECTIVE_UNIT_DIGEST": "sha256:" + "d" * 64,
        }
        rogue = SecForm4Collector(
            case.paths, policy=qualifying.policy,
            transport=sec_capture_tests.FakeTransport(router),
            timebase=case.timebase,
            budget=SecTrafficBudget(case.paths.sec_budget, qualifying.policy,
                                    timebase=case.timebase),
            root=sec_capture_tests.ROOT, environ=forged_env)

        self.assertEqual(
            rogue.fingerprint, qualifying.fingerprint,
            "fingerprint FACT: service_managed/invocation_id are not bound into "
            "acquisition_critical_fingerprint, so a forged-but-unmanaged process "
            "can share the real fingerprint")
        self.assertFalse(rogue.lifecycle.get("service_managed"))
        self.assertFalse(rogue.lifecycle.get("qualifying_service_mode"))

        rogue.poll()
        qualifying.record_service_start()
        qualifying.poll()
        report = audit_observation_window(qualifying, now=case.timebase.now())
        self.assertFalse(
            report["accountable"],
            "in this reproduction the window still fails closed (see docstring); "
            "if this ever flips to True it is a REAL_DEFECT, not a NON_ISSUE")


if __name__ == "__main__":
    unittest.main()
