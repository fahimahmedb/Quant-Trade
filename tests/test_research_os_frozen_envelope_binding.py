"""A frozen envelope must identify the same candidate and hashed protocol."""
from copy import deepcopy
import unittest

from research.research_os.expansion.experiment_runner import DryRunExperimentRunner, FrozenExperimentBindingError
from research.research_os.scientific_store import sha256_json
from research.research_os.tests.test_experiment_runner_frozen_protocol import fixture


class FrozenEnvelopeBindingTests(unittest.TestCase):
    def test_payload_edit_with_stale_protocol_hash_cannot_freeze(self):
        envelope, sources, meta = fixture()
        envelope["protocol_payload"]["candidate"]["claim"] = "changed after declared freeze"
        before = deepcopy(envelope)
        result = DryRunExperimentRunner().plan(envelope, sources, meta)
        self.assertEqual(result["status"], "BLOCK")
        self.assertIn("FROZEN_PROTOCOL_HASH_MISMATCH", result["blockers"])
        self.assertEqual(envelope, before)

    def test_rehashed_payload_still_requires_matching_hypothesis_and_generation(self):
        for key, code in (("hypothesis_id", "HYPOTHESIS"), ("generation_id", "GENERATION")):
            with self.subTest(field=key):
                envelope, sources, meta = fixture()
                envelope["protocol_payload"]["candidate"][key] = "different"
                envelope["protocol_hash"] = sha256_json(envelope["protocol_payload"])
                result = DryRunExperimentRunner().plan(envelope, sources, meta)
                self.assertEqual(result["status"], "BLOCK")
                self.assertIn("FROZEN_PROTOCOL_" + code + "_BINDING_MISMATCH", result["blockers"])

    def test_valid_frozen_and_opaque_legacy_envelopes_keep_their_ceilings(self):
        runner = DryRunExperimentRunner()
        envelope, sources, meta = fixture()
        result = runner.plan(envelope, sources, meta)
        self.assertEqual(result["status"], "READY_FOR_REPRODUCIBLE_DRY_RUN")
        self.assertEqual(runner.verify_bindings(result, envelope, sources, meta)["status"],
                         "FROZEN_BINDINGS_MATCH")
        for malformed in (None, [], ["invalid"], "not-a-payload"):
            changed = deepcopy(envelope)
            changed["protocol_payload"] = malformed
            with self.subTest(payload=malformed), self.assertRaises(FrozenExperimentBindingError):
                runner.verify_bindings(result, changed, sources, meta)
        del meta["frozen_protocol"]
        envelope.pop("protocol_payload")
        envelope["protocol_hash"] = "legacy-opaque-reference"
        legacy = runner.plan(envelope, sources, meta)
        self.assertEqual(legacy["frozen_protocol_capability"], "LEGACY_DRY_RUN_ONLY")
        self.assertEqual(runner.replay(legacy)["status"], "REPLAY_MATCH")
        self.assertFalse(legacy["outcome_access_authorized"])


if __name__ == "__main__":
    unittest.main()
