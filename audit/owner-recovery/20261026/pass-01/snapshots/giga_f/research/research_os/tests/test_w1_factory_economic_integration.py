from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from research.research_os.expansion.economic_test_readiness_v1 import READY, economic_test_readiness
from research.research_os.tests.test_economic_readiness_integration import fixture, legacy


def _declare_geometry_and_power(protocol):
    protocol["geometry_declaration"] = {
        "status": "DECLARED", "observation_unit": "event", "target_observations": 120,
        "dependence_assumption": "independent event units by preregistration",
        "cluster_key": None, "max_cluster_share": None, "sampling_rule": "all eligible events",
        "assumptions": ["pre-outcome"],
    }
    protocol["power_declaration"] = {
        "status": "DECLARED", "minimum_detectable_effect": 0.10, "baseline_scale": 1.0,
        "significance_level": 0.05, "desired_power": 0.80, "required_observations": 120,
        "method": "DECLARED_BY_PROTOCOL_OWNER", "assumptions": ["pre-outcome"],
    }


class W1FactoryEconomicIntegrationTests(unittest.TestCase):
    def run_package(self, package=None, *, frozen=None):
        return economic_test_readiness(package or fixture(), legacy=legacy(), frozen=frozen)

    def test_current_readiness_path_binds_registry_receipt_and_replay(self):
        result = self.run_package()
        self.assertEqual(result["status"], READY, result["block_reasons"])
        infrastructure = result["experiment_infrastructure"]
        self.assertEqual(infrastructure["status"], "PASS")
        self.assertEqual(infrastructure["registry"]["lifecycle"], "REPLAY_VERIFIED")
        self.assertEqual(infrastructure["geometry"]["status"], "UNKNOWN")
        self.assertEqual(infrastructure["power"]["status"], "UNKNOWN")
        self.assertIn("GEOMETRY_DECLARATION_UNKNOWN", infrastructure["declaration_gaps"])
        self.assertIn("POWER_DECLARATION_UNKNOWN", infrastructure["declaration_gaps"])
        self.assertEqual(result["validator"]["checks"]["experiment_infrastructure"]["status"], "PASS")
        self.assertFalse(infrastructure["outcome_accessed"])

    def test_public_contract_schema_tracks_real_attestation_shape(self):
        result = self.run_package()
        self.assertEqual(result["status"], READY, result["block_reasons"])
        infrastructure = result["experiment_infrastructure"]
        root = Path(__file__).resolve().parents[3]
        schema = json.loads((root / "research/research_os/contracts/experiment-infrastructure.schema.json").read_text())

        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(set(schema["properties"]), set(infrastructure))
        self.assertEqual(set(schema["required"]), set(infrastructure))

        definitions = schema["$defs"]
        for name in ("registry", "frozen_registry"):
            self.assertIs(definitions["registry"]["additionalProperties"], False)
            self.assertEqual(set(definitions["registry"]["properties"]), set(infrastructure[name]))
            self.assertEqual(set(definitions["registry"]["required"]), set(infrastructure[name]))

        for name in ("geometry", "power"):
            self.assertIs(definitions[name]["additionalProperties"], False)
            self.assertEqual(set(definitions[name]["properties"]), set(infrastructure[name]))
            self.assertEqual(set(definitions[name]["required"]), set(infrastructure[name]))
            self.assertEqual(len(infrastructure[name]["declaration_hash"]), 64)

        self.assertTrue(set(definitions["frozenProtocol"]["required"]).issubset(infrastructure["frozen_protocol"]))
        self.assertTrue(set(definitions["executionPlan"]["required"]).issubset(infrastructure["execution_plan"]))
        self.assertEqual(set(definitions["replay"]["properties"]), set(infrastructure["replay"]))
        self.assertEqual(set(definitions["replay"]["required"]), set(infrastructure["replay"]))
        receipt = infrastructure["execution_plan"]["pre_outcome_receipt"]
        self.assertEqual(set(definitions["preOutcomeReceipt"]["properties"]), set(receipt))
        self.assertEqual(set(definitions["preOutcomeReceipt"]["required"]), set(receipt))

    def test_declared_geometry_and_power_are_protocol_bound_without_empirical_claim(self):
        package = fixture()
        protocol = package["runner_meta"]["frozen_protocol"]
        _declare_geometry_and_power(protocol)
        protocol["geometry_declaration"]["assumptions"] = ["planned geometry; no outcomes inspected"]
        protocol["power_declaration"]["assumptions"] = ["planning declaration only; no empirical effect estimate"]
        result = self.run_package(package)
        self.assertEqual(result["status"], READY, result["block_reasons"])
        infrastructure = result["experiment_infrastructure"]
        self.assertEqual(infrastructure["declaration_gaps"], [])
        self.assertEqual(infrastructure["geometry"]["protocol_hash"], result["experiment_plan"]["plan"]["protocol_hash"])
        self.assertEqual(infrastructure["power"]["protocol_hash"], result["experiment_plan"]["plan"]["protocol_hash"])
        frozen_protocol = result["experiment_plan"]["frozen_protocol"]
        self.assertEqual(frozen_protocol["multiplicity_method"], protocol["multiplicity_method"])
        self.assertEqual(frozen_protocol["geometry_declaration"], protocol["geometry_declaration"])
        self.assertEqual(frozen_protocol["power_declaration"], protocol["power_declaration"])
        self.assertFalse(result["outcome_accessed"])

    def test_geometry_mutation_after_frozen_readiness_cannot_rebind(self):
        package = fixture()
        protocol = package["runner_meta"]["frozen_protocol"]
        _declare_geometry_and_power(protocol)
        frozen = self.run_package(package)
        mutated = deepcopy(package)
        mutated["runner_meta"]["frozen_protocol"]["geometry_declaration"]["target_observations"] = 121
        rebound = self.run_package(mutated, frozen=frozen)
        self.assertEqual(rebound["status"], "BLOCK")
        self.assertIn("PROTOCOL_BINDING_MISMATCH", rebound["block_reasons"])
        self.assertTrue(any("EXPERIMENT_INFRASTRUCTURE_BINDING_MISMATCH" in item for item in rebound["block_reasons"]))

    def test_power_and_multiplicity_mutation_hit_runner_protocol_binding(self):
        package = fixture()
        _declare_geometry_and_power(package["runner_meta"]["frozen_protocol"])
        frozen = self.run_package(package)
        mutations = (
            lambda p: p["runner_meta"]["frozen_protocol"]["power_declaration"].update(desired_power=0.85),
            lambda p: p["runner_meta"]["frozen_protocol"].update(multiplicity_method="changed after freeze"),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                rebound_package = deepcopy(package)
                mutate(rebound_package)
                rebound = self.run_package(rebound_package, frozen=frozen)
                self.assertEqual(rebound["status"], "BLOCK")
                self.assertIn("PROTOCOL_BINDING_MISMATCH", rebound["block_reasons"])

    def test_malformed_power_declaration_fails_closed(self):
        package = fixture()
        package["runner_meta"]["frozen_protocol"]["power_declaration"] = {
            "status": "DECLARED", "minimum_detectable_effect": True,
        }
        result = self.run_package(package)
        self.assertEqual(result["status"], "BLOCK")
        self.assertTrue(any("EXPERIMENT_INFRASTRUCTURE_INVALID" in item for item in result["block_reasons"]))


if __name__ == "__main__":
    unittest.main()
