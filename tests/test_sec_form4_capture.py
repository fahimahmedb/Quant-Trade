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
from quant.dataplane.sec.store import (ACCESS_FORBIDDEN, CAPTURED_OK, DEDUPLICATED,  # noqa: E402
                                       DISCOVERY_INVALID, HUNG_REQUEST,
                                       INCOMPLETE_TRANSFER, NEW_ITEMS, NO_NEW_DATA,
                                       RATE_LIMITED, REQUEST_FAILED, SERVER_ERROR,
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
    """Same ``fetch`` contract as the real transport, so production has no test branch."""

    def __init__(self, handler):
        self.handler = handler
        self.requested: list[str] = []

    def fetch(self, path: str) -> SecHttpResponse:
        self.requested.append(path)
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

    def test_a_filter_that_does_not_surface_form_4_is_an_error(self) -> None:
        """A discovery filter that cannot be shown to work is never NO_NEW_DATA."""
        wrong_form = build_feed([1], form="8-K")
        with self.assertRaises(DiscoveryInvalid) as raised:
            parse_discovery_page(wrong_form, requested_start=0, requested_count=40)
        self.assertTrue(raised.exception.reason.startswith(
            "discovery_form_type_filter_mismatch"))
        # An ownership form other than 4 when 4 was requested is also a mismatch.
        with self.assertRaises(DiscoveryInvalid):
            parse_discovery_page(build_feed([2], form="3"), requested_start=0,
                                 requested_count=40)
        collector = self.collector(lambda path, call: response(wrong_form))
        outcome = collector.poll()
        self.assertEqual(outcome.result_state, DISCOVERY_INVALID)
        self.assertNotEqual(outcome.result_state, NO_NEW_DATA)

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
                         for path in self.paths.sec_firewall_safe_journals()
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
