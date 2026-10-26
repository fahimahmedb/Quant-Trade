"""Synthetic local HTML fixtures prove archival, never publisher authenticity."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from quant.dataplane.evidence import EvidenceCorruptionError, EvidenceStore
from research.research_os.expansion.source_adapters_v1 import capture_apple_dividend_announcements


class RawEvidenceCaptureTests(unittest.TestCase):
    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        source = Path(__file__).resolve().parents[1] / "research/research_os/sources/apple_dividend_announcements.json"
        captured = deepcopy(json.loads(source.read_text())["documentary_packet"]["capture"])
        paths, original = [], []
        for index, record in enumerate(captured["records"]):
            raw = ("<!-- SYNTHETIC LOCAL STORAGE TEST; NOT PUBLISHER EVIDENCE -->\n<p>"
                   + record["capture_excerpt"] + "</p>").encode()
            record["raw_sha256"] = hashlib.sha256(raw).hexdigest()
            path = root / f"synthetic-{index}.html"
            path.write_bytes(raw)
            paths.append(path)
            original.append(raw)
        return captured, paths, original, EvidenceStore(root / "raw-evidence")

    def test_exact_raw_bytes_are_retrievable_idempotently_without_changing_packet(self):
        captured, paths, raw, store = self.fixture()
        before = deepcopy(captured)
        legacy = capture_apple_dividend_announcements(captured, paths)
        self.assertEqual(capture_apple_dividend_announcements(captured, paths, evidence_store=store), legacy)
        first_manifest = store.read_manifest()
        self.assertEqual(capture_apple_dividend_announcements(captured, paths, evidence_store=store), legacy)
        self.assertEqual(store.read_manifest(), first_manifest)
        for record, original in zip(captured["records"], raw):
            self.assertEqual(store.get_bytes("sha256:" + record["raw_sha256"]), original)
        self.assertEqual(captured, before)
        self.assertTrue(store.audit_manifest())

    def test_all_inputs_must_validate_before_any_raw_evidence_is_archived(self):
        captured, paths, _, store = self.fixture()
        paths[1].write_bytes(b"synthetic mismatched second document")
        with patch.object(store, "put_bytes", wraps=store.put_bytes) as write:
            with self.assertRaisesRegex(ValueError, "capture digest mismatch"):
                capture_apple_dividend_announcements(captured, paths, evidence_store=store)
            write.assert_not_called()
        self.assertEqual(store.read_manifest(), [])

    def test_existing_corrupt_raw_object_cannot_be_silently_reused_or_overwritten(self):
        captured, paths, _, store = self.fixture()
        capture_apple_dividend_announcements(captured, paths, evidence_store=store)
        target = store.object_path("sha256:" + captured["records"][0]["raw_sha256"])
        target.write_bytes(b"synthetic corruption")
        with self.assertRaises(EvidenceCorruptionError):
            capture_apple_dividend_announcements(captured, paths, evidence_store=store)
        self.assertEqual(target.read_bytes(), b"synthetic corruption")

    def test_archival_uses_verified_bytes_even_if_caller_changes_a_file_mid_archive(self):
        captured, paths, original, store = self.fixture()
        write = store.put_bytes
        def mutate_then_write(raw, **kwargs):
            paths[1].write_bytes(b"synthetic concurrent file replacement")
            return write(raw, **kwargs)
        legacy = capture_apple_dividend_announcements(captured, paths)
        with patch.object(store, "put_bytes", side_effect=mutate_then_write):
            self.assertEqual(capture_apple_dividend_announcements(captured, paths, evidence_store=store), legacy)
        for record, raw in zip(captured["records"], original):
            self.assertEqual(store.get_bytes("sha256:" + record["raw_sha256"]), raw)
        self.assertNotEqual(paths[1].read_bytes(), original[1])
