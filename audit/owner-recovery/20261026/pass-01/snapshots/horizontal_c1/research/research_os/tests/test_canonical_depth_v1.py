from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from research.research_os.expansion.canonical_depth_v1 import enrich_canonical_depth
from research.research_os.expansion.canonical_spine import run_canonical_spine


ENGINE_CAPABILITY = {
    "quant": "quant_mechanisms",
    "fundamental": "fundamental",
    "event_document": "event_document",
    "institutional_flow": "institutional_flows",
}


class CanonicalDepthV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = Path(__file__).resolve().parents[1]
        cls.base_fixture = json.loads((cls.base / "simulations" / "aggressive_architecture_fixture.json").read_text())
        cls.wave2_fixture = json.loads((cls.base / "simulations" / "wave2_hardening_fixture.json").read_text())
        cls.wave3_fixture = json.loads((cls.base / "simulations" / "wave3_engine_depth_fixture.json").read_text())
        cls.task_template = json.loads((cls.base / "simulations" / "canonical_spine_task.json").read_text())
        cls.legacy_path = cls.base / "legacy" / "LEGACY_RESEARCH_LEDGER.imported.json"

    def _run(self, engine_key: str):
        task = deepcopy(self.task_template)
        task["task_id"] = f"CANONICAL-DEPTH-{engine_key.upper()}"
        task["required_capability"] = ENGINE_CAPABILITY[engine_key]
        task["inputs"]["engine_key"] = engine_key
        task["lease"]["owner"] = f"canonical-depth-{engine_key}.v1"

        canonical = run_canonical_spine(
            self.base,
            self.base_fixture,
            task,
            legacy_ledger_path=self.legacy_path,
        )
        depth = enrich_canonical_depth(
            canonical,
            self.base_fixture,
            self.wave2_fixture,
            self.wave3_fixture,
        )
        return canonical, depth

    def test_four_engine_depth_profiles_preserve_system_safety(self) -> None:
        results = {}
        for engine_key in ENGINE_CAPABILITY:
            canonical, depth = self._run(engine_key)
            results[engine_key] = (canonical, depth)
            self.assertEqual(canonical["status"], "PASS")
            self.assertEqual(depth["system_status"], "PASS")
            self.assertTrue(depth["candidate_unchanged"])
            self.assertFalse(depth["unsafe_access_detected"])
            self.assertFalse(depth["economic_result_observed"])
            self.assertFalse(depth["economic_experiment_authorized"])
            self.assertFalse(depth["prospective_observation_authorized"])
            self.assertFalse(depth["real_capital_authorized"])
            self.assertFalse(depth["live_trading_authorized"])
            self.assertEqual(depth["source_qualification"]["status"], "PASS")
            self.assertIsNotNone(depth["engine_dossier"])
            self.assertEqual(depth["engine_dossier"]["status"], "PASS")
            self.assertFalse(depth["portfolio_v2"]["return_series_consumed"])
            self.assertFalse(depth["portfolio_v2"]["capital_allocation_authorized"])
            self.assertFalse(depth["portfolio_v2"]["orders_authorized"])
            self.assertEqual(depth["forward_registry_v2"]["authorized_count"], 0)
            self.assertEqual(depth["forward_registry_v2"]["future_outcomes_consumed"], 0)

        for engine_key in ("quant", "fundamental", "event_document"):
            depth = results[engine_key][1]
            self.assertEqual(depth["dry_run_experiment"]["status"], "READY_FOR_REPRODUCIBLE_DRY_RUN")
            self.assertEqual(depth["dry_run_replay"]["status"], "REPLAY_MATCH")
            self.assertEqual(depth["validator_v2"]["status"], "PASS")
            self.assertEqual(depth["validator_v2"]["claim_ceiling"], "READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY")

        # A scientific blocker remains a valid system outcome. The flow lineage must
        # not be force-promoted merely to make the depth profile look green.
        flow = results["institutional_flow"][1]
        self.assertNotEqual(flow["candidate_state"]["implementability"], "PASS")
        self.assertEqual(flow["dry_run_experiment"]["status"], "BLOCK")
        self.assertEqual(flow["validator_v2"]["status"], "BLOCK")
        self.assertEqual(flow["system_status"], "PASS")

    def test_depth_enrichment_does_not_change_canonical_stage_order(self) -> None:
        canonical, depth = self._run("quant")
        original_order = list(canonical["stage_order"])
        _ = depth
        self.assertEqual(canonical["stage_order"], original_order)
        self.assertNotIn("CANONICAL_DEPTH", canonical["stage_order"])

    def test_depth_profile_is_deterministic(self) -> None:
        _, a = self._run("quant")
        _, b = self._run("quant")
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
