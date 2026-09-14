from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from quant.recorders.http import FetchResponse, NetworkFetchError
from quant.recorders.models import EndpointSpec
from quant.recorders.recorder import ForwardRecorder
from quant.recorders.storage import AtomicCaptureStore


class FakeTransport:
    def __init__(self, bodies):
        self.bodies = list(bodies)
    def fetch(self, endpoint, *, timeout_seconds):
        body = self.bodies.pop(0)
        if isinstance(body, Exception):
            raise body
        return FetchResponse(200, {"content-type": "application/json"}, body)


class StepClock:
    def __init__(self, values):
        self.values = list(values)
        self.last = self.values[-1]
    def __call__(self):
        if self.values:
            self.last = self.values.pop(0)
        return self.last


class MonoClock:
    def __init__(self): self.value = 0
    def __call__(self):
        self.value += 5_000_000
        return self.value


def spec():
    return EndpointSpec("test-time", "test", "spot", "BTCUSDT", "server_time", "https://public.invalid/time", source_time_field="serverTime", expected_cadence_seconds=60)


class RestartTests(unittest.TestCase):
    def test_restart_deduplicates_raw_and_records_polling_gap(self):
        t0 = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
        body = json.dumps({"serverTime": int(t0.timestamp() * 1000)}).encode()
        with tempfile.TemporaryDirectory() as tmp:
            store = AtomicCaptureStore(tmp)
            first = ForwardRecorder(store, transport=FakeTransport([body]), now_fn=StepClock([t0, t0, t0]), monotonic_ns_fn=MonoClock())
            summary1 = first.run_once([spec()])
            self.assertEqual((summary1.captured, summary1.successful, summary1.failed, summary1.final_mode), (1, 1, 0, "IDLE"))

            t1 = t0 + timedelta(minutes=5)
            second = ForwardRecorder(store, transport=FakeTransport([body]), now_fn=StepClock([t1, t1, t1, t1]), monotonic_ns_fn=MonoClock())
            summary2 = second.run_once([spec()])
            self.assertEqual(summary2.duplicates, 1)
            self.assertGreaterEqual(summary2.gaps_written, 1)
            raw_files = list(Path(tmp).glob("raw/**/*.bin"))
            capture_files = list(Path(tmp).glob("captures/**/*.json"))
            gap_files = list(Path(tmp).glob("gaps/**/*.json"))
            self.assertEqual(len(raw_files), 1)
            self.assertEqual(len(capture_files), 2)
            self.assertTrue(any(json.loads(path.read_text())["reason"] == "polling_gap" for path in gap_files))
            self.assertEqual(store.load_state().mode, "IDLE")

    def test_unclean_restart_is_ledgered_and_recovers_to_idle(self):
        t0 = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
        body = b'{"serverTime":1789387200000}'
        with tempfile.TemporaryDirectory() as tmp:
            store = AtomicCaptureStore(tmp)
            state = store.load_state()
            state.mode = "RUN"
            state.run_id = "crashed-run"
            store.save_state(state)
            recorder = ForwardRecorder(store, transport=FakeTransport([body]), now_fn=StepClock([t0, t0, t0, t0]), monotonic_ns_fn=MonoClock())
            summary = recorder.run_once([spec()])
            self.assertGreaterEqual(summary.gaps_written, 1)
            reasons = [json.loads(path.read_text())["reason"] for path in Path(tmp).glob("gaps/**/*.json")]
            self.assertIn("unclean_restart", reasons)
            self.assertEqual(store.load_state().mode, "IDLE")

    def test_http_error_raw_is_persisted_but_not_counted_successful(self):
        t0 = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
        class HttpErrorTransport:
            def fetch(self, endpoint, *, timeout_seconds):
                return FetchResponse(451, {"content-type": "application/json"}, b'{"code":451,"msg":"blocked"}')
        with tempfile.TemporaryDirectory() as tmp:
            store = AtomicCaptureStore(tmp)
            recorder = ForwardRecorder(store, transport=HttpErrorTransport(), now_fn=StepClock([t0, t0, t0]), monotonic_ns_fn=MonoClock())
            summary = recorder.run_once([spec()])
            self.assertEqual((summary.captured, summary.successful, summary.failed), (1, 0, 1))
            self.assertEqual(len(list(Path(tmp).glob("raw/**/*.bin"))), 1)
            reasons = [json.loads(path.read_text())["reason"] for path in Path(tmp).glob("gaps/**/*.json")]
            self.assertIn("http_error", reasons)

    def test_fetch_error_is_gap_and_finally_returns_idle(self):
        t0 = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            store = AtomicCaptureStore(tmp)
            recorder = ForwardRecorder(store, transport=FakeTransport([NetworkFetchError("dns")]), now_fn=StepClock([t0, t0]), monotonic_ns_fn=MonoClock())
            summary = recorder.run_once([spec()])
            self.assertEqual((summary.captured, summary.failed), (0, 1))
            self.assertEqual(store.load_state().mode, "IDLE")
            reasons = [json.loads(path.read_text())["reason"] for path in Path(tmp).glob("gaps/**/*.json")]
            self.assertIn("fetch_error", reasons)


if __name__ == "__main__":
    unittest.main()
