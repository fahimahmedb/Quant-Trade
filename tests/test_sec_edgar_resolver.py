"""EDGAR acceptance resolution: durability, exact resume and safe concurrency.

Concurrency is admissible for this stage only under three conditions, and each
is asserted here rather than assumed:

* one process-global rate limiter, so Fair Access pace does not scale with the
  worker count;
* disjoint accession assignment, so no document is fetched twice;
* atomic cache writes plus a batched checkpoint carrying each document's
  sha256, so a kill at any instant resumes exactly.

The census definition is not exercised here. This file is about transport
durability only.
"""

import json
import sys
import threading
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.dataplane.sec_form4 import (
    AcceptanceIdentityError,
    RateLimiter,
    _sha256_bytes,
    assign_disjoint,
    load_acceptance_checkpoint,
    parse_acceptance_document,
    repair_checkpoint_tail,
    resolve_acceptance_documents,
    verify_acceptance_document,
    validate_acceptance_cache,
    write_atomic,
)

import tempfile


ISSUER_CIK = "0000320193"


def header(accession: str, stamp: str, owner: str = "0001723460",
           submission_type: str = "4", issuer: str = ISSUER_CIK) -> bytes:
    """A realistic EDGAR index-headers document.

    Identity is verified before an acceptance time is accepted, so a fixture
    carrying only a timestamp is not a document the resolver would trust.
    """
    return (
        "<HTML><HEAD>\n<!--\n"
        f"<SEC-HEADER>{accession}.hdr.sgml\n"
        f"<ACCEPTANCE-DATETIME>{stamp}\n"
        f"<ACCESSION-NUMBER>{accession}\n"
        f"<TYPE>{submission_type}\n"
        f"<REPORTING-OWNER>\n<OWNER-DATA>\n<CIK>{owner}\n"
        "</OWNER-DATA>\n</REPORTING-OWNER>\n"
        f"<ISSUER>\n<COMPANY-DATA>\n<CIK>{issuer}\n</COMPANY-DATA>\n</ISSUER>\n"
        "</SEC-HEADER>\n-->\n</HEAD></HTML>"
    ).encode()


ACCESSIONS = [f"000123456{i // 100}-2{i % 5}-{i:06d}" for i in range(40)]
ISSUERS = {acc: ISSUER_CIK for acc in ACCESSIONS}
OWNERS = {acc: ["0001723460"] for acc in ACCESSIONS}
PAYLOADS = {acc: header(acc, f"2024010{(i % 9) + 1}12000{i % 10}")
            for i, acc in enumerate(ACCESSIONS)}


class RecordingFetcher:
    """Counts every fetch so double work and pacing are observable."""

    def __init__(self, fail: set[str] | None = None, delay: float = 0.0):
        self.calls: list[str] = []
        self.times: list[float] = []
        self.lock = threading.Lock()
        self.fail = fail or set()
        self.delay = delay

    def __call__(self, url: str) -> bytes:
        accession = url.rstrip("/").split("/")[-1].replace("-index-headers.html", "")
        with self.lock:
            self.calls.append(accession)
            self.times.append(time.monotonic())
        if self.delay:
            time.sleep(self.delay)
        if accession in self.fail:
            raise RuntimeError("edgar unavailable")
        return PAYLOADS[accession]


class DeterminismTests(unittest.TestCase):
    def resolve(self, directory: str, workers: int, fetcher):
        base = Path(directory)
        return resolve_acceptance_documents(
            ACCESSIONS, ISSUERS, owners_of=OWNERS, cache_dir=base / "cache",
            checkpoint_path=base / "checkpoint.jsonl", fetcher=fetcher,
            workers=workers, rate_per_second=1000.0, batch_size=7)

    def test_worker_count_does_not_change_the_result(self):
        with tempfile.TemporaryDirectory() as one, tempfile.TemporaryDirectory() as many:
            sequential, seq_fail = self.resolve(one, 1, RecordingFetcher())
            concurrent, con_fail = self.resolve(many, 6, RecordingFetcher())
        self.assertEqual(sequential, concurrent)
        self.assertEqual(seq_fail, con_fail)
        self.assertEqual(len(sequential), len(ACCESSIONS))

    def test_failures_are_reported_in_a_stable_order(self):
        broken = {ACCESSIONS[3], ACCESSIONS[17], ACCESSIONS[29]}
        with tempfile.TemporaryDirectory() as one, tempfile.TemporaryDirectory() as many:
            _, seq_fail = self.resolve(one, 1, RecordingFetcher(fail=broken))
            _, con_fail = self.resolve(many, 6, RecordingFetcher(fail=broken))
        self.assertEqual([a for a, _ in seq_fail], sorted(broken))
        self.assertEqual(seq_fail, con_fail)


