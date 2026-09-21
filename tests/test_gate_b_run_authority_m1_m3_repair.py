from __future__ import annotations

import datetime as dt
import errno
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


runctl = load_module("quant_gate_b_runctl_r1", ROOT / "scripts" / "quant_gate_b_runctl.py")

CANDIDATE = "4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072"
TREE = "4d15ef6f471213ee6ab56337b555d2906ef9bf16"
INPUT = "sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2"
RUN1 = "gate-b-11111111-1111-4111-8111-111111111111"
RUN2 = "gate-b-22222222-2222-4222-8222-222222222222"
NOW = dt.datetime(2026, 9, 21, 10, 0, 0, tzinfo=dt.timezone.utc)


class Harness:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.checkout = self.root / "checkout"
        self.checkout.mkdir()
        self.state = self.root / "state"
        self.registry_path = self.state / "registry.jsonl"
        self.receipts = self.state / "receipts"
        self.registry = runctl.Registry(self.registry_path, self.checkout)

    def close(self):
        self.tmp.cleanup()

    def set_epoch(self, when=NOW):
        return self.registry.set_revocation_epoch(epoch=1, reference="blue/revocation/1", event_time=when)

    def reserve(self, run_id=RUN1, host="host-A", when=NOW):
        return self.registry.reserve(
            candidate_sha=CANDIDATE,
            git_tree=TREE,
            verified_input_tree_digest=INPUT,
            target_host_opaque_id=host,
            blue_reference="blue/decision",
            operator_identity_reference="operator/ref",
            run_id_factory=lambda: run_id,
            event_time=when,
        )

    def activation(
        self,
        reservation,
        *,
        activation_id="activation-1",
        issued=NOW - dt.timedelta(minutes=1),
        not_before=NOW - dt.timedelta(seconds=30),
        expires=NOW + dt.timedelta(minutes=5),
        timestamp_overrides=None,
    ):
        obj = {
            "schema": runctl.ACTIVATION_SCHEMA,
            "activation_id": activation_id,
            "run_id": reservation["run_id"],
            "attempt_number": reservation["attempt_number"],
            "reservation_digest": reservation["event_digest"],
            "candidate_sha": CANDIDATE,
            "git_tree": TREE,
            "verified_input_tree_digest": INPUT,
            "target_host_opaque_id": reservation["target_host_opaque_id"],
            "issued_at_utc": runctl.utc_text(issued),
            "not_before_utc": runctl.utc_text(not_before),
            "expires_at_utc": runctl.utc_text(expires),
            "revocation_epoch": 1,
            "revocation_reference": "blue/revocation/1",
            "gate_b_mutation_authorized": True,
        }
        if timestamp_overrides:
            obj.update(timestamp_overrides)
        raw = runctl.canonical_json_bytes(obj)
        return obj, raw, runctl.sha256_digest(raw)

    def seal(self, reservation, **kwargs):
        obj, raw, digest = self.activation(reservation, **kwargs)
        event = self.registry.seal_activation(activation_bytes=raw, activation_digest=digest, event_time=NOW)
        return obj, raw, digest, event

    def consume(self, raw, digest, *, run_id=RUN1, now=NOW):
        return self.registry.consume_activation(
            activation_bytes=raw,
            activation_digest=digest,
            receipt_dir=self.receipts,
            expected_run_id=run_id,
            expected_candidate=(CANDIDATE, TREE, INPUT),
            now=now,
        )

    def binding(self, reservation, activation_digest, *, ordinal=1, artifact_digest=None, artifact_type="diagnostic"):
        obj = {
            "schema": runctl.EVIDENCE_BINDING_SCHEMA,
            "run_id": reservation["run_id"],
            "attempt_number": reservation["attempt_number"],
            "activation_digest": activation_digest,
            "reservation_digest": reservation["event_digest"],
            "candidate_sha": CANDIDATE,
            "git_tree": TREE,
            "verified_input_tree_digest": INPUT,
            "target_host_opaque_id": reservation["target_host_opaque_id"],
            "artifact_type": artifact_type,
            "artifact_ordinal": ordinal,
            "artifact_digest": artifact_digest or ("sha256:" + "a" * 64),
            "created_at_utc": runctl.utc_text(NOW),
        }
        raw = runctl.canonical_json_bytes(obj)
        return obj, raw, runctl.sha256_digest(raw)


def fd_path(fd: int) -> str:
    try:
        return os.readlink(f"/proc/self/fd/{fd}")
    except OSError:
        return ""


