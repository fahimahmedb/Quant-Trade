"""Tests for the P0 SEC/Form-4 durable raw-capture lane.

The numbered requirements in ``NEXT_BUILD_MISSION.md`` ("Tests required before
live enablement") are cited on the tests that discharge them, so a reviewer can
check the list rather than trust a summary.
"""

from __future__ import annotations

import dataclasses
import errno
import uuid
import gzip
import json
import os
import sys
import unittest
from unittest import mock
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.dataplane.sec.budget import (SecCooldownActive, SecTrafficBudget,  # noqa: E402
                                        seconds_from_retry_after)
from quant.dataplane.sec.policy import (SEC_DOCUMENTED_MAX_REQUESTS_PER_SECOND,  # noqa: E402
                                        SEC_POLICY_SOURCES, SecAccessPolicy,
                                        SecPolicyNotConfigured, USER_AGENT_ENV,
                                        is_configured, policy_from_environment)
from quant.dataplane.sec.store import (CAPTURED, NOT_ADMISSIBLE_FOR_CONFIRMATION,  # noqa: E402
                                       NOT_VISIBLE_FOR_SCIENTIFIC_PROTOCOL,
                                       RawObjectConflict, SecAcquisitionEnvelope,
                                       SecAttemptRecord, SecCaptureStore,
                                       SecRawObjectRecord, SecStorageFailure,
                                       digest_bytes)
from quant.dataplane.sec import fingerprint as fingerprint_module  # noqa: E402
from quant.dataplane.sec.fingerprint import (ACQUISITION_CRITICAL_MODULES,  # noqa: E402
                                             EXPLICITLY_NONCRITICAL,
                                             FINGERPRINT_SCHEMA_VERSION,
                                             INCLUDE_CANONICAL, TRANSFORM_CANONICAL,
                                             PolicyClassificationInvalid,
                                             UnclassifiedPolicyField,
                                             acquisition_critical_fingerprint,
                                             build_manifest, canonical_json,
                                             canonical_policy, compute_fingerprint,
                                             policy_field_names,
                                             verify_policy_classification)
from quant.dataplane.sec.audit import audit_observation_window  # noqa: E402
from quant.dataplane.sec.scheduler import (AUTHORIZED_SUPERSESSION_CAUSES,  # noqa: E402
                                           AWAITING_POLL, BACKOFF,
                                           BACKOFF_ENTERED, BLOCKED_NOT_CONFIGURED,
                                           CONFIG_FAIL_CLOSED, COOLDOWN,
                                           DRAIN_COMPLETED, DRAINING, LANE_ENABLED,
                                           POLL_COMPLETED, SCHEDULER_STATES,
                                           SERVICE_START, SchedulerTransition,
                                           WORK_ENQUEUED)
from quant.dataplane.sec.supervisor import (AUTOMATIC_CAUSES,  # noqa: E402
                                            AUTOMATIC_RESTART_AFTER_FAILURE,
                                            AUTOMATIC_RESTART_AFTER_SUPERVISOR_FAILURE,
                                            DEPLOYMENT_RESTART, INVALIDATING_CAUSES,
                                            LIFECYCLE_CAUSES, MANUAL_START,
                                            SCHEDULED_START, UNATTESTED,
                                            effective_service_configuration,
                                            lifecycle_provenance,
                                            service_manager_provenance)
from quant.dataplane.sec.timebase import FrozenTimebase  # noqa: E402
from quant.dataplane.sec.visibility import (assert_no_count_proxies,  # noqa: E402
                                            assert_no_scientific_content,
                                            find_count_proxies, find_leaks)
from quant.dataplane.sec.transport import (COMPLETE,  # noqa: E402
                                           DEADLINE_EXCEEDED as DEADLINE_EXCEEDED_OUTCOME,
                                           PermitAlreadySpent, RequestPermit,
                                           SecHttpResponse, SecHttpTransport,
                                           SecTransportError, TRUNCATED)
from quant.paths import QuantPaths  # noqa: E402
from quant.state import append_jsonl, parse_ts, read_jsonl  # noqa: E402


USER_AGENT = "Quant Research quant-research@example.com"


class SecCaptureTestCase(unittest.TestCase):
    """Isolated system root per test, exactly as the V1 suite does."""

    def setUp(self) -> None:
        import tempfile
        self._directory = tempfile.TemporaryDirectory(prefix="quant-sec-p0-")
        self.addCleanup(self._directory.cleanup)
        self.root = Path(self._directory.name)
        self.paths = QuantPaths(self.root).ensure()
        self.timebase = FrozenTimebase()

    def policy(self, **overrides) -> SecAccessPolicy:
        return SecAccessPolicy(user_agent=USER_AGENT, **overrides)

    def store(self) -> SecCaptureStore:
        return SecCaptureStore(self.paths, root=ROOT)

    def budget(self, policy: SecAccessPolicy | None = None) -> SecTrafficBudget:
        self.paths.ensure_sec()
        import random
        return SecTrafficBudget(self.paths.sec_budget, policy or self.policy(),
                                timebase=self.timebase, rng=random.Random(7))


