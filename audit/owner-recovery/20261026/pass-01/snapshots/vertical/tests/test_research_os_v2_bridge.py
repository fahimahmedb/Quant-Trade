import unittest

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext
from research.research_os.expansion.v2_bridge import (
    adapt_engine_output_to_v2_candidate,
    adapt_existing_validation_to_v2,
)
from research.research_os.expansion.v2_core import V2ContractError


class V2BridgeTests(unittest.TestCase):
    def synthetic_output(self, key):
        return ENGINE_REGISTRY[key].run(
            {"source_ref": f"synthetic://{key}"},
            EngineContext(f"RUN-{key}", synthetic_only=True),
        )

    def adapt(self, key):
        return adapt_engine_output_to_v2_candidate(
            self.synthetic_output(key),
            research_trial_id=f"TRIAL-{key}",
            research_epoch_id="E1",
            producer_identity={"engine_key": key, "worker": "producer"},
            disconfirmation_manifest={"attempted": True, "status": "NO_BLOCKER_FOUND"},
        )

    def test_all_existing_primary_engines_bridge_to_v2(self):
        expected = {
            "fundamental": ("fundamental", "FundamentalExtension"),
            "event_document": ("event", "EventExtension"),
            "institutional_flow": ("forced_flow", "ForcedFlowExtension"),
            "quant": ("quant", "QuantExtension"),
        }
        for key, (family, extension) in expected.items():
            with self.subTest(engine=key):
                candidate = self.adapt(key)
                self.assertEqual(candidate["family"], family)
                self.assertEqual(candidate["extension"]["type"], extension)
                self.assertEqual(candidate["research_epoch_id"], "E1")
                self.assertEqual(len(candidate["candidate_hash"]), 64)

    def test_non_forced_flow_families_do_not_receive_fake_forced_actor(self):
        fundamental = self.adapt("fundamental")
        event = self.adapt("event_document")
        quant = self.adapt("quant")
        for candidate in (fundamental, event, quant):
            self.assertNotIn("forced_constrained_actor", candidate["extension"])
            self.assertNotIn("binding_constraint", candidate["extension"])

    def test_synthetic_bridge_keeps_unknowns_explicit(self):
        event = self.adapt("event_document")
        self.assertEqual(event["extension"]["availability_time"], "UNKNOWN")
        self.assertEqual(event["extension"]["reaction_channel"], "UNRESOLVED")
        self.assertEqual(event["economic_expression"]["direction"], "NOT_YET_MEASURABLE")

    def test_existing_validator_pass_maps_to_v2_complete_pass(self):
        candidate = self.adapt("fundamental")
        result = adapt_existing_validation_to_v2(
            v2_candidate=candidate,
            existing_validation={"status": "PASS", "failures": []},
            validator_identity="independent-validator.v2",
            validator_version="2",
            validator_model="gpt-oss-10.2b-q4-k-m",
            validator_prompt_hash="p" * 64,
            validator_context_hash="c" * 64,
            validator_retrieval_manifest_hash="r" * 64,
            producer_identity_hash="a" * 64,
            validator_state_identity_hash="b" * 64,
            independence_evidence=dict.fromkeys(("information_isolation", "retrieval_independence", "cognitive_independence", "state_isolation"), True),
        )
        self.assertEqual(result["execution_state"], "COMPLETE")
        self.assertEqual(result["scientific_decision"], "PASS")
        self.assertEqual(result["epistemic_blockers"], [])

    def test_existing_validator_block_preserves_blockers(self):
        candidate = self.adapt("fundamental")
        result = adapt_existing_validation_to_v2(
            v2_candidate=candidate,
            existing_validation={"status": "BLOCK", "failures": ["PIT_UNRESOLVED"]},
            validator_identity="independent-validator.v2",
            validator_version="2",
            validator_model="gpt-oss-10.2b-q4-k-m",
            validator_prompt_hash="p" * 64,
            validator_context_hash="c" * 64,
            validator_retrieval_manifest_hash="r" * 64,
            producer_identity_hash="a" * 64,
            validator_state_identity_hash="b" * 64,
        )
        self.assertEqual(result["scientific_decision"], "BLOCK")
        self.assertIn("PIT_UNRESOLVED", result["epistemic_blockers"])
        self.assertIn("VALIDATOR_FOUR_AXIS_INDEPENDENCE_NOT_PROVEN", result["epistemic_blockers"])

    def test_validator_state_isolation_is_not_name_only(self):
        candidate = self.adapt("fundamental")
        with self.assertRaisesRegex(V2ContractError, "STATE_ISOLATION_NOT_PROVEN"):
            adapt_existing_validation_to_v2(
                v2_candidate=candidate,
                existing_validation={"status": "PASS", "failures": []},
                validator_identity="different-name",
                validator_version="2",
                validator_model="gpt-oss",
                validator_prompt_hash="p",
                validator_context_hash="c",
                validator_retrieval_manifest_hash="r",
                producer_identity_hash="same",
                validator_state_identity_hash="same",
            )


if __name__ == "__main__":
    unittest.main()
