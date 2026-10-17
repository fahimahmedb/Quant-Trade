from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext
from research.research_os.expansion.engine_dossiers_v1 import build_engine_dossier
from research.research_os.expansion.source_adapters_v1 import validate_adapter_spec
from research.research_os.expansion.wave3_engine_depth import build_wave3_engine_depth


class Wave3EngineDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = Path("research/research_os")
        cls.base_fixture = json.loads((cls.base / "simulations" / "aggressive_architecture_fixture.json").read_text())
        cls.wave2_fixture = json.loads((cls.base / "simulations" / "wave2_hardening_fixture.json").read_text())
        cls.wave3_fixture = json.loads((cls.base / "simulations" / "wave3_engine_depth_fixture.json").read_text())
        cls.legacy_path = cls.base / "legacy" / "LEGACY_RESEARCH_LEDGER.imported.json"

    def build(self):
        return build_wave3_engine_depth(
            self.base_fixture,
            self.wave2_fixture,
            self.wave3_fixture,
            legacy_ledger_path=self.legacy_path if self.legacy_path.exists() else None,
        )

    def test_wave3_passes_with_four_deep_engine_dossiers(self) -> None:
        result = self.build()
        self.assertEqual(result["wave3_status"], "PASS")
        self.assertEqual(result["wave2_status"], "PASS")
        dossiers = result["engine_dossiers"]
        self.assertEqual(dossiers["record_count"], 4)
        self.assertEqual(dossiers["pass_count"], 4)
        self.assertEqual(dossiers["block_count"], 0)
        self.assertEqual(dossiers["economic_results_observed"], 0)
        self.assertEqual(dossiers["candidate_mutations"], 0)
        self.assertTrue(all(record["outcome_accessed"] is False for record in dossiers["records"]))

    def test_design_only_adapters_are_valid_but_inactive(self) -> None:
        result = self.build()
        registry = result["adapter_registry"]
        self.assertEqual(registry["entry_count"], 5)
        self.assertEqual(registry["activated_count"], 0)
        self.assertEqual(registry["network_enabled_count"], 0)
        self.assertEqual(registry["outcome_authorized_count"], 0)
        self.assertTrue(registry["immutable"])
        self.assertTrue(all(item["status"] == "PASS" for item in result["validated_adapters"].values()))
        self.assertTrue(all(item["status"] == "READY_DESIGN_ONLY" for item in result["adapter_bindings"].values()))

    def test_flow_dossier_can_be_complete_while_wave2_scientific_gate_blocks(self) -> None:
        result = self.build()
        flow = result["engine_states"]["SYN-FLOW-001"]
        self.assertEqual(flow["dossier"], "PASS")
        self.assertEqual(flow["adapter_binding"], "READY_DESIGN_ONLY")
        self.assertEqual(flow["wave2_dry_run"], "BLOCK")
        self.assertEqual(flow["wave2_validator"], "BLOCK")
        self.assertEqual(flow["economic_result"], "NOT_OBSERVED")

    def test_candidate_hypotheses_are_not_mutated(self) -> None:
        result = self.build()
        integrity = result["candidate_integrity"]
        self.assertTrue(integrity["unchanged"])
        self.assertEqual(integrity["before"], integrity["after"])
        self.assertFalse(result["unsafe_access_detected"])

    def test_network_enabled_adapter_is_blocked(self) -> None:
        spec = copy.deepcopy(self.wave3_fixture["adapters"][0])
        spec["network_access"] = True
        validated = validate_adapter_spec(spec)
        self.assertEqual(validated["status"], "BLOCK")
        self.assertIn("NETWORK_ACCESS_FORBIDDEN_IN_WAVE3", validated["blockers"])
        self.assertFalse(validated["activated"])
        self.assertFalse(validated["outcome_access_authorized"])

    def test_missing_fundamental_section_blocks_dossier(self) -> None:
        output = ENGINE_REGISTRY["fundamental"].run(
            self.base_fixture["sources"]["fundamental"],
            EngineContext(run_id="WAVE3-UNIT", synthetic_only=True),
        )
        detail = copy.deepcopy(self.wave3_fixture["engine_details"]["SYN-FUND-001"])
        detail.pop("valuation_frame")
        record = build_engine_dossier(output, detail)
        self.assertEqual(record["status"], "BLOCK")
        self.assertIn("MISSING_VALUATION_FRAME", record["blockers"])
        self.assertFalse(record["candidate_mutated"])
        self.assertFalse(record["outcome_accessed"])

    def test_all_authorities_remain_off(self) -> None:
        result = self.build()
        self.assertFalse(result["real_source_activation_authorized"])
        self.assertFalse(result["network_access_authorized"])
        self.assertFalse(result["economic_experiment_authorized"])
        self.assertFalse(result["prospective_observation_authorized"])
        self.assertFalse(result["real_capital_authorized"])
        self.assertFalse(result["live_trading_authorized"])

    def test_wave3_is_deterministic(self) -> None:
        self.assertEqual(self.build(), self.build())


if __name__ == "__main__":
    unittest.main()