class DisjointWorkTests(unittest.TestCase):
    def test_no_accession_is_fetched_twice(self):
        fetcher = RecordingFetcher()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            resolve_acceptance_documents(
                ACCESSIONS, ISSUERS, owners_of=OWNERS, cache_dir=base / "cache",
                checkpoint_path=base / "cp.jsonl", fetcher=fetcher,
                workers=8, rate_per_second=1000.0)
        self.assertEqual(sorted(fetcher.calls), sorted(ACCESSIONS))
        self.assertEqual(len(fetcher.calls), len(set(fetcher.calls)))

    def test_shards_partition_the_work_exactly(self):
        shards = assign_disjoint(ACCESSIONS, 5)
        flat = [item for shard in shards for item in shard]
        self.assertEqual(sorted(flat), sorted(ACCESSIONS))
        self.assertEqual(len(flat), len(set(flat)))


class FairAccessTests(unittest.TestCase):
    def test_the_rate_limit_is_global_not_per_worker(self):
        """Eight workers must not draw eight times the configured rate."""
        rate = 20.0
        fetcher = RecordingFetcher()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            started = time.monotonic()
            resolve_acceptance_documents(
                ACCESSIONS, ISSUERS, owners_of=OWNERS, cache_dir=base / "cache",
                checkpoint_path=base / "cp.jsonl", fetcher=fetcher,
                workers=8, rate_per_second=rate)
            elapsed = time.monotonic() - started
        observed = len(ACCESSIONS) / elapsed
        self.assertLessEqual(observed, rate * 1.6,
                             f"observed {observed:.1f}/s against a {rate}/s budget")

    def test_a_single_limiter_paces_every_thread(self):
        limiter = RateLimiter(50.0, burst=1)
        stamps: list[float] = []
        lock = threading.Lock()

        def draw():
            for _ in range(10):
                limiter.acquire()
                with lock:
                    stamps.append(time.monotonic())

        threads = [threading.Thread(target=draw) for _ in range(4)]
        start = time.monotonic()
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        elapsed = time.monotonic() - start
        self.assertGreaterEqual(elapsed, 39 / 50 * 0.8)
        self.assertEqual(len(stamps), 40)


