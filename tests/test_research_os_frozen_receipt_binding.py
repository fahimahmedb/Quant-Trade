"""A receipt must belong to the exact frozen plan and preserve closed authority."""
from copy import deepcopy
import unittest

from research.research_os.expansion.experiment_runner import DryRunExperimentRunner
from research.research_os.scientific_store import sha256_json
from research.research_os.tests.test_experiment_runner_frozen_protocol import fixture


class FrozenReceiptBindingTests(unittest.TestCase):
    def setUp(self):
        self.runner = DryRunExperimentRunner()
        self.envelope, self.sources, self.meta = fixture()
        self.plan = self.runner.plan(self.envelope, self.sources, self.meta)

    @staticmethod
    def rehash(receipt):
        receipt["receipt_hash"] = sha256_json({k:v for k,v in receipt.items() if k != "receipt_hash"})

    def test_foreign_receipt_cannot_replay_or_rebind(self):
        other_meta = deepcopy(self.meta)
        other_meta["seed"] += 1
        other = self.runner.plan(self.envelope, self.sources, other_meta)
        self.plan["pre_outcome_receipt"] = other["pre_outcome_receipt"]
        for action in (lambda: self.runner.replay(self.plan),
                       lambda: self.runner.verify_bindings(self.plan, self.envelope, self.sources, self.meta)):
            with self.assertRaisesRegex(ValueError, "RECEIPT_BINDING_MISMATCH"):
                action()

    def test_missing_receipt_and_rehashed_binding_changes_are_rejected(self):
        missing = deepcopy(self.plan)
        missing.pop("pre_outcome_receipt")
        with self.assertRaisesRegex(ValueError, "RECEIPT_REQUIRED"):
            self.runner.replay(missing)
        downgraded = deepcopy(missing)
        downgraded.pop("frozen_protocol")
        with self.assertRaisesRegex(ValueError, "FROZEN_PROTOCOL_REQUIRED"):
            self.runner.replay(downgraded)
        for key, value in (("experiment_id", "other"), ("execution_plan_hash", "a"*64),
                           ("frozen_protocol_hash", "b"*64), ("binding_hashes", {}),
                           ("receipt_version", "unknown"), ("status", "BLOCK")):
            with self.subTest(key=key):
                changed = deepcopy(self.plan)
                receipt = changed["pre_outcome_receipt"]
                receipt[key] = value
                self.rehash(receipt)
                with self.assertRaisesRegex(ValueError, "RECEIPT_BINDING_MISMATCH"):
                    self.runner.replay(changed)
        renamed = deepcopy(self.plan)
        renamed["experiment_id"] = "other"
        with self.assertRaisesRegex(ValueError, "EXPERIMENT_ID_BINDING_MISMATCH"):
            self.runner.replay(renamed)

    def test_receipt_authority_must_be_explicitly_false_without_affecting_legacy(self):
        for key in ("economic_experiment_authorized", "prospective_observation_authorized",
                    "real_capital_authorized", "live_trading_authorized"):
            for value in (True, None, "false", 0, "MISSING"):
                with self.subTest(key=key, value=value):
                    changed = deepcopy(self.plan)
                    receipt = changed["pre_outcome_receipt"]
                    if value == "MISSING":
                        del receipt[key]
                    else:
                        receipt[key] = value
                    self.rehash(receipt)
                    with self.assertRaisesRegex(PermissionError, "AUTHORITY_NOT_CLOSED"):
                        self.runner.replay(changed)
        self.assertEqual(self.runner.replay(self.plan)["status"], "REPLAY_MATCH")
        meta = deepcopy(self.meta)
        del meta["frozen_protocol"]
        legacy = self.runner.plan(self.envelope, self.sources, meta)
        self.assertEqual(self.runner.replay(legacy)["status"], "REPLAY_MATCH")


if __name__ == "__main__":
    unittest.main()
