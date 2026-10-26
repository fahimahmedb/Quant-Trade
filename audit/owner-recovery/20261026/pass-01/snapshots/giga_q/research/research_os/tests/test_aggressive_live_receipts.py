from __future__ import annotations

import json
import unittest
from pathlib import Path

from research.research_os.expansion.live_receipts import run_with_live_receipts


class AggressiveLiveReceiptsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = Path(__file__).resolve().parents[1]
        fixture = json.loads((base / "simulations" / "aggressive_architecture_fixture.json").read_text())
        cls.first = run_with_live_receipts(fixture)
        cls.second = run_with_live_receipts(fixture)

    def test_bridge_passes(self):
        self.assertEqual(self.first["status"], "PASS")
        self.assertEqual(self.first["live_lab_bridge"]["status"], "PASS")
        self.assertFalse(self.first["live_lab_bridge"]["economic_semantics_fabricated"])

    def test_native_event_shape(self):
        events = self.first["worker_events"]
        self.assertGreater(len(events), 0)
        self.assertEqual(set(self.first["live_lab_bridge"]["native_event_types"]), {"ACTION_STARTED", "ACTION_COMPLETED"})
        for event in events:
            self.assertIn(event["event_type"], {"ACTION_STARTED", "ACTION_COMPLETED"})
            self.assertGreaterEqual(event["event_seq"], 1)
            self.assertEqual(event["generation"], 1)
            self.assertTrue(event["event_id"].startswith(self.first["run_id"] + ":"))

    def test_receipts_are_durable_facts_not_authority(self):
        receipts = self.first["worker_receipts"]
        self.assertEqual(self.first["live_lab_bridge"]["receipt_count"], len(receipts))
        self.assertGreater(len(receipts), 0)
        self.assertEqual(len({r["receipt_id"] for r in receipts}), len(receipts))
        for receipt in receipts:
            self.assertEqual(len(receipt["artifact_hash"]), 64)
            self.assertFalse(receipt["economic_experiment_authorized"])
            self.assertFalse(receipt["prospective_observation_authorized"])
            self.assertFalse(receipt["real_capital_authorized"])
            self.assertFalse(receipt["live_trading_authorized"])

    def test_implementability_block_is_visible(self):
        blocker_events = [
            e for e in self.first["worker_events"]
            if e["worker_id"] == "implementability.v1"
            and e["action_id"] == "implementability:SYN-FLOW-001"
            and e["event_type"] == "ACTION_STARTED"
        ]
        self.assertEqual(len(blocker_events), 1)
        self.assertEqual(blocker_events[0]["payload"]["ui_activity"], "blocker")

    def test_replay_is_deterministic(self):
        self.assertEqual(self.first["integration_fingerprint"], self.second["integration_fingerprint"])
        self.assertEqual(self.first["worker_events"], self.second["worker_events"])
        self.assertEqual(self.first["worker_receipts"], self.second["worker_receipts"])


if __name__ == "__main__":
    unittest.main()
