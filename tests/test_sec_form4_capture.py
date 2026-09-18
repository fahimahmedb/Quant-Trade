"""Adversarial proof for P0 SEC/Form-4 durable raw capture."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.clock import QuantSystem
from quant.dataplane.sec_form4 import (FILING_ENDPOINT_CLASS, HttpResponse, SecCapturePolicy,
                                       SecCollectorConfig, SecForm4Collector)
from quant.dataplane.sec_form4_raw import SecAttemptRecord, SecCaptureStore
from quant.events import EventLog
from quant.paths import QuantPaths
from quant.state import ComponentRegistry, read_jsonl

ACCESSION = "0000000001-26-000001"
INDEX_URL = ("https://www.sec.gov/Archives/edgar/data/1/000000000126000001/"
             f"{ACCESSION}-index.htm")
TEXT_URL = INDEX_URL[:-len("-index.htm")] + ".txt"
EMPTY_FEED = b'<feed xmlns="http://www.w3.org/2005/Atom"></feed>'
ONE_FEED = (f'<feed xmlns="http://www.w3.org/2005/Atom"><entry>'
            f'<link href="{INDEX_URL}" /></entry></feed>').encode()
FILING_BYTES = b"<SEC-DOCUMENT>SECRET-FORM4-CONTENT\r\nraw bytes\x00\xff"


class FakeClock:
    def __init__(self):
        self.value = datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)
        self.sleeps: list[float] = []

    def now(self):
        return self.value

    def sleep(self, seconds: float):
        self.sleeps.append(seconds)
        self.value += timedelta(seconds=seconds)

    def advance(self, seconds: float):
        self.value += timedelta(seconds=seconds)


class QueueTransport:
    def __init__(self, clock: FakeClock, responses):
        self.clock = clock
        self.responses = list(responses)
        self.calls: list[dict] = []

    def fetch(self, url, headers, timeout):
        self.calls.append({"url": url, "headers": dict(headers), "at": self.clock.now(),
                           "timeout": timeout})
        if not self.responses:
            raise AssertionError("unexpected HTTP request")
        item = self.responses.pop(0)
        if isinstance(item, BaseException):
            raise item
        advance, reply = item if isinstance(item, tuple) else (0, item)
        if advance:
            self.clock.advance(advance)
        return reply


def response(status: int, body: bytes, media="text/plain"):
    return HttpResponse(status, body, {"content-type": media,
                                      "content-length": str(len(body))})


def config(enabled=True):
    return SecCollectorConfig(enabled=enabled, requester_name="Quant Test",
                              contact_email="test@example.com", git_commit="deadbeef",
                              timeout_seconds=1, max_documents_per_poll=1)


def policy(**overrides):
    values = dict(poll_seconds=60, request_rate_per_second=2.0, max_concurrency=1,
                  backoff_seconds=[5, 15], rate_control_backoff_seconds=900,
                  permanent_4xx_backoff_seconds=300)
    values.update(overrides)
    return SecCapturePolicy(**values)


def collector(root: Path, clock: FakeClock, responses, **kwargs):
    paths = QuantPaths(root).ensure()
    transport = QueueTransport(clock, responses)
    item = SecForm4Collector(paths, EventLog(paths.events), ComponentRegistry(paths.components),
                             config=config(), policy=policy(**kwargs), transport=transport,
                             now=clock.now, sleep=clock.sleep, jitter=lambda _: 0.0)
    item.recover()
    return item, transport


def terminal(attempt_id: str, body: bytes, source=TEXT_URL):
    return SecAttemptRecord(
        attempt_id=attempt_id, attempt_kind="FILING", phase="COMPLETED",
        source_locator=source, request_attempted_at_utc="2026-09-18T12:00:00+00:00",
        response_received_at_utc="2026-09-18T12:00:01+00:00",
        result_state="RESPONSE_CAPTURED", http_status=200,
        raw_object_sha256=SecCaptureStore.digest(body), byte_length=len(body),
        collector_version="test", git_commit="deadbeef", endpoint_class=FILING_ENDPOINT_CLASS,
        media_type="text/plain")


class RawStoreTests(unittest.TestCase):
    def test_exact_bytes_survive_store_reload_and_manifest_rebuild(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = QuantPaths(Path(directory)).ensure()
            store = SecCaptureStore(paths)
            record, _ = store.capture_response(terminal("a1", FILING_BYTES), FILING_BYTES,
                                               ACCESSION)
            self.assertEqual(store.read_raw(record.sha256), FILING_BYTES)
            paths.sec_form4_manifest.unlink()
            SecCaptureStore(paths).rebuild_manifest()
            rows = list(read_jsonl(paths.sec_form4_manifest))
            self.assertEqual(rows[0]["sha256"], record.sha256)
            self.assertEqual(rows[0]["byte_length"], len(FILING_BYTES))

    def test_duplicate_same_response_never_overwrites_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = QuantPaths(Path(directory)).ensure()
            store = SecCaptureStore(paths)
            first, _ = store.capture_response(terminal("a1", FILING_BYTES), FILING_BYTES,
                                              ACCESSION)
            stat_before = store.object_path(first.sha256).stat()
            second, conflict = store.capture_response(terminal("a2", FILING_BYTES), FILING_BYTES,
                                                      ACCESSION)
            stat_after = store.object_path(second.sha256).stat()
            self.assertFalse(conflict)
            self.assertEqual(first.sha256, second.sha256)
            self.assertEqual(stat_before.st_ino, stat_after.st_ino)
            self.assertEqual(len(list(read_jsonl(paths.sec_form4_manifest))), 1)
            self.assertEqual(len(list(read_jsonl(paths.sec_form4_source_versions))), 1)

    def test_same_source_identity_with_different_bytes_is_explicit_conflict(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = QuantPaths(Path(directory)).ensure()
            store = SecCaptureStore(paths)
            store.capture_response(terminal("a1", b"first"), b"first", ACCESSION)
            _, conflict = store.capture_response(terminal("a2", b"second"), b"second", ACCESSION)
            versions = list(read_jsonl(paths.sec_form4_source_versions))
            self.assertTrue(conflict)
            self.assertEqual(len(versions), 2)
            self.assertFalse(versions[0]["conflict"])
            self.assertTrue(versions[1]["conflict"])
            self.assertNotEqual(versions[0]["raw_object_sha256"], versions[1]["raw_object_sha256"])

    def test_real_process_kill_after_staged_commit_recovers_on_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            child = r'''
import os, sys
from pathlib import Path
sys.path.insert(0, sys.argv[2])
from quant.paths import QuantPaths
from quant.dataplane.sec_form4_raw import SecAttemptRecord, SecCaptureStore
root=Path(sys.argv[1]); paths=QuantPaths(root).ensure(); body=b"kill-boundary-bytes"
def hook(point):
    if point == "after_stage_commit": os._exit(73)
store=SecCaptureStore(paths, fault_hook=hook)
rec=SecAttemptRecord("kill-attempt","FILING","COMPLETED","https://www.sec.gov/test",
"2026-09-18T00:00:00+00:00","2026-09-18T00:00:01+00:00","RESPONSE_CAPTURED",200,
SecCaptureStore.digest(body),len(body),"test","deadbeef","sec_complete_submission_text","text/plain")
store.capture_response(rec, body, "0000000001-26-000001")
'''
            proc = subprocess.run([sys.executable, "-c", child, str(root), str(ROOT / "src")])
            self.assertEqual(proc.returncode, 73)
            store = SecCaptureStore(QuantPaths(root).ensure())
            result = store.reconcile()
            digest = SecCaptureStore.digest(b"kill-boundary-bytes")
            self.assertTrue(result["recovered"])
            self.assertEqual(store.read_raw(digest), b"kill-boundary-bytes")
            terminals = [row for row in read_jsonl(store.attempts_path)
                         if row["attempt_id"] == "kill-attempt" and row["phase"] == "COMPLETED"]
            self.assertEqual(len(terminals), 1)


class CollectorTests(unittest.TestCase):
    def test_attempted_and_received_times_are_distinct_and_durable(self):
        with tempfile.TemporaryDirectory() as directory:
            clock = FakeClock()
            item, _ = collector(Path(directory), clock, [(2, response(200, EMPTY_FEED,
                                                                      "application/atom+xml"))])
            self.assertEqual(item.poll_once(), "NO_NEW_DATA")
            attempts = [row for row in read_jsonl(item.paths.sec_form4_attempts)
                        if row["attempt_kind"] == "DISCOVERY" and row["phase"] == "COMPLETED"]
            self.assertEqual(len(attempts), 1)
            self.assertNotEqual(attempts[0]["request_attempted_at_utc"],
                                attempts[0]["response_received_at_utc"])

    def test_no_new_poll_leaves_append_only_heartbeat(self):
        with tempfile.TemporaryDirectory() as directory:
            clock = FakeClock()
            item, _ = collector(Path(directory), clock,
                                [response(200, EMPTY_FEED, "application/atom+xml")])
            self.assertEqual(item.poll_once(), "NO_NEW_DATA")
            poll_rows = [row for row in read_jsonl(item.paths.sec_form4_attempts)
                         if row["attempt_kind"] == "POLL"]
            self.assertEqual([row["phase"] for row in poll_rows], ["STARTED", "COMPLETED"])
            self.assertEqual(poll_rows[-1]["result_state"], "NO_NEW_DATA")
            self.assertIsNotNone(item.state.last_successful_poll_at_utc)

    def test_content_length_mismatch_preserves_received_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            clock = FakeClock()
            malformed = HttpResponse(
                200, b"received-despite-bad-length",
                {"content-type": "application/atom+xml", "content-length": "999"})
            item, _ = collector(Path(directory), clock, [malformed])
            self.assertEqual(item.poll_once(), "BLOCKED")
            digest = SecCaptureStore.digest(malformed.body)
            self.assertEqual(item.store.read_raw(digest), malformed.body)
            completed = [row for row in read_jsonl(item.paths.sec_form4_attempts)
                         if row["attempt_kind"] == "DISCOVERY"
                         and row["phase"] == "COMPLETED"]
            self.assertEqual(completed[-1]["result_state"], "CONTENT_LENGTH_MISMATCH")
            self.assertEqual(completed[-1]["raw_object_sha256"], digest)

    def test_timeout_and_5xx_retries_are_bounded(self):
        for responses in ([TimeoutError("x"), TimeoutError("x"), TimeoutError("x")],
                          [response(503, b"busy"), response(503, b"busy"),
                           response(503, b"busy")]):
            with self.subTest(kind=type(responses[0]).__name__):
                with tempfile.TemporaryDirectory() as directory:
                    clock = FakeClock()
                    item, transport = collector(Path(directory), clock, responses)
                    self.assertEqual(item.poll_once(), "BLOCKED")
                    self.assertEqual(len(transport.calls), 3)
                    self.assertEqual(clock.sleeps[:2], [5.0, 15.0])
                    self.assertEqual(item.state.status, "BLOCKED")

    def test_429_enters_extended_backoff_without_hot_loop(self):
        with tempfile.TemporaryDirectory() as directory:
            clock = FakeClock()
            item, transport = collector(Path(directory), clock, [response(429, b"slow")])
            self.assertEqual(item.poll_once(), "BLOCKED")
            self.assertEqual(len(transport.calls), 1)
            self.assertFalse(item.due())
            blocked_until = datetime.fromisoformat(item.state.blocked_until_utc)
            self.assertEqual((blocked_until - clock.now()).total_seconds(), 900)

    def test_403_enters_extended_backoff_without_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            clock = FakeClock()
            item, transport = collector(Path(directory), clock, [response(403, b"blocked")])
            self.assertEqual(item.poll_once(), "BLOCKED")
            self.assertEqual(len(transport.calls), 1)
            self.assertFalse(item.due())
            self.assertEqual(item.state.last_error_class, "HTTP_403")

    def test_global_limiter_is_two_per_second_and_sequential(self):
        with tempfile.TemporaryDirectory() as directory:
            clock = FakeClock()
            item, transport = collector(Path(directory), clock, [
                response(200, ONE_FEED, "application/atom+xml"),
                response(200, FILING_BYTES),
            ])
            self.assertEqual(item.poll_once(), "CAPTURED")
            self.assertEqual(len(transport.calls), 2)
            delta = (transport.calls[1]["at"] - transport.calls[0]["at"]).total_seconds()
            self.assertGreaterEqual(delta, 0.5)
            self.assertEqual(item.policy.max_concurrency, 1)

    def test_restart_preserves_cursor_history_and_raw_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); clock = FakeClock()
            first, _ = collector(root, clock, [response(200, ONE_FEED, "application/atom+xml"),
                                               response(200, FILING_BYTES)])
            self.assertEqual(first.poll_once(), "CAPTURED")
            digest = first.state.last_raw_object_sha256
            history = first.store.attempt_history_digest()
            second, _ = collector(root, clock, [])
            self.assertEqual(second.state.last_raw_object_sha256, digest)
            self.assertEqual(second.store.attempt_history_digest(), history)
            self.assertEqual(second.store.read_raw(digest), FILING_BYTES)
            self.assertIn(ACCESSION, second.state.known_source_ids)

    def test_status_serialization_cannot_expose_filing_body_or_scientific_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            clock = FakeClock()
            item, _ = collector(Path(directory), clock, [response(200, ONE_FEED,
                                                              "application/atom+xml"),
                                                         response(200, FILING_BYTES)])
            self.assertEqual(item.poll_once(), "CAPTURED")
            rendered = json.dumps(item.status_snapshot(), sort_keys=True)
            self.assertNotIn("SECRET-FORM4-CONTENT", rendered)
            for forbidden in ("source_identity", "source_locator", "known_source_ids", "pending",
                              "issuer", "transaction_code", "filing_count"):
                self.assertNotIn(f'"{forbidden}"', rendered)
            self.assertIn("NOT_VISIBLE_FOR_SCIENTIFIC_PROTOCOL", rendered)
            self.assertIn("NOT_ADMISSIBLE_FOR_CONFIRMATION", rendered)

    def test_clock_owns_capture_and_runs_it_before_blocked_research(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); clock = FakeClock()
            system = QuantSystem(root)
            system.sec_capture.config = config()
            system.sec_capture.policy = policy()
            system.sec_capture.now = clock.now
            system.sec_capture.sleep = clock.sleep
            system.sec_capture.rate_limiter.now = clock.now
            system.sec_capture.rate_limiter.sleep = clock.sleep
            system.sec_capture.transport = QueueTransport(
                clock, [response(200, EMPTY_FEED, "application/atom+xml")])
            system.boot()
            self.assertEqual(system.tick(), "SEC_CAPTURE")
            self.assertEqual(system.sec_capture.state.last_poll_result, "NO_NEW_DATA")


if __name__ == "__main__":
    unittest.main()
