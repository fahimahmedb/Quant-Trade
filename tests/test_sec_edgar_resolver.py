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
    RateLimiter,
    _sha256_bytes,
    assign_disjoint,
    load_acceptance_checkpoint,
    resolve_acceptance_documents,
    validate_acceptance_cache,
    write_atomic,
)

import tempfile


def header(stamp: str) -> bytes:
    return f"<SEC-HEADER>\n<ACCEPTANCE-DATETIME>{stamp}\n</SEC-HEADER>".encode()


ACCESSIONS = [f"000123456{i // 100}-2{i % 5}-{i:06d}" for i in range(40)]
ISSUERS = {acc: "0000320193" for acc in ACCESSIONS}
PAYLOADS = {acc: header(f"2024010{(i % 9) + 1}12000{i % 10}")
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
            ACCESSIONS, ISSUERS, cache_dir=base / "cache",
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
                ACCESSIONS, ISSUERS, cache_dir=base / "cache",
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
                ACCESSIONS, ISSUERS, cache_dir=base / "cache",
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
                ACCESSIONS[:15], ISSUERS, cache_dir=base / "cache",
                checkpoint_path=base / "cp.jsonl", fetcher=first,
                workers=3, rate_per_second=1000.0, batch_size=2)

            second = RecordingFetcher()
            resolved, failures = resolve_acceptance_documents(
                ACCESSIONS, ISSUERS, cache_dir=base / "cache",
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
                ACCESSIONS[:9], ISSUERS, cache_dir=base / "cache",
                checkpoint_path=base / "cp.jsonl", fetcher=RecordingFetcher(),
                workers=4, rate_per_second=1000.0, batch_size=3)
            resumed, _ = resolve_acceptance_documents(
                ACCESSIONS, ISSUERS, cache_dir=base / "cache",
                checkpoint_path=base / "cp.jsonl", fetcher=RecordingFetcher(),
                workers=4, rate_per_second=1000.0, batch_size=3)

            other = Path(whole)
            uninterrupted, _ = resolve_acceptance_documents(
                ACCESSIONS, ISSUERS, cache_dir=other / "cache",
                checkpoint_path=other / "cp.jsonl", fetcher=RecordingFetcher(),
                workers=1, rate_per_second=1000.0)
        self.assertEqual(resumed, uninterrupted)

    def test_every_checkpoint_entry_carries_a_verifiable_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            resolve_acceptance_documents(
                ACCESSIONS[:6], ISSUERS, cache_dir=base / "cache",
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
                ACCESSIONS[:5], ISSUERS, cache_dir=base / "cache",
                checkpoint_path=base / "cp.jsonl", fetcher=RecordingFetcher(),
                workers=1, rate_per_second=1000.0)
            tampered = base / "cache" / f"{ACCESSIONS[2]}.html"
            tampered.write_bytes(header("20990101120000"))
            missing = base / "cache" / f"{ACCESSIONS[4]}.html"
            missing.unlink()

            kept, stale = validate_acceptance_cache(
                load_acceptance_checkpoint(base / "cp.jsonl"), base / "cache")
            self.assertEqual(stale, sorted([ACCESSIONS[2], ACCESSIONS[4]]))
            self.assertNotIn(ACCESSIONS[2], kept)

            again = RecordingFetcher()
            resolve_acceptance_documents(
                ACCESSIONS[:5], ISSUERS, cache_dir=base / "cache",
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


if __name__ == "__main__":
    unittest.main()
