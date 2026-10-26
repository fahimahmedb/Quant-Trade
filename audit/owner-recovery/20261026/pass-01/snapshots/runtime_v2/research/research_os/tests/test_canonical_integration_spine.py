from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from research.research_os.expansion.canonical_spine import run_canonical_spine
from research.research_os.legacy import LegacyKnowledgeBase


EXPECTED_ORDER = [
    "GOVERNANCE_SNAPSHOT",
    "CONTROL_PLANE_SNAPSHOT",
    "TASK_CLAIM",
    "CANDIDATE_HYPOTHESIS",
    "LEGACY_SCREEN",
    "IMPLEMENTABILITY_ASSESSMENT",
    "EXPERIMENT_ENVELOPE",
    "INDEPENDENT_VALIDATION",
    "RED_TEAM_ASSESSMENT",
    "ECONOMIC_IDENTITY",
    "PORTFOLIO_MAP",
    "FORWARD_REGISTRATION",
    "DECAY_GUARD",
    "LEARNING_TELEMETRY",
    "CANONICAL_PERSISTENCE",
    "HANDOFF",
]


class CanonicalIntegrationSpineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = Path(__file__).resolve().parents[1]
        cls.fixture = json.loads((cls.base / "simulations" / "aggressive_architecture_fixture.json").read_text())
        cls.task = json.loads((cls.base / "simulations" / "canonical_spine_task.json").read_text())
        cls.legacy_path = cls.base / "legacy" / "LEGACY_RESEARCH_LEDGER.imported.json"

    def run_spine(self, **kwargs):
        return run_canonical_spine(
            self.base,
            self.fixture,
            self.task,
            legacy_ledger_path=self.legacy_path,
            **kwargs,
        )

    def test_normal_path_passes_in_exact_canonical_order(self) -> None:
        result = self.run_spine()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["stage_order"], EXPECTED_ORDER)
        self.assertLess(
            result["stage_order"].index("LEGACY_SCREEN"),
            result["stage_order"].index("IMPLEMENTABILITY_ASSESSMENT"),
        )
        self.assertTrue(result["downstream_executed"])
        self.assertEqual(result["control_plane"]["status"], "PASS")
        self.assertEqual(result["task_validation"]["status"], "PASS")
        self.assertTrue(result["scientific_ledger"]["verified"])
        self.assertEqual(result["trial_ledger"][0]["effective_trials_status"], "UNKNOWN")
        self.assertIsNone(result["trial_ledger"][0]["estimated_effective_trials"])
        self.assertEqual(set(result["live_lab_bridge"]["native_event_types"]), {"ACTION_STARTED", "ACTION_COMPLETED"})
        self.assertEqual(result["live_lab_bridge"]["event_count"], len(EXPECTED_ORDER) * 2)
        self.assertEqual(result["live_lab_bridge"]["receipt_count"], len(EXPECTED_ORDER))
        self.assertTrue(all(value is False for value in result["authority"].values()))
        self.assertFalse(result["experiment_envelope"]["outcome_opened"])
        self.assertFalse(result["forward_registration"]["observation_started"])
        self.assertEqual(result["forward_registration"]["future_outcomes_consumed"], 0)
        self.assertFalse(result["portfolio"]["capital_allocation_authorized"])
        self.assertFalse(result["portfolio"]["orders_authorized"])
        self.assertTrue(result["validation"]["independent_from_producer"])

    def test_deterministic_replay(self) -> None:
        a = self.run_spine()
        b = self.run_spine()
        self.assertEqual(a["canonical_fingerprint"], b["canonical_fingerprint"])
        self.assertEqual(a["scientific_ledger"], b["scientific_ledger"])
        self.assertEqual(a["worker_events"], b["worker_events"])
        self.assertEqual(a["worker_receipts"], b["worker_receipts"])

    def test_exact_legacy_duplicate_stops_before_expensive_downstream(self) -> None:
        legacy = LegacyKnowledgeBase.load(self.base, self.legacy_path)
        self.assertTrue(legacy.by_id)
        duplicate_id = sorted(legacy.by_id)[0]
        result = self.run_spine(candidate_override_hypothesis_id=duplicate_id)
        self.assertEqual(result["status"], "BLOCKED_EXACT_LEGACY_DUPLICATE")
        self.assertEqual(result["legacy"]["screen"]["status"], "BLOCK_EXACT_LEGACY_DUPLICATE")
        self.assertFalse(result["downstream_executed"])
        self.assertEqual(result["downstream_stage_kinds"], [])
        self.assertNotIn("IMPLEMENTABILITY_ASSESSMENT", result["stage_order"])
        self.assertNotIn("EXPERIMENT_ENVELOPE", result["stage_order"])
        self.assertNotIn("INDEPENDENT_VALIDATION", result["stage_order"])
        self.assertNotIn("PORTFOLIO_MAP", result["stage_order"])
        self.assertNotIn("FORWARD_REGISTRATION", result["stage_order"])
        self.assertTrue(result["scientific_ledger"]["verified"])
        self.assertTrue(all(value is False for value in result["authority"].values()))

    def test_task_authority_violation_is_rejected(self) -> None:
        bad = deepcopy(self.task)
        bad["authority"]["economic_experiment_authorized"] = True
        with self.assertRaises(ValueError):
            run_canonical_spine(
                self.base,
                self.fixture,
                bad,
                legacy_ledger_path=self.legacy_path,
            )

    def test_task_route_mismatch_is_rejected(self) -> None:
        bad = deepcopy(self.task)
        bad["required_capability"] = "fundamental"
        with self.assertRaises(ValueError):
            run_canonical_spine(
                self.base,
                self.fixture,
                bad,
                legacy_ledger_path=self.legacy_path,
            )


if __name__ == "__main__":
    unittest.main()
