from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quant.dataplane.adapters import DataUnavailable, fetch_yahoo_daily
from quant.dataplane.evidence import EvidenceStore, sha256_bytes
from quant.dataplane.registry import DatasetRecord, DatasetRegistry


T0 = "2026-01-02T12:00:00+00:00"


class _Response:
    def __init__(self, payload: bytes):
        self.payload = payload

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return self.payload


def _yahoo_payload(close: float = 100.0) -> bytes:
    return json.dumps({
        "chart": {
            "error": None,
            "result": [{
                "timestamp": [1609459200],
                "indicators": {
                    "quote": [{
                        "open": [close - 1.0],
                        "high": [close + 1.0],
                        "low": [close - 2.0],
                        "close": [close],
                        "volume": [1234],
                    }],
                    "adjclose": [{"adjclose": [close]}],
                },
            }],
        },
    }, separators=(",", ":")).encode("utf-8")


class AdapterEvidenceContractTests(unittest.TestCase):
    def test_network_bytes_are_committed_before_structured_consumption(self) -> None:
        payload = _yahoo_payload()
        with tempfile.TemporaryDirectory() as directory:
            store = EvidenceStore(Path(directory))
            with patch("quant.dataplane.adapters.urllib.request.urlopen",
                       return_value=_Response(payload)):
                panel, provenance = fetch_yahoo_daily(["ABC"], evidence_store=store)

            self.assertEqual(panel.symbols, ["ABC"])
            self.assertEqual(provenance["evidence_status"], "CAPTURED")
            self.assertEqual(provenance["source_identity"], "yahoo_finance")
            self.assertEqual(provenance["source_product_identity"], "chart_api_v8_daily")
            self.assertEqual(len(provenance["evidence"]), 1)
            binding = provenance["evidence"][0]
            self.assertEqual(binding["sha256"], sha256_bytes(payload))
            self.assertEqual(store.get_bytes(binding["sha256"]), payload)
            self.assertIn(binding["receipt_id"],
                          [receipt.receipt_id for receipt in store.receipts(binding["sha256"])])

    def test_complete_but_unparseable_response_is_evidence_not_available_data(self) -> None:
        payload = b"not-json"
        with tempfile.TemporaryDirectory() as directory:
            store = EvidenceStore(Path(directory))
            with patch("quant.dataplane.adapters.urllib.request.urlopen",
                       return_value=_Response(payload)):
                with self.assertRaises(DataUnavailable):
                    fetch_yahoo_daily(["ABC"], evidence_store=store)
            self.assertEqual(store.get_bytes(sha256_bytes(payload)), payload)

    def test_same_uri_changed_bytes_are_distinct_content_identities(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = EvidenceStore(Path(directory))
            first = store.put_bytes(b"v1", source_uri="https://example.test/same", retrieved_at=T0)
            second = store.put_bytes(b"v2", source_uri="https://example.test/same", retrieved_at=T0)
            self.assertNotEqual(first.sha256, second.sha256)
            self.assertEqual(store.get_bytes(first.sha256), b"v1")
            self.assertEqual(store.get_bytes(second.sha256), b"v2")

    def test_renamed_uri_same_bytes_reuses_content_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = EvidenceStore(Path(directory))
            first = store.put_bytes(b"same", source_uri="https://example.test/old", retrieved_at=T0)
            second = store.put_bytes(b"same", source_uri="https://example.test/new", retrieved_at=T0)
            self.assertEqual(first.sha256, second.sha256)
            self.assertNotEqual(first.receipt_id, second.receipt_id)


class RegistryEvidenceGateTests(unittest.TestCase):
    def _registry(self, root: Path) -> DatasetRegistry:
        return DatasetRegistry(root / "var" / "dataset_registry.json", root)

    @staticmethod
    def _record(**overrides: object) -> DatasetRecord:
        values = {
            "dataset_id": "evidence-bound",
            "source": "declared source",
            "adapter": "test",
            "path": "data/datasets/test.csv",
            "availability": "AVAILABLE",
            "validation": {"passed": True, "problems": []},
            "evidence_required": True,
            "evidence_store_path": "var/evidence",
            "evidence": [],
        }
        values.update(overrides)
        return DatasetRecord(**values)

    def test_available_without_evidence_identity_is_rejected_downstream(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = self._registry(root)
            record = registry.register(self._record())
            self.assertEqual(record.availability, "INVALID")
            self.assertEqual(registry.available(), [])
            self.assertEqual(registry.missing_for([record.dataset_id]), [record.dataset_id])
            self.assertIn("no raw evidence identity", " ".join(record.validation["problems"]))

    def test_recoverable_content_and_receipt_qualify_binding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = EvidenceStore(root / "var" / "evidence")
            receipt = store.put_bytes(b"raw", source_uri="synthetic://raw", retrieved_at=T0)
            registry = self._registry(root)
            record = registry.register(self._record(evidence=[{
                "sha256": receipt.sha256,
                "receipt_id": receipt.receipt_id,
            }]))
            self.assertEqual(record.availability, "AVAILABLE")
            self.assertEqual([item.dataset_id for item in registry.available()], [record.dataset_id])

    def test_unrecoverable_raw_bytes_make_previous_available_record_unusable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = EvidenceStore(root / "var" / "evidence")
            receipt = store.put_bytes(b"raw", source_uri="synthetic://raw", retrieved_at=T0)
            registry = self._registry(root)
            record = registry.register(self._record(evidence=[{
                "sha256": receipt.sha256,
                "receipt_id": receipt.receipt_id,
            }]))
            self.assertTrue(registry.is_usable(record))
            store.object_path(receipt.sha256).unlink()
            self.assertFalse(registry.is_usable(record))
            self.assertEqual(registry.missing_for([record.dataset_id]), [record.dataset_id])

    def test_receipt_id_must_resolve_for_the_declared_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = EvidenceStore(root / "var" / "evidence")
            receipt = store.put_bytes(b"raw", source_uri="synthetic://raw", retrieved_at=T0)
            registry = self._registry(root)
            record = registry.register(self._record(evidence=[{
                "sha256": receipt.sha256,
                "receipt_id": "receipt:" + "0" * 64,
            }]))
            self.assertEqual(record.availability, "INVALID")
            self.assertIn("receipt is not recoverable", " ".join(record.validation["problems"]))


if __name__ == "__main__":
    unittest.main()
