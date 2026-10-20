"""Freeze must reject invalid multiplicity before downstream validation."""
import unittest
from unittest.mock import patch

from research.research_os.expansion.experiment_runner import DryRunExperimentRunner
from research.research_os.tests.test_experiment_runner_frozen_protocol import fixture


class FrozenTrialAccountingTests(unittest.TestCase):
    def test_legacy_hash_valid_nonfinite_plan_cannot_replay_or_rebind(self):
        runner = DryRunExperimentRunner()
        for value in (float("nan"), float("inf")):
            with self.subTest(value=value):
                envelope, sources, meta = fixture()
                meta["frozen_protocol"]["effective_trials"] = value
                # Reproduce the former acceptance without corrupting any hash:
                # integrity alone must not make an invalid old freeze admissible.
                with patch("research.research_os.expansion.experiment_runner._valid_effective_trials",
                           return_value=True):
                    legacy_plan = runner.plan(envelope, sources, meta)
                for action in (lambda: runner.replay(legacy_plan),
                               lambda: runner.verify_bindings(legacy_plan, envelope, sources, meta)):
                    with self.assertRaisesRegex(ValueError, "FROZEN_PROTOCOL_EFFECTIVE_TRIALS_INVALID"):
                        action()

    def test_nonfinite_or_invalid_estimates_cannot_freeze(self):
        for value in (float("nan"), float("inf"), -float("inf"), True, False, -1, "infinite", None):
            with self.subTest(value=value):
                envelope, sources, meta = fixture()
                meta["frozen_protocol"]["effective_trials"] = value
                plan = DryRunExperimentRunner().plan(envelope, sources, meta)
                self.assertEqual(plan["status"], "BLOCK")
                self.assertNotEqual(plan["frozen_protocol_capability"], "READY")
                self.assertIn("FROZEN_PROTOCOL_EFFECTIVE_TRIALS_INVALID", plan["blockers"])
                self.assertFalse(plan["outcome_accessed"])

    def test_unknown_and_finite_estimates_preserve_freeze_and_rebinding(self):
        runner = DryRunExperimentRunner()
        for value in ("UNKNOWN", 0, 1, 2.5, 10**400):
            with self.subTest(value=value):
                envelope, sources, meta = fixture()
                meta["frozen_protocol"]["effective_trials"] = value
                plan = runner.plan(envelope, sources, meta)
                self.assertEqual(plan["status"], "READY_FOR_REPRODUCIBLE_DRY_RUN")
                self.assertEqual(plan["frozen_protocol"]["effective_trials"], value)
                self.assertEqual(runner.replay(plan)["status"], "REPLAY_MATCH")
                self.assertEqual(runner.verify_bindings(plan, envelope, sources, meta)["status"],
                                 "FROZEN_BINDINGS_MATCH")


if __name__ == "__main__":
    unittest.main()