class GateBRunAuthorityM1M3RepairTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()

    def tearDown(self):
        self.h.close()

    def _sealed(self):
        self.h.set_epoch()
        r = self.h.reserve()
        _, raw, digest, _ = self.h.seal(r)
        return r, raw, digest

    def test_registry_short_write_is_completed_exactly(self):
        self.h.set_epoch()
        real_write = os.write
        partials = []

        def short_once(fd, data):
            if fd_path(fd) == str(self.h.registry_path) and not partials:
                payload = bytes(data)
                n = max(1, len(payload) // 3)
                partials.append(n)
                return real_write(fd, payload[:n])
            return real_write(fd, data)

        with mock.patch.object(runctl.os, "write", side_effect=short_once):
            reservation = self.h.reserve()
        self.assertTrue(partials)
        events = runctl.load_registry(self.h.registry_path)
        self.assertEqual(events[-1]["event_digest"], reservation["event_digest"])

    def test_registry_repeated_partial_writes_are_completed(self):
        self.h.set_epoch()
        real_write = os.write
        calls = 0

        def tiny(fd, data):
            nonlocal calls
            if fd_path(fd) == str(self.h.registry_path):
                calls += 1
                payload = bytes(data)
                return real_write(fd, payload[: min(7, len(payload))])
            return real_write(fd, data)

        with mock.patch.object(runctl.os, "write", side_effect=tiny):
            self.h.reserve()
        self.assertGreater(calls, 2)
        runctl.load_registry(self.h.registry_path)

    def test_interrupted_write_retries(self):
        self.h.set_epoch()
        real_write = os.write
        interrupted = False

        def eintr_once(fd, data):
            nonlocal interrupted
            if fd_path(fd) == str(self.h.registry_path) and not interrupted:
                interrupted = True
                raise InterruptedError(errno.EINTR, "interrupted")
            return real_write(fd, data)

        with mock.patch.object(runctl.os, "write", side_effect=eintr_once):
            self.h.reserve()
        self.assertTrue(interrupted)
        runctl.load_registry(self.h.registry_path)

    def test_zero_progress_registry_write_fails_closed(self):
        self.h.set_epoch()
        real_write = os.write
        fired = False

        def zero_once(fd, data):
            nonlocal fired
            if fd_path(fd) == str(self.h.registry_path) and not fired:
                fired = True
                return 0
            return real_write(fd, data)

        with mock.patch.object(runctl.os, "write", side_effect=zero_once):
            with self.assertRaisesRegex(runctl.AuthorityError, "zero progress"):
                self.h.reserve()
        self.assertTrue(fired)
        events = runctl.load_registry(self.h.registry_path)
        self.assertEqual([e["event_type"] for e in events], ["REVOCATION_EPOCH_SET"])

    def test_injected_registry_write_failure_does_not_return_consume_authority(self):
        _, raw, digest = self._sealed()
        real_write = os.write
        stage = 0

        def partial_then_fail(fd, data):
            nonlocal stage
            if fd_path(fd) == str(self.h.registry_path):
                payload = bytes(data)
                if stage == 0:
                    stage = 1
                    return real_write(fd, payload[: max(1, len(payload) // 4)])
                if stage == 1:
                    stage = 2
                    raise OSError(errno.EIO, "injected")
            return real_write(fd, data)

        with mock.patch.object(runctl.os, "write", side_effect=partial_then_fail):
            with self.assertRaisesRegex(runctl.AuthorityError, "write failed"):
                self.h.consume(raw, digest)
        with self.assertRaisesRegex(runctl.AuthorityError, "truncated"):
            runctl.load_registry(self.h.registry_path)

    def test_first_registry_creation_requires_parent_directory_fsync(self):
        seen = []
        real = runctl._fsync_dir

        def record(path):
            seen.append(Path(path))
            return real(path)

        with mock.patch.object(runctl, "_fsync_dir", side_effect=record):
            self.h.set_epoch()
        self.assertIn(self.h.state, seen)

    def test_first_registry_creation_parent_fsync_failure_is_visible(self):
        real_fsync_dir = runctl._fsync_dir
        calls = 0

        def fail_registry_entry_fsync(path):
            nonlocal calls
            calls += 1
            # F11 lock-authority bootstrap now durably creates its own directory
            # entries before the registry append. Let that independent durability
            # point succeed, then inject failure at the registry-entry fsync.
            if calls == 1:
                return real_fsync_dir(path)
            raise runctl.AuthorityError("dir fsync injected")

        with mock.patch.object(runctl, "_fsync_dir", side_effect=fail_registry_entry_fsync):
            with self.assertRaisesRegex(runctl.AuthorityError, "dir fsync injected"):
                self.h.set_epoch()
        events = runctl.load_registry(self.h.registry_path)
        self.assertEqual(events[-1]["event_type"], "REVOCATION_EPOCH_SET")

    def test_existing_registry_append_does_not_depend_on_new_entry_fsync(self):
        self.h.set_epoch()
        with mock.patch.object(runctl, "_fsync_dir", side_effect=runctl.AuthorityError("should not be called")):
            reservation = self.h.reserve()
        self.assertEqual(reservation["event_type"], "RUN_RESERVED")

    def test_receipt_short_write_is_completed_and_revalidated(self):
        _, raw, digest = self._sealed()
        real_write = os.write
        short = False

        def short_receipt_once(fd, data):
            nonlocal short
            if "/.receipt-" in fd_path(fd) and not short:
                short = True
                payload = bytes(data)
                n = max(1, len(payload) // 2)
                return real_write(fd, payload[:n])
            return real_write(fd, data)

        with mock.patch.object(runctl.os, "write", side_effect=short_receipt_once):
            _, receipt = self.h.consume(raw, digest)
        self.assertTrue(short)
        final = Path(receipt["path"])
        self.assertEqual(runctl.sha256_digest(final.read_bytes()), receipt["digest"])

    def test_receipt_repeated_partial_writes_are_completed(self):
        _, raw, digest = self._sealed()
        real_write = os.write
        calls = 0

        def tiny_receipt(fd, data):
            nonlocal calls
            if "/.receipt-" in fd_path(fd):
                calls += 1
                payload = bytes(data)
                return real_write(fd, payload[: min(5, len(payload))])
            return real_write(fd, data)

        with mock.patch.object(runctl.os, "write", side_effect=tiny_receipt):
            _, receipt = self.h.consume(raw, digest)
        self.assertGreater(calls, 2)
        self.assertEqual(runctl.sha256_digest(Path(receipt["path"]).read_bytes()), receipt["digest"])

    def test_receipt_directory_fsync_failure_after_consumption_is_fail_closed(self):
        _, raw, digest = self._sealed()
        with mock.patch.object(runctl, "_fsync_dir", side_effect=runctl.AuthorityError("receipt dir fsync failed")):
            with self.assertRaisesRegex(runctl.AuthorityError, "receipt dir fsync failed"):
                self.h.consume(raw, digest)
        events = runctl.load_registry(self.h.registry_path)
        self.assertEqual(events[-1]["event_type"], "ACTIVATION_CONSUMED")
        with self.assertRaisesRegex(runctl.AuthorityError, "already been consumed"):
            self.h.consume(raw, digest)

    def test_receipt_link_failure_after_consumption_remains_consumed(self):
        _, raw, digest = self._sealed()
        with mock.patch.object(runctl.os, "link", side_effect=OSError(errno.EIO, "link injected")):
            with self.assertRaises(OSError):
                self.h.consume(raw, digest)
        with self.assertRaisesRegex(runctl.AuthorityError, "already been consumed"):
            self.h.consume(raw, digest)

    def test_preexisting_receipt_collision_is_red_and_consumed(self):
        r, raw, digest = self._sealed()
        receipt = {
            "schema": runctl.RECEIPT_SCHEMA,
            "run_id": RUN1,
            "attempt_number": r["attempt_number"],
            "activation_id": "activation-1",
            "activation_digest": digest,
            "reservation_digest": r["event_digest"],
            "candidate_sha": CANDIDATE,
            "git_tree": TREE,
            "verified_input_tree_digest": INPUT,
            "target_host_opaque_id": "host-A",
            "consumed_at_utc": runctl.utc_text(NOW),
        }
        rb = runctl.canonical_json_bytes(receipt) + b"\n"
        p = self.h.receipts / (runctl.sha256_digest(rb).split(":", 1)[1] + ".json")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"foreign\n")
        with self.assertRaisesRegex(runctl.AuthorityError, "receipt already exists"):
            self.h.consume(raw, digest)
        with self.assertRaisesRegex(runctl.AuthorityError, "already been consumed"):
            self.h.consume(raw, digest)
        self.assertEqual(p.read_bytes(), b"foreign\n")

    def test_expiry_while_waiting_on_real_independent_flock_is_rejected(self):
        self.h.set_epoch(when=dt.datetime.now(dt.timezone.utc))
        r = self.h.reserve(when=dt.datetime.now(dt.timezone.utc))
        now = dt.datetime.now(dt.timezone.utc)
        _, raw, digest, _ = self.h.seal(
            r,
            issued=now - dt.timedelta(seconds=2),
            not_before=now - dt.timedelta(seconds=1),
            expires=now + dt.timedelta(seconds=2),
        )
        code = r'''
import fcntl, os, sys, time
p=sys.argv[1]
fd=os.open(p, os.O_RDWR|os.O_CREAT, 0o600)
fcntl.flock(fd, fcntl.LOCK_EX)
print("LOCKED", flush=True)
time.sleep(3.0)
fcntl.flock(fd, fcntl.LOCK_UN)
os.close(fd)
'''
        proc = subprocess.Popen(
            [sys.executable, "-c", code, str(self.h.registry.lock)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            self.assertEqual(proc.stdout.readline().strip(), "LOCKED")
            start = time.monotonic()
            with self.assertRaisesRegex(runctl.AuthorityError, "stale/expired"):
                self.h.registry.consume_activation(
                    activation_bytes=raw,
                    activation_digest=digest,
                    receipt_dir=self.h.receipts,
                    expected_run_id=RUN1,
                    expected_candidate=(CANDIDATE, TREE, INPUT),
                    now=None,
                )
            self.assertGreaterEqual(time.monotonic() - start, 2.0)
        finally:
            proc.wait(timeout=10)
            stderr = proc.stderr.read()
            proc.stdout.close()
            proc.stderr.close()
            if proc.returncode:
                self.fail(stderr)
        self.assertFalse(any(e["event_type"] == "ACTIVATION_CONSUMED" for e in runctl.load_registry(self.h.registry_path)))

    def test_future_issued_activation_red(self):
        self.h.set_epoch(); r = self.h.reserve()
        _, raw, digest, _ = self.h.seal(
            r,
            issued=NOW + dt.timedelta(seconds=1),
            not_before=NOW - dt.timedelta(seconds=1),
            expires=NOW + dt.timedelta(minutes=1),
        )
        with self.assertRaisesRegex(runctl.AuthorityError, "issued in the future"):
            self.h.consume(raw, digest)

    def test_not_yet_valid_activation_red(self):
        self.h.set_epoch(); r = self.h.reserve()
        _, raw, digest, _ = self.h.seal(
            r,
            issued=NOW - dt.timedelta(seconds=1),
            not_before=NOW + dt.timedelta(seconds=1),
            expires=NOW + dt.timedelta(minutes=1),
        )
        with self.assertRaisesRegex(runctl.AuthorityError, "not yet valid"):
            self.h.consume(raw, digest)

    def test_invalid_chronology_red(self):
        cases = [
            (NOW - dt.timedelta(seconds=1), NOW + dt.timedelta(seconds=2), NOW + dt.timedelta(seconds=1)),
            (NOW - dt.timedelta(seconds=1), NOW + dt.timedelta(seconds=1), NOW + dt.timedelta(seconds=1)),
            (NOW + dt.timedelta(seconds=2), NOW + dt.timedelta(seconds=1), NOW + dt.timedelta(minutes=1)),
        ]
        for index, (issued, not_before, expires) in enumerate(cases):
            with self.subTest(index=index):
                h = Harness()
                try:
                    h.set_epoch(); r = h.reserve()
                    _, raw, digest, _ = h.seal(r, issued=issued, not_before=not_before, expires=expires)
                    with self.assertRaises(runctl.AuthorityError):
                        h.consume(raw, digest)
                finally:
                    h.close()

    def test_exact_expiry_boundary_red_and_valid_window_green(self):
        self.h.set_epoch(); r = self.h.reserve()
        _, raw, digest, _ = self.h.seal(r, issued=NOW-dt.timedelta(seconds=2), not_before=NOW-dt.timedelta(seconds=1), expires=NOW)
        with self.assertRaisesRegex(runctl.AuthorityError, "stale/expired"):
            self.h.consume(raw, digest)

        h = Harness()
        try:
            h.set_epoch(); r2 = h.reserve()
            _, raw2, digest2, _ = h.seal(r2)
            ev, _ = h.consume(raw2, digest2)
            self.assertEqual(ev["event_type"], "ACTIVATION_CONSUMED")
        finally:
            h.close()

    def test_non_utc_timestamp_is_rejected(self):
        self.h.set_epoch(); r = self.h.reserve()
        _, raw, digest = self.h.activation(r, timestamp_overrides={"issued_at_utc": "2026-09-21T09:59:00+00:00"})
        with self.assertRaisesRegex(runctl.AuthorityError, "invalid UTC"):
            self.h.registry.seal_activation(activation_bytes=raw, activation_digest=digest, event_time=NOW)

    def _consumed(self, h=None, run_id=RUN1, activation_id="activation-1"):
        h = h or self.h
        h.set_epoch(); r = h.reserve(run_id=run_id)
        _, raw, digest, _ = h.seal(r, activation_id=activation_id)
        h.consume(raw, digest, run_id=run_id)
        return r, digest

    def test_binding_from_another_run_activation_is_red(self):
        r1, d1 = self._consumed()
        self.h.registry.terminal(run_id=RUN1, status="FAILED_TERMINAL", reason="done", event_time=NOW)
        r2 = self.h.reserve(run_id=RUN2)
        _, raw2, d2, _ = self.h.seal(r2, activation_id="activation-2")
        self.h.consume(raw2, d2, run_id=RUN2)
        _, braw, bd = self.h.binding(r2, d1)
        with self.assertRaisesRegex(runctl.AuthorityError, "activation digest mismatch"):
            self.h.registry.bind_evidence(binding_bytes=braw, binding_digest=bd, event_time=NOW)

    def test_binding_to_sealed_but_unconsumed_activation_is_red(self):
        self.h.set_epoch(); r = self.h.reserve()
        _, _, digest, _ = self.h.seal(r)
        _, braw, bd = self.h.binding(r, digest)
        with self.assertRaisesRegex(runctl.AuthorityError, "requires consumed"):
            self.h.registry.bind_evidence(binding_bytes=braw, binding_digest=bd, event_time=NOW)

    def test_binding_digest_must_match_actual_consumed_activation(self):
        r, digest = self._consumed()
        wrong = "sha256:" + "b" * 64
        self.assertNotEqual(wrong, digest)
        _, braw, bd = self.h.binding(r, wrong)
        with self.assertRaisesRegex(runctl.AuthorityError, "activation digest mismatch"):
            self.h.registry.bind_evidence(binding_bytes=braw, binding_digest=bd, event_time=NOW)

    def test_ordinal_bool_string_zero_and_negative_are_red(self):
        r, digest = self._consumed()
        for ordinal in (True, False, "1", 0, -1):
            with self.subTest(ordinal=ordinal):
                _, raw, bd = self.h.binding(r, digest, ordinal=ordinal)
                with self.assertRaisesRegex(runctl.AuthorityError, "ordinal invalid"):
                    self.h.registry.bind_evidence(binding_bytes=raw, binding_digest=bd, event_time=NOW)

    def test_duplicate_ordinal_is_red(self):
        r, digest = self._consumed()
        _, raw1, bd1 = self.h.binding(r, digest, ordinal=1, artifact_digest="sha256:" + "a" * 64)
        ev = self.h.registry.bind_evidence(binding_bytes=raw1, binding_digest=bd1, event_time=NOW)
        self.assertEqual(ev["artifact_ordinal"], 1)
        _, raw2, bd2 = self.h.binding(r, digest, ordinal=1, artifact_digest="sha256:" + "b" * 64)
        with self.assertRaisesRegex(runctl.AuthorityError, "duplicate evidence ordinal"):
            self.h.registry.bind_evidence(binding_bytes=raw2, binding_digest=bd2, event_time=NOW)

    def test_binding_schema_digest_and_type_are_strict(self):
        r, digest = self._consumed()
        obj, _, _ = self.h.binding(r, digest)
        obj["unexpected"] = "x"
        raw = runctl.canonical_json_bytes(obj)
        with self.assertRaisesRegex(runctl.AuthorityError, "binding malformed"):
            self.h.registry.bind_evidence(binding_bytes=raw, binding_digest=runctl.sha256_digest(raw), event_time=NOW)

        _, raw2, bd2 = self.h.binding(r, digest, artifact_digest="not-a-digest")
        with self.assertRaisesRegex(runctl.AuthorityError, "binding malformed"):
            self.h.registry.bind_evidence(binding_bytes=raw2, binding_digest=bd2, event_time=NOW)

        _, raw3, bd3 = self.h.binding(r, digest, artifact_type="bad type with spaces")
        with self.assertRaisesRegex(runctl.AuthorityError, "artifact type"):
            self.h.registry.bind_evidence(binding_bytes=raw3, binding_digest=bd3, event_time=NOW)

    def test_valid_binding_positive_control(self):
        r, digest = self._consumed()
        _, raw, bd = self.h.binding(r, digest, ordinal=1)
        ev = self.h.registry.bind_evidence(binding_bytes=raw, binding_digest=bd, event_time=NOW)
        self.assertEqual(ev["activation_digest"], digest)
        self.assertEqual(ev["artifact_type"], "diagnostic")
        runctl.load_registry(self.h.registry_path)


if __name__ == "__main__":
    unittest.main()