class PolicyTests(SecCaptureTestCase):
    def test_policy_fails_closed_without_declared_user_agent(self) -> None:
        """Fail closed when the SEC-required identity is absent."""
        with self.assertRaises(SecPolicyNotConfigured):
            policy_from_environment({})
        with self.assertRaises(SecPolicyNotConfigured):
            policy_from_environment({USER_AGENT_ENV: "   "})
        self.assertFalse(is_configured({}))

    def test_user_agent_must_carry_a_contact_address(self) -> None:
        with self.assertRaises(SecPolicyNotConfigured):
            policy_from_environment({USER_AGENT_ENV: "QuantBot/1.0"})
        policy = policy_from_environment({USER_AGENT_ENV: USER_AGENT})
        self.assertEqual(policy.user_agent, USER_AGENT)
        self.assertTrue(is_configured({USER_AGENT_ENV: USER_AGENT}))

    def test_configured_rate_stays_far_below_the_documented_sec_ceiling(self) -> None:
        policy = self.policy()
        self.assertLessEqual(policy.max_requests_per_second,
                             SEC_DOCUMENTED_MAX_REQUESTS_PER_SECOND)
        self.assertEqual(policy.max_requests_per_second, 2.0)
        self.assertEqual(policy.max_concurrency, 1)
        self.assertEqual(policy.discovery_poll_seconds, 60.0)
        self.assertFalse(policy.allow_burst)
        with self.assertRaises(SecPolicyNotConfigured):
            SecAccessPolicy(user_agent=USER_AGENT, max_requests_per_second=25.0)

    def test_policy_records_the_consulted_authoritative_sources(self) -> None:
        """The mission requires the consulted source and date, not an assumption."""
        self.assertTrue(SEC_POLICY_SOURCES)
        for source in SEC_POLICY_SOURCES:
            self.assertTrue(source["url"].startswith("https://www.sec.gov/"))
            self.assertRegex(source["reviewed_or_updated"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertRegex(source["consulted_at_utc"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertIn("10 requests", source["quoted_max_request_rate"].replace("/second", " per second"))
        rendered = self.policy().to_dict()
        self.assertEqual(len(rendered["policy_sources"]), len(SEC_POLICY_SOURCES))

    def test_backoff_schedule_is_the_frozen_bounded_ladder(self) -> None:
        policy = self.policy()
        self.assertEqual(policy.backoff_schedule_seconds, (5.0, 15.0, 60.0, 300.0, 900.0))
        # Past the end the ladder stops growing rather than running away.
        self.assertEqual(policy.backoff_seconds(99), 900.0)


class RawStoreTests(SecCaptureTestCase):
    def test_exact_bytes_survive_store_and_reload(self) -> None:
        """Requirement 1: exact byte identity survives store/reload."""
        store = self.store()
        body = b"<?xml version='1.0'?><ownershipDocument>\x00\xff exact \r\n bytes</ownershipDocument>"
        written = store.put_object(body)
        self.assertEqual(written.raw_object_sha256, digest_bytes(body))
        self.assertEqual(written.byte_length, len(body))
        self.assertFalse(written.deduplicated)
        self.assertEqual(store.read_object(written.raw_object_sha256), body)
        # Re-reading through a fresh store object proves it is on disk, not cached.
        self.assertEqual(self.store().read_object(written.raw_object_sha256), body)

    def test_duplicate_identical_response_does_not_overwrite_prior_evidence(self) -> None:
        """Requirement 2: a duplicate deduplicates, it does not rewrite."""
        store = self.store()
        body = b"identical form 4 bytes"
        first = store.put_object(body)
        before = first.path.stat()
        second = store.put_object(body)
        self.assertTrue(second.deduplicated)
        self.assertEqual(first.raw_object_sha256, second.raw_object_sha256)
        after = first.path.stat()
        self.assertEqual((before.st_ino, before.st_mtime_ns), (after.st_ino, after.st_mtime_ns))

    def test_stored_objects_are_read_only_on_disk(self) -> None:
        store = self.store()
        written = store.put_object(b"immutable")
        mode = written.path.stat().st_mode & 0o777
        self.assertEqual(mode, 0o444, "a raw object must not be writable in place")

    def test_conflicting_bytes_under_one_identity_create_an_explicit_version(self) -> None:
        """Requirement 3: same source identity, different bytes -> conflict."""
        store = self.store()
        identity = "0001234567-26-000123"
        first = store.put_object(b"version one bytes")
        second = store.put_object(b"version two bytes")
        self.assertNotEqual(first.raw_object_sha256, second.raw_object_sha256)
        v1 = store.record_source_version(source_identity=identity,
                                         raw_object_sha256=first.raw_object_sha256,
                                         observed_at_utc=self.timebase.now_iso())
        self.timebase.advance(60)
        v2 = store.record_source_version(source_identity=identity,
                                        raw_object_sha256=second.raw_object_sha256,
                                        observed_at_utc=self.timebase.now_iso())
        self.assertFalse(v1.conflict)
        self.assertTrue(v2.conflict)
        self.assertEqual(v2.version, 2)
        self.assertEqual(v2.prior_sha256, first.raw_object_sha256)
        # Both objects remain readable: nothing was replaced.
        self.assertEqual(store.read_object(first.raw_object_sha256), b"version one bytes")
        self.assertEqual(store.read_object(second.raw_object_sha256), b"version two bytes")
        self.assertEqual(len(store.conflicts()), 1)

    def test_identical_recapture_of_one_identity_is_not_a_conflict(self) -> None:
        store = self.store()
        identity = "0001234567-26-000124"
        written = store.put_object(b"stable bytes")
        store.record_source_version(source_identity=identity,
                                    raw_object_sha256=written.raw_object_sha256,
                                    observed_at_utc=self.timebase.now_iso())
        again = store.record_source_version(source_identity=identity,
                                           raw_object_sha256=written.raw_object_sha256,
                                           observed_at_utc=self.timebase.now_iso())
        self.assertFalse(again.conflict)
        self.assertEqual(again.version, 2)
        self.assertEqual(store.conflicts(), [])

    def test_corrupted_object_is_detected_rather_than_served(self) -> None:
        store = self.store()
        written = store.put_object(b"trustworthy bytes")
        written.path.chmod(0o644)
        written.path.write_bytes(b"tampered bytes!!")
        with self.assertRaises(RawObjectConflict):
            store.read_object(written.raw_object_sha256)
        self.assertEqual(store.verify_objects(), [written.raw_object_sha256])

    def test_incomplete_bytes_live_outside_the_valid_object_namespace(self) -> None:
        """Requirement 18: a truncated transfer is never a valid raw capture."""
        store = self.store()
        partial = b"<?xml version='1.0'?><ownershipDoc"
        written = store.put_object(partial, incomplete=True)
        self.assertFalse(store.has_object(written.raw_object_sha256),
                         "partial bytes must not appear in the valid raw store")
        self.assertTrue(store.incomplete_path(written.raw_object_sha256).exists())
        self.assertEqual(store.storage_health()["incomplete_objects"], 1)
        self.assertEqual(store.storage_health()["raw_objects"], 0)

    def test_disk_full_during_raw_write_raises_instead_of_acknowledging(self) -> None:
        """Requirement 16: a write failure cannot acknowledge uncaptured evidence."""
        store = self.store()
        real_write = os.write

        def full_disk(fd: int, data: bytes) -> int:
            raise OSError(errno.ENOSPC, "No space left on device")

        os.write = full_disk
        try:
            with self.assertRaises(SecStorageFailure):
                store.put_object(b"bytes that cannot be written")
        finally:
            os.write = real_write
        self.assertEqual(store.storage_health()["raw_objects"], 0)
        self.assertEqual(store.storage_health()["uncommitted_staging_files"], 0,
                         "a failed write must not leave staging litter behind")
        self.assertEqual(store.envelopes(), [])

    def test_capture_does_not_imply_visibility_or_admissibility(self) -> None:
        """Section 7 of the reclassification: three independent states."""
        store = self.store()
        record = store.record_raw_object(SecRawObjectRecord(
            raw_object_sha256=digest_bytes(b"x"), byte_length=1,
            first_received_at_utc=self.timebase.now_iso(), endpoint_class="test"))
        self.assertEqual(record.capture_state, CAPTURED)
        self.assertEqual(record.visibility_state, NOT_VISIBLE_FOR_SCIENTIFIC_PROTOCOL)
        self.assertEqual(record.admissibility_state, NOT_ADMISSIBLE_FOR_CONFIRMATION)
        health = store.storage_health()
        self.assertEqual(health["visibility_state"], NOT_VISIBLE_FOR_SCIENTIFIC_PROTOCOL)
        self.assertEqual(health["admissibility_state"], NOT_ADMISSIBLE_FOR_CONFIRMATION)


class JournalTests(SecCaptureTestCase):
    def test_attempt_and_receipt_timestamps_are_distinct_and_durable(self) -> None:
        """Requirement 4: attempt and receipt times are separate, persisted facts."""
        store = self.store()
        attempted = self.timebase.now_iso()
        self.timebase.advance(3.5)
        received = self.timebase.now_iso()
        store.record_attempt(SecAttemptRecord(
            attempt_id="a1", attempt_kind="DISCOVERY", endpoint_class="test",
            source_locator_digest=digest_bytes(b"locator"),
            request_attempted_at_utc=attempted, response_received_at_utc=received,
            result_state="NO_NEW_DATA", collector_version="v", git_commit="c",
            http_status=200, duration_seconds=3.5))
        reloaded = self.store().attempts()
        self.assertEqual(len(reloaded), 1)
        self.assertNotEqual(reloaded[0]["request_attempted_at_utc"],
                            reloaded[0]["response_received_at_utc"])
        self.assertEqual(reloaded[0]["request_attempted_at_utc"], attempted)
        self.assertEqual(reloaded[0]["response_received_at_utc"], received)

    def test_source_publication_time_is_never_the_local_receipt_time(self) -> None:
        """A backfill acquired today keeps today's receipt time."""
        store = self.store()
        received = self.timebase.now_iso()
        envelope = store.record_envelope(SecAcquisitionEnvelope(
            envelope_id="e1", attempt_id="a1", source_identity="0001-26-000001",
            source_locator="https://www.sec.gov/Archives/edgar/data/1/x.txt",
            endpoint_class="test", request_attempted_at_utc=received,
            response_received_at_utc=received, http_status=200,
            raw_object_sha256=digest_bytes(b"body"), byte_length=4,
            collector_version="v", git_commit="c",
            source_published_at_utc="2019-04-01T20:15:00-04:00"))
        self.assertNotEqual(envelope.source_published_at_utc,
                            envelope.response_received_at_utc)
        self.assertTrue(envelope.response_received_at_utc.startswith("2026-09-18"))
        self.assertTrue(envelope.source_published_at_utc.startswith("2019-"))

    def test_committed_identities_are_exactly_the_envelopes_on_disk(self) -> None:
        """Acknowledgement is the envelope, so a crash before it is replayable."""
        store = self.store()
        self.assertEqual(store.committed_identities(), {})
        written = store.put_object(b"raw bytes only")
        # Bytes durable, envelope not yet: the identity is not acknowledged.
        self.assertEqual(store.committed_identities(), {})
        store.record_envelope(SecAcquisitionEnvelope(
            envelope_id="e1", attempt_id="a1", source_identity="ID-1",
            source_locator="loc", endpoint_class="test",
            request_attempted_at_utc=self.timebase.now_iso(),
            response_received_at_utc=self.timebase.now_iso(), http_status=200,
            raw_object_sha256=written.raw_object_sha256, byte_length=written.byte_length,
            collector_version="v", git_commit="c"))
        self.assertEqual(self.store().committed_identities(),
                         {"ID-1": written.raw_object_sha256})

    def test_identifying_locators_stay_out_of_the_firewall_safe_journals(self) -> None:
        store = self.store()
        locator = "https://www.sec.gov/Archives/edgar/data/320193/000032019326000010/0000320193-26-000010.txt"
        locator_digest = store.record_locator(
            locator=locator, source_identity="0000320193-26-000010",
            endpoint_class="test", observed_at_utc=self.timebase.now_iso())
        store.record_attempt(SecAttemptRecord(
            attempt_id="a1", attempt_kind="FILING", endpoint_class="test",
            source_locator_digest=locator_digest,
            request_attempted_at_utc=self.timebase.now_iso(),
            result_state="CAPTURED", collector_version="v", git_commit="c"))
        safe = "\n".join(path.read_text(encoding="utf-8")
                         for path in self.paths.sec_operator_internal_journals()
                         if path.exists())
        self.assertNotIn("0000320193", safe)
        self.assertNotIn("Archives/edgar/data", safe)
        self.assertIn(locator_digest, safe)
        # The restricted journal still permits point-in-time reconstruction.
        resolved = store.resolve_locator(locator_digest)
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved["source_locator"], locator)


class TrafficBudgetTests(SecCaptureTestCase):
    def test_requests_are_spaced_by_the_configured_rate_with_no_burst(self) -> None:
        budget = self.budget()
        first = budget.reserve("discovery")
        self.assertEqual(first["waited_seconds"], 0.0)
        second = budget.reserve("discovery")
        self.assertAlmostEqual(second["waited_seconds"], 0.5, places=6)
        # Idling does not accumulate burst credit, but it does not cost a wait.
        self.timebase.advance(120)
        third = budget.reserve("filing")
        self.assertEqual(third["waited_seconds"], 0.0)
        fourth = budget.reserve("filing")
        self.assertAlmostEqual(fourth["waited_seconds"], 0.5, places=6)

    def test_the_budget_is_global_across_consumers_not_per_instance(self) -> None:
        """A second SEC consumer shares one budget file, so the rate cannot double."""
        policy = self.policy()
        first = self.budget(policy)
        import random
        second = SecTrafficBudget(self.paths.sec_budget, policy, timebase=self.timebase,
                                  rng=random.Random(7))
        first.reserve("discovery")
        waited = second.reserve("some_other_sec_consumer")["waited_seconds"]
        self.assertAlmostEqual(waited, 0.5, places=6,
                               msg="a separate consumer must not get a free slot")
        self.assertEqual(second.load().requests, 2)

    def test_cooldown_is_durable_across_restart_and_never_shortened(self) -> None:
        """Requirement 13: an active cooldown survives a restart."""
        budget = self.budget()
        budget.enter_cooldown(300.0, "rate_limited")
        with self.assertRaises(SecCooldownActive) as raised:
            budget.reserve("discovery")
        self.assertAlmostEqual(raised.exception.remaining_seconds, 300.0, places=3)
        # A fresh object reads the same durable cooldown.
        reborn = self.budget()
        self.assertAlmostEqual(reborn.cooldown_remaining(), 300.0, places=3)
        # A shorter proposal cannot shorten an authoritative cooldown.
        reborn.enter_cooldown(5.0, "transient")
        self.assertAlmostEqual(reborn.cooldown_remaining(), 300.0, places=3)
        self.assertEqual(reborn.load().cooldown_reason, "rate_limited")
        reborn.enter_cooldown(900.0, "forbidden")
        self.assertAlmostEqual(reborn.cooldown_remaining(), 900.0, places=3)
        self.timebase.advance(901)
        self.assertEqual(reborn.cooldown_remaining(), 0.0)
        reborn.reserve("discovery")

    def test_backoff_walks_the_frozen_ladder_with_jitter_and_stops_growing(self) -> None:
        budget = self.budget()
        observed = [budget.next_backoff_seconds() for _ in range(7)]
        ladder = self.policy().backoff_schedule_seconds
        for index, value in enumerate(observed):
            base = ladder[min(index, len(ladder) - 1)]
            self.assertGreaterEqual(value, base * 0.75)
            self.assertLessEqual(value, base * 1.25)
        self.assertEqual(budget.load().backoff_step, len(ladder) - 1)
        budget.reset_backoff()
        self.assertEqual(budget.load().backoff_step, 0)

    def test_retry_after_is_parsed_in_both_permitted_forms(self) -> None:
        now = self.timebase.now()
        self.assertEqual(seconds_from_retry_after("120", now), 120.0)
        self.assertIsNone(seconds_from_retry_after(None, now))
        self.assertIsNone(seconds_from_retry_after("", now))
        later = (now + timedelta(seconds=90))
        stamp = later.strftime("%a, %d %b %Y %H:%M:%S GMT")
        parsed = seconds_from_retry_after(stamp, now)
        self.assertIsNotNone(parsed)
        self.assertAlmostEqual(parsed, 90.0, delta=1.0)
        # A past date is a zero-second cooldown, never a negative one.
        past = (now - timedelta(seconds=600)).strftime("%a, %d %b %Y %H:%M:%S GMT")
        self.assertEqual(seconds_from_retry_after(past, now), 0.0)

    def test_a_spent_slot_is_durable_before_the_request_is_made(self) -> None:
        budget = self.budget()
        budget.reserve("discovery")
        # Simulating a kill during the request: nothing in memory carries over.
        self.assertIsNotNone(json.loads(self.paths.sec_budget.read_text())["last_request_at_utc"])
        self.assertAlmostEqual(self.budget().reserve("discovery")["waited_seconds"], 0.5,
                               places=6)


class TransportSemanticTests(SecCaptureTestCase):
    def test_compressed_response_hashes_the_exact_received_bytes(self) -> None:
        """Requirement 17: compression preserves exact-byte semantics."""
        plain = b"<feed xmlns='http://www.w3.org/2005/Atom'><title>Latest</title></feed>"
        compressed = gzip.compress(plain)
        response = SecHttpResponse(status=200, reason="OK", body=compressed,
                                  headers={"Content-Encoding": "gzip",
                                           "Content-Length": str(len(compressed)),
                                           "Content-Type": "application/atom+xml"})
        self.assertEqual(response.byte_length, len(compressed))
        self.assertEqual(response.content_encoding, "gzip")
        self.assertEqual(response.decoded_body(), plain)
        store = self.store()
        written = store.put_object(response.body)
        self.assertEqual(written.raw_object_sha256, digest_bytes(compressed))
        self.assertNotEqual(written.raw_object_sha256, digest_bytes(plain),
                            "the hash must describe the bytes received, not a decoded copy")
        self.assertEqual(store.read_object(written.raw_object_sha256), compressed)
        metadata = response.transport_metadata()
        self.assertEqual(metadata["content_encoding"], "gzip")
        self.assertEqual(metadata["declared_content_length"], len(compressed))

    def test_body_that_lies_about_its_encoding_is_a_transport_failure(self) -> None:
        response = SecHttpResponse(status=200, reason="OK", body=b"not gzip at all",
                                  headers={"Content-Encoding": "gzip"})
        with self.assertRaises(SecTransportError):
            response.decoded_body()

    def test_short_body_against_declared_length_is_marked_truncated(self) -> None:
        response = SecHttpResponse(status=200, reason="OK", body=b"12345",
                                  headers={"Content-Length": "500"},
                                  transfer_outcome=TRUNCATED)
        self.assertFalse(response.complete)
        complete = SecHttpResponse(status=200, reason="OK", body=b"12345",
                                   headers={"Content-Length": "5"})
        self.assertTrue(complete.complete)
        self.assertEqual(complete.transfer_outcome, COMPLETE)

    def test_transport_errors_never_carry_response_content(self) -> None:
        error = SecTransportError("request_failed:TimeoutError")
        self.assertNotIn(" ", str(error))
        self.assertEqual(error.error_class, "request_failed:TimeoutError")


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------------------
# Discovery semantics and coverage truthfulness
# ---------------------------------------------------------------------------

from datetime import date  # noqa: E402

from quant.dataplane.sec.collector import (COMPLETE as COVERAGE_COMPLETE,  # noqa: E402
                                           COVERAGE_UNKNOWN, CURSOR_FELL_OUT_OF_WINDOW,
                                           DAILY_INDEX_GAP, DAILY_INDEX_UNAVAILABLE,
                                           FalseSuccessPrevented, NEVER_RAN,
                                           PAGE_BUDGET_EXHAUSTED, PAGE_FETCH_FAILED,
                                           PAGINATION_INTERRUPTED, RUNNING,
                                           SecForm4Collector, STALE,
                                           assert_no_new_data_earned)
from quant.dataplane.sec.discovery import (DiscoveryInvalid, daily_index_path,  # noqa: E402
                                           discovery_path, parse_daily_index,
                                           parse_discovery_page)
from quant.dataplane.sec.store import (ACCESS_FORBIDDEN, CAPTURED_OK,  # noqa: E402
                                       COOLDOWN_SUPPRESSED, DEDUPLICATED,
                                       DISCOVERY_INVALID, HUNG_REQUEST,
                                       INCOMPLETE_TRANSFER, NEW_ITEMS, NO_NEW_DATA,
                                       PERMANENT_CLIENT_ERROR, RATE_LIMITED,
                                       REQUEST_FAILED, SERVER_ERROR, STORAGE_FAILED,
                                       digest_text)

FIXTURES = ROOT / "tests" / "fixtures" / "sec"


def response(body: bytes, status: int = 200, headers: dict[str, str] | None = None,
             transfer_outcome: str = COMPLETE) -> SecHttpResponse:
    supplied = dict(headers or {})
    supplied.setdefault("Content-Type", "application/atom+xml")
    if transfer_outcome == COMPLETE:
        supplied.setdefault("Content-Length", str(len(body)))
    return SecHttpResponse(status=status, reason="OK", body=body, headers=supplied,
                           transfer_outcome=transfer_outcome)


ENTRY_TEMPLATE = """\t<entry>
\t\t<title>{form} - SYNTHETIC ISSUER {n} ({cik}) (Issuer)</title>
\t\t<link rel="alternate" type="text/html" href="https://www.sec.gov/Archives/edgar/data/{cik_int}/{nodash}/{accession}-index.htm"/>
\t\t<updated>2026-09-18T{hh}:{mm}:00-04:00</updated>
\t\t<category scheme="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany" label="form type" term="{form}"/>
\t\t<id>urn:tag:sec.gov,2008:accession-number={accession}</id>
\t</entry>"""


def synthetic_accession(index: int) -> str:
    return f"{9000000000 + index:010d}-26-{index:06d}"


def build_feed(indices: list[int], *, form: str = "4",
               feed_updated: str = "2026-09-18T16:35:12-04:00",
               entries: list[str] | None = None) -> bytes:
    body = entries if entries is not None else [
        ENTRY_TEMPLATE.format(
            form=form, n=index, cik=f"{9000000000 + index:010d}",
            cik_int=str(9000000000 + index), nodash=synthetic_accession(index).replace("-", ""),
            accession=synthetic_accession(index), hh=f"{(index % 8) + 9:02d}",
            mm=f"{index % 60:02d}")
        for index in indices]
    return ("<?xml version=\"1.0\" encoding=\"ISO-8859-1\" ?>\n"
            "<feed xmlns=\"http://www.w3.org/2005/Atom\">\n"
            "\t<title>Latest Filings - Ownership Forms</title>\n"
            "\t<link rel=\"self\" type=\"application/atom+xml\" href=\"https://www.sec.gov/"
            "cgi-bin/browse-edgar?action=getcurrent\"/>\n"
            f"\t<updated>{feed_updated}</updated>\n"
            + "\n".join(body) + "\n</feed>\n").encode("iso-8859-1")


class FakeTransport:
    """Same ``fetch`` contract as the real transport, so production has no test branch.

    It honours the permit exactly as the real transport does - consumed at send,
    single use - so every test in this file exercises the one-request-per-permit
    invariant rather than only the tests that name it.
    """

    def __init__(self, handler):
        self.handler = handler
        self.requested: list[str] = []
        #: Attempt id carried by the permit for each request actually emitted.
        self.permits_consumed: list[str] = []

    def fetch(self, path: str, permit) -> SecHttpResponse:
        permit.consume()
        self.requested.append(path)
        self.permits_consumed.append(permit.attempt_id)
        outcome = self.handler(path, len(self.requested) - 1)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    def close(self) -> None:
        pass


class CollectorTestCase(SecCaptureTestCase):
    def collector(self, handler, *, enable: bool = True, **overrides) -> SecForm4Collector:
        import random
        policy = self.policy(**overrides)
        transport = FakeTransport(handler)
        budget = SecTrafficBudget(self.paths.sec_budget, policy, timebase=self.timebase,
                                  rng=random.Random(3))
        collector = SecForm4Collector(
            self.paths, policy=policy, transport=transport, timebase=self.timebase,
            budget=budget, root=ROOT)
        self.transport = transport
        if enable:
            collector.enable()
        return collector

    def reborn(self, handler, **overrides) -> SecForm4Collector:
        """A fresh collector over the same durable state: a restart."""
        return self.collector(handler, enable=False, **overrides)

    @staticmethod
    def fixture_router(*, atom: bytes | None = None, submission: bytes | None = None,
                       index: bytes | None = None):
        atom = atom if atom is not None else (FIXTURES / "latest_form4_page.atom").read_bytes()
        submission = (submission if submission is not None
                      else (FIXTURES / "form4_submission.txt").read_bytes())

        def handler(path: str, call: int):
            if path.startswith("/cgi-bin/browse-edgar"):
                return response(atom)
            if path.startswith("/Archives/edgar/daily-index"):
                if index is None:
                    return response(b"", status=404)
                return response(index, headers={"Content-Type": "text/plain"})
            if path.endswith(".txt"):
                return response(submission, headers={"Content-Type": "text/plain"})
            return response(b"unexpected", status=404)

        return handler


class KnownFixtureDiscoveryTests(CollectorTestCase):
    def test_known_form4_fixture_drives_discovery_to_raw_document_bytes(self) -> None:
        """Requirement 6: discovery -> Form-4 identity -> locator -> raw bytes."""
        collector = self.collector(self.fixture_router())
        outcome = collector.poll()
        self.assertTrue(outcome.valid_discovery)
        self.assertEqual(outcome.result_state, NEW_ITEMS)
        self.assertEqual(outcome.coverage_state, COVERAGE_COMPLETE)
        self.assertTrue(outcome.heartbeat_durable)
        self.assertEqual(outcome.pages_walked, 1)
        self.assertEqual(outcome.enqueued, 3, "three Form-4 entries including one 4/A")

        # The discovery response itself is preserved as an immutable raw object.
        atom_bytes = (FIXTURES / "latest_form4_page.atom").read_bytes()
        self.assertEqual(outcome.discovery_object_sha256, digest_bytes(atom_bytes))
        self.assertEqual(collector.store.read_object(outcome.discovery_object_sha256),
                         atom_bytes)

        results = collector.drain(max_items=3)
        self.assertEqual([item["result_state"] for item in results], [CAPTURED_OK] * 3)
        submission = (FIXTURES / "form4_submission.txt").read_bytes()
        self.assertEqual(collector.store.read_object(results[0]["raw_object_sha256"]),
                         submission)

        envelopes = {item["source_identity"]: item for item in collector.store.envelopes()}
        self.assertEqual(set(envelopes), {"0000320193-26-000045", "0000789019-26-000112",
                                          "0001018724-26-000301"})
        first = envelopes["0000320193-26-000045"]
        self.assertEqual(first["raw_object_sha256"], digest_bytes(submission))
        self.assertEqual(first["byte_length"], len(submission))
        # Every task is bound to the discovery page that produced it.
        self.assertEqual(first["discovery_object_sha256"], outcome.discovery_object_sha256)
        self.assertEqual(first["poll_id"], outcome.poll_id)
        # Source publication time is recorded, and is not the receipt time.
        self.assertEqual(first["source_published_at_utc"], "2026-09-18T16:31:05-04:00")
        self.assertNotEqual(first["source_published_at_utc"],
                            first["response_received_at_utc"])
        self.assertTrue(first["response_received_at_utc"].startswith("2026-09-18T12:"))
        self.assertEqual(first["capture_state"], CAPTURED)
        self.assertEqual(first["visibility_state"], NOT_VISIBLE_FOR_SCIENTIFIC_PROTOCOL)

    def test_raw_document_locator_is_derived_without_crawling_the_filing(self) -> None:
        """One request per filing: the complete submission text file."""
        collector = self.collector(self.fixture_router())
        collector.poll()
        collector.drain(max_items=3)
        filing_requests = [path for path in self.transport.requested if path.endswith(".txt")]
        self.assertEqual(len(filing_requests), 3)
        self.assertEqual(
            filing_requests[0],
            "/Archives/edgar/data/320193/000032019326000045/0000320193-26-000045.txt")

    def test_cursor_advances_only_after_every_task_is_acknowledged(self) -> None:
        collector = self.collector(self.fixture_router())
        outcome = collector.poll()
        self.assertIsNone(collector.state.cursor_identity_digest,
                          "the anchor must not move while tasks are unacknowledged")
        self.assertIsNotNone(collector.state.pending_cursor_identity_digest)
        collector.drain(max_items=2)
        self.assertIsNone(collector.state.cursor_identity_digest)
        collector.drain(max_items=1)
        self.assertEqual(collector.state.cursor_identity_digest,
                         digest_text("0000320193-26-000045"))
        self.assertEqual(collector.state.pending_tasks, [])
        del outcome


class AntiFalseSuccessTests(CollectorTestCase):
    def test_guard_rejects_unearned_no_new_data(self) -> None:
        """The guard itself, independent of any transport."""
        assert_no_new_data_earned(True, COVERAGE_COMPLETE, 0)
        with self.assertRaises(FalseSuccessPrevented):
            assert_no_new_data_earned(False, COVERAGE_COMPLETE, 0)
        with self.assertRaises(FalseSuccessPrevented):
            assert_no_new_data_earned(True, COVERAGE_UNKNOWN, 0)
        with self.assertRaises(FalseSuccessPrevented):
            assert_no_new_data_earned(True, COVERAGE_COMPLETE, 3)

    def test_html_error_page_with_http_200_cannot_become_no_new_data(self) -> None:
        """Requirement 7: nominal success, HTML body -> ERROR, never NO_NEW_DATA."""
        html = (FIXTURES / "edgar_error_page.html").read_bytes()
        collector = self.collector(lambda path, call: response(
            html, headers={"Content-Type": "text/html"}))
        outcome = collector.poll()
        self.assertEqual(outcome.result_state, DISCOVERY_INVALID)
        self.assertFalse(outcome.valid_discovery)
        self.assertEqual(outcome.coverage_state, COVERAGE_UNKNOWN)
        self.assertEqual(outcome.error_class, "html_page_returned_for_atom_discovery")
        self.assertNotEqual(outcome.result_state, NO_NEW_DATA)
        # The heartbeat still exists, and the bytes are preserved as evidence.
        self.assertTrue(outcome.heartbeat_durable)
        self.assertEqual(collector.store.attempts()[-1]["http_status"], 200)
        self.assertEqual(collector.store.read_object(digest_bytes(html)), html)
        self.assertEqual([gap["kind"] for gap in collector.state.open_gaps],
                         [PAGE_FETCH_FAILED])

    def test_structurally_invalid_payloads_cannot_become_no_new_data(self) -> None:
        cases = {
            b"": "empty_discovery_body",
            b"\x00\x01 not xml at all": "discovery_xml_parse_failed:ParseError",
            b"<rss version='2.0'><channel/></rss>": "discovery_root_is_not_an_atom_feed",
            b"<feed xmlns='http://www.w3.org/2005/Atom'><title>T</title>"
            b"<link href='x'/></feed>": "discovery_feed_missing_updated_marker",
            b"<feed xmlns='http://www.w3.org/2005/Atom'><updated>2026</updated>"
            b"<link href='x'/></feed>": "discovery_feed_missing_title",
            b"<feed xmlns='http://www.w3.org/2005/Atom'><title>T</title>"
            b"<updated>2026</updated></feed>": "discovery_feed_missing_self_description",
        }
        for body, expected in cases.items():
            with self.subTest(expected=expected):
                with self.assertRaises(DiscoveryInvalid) as raised:
                    parse_discovery_page(body, requested_start=0, requested_count=40)
                self.assertEqual(raised.exception.reason, expected)

    def test_prefix_matched_non_ownership_forms_are_excluded_not_errors(self) -> None:
        """EDGAR matches ``type`` by prefix, so ``type=4`` also returns 497*.

        Observed live during the pre-t0 rodage: a ``497J`` fund filing arrived on
        the Form-4 feed. The server filter is a narrowing hint; local
        classification is authoritative. Excluding an unwanted form is normal
        operation, so it must not fail the poll - but the exclusion is explicit
        and inspectable, never a silent drop.
        """
        mixed = build_feed([], entries=[
            ENTRY_TEMPLATE.format(form="4", n=1, cik="0000320193", cik_int="320193",
                                  nodash="000032019326000045",
                                  accession="0000320193-26-000045", hh="16", mm="31"),
            ENTRY_TEMPLATE.format(form="497J", n=2, cik="0000789019", cik_int="789019",
                                  nodash="000078901926000112",
                                  accession="0000789019-26-000112", hh="16", mm="22"),
            ENTRY_TEMPLATE.format(form="497K", n=3, cik="0001018724", cik_int="1018724",
                                  nodash="000101872426000301",
                                  accession="0001018724-26-000301", hh="16", mm="04"),
            ENTRY_TEMPLATE.format(form="4/A", n=4, cik="0001045810", cik_int="1045810",
                                  nodash="000104581026000777",
                                  accession="0001045810-26-000777", hh="15", mm="50")])
        page = parse_discovery_page(mixed, requested_start=0, requested_count=40)
        self.assertEqual(page.entry_count, 4)
        self.assertEqual([entry.form_type for entry in page.form_4_entries()], ["4", "4/A"])
        self.assertEqual(page.excluded_form_types, ["497J", "497K"])

        collector = self.collector(self.fixture_router(atom=mixed))
        outcome = collector.poll()
        self.assertTrue(outcome.valid_discovery,
                        "an unwanted form type is not a broken discovery")
        self.assertEqual(outcome.result_state, NEW_ITEMS)
        self.assertEqual(outcome.enqueued, 2, "only the ownership filings are queued")
        self.assertEqual(collector.state.open_gaps, [])

    def test_an_unreadable_form_type_is_still_an_error(self) -> None:
        """The real guard: a term we cannot read means the filter is unproven."""
        # XML-valid terms that are not readable as an EDGAR form type. (A term
        # containing raw markup breaks XML parsing first, which is also an
        # error, just an earlier one.)
        for bad in ("not a form type!", "4" * 40, "../../etc/passwd", "form type: four"):
            with self.subTest(term=bad):
                feed = build_feed([], entries=[
                    "\t<entry>\n\t\t<title>x</title>\n"
                    "\t\t<link rel='alternate' href='https://www.sec.gov/Archives/edgar/"
                    "data/1/900000000126000001/9000000001-26-000001-index.htm'/>\n"
                    f"\t\t<category term='{bad}' label='form type'/>\n"
                    "\t\t<id>urn:tag:sec.gov,2008:accession-number="
                    "9000000001-26-000001</id>\n\t</entry>"])
                with self.assertRaises(DiscoveryInvalid) as raised:
                    parse_discovery_page(feed, requested_start=0, requested_count=40)
                self.assertTrue(raised.exception.reason.startswith(
                    "discovery_entry_form_type_unparseable"))
        collector = self.collector(lambda path, call: response(build_feed([], entries=[
            "\t<entry>\n\t\t<title>x</title>\n"
            "\t\t<link rel='alternate' href='https://www.sec.gov/Archives/edgar/data/1/"
            "900000000126000001/9000000001-26-000001-index.htm'/>\n"
            "\t\t<category term='not a form!' label='form type'/>\n"
            "\t\t<id>urn:tag:sec.gov,2008:accession-number=9000000001-26-000001</id>\n"
            "\t</entry>"])))
        outcome = collector.poll()
        self.assertEqual(outcome.result_state, DISCOVERY_INVALID)
        self.assertNotEqual(outcome.result_state, NO_NEW_DATA)

    def test_a_page_of_only_unwanted_forms_is_valid_but_yields_nothing(self) -> None:
        """No Form 4 in a prefix-matched window is not a failure, and not new data."""
        only_funds = build_feed([], entries=[
            ENTRY_TEMPLATE.format(form="497J", n=2, cik="0000789019", cik_int="789019",
                                  nodash="000078901926000112",
                                  accession="0000789019-26-000112", hh="16", mm="22")])
        collector = self.collector(self.fixture_router(atom=only_funds))
        outcome = collector.poll()
        self.assertTrue(outcome.valid_discovery)
        self.assertEqual(outcome.enqueued, 0)
        self.assertEqual(outcome.result_state, NO_NEW_DATA,
                         "a validated page with no ownership filing is earned NO_NEW_DATA")

    def test_entry_missing_form_type_or_locator_is_an_error(self) -> None:
        missing_category = build_feed([], entries=[
            "\t<entry>\n\t\t<title>4 - X</title>\n"
            "\t\t<link rel='alternate' href='https://www.sec.gov/Archives/edgar/data/1/"
            "900000000126000001/9000000001-26-000001-index.htm'/>\n"
            "\t\t<id>urn:tag:sec.gov,2008:accession-number=9000000001-26-000001</id>\n"
            "\t</entry>"])
        with self.assertRaises(DiscoveryInvalid) as raised:
            parse_discovery_page(missing_category, requested_start=0, requested_count=40)
        self.assertEqual(raised.exception.reason, "discovery_entry_missing_form_type")

        bad_locator = build_feed([], entries=[
            "\t<entry>\n\t\t<title>4 - X</title>\n"
            "\t\t<link rel='alternate' href='https://www.sec.gov/some/other/place.htm'/>\n"
            "\t\t<category term='4' label='form type'/>\n"
            "\t\t<id>urn:tag:sec.gov,2008:accession-number=9000000001-26-000001</id>\n"
            "\t</entry>"])
        with self.assertRaises(DiscoveryInvalid) as raised:
            parse_discovery_page(bad_locator, requested_start=0, requested_count=40)
        self.assertEqual(raised.exception.reason, "discovery_entry_locator_unrecognized")

    def test_disagreeing_accession_identities_are_an_error(self) -> None:
        conflicting = build_feed([], entries=[
            "\t<entry>\n\t\t<title>4 - X</title>\n"
            "\t\t<link rel='alternate' href='https://www.sec.gov/Archives/edgar/data/1/"
            "900000000126000001/9000000001-26-000001-index.htm'/>\n"
            "\t\t<category term='4' label='form type'/>\n"
            "\t\t<id>urn:tag:sec.gov,2008:accession-number=9000000009-26-000009</id>\n"
            "\t</entry>"])
        with self.assertRaises(DiscoveryInvalid) as raised:
            parse_discovery_page(conflicting, requested_start=0, requested_count=40)
        self.assertEqual(raised.exception.reason,
                         "discovery_entry_accession_identity_conflict")

    def test_more_entries_than_requested_breaks_continuation_arithmetic(self) -> None:
        with self.assertRaises(DiscoveryInvalid) as raised:
            parse_discovery_page(build_feed([1, 2, 3]), requested_start=0, requested_count=2)
        self.assertEqual(raised.exception.reason,
                         "discovery_returned_more_entries_than_requested")

    def test_no_new_data_is_earned_and_costs_exactly_one_request(self) -> None:
        """Requirement 5: a no-new-data poll leaves a heartbeat, cheaply."""
        collector = self.collector(self.fixture_router())
        collector.poll()
        collector.drain(max_items=3)
        before = len(self.transport.requested)
        attempts_before = len(collector.store.attempts())

        self.timebase.advance(60)
        outcome = collector.poll()
        self.assertEqual(outcome.result_state, NO_NEW_DATA)
        self.assertTrue(outcome.valid_discovery)
        self.assertEqual(outcome.coverage_state, COVERAGE_COMPLETE)
        self.assertEqual(outcome.new_identities, 0)
        self.assertEqual(len(self.transport.requested) - before, 1,
                         "steady state must cost one discovery request and no refetch")
        # The heartbeat is durable even though nothing new was found.
        self.assertEqual(len(collector.store.attempts()) - attempts_before, 1)
        self.assertEqual(collector.store.attempts()[-1]["attempt_kind"], "DISCOVERY")
        self.assertIsNotNone(collector.store.attempts()[-1]["response_received_at_utc"])


class CoverageTruthfulnessTests(CollectorTestCase):
    def test_pagination_walks_only_as_far_as_the_anchor_under_one_limiter(self) -> None:
        """Requirement 8: overflow is walked, and every page shares the budget."""
        pages = {0: build_feed([10, 9]), 2: build_feed([8, 7]), 4: build_feed([6, 5])}

        def handler(path: str, call: int):
            start = int(path.split("start=")[1].split("&")[0])
            return response(pages[start])

        collector = self.collector(handler, discovery_page_size=2)
        collector.state.cursor_identity_digest = digest_text(synthetic_accession(6))
        collector.save()
        outcome = collector.poll()
        self.assertTrue(outcome.valid_discovery)
        self.assertEqual(outcome.pages_walked, 3, "the anchor is on the third page")
        self.assertEqual(outcome.coverage_state, COVERAGE_COMPLETE)
        self.assertEqual(outcome.result_state, NEW_ITEMS)
        # Only the four entries newer than the anchor; the fifth is behind it.
        self.assertEqual(outcome.enqueued, 4)
        self.assertEqual(collector.budget.load().requests, 3,
                         "every page must spend a slot from the same global budget")
        self.assertEqual(collector.state.open_gaps, [])

    def test_page_budget_exhaustion_is_coverage_unknown_not_complete(self) -> None:
        """A window overflow that cannot be walked out is never complete coverage."""
        def handler(path: str, call: int):
            start = int(path.split("start=")[1].split("&")[0])
            return response(build_feed([100 - start, 99 - start]))

        collector = self.collector(handler, discovery_page_size=2,
                                   max_discovery_pages_per_poll=2)
        collector.state.cursor_identity_digest = digest_text("0000000001-26-000001")
        collector.save()
        outcome = collector.poll()
        self.assertTrue(outcome.valid_discovery, "the pages themselves parsed correctly")
        self.assertEqual(outcome.coverage_state, COVERAGE_UNKNOWN)
        self.assertEqual(outcome.result_state, COVERAGE_UNKNOWN)
        self.assertEqual(outcome.pages_walked, 2)
        gap = collector.state.open_gaps[-1]
        self.assertEqual(gap["kind"], PAGE_BUDGET_EXHAUSTED)
        self.assertEqual(gap["page_start"], 0)
        self.assertEqual(gap["page_range_end"], 4, "the affected page range is recorded")

    def test_missing_intermediate_page_produces_durable_coverage_unknown(self) -> None:
        """Requirement 9: an interrupted page walk records the affected range."""
        def handler(path: str, call: int):
            start = int(path.split("start=")[1].split("&")[0])
            if start == 0:
                return response(build_feed([10, 9]))
            return response(b"<html><body>503</body></html>", status=503,
                            headers={"Content-Type": "text/html"})

        collector = self.collector(handler, discovery_page_size=2)
        collector.state.cursor_identity_digest = digest_text(synthetic_accession(1))
        collector.save()
        outcome = collector.poll()
        self.assertEqual(outcome.coverage_state, COVERAGE_UNKNOWN)
        self.assertEqual(outcome.result_state, SERVER_ERROR)
        self.assertNotEqual(outcome.result_state, NO_NEW_DATA)
        gap = collector.state.open_gaps[-1]
        self.assertEqual(gap["kind"], PAGE_FETCH_FAILED)
        self.assertEqual((gap["page_start"], gap["page_range_end"]), (2, 4))
        # Durable: a fresh collector still sees the unknown coverage.
        self.assertEqual(self.reborn(handler).state.coverage_state, COVERAGE_UNKNOWN)

    def test_cursor_falling_out_of_the_window_is_coverage_unknown(self) -> None:
        collector = self.collector(self.fixture_router())
        collector.state.cursor_identity_digest = digest_text("0000000001-26-000001")
        collector.save()
        outcome = collector.poll()
        self.assertTrue(outcome.valid_discovery)
        self.assertEqual(outcome.coverage_state, COVERAGE_UNKNOWN)
        gap = collector.state.open_gaps[-1]
        self.assertEqual(gap["kind"], CURSOR_FELL_OUT_OF_WINDOW)
        self.assertEqual(gap["from_cursor_identity_digest"],
                         digest_text("0000000001-26-000001"))

    def test_healthy_heartbeat_never_upgrades_unproven_coverage(self) -> None:
        """A successful poll with an open gap stays COVERAGE_UNKNOWN."""
        collector = self.collector(self.fixture_router())
        collector.poll()
        collector.drain(max_items=3)
        self.assertEqual(collector.state.coverage_state, COVERAGE_COMPLETE)
        # An unrelated gap is discovered, for instance by reconciliation.
        collector._open_gap(DAILY_INDEX_GAP, {"day": "2026-09-17",
                                              "interval_start": "2026-09-17",
                                              "interval_end": "2026-09-17"})
        self.assertEqual(collector.state.coverage_state, COVERAGE_UNKNOWN)
        self.timebase.advance(60)
        outcome = collector.poll()
        self.assertEqual(outcome.result_state, COVERAGE_UNKNOWN)
        self.assertEqual(outcome.coverage_state, COVERAGE_UNKNOWN,
                         "liveness is not coverage: the gap is still open")
        self.assertEqual(collector.liveness(), RUNNING)

    def test_restart_during_pagination_is_unknown_then_resolved_by_proof(self) -> None:
        """A partial walk cannot claim its range; a later proof resolves it."""
        pages = {0: build_feed([10, 9]), 2: build_feed([8, 7])}

        def handler(path: str, call: int):
            start = int(path.split("start=")[1].split("&")[0])
            return response(pages[start])

        collector = self.collector(handler, discovery_page_size=2)
        # A poll that died after its first page, exactly as it is left on disk.
        collector.state.active_poll = {
            "poll_id": "interrupted01", "started_at_utc": self.timebase.now_iso(),
            "pages": [{"page_start": 0, "raw_object_sha256": None, "page_full": True,
                       "next_start": 2}],
            "continuity": False, "closed": False, "task_ids": [],
            "newest_identity_digest": None, "newest_feed_updated": None}
        collector.state.cursor_identity_digest = digest_text(synthetic_accession(7))
        collector.save()

        restarted = self.reborn(handler, discovery_page_size=2)
        self.assertIsNotNone(restarted.state.active_poll)
        outcome = restarted.poll()
        interrupted = [gap for gap in restarted.state.resolved_gaps
                       if gap["kind"] == PAGINATION_INTERRUPTED]
        self.assertEqual(len(interrupted), 1, "the interrupted range was recorded")
        self.assertEqual(interrupted[0]["page_start"], 2)
        self.assertEqual(interrupted[0]["resolution"], "continuity re-established")
        self.assertEqual(outcome.coverage_state, COVERAGE_COMPLETE)
        self.assertEqual(restarted.state.open_gaps, [])
        self.assertIsNone(restarted.state.active_poll)

    def test_restart_during_pagination_stays_unknown_when_nothing_proves_it(self) -> None:
        def handler(path: str, call: int):
            return response(b"<html>down</html>", status=503,
                            headers={"Content-Type": "text/html"})

        collector = self.collector(handler)
        collector.state.active_poll = {
            "poll_id": "interrupted02", "started_at_utc": self.timebase.now_iso(),
            "pages": [{"page_start": 0, "raw_object_sha256": None, "page_full": True,
                       "next_start": 40}],
            "continuity": False, "closed": False, "task_ids": [],
            "newest_identity_digest": None, "newest_feed_updated": None}
        collector.save()
        outcome = self.reborn(handler).poll()
        self.assertEqual(outcome.coverage_state, COVERAGE_UNKNOWN)
        self.assertIn(PAGINATION_INTERRUPTED,
                      [gap["kind"] for gap in self.reborn(handler).state.open_gaps])


class ReconciliationTests(CollectorTestCase):
    def test_daily_index_confirms_coverage_when_everything_expected_was_captured(self) -> None:
        index = (FIXTURES / "master.20260917.idx").read_bytes()
        atom = build_feed([], entries=[
            ENTRY_TEMPLATE.format(form="4", n=1, cik="0000320193", cik_int="320193",
                                  nodash="000032019326000044",
                                  accession="0000320193-26-000044", hh="10", mm="00"),
            ENTRY_TEMPLATE.format(form="4", n=2, cik="0000789019", cik_int="789019",
                                  nodash="000078901926000111",
                                  accession="0000789019-26-000111", hh="09", mm="30")])
        collector = self.collector(self.fixture_router(atom=atom, index=index))
        collector.poll()
        collector.drain(max_items=2)
        self.assertEqual(collector.state.coverage_state, COVERAGE_COMPLETE)
        outcome = collector.reconcile(date(2026, 9, 17))
        self.assertTrue(outcome["reconciled"])
        self.assertIsNone(outcome["gap_id"])
        self.assertIn("2026-09-17", collector.state.reconciled_days)
        self.assertEqual(collector.state.coverage_state, COVERAGE_COMPLETE)

    def test_daily_index_gap_is_detected_and_keeps_identities_restricted(self) -> None:
        index = (FIXTURES / "master.20260917.idx").read_bytes()
        collector = self.collector(self.fixture_router(index=index))
        outcome = collector.reconcile(date(2026, 9, 17))
        self.assertFalse(outcome["reconciled"])
        self.assertIsNotNone(outcome["gap_id"])
        self.assertEqual(collector.state.coverage_state, COVERAGE_UNKNOWN)
        gap = collector.state.open_gaps[-1]
        self.assertEqual(gap["kind"], DAILY_INDEX_GAP)
        self.assertEqual((gap["interval_start"], gap["interval_end"]),
                         ("2026-09-17", "2026-09-17"))
        # The expected-but-missing identities exist, in the restricted tier only.
        restricted = (self.paths.sec_restricted / "reconciliation.jsonl").read_text()
        self.assertIn("0000320193-26-000044", restricted)
        safe = "\n".join(path.read_text(encoding="utf-8")
                         for path in self.paths.sec_operator_internal_journals()
                         if path.exists())
        self.assertNotIn("0000320193-26-000044", safe)

    def test_unavailable_or_invalid_daily_index_never_confirms_coverage(self) -> None:
        collector = self.collector(self.fixture_router(index=None))
        outcome = collector.reconcile(date(2026, 9, 17))
        self.assertFalse(outcome["reconciled"])
        self.assertNotIn("2026-09-17", collector.state.reconciled_days)
        self.assertIn("2026-09-17", collector.state.unreconciled_days)
        self.assertEqual(collector.state.open_gaps[-1]["kind"], DAILY_INDEX_UNAVAILABLE)

        html = (FIXTURES / "edgar_error_page.html").read_bytes()
        other = self.collector(self.fixture_router(index=html))
        result = other.reconcile(date(2026, 9, 17))
        self.assertFalse(result["reconciled"])
        self.assertEqual(result["error_class"], "html_page_returned_for_daily_index")

    def test_daily_index_parser_rejects_shapes_it_cannot_account_for(self) -> None:
        day = date(2026, 9, 17)
        cases = {
            b"": "empty_daily_index_body",
            b"header only, no separator": "daily_index_missing_header_separator",
            b"CIK|Name\n-----\n": "daily_index_contained_no_rows",
            b"CIK|Name\n-----\n320193|X|4\n": "daily_index_row_shape_unexpected",
            b"CIK|Name\n-----\n320193|X|4|2026-09-17|edgar/data/320193/nope.txt\n":
                "daily_index_row_missing_accession",
        }
        for body, expected in cases.items():
            with self.subTest(expected=expected):
                with self.assertRaises(DiscoveryInvalid) as raised:
                    parse_daily_index(body, day)
                self.assertEqual(raised.exception.reason, expected)

    def test_reconciliation_targets_the_oldest_unreconciled_closed_weekday(self) -> None:
        collector = self.collector(self.fixture_router())
        collector.state.bootstrap_started_at_utc = "2026-09-16T12:00:00+00:00"
        collector.save()
        self.assertEqual(collector.reconciliation_due(), date(2026, 9, 16))
        collector.state.reconciled_days.append("2026-09-16")
        collector.save()
        # 2026-09-17 is a Thursday; today (the 18th) is not yet settled.
        self.assertEqual(collector.reconciliation_due(), date(2026, 9, 17))
        collector.state.reconciled_days.append("2026-09-17")
        collector.save()
        self.assertIsNone(collector.reconciliation_due())

    def test_one_accession_listed_once_per_filer_enqueues_one_task(self) -> None:
        """EDGAR lists a Form 4 once per filer; identity is what deduplicates.

        Observed on the first live probe: a 40-entry page carried 19 distinct
        accessions, so entry position would have queued each filing twice.
        """
        repeated = build_feed([], entries=[
            ENTRY_TEMPLATE.format(form="4", n=1, cik="0000320193", cik_int="320193",
                                  nodash="000032019326000045",
                                  accession="0000320193-26-000045", hh="16", mm="31"),
            ENTRY_TEMPLATE.format(form="4", n=2, cik="0001214156", cik_int="1214156",
                                  nodash="000032019326000045",
                                  accession="0000320193-26-000045", hh="16", mm="31"),
            ENTRY_TEMPLATE.format(form="4", n=3, cik="0000789019", cik_int="789019",
                                  nodash="000078901926000112",
                                  accession="0000789019-26-000112", hh="16", mm="22")])
        collector = self.collector(self.fixture_router(atom=repeated))
        outcome = collector.poll()
        self.assertEqual(outcome.enqueued, 2, "two distinct accessions, three entries")
        identities = {task["identity_digest"] for task in collector.state.pending_tasks}
        self.assertEqual(len(identities), len(collector.state.pending_tasks))
        results = collector.drain(max_items=5)
        self.assertEqual([item["result_state"] for item in results], [CAPTURED_OK] * 2)
        self.assertEqual(collector.state.pending_tasks, [])


# ---------------------------------------------------------------------------
# Request-control behaviour under adverse responses
# ---------------------------------------------------------------------------

class RequestControlTests(CollectorTestCase):
    def test_429_enters_rate_limit_backoff_and_honours_retry_after(self) -> None:
        """Requirement 11: 429 stops draining and respects the authoritative wait."""
        collector = self.collector(lambda path, call: response(
            b"slow down", status=429, headers={"Retry-After": "600",
                                               "Content-Type": "text/plain"}))
        outcome = collector.poll()
        self.assertEqual(outcome.result_state, RATE_LIMITED)
        self.assertNotEqual(outcome.result_state, NO_NEW_DATA)
        self.assertAlmostEqual(collector.cooldown_remaining(), 600.0, delta=1.0,
                               msg="Retry-After above the policy floor must win")
        self.assertEqual(collector.budget.load().cooldown_reason, "http_429_rate_limited")
        self.assertEqual(collector.store.attempts()[-1]["retry_after_seconds"], 600.0)
        # Ordinary draining stops immediately: no further request is made.
        before = len(self.transport.requested)
        self.assertFalse(collector.poll_due())
        self.assertEqual(collector.poll().result_state, COOLDOWN_SUPPRESSED)
        self.assertEqual(len(self.transport.requested), before)

    def test_429_without_retry_after_falls_back_to_the_policy_floor(self) -> None:
        collector = self.collector(lambda path, call: response(b"x", status=429))
        collector.poll()
        self.assertAlmostEqual(collector.cooldown_remaining(),
                               self.policy().rate_limit_cooldown_seconds, delta=1.0)

    def test_403_does_not_hot_loop_and_records_a_blocked_state(self) -> None:
        """Requirement 12: an access-control 403 backs off hard, never spins."""
        html = (FIXTURES / "edgar_error_page.html").read_bytes()
        collector = self.collector(lambda path, call: response(
            html, status=403, headers={"Content-Type": "text/html"}))
        outcome = collector.poll()
        self.assertEqual(outcome.result_state, ACCESS_FORBIDDEN)
        self.assertAlmostEqual(collector.cooldown_remaining(),
                               self.policy().forbidden_cooldown_seconds, delta=1.0)
        self.assertIn("403", collector.state.blocked_reason or "")
        requests_after_first = len(self.transport.requested)
        for _ in range(6):
            collector.poll()
            collector.drain(max_items=3)
        self.assertEqual(len(self.transport.requested), requests_after_first,
                         "a 403 must not be retried in a loop")
        state, detail = collector.component_state()
        self.assertEqual(state, "BLOCKED")
        self.assertIn("cooldown", detail)

    def test_timeout_and_5xx_walk_the_bounded_backoff_ladder(self) -> None:
        """Requirement 10: transient failures back off, bounded, with jitter."""
        collector = self.collector(lambda path, call: response(b"oops", status=503))
        ladder = self.policy().backoff_schedule_seconds
        observed = []
        for _ in range(7):
            outcome = collector.poll()
            self.assertEqual(outcome.result_state, SERVER_ERROR)
            observed.append(collector.cooldown_remaining())
            # Let the cooldown expire so the next attempt is permitted.
            self.timebase.advance(collector.cooldown_remaining() + 61)
        for index, value in enumerate(observed):
            base = ladder[min(index, len(ladder) - 1)]
            self.assertGreaterEqual(value, base * 0.7)
            self.assertLessEqual(value, base * 1.3)
        self.assertLessEqual(observed[-1], ladder[-1] * 1.3, "the ladder is bounded")

    def test_a_successful_poll_resets_the_backoff_ladder(self) -> None:
        state = {"fail": True}

        def handler(path: str, call: int):
            if state["fail"]:
                return response(b"oops", status=503)
            return response((FIXTURES / "latest_form4_page.atom").read_bytes())

        collector = self.collector(handler)
        collector.poll()
        self.assertGreater(collector.budget.load().backoff_step, 0)
        self.timebase.advance(collector.cooldown_remaining() + 61)
        state["fail"] = False
        collector.poll()
        self.assertEqual(collector.budget.load().backoff_step, 0)

    def test_hung_request_leaves_a_diagnosable_liveness_state(self) -> None:
        """Requirement 20: a blocked request is diagnosable, never a silent stall."""
        collector = self.collector(lambda path, call: SecTransportError(
            "read_timeout:TimeoutError", DEADLINE_EXCEEDED_OUTCOME))
        outcome = collector.poll()
        self.assertEqual(outcome.result_state, HUNG_REQUEST)
        self.assertNotEqual(outcome.result_state, NO_NEW_DATA)
        self.assertTrue(outcome.heartbeat_durable)
        attempt = collector.store.attempts()[-1]
        self.assertEqual(attempt["result_state"], HUNG_REQUEST)
        self.assertEqual(attempt["transfer_outcome"], DEADLINE_EXCEEDED_OUTCOME)
        self.assertEqual(attempt["error_class"], "read_timeout:TimeoutError")
        self.assertIsNone(attempt["response_received_at_utc"],
                          "no response was received, so no receipt time is invented")
        self.assertEqual(collector.liveness(), RUNNING,
                         "the collector is alive; the request is what failed")
        self.assertGreater(collector.cooldown_remaining(), 0)

    def test_truncated_transfer_never_becomes_a_capture(self) -> None:
        """Requirement 18, at the collector level."""
        body = (FIXTURES / "form4_submission.txt").read_bytes()[:400]

        def handler(path: str, call: int):
            if path.startswith("/cgi-bin"):
                return response((FIXTURES / "latest_form4_page.atom").read_bytes())
            return response(body, headers={"Content-Length": "9999",
                                           "Content-Type": "text/plain"},
                            transfer_outcome=TRUNCATED)

        collector = self.collector(handler)
        collector.poll()
        results = collector.drain(max_items=1)
        self.assertEqual(results[0]["result_state"], INCOMPLETE_TRANSFER)
        self.assertEqual(collector.store.envelopes(), [],
                         "an incomplete transfer may not be acknowledged")
        self.assertEqual(len(collector.state.pending_tasks), 3,
                         "the task stays queued for a safe retry")
        attempt = collector.store.attempts()[-1]
        self.assertIsNotNone(attempt["incomplete_object_sha256"])
        self.assertIsNone(attempt["raw_object_sha256"])
        self.assertFalse(collector.store.has_object(digest_bytes(body)))
        self.assertTrue(collector.store.incomplete_path(digest_bytes(body)).exists())

    def test_compressed_discovery_and_filing_hash_the_wire_bytes(self) -> None:
        """Requirement 17, at the collector level: the gzip path the SEC actually uses."""
        atom = gzip.compress((FIXTURES / "latest_form4_page.atom").read_bytes())
        submission = gzip.compress((FIXTURES / "form4_submission.txt").read_bytes())

        def handler(path: str, call: int):
            body = atom if path.startswith("/cgi-bin") else submission
            return response(body, headers={"Content-Encoding": "gzip",
                                           "Content-Length": str(len(body))})

        collector = self.collector(handler)
        outcome = collector.poll()
        self.assertTrue(outcome.valid_discovery, "a gzip body must parse after decoding")
        self.assertEqual(outcome.discovery_object_sha256, digest_bytes(atom),
                         "the stored hash describes the compressed wire bytes")
        results = collector.drain(max_items=1)
        self.assertEqual(results[0]["raw_object_sha256"], digest_bytes(submission))
        self.assertEqual(collector.store.read_object(results[0]["raw_object_sha256"]),
                         submission)
        envelope = collector.store.envelopes()[0]
        self.assertEqual(envelope["content_encoding"], "gzip")
        self.assertEqual(envelope["byte_length"], len(submission))

    def test_permanent_4xx_is_recorded_without_escalating_cooldown(self) -> None:
        collector = self.collector(lambda path, call: response(b"gone", status=404))
        outcome = collector.poll()
        self.assertEqual(outcome.result_state, PERMANENT_CLIENT_ERROR)
        self.assertEqual(collector.cooldown_remaining(), 0.0,
                         "a permanent 4xx is journalled, not escalated")
        self.assertEqual(collector.store.attempts()[-1]["error_class"], "http_404")

    def test_no_new_data_request_failed_and_did_not_run_are_distinguishable(self) -> None:
        """The three cases a reviewer must be able to separate afterwards."""
        collector = self.collector(self.fixture_router(), enable=False)
        self.assertEqual(collector.liveness(), NEVER_RAN)
        self.assertEqual(collector.store.attempts(), [])

        collector.enable()
        collector.poll()
        collector.drain(max_items=3)
        self.timebase.advance(60)
        quiet = collector.poll()
        self.assertEqual(quiet.result_state, NO_NEW_DATA)

        self.timebase.advance(60)
        broken = self.collector(lambda path, call: SecTransportError("request_failed:OSError"))
        failed = broken.poll()
        self.assertEqual(failed.result_state, REQUEST_FAILED)

        states = [record["result_state"] for record in broken.store.attempts()]
        self.assertIn(REQUEST_FAILED, states)
        self.assertEqual(broken.liveness(), RUNNING)
        # A collector that stops asking becomes STALE rather than quietly "fine".
        self.timebase.advance(60 * 60)
        self.assertEqual(broken.liveness(), STALE)


# ---------------------------------------------------------------------------
# Crash boundaries and restart safety
# ---------------------------------------------------------------------------

class _SimulatedCrash(RuntimeError):
    """Stands in for the process dying at one specific commit boundary."""


class CrashBoundaryTests(CollectorTestCase):
    """Requirement 15: every commit boundary is replayable without silent loss.

    Each test kills the collector at one boundary, rebuilds it from disk exactly
    as a restart would, and checks two things: nothing captured disappeared, and
    nothing was silently substituted or acquired twice.
    """

    def setUp(self) -> None:
        super().setUp()
        self.router = self.fixture_router()

    def test_crash_between_discovery_and_queue_rediscovers_rather_than_skips(self) -> None:
        collector = self.collector(self.router)
        original = collector.store.record_locator

        def crash_on_filing_locator(**kwargs):
            if kwargs.get("endpoint_class") == "edgar_archives_submission_text":
                raise _SimulatedCrash("died before the task reached the queue")
            return original(**kwargs)

        collector.store.record_locator = crash_on_filing_locator
        with self.assertRaises(_SimulatedCrash):
            collector.poll()

        restarted = self.reborn(self.router)
        self.assertEqual(restarted.state.pending_tasks, [])
        self.assertIsNone(restarted.state.cursor_identity_digest,
                          "the anchor must not have moved past undiscovered work")
        # The discovery response itself is preserved, and the poll is replayable.
        self.assertTrue(restarted.store.raw_manifest())
        outcome = restarted.poll()
        self.assertEqual(outcome.enqueued, 3, "the same work is rediscovered, not skipped")
        self.assertEqual(len(restarted.store.raw_manifest()), 1,
                         "the identical discovery response deduplicated")

    def test_crash_between_raw_write_and_envelope_replays_safely(self) -> None:
        collector = self.collector(self.router)
        collector.poll()
        collector.store.record_envelope = lambda envelope: (_ for _ in ()).throw(
            _SimulatedCrash("died after the bytes were durable"))
        with self.assertRaises(_SimulatedCrash):
            collector.drain(max_items=1)

        restarted = self.reborn(self.router)
        self.assertEqual(restarted.store.envelopes(), [],
                         "no envelope means the filing was never acknowledged")
        self.assertEqual(len(restarted.state.pending_tasks), 3,
                         "the task is still queued for replay")
        submission = (FIXTURES / "form4_submission.txt").read_bytes()
        self.assertTrue(restarted.store.has_object(digest_bytes(submission)),
                        "bytes already written must survive the crash")
        results = restarted.drain(max_items=1)
        self.assertEqual(results[0]["result_state"], CAPTURED_OK)
        self.assertEqual(len(restarted.store.envelopes()), 1)
        # The replay deduplicated rather than writing a second object.
        matching = [record for record in restarted.store.raw_manifest()
                    if record["raw_object_sha256"] == digest_bytes(submission)]
        self.assertEqual(len(matching), 1, "no duplicate raw object was created")

    def test_crash_between_envelope_and_acknowledgement_costs_no_refetch(self) -> None:
        collector = self.collector(self.router)
        collector.poll()
        collector._drop_task = lambda task: (_ for _ in ()).throw(
            _SimulatedCrash("died after the envelope was durable"))
        with self.assertRaises(_SimulatedCrash):
            collector.drain(max_items=1)
        self.assertEqual(len(collector.store.envelopes()), 1)

        restarted = self.reborn(self.router)
        self.assertEqual(len(restarted.state.pending_tasks), 3)
        before = len(self.transport.requested)
        results = restarted.drain(max_items=1)
        self.assertEqual(results[0]["result_state"], DEDUPLICATED)
        self.assertEqual(results[0]["requests_spent"], 0,
                         "a durable envelope means the filing is never fetched again")
        self.assertEqual(len(self.transport.requested), before)
        self.assertEqual(len(restarted.store.envelopes()), 1,
                         "no second envelope was appended")
        self.assertEqual(len(restarted.state.pending_tasks), 2)

    def test_crash_between_acknowledgement_and_cursor_advance_is_recoverable(self) -> None:
        collector = self.collector(self.router)
        collector.poll()
        collector.drain(max_items=2)
        collector._maybe_advance_cursor = lambda: (_ for _ in ()).throw(
            _SimulatedCrash("died before the cursor moved"))
        with self.assertRaises(_SimulatedCrash):
            collector.drain(max_items=1)

        restarted = self.reborn(self.router)
        self.assertIsNone(restarted.state.cursor_identity_digest,
                          "the cursor did not advance, so nothing was skipped")
        self.assertIsNotNone(restarted.state.pending_cursor_identity_digest)
        before = len(self.transport.requested)
        restarted.drain(max_items=1)
        self.assertEqual(len(self.transport.requested), before,
                         "the acknowledged filing is not fetched again")
        self.assertEqual(restarted.state.pending_tasks, [])
        self.assertEqual(restarted.state.cursor_identity_digest,
                         digest_text("0000320193-26-000045"),
                         "the cursor advances once every task is acknowledged")

    def test_disk_full_during_acquisition_cannot_acknowledge_anything(self) -> None:
        """Requirement 16, at the collector level."""
        collector = self.collector(self.router)
        collector.poll()
        real_put = collector.store.put_object

        def full_disk(body: bytes, *, incomplete: bool = False):
            raise SecStorageFailure("raw object write failed: ENOSPC")

        collector.store.put_object = full_disk
        results = collector.drain(max_items=1)
        self.assertEqual(results[0]["result_state"], STORAGE_FAILED)
        self.assertEqual(collector.store.envelopes(), [])
        self.assertEqual(len(collector.state.pending_tasks), 3,
                         "nothing may be acknowledged when the bytes cannot be stored")
        self.assertEqual(collector.store.attempts()[-1]["result_state"], STORAGE_FAILED)
        self.assertIsNone(collector.store.attempts()[-1]["raw_object_sha256"])

        # Recovery once storage returns: the same task completes normally.
        collector.store.put_object = real_put
        recovered = collector.drain(max_items=1)
        self.assertEqual(recovered[0]["result_state"], CAPTURED_OK)
        self.assertEqual(len(collector.store.envelopes()), 1)

    def test_restart_preserves_append_only_history_and_all_lane_state(self) -> None:
        """Requirement 14: nothing captured disappears, nothing is replaced."""
        collector = self.collector(self.router)
        collector.poll()
        collector.drain(max_items=3)
        collector.budget.enter_cooldown(300.0, "http_429_rate_limited")
        attempts = collector.store.attempts()
        envelopes = collector.store.envelopes()
        manifest = collector.store.raw_manifest()
        cursor = collector.state.cursor_identity_digest
        coverage = collector.state.coverage_state

        restarted = self.reborn(self.router)
        self.assertEqual(restarted.store.attempts(), attempts)
        self.assertEqual(restarted.store.envelopes(), envelopes)
        self.assertEqual(restarted.store.raw_manifest(), manifest)
        self.assertEqual(restarted.state.cursor_identity_digest, cursor)
        self.assertEqual(restarted.state.coverage_state, coverage)
        self.assertEqual(restarted.state.enabled, True)
        self.assertEqual(restarted.store.verify_objects(), [])
        # Requirement 13: the SEC cooldown is still in force after the restart.
        self.assertAlmostEqual(restarted.cooldown_remaining(), 300.0, delta=1.0)
        self.assertFalse(restarted.poll_due())
        state, detail = restarted.component_state()
        self.assertEqual(state, "BLOCKED")


# ---------------------------------------------------------------------------
# Visibility firewall
# ---------------------------------------------------------------------------

class VisibilityFirewallTests(CollectorTestCase):
    """Requirement 19: no interpretable Form-4 content reaches a visible surface."""

    def test_leak_detector_recognises_the_content_it_is_meant_to_catch(self) -> None:
        submission = (FIXTURES / "form4_submission.txt").read_text(encoding="utf-8")
        self.assertTrue(find_leaks(submission), "the detector must flag a real Form 4")
        self.assertIn("accession_number", find_leaks("filing 0000320193-26-000045 arrived"))
        self.assertIn("filing_archive_path",
                      find_leaks("https://www.sec.gov/Archives/edgar/data/1/x.txt"))
        self.assertIn("transaction_field", find_leaks("<transactionCode>P</transactionCode>"))
        self.assertIn("filer_identity_field", find_leaks("<issuerName>ACME</issuerName>"))
        self.assertEqual(find_leaks("coverage COMPLETE, sha256:abc, 2048 bytes"), [])

    def test_no_visible_surface_exposes_captured_form_4_content(self) -> None:
        from quant.clock import QuantSystem
        from quant.status.brief import build_chief_brief
        from quant.status.render import render_status

        collector = self.collector(self.fixture_router(
            index=(FIXTURES / "master.20260917.idx").read_bytes()))
        collector.poll()
        collector.drain(max_items=3)
        collector.reconcile(date(2026, 9, 17))

        system = QuantSystem(self.root)
        system.sec = collector
        system.boot()
        snapshot = system.snapshot()
        surfaces = {
            "status surface": render_status(snapshot),
            "CHIEF_BRIEF.md": build_chief_brief(snapshot),
            "snapshot JSON": json.dumps(snapshot, sort_keys=True, default=str),
            "collector telemetry": json.dumps(collector.telemetry(), sort_keys=True,
                                              default=str),
            "event log": self.paths.events.read_text(encoding="utf-8"),
        }
        for path in self.paths.sec_operator_internal_journals():
            if path.exists():
                surfaces[f"journal {path.name}"] = path.read_text(encoding="utf-8")
        for where, text in surfaces.items():
            with self.subTest(surface=where):
                assert_no_scientific_content(text, where)

        # The content really was captured: it is in the restricted tier only.
        restricted = "\n".join(path.read_text(encoding="utf-8")
                               for path in self.paths.sec_restricted.glob("*.jsonl"))
        self.assertIn("0000320193-26-000045", restricted)
        self.assertTrue(find_leaks(restricted),
                        "the restricted tier is where identity legitimately lives")

    def test_telemetry_publishes_no_filing_counts(self) -> None:
        collector = self.collector(self.fixture_router())
        collector.poll()
        collector.drain(max_items=3)
        telemetry = collector.telemetry()
        # Protocol-mutating actors receive no activity-volume/timing proxy.
        for forbidden in ("work_in_flight", "cursor_identity_digest",
                          "last_attempt_at_utc", "last_capture_at_utc",
                          "next_due_at_utc", "raw_bytes", "requests_spent"):
            self.assertNotIn(forbidden, json.dumps(telemetry))
        self.assertEqual(find_count_proxies(telemetry), [])
        self.assertNotIn("raw_objects", telemetry["storage"])
        self.assertNotIn("pending_tasks", telemetry)
        self.assertNotIn("captures", telemetry)

    def test_exceptions_and_error_classes_never_carry_response_content(self) -> None:
        leaky = (b"<html><body>ACME CORP filing 0000320193-26-000045 "
                 b"<transactionCode>P</transactionCode></body></html>")
        collector = self.collector(lambda path, call: response(
            leaky, headers={"Content-Type": "text/html"}))
        outcome = collector.poll()
        self.assertEqual(find_leaks(outcome.error_class or ""), [])
        self.assertEqual(find_leaks(json.dumps(outcome.to_dict(), default=str)), [])
        assert_no_scientific_content(self.paths.sec_attempts.read_text(encoding="utf-8"),
                                     "attempt journal")
        assert_no_scientific_content(self.paths.events.read_text(encoding="utf-8")
                                     if self.paths.events.exists() else "", "event log")
        # The offending bytes are still preserved as evidence.
        self.assertEqual(collector.store.read_object(digest_bytes(leaky)), leaky)

    def test_discovery_invalid_reason_classes_are_bounded_not_echoed(self) -> None:
        hostile = build_feed([], entries=[
            "\t<entry>\n\t\t<title>4 - X</title>\n"
            "\t\t<link rel='alternate' href='https://www.sec.gov/Archives/edgar/data/1/"
            "900000000126000001/9000000001-26-000001-index.htm'/>\n"
            "\t\t<category term='ACME CORP 0000320193-26-000045 transactionCode' "
            "label='form type'/>\n"
            "\t\t<id>urn:tag:sec.gov,2008:accession-number=9000000001-26-000001</id>\n"
            "\t</entry>"])
        with self.assertRaises(DiscoveryInvalid) as raised:
            parse_discovery_page(hostile, requested_start=0, requested_count=40)
        self.assertEqual(find_leaks(raised.exception.reason), [],
                         "a reason class must not echo arbitrary source text")
        self.assertLessEqual(len(raised.exception.reason), 60)


# ---------------------------------------------------------------------------
# HIDDEN_TRANSPORT_RETRY: one reservation, one request, one attempt id
# ---------------------------------------------------------------------------

class RequestAccountingTests(CollectorTestCase):
    """`P0_ACQUISITION_CRITICAL_FINGERPRINT_V1.md` §6.

    The invariant is structural: the transport cannot send without a permit and
    cannot send twice with one. These tests check that the structure holds on
    the paths the collector actually takes, including every failure path, since
    a failure is exactly where the removed retry used to fire.
    """

    def assert_one_to_one(self, collector, transport) -> None:
        """Requests emitted == budget reservations == distinct durable attempt ids."""
        attempts = collector.store.attempts()
        journalled = [record["attempt_id"] for record in attempts
                      if record["result_state"] != COOLDOWN_SUPPRESSED]
        reservations = collector.budget.load().requests
        self.assertEqual(len(transport.requested), reservations,
                         "an HTTP request was emitted without a budget reservation")
        self.assertEqual(len(transport.requested), len(journalled),
                         "an HTTP request was emitted without a durable attempt id")
        self.assertEqual(len(set(journalled)), len(journalled),
                         "an attempt id was reused across requests")
        self.assertEqual(transport.permits_consumed, journalled,
                         "the permit attempt ids must match the journal, in order")

    def test_transport_refuses_a_second_request_under_one_permit(self) -> None:
        permit = RequestPermit(attempt_id="a1", reserved_at_utc="2026-09-18T00:00:00+00:00",
                               endpoint_class="test")
        permit.consume()
        with self.assertRaises(PermitAlreadySpent):
            permit.consume()

    def test_the_permit_is_spent_even_when_the_request_fails(self) -> None:
        """The removed retry lived exactly here: a failure after the send.

        The permit is consumed before the socket write, so a connection-level
        failure can never be re-sent under the same reservation.
        """
        class ExplodingConnection:
            def request(self, *args, **kwargs):
                raise OSError("connection reset by peer")

            def close(self):
                pass

        transport = SecHttpTransport(self.policy(), timebase=self.timebase)
        transport._connection = ExplodingConnection()
        permit = RequestPermit(attempt_id="a1", reserved_at_utc="t", endpoint_class="test")
        with self.assertRaises(SecTransportError):
            transport.fetch("/cgi-bin/browse-edgar", permit)
        self.assertTrue(permit.spent, "a failed send still consumes its permit")
        self.assertEqual(transport.requests_sent, 1,
                         "exactly one request was attempted, and it is counted")
        with self.assertRaises(PermitAlreadySpent):
            transport.fetch("/cgi-bin/browse-edgar", permit)

    def test_an_idle_connection_is_recycled_before_sending_not_retried_after(self) -> None:
        """The permitted reconnect: no extra request, no hidden retry."""
        transport = SecHttpTransport(self.policy(idle_reuse_seconds=20.0),
                                     timebase=self.timebase)

        class DeadConnection:
            closed = False

            def close(self):
                DeadConnection.closed = True

        transport._connection = DeadConnection()
        transport._connection_last_used = self.timebase.now()
        # Fresh enough to reuse.
        self.timebase.advance(5)
        transport._recycle_if_idle()
        self.assertIsNotNone(transport._connection)
        # Idle past the threshold: replaced before the next send.
        self.timebase.advance(30)
        transport._recycle_if_idle()
        self.assertIsNone(transport._connection)
        self.assertTrue(DeadConnection.closed)
        self.assertEqual(transport.requests_sent, 0,
                         "recycling a connection must not emit a request")

    def test_accounting_holds_across_a_normal_poll_and_drain(self) -> None:
        collector = self.collector(self.fixture_router())
        collector.poll()
        collector.drain(max_items=3)
        self.timebase.advance(60)
        collector.poll()
        self.assert_one_to_one(collector, self.transport)

    def test_accounting_holds_across_every_failure_path(self) -> None:
        """Each adverse response class, driven through the real collector path."""
        cases = {
            "transport_error": lambda path, call: SecTransportError("request_failed:OSError"),
            "hung": lambda path, call: SecTransportError("read_timeout:TimeoutError",
                                                         DEADLINE_EXCEEDED_OUTCOME),
            "server_error": lambda path, call: response(b"oops", status=503),
            "rate_limited": lambda path, call: response(b"x", status=429),
            "forbidden": lambda path, call: response(b"x", status=403),
            "permanent": lambda path, call: response(b"x", status=404),
            "html_200": lambda path, call: response(
                b"<html><body>error</body></html>", headers={"Content-Type": "text/html"}),
            "truncated": lambda path, call: response(
                b"partial", headers={"Content-Length": "9999"}, transfer_outcome=TRUNCATED),
        }
        for name, handler in cases.items():
            with self.subTest(case=name):
                self.setUp()
                collector = self.collector(handler)
                collector.poll()
                # Push past any cooldown and try again, so a retry-shaped path
                # would show up as an extra request if one existed.
                self.timebase.advance(collector.cooldown_remaining() + 120)
                collector.poll()
                self.assert_one_to_one(collector, self.transport)

    def test_accounting_holds_while_paginating_and_reconciling(self) -> None:
        pages = {0: build_feed([10, 9]), 2: build_feed([8, 7]), 4: build_feed([6, 5])}

        def handler(path: str, call: int):
            if path.startswith("/Archives/edgar/daily-index"):
                return response((FIXTURES / "master.20260917.idx").read_bytes(),
                                headers={"Content-Type": "text/plain"})
            if path.startswith("/cgi-bin"):
                start = int(path.split("start=")[1].split("&")[0])
                return response(pages[start])
            return response((FIXTURES / "form4_submission.txt").read_bytes(),
                            headers={"Content-Type": "text/plain"})

        collector = self.collector(handler, discovery_page_size=2)
        collector.state.cursor_identity_digest = digest_text(synthetic_accession(6))
        collector.save()
        collector.poll()
        collector.drain(max_items=4)
        collector.reconcile(date(2026, 9, 17))
        self.assert_one_to_one(collector, self.transport)

    def test_a_cooldown_suppressed_attempt_spends_no_reservation_and_no_request(self) -> None:
        collector = self.collector(self.fixture_router())
        collector.budget.enter_cooldown(300.0, "http_429_rate_limited")
        before = len(self.transport.requested)
        outcome = collector.poll()
        self.assertEqual(outcome.result_state, COOLDOWN_SUPPRESSED)
        self.assertEqual(len(self.transport.requested), before,
                         "a suppressed attempt must not reach the network")
        # It still leaves a durable record, so the audit sees why nothing went out.
        self.assertEqual(collector.store.attempts()[-1]["result_state"], COOLDOWN_SUPPRESSED)
        self.assertIsNone(collector.store.attempts()[-1]["http_status"])
        self.assert_one_to_one(collector, self.transport)

    def test_the_transport_has_no_retry_construct_left(self) -> None:
        """A source-level guard: the defect was a nested re-send, so ban the shape."""
        source = (ROOT / "src" / "quant" / "dataplane" / "sec" / "transport.py").read_text()
        body = source[source.index("def _fetch_once"):]
        self.assertEqual(body.count("connection.request("), 1,
                         "transport must emit at most one request per fetch")
        self.assertEqual(body.count("getresponse("), 1)


# ---------------------------------------------------------------------------
# INCOMPLETE_CRITICAL_POLICY_SERIALIZATION and the V1 fingerprint
# ---------------------------------------------------------------------------

class PolicyClassificationTests(SecCaptureTestCase):
    """`P0_ACQUISITION_CRITICAL_FINGERPRINT_V1.md` §4, completeness invariant."""

    def test_classification_covers_every_policy_field_exactly_once(self) -> None:
        fields = policy_field_names()
        noncritical = frozenset(EXPLICITLY_NONCRITICAL)
        self.assertEqual(INCLUDE_CANONICAL | TRANSFORM_CANONICAL | noncritical, fields,
                         "POLICY_FIELD_SET must equal the union of the three sets")
        self.assertEqual(INCLUDE_CANONICAL & TRANSFORM_CANONICAL, frozenset())
        self.assertEqual(INCLUDE_CANONICAL & noncritical, frozenset())
        self.assertEqual(TRANSFORM_CANONICAL & noncritical, frozenset())
        verify_policy_classification()

    def test_every_noncritical_field_carries_a_frozen_rationale(self) -> None:
        for name, rationale in EXPLICITLY_NONCRITICAL.items():
            with self.subTest(field=name):
                self.assertGreater(len(rationale), 120,
                                   "a non-critical claim needs an argued rationale")
                self.assertIn("runtime", rationale.lower())

    def test_an_unclassified_policy_field_blocks_fingerprint_generation(self) -> None:
        """The defence the governance asks for: fail generation, not just tests."""
        original = dataclasses.fields(SecAccessPolicy)
        added = dataclasses.field(default=1.0)
        added.name = "future_unclassified_knob"
        added.type = float

        def with_extra_field(cls):
            return tuple(list(original) + [added])

        with mock.patch.object(dataclasses, "fields", side_effect=with_extra_field):
            with self.assertRaises(UnclassifiedPolicyField) as raised:
                verify_policy_classification()
            self.assertIn("future_unclassified_knob", str(raised.exception))
            with self.assertRaises(UnclassifiedPolicyField):
                canonical_policy(self.policy())
            with self.assertRaises(UnclassifiedPolicyField):
                acquisition_critical_fingerprint(self.policy(), root=ROOT)

    def test_a_classification_for_a_removed_field_is_also_rejected(self) -> None:
        with mock.patch.object(fingerprint_module, "INCLUDE_CANONICAL",
                               INCLUDE_CANONICAL | {"field_that_no_longer_exists"}):
            with self.assertRaises(PolicyClassificationInvalid):
                verify_policy_classification()

    def test_overlapping_classifications_are_rejected(self) -> None:
        with mock.patch.object(fingerprint_module, "TRANSFORM_CANONICAL",
                               TRANSFORM_CANONICAL | {"discovery_poll_seconds"}):
            with self.assertRaises(PolicyClassificationInvalid):
                verify_policy_classification()

    def test_canonical_policy_carries_the_fields_to_dict_omitted(self) -> None:
        """The concrete defect: to_dict() could not serve as the fingerprint source."""
        canonical = canonical_policy(self.policy())
        telemetry = self.policy().to_dict()
        for omitted in ("filings_per_drain", "accept_encoding", "max_response_bytes"):
            with self.subTest(field=omitted):
                self.assertIn(omitted, canonical)
                self.assertNotIn(omitted, telemetry,
                                 "test guards the reason a dedicated serializer exists")

    def test_requester_identity_is_bound_but_never_plaintext(self) -> None:
        canonical = canonical_policy(self.policy())
        self.assertNotIn("user_agent", canonical)
        binding = canonical["requester_identity_binding"]
        self.assertTrue(binding.startswith("sha256:"))
        self.assertNotIn("example.com", binding)
        self.assertNotIn("Quant", binding)
        # Different declared identity, different binding.
        other = SecAccessPolicy(user_agent="Other Requester other@example.org")
        self.assertNotEqual(canonical_policy(other)["requester_identity_binding"], binding)


class FingerprintTests(SecCaptureTestCase):
    """`P0_ACQUISITION_CRITICAL_FINGERPRINT_V1.md` §8, before-t0 acceptance."""

    def fingerprint(self, **overrides) -> str:
        return acquisition_critical_fingerprint(self.policy(**overrides), root=ROOT)

    def test_two_identical_builds_produce_the_same_fingerprint(self) -> None:
        self.assertEqual(self.fingerprint(), self.fingerprint())
        # And through a whole separate manifest construction.
        first = build_manifest(self.policy(), root=ROOT)
        second = build_manifest(self.policy(), root=ROOT)
        self.assertEqual(canonical_json(first), canonical_json(second))
        self.assertEqual(compute_fingerprint(first), compute_fingerprint(second))

    def test_the_manifest_contains_every_mandated_v1_member(self) -> None:
        manifest = build_manifest(self.policy(), root=ROOT)
        self.assertEqual(manifest["schema"], FINGERPRINT_SCHEMA_VERSION)
        # Code-semantic roots, all of them, per the frozen module list.
        for module in ACQUISITION_CRITICAL_MODULES:
            self.assertIn(module, manifest["code"])
            self.assertTrue(manifest["code"][module].startswith("sha256:"))
        self.assertIn("src/quant/clock.py", manifest["code"],
                      "clock.py is fingerprint-critical in full until the "
                      "acquisition scheduling path is isolated")
        # Every mandated runtime value.
        for value in ("discovery_poll_seconds", "max_concurrency", "max_requests_per_second",
                      "allow_burst", "connect_timeout_seconds", "read_timeout_seconds",
                      "total_deadline_seconds", "backoff_schedule_seconds", "jitter_ratio",
                      "rate_limit_cooldown_seconds", "forbidden_cooldown_seconds",
                      "discovery_page_size", "max_discovery_pages_per_poll",
                      "filings_per_drain", "accept_encoding", "max_response_bytes",
                      "requester_identity_binding"):
            self.assertIn(value, manifest["policy"])
        self.assertIn("host", manifest["request_shape"])
        self.assertIn("query_construction_version", manifest["request_shape"])
        self.assertIn("service_definition_digests", manifest["supervisor"])
        self.assertIn("restart_policy", manifest["supervisor"])

    def test_changing_a_timeout_changes_the_fingerprint(self) -> None:
        baseline = self.fingerprint()
        self.assertNotEqual(self.fingerprint(connect_timeout_seconds=11.0), baseline)
        self.assertNotEqual(self.fingerprint(read_timeout_seconds=21.0), baseline)
        self.assertNotEqual(self.fingerprint(total_deadline_seconds=61.0), baseline)
        self.assertNotEqual(self.fingerprint(idle_reuse_seconds=30.0), baseline)

    def test_changing_a_retry_or_backoff_rule_changes_the_fingerprint(self) -> None:
        baseline = self.fingerprint()
        self.assertNotEqual(
            self.fingerprint(backoff_schedule_seconds=(5.0, 15.0, 60.0, 300.0, 1800.0)),
            baseline)
        self.assertNotEqual(self.fingerprint(jitter_ratio=0.1), baseline)
        self.assertNotEqual(self.fingerprint(rate_limit_cooldown_seconds=600.0), baseline)
        self.assertNotEqual(self.fingerprint(forbidden_cooldown_seconds=7200.0), baseline)

    def test_changing_discovery_or_coverage_settings_changes_the_fingerprint(self) -> None:
        baseline = self.fingerprint()
        self.assertNotEqual(self.fingerprint(discovery_page_size=41), baseline)
        self.assertNotEqual(self.fingerprint(max_discovery_pages_per_poll=11), baseline)
        self.assertNotEqual(self.fingerprint(filings_per_drain=2), baseline)
        self.assertNotEqual(self.fingerprint(discovery_poll_seconds=30.0), baseline)

    def test_changing_any_critical_policy_field_changes_the_fingerprint(self) -> None:
        """Sweep every INCLUDE_CANONICAL field rather than a chosen sample."""
        baseline = self.fingerprint()
        mutations = {
            "discovery_poll_seconds": 90.0, "max_concurrency": 2,
            "max_requests_per_second": 1.0, "allow_burst": True,
            "connect_timeout_seconds": 12.0, "read_timeout_seconds": 25.0,
            "idle_reuse_seconds": 45.0, "total_deadline_seconds": 90.0,
            "backoff_schedule_seconds": (1.0, 2.0), "jitter_ratio": 0.5,
            "rate_limit_cooldown_seconds": 301.0, "forbidden_cooldown_seconds": 3601.0,
            "discovery_page_size": 20, "max_discovery_pages_per_poll": 3,
            "filings_per_drain": 5, "accept_encoding": "identity",
            "max_response_bytes": 1024,
        }
        self.assertEqual(set(mutations), set(INCLUDE_CANONICAL),
                         "every canonically included field needs a mutation case")
        for name, value in mutations.items():
            with self.subTest(field=name):
                if name in {"max_concurrency", "allow_burst"}:
                    # Those alternative policies are no longer implementable:
                    # P0 structurally supports one concurrent request/no burst.
                    with self.assertRaises(SecPolicyNotConfigured):
                        self.policy(**{name: value})
                else:
                    self.assertNotEqual(self.fingerprint(**{name: value}), baseline)

    def test_changing_the_declared_sec_identity_changes_the_fingerprint(self) -> None:
        other = SecAccessPolicy(user_agent="Different Requester ops@example.org")
        self.assertNotEqual(acquisition_critical_fingerprint(other, root=ROOT),
                            self.fingerprint())

    def test_changing_acquisition_code_changes_the_fingerprint(self) -> None:
        """A module edit must move the fingerprint even with identical config."""
        import shutil, tempfile
        with tempfile.TemporaryDirectory() as directory:
            mirror = Path(directory) / "repo"
            shutil.copytree(ROOT / "src", mirror / "src")
            shutil.copytree(ROOT / "deploy", mirror / "deploy")
            shutil.copytree(ROOT / "scripts", mirror / "scripts")
            before = acquisition_critical_fingerprint(self.policy(), root=mirror)
            target = mirror / "src" / "quant" / "dataplane" / "sec" / "collector.py"
            target.write_text(target.read_text() + "\n# acquisition semantics changed\n")
            self.assertNotEqual(acquisition_critical_fingerprint(self.policy(), root=mirror),
                                before)

    def test_changing_the_supervisor_restart_policy_changes_the_fingerprint(self) -> None:
        import shutil, tempfile
        with tempfile.TemporaryDirectory() as directory:
            mirror = Path(directory) / "repo"
            shutil.copytree(ROOT / "src", mirror / "src")
            shutil.copytree(ROOT / "deploy", mirror / "deploy")
            shutil.copytree(ROOT / "scripts", mirror / "scripts")
            before = acquisition_critical_fingerprint(self.policy(), root=mirror)
            unit = mirror / "deploy" / "quant-sec-capture.service"
            unit.write_text(unit.read_text().replace("RestartSec=15", "RestartSec=120"))
            self.assertNotEqual(acquisition_critical_fingerprint(self.policy(), root=mirror),
                                before)

    def test_current_runtime_tree_change_moves_conservative_fingerprint(self) -> None:
        """Before t0, widen rather than guess which import-time code is harmless."""
        import shutil, tempfile
        with tempfile.TemporaryDirectory() as directory:
            mirror = Path(directory) / "repo"
            shutil.copytree(ROOT / "src", mirror / "src")
            shutil.copytree(ROOT / "deploy", mirror / "deploy")
            shutil.copytree(ROOT / "scripts", mirror / "scripts")
            before = acquisition_critical_fingerprint(self.policy(), root=mirror)
            # A downstream parser/normalizer, and an edit to a non-acquisition plane.
            (mirror / "src" / "quant" / "dataplane" / "form4_parser.py").write_text(
                "'''Downstream parser, strictly after immutable raw storage.'''\n")
            desk = mirror / "src" / "quant" / "desk" / "desk.py"
            desk.write_text(desk.read_text() + "\n# unrelated desk change\n")
            self.assertNotEqual(
                acquisition_critical_fingerprint(self.policy(), root=mirror), before,
                "current service topology conservatively freezes the Python runtime tree")

    def test_recording_a_newer_sec_documentation_revision_does_not_reset_t0(self) -> None:
        """The frozen rationale for the one EXPLICITLY_NONCRITICAL field, tested."""
        baseline = self.fingerprint()
        restated = SecAccessPolicy(
            user_agent=USER_AGENT,
            sources=({"url": "https://www.sec.gov/os/webmaster-faq",
                      "reviewed_or_updated": "2027-01-01",
                      "consulted_at_utc": "2027-01-02"},))
        self.assertEqual(acquisition_critical_fingerprint(restated, root=ROOT), baseline)
        # But an actual limit changed in response to that re-check does reset it.
        self.assertNotEqual(self.fingerprint(max_requests_per_second=1.5), baseline)

    def test_the_fingerprint_is_deterministic_json_not_dict_order(self) -> None:
        manifest = build_manifest(self.policy(), root=ROOT)
        shuffled = dict(reversed(list(manifest.items())))
        self.assertEqual(compute_fingerprint(shuffled), compute_fingerprint(manifest))


# ---------------------------------------------------------------------------
# Scheduler and lifecycle provenance
# ---------------------------------------------------------------------------

class SchedulerProvenanceTests(CollectorTestCase):
    """`BLUE_P0_RAW_CAPTURE_CHECKPOINT_ADDENDUM_2026-09-18.md §5.2`."""

    def test_every_cadence_changing_event_records_a_transition(self) -> None:
        collector = self.collector(self.fixture_router(), enable=False)
        self.assertEqual(collector.scheduler.all(), [])
        collector.enable()
        collector.poll()
        collector.drain(max_items=3)
        causes = [record["cause"] for record in collector.scheduler.all()]
        for expected in (LANE_ENABLED, POLL_COMPLETED, DRAIN_COMPLETED):
            self.assertIn(expected, causes)

    def test_each_transition_carries_the_full_mandated_payload(self) -> None:
        collector = self.collector(self.fixture_router())
        collector.poll()
        for record in collector.scheduler.all():
            with self.subTest(transition=record["transition_id"]):
                self.assertIn(record["state"], SCHEDULER_STATES)
                self.assertTrue(record["recorded_at_utc"])
                self.assertTrue(record["cause"])
                self.assertTrue(record["acquisition_critical_fingerprint"].startswith("sha256:"))
                self.assertIn("next_due_at_utc", record)
                self.assertIn("cooldown_until_utc", record)
                self.assertIn("backoff_step", record)

    def test_next_due_at_reflects_cadence_backoff_and_pending_work(self) -> None:
        collector = self.collector(self.fixture_router())
        collector.poll()
        # Pending filings are due immediately.
        self.assertTrue(collector.state.pending_tasks)
        self.assertEqual(collector.scheduler_state(), DRAINING)
        collector.drain(max_items=3)
        # Then the cadence governs.
        self.assertEqual(collector.scheduler_state(), AWAITING_POLL)
        due = parse_ts(collector.next_due_at())
        expected = parse_ts(collector.state.last_poll_started_at_utc) + timedelta(seconds=60)
        self.assertEqual(due, expected)
        # A cooldown moves the due time to the cooldown end.
        collector.budget.enter_cooldown(300.0, "http_429_rate_limited")
        self.assertEqual(collector.scheduler_state(), COOLDOWN)
        self.assertEqual(collector.next_due_at(),
                         collector.budget.load().cooldown_until_utc)

    def test_a_backoff_transition_is_prospective_not_post_hoc(self) -> None:
        """The audit must learn when the next try is due, not just that one failed."""
        collector = self.collector(lambda path, call: response(b"oops", status=503))
        collector.poll()
        backoffs = [record for record in collector.scheduler.all()
                    if record["cause"] == BACKOFF_ENTERED]
        self.assertTrue(backoffs)
        transition = backoffs[-1]
        self.assertEqual(transition["state"], BACKOFF)
        self.assertIsNotNone(transition["next_due_at_utc"],
                             "a backoff must declare when the retry becomes due")
        self.assertGreater(parse_ts(transition["next_due_at_utc"]), self.timebase.now()
                           - timedelta(seconds=1))

    def test_a_blocked_lane_still_declares_its_state(self) -> None:
        """Silence must never be the only evidence that nothing was due."""
        collector = SecForm4Collector(self.paths, timebase=self.timebase, root=ROOT,
                                      environ={})
        self.assertFalse(collector.configured)
        collector.record_service_start()
        latest = collector.scheduler.latest()
        self.assertEqual(latest["state"], BLOCKED_NOT_CONFIGURED)
        self.assertEqual(latest["cause"], CONFIG_FAIL_CLOSED)
        self.assertIsNone(latest["next_due_at_utc"],
                          "nothing becomes due without an external change")

    def test_scheduler_journal_is_append_only_across_restart(self) -> None:
        collector = self.collector(self.fixture_router())
        collector.poll()
        before = collector.scheduler.all()
        restarted = self.reborn(self.fixture_router())
        self.assertEqual(restarted.scheduler.all()[:len(before)], before)


class LifecycleProvenanceTests(CollectorTestCase):
    def test_the_collector_never_attests_its_own_origin(self) -> None:
        collector = self.collector(self.fixture_router())
        self.assertEqual(collector.lifecycle["lifecycle_cause"], UNATTESTED)
        self.assertFalse(collector.lifecycle["externally_attested"])
        readiness = collector.t0_readiness()
        self.assertIn("LIFECYCLE_CAUSE_UNATTESTED", readiness["blockers"])
        self.assertFalse(readiness["instrumentation_ready"])

    def test_a_supervisor_supplied_cause_is_recorded_verbatim(self) -> None:
        for cause in LIFECYCLE_CAUSES:
            with self.subTest(cause=cause):
                provenance = lifecycle_provenance({
                    "QUANT_SEC_LIFECYCLE_CAUSE": cause,
                    "QUANT_SEC_BOOT_ID": "boot-123",
                    "QUANT_SEC_BOOT_AT_UTC": "2026-09-18T00:00:00+00:00",
                    "QUANT_SEC_SUPERVISOR_ID": "sup-1"})
                self.assertEqual(provenance["lifecycle_cause"], cause)
                self.assertTrue(provenance["externally_attested"])
                self.assertEqual(provenance["boot_id"], "boot-123")

    def test_an_unrecognised_cause_is_not_silently_accepted(self) -> None:
        provenance = lifecycle_provenance({"QUANT_SEC_LIFECYCLE_CAUSE": "LOOKS_FINE"})
        self.assertEqual(provenance["lifecycle_cause"], UNATTESTED)
        self.assertEqual(provenance["lifecycle_cause_declared"], "LOOKS_FINE")
        self.assertFalse(provenance["externally_attested"])

    def test_manual_start_is_flagged_as_invalidating(self) -> None:
        provenance = lifecycle_provenance({"QUANT_SEC_LIFECYCLE_CAUSE": MANUAL_START})
        self.assertTrue(provenance["invalidates_observation_window"])
        self.assertTrue(
            lifecycle_provenance({"QUANT_SEC_LIFECYCLE_CAUSE": SCHEDULED_START})
            ["invalidates_observation_window"])
        for benign in (AUTOMATIC_RESTART_AFTER_FAILURE, DEPLOYMENT_RESTART):
            self.assertFalse(
                lifecycle_provenance({"QUANT_SEC_LIFECYCLE_CAUSE": benign})
                ["invalidates_observation_window"])

    def test_service_start_is_journalled_with_the_active_fingerprint(self) -> None:
        collector = self.collector(self.fixture_router())
        collector.lifecycle = lifecycle_provenance({
            "QUANT_SEC_LIFECYCLE_CAUSE": SCHEDULED_START,
            "QUANT_SEC_BOOT_ID": "boot-abc"})
        record = collector.record_service_start()
        self.assertEqual(record["lifecycle_cause"], SCHEDULED_START)
        self.assertEqual(record["boot_id"], "boot-abc")
        self.assertTrue(record["acquisition_critical_fingerprint"].startswith("sha256:"))
        persisted = list(read_jsonl(self.paths.sec_lifecycle))
        self.assertEqual(len(persisted), 1)
        self.assertEqual(persisted[0]["boot_id"], "boot-abc")


class ObservationAuditTests(CollectorTestCase):
    def test_a_healthy_run_is_accountable(self) -> None:
        collector = self.collector(self.fixture_router())
        collector.lifecycle = lifecycle_provenance({
            "QUANT_SEC_LIFECYCLE_CAUSE": DEPLOYMENT_RESTART, "QUANT_SEC_BOOT_ID": "b1",
            "QUANT_SEC_SUPERVISOR_ID": "sup-observation"})
        collector.record_service_start()
        collector.poll()
        collector.drain(max_items=3)
        report = audit_observation_window(collector)
        self.assertTrue(report["accountable"], report["findings"])
        self.assertTrue(report["fingerprint_stable"])
        self.assertEqual(report["lifecycle_causes"], [DEPLOYMENT_RESTART])

    def test_an_unattested_start_is_reported_not_assumed_benign(self) -> None:
        collector = self.collector(self.fixture_router())
        collector.record_service_start()
        collector.poll()
        report = audit_observation_window(collector)
        self.assertFalse(report["accountable"])
        self.assertIn("LIFECYCLE_CAUSE_UNATTESTED", report["findings"])

    def test_a_manual_start_is_reported_as_an_invalidating_intervention(self) -> None:
        collector = self.collector(self.fixture_router())
        collector.lifecycle = lifecycle_provenance({
            "QUANT_SEC_LIFECYCLE_CAUSE": MANUAL_START, "QUANT_SEC_BOOT_ID": "b1",
            "QUANT_SEC_SUPERVISOR_ID": "sup-observation"})
        collector.record_service_start()
        collector.poll()
        report = audit_observation_window(collector)
        self.assertFalse(report["accountable"])
        self.assertIn("INVALIDATING_INTERVENTION", report["findings"])

    def test_a_changed_fingerprint_mid_window_is_detected(self) -> None:
        collector = self.collector(self.fixture_router())
        collector.lifecycle = lifecycle_provenance({
            "QUANT_SEC_LIFECYCLE_CAUSE": DEPLOYMENT_RESTART, "QUANT_SEC_BOOT_ID": "b1",
            "QUANT_SEC_SUPERVISOR_ID": "sup-observation"})
        collector.record_service_start()
        collector.poll()
        # A deployment that moved acquisition semantics mid-window.
        collector.fingerprint = "sha256:" + "0" * 64
        collector.record_current_state(SERVICE_START, detail="redeployed")
        report = audit_observation_window(collector)
        self.assertFalse(report["accountable"])
        self.assertIn("ACQUISITION_FINGERPRINT_CHANGED", report["findings"])
        self.assertEqual(len(report["fingerprints_observed"]), 2)

    def test_the_audit_never_infers_health_from_an_empty_journal(self) -> None:
        collector = self.collector(self.fixture_router(), enable=False)
        report = audit_observation_window(collector)
        self.assertFalse(report["accountable"])
        self.assertIn("NO_SCHEDULER_PROVENANCE", report["findings"])
        self.assertEqual(report["expected_actions"], 0)

    def test_the_audit_reports_and_never_closes_the_continuity_state(self) -> None:
        collector = self.collector(self.fixture_router())
        collector.record_service_start()
        report = audit_observation_window(collector)
        self.assertEqual(report["t0_authority"], "BLUE_TEAM")
        self.assertEqual(report["p0_continuous_service_state"],
                         "OPEN / NOT_YET_PROVEN_CONTINUOUS")
        self.assertEqual(collector.t0_readiness()["t0_authority"], "BLUE_TEAM")


# ---------------------------------------------------------------------------
# Continuous-service behaviour under the Control Plane
# ---------------------------------------------------------------------------

class ContinuousServiceTests(CollectorTestCase):
    """`NEXT_BUILD_MISSION.md` continuous-service work items, offline.

    These drive the real `QuantSystem` clock rather than the collector directly,
    because the claim being tested is about scheduling, not about capture.
    """

    def system(self, handler, *, enable: bool = True):
        import random
        from quant.clock import QuantSystem, Timer

        class FrozenTimer(Timer):
            def __init__(self, timebase):
                self.timebase = timebase

            def now(self):
                return self.timebase.now()

            def sleep(self, seconds):
                self.timebase.sleep(seconds)

        policy = self.policy()
        transport = FakeTransport(handler)
        system = QuantSystem(self.root, timer=FrozenTimer(self.timebase))
        collector = SecForm4Collector(
            self.paths, policy=policy, transport=transport, timebase=self.timebase,
            budget=SecTrafficBudget(self.paths.sec_budget, policy, timebase=self.timebase,
                                    rng=random.Random(5)),
            root=ROOT, emit=system.log.emit,
            environ={"QUANT_SEC_LIFECYCLE_CAUSE": SCHEDULED_START,
                     "QUANT_SEC_BOOT_ID": "boot-service-1"})
        system.sec = collector
        self.transport = transport
        if enable:
            collector.enable()
        return system, collector

    def test_capture_is_scheduled_ahead_of_replayable_research_and_desk_work(self) -> None:
        """Item 1: a backlog of replayable work cannot starve acquisition."""
        from autonomous_research.runtime import ResearchTask
        system, collector = self.system(self.fixture_router())
        system.boot()
        # Queue replayable work that is genuinely due, which is the backlog that
        # starved the capture lane on the first live run.
        system.queue.add(ResearchTask(
            task_id="RESEARCH-BACKLOG-PROBE", lane="probe", priority=99.0,
            reason="a due, replayable task competing with acquisition",
            worker="research_lane", required_resources=[], status="PENDING",
            metadata={"lane_name": "probe"}))
        system.queue.save()
        self.assertIsNotNone(system.queue.next_due(),
                             "the test needs genuinely due replayable work")
        outcome = system.tick()
        self.assertTrue(outcome.startswith("SEC_"),
                        f"acquisition must win the first tick, got {outcome}")
        # And the replayable task is still there, waiting rather than lost.
        self.assertEqual(system.queue.tasks["RESEARCH-BACKLOG-PROBE"].status, "PENDING")

    def test_repeated_cycles_leave_liveness_evidence_with_no_new_filing(self) -> None:
        """Item 2: quiet periods are evidenced, not silent."""
        system, collector = self.system(self.fixture_router())
        system.boot()
        for _ in range(6):
            system.tick()
        collector.drain(max_items=3)
        attempts_before = len(collector.store.attempts())
        for _ in range(3):
            self.timebase.advance(61)
            system.tick()
        self.assertGreater(len(collector.store.attempts()), attempts_before)
        quiet = [record for record in collector.store.attempts()
                 if record["result_state"] in (CAPTURED_OK, DEDUPLICATED)]
        self.assertTrue(quiet)
        self.assertEqual(collector.state.last_result_state, NO_NEW_DATA)
        self.assertEqual(collector.liveness(), RUNNING)

    def test_a_collector_that_stops_polling_becomes_observably_stale(self) -> None:
        """Item 6: heartbeat health cannot masquerade as coverage."""
        system, collector = self.system(self.fixture_router())
        system.boot()
        system.tick()
        self.assertEqual(collector.liveness(), RUNNING)
        self.timebase.advance(60 * 60 * 6)
        self.assertEqual(collector.liveness(), STALE)
        # Coverage is a separate axis and is not upgraded by a healthy heartbeat.
        self.assertIn(collector.state.coverage_state, (COVERAGE_COMPLETE, COVERAGE_UNKNOWN))

    def test_losing_the_requester_identity_fails_closed_as_blocked(self) -> None:
        """Item 5: missing identity is BLOCKED, never healthy idle service."""
        from quant.clock import QuantSystem
        system = QuantSystem(self.root)
        system.sec = SecForm4Collector(self.paths, timebase=self.timebase, root=ROOT,
                                       environ={})
        system.boot()
        outcome = system.tick()
        self.assertEqual(outcome, "IDLE", "a fail-closed lane produces no capture work")
        state = system.components.get("SEC_CAPTURE")
        self.assertEqual(state.state, "BLOCKED")
        self.assertIn("not configured", (state.detail or ""))
        self.assertFalse(system.sec.t0_readiness()["instrumentation_ready"])
        # And it is visible as blocked rather than absent on the status surface.
        from quant.status.render import render_status
        surface = render_status(system.snapshot())
        self.assertIn("BLOCKED", surface[surface.index("SEC FORM-4"):])

    def test_a_capture_fault_is_isolated_and_does_not_stop_the_system(self) -> None:
        system, collector = self.system(self.fixture_router())
        system.boot()
        collector.poll = lambda: (_ for _ in ()).throw(RuntimeError("capture exploded"))
        collector.has_pending_work = lambda: False
        collector.poll_due = lambda: True
        outcome = system.tick()
        self.assertEqual(outcome, "SEC_FAULT")
        self.assertEqual(system.components.get("SEC_CAPTURE").state, "FAULT")
        # The system is still alive and keeps working afterwards.
        collector.poll_due = lambda: False
        collector.reconciliation_due = lambda: None
        self.assertIn(system.tick(), {"RESEARCH", "SESSION", "IDLE", "LEARNED", "BLOCKED"})

    def test_restart_mid_service_resumes_without_mutating_prior_evidence(self) -> None:
        """Item 3: ordinary restart resumes from durable state."""
        system, collector = self.system(self.fixture_router())
        system.boot()
        system.tick()
        collector.drain(max_items=2)
        attempts = collector.store.attempts()
        envelopes = collector.store.envelopes()
        transitions = collector.scheduler.all()

        import random
        policy = self.policy()
        restarted = SecForm4Collector(
            self.paths, policy=policy, transport=FakeTransport(
                self.fixture_router()),
            timebase=self.timebase,
            budget=SecTrafficBudget(self.paths.sec_budget, policy, timebase=self.timebase,
                                    rng=random.Random(5)),
            root=ROOT,
            environ={"QUANT_SEC_LIFECYCLE_CAUSE": AUTOMATIC_RESTART_AFTER_FAILURE,
                     "QUANT_SEC_BOOT_ID": "boot-service-2"})
        self.assertEqual(restarted.store.attempts(), attempts)
        self.assertEqual(restarted.store.envelopes(), envelopes)
        self.assertEqual(restarted.scheduler.all()[:len(transitions)], transitions)
        restarted.record_service_start()
        # A second boot id appears, and the cause is the supervisor's, not ours.
        lifecycle = list(read_jsonl(self.paths.sec_lifecycle))
        self.assertEqual(lifecycle[-1]["lifecycle_cause"], AUTOMATIC_RESTART_AFTER_FAILURE)
        self.assertEqual(lifecycle[-1]["boot_id"], "boot-service-2")
        # An automatic restart does not invalidate the window.
        self.assertFalse(lifecycle[-1]["invalidates_observation_window"])
        self.assertEqual(restarted.fingerprint, collector.fingerprint,
                         "a restart alone must not move the acquisition fingerprint")

    def test_the_status_surface_stays_firewall_safe_with_the_new_provenance(self) -> None:
        from quant.status.brief import build_chief_brief
        from quant.status.render import render_status
        system, collector = self.system(self.fixture_router())
        system.boot()
        system.tick()
        collector.drain(max_items=3)
        snapshot = system.snapshot()
        for where, text in (("status surface", render_status(snapshot)),
                            ("CHIEF_BRIEF.md", build_chief_brief(snapshot)),
                            ("scheduler journal",
                             self.paths.sec_scheduler.read_text(encoding="utf-8")),
                            ("lifecycle journal",
                             self.paths.sec_lifecycle.read_text(encoding="utf-8")),
                            ("fingerprint manifest",
                             self.paths.sec_fingerprint.read_text(encoding="utf-8")
                             if self.paths.sec_fingerprint.exists() else "")):
            with self.subTest(surface=where):
                assert_no_scientific_content(text, where)

    def test_the_fingerprint_manifest_never_carries_the_contact_address(self) -> None:
        system, collector = self.system(self.fixture_router())
        payload = collector.materialize_fingerprint()
        rendered = json.dumps(payload, sort_keys=True)
        self.assertNotIn("example.com", rendered)
        self.assertNotIn(USER_AGENT, rendered)
        self.assertIn("requester_identity_binding", rendered)

    def test_a_fresh_install_can_boot_the_control_plane(self) -> None:
        """Regression: a fresh var/ must not crash boot().

        Found while regenerating the status artifacts on the Blue base commit
        c1a955316055aaf6c1b28853e21ed07e36e55f6a. The insider_filings legacy
        entry had gained `acceptance` and `affected_subsystems` keys describing
        its capability gap, but only `capability` was filtered out of the
        ResearchTask kwargs, so ResearchTask(**entry) raised TypeError. An
        already-seeded queue hid it, because the seeding call short-circuits on
        the task id - so it reproduced only on a first boot, which is exactly
        when a new deployment of the capture service starts.
        """
        import shutil, tempfile
        from quant.clock import QuantSystem
        with tempfile.TemporaryDirectory(prefix="quant-fresh-boot-") as directory:
            root = Path(directory)
            (root / "research").mkdir()
            shutil.copy2(ROOT / "research" / "opportunity_map.json", root / "research")
            system = QuantSystem(root)
            seeded = system.boot()["seeded"]
            self.assertIn("SCAN-INSIDER-FILINGS-001", seeded)
            # The capability gap it describes is still raised for the Build Plane.
            gaps = {task["task_id"]: task for task in system.learning.open_build_tasks()}
            gap = gaps["BUILD-SCAN-INSIDER-FILINGS-001"]
            self.assertIn("admissibility", gap["capability"])
            self.assertIn("visibility firewall", gap["acceptance"])
            # And booting twice is stable.
            QuantSystem(root).boot()


# ---------------------------------------------------------------------------
# RETROSPECTIVE_AUDIT_CAN_FALSE_PASS
# ---------------------------------------------------------------------------

class AuditFalsePassTests(CollectorTestCase):
    """Each test constructs a journal that the previous audit called accountable.

    The defect class was that obligations had no identity, so reconciliation was
    many-to-many: a pre-due attempt could answer a future deadline, one attempt
    could answer several deadlines, and any later transition could cancel an
    earlier one. These are the three false passes, plus the legitimate
    supersession that must still pass.
    """

    def setUp(self) -> None:
        super().setUp()
        self.lane = self.collector_with_attested_lifecycle()

    def collector_with_attested_lifecycle(self, *, enable: bool = False):
        """A collector whose scheduler journal starts empty.

        Enabling the lane or recording a service start would add real
        obligations, which would mix into the hand-built scenarios below. The
        lifecycle record these tests need is therefore written directly, so the
        only transitions in the ledger are the ones the scenario states.
        """
        collector = self.collector(self.fixture_router(), enable=enable)
        collector.lifecycle = lifecycle_provenance({
            "QUANT_SEC_LIFECYCLE_CAUSE": DEPLOYMENT_RESTART,
            "QUANT_SEC_BOOT_ID": "boot-audit",
            "QUANT_SEC_SUPERVISOR_ID": "sup-audit"})
        collector.state.coverage_state = COVERAGE_COMPLETE
        collector.state.open_gaps = []
        collector.save()
        return collector

    def write_transition(self, *, recorded_at: str, due_at: str | None, cause: str,
                         obligation_id: str | None, supersedes: str | None = None,
                         state: str = AWAITING_POLL) -> None:
        """Append a scheduler transition directly, to build an exact scenario."""
        self.lane.scheduler.record(SchedulerTransition(
            transition_id=f"t-{uuid.uuid4().hex[:8]}",
            recorded_at_utc=recorded_at, state=state, cause=cause,
            next_due_at_utc=due_at,
            acquisition_critical_fingerprint=self.lane.fingerprint or "fp",
            obligation_id=obligation_id, supersedes_obligation_id=supersedes,
            boot_id="boot-audit", lifecycle_cause=DEPLOYMENT_RESTART))

    def write_attempt(self, *, attempted_at: str, attempt_id: str,
                      result_state: str = CAPTURED_OK,
                      obligation_id: str | None = None) -> None:
        if obligation_id is None:
            used = {record.get("obligation_id") for record in self.lane.store.attempts()}
            superseded = {record.get("supersedes_obligation_id")
                          for record in self.lane.scheduler.all()
                          if record.get("supersedes_obligation_id")}
            candidates = [record.get("obligation_id")
                          for record in self.lane.scheduler.all()
                          if record.get("obligation_id")
                          and record.get("obligation_id") not in used
                          and record.get("obligation_id") not in superseded]
            obligation_id = candidates[0] if candidates else None
        intent_path = self.paths.sec / "request_intents.jsonl"
        append_jsonl(intent_path, {"event": "INTENT", "attempt_id": attempt_id,
                                   "obligation_id": obligation_id})
        append_jsonl(intent_path, {"event": "RESERVED", "attempt_id": attempt_id,
                                   "obligation_id": obligation_id})
        self.lane.store.record_attempt(SecAttemptRecord(
            attempt_id=attempt_id, attempt_kind="DISCOVERY", endpoint_class="test",
            source_locator_digest=digest_text("loc"),
            request_attempted_at_utc=attempted_at,
            response_received_at_utc=attempted_at,
            result_state=result_state, collector_version="v", git_commit="c",
            obligation_id=obligation_id, http_status=200))
        append_jsonl(intent_path, {"event": "FINISHED", "attempt_id": attempt_id})

    def audit(self, *, now: str):
        # Written directly rather than through record_service_start, which would
        # also append a transition and add an obligation to the scenario.
        append_jsonl(self.paths.sec_lifecycle,
                     dict(self.lane.lifecycle,
                          recorded_at_utc="2026-09-18T11:59:00+00:00",
                          acquisition_critical_fingerprint=self.lane.fingerprint
                          or "fp"))
        return audit_observation_window(self.lane, tolerance_seconds=180.0,
                                        now=parse_ts(now))

    # --- case A: an earlier attempt must not satisfy a later obligation -----
    def test_an_attempt_before_the_due_time_does_not_satisfy_the_obligation(self) -> None:
        """Defect A. `abs(attempt - due) <= tolerance` accepted a pre-due request."""
        self.write_transition(recorded_at="2026-09-18T12:00:00+00:00",
                              due_at="2026-09-18T12:05:00+00:00",
                              cause=POLL_COMPLETED, obligation_id="OB-1")
        # The only request happened a minute BEFORE the deadline it would answer,
        # and well inside the 180s tolerance window in absolute terms.
        self.write_attempt(attempted_at="2026-09-18T12:04:00+00:00", attempt_id="A-1")
        report = self.audit(now="2026-09-18T12:30:00+00:00")
        self.assertFalse(report["accountable"])
        self.assertIn("UNEXPLAINED_EXPECTED_ACTION", report["findings"])
        self.assertEqual(report["obligations_unexplained"], 1)
        self.assertEqual(report["unexplained_obligations"][0]["obligation_id"], "OB-1")
        self.assertEqual(report["obligations_resolved_by_attempt"], 0)

    def test_an_attempt_after_the_due_time_within_tolerance_does_satisfy_it(self) -> None:
        """The forward-only rule must still accept a slightly late tick."""
        self.write_transition(recorded_at="2026-09-18T12:00:00+00:00",
                              due_at="2026-09-18T12:05:00+00:00",
                              cause=POLL_COMPLETED, obligation_id="OB-1")
        self.write_attempt(attempted_at="2026-09-18T12:06:30+00:00", attempt_id="A-1")
        report = self.audit(now="2026-09-18T12:30:00+00:00")
        self.assertEqual(report["obligations_resolved_by_attempt"], 1)
        self.assertEqual(report["obligations_unexplained"], 0)

    def test_an_attempt_beyond_tolerance_does_not_satisfy_the_obligation(self) -> None:
        self.write_transition(recorded_at="2026-09-18T12:00:00+00:00",
                              due_at="2026-09-18T12:05:00+00:00",
                              cause=POLL_COMPLETED, obligation_id="OB-1")
        self.write_attempt(attempted_at="2026-09-18T12:20:00+00:00", attempt_id="A-1")
        report = self.audit(now="2026-09-18T12:40:00+00:00")
        self.assertEqual(report["obligations_unexplained"], 1)

    # --- case B: one attempt cannot answer two obligations ------------------
    def test_one_attempt_cannot_satisfy_two_due_obligations(self) -> None:
        """Defect B. Attempts were matched with `any(...)` and never consumed."""
        self.write_transition(recorded_at="2026-09-18T12:00:00+00:00",
                              due_at="2026-09-18T12:05:00+00:00",
                              cause=POLL_COMPLETED, obligation_id="OB-1")
        # A second, independent obligation due at the same moment. Nothing
        # supersedes either one, so both need their own answer.
        self.write_transition(recorded_at="2026-09-18T12:00:30+00:00",
                              due_at="2026-09-18T12:05:00+00:00",
                              cause=WORK_ENQUEUED, obligation_id="OB-2",
                              state=DRAINING)
        self.write_attempt(attempted_at="2026-09-18T12:05:10+00:00", attempt_id="A-1")
        report = self.audit(now="2026-09-18T12:30:00+00:00")
        self.assertFalse(report["accountable"])
        self.assertEqual(report["obligations_resolved_by_attempt"], 1,
                         "the single request may retire exactly one obligation")
        self.assertEqual(report["obligations_unexplained"], 1)
        self.assertEqual(report["reconciliation"], "one_obligation_to_one_resolution")

    def test_two_attempts_satisfy_two_obligations(self) -> None:
        self.write_transition(recorded_at="2026-09-18T12:00:00+00:00",
                              due_at="2026-09-18T12:05:00+00:00",
                              cause=POLL_COMPLETED, obligation_id="OB-1")
        self.write_transition(recorded_at="2026-09-18T12:00:30+00:00",
                              due_at="2026-09-18T12:05:00+00:00",
                              cause=WORK_ENQUEUED, obligation_id="OB-2", state=DRAINING)
        self.write_attempt(attempted_at="2026-09-18T12:05:10+00:00", attempt_id="A-1")
        self.write_attempt(attempted_at="2026-09-18T12:05:40+00:00", attempt_id="A-2")
        report = self.audit(now="2026-09-18T12:30:00+00:00")
        self.assertEqual(report["obligations_resolved_by_attempt"], 2)
        self.assertEqual(report["obligations_unexplained"], 0)
        self.assertTrue(report["accountable"], report["findings"])

    # --- case C: supersession cannot be retroactive -------------------------
    def test_a_transition_after_a_missed_deadline_cannot_erase_the_hole(self) -> None:
        """Defect C. Any later transition used to count as supersession."""
        self.write_transition(recorded_at="2026-09-18T12:00:00+00:00",
                              due_at="2026-09-18T12:05:00+00:00",
                              cause=POLL_COMPLETED, obligation_id="OB-1")
        # The service came back long after the deadline and re-planned, naming
        # the obligation it replaces. That is a post-hoc note, not an excuse.
        self.write_transition(recorded_at="2026-09-18T12:40:00+00:00",
                              due_at="2026-09-18T12:45:00+00:00",
                              cause=SERVICE_START, obligation_id="OB-2",
                              supersedes="OB-1")
        report = self.audit(now="2026-09-18T12:41:00+00:00")
        self.assertFalse(report["accountable"])
        self.assertIn("UNEXPLAINED_EXPECTED_ACTION", report["findings"])
        unexplained = {item["obligation_id"] for item in report["unexplained_obligations"]}
        self.assertEqual(unexplained, {"OB-1"})
        self.assertEqual(report["obligations_resolved_by_supersession"], 0)
        # OB-2 is not yet due, so it is pending rather than a second hole.
        self.assertEqual(report["obligations_pending"], 1)

    def test_a_transition_before_the_due_time_supersedes_and_stays_accountable(self) -> None:
        """The legitimate re-plan: prospective, named, authorized cause."""
        self.write_transition(recorded_at="2026-09-18T12:00:00+00:00",
                              due_at="2026-09-18T12:05:00+00:00",
                              cause=POLL_COMPLETED, obligation_id="OB-1")
        # Work arrived before the poll came due, so the lane re-planned.
        self.write_transition(recorded_at="2026-09-18T12:02:00+00:00",
                              due_at="2026-09-18T12:03:00+00:00",
                              cause=WORK_ENQUEUED, obligation_id="OB-2",
                              supersedes="OB-1", state=DRAINING)
        self.write_attempt(attempted_at="2026-09-18T12:03:20+00:00", attempt_id="A-1")
        report = self.audit(now="2026-09-18T12:30:00+00:00")
        self.assertTrue(report["accountable"], report["findings"])
        self.assertEqual(report["obligations_resolved_by_supersession"], 1)
        self.assertEqual(report["obligations_resolved_by_attempt"], 1)
        self.assertEqual(report["obligations_unexplained"], 0)

    def test_supersession_requires_naming_the_obligation_it_replaces(self) -> None:
        self.write_transition(recorded_at="2026-09-18T12:00:00+00:00",
                              due_at="2026-09-18T12:05:00+00:00",
                              cause=POLL_COMPLETED, obligation_id="OB-1")
        # Recorded before the deadline, but names nothing. Not a supersession.
        self.write_transition(recorded_at="2026-09-18T12:02:00+00:00",
                              due_at="2026-09-18T12:09:00+00:00",
                              cause=WORK_ENQUEUED, obligation_id="OB-2")
        report = self.audit(now="2026-09-18T12:30:00+00:00")
        self.assertFalse(report["accountable"])
        self.assertIn("OB-1", {item["obligation_id"]
                               for item in report["unexplained_obligations"]})

    def test_supersession_requires_an_authorized_cause(self) -> None:
        self.write_transition(recorded_at="2026-09-18T12:00:00+00:00",
                              due_at="2026-09-18T12:05:00+00:00",
                              cause=POLL_COMPLETED, obligation_id="OB-1")
        self.write_transition(recorded_at="2026-09-18T12:02:00+00:00",
                              due_at="2026-09-18T12:09:00+00:00",
                              cause="OPERATOR_DECIDED_TO_SKIP", obligation_id="OB-2",
                              supersedes="OB-1")
        report = self.audit(now="2026-09-18T12:30:00+00:00")
        self.assertFalse(report["accountable"],
                         "an unrecognised cause must not retire an obligation")
        self.assertEqual(report["obligations_resolved_by_supersession"], 0)

    def test_one_transition_cannot_supersede_two_obligations(self) -> None:
        """Resolutions are consumed on both sides of the ledger."""
        self.write_transition(recorded_at="2026-09-18T12:00:00+00:00",
                              due_at="2026-09-18T12:05:00+00:00",
                              cause=POLL_COMPLETED, obligation_id="OB-1")
        self.write_transition(recorded_at="2026-09-18T12:00:10+00:00",
                              due_at="2026-09-18T12:05:00+00:00",
                              cause=WORK_ENQUEUED, obligation_id="OB-2", state=DRAINING)
        # One transition claiming to replace both.
        transition_id = f"t-{uuid.uuid4().hex[:8]}"
        for target in ("OB-1", "OB-2"):
            self.lane.scheduler.record(SchedulerTransition(
                transition_id=transition_id,
                recorded_at_utc="2026-09-18T12:02:00+00:00", state=AWAITING_POLL,
                cause=POLL_COMPLETED, next_due_at_utc="2026-09-18T12:20:00+00:00",
                acquisition_critical_fingerprint="fp", obligation_id="OB-3",
                supersedes_obligation_id=target, boot_id="boot-audit",
                lifecycle_cause=SCHEDULED_START))
        report = self.audit(now="2026-09-18T12:30:00+00:00")
        self.assertEqual(report["obligations_resolved_by_supersession"], 1,
                         "one re-plan retires one obligation")
        self.assertFalse(report["accountable"])

    # --- ledger integrity ---------------------------------------------------
    def test_an_obligation_without_identity_fails_the_window(self) -> None:
        """A journal that cannot be reconciled by name is not audited by time."""
        self.write_transition(recorded_at="2026-09-18T12:00:00+00:00",
                              due_at="2026-09-18T12:05:00+00:00",
                              cause=POLL_COMPLETED, obligation_id=None)
        report = self.audit(now="2026-09-18T12:30:00+00:00")
        self.assertFalse(report["accountable"])
        self.assertIn("OBLIGATION_IDENTITY_MISSING", report["findings"])
        self.assertEqual(len(report["obligations_without_identity"]), 1)

    def test_every_obligation_has_exactly_one_status(self) -> None:
        self.write_transition(recorded_at="2026-09-18T12:00:00+00:00",
                              due_at="2026-09-18T12:05:00+00:00",
                              cause=POLL_COMPLETED, obligation_id="OB-1")
        self.write_transition(recorded_at="2026-09-18T12:06:00+00:00",
                              due_at="2026-09-18T12:11:00+00:00",
                              cause=POLL_COMPLETED, obligation_id="OB-2")
        self.write_attempt(attempted_at="2026-09-18T12:05:05+00:00", attempt_id="A-1")
        report = self.audit(now="2026-09-18T12:12:00+00:00")
        total = (report["obligations_resolved_by_attempt"]
                 + report["obligations_resolved_by_supersession"]
                 + report["obligations_pending"]
                 + report["obligations_unexplained"])
        self.assertEqual(total, report["obligations"],
                         "the four statuses must partition the ledger exactly")

    def test_a_live_service_last_obligation_is_pending_not_a_hole(self) -> None:
        """The newest commitment of a running service is not yet a miss."""
        self.write_transition(recorded_at="2026-09-18T12:00:00+00:00",
                              due_at="2026-09-18T12:05:00+00:00",
                              cause=POLL_COMPLETED, obligation_id="OB-1")
        report = self.audit(now="2026-09-18T12:05:30+00:00")
        self.assertEqual(report["obligations_pending"], 1)
        self.assertEqual(report["obligations_unexplained"], 0)
        self.assertTrue(report["accountable"], report["findings"])

    def test_the_real_collector_emits_reconcilable_obligations(self) -> None:
        """The production path must produce a ledger the audit can settle."""
        collector = self.collector_with_attested_lifecycle(enable=True)
        collector.record_service_start()
        collector.poll()
        collector.drain(max_items=3)
        transitions = collector.scheduler.all()
        committed = [record for record in transitions if record.get("next_due_at_utc")]
        self.assertTrue(committed)
        for record in committed:
            with self.subTest(transition=record["transition_id"]):
                self.assertTrue(record["obligation_id"],
                                "every commitment must be named")
        # Each transition after the first declares what it replaces.
        chained = [record for record in transitions
                   if record.get("supersedes_obligation_id")]
        self.assertTrue(chained, "re-plans must name the obligation they replace")
        report = audit_observation_window(collector)
        self.assertTrue(report["accountable"], report["findings"])
        self.assertEqual(report["obligations_without_identity"], [])


# ---------------------------------------------------------------------------
# LIFECYCLE_PROVENANCE_NOT_AUTHORITATIVE
# ---------------------------------------------------------------------------

SERVICE_MANAGED_ENV = {"QUANT_SEC_SERVICE_MANAGER": "systemd",
                       "INVOCATION_ID": "9f2c1b7ad4e14f0c8a3e5d6b7c8f9a0b"}


class LaunchProvenanceTests(SecCaptureTestCase):
    """Replacement supervisors never infer an automatic cause."""

    def launcher(self):
        sys.path.insert(0, str(ROOT / "deploy"))
        import quant_sec_supervisor as launcher
        return launcher

    def test_absence_of_provenance_is_manual(self) -> None:
        self.assertEqual(
            self.launcher().classify({}, "sha256:aaa", manual=False,
                                     service_managed=False, invocation_id=None),
            MANUAL_START)

    def test_service_managed_first_launch_still_needs_authority(self) -> None:
        self.assertEqual(
            self.launcher().classify({}, "sha256:aaa", manual=False,
                                     service_managed=True, invocation_id="inv-1"),
            MANUAL_START)

    def test_replacement_after_dead_supervisor_is_manual_even_immediately(self) -> None:
        previous = {"fingerprint": "sha256:aaa", "last_child_exit_code": None,
                    "supervisor_running": True, "supervisor_invocation_id": "inv-1",
                    "host_boot_id": "boot-A",
                    "boot_at_utc": self.timebase.now().isoformat()}
        cause = self.launcher().classify(
            previous, "sha256:aaa", manual=False, service_managed=True,
            invocation_id="inv-2", boot_id="boot-A", now=self.timebase.now())
        self.assertEqual(cause, MANUAL_START)

    def test_only_same_supervisor_witness_can_attest_child_restart(self) -> None:
        cause = self.launcher().classify(
            {}, "sha256:aaa", manual=False, service_managed=True,
            invocation_id="inv-1", witnessed_child_failure=True)
        self.assertEqual(cause, AUTOMATIC_RESTART_AFTER_FAILURE)

    def test_deployment_requires_explicit_authority(self) -> None:
        changed = {"fingerprint": "sha256:old"}
        self.assertEqual(
            self.launcher().classify(
                changed, "sha256:new", manual=False, service_managed=True,
                invocation_id="inv-2"),
            MANUAL_START)
        self.assertEqual(
            self.launcher().classify(
                changed, "sha256:new", manual=False, service_managed=True,
                invocation_id="inv-2", deployment_authorized=True),
            DEPLOYMENT_RESTART)

    def test_legacy_replacement_supervisor_cause_is_invalidating(self) -> None:
        self.assertIn(AUTOMATIC_RESTART_AFTER_SUPERVISOR_FAILURE, INVALIDATING_CAUSES)
        self.assertNotIn(AUTOMATIC_RESTART_AFTER_SUPERVISOR_FAILURE, AUTOMATIC_CAUSES)

    def test_a_launch_without_a_service_manager_is_not_qualifying(self) -> None:
        provenance = lifecycle_provenance({
            "QUANT_SEC_LIFECYCLE_CAUSE": DEPLOYMENT_RESTART,
            "QUANT_SEC_BOOT_ID": "boot-1",
            "QUANT_SEC_QUALIFYING_MODE": "1"})
        self.assertFalse(provenance["service_managed"])
        self.assertFalse(provenance["qualifying_service_mode"])

    def test_an_authorized_service_managed_launch_can_be_qualifying(self) -> None:
        provenance = lifecycle_provenance({
            **SERVICE_MANAGED_ENV,
            "QUANT_SEC_LIFECYCLE_CAUSE": DEPLOYMENT_RESTART,
            "QUANT_SEC_BOOT_ID": "boot-1",
            "QUANT_SEC_QUALIFYING_MODE": "1",
            "QUANT_SEC_LAUNCH_AUTHORITY_NONCE": "nonce-1"})
        self.assertTrue(provenance["service_managed"])
        self.assertTrue(provenance["qualifying_service_mode"])
        self.assertEqual(provenance["launch_authority_nonce"], "nonce-1")

    def test_readiness_blocks_a_manual_start(self) -> None:
        collector = SecForm4Collector(
            self.paths, policy=self.policy(),
            transport=FakeTransport(lambda p, c: None), timebase=self.timebase, root=ROOT,
            environ={**SERVICE_MANAGED_ENV, "QUANT_SEC_LIFECYCLE_CAUSE": MANUAL_START,
                     "QUANT_SEC_BOOT_ID": "b1", "QUANT_SEC_QUALIFYING_MODE": "1"})
        readiness = collector.t0_readiness()
        self.assertFalse(readiness["instrumentation_ready"])
        self.assertIn("INVALIDATING_LIFECYCLE_CAUSE", readiness["blockers"])


class QualifyingModeGateTests(SecCaptureTestCase):
    """Acquisition-critical runtime overrides are refused or bound."""

    def run_launcher(self, *args, environ: dict[str, str] | None = None):
        import subprocess
        environment = {**os.environ, "QUANT_SEC_USER_AGENT": USER_AGENT}
        environment.pop("INVOCATION_ID", None)
        environment.pop("QUANT_SEC_SERVICE_MANAGER", None)
        environment.update(environ or {})
        return subprocess.run(
            [sys.executable, str(ROOT / "deploy" / "quant_sec_supervisor.py"),
             "--root", str(self.root), *args],
            capture_output=True, text=True, env=environment, timeout=120)

    def test_qualifying_mode_refuses_a_poll_seconds_override(self) -> None:
        result = self.run_launcher("--qualifying", "--poll-seconds", "5",
                                   environ=SERVICE_MANAGED_ENV)
        self.assertEqual(result.returncode, 2)
        self.assertIn("QUALIFYING_OVERRIDE_REFUSED", result.stdout)

    def test_qualifying_mode_refuses_a_max_waits_override(self) -> None:
        result = self.run_launcher("--qualifying", "--max-waits", "2",
                                   environ=SERVICE_MANAGED_ENV)
        self.assertEqual(result.returncode, 2)
        self.assertIn("QUALIFYING_OVERRIDE_REFUSED", result.stdout)

    def test_qualifying_mode_refuses_a_manual_start(self) -> None:
        result = self.run_launcher("--qualifying", "--manual", environ=SERVICE_MANAGED_ENV)
        self.assertEqual(result.returncode, 2)
        self.assertIn("QUALIFYING_MANUAL_OVERRIDE_REFUSED", result.stdout)

    def test_qualifying_mode_refuses_a_launch_without_a_service_manager(self) -> None:
        result = self.run_launcher("--qualifying")
        self.assertEqual(result.returncode, 2)
        self.assertIn("SERVICE_MANAGER_UNATTESTED", result.stdout)

    def test_effective_runtime_configuration_is_bound_into_the_fingerprint(self) -> None:
        """Two services from identical code with different cadence must differ."""
        base = {**SERVICE_MANAGED_ENV, "QUANT_SEC_QUALIFYING_MODE": "1",
                "QUANT_SEC_SERVICE_POLL_SECONDS": "60.0",
                "QUANT_SEC_SERVICE_RESTART_DELAY_SECONDS": "15.0"}
        first = acquisition_critical_fingerprint(self.policy(), root=ROOT, environ=base)
        faster = acquisition_critical_fingerprint(
            self.policy(), root=ROOT,
            environ={**base, "QUANT_SEC_SERVICE_POLL_SECONDS": "5.0"})
        self.assertNotEqual(faster, first, "wake cadence must move the fingerprint")
        bounded = acquisition_critical_fingerprint(
            self.policy(), root=ROOT, environ={**base, "QUANT_SEC_SERVICE_MAX_WAITS": "3"})
        self.assertNotEqual(bounded, first, "a service lifetime bound must move it")
        slower_restart = acquisition_critical_fingerprint(
            self.policy(), root=ROOT,
            environ={**base, "QUANT_SEC_SERVICE_RESTART_DELAY_SECONDS": "120.0"})
        self.assertNotEqual(slower_restart, first, "restart pacing must move it")
        non_qualifying = acquisition_critical_fingerprint(
            self.policy(), root=ROOT, environ={**base, "QUANT_SEC_QUALIFYING_MODE": "0"})
        self.assertNotEqual(non_qualifying, first,
                            "qualifying and non-qualifying services are not the same service")
        # Identical environments still agree.
        self.assertEqual(acquisition_critical_fingerprint(self.policy(), root=ROOT,
                                                          environ=base), first)

    def test_the_manifest_records_the_effective_service_invocation(self) -> None:
        manifest = build_manifest(self.policy(), root=ROOT, environ={
            **SERVICE_MANAGED_ENV, "QUANT_SEC_QUALIFYING_MODE": "1",
            "QUANT_SEC_SERVICE_POLL_SECONDS": "60.0"})
        invocation = manifest["supervisor"]["effective_service_invocation"]
        self.assertEqual(invocation["poll_seconds"], 60.0)
        self.assertTrue(invocation["qualifying_mode"])
        self.assertIsNone(invocation["max_waits"])

    def test_the_unit_declares_the_service_manager_and_qualifying_mode(self) -> None:
        unit = (ROOT / "deploy" / "quant-sec-capture.service").read_text(encoding="utf-8")
        self.assertIn("Environment=QUANT_SEC_SERVICE_MANAGER=systemd", unit)
        self.assertIn("--qualifying", unit)
        self.assertIn("Restart=on-failure", unit)


# ---------------------------------------------------------------------------
# VISIBILITY_FIREWALL_REGRESSION
# ---------------------------------------------------------------------------

class CountProxyFirewallTests(SecCaptureTestCase):
    """Blue finding 3. A prose promise is not a control.

    The first rodage artifact published `attempts_by_endpoint_kind.FILING = 7`
    while asserting it carried no filing count. Under the frozen path one filing
    costs one FILING request, so that integer was a filing count by proxy. These
    tests make the *shape* of that defect detectable.
    """

    def test_the_detector_catches_the_exact_field_blue_found(self) -> None:
        offending = {"rodage_observations": {
            "attempts_by_endpoint_kind": {"DISCOVERY": 3, "FILING": 7}}}
        proxies = find_count_proxies(offending)
        self.assertEqual(len(proxies), 1)
        self.assertIn("FILING", proxies[0])
        with self.assertRaises(AssertionError):
            assert_no_count_proxies(offending, "artifact")

    def test_the_detector_catches_other_filing_count_shapes(self) -> None:
        for payload in ({"filings_captured": 12},
                        {"nested": {"filing_requests": 4}},
                        {"accessions_seen": 9},
                        {"envelopes_written": 5},
                        {"totals": [{"source_versions": 3}]}):
            with self.subTest(payload=payload):
                self.assertTrue(find_count_proxies(payload),
                                f"{payload} should be flagged as a filing-count proxy")

    def test_operational_health_numbers_remain_permitted(self) -> None:
        """The firewall forbids scientific volume, not all numbers."""
        healthy = {"poll_seconds": 60.0, "max_requests_per_second": 2.0,
                   "max_concurrency": 1, "cooldown_active": False}
        self.assertEqual(find_count_proxies(healthy), [])
        assert_no_count_proxies(healthy, "telemetry")
        for proxy in ({"raw_bytes": 49752}, {"requests_spent": 22},
                      {"scheduler_transitions": 14}, {"obligations": 13}):
            self.assertTrue(find_count_proxies(proxy))

    def test_booleans_are_never_treated_as_counts(self) -> None:
        self.assertEqual(find_count_proxies({"filing_present": True}), [])

    def test_historical_rodage_preserves_exposure_instead_of_rewriting_history(self) -> None:
        """Old artifacts are immutable provenance, not current publishable surfaces."""
        path = ROOT / "handoff" / "SEC_FORM4_P0_PRE_T0_RODAGE_2026-09-18.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        assert_no_scientific_content(path.read_text(encoding="utf-8"), path.name)
        self.assertTrue(find_count_proxies(document),
                        "historical proxy exposure must remain observable in provenance")
        self.assertIn("attempts_by_endpoint_kind",
                      document["visibility_firewall_provenance"]["what_was_exposed"])

    def test_the_artifact_preserves_the_irreversible_exposure_provenance(self) -> None:
        """Removing the value must not become a claim that it never happened."""
        path = ROOT / "handoff" / "SEC_FORM4_P0_PRE_T0_RODAGE_2026-09-18.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        provenance = document["visibility_firewall_provenance"]
        self.assertTrue(provenance["observed_by_blue"])
        self.assertTrue(provenance["exposure_is_irreversible"])
        self.assertFalse(provenance["blindness_restored"],
                         "the artifact must not claim blindness was restored")
        self.assertIn("no authority", provenance["authority"])
        self.assertIn("attempts_by_endpoint_kind", provenance["what_was_exposed"])

    def test_historical_handoff_artifacts_are_content_free_but_may_record_known_proxies(self) -> None:
        """Do not sanitize old evidence and then claim the actors never saw it."""
        for path in sorted((ROOT / "handoff").glob("*.json")):
            with self.subTest(artifact=path.name):
                assert_no_scientific_content(path.read_text(encoding="utf-8"), path.name)

    def test_current_public_projection_is_firewall_safe(self) -> None:
        collector = self.collector_for_telemetry()
        collector.poll()
        collector.drain(max_items=3)
        assert_no_count_proxies(collector.telemetry(), "collector telemetry")

    def test_live_telemetry_publishes_no_count_proxy(self) -> None:
        collector = self.collector_for_telemetry()
        collector.poll()
        collector.drain(max_items=3)
        assert_no_count_proxies(collector.telemetry(), "collector telemetry")
        self.assertIsInstance(audit_observation_window(collector)["accountable"], bool)

    def collector_for_telemetry(self):
        import random
        policy = self.policy()
        transport = FakeTransport(CollectorTestCase.fixture_router())
        collector = SecForm4Collector(
            self.paths, policy=policy, transport=transport, timebase=self.timebase,
            budget=SecTrafficBudget(self.paths.sec_budget, policy, timebase=self.timebase,
                                    rng=random.Random(11)),
            root=ROOT, environ={**SERVICE_MANAGED_ENV,
                                "QUANT_SEC_LIFECYCLE_CAUSE": DEPLOYMENT_RESTART,
                                "QUANT_SEC_BOOT_ID": "boot-tel",
                                "QUANT_SEC_SUPERVISOR_ID": "sup-tel",
                                "QUANT_SEC_LAUNCH_AUTHORITY_NONCE": "deploy-tel",
                                "QUANT_SEC_EFFECTIVE_UNIT_DIGEST": "sha256:" + "d" * 64,
                                "QUANT_SEC_QUALIFYING_MODE": "1"})
        collector.materialize_fingerprint()
        collector.enable()
        return collector


# ---------------------------------------------------------------------------
# Rodage falsification attempts
# ---------------------------------------------------------------------------

class RodageFalsificationTests(CollectorTestCase):
    """Deliberate attempts to make the instrumentation report something false.

    The pre-t0 rodage brief asks for these specifically: a missed obligation, a
    stale service, an override, an invalid discovery, and a crash, each checked
    for whether the system would still call itself healthy.
    """

    def qualifying_collector(self, handler, *, cause: str = DEPLOYMENT_RESTART,
                             boot_id: str = "boot-q1", enable: bool = True):
        import random
        policy = self.policy()
        transport = FakeTransport(handler)
        collector = SecForm4Collector(
            self.paths, policy=policy, transport=transport, timebase=self.timebase,
            budget=SecTrafficBudget(self.paths.sec_budget, policy, timebase=self.timebase,
                                    rng=random.Random(13)),
            root=ROOT, environ={**SERVICE_MANAGED_ENV,
                                "QUANT_SEC_LIFECYCLE_CAUSE": cause,
                                "QUANT_SEC_BOOT_ID": boot_id,
                                "QUANT_SEC_SUPERVISOR_ID": "sup-rodage",
                                "QUANT_SEC_LAUNCH_AUTHORITY_NONCE": "rodage-authority",
                                "QUANT_SEC_EFFECTIVE_UNIT_DIGEST": "sha256:" + "d" * 64,
                                "QUANT_SEC_QUALIFYING_MODE": "1",
                                "QUANT_SEC_SERVICE_POLL_SECONDS": "60.0"})
        self.transport = transport
        collector.materialize_fingerprint()
        # A real restart does not re-enable an already-enabled lane: sec-serve
        # only calls enable() when durable state says the lane is off.
        if enable and not collector.state.enabled:
            collector.enable()
        return collector

    def test_a_service_that_simply_stops_polling_is_not_accountable(self) -> None:
        """The core falsification: skip the work and see if the audit notices."""
        collector = self.qualifying_collector(self.fixture_router())
        collector.record_service_start()
        collector.poll()
        collector.drain(max_items=3)
        self.assertTrue(audit_observation_window(collector)["accountable"])
        # Now the service goes silent for an hour. Nothing is recorded, which is
        # exactly the case a journal of attempts alone cannot distinguish from
        # "nothing was due".
        self.timebase.advance(3600)
        report = audit_observation_window(collector)
        self.assertFalse(report["accountable"],
                         "an hour of silence against an open obligation is a hole")
        self.assertIn("UNEXPLAINED_EXPECTED_ACTION", report["findings"])
        self.assertGreaterEqual(report["obligations_unexplained"], 1)
        self.assertEqual(collector.liveness(), STALE)

    def test_a_stale_service_cannot_present_itself_as_healthy(self) -> None:
        collector = self.qualifying_collector(self.fixture_router())
        collector.record_service_start()
        collector.poll()
        collector.drain(max_items=3)
        self.timebase.advance(3600 * 4)
        telemetry = collector.telemetry()
        self.assertEqual(telemetry["liveness"], STALE)
        # Coverage is a separate axis and must not be upgraded by liveness.
        self.assertEqual(telemetry["coverage_state"], COVERAGE_COMPLETE)
        self.assertFalse(audit_observation_window(collector)["accountable"])

    def test_an_invalid_discovery_leaves_an_accounted_attempt_and_no_false_coverage(self) -> None:
        html = (FIXTURES / "edgar_error_page.html").read_bytes()
        collector = self.qualifying_collector(
            lambda path, call: response(html, headers={"Content-Type": "text/html"}))
        collector.record_service_start()
        outcome = collector.poll()
        self.assertEqual(outcome.result_state, DISCOVERY_INVALID)
        self.assertEqual(outcome.coverage_state, COVERAGE_UNKNOWN)
        # The attempt is recorded, so the obligation it answered is accounted for
        # even though the poll failed. A failure is not a hole.
        report = audit_observation_window(collector)
        self.assertNotIn("UNEXPLAINED_EXPECTED_ACTION", report["findings"])
        self.assertGreaterEqual(report["obligations_resolved_by_attempt"]
                                + report["obligations_resolved_by_supersession"], 1)

    def test_a_cooldown_period_is_explained_rather_than_silent(self) -> None:
        collector = self.qualifying_collector(
            lambda path, call: response(b"slow down", status=429,
                                        headers={"Retry-After": "300"}))
        collector.record_service_start()
        collector.poll()
        # The cooldown moved the next due time, and said so prospectively.
        cooldown_transitions = [record for record in collector.scheduler.all()
                                if record["state"] == COOLDOWN]
        self.assertTrue(cooldown_transitions)
        transition = cooldown_transitions[-1]
        self.assertIsNotNone(transition["next_due_at_utc"])
        self.assertIsNotNone(transition["obligation_id"])
        self.assertIsNotNone(transition["supersedes_obligation_id"])
        # Waiting out the cooldown is service, not a hole.
        self.timebase.advance(60)
        report = audit_observation_window(collector)
        self.assertNotIn("UNEXPLAINED_EXPECTED_ACTION", report["findings"])

    def test_a_restart_preserves_the_open_obligation(self) -> None:
        """A restart must not orphan the commitment the audit is waiting on."""
        collector = self.qualifying_collector(self.fixture_router())
        collector.record_service_start()
        collector.poll()
        collector.drain(max_items=3)
        open_obligation = collector.state.open_obligation_id
        self.assertIsNotNone(open_obligation)

        restarted = self.qualifying_collector(
            self.fixture_router(), cause=AUTOMATIC_RESTART_AFTER_FAILURE,
            boot_id="boot-q2")
        self.assertEqual(restarted.state.open_obligation_id, open_obligation,
                         "the open obligation survives the restart")
        restarted.record_service_start()
        # Restart preserves the original commitment without minting a replacement.
        latest = restarted.scheduler.latest()
        self.assertEqual(latest["obligation_id"], open_obligation)
        self.assertEqual(restarted.state.open_obligation_id, open_obligation)
        report = audit_observation_window(restarted)
        self.assertTrue(report["fingerprint_stable"])
        self.assertIn(AUTOMATIC_RESTART_AFTER_FAILURE,
                      report["lifecycle_causes"])
        self.assertFalse(
            any(record["lifecycle_cause"] in INVALIDATING_CAUSES
                for record in read_jsonl(self.paths.sec_lifecycle)),
            "a child restart witnessed by the same live supervisor is non-invalidating")

    def test_a_manual_restart_mid_window_is_reported_as_invalidating(self) -> None:
        collector = self.qualifying_collector(self.fixture_router())
        collector.record_service_start()
        collector.poll()
        intervened = self.qualifying_collector(self.fixture_router(),
                                               cause=MANUAL_START, boot_id="boot-q3")
        intervened.record_service_start()
        report = audit_observation_window(intervened)
        self.assertFalse(report["accountable"])
        self.assertIn("INVALIDATING_INTERVENTION", report["findings"])

    def test_no_publication_period_still_leaves_obligations_answered(self) -> None:
        """A quiet source is not a quiet service."""
        empty_feed = build_feed([], entries=[])
        collector = self.qualifying_collector(self.fixture_router(atom=empty_feed))
        collector.record_service_start()
        first = collector.poll()
        self.assertTrue(first.valid_discovery)
        for _ in range(3):
            self.timebase.advance(60)
            collector.poll()
        report = audit_observation_window(collector)
        self.assertTrue(report["accountable"], report["findings"])
        self.assertEqual(collector.state.last_result_state, NO_NEW_DATA)
        self.assertEqual(report["obligations_unexplained"], 0)

    def test_operator_internal_journals_are_content_free_but_not_count_free(self) -> None:
        """The tier contract, stated honestly and pinned by a test.

        Found while remediating the firewall regression: the tier was named
        `sec_firewall_safe_journals`, which reads as "publishable". It is not.
        These journals carry no filing-identifying string, and that is all they
        promise - the drain path records one transition per acquired filing, so a
        reader with file access can recover the count. The no-count rule binds the
        published projection, not the journals.
        """
        collector = self.qualifying_collector(self.fixture_router())
        collector.record_service_start()
        collector.poll()
        collector.drain(max_items=3)

        # What the tier does promise: no identifying content.
        for path in self.paths.sec_operator_internal_journals():
            if path.exists():
                with self.subTest(journal=path.name):
                    assert_no_scientific_content(path.read_text(encoding="utf-8"),
                                                 path.name)

        # What it does not promise, demonstrated rather than glossed over.
        drains = [record for record in collector.scheduler.all()
                  if record["cause"] == DRAIN_COMPLETED]
        self.assertTrue(drains, "the journal does record one drain per acquisition")

        # The published projection is what must be count-free, and is.
        from quant.clock import QuantSystem
        from quant.status.brief import build_chief_brief
        from quant.status.render import render_status
        system = QuantSystem(self.root)
        system.sec = collector
        snapshot = system.snapshot()
        for where, payload in (("collector telemetry", collector.telemetry()),
                               ("snapshot sec_capture", snapshot["sec_capture"])):
            with self.subTest(surface=where):
                assert_no_count_proxies(payload, where)
        for where, text in (("status surface", render_status(snapshot)),
                            ("CHIEF_BRIEF.md", build_chief_brief(snapshot))):
            with self.subTest(surface=where):
                assert_no_scientific_content(text, where)
                self.assertNotIn("DRAIN_COMPLETED", text,
                                 "a published surface must not tally drain events")


class AuditAdversarialExtraTests(AuditFalsePassTests):
    """Further attempts to make the ledger settle something it should not."""

    def test_a_supersession_recorded_exactly_at_the_due_time_is_too_late(self) -> None:
        """The boundary. `before the due time` must mean strictly before."""
        self.write_transition(recorded_at="2026-09-18T12:00:00+00:00",
                              due_at="2026-09-18T12:05:00+00:00",
                              cause=POLL_COMPLETED, obligation_id="OB-1")
        self.write_transition(recorded_at="2026-09-18T12:05:00+00:00",
                              due_at="2026-09-18T12:20:00+00:00",
                              cause=POLL_COMPLETED, obligation_id="OB-2",
                              supersedes="OB-1")
        report = self.audit(now="2026-09-18T12:30:00+00:00")
        self.assertEqual(report["obligations_resolved_by_supersession"], 0,
                         "a supersession at the deadline has not prevented the miss")
        self.assertFalse(report["accountable"])

    def test_a_chain_of_supersessions_cannot_clear_an_older_missed_obligation(self) -> None:
        """A long re-plan chain must not sweep up a deadline already missed."""
        self.write_transition(recorded_at="2026-09-18T12:00:00+00:00",
                              due_at="2026-09-18T12:05:00+00:00",
                              cause=POLL_COMPLETED, obligation_id="OB-1")
        # Nothing answered OB-1. Later the service re-plans repeatedly, each step
        # naming the previous obligation, as the live collector legitimately does.
        previous = "OB-1"
        for index, minute in enumerate(range(40, 46), start=2):
            obligation = f"OB-{index}"
            self.write_transition(recorded_at=f"2026-09-18T12:{minute}:00+00:00",
                                  due_at=f"2026-09-18T12:{minute + 1}:00+00:00",
                                  cause=POLL_COMPLETED, obligation_id=obligation,
                                  supersedes=previous)
            previous = obligation
        report = self.audit(now="2026-09-18T13:30:00+00:00")
        self.assertFalse(report["accountable"])
        self.assertIn("OB-1", {item["obligation_id"]
                               for item in report["unexplained_obligations"]},
                      "the original miss survives any later chain")

    def test_an_attempt_cannot_answer_an_obligation_created_after_it(self) -> None:
        """Even inside tolerance, causality runs one way."""
        self.write_attempt(attempted_at="2026-09-18T12:00:00+00:00", attempt_id="A-1")
        # The obligation is created after the request, and comes due after it too.
        self.write_transition(recorded_at="2026-09-18T12:01:00+00:00",
                              due_at="2026-09-18T12:02:00+00:00",
                              cause=POLL_COMPLETED, obligation_id="OB-1")
        report = self.audit(now="2026-09-18T12:30:00+00:00")
        self.assertEqual(report["obligations_resolved_by_attempt"], 0)
        self.assertFalse(report["accountable"])

    def test_many_attempts_cannot_cover_more_obligations_than_they_number(self) -> None:
        """Three obligations, two requests: at most two can be answered."""
        for index, minute in enumerate(("05", "06", "07"), start=1):
            self.write_transition(recorded_at="2026-09-18T12:00:00+00:00",
                                  due_at=f"2026-09-18T12:{minute}:00+00:00",
                                  cause=POLL_COMPLETED, obligation_id=f"OB-{index}")
        self.write_attempt(attempted_at="2026-09-18T12:05:10+00:00", attempt_id="A-1")
        self.write_attempt(attempted_at="2026-09-18T12:06:10+00:00", attempt_id="A-2")
        report = self.audit(now="2026-09-18T12:40:00+00:00")
        self.assertLessEqual(report["obligations_resolved_by_attempt"], 2)
        self.assertGreaterEqual(report["obligations_unexplained"], 1)
        self.assertFalse(report["accountable"])


# ---------------------------------------------------------------------------
# A systemd launch is not a reason (Blue follow-up 1)
# ---------------------------------------------------------------------------

class OperatorRestartTests(SecCaptureTestCase):
    """No boot/timing/fingerprint heuristic upgrades a replacement supervisor."""

    def launcher(self):
        sys.path.insert(0, str(ROOT / "deploy"))
        import quant_sec_supervisor as module
        return module

    def classify(self, previous, **kwargs):
        defaults = {"manual": False, "service_managed": True,
                    "invocation_id": "inv-2", "boot_id": "boot-A",
                    "now": self.timebase.now()}
        defaults.update(kwargs)
        return self.launcher().classify(previous, "sha256:fp", **defaults)

    def test_systemctl_restart_is_manual(self) -> None:
        self.assertEqual(self.classify({"fingerprint": "sha256:fp"}), MANUAL_START)

    def test_host_reboot_does_not_prove_automaticity(self) -> None:
        previous = {"fingerprint": "sha256:fp", "host_boot_id": "boot-A"}
        self.assertEqual(self.classify(previous, boot_id="boot-B"), MANUAL_START)

    def test_fast_restart_after_failure_is_still_manual_for_new_supervisor(self) -> None:
        failed = {"fingerprint": "sha256:fp", "last_child_exit_code": 1,
                  "last_child_exit_at_utc": self.timebase.now().isoformat()}
        self.assertEqual(self.classify(failed), MANUAL_START)

    def test_fingerprint_change_alone_is_not_deployment_authority(self) -> None:
        previous = {"fingerprint": "sha256:old"}
        self.assertEqual(
            self.launcher().classify(previous, "sha256:new", manual=False,
                                     service_managed=True, invocation_id="inv-2"),
            MANUAL_START)

    def test_explicit_deployment_authority_is_distinct(self) -> None:
        self.assertEqual(
            self.launcher().classify({}, "sha256:fp", manual=False,
                                     service_managed=True, invocation_id="inv-1",
                                     deployment_authorized=True),
            DEPLOYMENT_RESTART)

    def test_the_host_boot_id_is_read_from_the_kernel(self) -> None:
        from quant.dataplane.sec.supervisor import host_boot_id
        self.assertTrue(host_boot_id())
        self.assertIsNone(host_boot_id("/nonexistent/boot_id"))


class MaterializedFingerprintTests(CollectorTestCase):
    """Existence was never the question.

    A materialized manifest describing a different build than the one running is
    worse than none: it presents a frozen state the service does not have. That is
    how a stale fingerprint reached a published rodage artifact.
    """

    def qualifying(self):
        import random
        policy = self.policy()
        return SecForm4Collector(
            self.paths, policy=policy, transport=FakeTransport(self.fixture_router()),
            timebase=self.timebase,
            budget=SecTrafficBudget(self.paths.sec_budget, policy, timebase=self.timebase,
                                    rng=random.Random(17)),
            root=ROOT, environ={**SERVICE_MANAGED_ENV,
                                "QUANT_SEC_LIFECYCLE_CAUSE": DEPLOYMENT_RESTART,
                                "QUANT_SEC_BOOT_ID": "boot-fp",
                                "QUANT_SEC_SUPERVISOR_ID": "sup-fp",
                                "QUANT_SEC_LAUNCH_AUTHORITY_NONCE": "deploy-fp",
                                "QUANT_SEC_EFFECTIVE_UNIT_DIGEST": "sha256:" + "e" * 64,
                                "QUANT_SEC_QUALIFYING_MODE": "1"})

    def test_readiness_blocks_when_nothing_is_materialized(self) -> None:
        collector = self.qualifying()
        self.assertIsNone(collector.materialized_fingerprint())
        readiness = collector.t0_readiness()
        self.assertIn("FINGERPRINT_NOT_MATERIALIZED", readiness["blockers"])
        self.assertFalse(readiness["fingerprint_matches_materialized"])

    def test_readiness_blocks_when_the_materialized_fingerprint_is_stale(self) -> None:
        """The defect: a manifest on disk from a previous build."""
        collector = self.qualifying()
        collector.materialize_fingerprint()
        self.assertEqual(collector.materialized_fingerprint(), collector.fingerprint)

        # A deployment changed acquisition code; the manifest on disk did not move.
        stale = json.loads(self.paths.sec_fingerprint.read_text(encoding="utf-8"))
        stale["acquisition_critical_fingerprint"] = "sha256:" + "0" * 64
        self.paths.sec_fingerprint.write_text(json.dumps(stale, indent=2, sort_keys=True))

        reborn = self.qualifying()
        readiness = reborn.t0_readiness()
        self.assertIn("FINGERPRINT_MATERIALIZED_SELF_MISMATCH", readiness["blockers"])
        self.assertNotIn("FINGERPRINT_NOT_MATERIALIZED", readiness["blockers"])
        self.assertFalse(readiness["instrumentation_ready"])
        self.assertFalse(readiness["fingerprint_matches_materialized"])
        self.assertNotEqual(readiness["materialized_fingerprint"],
                            readiness["acquisition_critical_fingerprint"])

    def test_telemetry_surfaces_the_mismatch_on_a_live_service(self) -> None:
        collector = self.qualifying()
        collector.materialize_fingerprint()
        self.assertTrue(collector.telemetry()["fingerprint_matches_materialized"])
        stale = json.loads(self.paths.sec_fingerprint.read_text(encoding="utf-8"))
        stale["acquisition_critical_fingerprint"] = "sha256:" + "1" * 64
        self.paths.sec_fingerprint.write_text(json.dumps(stale, indent=2, sort_keys=True))
        self.assertFalse(self.qualifying().telemetry()["fingerprint_matches_materialized"])

    def test_rematerializing_after_a_change_refuses_silent_repair(self) -> None:
        collector = self.qualifying()
        stale = {"acquisition_critical_fingerprint": "sha256:" + "2" * 64}
        self.paths.ensure_sec()
        self.paths.sec_fingerprint.write_text(json.dumps(stale, indent=2, sort_keys=True))
        self.assertFalse(collector.t0_readiness()["instrumentation_ready"])
        with self.assertRaises(SecStorageFailure):
            collector.materialize_fingerprint()

    def test_a_changed_acquisition_module_makes_the_materialized_fingerprint_stale(self) -> None:
        """End to end: the check catches exactly the visibility.py case."""
        import shutil, tempfile
        collector = self.qualifying()
        collector.materialize_fingerprint()
        with tempfile.TemporaryDirectory() as directory:
            mirror = Path(directory) / "repo"
            shutil.copytree(ROOT / "src", mirror / "src")
            shutil.copytree(ROOT / "deploy", mirror / "deploy")
            shutil.copytree(ROOT / "scripts", mirror / "scripts")
            target = mirror / "src" / "quant" / "dataplane" / "sec" / "visibility.py"
            target.write_text(target.read_text() + "\n# firewall rule changed\n")
            import random
            policy = self.policy()
            moved = SecForm4Collector(
                self.paths, policy=policy,
                transport=FakeTransport(self.fixture_router()), timebase=self.timebase,
                budget=SecTrafficBudget(self.paths.sec_budget, policy,
                                        timebase=self.timebase, rng=random.Random(17)),
                root=mirror, environ={**SERVICE_MANAGED_ENV,
                                      "QUANT_SEC_LIFECYCLE_CAUSE": DEPLOYMENT_RESTART,
                                      "QUANT_SEC_BOOT_ID": "boot-fp",
                                      "QUANT_SEC_SUPERVISOR_ID": "sup-fp",
                                      "QUANT_SEC_LAUNCH_AUTHORITY_NONCE": "deploy-fp",
                                      "QUANT_SEC_EFFECTIVE_UNIT_DIGEST": "sha256:" + "e" * 64,
                                      "QUANT_SEC_QUALIFYING_MODE": "1"})
            self.assertNotEqual(moved.fingerprint, collector.fingerprint)
            self.assertIn("FINGERPRINT_MATERIALIZED_MISMATCH",
                          moved.t0_readiness()["blockers"])
