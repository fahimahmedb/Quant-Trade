from __future__ import annotations

import json
import unittest
from pathlib import Path

from research.research_os.expansion.final_shape import run_aggressive_pipeline


class AggressiveArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = Path(__file__).resolve().parents[1]
        fixture = json.loads((base / "simulations" / "aggressive_architecture_fixture.json").read_text())
        cls.first = run_aggressive_pipeline(fixture)
        cls.second = run_aggressive_pipeline(fixture)

    def test_pipeline_passes(self):
        self.assertEqual(self.first["status"], "PASS")
        self.assertTrue(self.first["synthetic_only"])

    def test_five_producer_families_present(self):
        families = {x["engine_family"] for x in self.first["engine_outputs"]}
        self.assertEqual(families, {
            "QUANT_MECHANISM",
            "FUNDAMENTAL",
            "EVENT_DOCUMENT",
            "INSTITUTIONAL_FLOW",
            "EDGE_ARCHAEOLOGY",
        })

    def test_implementability_is_early_and_non_destructive(self):
        by_id = {x["hypothesis_id"]: x for x in self.first["implementability"]}
        self.assertEqual(by_id["SYN-FLOW-001"]["status"], "PARK_IMPLEMENTABILITY")
        self.assertIn("COST_MODEL_NOT_QUALIFIED", by_id["SYN-FLOW-001"]["blockers"])
        self.assertIn("CAPACITY_NOT_OBSERVABLE", by_id["SYN-FLOW-001"]["blockers"])
        self.assertFalse(any(x["mechanism_rewritten"] for x in by_id.values()))
        self.assertFalse(any(x["research_decision_rewritten"] for x in by_id.values()))

    def test_experiment_infra_never_opens_outcomes(self):
        for envelope in self.first["experiment_envelopes"]:
            self.assertFalse(envelope["outcome_opened"])
            self.assertEqual(envelope["result"], "NOT_OBSERVED")
            self.assertEqual(envelope["observed_attempts"], 0)
            self.assertEqual(envelope["effective_trials_status"], "UNKNOWN")
        flow = next(x for x in self.first["experiment_envelopes"] if x["hypothesis_generation"].startswith("SYN-FLOW-001"))
        self.assertEqual(flow["status"], "NOT_FROZEN_BY_IMPLEMENTABILITY")
        self.assertIsNone(flow["protocol_hash"])

    def test_validator_is_independent(self):
        self.assertTrue(all(x["independent_from_producer"] for x in self.first["validations"]))
        self.assertTrue(all(x["validator"] != x["producer_engine"] for x in self.first["validations"]))
        self.assertTrue(all(x["claim_mutated"] is False for x in self.first["validations"]))

    def test_red_team_has_negative_rights_and_no_repairs(self):
        flow = next(x for x in self.first["red_teams"] if x["hypothesis_id"] == "SYN-FLOW-001")
        self.assertEqual(flow["status"], "BLOCK")
        self.assertIn("BLOCK_COST_MODEL", flow["negative_rights"])
        self.assertIn("BLOCK_CAPACITY", flow["negative_rights"])
        self.assertFalse(any(x["repair_attempted"] for x in self.first["red_teams"]))
        self.assertFalse(any(x["claim_mutated"] for x in self.first["red_teams"]))

    def test_portfolio_map_has_identity_but_no_capital(self):
        p = self.first["portfolio"]
        self.assertEqual(p["portfolio_engine"], "portfolio-map.v1")
        self.assertEqual(len(p["identities"]), 5)
        self.assertEqual(len(p["pairwise"]), 10)
        self.assertFalse(p["capital_allocation_authorized"])
        self.assertFalse(p["position_sizing_authorized"])
        self.assertFalse(p["orders_authorized"])

    def test_forward_farm_is_readiness_only(self):
        for r in self.first["forward_farm"]:
            self.assertEqual(r["observation_authorization"], "NOT_AUTHORIZED")
            self.assertFalse(r["observation_started"])
            self.assertEqual(r["future_outcomes_consumed"], 0)
            self.assertTrue(r["material_change_requires_new_generation"])
        flow = next(x for x in self.first["forward_farm"] if x["hypothesis_id"] == "SYN-FLOW-001")
        self.assertEqual(flow["readiness"], "NOT_READY")

    def test_decay_is_inactive_by_authority(self):
        d = self.first["decay"]
        self.assertEqual(d["status"], "INACTIVE_BY_AUTHORITY")
        self.assertEqual(d["observations_consumed"], 0)
        self.assertEqual(d["decay_decisions_emitted"], 0)

    def test_learning_does_not_invent_edge_or_trials(self):
        t = self.first["learning_telemetry"]
        self.assertEqual(t["effective_trials_status"], "UNKNOWN")
        self.assertIsNone(t["effective_trials"])
        self.assertFalse(t["economic_edge_inferred"])
        self.assertFalse(t["research_budget_allocator_enabled"])

    def test_authority_boundaries(self):
        self.assertEqual(self.first["authority"], {
            "economic_experiment_authorized": False,
            "prospective_observation_authorized": False,
            "real_capital_authorized": False,
            "live_trading_authorized": False,
        })

    def test_deterministic_replay(self):
        self.assertEqual(self.first["deterministic_fingerprint"], self.second["deterministic_fingerprint"])
        self.assertEqual(self.first, self.second)


if __name__ == "__main__":
    unittest.main()
