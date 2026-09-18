"""Tests for the P0 SEC/Form-4 durable raw-capture lane.

The numbered requirements in ``NEXT_BUILD_MISSION.md`` ("Tests required before
live enablement") are cited on the tests that discharge them, so a reviewer can
check the list rather than trust a summary.
"""

from __future__ import annotations

import errno
import gzip
import json
import os
import sys
import unittest
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
from quant.dataplane.sec.timebase import FrozenTimebase  # noqa: E402
from quant.dataplane.sec.transport import (COMPLETE, SecHttpResponse,  # noqa: E402
                                           SecTransportError, TRUNCATED)
from quant.paths import QuantPaths  # noqa: E402


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
                         for path in self.paths.sec_firewall_safe_journals()
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
