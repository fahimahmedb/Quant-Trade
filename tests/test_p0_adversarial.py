"""Deep adversarial P0 pre-t0 tests.

These tests are deliberately production-path oriented.  They target failure
classes that local helper tests can miss: state produced by main(), relaunch,
materialization tamper, real transport send accounting and signal-proxy leakage.
No external SEC request is made.
"""
from __future__ import annotations

import fcntl
import gzip
import importlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "deploy"))

import quant_sec_supervisor as launcher

from quant.clock import QuantSystem
from quant.dataplane.sec.audit import audit_observation_window
from quant.dataplane.sec.budget import SecTrafficBudget
from quant.dataplane.sec.collector import SecForm4Collector, STALE
from quant.dataplane.sec.fingerprint import build_manifest
from quant.dataplane.sec.policy import SecAccessPolicy
from quant.dataplane.sec.store import SecStorageFailure
from quant.dataplane.sec.supervisor import (
    AUTOMATIC_RESTART_AFTER_FAILURE, DEPLOYMENT_RESTART, MANUAL_START)
from quant.dataplane.sec.transport import (
    COMPLETE, RequestPermit, SecHttpResponse, SecHttpTransport, SecTransportError)
from quant.paths import QuantPaths
from quant.state import read_jsonl

from tests.test_sec_form4_capture import (
    CollectorTestCase, FakeTransport, ROOT as TEST_ROOT, SERVICE_MANAGED_ENV,
    USER_AGENT)


class _ImmediateChild:
    def __init__(self, code=0):
        self.returncode = code
        self.pid = 999999
        self._done = False

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        return self.returncode


class SupervisorProductionPathTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="p0-supervisor-adversarial-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "scripts").mkdir(parents=True)
        # The child is mocked, but the launcher still requires this path to exist.
        (self.root / "scripts" / "quant.py").write_text("raise SystemExit(0)\n")

    def _run(self, *, invocation, authority=None, child_codes=(0,)):
        env = {
            "QUANT_SEC_USER_AGENT": USER_AGENT,
            "QUANT_SEC_SERVICE_MANAGER": "systemd",
            "INVOCATION_ID": invocation,
        }
        codes = iter(child_codes)

        def popen(*args, **kwargs):
            return _ImmediateChild(next(codes))

        argv = ["quant_sec_supervisor.py", "--root", str(self.root)]
        if len(child_codes) > 1:
            argv += ["--max-restarts", str(len(child_codes))]
        with mock.patch.dict(os.environ, env, clear=True), \
             mock.patch.object(sys, "argv", argv), \
             mock.patch.object(launcher, "_effective_environment",
                               return_value=({**env, "QUANT_SEC_SERVICE_POLL_SECONDS": "60",
                                              "QUANT_SEC_QUALIFYING_MODE": "0"}, 60.0)), \
             mock.patch.object(launcher, "current_fingerprint",
                               return_value="sha256:" + "a" * 64), \
             mock.patch.object(launcher, "materialize_if_absent",
                               return_value="sha256:" + "a" * 64), \
             mock.patch.object(launcher, "_consume_deployment_authority",
                               return_value=authority), \
             mock.patch.object(launcher, "host_boot_id", return_value="kernel-boot-A"), \
             mock.patch.object(launcher.subprocess, "Popen", side_effect=popen), \
             mock.patch.object(launcher, "RESTART_DELAY_SECONDS", 0.0):
            return launcher.main()

    def test_main_state_roundtrip_keeps_kernel_boot_distinct_from_child(self):
        authority = {"nonce": "deploy-1"}
        self.assertEqual(self._run(invocation="inv-1", authority=authority), 0)
        first = launcher.read_state(launcher.supervisor_state_path(self.root))
        self.assertEqual(first["host_boot_id"], "kernel-boot-A")
        self.assertNotEqual(first["child_boot_id"], first["host_boot_id"])
        self.assertEqual(first["lifecycle_cause"], DEPLOYMENT_RESTART)

        # Exact real regression: a replacement supervisor on the same host after
        # the clean exit defaults invalidating, rather than fabricating a reboot.
        self.assertEqual(self._run(invocation="inv-2", authority=None), 0)
        second = launcher.read_state(launcher.supervisor_state_path(self.root))
        self.assertEqual(second["host_boot_id"], "kernel-boot-A")
        self.assertEqual(second["lifecycle_cause"], MANUAL_START)

    def test_same_living_supervisor_can_attest_child_failure_restart(self):
        self.assertEqual(self._run(invocation="inv-1", authority=None,
                                   child_codes=(1, 0)), 0)
        state = launcher.read_state(launcher.supervisor_state_path(self.root))
        self.assertEqual(state["lifecycle_cause"], AUTOMATIC_RESTART_AFTER_FAILURE)

    def test_corrupt_prior_supervisor_state_never_buys_clean_cause(self):
        path = launcher.supervisor_state_path(self.root)
        path.parent.mkdir(parents=True)
        path.write_text("{")
        self.assertEqual(self._run(invocation="inv-2", authority=None), 0)
        state = launcher.read_state(path)
        self.assertTrue(state["previous_state_invalid"])
        self.assertEqual(state["lifecycle_cause"], MANUAL_START)

    def test_double_supervisor_is_rejected_by_real_lock(self):
        sec = self.root / "var" / "sec"
        sec.mkdir(parents=True)
        fd = os.open(sec / "supervisor.lock", os.O_CREAT | os.O_RDWR, 0o600)
        self.addCleanup(os.close, fd)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.assertEqual(self._run(invocation="inv-2", authority=None), 2)


