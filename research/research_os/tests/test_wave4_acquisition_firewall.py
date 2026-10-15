from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from research.research_os.expansion.acquisition_firewall_v1 import (
    build_acquisition_plan,
    content_firewall,
)
from research.research_os.expansion.typed_pit_registry_v1 import TypedPITRegistry
from research.research_os.expansion.wave4_acquisition_firewall import build_wave4_acquisition_firewall
from research.research_os.expansion.wave3_engine_depth import build_wave3_engine_depth


class Wave4AcquisitionFirewallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = Path("research/research_os")
        cls.base_fixture = json.loads((cls.base / "simulations" / "aggressive_architecture_fixture.json").read_text())
        cls.wave2_fixture = json.loads((cls.base / "simulations" / "wave2_hardening_fixture.json").read_text())
        cls.wave3_fixture = json.loads((cls.base / "simulations" / "wave3_engine_depth_fixture.json").read_text())
        cls.wave4_fixture = json.loads((cls.base / "simulations" / "wave4_acquisition_firewall_fixture.json").read_text())
        cls.legacy_path = cls.base / "legacy" / "LEGACY_RESEARCH_LEDGER.imported.json"

    def build(self):
        return build_wave4_acquisition_firewall(
            self.base_fixture,
            self.wave2_fixture,
            self.wave3_fixture,
            self.wave4_fixture,
            legacy_ledger_path=self.legacy_path if self.legacy_path.exists() else None,
        )

    def wave3(self):
        return build_wave3_engine_depth(
            self.base_fixture,
            self.wave2_fixture,
            self.wave3_fixture,
            legacy_ledger_path=self.legacy_path if self.legacy_path.exists() else None,
        )

    def test_wave4_builds_five_typed_pit_records_without_network(self) -> None:
        result = self.build()
        self.assertEqual(result["wave4_status"], "PASS")
        self.assertEqual(result["wave3_status"], "PASS")
        self.assertFalse(result["unsafe_access_detected"])
        self.assertEqual(len(result["acquisition_plans"]), 5)
        self.assertTrue(all(plan["status"] == "READY_AWAITING_SOURCE_ACTIVATION_AUTHORITY" for plan in result["acquisition_plans"].values()))
        self.assertTrue(all(plan["network_call_performed"] is False for plan in result["acquisition_plans"].values()))
        self.assertTrue(all(plan["outcome_accessed"] is False for plan in result["acquisition_plans"].values()))
        self.assertEqual(result["firewall_summary"]["record_count"], 5)
        self.assertEqual(result["firewall_summary"]["pass_count"], 5)
        self.assertEqual(result["firewall_summary"]["block_count"], 0)
        self.assertEqual(result["firewall_summary"]["network_records"], 0)
        self.assertEqual(result["firewall_summary"]["outcomes_accessed"], 0)

    def test_typed_registry_is_complete_and_immutable_by_contract(self) -> None:
        result = self.build()
        registry = result["typed_pit_registry"]
        self.assertEqual(registry["entry_count"], 5)
        self.assertEqual(registry["point_in_time_count"], 5)
        self.assertEqual(registry["network_origin_count"], 0)
        self.assertEqual(registry["outcome_accessed_count"], 0)
        self.assertTrue(registry["immutable"])
        self.assertTrue(all(record["status"] == "PASS" for record in result["typed_pit_records"].values()))
        self.assertTrue(all(record["status"] == "PASS" for record in result["provenance_manifests"].values()))

    def test_every_primary_engine_has_typed_pit_input_refs(self) -> None:
        result = self.build()
        self.assertEqual(len(result["engine_input_bindings"]), 4)
        for binding in result["engine_input_bindings"].values():
            self.assertEqual(binding["status"], "READY_PIT_TYPED_FIXTURE_ONLY")
            self.assertTrue(binding["typed_pit_record_refs"])
            self.assertFalse(binding["network_access_authorized"])
            self.assertFalse(binding["outcome_access_authorized"])
            self.assertFalse(binding["candidate_mutated"])

    def test_forbidden_return_content_cannot_be_requested(self) -> None:
        wave3 = self.wave3()
        request = copy.deepcopy(self.wave4_fixture["acquisition_requests"][0])
        request["content_classes"].append("returns")
        adapter = wave3["validated_adapters"][request["adapter_id"]]
        plan = build_acquisition_plan(adapter, request)
        self.assertEqual(plan["status"], "BLOCK")
        self.assertIn("FORBIDDEN_CONTENT_REQUESTED:returns", plan["blockers"])
        self.assertFalse(plan["network_call_performed"])
        self.assertFalse(plan["outcome_accessed"])

    def test_outcome_bearing_raw_record_is_blocked(self) -> None:
        wave3 = self.wave3()
        request = self.wave4_fixture["acquisition_requests"][0]
        adapter = wave3["validated_adapters"][request["adapter_id"]]
        plan = build_acquisition_plan(adapter, request)
        raw = copy.deepcopy(self.wave4_fixture["raw_records"][request["request_id"]])
        raw["contains_outcome"] = True
        firewall = content_firewall(plan, raw)
        self.assertEqual(firewall["status"], "BLOCK")
        self.assertIn("OUTCOME_BEARING_RECORD_FORBIDDEN", firewall["blockers"])
        self.assertFalse(firewall["outcome_accessed"])

    def test_record_published_after_cutoff_is_blocked(self) -> None:
        wave3 = self.wave3()
        request = self.wave4_fixture["acquisition_requests"][0]
        adapter = wave3["validated_adapters"][request["adapter_id"]]
        plan = build_acquisition_plan(adapter, request)
        raw = copy.deepcopy(self.wave4_fixture["raw_records"][request["request_id"]])
        raw["published_at"] = "2026-10-15T13:05:00Z"
        raw["captured_at"] = "2026-10-15T13:06:00Z"
        firewall = content_firewall(plan, raw)
        self.assertEqual(firewall["status"], "BLOCK")
        self.assertIn("RECORD_PUBLISHED_AFTER_CLOCK_CUTOFF", firewall["blockers"])

    def test_registered_pit_record_cannot_be_silently_replaced(self) -> None:
        result = self.build()
        typed = copy.deepcopy(result["typed_pit_records"]["REQ-REG-001"])
        manifest = copy.deepcopy(result["provenance_manifests"]["REQ-REG-001"])
        registry = TypedPITRegistry()
        registry.register(typed, manifest)
        typed["typed_record_hash"] = "different-hash"
        with self.assertRaises(ValueError):
            registry.register(typed, manifest)

    def test_all_authorities_remain_off(self) -> None:
        result = self.build()
        self.assertFalse(result["real_source_activation_authorized"])
        self.assertFalse(result["network_access_authorized"])
        self.assertFalse(result["economic_experiment_authorized"])
        self.assertFalse(result["prospective_observation_authorized"])
        self.assertFalse(result["real_capital_authorized"])
        self.assertFalse(result["live_trading_authorized"])

    def test_wave4_is_deterministic(self) -> None:
        self.assertEqual(self.build(), self.build())


if __name__ == "__main__":
    unittest.main()
