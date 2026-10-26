from __future__ import annotations

from copy import deepcopy
import unittest

from research.research_os.expansion.experiment_runner import (
    DryRunExperimentRunner,
    FrozenExperimentBindingError,
    NOT_OBSERVED,
    UNKNOWN,
)
from research.research_os.scientific_store import sha256_json


START_SHA = "b570973836e0e7daf50ca095a7559d63328f0a57"


def fixture():
    candidate = {
        "hypothesis_id": "HYP-001",
        "generation_id": "GEN-001",
        "claim": "bounded preregistered relation",
        "decision_map": {"pass": "RETAIN", "fail": "REJECT"},
    }
    protocol_payload = {
        "hypothesis_id": candidate["hypothesis_id"],
        "generation_id": candidate["generation_id"],
        "candidate": candidate,
        "declared_metrics": ["gross_return", "net_return"],
    }
    envelope = {
        "experiment_id": "EXP-HYP-001-GEN-001",
        "status": "FROZEN_READY_NO_OUTCOME",
        "protocol_hash": sha256_json(protocol_payload),
        "protocol_payload": protocol_payload,
        "outcome_opened": False,
        "result": NOT_OBSERVED,
    }
    qualifications = [{
        "status": "PASS",
        "outcome_accessed": False,
        "route_hash": "route-001",
        "snapshot_hash": "snapshot-001",
    }]
    frozen_protocol = {
        "universe": ["AAPL"],
        "clock": "NYSE_CLOSE_T",
        "entry_definition": {"when": "T+1_OPEN", "side": "LONG"},
        "exit_definition": {"when": "T+5_CLOSE"},
        "economic_expression": "close_to_close_return",
        "benchmark": "SPY",
        "gross_metric": "gross_return",
        "net_metric": "net_return_after_declared_costs",
        "cost_assumptions": {"commission_bps": 0.0, "slippage_bps": 5.0},
        "capacity_assumptions": {"max_adv_fraction": 0.01},
        "sample_definition": {"unit": "event", "eligibility": "predeclared"},
        "sample_window": {"start": "2020-01-01", "end": "2025-12-31"},
        "exclusions": ["missing_entry_price"],
        "missing_data_policy": "DROP_EVENT_NO_IMPUTATION",
        "revision_policy": "AS_OF_AVAILABLE_AT_ONLY",
        "survivorship_policy": "POINT_IN_TIME_UNIVERSE",
        "falsification_rule": {"metric": "net_return", "operator": "<=", "value": 0.0},
        "decision_map": {"pass": "RETAIN", "fail": "REJECT"},
        "observed_attempt_count": 0,
        "effective_trials": UNKNOWN,
        "multiplicity_family": "FAMILY-HYP-001",
    }
    runner_meta = {
        "dataset_manifest_hash": "manifest-001",
        "code_hash": "execution-code-001",
        "environment_hash": "environment-hash-001",
        "seed": 42,
        "declared_metrics": ["gross_return", "net_return"],
        "code_sha": START_SHA,
        "environment": "python-3.12-linux-x86_64",
        "dependency_fingerprint": "deps-001",
        "source_pit_metadata": [{
            "source_id": "prices",
            "available_at_rule": "exchange_published_timestamp",
            "revision_policy": "NONE",
        }],
        "frozen_protocol": frozen_protocol,
    }
    return envelope, qualifications, runner_meta


