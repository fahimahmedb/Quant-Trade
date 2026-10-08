import json
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

import neg_risk_collector as n
import run_frozen_screen as r
from test_neg_risk_collector import book, event


class MeasurementCorrectionTests(unittest.TestCase):
    def payload(self, skew=False):
        e = n.normalize_standard_neg_risk_event(event())
        books = []
        for i, token in enumerate(e.token_ids):
            bids = [("0.55", "20")] if token in ("y2", "y3") else [("0.10", "20")]
            asks = [("0.30", "20")] if token == "n1" else [("0.90", "20")]
            ts = 1700000000000 + (50000 if skew and i == 0 else 0)
            books.append(book(token, bids, asks, t=ts))
        return e, books

    def test_corrected_arithmetic_equals_frozen_arithmetic_when_legacy_gate_valid(self):
        e, books = self.payload(skew=False)
        legacy = [asdict(x) for x in n.evaluate_routes(e, books)]
        corrected = [asdict(x) for x in r.evaluate_routes_same_economics(n, e, books)]
        self.assertEqual(corrected, legacy)

    def test_state_timestamp_skew_is_not_economic_input(self):
        e, skewed = self.payload(skew=True)
        with self.assertRaises(n.DataContractError):
            n.evaluate_routes(e, skewed)
        corrected = [asdict(x) for x in r.evaluate_routes_same_economics(n, e, skewed)]
        e2, synchronous = self.payload(skew=False)
        reference = [asdict(x) for x in n.evaluate_routes(e2, synchronous)]
        self.assertEqual(corrected, reference)

    def test_economic_constants_remain_frozen(self):
        self.assertEqual(r.SNAPSHOTS, 60)
        self.assertEqual(r.INTERVAL_S, 10.0)
        self.assertEqual(r.MAX_EVENTS, 10)
        self.assertEqual(str(r.THRESHOLD_USDC), "0.10")
        self.assertEqual(str(r.THRESHOLD_RATE), "0.001")
        self.assertEqual(r.MAX_ACQUISITION_SPAN_MS, 1000.0)

    def test_entrypoint_failure_still_writes_diagnostic(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out"
            code = r.run("smoke", out, simulate_failure=True)
            self.assertNotEqual(code, 0)
            diagnostic = json.loads((out / "diagnostic.json").read_text())
            self.assertEqual(diagnostic["status"], "FAILED")
            self.assertIn("SIMULATED_ENTRYPOINT_FAILURE", diagnostic["error"])


if __name__ == "__main__":
    unittest.main()
