"""Synthetic restart/coverage regressions; no network and no ZIP parsing."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from research.crypto_carry_f1 import capture_stage_a as c


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name) / "capture"
        self.candidates = Path(self.temp.name) / "candidates.txt"
        self.candidates.write_bytes(b"BTCUSDT\n")
        self.sha = c.digest(self.candidates)
        self.body = b"synthetic opaque compressed bytes; never parsed"
        self.fetches = []

    def listing(self, prefix):
        name = "BTCUSDT-fundingRate" if "fundingRate" in prefix else "BTCUSDT-1d"
        return [prefix + name + "-2023-12.zip", prefix + name + "-2024-01.zip"]

    def fetch(self, job, out_dir):
        self.fetches.append(job)
        ds, sym, key = job
        path = Path(out_dir) / ds / sym / key.rsplit("/", 1)[-1]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.body)
        sha = hashlib.sha256(self.body).hexdigest()
        return {"dataset": ds, "symbol": sym, "key": key, "ok": True,
                "sha256": sha, "checksum_sha256": sha, "bytes": len(self.body)}

    def capture(self):
        with patch.object(c.transport, "list_files", side_effect=self.listing), patch.object(c.transport, "fetch_one", side_effect=self.fetch):
            return c.capture(self.out, self.candidates, self.sha)

    def test_frozen_plan_filters_b_and_verifies_all_archives(self):
        report = self.capture()
        self.assertEqual((report["status"], report["verified"], report["rows_parsed"]), ("COMPLETE", 3, 0))
        self.assertTrue(all("2023-12" in job[2] for job in self.fetches))
        with patch.object(c.transport, "list_files", side_effect=AssertionError("verification listed")), patch.object(c.transport, "fetch_one", side_effect=AssertionError("verification downloaded")):
            self.assertEqual(c.capture(self.out, self.candidates, self.sha, True)["status"], "COMPLETE")

    def test_resume_preserves_plan_and_does_not_refetch_verified(self):
        self.capture()
        plan_bytes = (self.out / "plan_STAGE_A.json").read_bytes()
        self.fetches.clear()
        with patch.object(c.transport, "list_files", side_effect=AssertionError("resume relisted")), patch.object(c.transport, "fetch_one", side_effect=self.fetch):
            c.capture(self.out, self.candidates, self.sha)
        self.assertEqual(self.fetches, [])
        self.assertEqual((self.out / "plan_STAGE_A.json").read_bytes(), plan_bytes)

    def test_failure_is_incomplete_and_resume_fetches_only_missing(self):
        calls = 0
        def interrupt(job, out):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError("worker lost")
            return self.fetch(job, out)
        with patch.object(c.transport, "list_files", side_effect=self.listing), patch.object(c.transport, "fetch_one", side_effect=interrupt):
            with self.assertRaisesRegex(RuntimeError, "worker lost"):
                c.capture(self.out, self.candidates, self.sha)
        self.assertEqual(json.loads((self.out / "capture_STAGE_A.json").read_bytes())["verified"], 1)
        self.fetches.clear()
        self.capture()
        self.assertEqual(len(self.fetches), 2)

    def test_missing_or_changed_archive_blocks_verification_then_refetches(self):
        self.capture()
        files = sorted(self.out.glob("*/*/*.zip"))
        files[0].unlink()
        files[1].write_bytes(b"X" * len(self.body))
        with self.assertRaisesRegex(RuntimeError, "incomplete"):
            c.capture(self.out, self.candidates, self.sha, True)
        self.fetches.clear()
        self.capture()
        self.assertEqual(len(self.fetches), 2)

    def test_truncated_tail_repair_and_interior_corruption_rejection(self):
        self.capture()
        path = self.out / "manifest_STAGE_A.jsonl"
        clean = path.read_bytes()
        path.write_bytes(clean + b'{"key":')
        self.capture()
        self.assertEqual(path.read_bytes(), clean)
        path.write_bytes(b'{"key":\n' + clean)
        with self.assertRaisesRegex(ValueError, "corrupt acquisition manifest"):
            self.capture()

    def test_complete_unterminated_record_is_preserved(self):
        self.capture()
        path = self.out / "manifest_STAGE_A.jsonl"
        clean = path.read_bytes()
        path.write_bytes(clean.rstrip(b"\n"))
        self.capture()
        self.assertEqual(path.read_bytes(), clean)

    def test_bad_plan_binding_and_truncated_jobs_abort_before_download(self):
        self.capture()
        path = self.out / "plan_STAGE_A.json"
        original = json.loads(path.read_bytes())
        for field, value in [("candidates_sha256", "0" * 64), ("jobs", original["jobs"][:-1]), ("window", ["2024-01", "2024-12"])]:
            with self.subTest(field=field):
                plan = dict(original)
                plan[field] = value
                path.write_text(json.dumps(plan))
                with patch.object(c.transport, "fetch_one", side_effect=AssertionError("download before validation")):
                    with self.assertRaises(ValueError):
                        c.capture(self.out, self.candidates, self.sha)

    def test_persistent_listing_404_aborts_before_any_archive(self):
        def missing(prefix):
            c.transport.LISTING_404.append(prefix)
            return []
        with patch.object(c.transport, "list_files", side_effect=missing), patch.object(c.transport, "fetch_one", side_effect=AssertionError("download despite failed listing")):
            with self.assertRaises(ValueError):
                c.capture(self.out, self.candidates, self.sha)
        self.assertFalse((self.out / "plan_STAGE_A.json").exists())


if __name__ == "__main__":
    unittest.main()