class FrozenExperimentProtocolTests(unittest.TestCase):
    def setUp(self):
        self.runner = DryRunExperimentRunner()
        self.envelope, self.qualifications, self.meta = fixture()

    def plan(self):
        return self.runner.plan(self.envelope, self.qualifications, self.meta)

    def test_deterministic_replay(self):
        first = self.plan()
        second = self.plan()
        self.assertEqual(first, second)
        self.assertEqual(first["execution_plan_hash"], second["execution_plan_hash"])
        self.assertEqual(self.runner.replay(first)["status"], "REPLAY_MATCH")
        self.assertEqual(
            self.runner.verify_bindings(first, self.envelope, self.qualifications, self.meta)["status"],
            "FROZEN_BINDINGS_MATCH",
        )

    def test_frozen_protocol_binds_complete_pre_outcome_package(self):
        plan = self.plan()
        frozen = plan["frozen_protocol"]
        for field in (
            "hypothesis_id", "generation_id", "candidate_hash", "protocol_hash",
            "source_snapshot_hashes", "source_pit_metadata", "universe", "clock",
            "entry_definition", "exit_definition", "economic_expression", "benchmark",
            "gross_metric", "net_metric", "cost_assumptions", "capacity_assumptions",
            "sample_definition", "sample_window", "exclusions", "missing_data_policy",
            "revision_policy", "survivorship_policy", "falsification_rule", "decision_map",
            "observed_attempt_count", "effective_trials", "multiplicity_family", "seed",
            "environment", "code_sha", "environment_hash", "dependency_fingerprint",
        ):
            self.assertIn(field, frozen)
        self.assertEqual(plan["frozen_protocol_capability"], "READY")
        self.assertEqual(plan["status"], "READY_FOR_REPRODUCIBLE_DRY_RUN")

    def test_candidate_mismatch_rejected(self):
        frozen = self.plan()
        envelope = deepcopy(self.envelope)
        envelope["protocol_payload"]["candidate"]["claim"] = "mutated claim"
        with self.assertRaisesRegex(FrozenExperimentBindingError, "CANDIDATE_BINDING_MISMATCH"):
            self.runner.verify_bindings(frozen, envelope, self.qualifications, self.meta)

    def test_protocol_mismatch_rejected(self):
        frozen = self.plan()
        meta = deepcopy(self.meta)
        meta["frozen_protocol"]["gross_metric"] = "different_metric"
        with self.assertRaisesRegex(FrozenExperimentBindingError, "PROTOCOL_BINDING_MISMATCH"):
            self.runner.verify_bindings(frozen, self.envelope, self.qualifications, meta)

    def test_source_mismatch_rejected(self):
        frozen = self.plan()
        qualifications = deepcopy(self.qualifications)
        qualifications[0]["snapshot_hash"] = "snapshot-CHANGED"
        with self.assertRaisesRegex(FrozenExperimentBindingError, "SOURCE_BINDING_MISMATCH"):
            self.runner.verify_bindings(frozen, self.envelope, qualifications, self.meta)

    def test_pit_mismatch_rejected(self):
        frozen = self.plan()
        meta = deepcopy(self.meta)
        meta["source_pit_metadata"][0]["available_at_rule"] = "CHANGED"
        with self.assertRaisesRegex(FrozenExperimentBindingError, "PIT_BINDING_MISMATCH"):
            self.runner.verify_bindings(frozen, self.envelope, self.qualifications, meta)

    def test_generation_mismatch_rejected(self):
        frozen = self.plan()
        envelope = deepcopy(self.envelope)
        envelope["protocol_payload"]["generation_id"] = "GEN-002"
        envelope["protocol_payload"]["candidate"]["generation_id"] = "GEN-002"
        with self.assertRaisesRegex(FrozenExperimentBindingError, "GENERATION_BINDING_MISMATCH"):
            self.runner.verify_bindings(frozen, envelope, self.qualifications, self.meta)

    def test_environment_and_code_binding(self):
        frozen = self.plan()
        for field, value in (
            ("code_sha", "different-code-sha"),
            ("code_hash", "different-execution-code"),
            ("environment", "different-environment"),
            ("environment_hash", "different-environment-hash"),
            ("dependency_fingerprint", "different-deps"),
        ):
            with self.subTest(field=field):
                meta = deepcopy(self.meta)
                meta[field] = value
                with self.assertRaisesRegex(FrozenExperimentBindingError, "CODE_ENVIRONMENT_BINDING_MISMATCH"):
                    self.runner.verify_bindings(frozen, self.envelope, self.qualifications, meta)

    def test_outcome_remains_closed_and_receipt_is_bounded(self):
        plan = self.plan()
        self.assertIs(plan["outcome_accessed"], False)
        self.assertEqual(plan["economic_result"], NOT_OBSERVED)
        receipt = plan["pre_outcome_receipt"]
        self.assertIs(receipt["outcome_accessed"], False)
        self.assertEqual(receipt["economic_result"], NOT_OBSERVED)
        for authority in (
            "economic_experiment_authorized", "prospective_observation_authorized",
            "real_capital_authorized", "live_trading_authorized",
        ):
            self.assertIs(receipt[authority], False)

    def test_effective_trials_unknown_preserved(self):
        plan = self.plan()
        self.assertEqual(plan["frozen_protocol"]["effective_trials"], UNKNOWN)

    def test_replay_rejects_frozen_protocol_mutation(self):
        plan = self.plan()
        plan["frozen_protocol"]["clock"] = "MUTATED"
        with self.assertRaisesRegex(ValueError, "frozen protocol mutation detected"):
            self.runner.replay(plan)

    def test_replay_rejects_receipt_mutation(self):
        plan = self.plan()
        plan["pre_outcome_receipt"]["economic_result"] = 1.0
        with self.assertRaises((ValueError, PermissionError)):
            self.runner.replay(plan)

    def test_legacy_plan_payload_remains_backward_compatible(self):
        meta = deepcopy(self.meta)
        del meta["frozen_protocol"]
        plan = self.runner.plan(self.envelope, self.qualifications, meta)
        self.assertNotIn("frozen_protocol_hash", plan["plan"])
        self.assertNotIn("binding_hashes", plan["plan"])
        self.assertEqual(plan["frozen_protocol_capability"], "LEGACY_DRY_RUN_ONLY")


if __name__ == "__main__":
    unittest.main()
