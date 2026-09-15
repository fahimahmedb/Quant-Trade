from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

from quant.recorders.binance_public import binance_public_plan
from quant.recorders.models import CaptureRecord
from quant.recorders.storage import AtomicCaptureStore


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("record_forward_market_script", ROOT / "scripts" / "record_forward_market.py")
assert SPEC is not None and SPEC.loader is not None
SCRIPT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCRIPT)


class LiveProofGateTests(unittest.TestCase):
    def _seed_complete_plan(self, root: Path, *, status: int = 200) -> tuple:
        plan = binance_public_plan()
        store = AtomicCaptureStore(root)
        state = store.load_state()
        for sequence, endpoint in enumerate(plan, start=1):
            raw = ("{\"source\":\"%s\",\"sequence\":%d}" % (endpoint.source_id, sequence)).encode("utf-8")
            digest, raw_path, _ = store.persist_raw(
                utc_date="2026-09-15", source_id=endpoint.source_id, raw=raw
            )
            capture_id = "cap_" + f"{sequence:024x}"
            record = CaptureRecord(
                schema_version=1,
                capture_id=capture_id,
                sequence=sequence,
                source_id=endpoint.source_id,
                venue=endpoint.venue,
                market_type=endpoint.market_type,
                instrument=endpoint.instrument,
                purpose=endpoint.purpose,
                endpoint=endpoint.endpoint,
                retrieval_started_utc="2026-09-15T06:00:00.000Z",
                retrieval_completed_utc="2026-09-15T06:00:00.010Z",
                monotonic_started_ns=sequence * 100,
                monotonic_completed_ns=sequence * 100 + 10,
                duration_ms=0.00001,
                http_status=status,
                response_headers={"content-type": "application/json"},
                content_type="application/json",
                raw_sha256=digest,
                raw_bytes=len(raw),
                raw_path=raw_path,
                parser_version=endpoint.parser_version,
                source_time_ms=None,
                clock_skew_ms=None,
                duplicate_of=None,
                gap_from_previous_ms=None,
                gap_detected=False,
            )
            store.persist_capture(record)
            state.last_by_source[endpoint.source_id] = {
                "capture_id": capture_id,
                "raw_sha256": digest,
                "retrieval_completed_utc": record.retrieval_completed_utc,
                "sequence": sequence,
            }
            state.next_sequence = sequence + 1
            state.last_completed_utc = record.retrieval_completed_utc
        store.save_state(state)
        return plan

    def test_complete_durable_public_provenance_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = self._seed_complete_plan(root)
            proof = SCRIPT._verify_live_provenance(root, plan)
            self.assertEqual(proof["proof"], "PASS")
            self.assertEqual(proof["verified_sources"], len(plan))
            self.assertEqual(proof["failures"], [])

    def test_stale_successful_captures_cannot_satisfy_new_proof_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = self._seed_complete_plan(root)
            state = AtomicCaptureStore(root).recover_state()
            prior_sequences = {
                source_id: int(cursor["sequence"])
                for source_id, cursor in state.last_by_source.items()
            }
            proof = SCRIPT._verify_live_provenance(root, plan, prior_sequences=prior_sequences)
            self.assertEqual(proof["proof"], "FAIL")
            self.assertEqual(proof["verified_sources"], 0)
            self.assertEqual(len(proof["failures"]), len(plan))
            self.assertTrue(all("no fresh capture" in failure for failure in proof["failures"]))

    def test_non_2xx_capture_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = self._seed_complete_plan(root, status=451)
            proof = SCRIPT._verify_live_provenance(root, plan)
            self.assertEqual(proof["proof"], "FAIL")
            self.assertTrue(any("http_2xx" in failure for failure in proof["failures"]))

    def test_corrupted_raw_bytes_fail_hash_proof(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = self._seed_complete_plan(root)
            store = AtomicCaptureStore(root)
            cursor = store.load_state().last_by_source[plan[0].source_id]
            capture_id = cursor["capture_id"]
            capture_path = next((root / "captures").glob(f"**/{capture_id}.json"))
            import json
            metadata = json.loads(capture_path.read_text(encoding="utf-8"))
            (root / metadata["raw_path"]).write_bytes(b"corrupted")
            proof = SCRIPT._verify_live_provenance(root, plan)
            self.assertEqual(proof["proof"], "FAIL")
            self.assertTrue(any("sha256" in failure or "raw_bytes" in failure for failure in proof["failures"]))


if __name__ == "__main__":
    unittest.main()