class FingerprintClosureTests(CollectorTestCase):
    def test_runtime_import_closure_is_in_manifest(self):
        manifest = build_manifest(self.policy(), root=TEST_ROOT)
        required = {
            "src/quant/state.py",
            "src/quant/paths.py",
            "src/quant/events.py",
            "src/quant/status/render.py",
            "src/quant/status/brief.py",
            "src/quant/desk/desk.py",
            "src/autonomous_research/runtime.py",
            "scripts/quant.py",
            "scripts/status_artifacts.py",
            "scripts/verify_p0.py",
        }
        self.assertTrue(required <= set(manifest["code"]))
        self.assertIn("python", manifest["runtime"])
        self.assertIn("openssl", manifest["runtime"])

    def _qualifying(self):
        import random
        policy = self.policy()
        environ = {
            **SERVICE_MANAGED_ENV,
            "QUANT_SEC_LIFECYCLE_CAUSE": DEPLOYMENT_RESTART,
            "QUANT_SEC_BOOT_ID": "child-1",
            "QUANT_SEC_SUPERVISOR_ID": "sup-1",
            "QUANT_SEC_QUALIFYING_MODE": "1",
            "QUANT_SEC_SERVICE_POLL_SECONDS": "60",
            "QUANT_SEC_SERVICE_RESTART_DELAY_SECONDS": "15",
            "QUANT_SEC_SERVICE_RESTART_BURST_LIMIT": "5",
            "QUANT_SEC_EFFECTIVE_UNIT_DIGEST": "sha256:" + "b" * 64,
        }
        transport = FakeTransport(self.fixture_router())
        collector = SecForm4Collector(
            self.paths, policy=policy, transport=transport, timebase=self.timebase,
            budget=SecTrafficBudget(self.paths.sec_budget, policy,
                                    timebase=self.timebase, rng=random.Random(5)),
            root=TEST_ROOT, environ=environ)
        self.transport = transport
        return collector

    def test_manifest_body_tamper_is_detected_even_if_string_fingerprint_is_unchanged(self):
        collector = self._qualifying()
        payload = collector.materialize_fingerprint()
        tampered = dict(payload)
        tampered["manifest"] = json.loads(json.dumps(payload["manifest"]))
        tampered["manifest"]["policy"]["discovery_poll_seconds"] = 999999
        # Deliberately leave acquisition_critical_fingerprint unchanged.
        self.paths.sec_fingerprint.write_text(json.dumps(tampered))
        readiness = collector.t0_readiness()
        self.assertFalse(readiness["instrumentation_ready"])
        self.assertIn("FINGERPRINT_MATERIALIZED_SELF_MISMATCH", readiness["blockers"])

    def test_other_host_materialization_is_not_accepted(self):
        collector = self._qualifying()
        payload = collector.materialize_fingerprint()
        payload["host_identity_digest"] = "sha256:" + "0" * 64
        self.paths.sec_fingerprint.write_text(json.dumps(payload))
        readiness = collector.t0_readiness()
        self.assertIn("FINGERPRINT_MATERIALIZED_OTHER_HOST", readiness["blockers"])

    def test_qualifying_request_refuses_stale_materialization_before_network(self):
        collector = self._qualifying()
        collector.materialize_fingerprint()
        payload = json.loads(self.paths.sec_fingerprint.read_text())
        payload["acquisition_critical_fingerprint"] = "sha256:" + "1" * 64
        self.paths.sec_fingerprint.write_text(json.dumps(payload))
        collector.enable()
        with self.assertRaises(SecStorageFailure):
            collector.poll()
        self.assertEqual(self.transport.requested, [])


