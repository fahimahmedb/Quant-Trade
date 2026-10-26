"""Causal receipt/storage challenges using only synthetic fiscal fixtures."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from quant.edge_lab.fiscal_vintages import FiscalVintages
from quant.edge_lab.store import Refused


class FiscalVintageTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.at = "2026-10-11T17:40:00Z"
        self.store = FiscalVintages(self.root, clock=lambda: self.at)
        self.body = b'{"synthetic_fixture":true,"value":1}'
        self.url = "https://example.invalid/synthetic-fiscal"

    def record(self, **kwargs):
        return self.store.record(self.body, source_url=self.url, synthetic=True, **kwargs)

    def test_late_receipt_cannot_inherit_earlier_publication_as_availability(self):
        row = self.record(provider_release_at="2025-01-01T12:00:00Z")
        self.assertEqual(row["usable_from_utc"], "2026-10-11T17:40:00+00:00")
        self.assertFalse(row["publication_time_authenticated"])
        self.assertEqual(row["sha256"], hashlib.sha256(self.body).hexdigest())

    def test_same_bytes_after_restart_preserve_first_receipt_and_distinguish_byte_change(self):
        first = self.record(); saved = (self.root / (first["sha256"] + ".json")).read_bytes()
        self.store = FiscalVintages(self.root, clock=lambda: "2026-10-12T00:00:00Z")
        second = self.record()
        self.assertFalse(second["new_byte_version"])
        self.assertEqual(second["previous"], first["receipt_hash"])
        changed = self.store.record(b'{"synthetic_fixture":true,"value":2}', source_url=self.url, synthetic=True)
        self.assertTrue(changed["new_byte_version"])
        self.assertFalse(changed["economic_revision_authenticated"])
        self.assertEqual((self.root / (first["sha256"] + ".json")).read_bytes(), saved)

    def test_clock_regression_and_missing_timezone_fail_without_rewriting_index(self):
        self.record(); saved = (self.root / "manifest.json").read_bytes()
        for t in ("2026-10-11T17:39:59Z", "2026-10-11T17:40:01"):
            self.at = t
            with self.assertRaises(Refused): self.record()
            self.assertEqual((self.root / "manifest.json").read_bytes(), saved)

    def test_real_source_or_unlabelled_empirical_bytes_are_refused_before_storage(self):
        for body, url, synthetic in ((self.body, "https://ec.europa.eu/eurostat/api", True),
                (b'{"real":1}', self.url, True), (self.body, self.url, False)):
            with self.assertRaises(Refused): self.store.record(body, source_url=url, synthetic=synthetic)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_interrupted_write_and_corrupted_saved_payload_are_not_automatically_recaptured(self):
        sha = hashlib.sha256(self.body).hexdigest(); path = self.root/(sha+".json")
        path.write_bytes(self.body)
        with self.assertRaisesRegex(Refused, "interrupted"): self.record()
        path.unlink(); self.record(); path.write_bytes(b"damaged")
        with self.assertRaisesRegex(Refused, "differs"): self.record()
        self.assertEqual(path.read_bytes(), b"damaged")

    def test_payload_bound_and_damaged_index_fail_closed(self):
        with self.assertRaises(Refused): FiscalVintages(self.root, max_bytes=0)
        with self.assertRaises(Refused): self.store.record(b"x"*262145, source_url=self.url, synthetic=True)
        self.record(); path=self.root/"manifest.json"; s=json.loads(path.read_text());s["receipts"][0]["recorded_at_utc"]="2000-01-01T00:00:00Z";path.write_text(json.dumps(s))
        with self.assertRaisesRegex(Refused, "Damaged"): self.record()


if __name__ == "__main__": unittest.main()
