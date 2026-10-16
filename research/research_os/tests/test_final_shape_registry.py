from __future__ import annotations

import json
import unittest
from pathlib import Path

from research.research_os.expansion.final_shape import run_aggressive_pipeline


class FinalShapeRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Path(__file__).resolve().parents[1]
        cls.registry = json.loads((cls.base / "architecture" / "FINAL_SHAPE_MODULE_REGISTRY.json").read_text())
        cls.schema = json.loads((cls.base / "contracts" / "expansion-auxiliary.schema.json").read_text())
        fixture = json.loads((cls.base / "simulations" / "aggressive_architecture_fixture.json").read_text())
        cls.result = run_aggressive_pipeline(fixture)

    def test_common_contracts_are_stable(self):
        contracts = self.registry["canonical_shared_contracts"]
        self.assertEqual(contracts["status"], "STABLE_DO_NOT_REDEFINE")
        self.assertEqual(contracts["contracts"], [
            "HypothesisContract",
            "ResearchTask",
            "ExperimentResult",
            "EvidenceAssessment",
            "CandidateEconomicIdentity",
            "WorkerEvent",
        ])
        self.assertEqual(contracts["execution_companion"], "WorkerReceipt")

    def test_full_chain_is_registered(self):
        ids = {m["module_id"] for m in self.registry["modules"]}
        self.assertTrue({
            "canonical_core", "control_plane", "quant_mechanisms", "event_document",
            "fundamental", "institutional_flows", "edge_archaeology",
            "early_implementability", "experiment_infrastructure",
            "independent_validator", "red_team", "economic_identity",
            "portfolio_map", "forward_farm", "decay_monitoring",
            "learning_telemetry", "live_lab_bridge",
        }.issubset(ids))

    def test_authority_is_closed(self):
        self.assertTrue(all(v is False for v in self.registry["global_authority"].values()))
        self.assertTrue(all(v is False for v in self.result["authority"].values()))

    def test_auxiliary_schema_does_not_redefine_common_contracts(self):
        self.assertEqual(set(self.schema["$defs"]), {
            "ImplementabilityAssessment",
            "ExperimentEnvelope",
            "ForwardRegistration",
            "DecayAssessment",
        })
        description = self.schema["description"]
        for name in (
            "HypothesisContract", "ResearchTask", "ExperimentResult",
            "EvidenceAssessment", "CandidateEconomicIdentity", "WorkerEvent", "WorkerReceipt",
        ):
            self.assertIn(name, description)

    def test_produced_auxiliary_records_match_required_shapes(self):
        impl_required = set(self.schema["$defs"]["ImplementabilityAssessment"]["required"])
        env_required = set(self.schema["$defs"]["ExperimentEnvelope"]["required"])
        fwd_required = set(self.schema["$defs"]["ForwardRegistration"]["required"])
        decay_required = set(self.schema["$defs"]["DecayAssessment"]["required"])
        self.assertTrue(all(impl_required <= set(x) for x in self.result["implementability"]))
        self.assertTrue(all(env_required <= set(x) for x in self.result["experiment_envelopes"]))
        self.assertTrue(all(fwd_required <= set(x) for x in self.result["forward_farm"]))
        self.assertTrue(decay_required <= set(self.result["decay"]))

    def test_intentionally_inactive_layers_are_explicit(self):
        modules = {m["module_id"]: m for m in self.registry["modules"]}
        self.assertEqual(modules["forward_farm"]["status"], "READINESS_ONLY_AUTHORITY_OFF")
        self.assertEqual(modules["decay_monitoring"]["status"], "INACTIVE_BY_AUTHORITY")
        self.assertEqual(modules["portfolio_map"]["status"], "ACTIVE_THIN_NO_CAPITAL")
        self.assertEqual(modules["experiment_infrastructure"]["status"], "ACTIVE_THIN_NO_OUTCOME")


if __name__ == "__main__":
    unittest.main()
