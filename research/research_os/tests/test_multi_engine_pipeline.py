import copy
import json
import unittest
from pathlib import Path

from research.research_os.engines.pipeline import run_pipeline
from research.research_os.legacy import LegacyKnowledgeBase
from research.research_os.scientific_store import AppendOnlyHashLedger


class MultiEnginePipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Path(__file__).resolve().parents[1]
        fixture = json.loads((cls.base / "simulations" / "multi_engine_fixture.json").read_text())
        imported = cls.base / "legacy" / "LEGACY_RESEARCH_LEDGER.imported.json"
        cls.result = run_pipeline(fixture, legacy_ledger_path=imported if imported.exists() else None)

    def test_pipeline_passes(self):
        self.assertEqual(self.result["status"], "PASS")
        self.assertTrue(self.result["synthetic_only"])

    def test_control_plane_is_preprod_and_complete(self):
        c = self.result["control_plane"]
        self.assertEqual(c["status"], "PASS")
        self.assertEqual(set(c["capabilities"]), {
            "legacy_recovery",
            "quant_mechanisms",
            "fundamental",
            "event_document",
            "institutional_flows",
            "validator",
            "red_team",
            "portfolio_map",
        })
        self.assertTrue(all(value is False for value in c["global_authority"].values()))

    def test_all_initial_engines_present(self):
        families = {e["engine_family"] for e in self.result["engines"]}
        self.assertEqual(families, {
            "QUANT_MECHANISM",
            "FUNDAMENTAL",
            "EVENT_DOCUMENT",
            "INSTITUTIONAL_FLOW",
        })

    def test_legacy_source_is_pinned_and_read_only(self):
        summary = self.result["legacy"]["summary"]
        self.assertEqual(summary["source_commit"], "183ad65ff260b903a16548ce37948f54d47a9ec8")
        self.assertEqual(summary["ledger_blob_sha"], "ba9b165aaf96956776672df51233bb9bf1e6cbc9")
        self.assertTrue(summary["read_only"])
        self.assertEqual(summary["reconciliation_status"], "PARTIAL_WITH_EXPLICIT_GAPS")
        self.assertEqual(summary["historical_research_items_found"], 33)
        self.assertEqual(summary["known_duplicate_or_variant_items"], 17)
        self.assertEqual(summary["prospective_validated"], 0)
        self.assertEqual(summary["global_effective_trials"], "UNKNOWN")

    def test_legacy_gate_blocks_exact_duplicate_when_ledger_loaded(self):
        ledger = {
            "schema_version": "legacy-research-ledger-v1",
            "governance": {"historical_result_immutability": True},
            "records": [{
                "HYPOTHESIS_ID": "SYN-QUANT-001",
                "LEGACY_ID_IF_ANY": "UNKNOWN",
                "RESULT": "NEGATIVE",
                "RESEARCH_DECISION": "KILL",
                "NEXT_LEGITIMATE_STEP": "Do not repeat"
            }]
        }
        manifest = json.loads((self.base / "legacy" / "source_manifest.json").read_text())
        kb = LegacyKnowledgeBase(manifest, ledger)
        candidate = self.result["engines"][0]["candidate"]
        screened = kb.screen_candidate(candidate)
        self.assertEqual(screened["status"], "BLOCK_EXACT_LEGACY_DUPLICATE")
        self.assertEqual(screened["historical_decision"], "KILL")

    def test_scientific_ledger_is_hash_chained(self):
        ledger = self.result["scientific_ledger"]
        self.assertTrue(ledger["verified"])
        self.assertEqual(ledger["entry_count"], 10)
        entries = ledger["entries"]
        self.assertIsNone(entries[0]["previous_hash"])
        for left, right in zip(entries, entries[1:]):
            self.assertEqual(right["previous_hash"], left["entry_hash"])

    def test_hash_chain_detects_tampering(self):
        original_entries = self.result["scientific_ledger"]["entries"]
        ledger = AppendOnlyHashLedger()
        ledger.entries = copy.deepcopy(original_entries)
        self.assertTrue(ledger.verify())
        ledger.entries[0]["payload"]["research_decision"] = "PROMOTE"
        self.assertFalse(ledger.verify())

    def test_trial_ledger_separates_attempts_and_effective_trials(self):
        trials = self.result["trial_ledger"]
        self.assertEqual(len(trials), 4)
        self.assertTrue(all(t["observed_attempt_count"] == 1 for t in trials))
        self.assertTrue(all(t["effective_trials_status"] == "UNKNOWN" for t in trials))
        self.assertTrue(all(t["estimated_effective_trials"] is None for t in trials))

    def test_cross_exam_does_not_mutate_or_generate(self):
        c = self.result["cross_exam"]
        self.assertEqual(c["status"], "COMPLETE")
        self.assertFalse(c["mutated_hypotheses"])
        self.assertFalse(c["new_hypotheses_created"])

    def test_validation_is_independent_and_clean(self):
        self.assertTrue(all(v["validator"] == "independent-validator.v0" for v in self.result["validations"]))
        self.assertTrue(all(v["status"] == "PASS" for v in self.result["validations"]))
        self.assertEqual(self.result["red_team"]["status"], "PASS")

    def test_portfolio_has_no_capital_authority(self):
        p = self.result["portfolio"]
        self.assertFalse(p["capital_allocation_authorized"])
        self.assertEqual(p["marginal_portfolio_value"], "NOT_ESTIMATED_WITHOUT_EMPIRICAL_RETURN_DATA")
        self.assertEqual(len(p["identities"]), 4)

    def test_shadow_and_decay_respect_authority(self):
        s = self.result["shadow"]
        self.assertFalse(s["prospective_observation_authorized"])
        self.assertTrue(all(x["observation_authorization"] == "NOT_AUTHORIZED" for x in s["registrations"]))
        self.assertTrue(all(x["observation_started"] is False for x in s["registrations"]))
        self.assertEqual(self.result["decay"]["status"], "INACTIVE_BY_AUTHORITY")
        self.assertEqual(self.result["decay"]["observations_consumed"], 0)

    def test_learning_telemetry_does_not_invent_effective_trials(self):
        t = self.result["learning_telemetry"]
        self.assertEqual(t["known_attempts"], 4)
        self.assertEqual(t["effective_trials_status"], "UNKNOWN")
        self.assertIsNone(t["effective_trials"])

    def test_authority_invariants(self):
        self.assertEqual(self.result["authorities"], {
            "production_workers": False,
            "real_capital": False,
            "live_trading": False,
            "prospective_observation": False,
            "economic_experiment": False,
        })

    def test_worker_events_are_deterministic_and_native_shaped(self):
        events = self.result["worker_events"]
        self.assertGreaterEqual(len(events), 20)
        self.assertEqual(events[0]["emitted_at"], "2026-10-15T00:00:01Z")
        for event in events:
            self.assertIn(event["event_type"], {"ACTION_STARTED", "ACTION_COMPLETED"})
            self.assertGreaterEqual(event["event_seq"], 1)
            self.assertEqual(event["generation"], 1)
            self.assertIn(event["payload"]["ui_activity"], {
                "none","source-research","document-reading","data-qualification",
                "coding-testing","calculation-economic-look","audit-red-team",
                "commit-persistence","handoff","result","blocker"
            })


if __name__ == "__main__":
    unittest.main()
