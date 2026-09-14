from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from quant.recorders.models import CaptureRecord
from quant.recorders.storage import AtomicCaptureStore


class StorageTests(unittest.TestCase):
    def test_raw_bytes_are_exact_and_content_addressed(self):
        raw = b"\x00{not-normalized}\n\xff"
        with tempfile.TemporaryDirectory() as tmp:
            store = AtomicCaptureStore(tmp)
            digest, relative, duplicate = store.persist_raw(utc_date="2026-09-14", source_id="s", raw=raw)
            self.assertFalse(duplicate)
            self.assertEqual(digest, hashlib.sha256(raw).hexdigest())
            self.assertEqual((Path(tmp) / relative).read_bytes(), raw)
            digest2, relative2, duplicate2 = store.persist_raw(utc_date="2026-09-14", source_id="s", raw=raw)
            self.assertTrue(duplicate2)
            self.assertEqual((digest2, relative2), (digest, relative))

    def test_capture_replay_is_idempotent_and_conflict_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = AtomicCaptureStore(tmp)
            values = dict(
                schema_version=1, capture_id="cap_" + "a" * 24, sequence=1, source_id="s", venue="v",
                market_type="spot", instrument="BTCUSDT", purpose="depth", endpoint="https://x",
                retrieval_started_utc="2026-09-14T00:00:00.000Z", retrieval_completed_utc="2026-09-14T00:00:00.001Z",
                monotonic_started_ns=1, monotonic_completed_ns=2, duration_ms=0.000001, http_status=200,
                response_headers={}, content_type="application/json", raw_sha256="b" * 64, raw_bytes=1,
                raw_path="raw/x", parser_version="p", source_time_ms=None, clock_skew_ms=None,
                duplicate_of=None, gap_from_previous_ms=None, gap_detected=False,
            )
            record = CaptureRecord(**values)
            first = store.persist_capture(record)
            second = store.persist_capture(record)
            self.assertEqual(first, second)
            changed = CaptureRecord(**{**values, "raw_bytes": 2})
            with self.assertRaises(IOError):
                store.persist_capture(changed)

    def test_schemas_are_valid_json_and_no_outcome_fields(self):
        root = Path(__file__).resolve().parents[1]
        for path in sorted((root / "schemas").glob("forward_capture_*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["$schema"], "https://json-schema.org/draft/2020-12/schema")
            lowered = json.dumps(payload).lower()
            for forbidden in ("pnl", "signal_score", "strategy_return", "trade_decision"):
                self.assertNotIn(forbidden, lowered)


if __name__ == "__main__":
    unittest.main()
