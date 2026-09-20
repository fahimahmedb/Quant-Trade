"""Tests for the manual Forward Data runner.

The live Yahoo request is intentionally not made here. These tests prove the
runner uses the same due/execute seam with injectable adapters.
"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

from quant.dataplane.forward_capture import ATTEMPT_SUCCEEDED, FrozenForwardTimebase
from quant.dataplane.panel import PricePanel

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "forward_capture_runner", ROOT / "scripts" / "forward_capture_runner.py")
runner = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(runner)


def one_bar():
    return PricePanel([{
        "date": "2026-09-18",
        "symbol": "XLK",
        "open": 100.0,
        "high": 101.0,
        "low": 99.0,
        "close": 100.5,
        "adj_close": 100.5,
        "volume": 1_000_000.0,
    }])


class ForwardCaptureRunnerTest(unittest.TestCase):
    def test_due_runner_calls_exact_capture_seam_and_persists_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            timebase = FrozenForwardTimebase()
            calls = []

            def adapter(symbols):
                calls.append(tuple(symbols))
                return one_bar(), {"adapter": "fake"}

            summary = runner.run_capture(
                Path(directory), ["XLK"], adapter=adapter, timebase=timebase,
                attempt_id="runner-test-attempt")

            self.assertEqual(calls, [("XLK",)])
            self.assertEqual(summary["state"], "ATTEMPTED")
            self.assertEqual(summary["attempt_outcome"], ATTEMPT_SUCCEEDED)
            self.assertEqual(summary["accepted_count"], 1)
            self.assertEqual(summary["attempts_journaled"], 1)
            self.assertIsNotNone(summary["ledger_fingerprint"])
            paths = runner.state_paths(Path(directory))
            self.assertTrue(paths["observations"].exists())
            self.assertTrue(paths["attempts"].exists())
            self.assertTrue(paths["tasks"].exists())

    def test_not_due_runner_does_not_call_adapter_or_create_second_attempt(self):
        with tempfile.TemporaryDirectory() as directory:
            timebase = FrozenForwardTimebase()
            runner.run_capture(
                Path(directory), ["XLK"],
                adapter=lambda symbols: (one_bar(), {}),
                timebase=timebase,
                attempt_id="first-attempt")

            def must_not_run(symbols):
                raise AssertionError("adapter was called while task was NOT_DUE")

            second = runner.run_capture(
                Path(directory), ["XLK"], adapter=must_not_run, timebase=timebase)

            self.assertEqual(second["state"], "NOT_DUE")
            self.assertEqual(second["attempts_journaled"], 1)


if __name__ == "__main__":
    unittest.main()