class AtomicWriteTests(unittest.TestCase):
    def test_write_leaves_no_temporary_behind(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "doc.html"
            write_atomic(target, b"payload")
            self.assertEqual(target.read_bytes(), b"payload")
            self.assertEqual([p.name for p in Path(directory).iterdir()], ["doc.html"])

    def test_replacement_is_all_or_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "doc.html"
            write_atomic(target, b"first")
            write_atomic(target, b"second-and-longer")
            self.assertEqual(target.read_bytes(), b"second-and-longer")

    def test_concurrent_writers_never_expose_a_partial_document(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "doc.html"
            payloads = [bytes([code]) * 4096 for code in (65, 66, 67, 68)]
            observed: list[bytes] = []
            stop = threading.Event()

            def writer():
                for _ in range(40):
                    for payload in payloads:
                        write_atomic(target, payload)
                stop.set()

            def reader():
                while not stop.is_set():
                    if target.exists():
                        data = target.read_bytes()
                        if data:
                            observed.append(data)

            threads = [threading.Thread(target=writer), threading.Thread(target=reader)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            for data in observed:
                self.assertIn(data, payloads, "a reader observed a partially written file")


class ExactResumeTests(unittest.TestCase):
    def test_an_interrupted_run_resumes_without_refetching(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            first = RecordingFetcher()
            resolve_acceptance_documents(
                ACCESSIONS[:15], ISSUERS, owners_of=OWNERS, cache_dir=base / "cache",
                checkpoint_path=base / "cp.jsonl", fetcher=first,
                workers=3, rate_per_second=1000.0, batch_size=2)

            second = RecordingFetcher()
            resolved, failures = resolve_acceptance_documents(
                ACCESSIONS, ISSUERS, owners_of=OWNERS, cache_dir=base / "cache",
                checkpoint_path=base / "cp.jsonl", fetcher=second,
                workers=3, rate_per_second=1000.0, batch_size=2)

        self.assertEqual(len(resolved), len(ACCESSIONS))
        self.assertEqual(failures, [])
        self.assertEqual(sorted(second.calls), sorted(ACCESSIONS[15:]),
                         "resume must re-fetch exactly the outstanding accessions")

    def test_resume_equals_an_uninterrupted_run(self):
        with tempfile.TemporaryDirectory() as split, tempfile.TemporaryDirectory() as whole:
            base = Path(split)
            resolve_acceptance_documents(
                ACCESSIONS[:9], ISSUERS, owners_of=OWNERS, cache_dir=base / "cache",
                checkpoint_path=base / "cp.jsonl", fetcher=RecordingFetcher(),
                workers=4, rate_per_second=1000.0, batch_size=3)
            resumed, _ = resolve_acceptance_documents(
                ACCESSIONS, ISSUERS, owners_of=OWNERS, cache_dir=base / "cache",
                checkpoint_path=base / "cp.jsonl", fetcher=RecordingFetcher(),
                workers=4, rate_per_second=1000.0, batch_size=3)

            other = Path(whole)
            uninterrupted, _ = resolve_acceptance_documents(
                ACCESSIONS, ISSUERS, owners_of=OWNERS, cache_dir=other / "cache",
                checkpoint_path=other / "cp.jsonl", fetcher=RecordingFetcher(),
                workers=1, rate_per_second=1000.0)
        self.assertEqual(resumed, uninterrupted)

    def test_every_checkpoint_entry_carries_a_verifiable_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            resolve_acceptance_documents(
                ACCESSIONS[:6], ISSUERS, owners_of=OWNERS, cache_dir=base / "cache",
                checkpoint_path=base / "cp.jsonl", fetcher=RecordingFetcher(),
                workers=2, rate_per_second=1000.0, batch_size=2)
            entries = load_acceptance_checkpoint(base / "cp.jsonl")
            self.assertEqual(len(entries), 6)
            for accession, record in entries.items():
                payload = (base / "cache" / f"{accession}.html").read_bytes()
                self.assertEqual(record["sha256"], _sha256_bytes(payload))
                self.assertEqual(record["bytes"], len(payload))
                self.assertTrue(record["acceptance_time"])

    def test_a_checkpoint_entry_whose_bytes_changed_is_not_resumed(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            resolve_acceptance_documents(
                ACCESSIONS[:5], ISSUERS, owners_of=OWNERS, cache_dir=base / "cache",
                checkpoint_path=base / "cp.jsonl", fetcher=RecordingFetcher(),
                workers=1, rate_per_second=1000.0)
            tampered = base / "cache" / f"{ACCESSIONS[2]}.html"
            tampered.write_bytes(header(ACCESSIONS[2], "20990101120000"))
            missing = base / "cache" / f"{ACCESSIONS[4]}.html"
            missing.unlink()

            kept, stale = validate_acceptance_cache(
                load_acceptance_checkpoint(base / "cp.jsonl"), base / "cache",
                ISSUERS, OWNERS)
            self.assertEqual(stale, sorted([ACCESSIONS[2], ACCESSIONS[4]]))
            self.assertNotIn(ACCESSIONS[2], kept)

            again = RecordingFetcher()
            resolve_acceptance_documents(
                ACCESSIONS[:5], ISSUERS, owners_of=OWNERS, cache_dir=base / "cache",
                checkpoint_path=base / "cp.jsonl", fetcher=again,
                workers=1, rate_per_second=1000.0)
            self.assertEqual(sorted(again.calls), sorted([ACCESSIONS[2], ACCESSIONS[4]]))

    def test_a_torn_checkpoint_line_is_ignored_not_trusted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cp.jsonl"
            good = {"accession": "A", "sha256": "x", "bytes": 1, "acceptance_time": "t",
                    "url": "u"}
            path.write_text(json.dumps(good) + "\n" + '{"accession": "B", "sha2')
            entries = load_acceptance_checkpoint(path)
            self.assertEqual(list(entries), ["A"])


class DocumentIdentityTests(unittest.TestCase):
    """A timestamp is only meaningful once the document is proven to be the one asked for."""

    ACC = ACCESSIONS[0]

    def test_identity_is_read_from_the_sgml_block_not_the_rendering(self):
        document = parse_acceptance_document(PAYLOADS[self.ACC])
        self.assertEqual(document.accession, self.ACC)
        self.assertEqual(document.submission_type, "4")
        self.assertEqual(document.issuer_ciks, (ISSUER_CIK,))
        self.assertEqual(document.owner_ciks, ("0001723460",))

    def test_a_substituted_document_is_refused(self):
        other = header(ACCESSIONS[1], "20240101120000")
        with self.assertRaises(AcceptanceIdentityError) as caught:
            verify_acceptance_document(other, self.ACC, ISSUER_CIK, ["0001723460"])
        self.assertIn("expected", str(caught.exception))

    def test_an_amendment_cannot_supply_an_acceptance_time(self):
        amendment = header(self.ACC, "20240101120000", submission_type="4/A")
        with self.assertRaises(AcceptanceIdentityError):
            verify_acceptance_document(amendment, self.ACC, ISSUER_CIK, ["0001723460"])

    def test_a_document_for_another_issuer_is_refused(self):
        wrong = header(self.ACC, "20240101120000", issuer="0000999999")
        with self.assertRaises(AcceptanceIdentityError):
            verify_acceptance_document(wrong, self.ACC, ISSUER_CIK, ["0001723460"])

    def test_a_document_missing_the_expected_owner_is_refused(self):
        wrong = header(self.ACC, "20240101120000", owner="0000888888")
        with self.assertRaises(AcceptanceIdentityError):
            verify_acceptance_document(wrong, self.ACC, ISSUER_CIK, ["0001723460"])

    def test_bytes_that_merely_contain_a_timestamp_are_refused(self):
        with self.assertRaises(AcceptanceIdentityError):
            verify_acceptance_document(b"<ACCEPTANCE-DATETIME>20240101120000",
                                       self.ACC, ISSUER_CIK, ["0001723460"])


class CachePromotionTests(unittest.TestCase):
    """A cache entry no checkpoint vouches for must earn its place."""

    def test_a_legacy_entry_is_not_promoted_on_a_parsable_timestamp(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            cache = base / "cache"
            cache.mkdir(parents=True)
            # A legacy file: right shape, wrong document.
            (cache / f"{ACCESSIONS[0]}.html").write_bytes(
                header(ACCESSIONS[1], "20200101120000"))
            fetcher = RecordingFetcher()
            resolved, failures = resolve_acceptance_documents(
                ACCESSIONS[:2], ISSUERS, owners_of=OWNERS, cache_dir=cache,
                checkpoint_path=base / "cp.jsonl", fetcher=fetcher,
                workers=1, rate_per_second=1000.0)
            self.assertIn(ACCESSIONS[0], fetcher.calls,
                          "a legacy cache entry must be re-verified, not trusted")
            self.assertEqual(resolved[ACCESSIONS[0]]["acceptance_time"],
                             parse_acceptance_document(PAYLOADS[ACCESSIONS[0]]).acceptance_time)

    def test_a_genuine_legacy_entry_is_promoted_without_refetching(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            cache = base / "cache"
            cache.mkdir(parents=True)
            (cache / f"{ACCESSIONS[0]}.html").write_bytes(PAYLOADS[ACCESSIONS[0]])
            fetcher = RecordingFetcher()
            resolve_acceptance_documents(
                ACCESSIONS[:1], ISSUERS, owners_of=OWNERS, cache_dir=cache,
                checkpoint_path=base / "cp.jsonl", fetcher=fetcher,
                workers=1, rate_per_second=1000.0)
            self.assertEqual(fetcher.calls, [], "a verified document need not be refetched")


class ResumeRecomputationTests(unittest.TestCase):
    def test_a_stored_acceptance_time_is_not_trusted_over_the_bytes(self):
        """A matching hash proves the bytes are unchanged, not that the record describes them."""
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            resolve_acceptance_documents(
                ACCESSIONS[:3], ISSUERS, owners_of=OWNERS, cache_dir=base / "cache",
                checkpoint_path=base / "cp.jsonl", fetcher=RecordingFetcher(),
                workers=1, rate_per_second=1000.0)
            lines = (base / "cp.jsonl").read_text().splitlines()
            doctored = []
            for line in lines:
                record = json.loads(line)
                if record["accession"] == ACCESSIONS[1]:
                    record["acceptance_time"] = "1999-01-01T00:00:00"  # hash still matches
                doctored.append(json.dumps(record, sort_keys=True))
            (base / "cp.jsonl").write_text("\n".join(doctored) + "\n")

            kept, stale = validate_acceptance_cache(
                load_acceptance_checkpoint(base / "cp.jsonl"), base / "cache", ISSUERS, OWNERS)
            self.assertIn(ACCESSIONS[1], stale,
                          "a record contradicting its own bytes must not be resumed")
            for accession, record in kept.items():
                document = parse_acceptance_document(
                    (base / "cache" / f"{accession}.html").read_bytes())
                self.assertEqual(record["acceptance_time"], document.acceptance_time)


class TornTailTests(unittest.TestCase):
    def test_torn_tail_then_resume_then_append_then_reload(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            resolve_acceptance_documents(
                ACCESSIONS[:6], ISSUERS, owners_of=OWNERS, cache_dir=base / "cache",
                checkpoint_path=base / "cp.jsonl", fetcher=RecordingFetcher(),
                workers=1, rate_per_second=1000.0, batch_size=2)

            # Simulate a kill part-way through an append.
            path = base / "cp.jsonl"
            path.write_bytes(path.read_bytes() + b'{"accession": "0001234560-24-0000')

            dropped = repair_checkpoint_tail(path)
            self.assertGreater(dropped, 0)
            self.assertTrue(path.read_bytes().endswith(b"\n"))

            resolved, failures = resolve_acceptance_documents(
                ACCESSIONS[:10], ISSUERS, owners_of=OWNERS, cache_dir=base / "cache",
                checkpoint_path=path, fetcher=RecordingFetcher(),
                workers=1, rate_per_second=1000.0, batch_size=2)
            self.assertEqual(failures, [])
            self.assertEqual(len(resolved), 10)

            reloaded = load_acceptance_checkpoint(path)
            self.assertEqual(len(reloaded), 10, "every line must round-trip after repair")
            for line in path.read_text().splitlines():
                json.loads(line)

    def test_a_kill_between_cache_write_and_checkpoint_loses_nothing(self):
        """The dangerous boundary: bytes on disk, checkpoint not yet appended."""
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            cache = base / "cache"
            cache.mkdir(parents=True)
            for accession in ACCESSIONS[:4]:
                write_atomic(cache / f"{accession}.html", PAYLOADS[accession])
            # No checkpoint at all: the run died before its first flush.
            fetcher = RecordingFetcher()
            resolved, failures = resolve_acceptance_documents(
                ACCESSIONS[:4], ISSUERS, owners_of=OWNERS, cache_dir=cache,
                checkpoint_path=base / "cp.jsonl", fetcher=fetcher,
                workers=2, rate_per_second=1000.0, batch_size=2)
            self.assertEqual(fetcher.calls, [], "verified bytes on disk are not refetched")
            self.assertEqual(len(resolved), 4)
            self.assertEqual(len(load_acceptance_checkpoint(base / "cp.jsonl")), 4)


class RetryBudgetTests(unittest.TestCase):
    def test_every_retry_draws_from_the_global_budget(self):
        import urllib.error
        from quant.dataplane import sec_form4

        attempts = {"n": 0}
        draws = {"n": 0}

        class CountingLimiter(RateLimiter):
            def acquire(self, tokens: float = 1.0) -> None:
                draws["n"] += 1

        def flaky(request, timeout=None):
            attempts["n"] += 1
            raise urllib.error.HTTPError(request.full_url, 500, "boom", {}, None)

        limiter = CountingLimiter(1000.0)
        with mock.patch("urllib.request.urlopen", flaky), \
             mock.patch.dict(os.environ, {"SEC_USER_AGENT": "Quant-Trade a@b.com"}):
            with self.assertRaises(RuntimeError):
                sec_form4._http_get("https://www.sec.gov/x", retries=4, delay=0,
                                    limiter=limiter)
        self.assertEqual(attempts["n"], 4)
        self.assertEqual(draws["n"], 4, "a retry is a real request and must be charged")


import os  # noqa: E402
from unittest import mock  # noqa: E402


if __name__ == "__main__":
    unittest.main()
