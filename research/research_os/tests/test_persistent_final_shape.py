from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from research.research_os.expansion.persistent_state import (
    ForwardGenerationRegistry,
    ImmutableArtifactRegistry,
    build_persistent_final_shape,
)


class PersistentFinalShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Path(__file__).resolve().parents[1]
        cls.fixture = json.loads((cls.base / "simulations" / "aggressive_architecture_fixture.json").read_text())
        cls.imported = cls.base / "legacy" / "LEGACY_RESEARCH_LEDGER.imported.json"
        cls.result = build_persistent_final_shape(
            cls.fixture,
            legacy_ledger_path=cls.imported if cls.imported.exists() else None,
        )

    def test_persistent_state_passes(self):
        self.assertEqual(self.result["persistent_state_status"], "PASS")
        self.assertEqual(self.result["legacy"]["gate_status"], "PASS")
        self.assertEqual(self.result["legacy"]["exact_duplicate_count"], 0)
        self.assertFalse(self.result["legacy"]["historical_truth_mutated"])

    def test_pinned_legacy_is_loaded_when_materialized(self):
        if not self.imported.exists():
            self.skipTest("pinned ledger is materialized by CI")
        summary = self.result["legacy"]["summary"]
        self.assertEqual(summary["source_commit"], "183ad65ff260b903a16548ce37948f54d47a9ec8")
        self.assertEqual(summary["ledger_blob_sha"], "ba9b165aaf96956776672df51233bb9bf1e6cbc9")
        self.assertGreater(summary["loaded_record_count"], 0)
        self.assertTrue(summary["read_only"])

    def test_scientific_ledger_covers_full_shape_and_verifies(self):
        ledger = self.result["scientific_ledger"]
        self.assertTrue(ledger["verified"])
        kinds = {entry["kind"] for entry in ledger["entries"]}
        self.assertTrue({
            "SCIENTIFIC_SNAPSHOT", "TRIAL_RECORD", "LEGACY_REFERENCE", "LEGACY_SCREEN",
            "IMPLEMENTABILITY_ASSESSMENT", "EXPERIMENT_ENVELOPE", "INDEPENDENT_VALIDATION",
            "RED_TEAM_ASSESSMENT", "ECONOMIC_IDENTITY", "PORTFOLIO_MAP",
            "FORWARD_REGISTRATION", "DECAY_GUARD", "LEARNING_TELEMETRY", "WORKER_RECEIPT",
        }.issubset(kinds))

    def test_trial_ledger_keeps_effective_trials_unknown(self):
        trials = self.result["trial_ledger"]
        self.assertEqual(len(trials), 5)
        self.assertTrue(all(t["effective_trials_status"] == "UNKNOWN" for t in trials))
        self.assertTrue(all(t["estimated_effective_trials"] is None for t in trials))

    def test_experiment_registry_is_immutable(self):
        registry = ImmutableArtifactRegistry("test")
        envelope = deepcopy(self.result["experiment_envelopes"][0])
        artifact_id = envelope["experiment_id"]
        first = registry.register(artifact_id, envelope)
        second = registry.register(artifact_id, deepcopy(envelope))
        self.assertEqual(first, second)
        mutated = deepcopy(envelope)
        mutated["result"] = "FABRICATED_RESULT"
        with self.assertRaises(ValueError):
            registry.register(artifact_id, mutated)

    def test_forward_generation_registry_rejects_mutation(self):
        registry = ForwardGenerationRegistry("test-forward")
        registration = deepcopy(self.result["forward_farm"][0])
        registry.register_generation(registration)
        mutated = deepcopy(registration)
        mutated["readiness"] = "NOT_READY"
        with self.assertRaises(ValueError):
            registry.register_generation(mutated)

    def test_forward_observation_is_forbidden(self):
        registry = ForwardGenerationRegistry("test-forward")
        registration = deepcopy(self.result["forward_farm"][0])
        registry.register_generation(registration)
        with self.assertRaises(PermissionError):
            registry.consume_future_observation(registration["prospective_contract_id"], {"value": 1})

    def test_exact_legacy_duplicate_blocks_admission(self):
        candidate_id = self.result["engine_outputs"][0]["candidate"]["hypothesis_id"]
        ledger = {
            "schema_version": "legacy-research-ledger-v1",
            "governance": {"historical_result_immutability": True},
            "records": [{
                "HYPOTHESIS_ID": candidate_id,
                "LEGACY_ID_IF_ANY": "UNKNOWN",
                "RESULT": "NEGATIVE",
                "RESEARCH_DECISION": "KILL",
                "NEXT_LEGITIMATE_STEP": "Do not repeat"
            }]
        }
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.json"
            path.write_text(json.dumps(ledger))
            # Use the canonical manifest's schema contract through the loader by copying
            # only the ledger path; the source manifest remains repository-pinned.
            blocked = build_persistent_final_shape(self.fixture, legacy_ledger_path=path)
        self.assertEqual(blocked["legacy"]["gate_status"], "BLOCKED_EXACT_DUPLICATE")
        self.assertEqual(blocked["persistent_state_status"], "BLOCKED_OR_FAILED")


if __name__ == "__main__":
    unittest.main()