class DurabilityAndSemanticTests(CollectorTestCase):
    def test_torn_sec_journal_is_never_silently_discarded(self):
        self.paths.ensure_sec()
        self.paths.sec_scheduler.write_bytes(b'{"transition_id":"lost"')
        with self.assertRaises(ValueError):
            list(read_jsonl(self.paths.sec_scheduler))

    def test_future_attempt_timestamp_is_not_live(self):
        collector = self.collector(self.fixture_router())
        collector.state.last_attempt_at_utc = "2099-01-01T00:00:00+00:00"
        self.assertEqual(collector.liveness(), STALE)

    def test_http_200_non_form4_body_does_not_acknowledge_filing(self):
        collector = self.collector(
            self.fixture_router(submission=b"<html><body>access denied</body></html>"))
        collector.poll()
        result = collector.drain(max_items=1)[0]
        self.assertNotEqual(result["result_state"], "CAPTURED")
        self.assertEqual(collector.store.envelopes(), [])
        self.assertNotEqual(collector.state.coverage_state, "COMPLETE")

    def test_public_telemetry_has_no_activity_volume_or_timing_proxy(self):
        from quant.dataplane.sec.visibility import find_count_proxies
        collector = self.collector(self.fixture_router())
        collector.poll()
        public = collector.telemetry()
        self.assertEqual(find_count_proxies(public), [], public)
        rendered = json.dumps(public)
        for forbidden in (
            "last_capture_at_utc", "last_attempt_at_utc", "cursor_identity_digest",
            "next_due_at_utc", "work_in_flight", "raw_bytes", "requests_spent"):
            self.assertNotIn(forbidden, rendered)


class _Response:
    def __init__(self, body=b"OK", status=200, headers=None):
        self.status = status
        self.reason = "OK"
        self._body = body
        self._sent = False
        self._headers = headers or {"Content-Length": str(len(body))}

    def getheader(self, name):
        return self._headers.get(name)

    def read(self, amount):
        if self._sent:
            return b""
        self._sent = True
        return self._body


class _Connection:
    def __init__(self, response=None, error=None):
        self.response = response or _Response()
        self.error = error
        self.request_calls = 0
        self.closed = False

    def request(self, method, path, headers=None):
        self.request_calls += 1
        if self.error:
            raise self.error

    def getresponse(self):
        return self.response

    def close(self):
        self.closed = True


class ConnectionLevelAccountingTests(unittest.TestCase):
    def policy(self, **overrides):
        return SecAccessPolicy(user_agent=USER_AGENT, **overrides)

    def test_real_transport_path_emits_exactly_one_request_per_permit(self):
        transport = SecHttpTransport(self.policy())
        connection = _Connection(_Response(body=b"wire"))
        transport._connection = connection
        permit = RequestPermit("attempt-1", "2026-09-19T00:00:00+00:00", "test")
        response = transport.fetch("/fixture", permit)
        self.assertEqual(response.body, b"wire")
        self.assertEqual(connection.request_calls, 1)
        self.assertEqual(transport.requests_sent, 1)
        self.assertTrue(permit.spent)

    def test_connection_failure_is_not_hiddenly_resent(self):
        transport = SecHttpTransport(self.policy())
        connection = _Connection(error=ConnectionResetError("reset"))
        transport._connection = connection
        permit = RequestPermit("attempt-1", "2026-09-19T00:00:00+00:00", "test")
        with self.assertRaises(SecTransportError):
            transport.fetch("/fixture", permit)
        self.assertEqual(connection.request_calls, 1)
        self.assertEqual(transport.requests_sent, 1)
        self.assertTrue(permit.spent)


class AuditFailClosedTests(CollectorTestCase):
    def test_network_intent_without_finished_attempt_invalidates_audit(self):
        collector = self.collector(self.fixture_router())
        collector.lifecycle.update({
            "lifecycle_cause": DEPLOYMENT_RESTART,
            "boot_id": "child",
            "supervisor_id": "sup",
        })
        collector.record_service_start()
        collector.state.coverage_state = "COMPLETE"
        collector.save()
        from quant.state import append_jsonl
        append_jsonl(self.paths.sec / "request_intents.jsonl", {
            "event": "INTENT", "attempt_id": "crashed-send",
            "obligation_id": collector.state.open_obligation_id,
        })
        report = audit_observation_window(collector)
        self.assertFalse(report["accountable"])
        self.assertIn("REQUEST_ACCOUNTING_INCOMPLETE", report["findings"])


if __name__ == "__main__":
    unittest.main()
