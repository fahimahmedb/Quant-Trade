from __future__ import annotations

from copy import deepcopy
import unittest

from research.research_os.scientific_store import sha256_json
from research.research_os.expansion.experiment_infrastructure import bind_pre_outcome_infrastructure
from research.research_os.expansion.experiment_runner import DryRunExperimentRunner
from research.research_os.expansion.validation_readiness import (
    BLOCK,
    READY,
    validate_economic_test_readiness,
)
from research.research_os.expansion.validation_v2 import validator_economic_readiness_v3
from research.research_os.expansion.red_team_v2 import red_team_negative_rights_v2


def _fixture() -> dict:
    candidate = {
        "hypothesis_id": "H-ECON-READY-001",
        "generation_id": "G1",
        "mechanism": "pre-outcome fixture only",
        "claim": "future testable claim",
        "falsification_scope": ["reject if preregistered decision map says reject"],
        "decision_map": {"reject": "metric_below_floor", "continue": "metric_above_floor"},
    }
    candidate_hash = sha256_json(candidate)
    source_hashes = [sha256_json({"snapshot": "S1"})]
    expression_spec = {
        "instrument_rule": "fixture-instrument",
        "side_rule": "fixture-side",
        "entry_rule": "fixture-entry",
        "exit_rule": "fixture-exit",
        "horizon_rule": "fixture-horizon",
        "sizing_rule": "fixture-size",
    }
    expression = dict(zip(
        ("instrument", "direction_exposure_semantics", "entry_clock", "exit_clock", "horizon", "position_expression"),
        expression_spec.values(),
    ), universe="U-1")
    clock = {
        "timezone": "UTC",
        "data_cutoff": "2026-10-15T10:00:00+00:00",
        "decision_time": "2026-10-15T10:30:00+00:00",
        "freeze_time": "2026-10-15T11:00:00+00:00",
    }
    universe = {
        "status": "DEFINED",
        "universe_id": "U-1",
        "definition_hash": sha256_json({"universe": "fixture"}),
        "membership_policy": "point-in-time-membership",
    }
    costs = {
        "model_id": "COST-FIXTURE-V1",
        "fees_bps": 0,
        "spread_bps": 1,
        "slippage_bps": 2,
        "financing_bps": 0,
        "borrow_bps": 0,
    }
    capacity = {
        "model_id": "CAPACITY-FIXTURE-V1",
        "max_adv_fraction": .01,
        "evidence_ref": "fixture://declared-liquidity",
    }
    multiplicity_method = "all attempts counted before outcome access"
    declared = {
        "universe": deepcopy(universe),
        "clock": deepcopy(clock),
        "entry_definition": expression["entry_clock"],
        "exit_definition": expression["exit_clock"],
        "economic_expression": expression,
        "benchmark": "fixture-benchmark",
        "gross_metric": "gross",
        "net_metric": "net",
        "cost_assumptions": costs,
        "capacity_assumptions": capacity,
        "sample_definition": {"unit": "event"},
        "sample_window": {"start": "2020-01-01", "end": "2025-12-31"},
        "exclusions": [],
        "missing_data_policy": "NO_IMPUTATION",
        "revision_policy": "POINT_IN_TIME_ONLY",
        "survivorship_policy": "POINT_IN_TIME_UNIVERSE",
        "falsification_rule": candidate["falsification_scope"],
        "decision_map": candidate["decision_map"],
        "observed_attempt_count": 0,
        "effective_trials": "UNKNOWN",
        "multiplicity_family": "FAMILY-FIXTURE",
        "multiplicity_method": multiplicity_method,
    }
    sources = [{
        "snapshot_hash": source_hashes[0],
        "available_at": "2026-10-15T09:00:00+00:00",
        "route": {
            "route_id": "SRC-1",
            "source_class": "SYNTHETIC_FIXTURE",
            "transport": "MEMORY",
            "locator": "fixture://metadata",
            "permission_state": "FIXTURE_ONLY",
            "pit_mode": "VERSIONED_SNAPSHOT",
            "revision_policy": "IMMUTABLE",
            "survivorship_policy": "PIT_MEMBERSHIP",
            "timezone": "UTC",
            "availability_start": "2026-10-15T09:00:00+00:00",
            "contains_outcome": False,
        },
    }]
    implementation = {"status": "PASS", "basis": "SYNTHETIC_METADATA_ONLY"}
    protocol_payload = {
        "hypothesis_id": candidate["hypothesis_id"],
        "generation_id": candidate["generation_id"],
        "candidate": candidate,
        "source_snapshot_hashes": source_hashes,
        "outcome_access": "CLOSED",
        "dataset_provenance": {"sources": sources, "protocol": declared},
        "implementability_declaration": implementation,
        "declared_decision_map": candidate["decision_map"],
    }
    protocol_hash = sha256_json(protocol_payload)
    envelope = {
        "experiment_id": "EXP-H-ECON-READY-001-G1",
        "status": "FROZEN_READY_NO_OUTCOME",
        "protocol_hash": protocol_hash,
        "protocol_payload": protocol_payload,
        "candidate_hash": candidate_hash,
        "outcome_opened": False,
        "result": "NOT_OBSERVED",
    }
    pit = [{
        "source_id": "SRC-1",
        "snapshot_hash": source_hashes[0],
        "point_in_time_qualified": True,
        "available_at": "2026-10-15T09:00:00+00:00",
        "route_available_at": "2026-10-15T09:00:00+00:00",
        "revision_policy": "IMMUTABLE",
    }]
    qualifications = [{
        "status": "PASS",
        "outcome_accessed": False,
        "route_hash": sha256_json({"route": "SRC-1"}),
        "snapshot_hash": source_hashes[0],
    }]
    runner_meta = {
        "dataset_manifest_hash": sha256_json(sources),
        "code_hash": sha256_json({"code": "fixture"}),
        "environment_hash": sha256_json({"environment": "fixture"}),
        "seed": 7,
        "declared_metrics": ["gross", "net"],
        "code_sha": "fixture-code-sha",
        "environment": "fixture-python",
        "dependency_fingerprint": sha256_json({"deps": "fixture"}),
        "source_pit_metadata": pit,
        "frozen_protocol": declared,
    }
    runner = DryRunExperimentRunner()
    plan = runner.plan(envelope, qualifications, runner_meta)
    assert plan["status"] == "READY_FOR_REPRODUCIBLE_DRY_RUN", plan["blockers"]
    replay = runner.replay(plan)
    trial_accounting = {
        "hypothesis_id": candidate["hypothesis_id"],
        "generation_id": candidate["generation_id"],
        "observed_attempt_count": 0,
        "effective_trials_status": "UNKNOWN",
        "estimated_effective_trials": None,
    }
    infrastructure = bind_pre_outcome_infrastructure(
        envelope=envelope,
        plan=plan,
        replay=replay,
        trial_accounting=trial_accounting,
    )
    binding_payload = {
        "candidate_hash": candidate_hash,
        "protocol_hash": protocol_hash,
        "source_snapshot_hashes": source_hashes,
        "execution_plan_hash": plan["execution_plan_hash"],
        "experiment_registry_id": infrastructure["registry"]["registry_id"],
        "experiment_registry_hash": infrastructure["registry"]["entry_hash"],
        "experiment_infrastructure_hash": infrastructure["infrastructure_hash"],
    }
    bundle = {
        "candidate": candidate,
        "candidate_hash": candidate_hash,
        "producer_id": "candidate-producer.v1",
        "validator_id": "independent-validator.v3",
        "legacy_screening": {
            "status": "PASS",
            "evidence_hash": sha256_json({"legacy": "screened"}),
        },
        "sources": {
            "manifest_hash": sha256_json(sources),
            "snapshot_hashes": source_hashes,
            "pit_metadata": pit,
        },
        "clock": clock,
        "universe": universe,
        "economic_expression": {
            "status": "COMPLETE",
            "spec": expression_spec,
            "expression_hash": sha256_json(expression_spec),
        },
        "implementability": {
            "status": "PASS",
            "declaration_hash": sha256_json(implementation),
        },
        "protocol": envelope,
        "reproducibility": {
            "status": "BOUND",
            "binding_payload": binding_payload,
            "binding_hash": sha256_json(binding_payload),
            "outcome_accessed": False,
        },
        "experiment_infrastructure": infrastructure,
        "multiplicity": {
            "declared": True,
            "method": multiplicity_method,
        },
        "trial_accounting": trial_accounting,
        "cost_model": {
            "status": "DECLARED",
            "model_id": costs["model_id"],
            "declaration_hash": sha256_json(costs),
        },
        "capacity": {
            "status": "DECLARED",
            "model_id": capacity["model_id"],
            "declaration_hash": sha256_json(capacity),
        },
        "outcome_access": {
            "opened": False,
            "consumed": False,
            "result": "NOT_OBSERVED",
        },
    }
    return bundle


def _rehash_infrastructure(fixture: dict) -> None:
    infrastructure = fixture["experiment_infrastructure"]
    for key in ("registry", "frozen_registry"):
        record = infrastructure[key]
        record["entry_hash"] = sha256_json({k: v for k, v in record.items() if k != "entry_hash"})
    infrastructure["infrastructure_hash"] = sha256_json(
        {k: v for k, v in infrastructure.items() if k != "infrastructure_hash"}
    )
    binding = fixture["reproducibility"]["binding_payload"]
    binding["experiment_registry_id"] = infrastructure["registry"]["registry_id"]
    binding["experiment_registry_hash"] = infrastructure["registry"]["entry_hash"]
    binding["experiment_infrastructure_hash"] = infrastructure["infrastructure_hash"]
    fixture["reproducibility"]["binding_hash"] = sha256_json(binding)


class EconomicReadinessValidationTests(unittest.TestCase):
    def test_pass_when_every_precondition_is_present(self):
        receipt = validator_economic_readiness_v3(readiness_bundle=_fixture())
        self.assertEqual(receipt["status"], READY)
        self.assertTrue(receipt["ready_for_authorized_economic_test"])
        self.assertFalse(receipt["economic_test_authorized"])
        self.assertEqual(receipt["block_reasons"], [])
        self.assertEqual(receipt["checks"]["frozen_input_binding"]["status"], "PASS")
        self.assertEqual(receipt["checks"]["experiment_infrastructure"]["status"], "PASS")
        self.assertEqual(receipt["checks"]["outcome_firewall"]["status"], "PASS")
        red = red_team_negative_rights_v2(receipt)
        self.assertEqual(red["status"], "PASS")
        self.assertEqual(red["negative_rights"], [])

    def test_block_on_missing_or_foreign_experiment_infrastructure(self):
        fixture = _fixture()
        del fixture["experiment_infrastructure"]
        receipt = validate_economic_test_readiness(fixture)
        self.assertEqual(
            receipt["checks"]["experiment_infrastructure"]["reason_code"],
            "EXPERIMENT_INFRASTRUCTURE_NOT_QUALIFIED",
        )

        fixture = _fixture()
        foreign_hash = sha256_json({"candidate": "foreign-but-self-consistent"})
        fixture["experiment_infrastructure"]["registry"]["candidate_hash"] = foreign_hash
        fixture["experiment_infrastructure"]["frozen_registry"]["candidate_hash"] = foreign_hash
        _rehash_infrastructure(fixture)
        receipt = validate_economic_test_readiness(fixture)
        self.assertEqual(receipt["checks"]["experiment_infrastructure"]["status"], "FAIL")

    def test_block_on_self_consistent_geometry_forgery_not_present_in_runner_freeze(self):
        fixture = _fixture()
        infrastructure = fixture["experiment_infrastructure"]
        geometry = {
            "protocol_hash": fixture["protocol"]["protocol_hash"],
            "status": "DECLARED",
            "observation_unit": "event",
            "target_observations": 999,
            "dependence_assumption": "forged after runner freeze",
            "cluster_key": None,
            "max_cluster_share": None,
            "sampling_rule": "forged",
            "assumptions": ["self-consistent hash but absent from frozen protocol"],
        }
        geometry["declaration_hash"] = sha256_json(geometry)
        infrastructure["geometry"] = geometry
        infrastructure["registry"]["geometry_hash"] = geometry["declaration_hash"]
        infrastructure["frozen_registry"]["geometry_hash"] = geometry["declaration_hash"]
        _rehash_infrastructure(fixture)
        receipt = validate_economic_test_readiness(fixture)
        self.assertEqual(receipt["checks"]["experiment_infrastructure"]["status"], "FAIL")

    def test_block_on_multiplicity_method_drift_from_runner_freeze(self):
        fixture = _fixture()
        fixture["multiplicity"]["method"] = "different method after freeze"
        receipt = validate_economic_test_readiness(fixture)
        self.assertEqual(receipt["checks"]["experiment_infrastructure"]["status"], "FAIL")

    def test_block_when_embedded_runner_plan_is_tampered_even_if_outer_hashes_are_rebuilt(self):
        fixture = _fixture()
        plan = fixture["experiment_infrastructure"]["execution_plan"]
        plan["plan"]["seed"] = 999
        _rehash_infrastructure(fixture)
        receipt = validate_economic_test_readiness(fixture)
        self.assertEqual(receipt["checks"]["experiment_infrastructure"]["status"], "FAIL")

    def test_block_on_missing_protocol_freeze(self):
        fixture = _fixture()
        fixture["protocol"]["status"] = "NOT_FROZEN"
        receipt = validate_economic_test_readiness(fixture)
        self.assertEqual(receipt["status"], BLOCK)
        self.assertEqual(receipt["checks"]["protocol_freeze"]["reason_code"], "PROTOCOL_NOT_FROZEN")
        self.assertIn("BLOCK_REPRODUCIBILITY", red_team_negative_rights_v2(receipt)["negative_rights"])

    def test_block_on_missing_implementability(self):
        fixture = _fixture()
        fixture["implementability"]["status"] = "BLOCK"
        receipt = validate_economic_test_readiness(fixture)
        self.assertEqual(receipt["checks"]["implementability_declaration"]["status"], "FAIL")
        self.assertIn("BLOCK_IMPLEMENTABILITY", red_team_negative_rights_v2(receipt)["negative_rights"])

    def test_block_on_missing_multiplicity(self):
        fixture = _fixture()
        fixture["multiplicity"]["declared"] = False
        receipt = validate_economic_test_readiness(fixture)
        self.assertEqual(receipt["checks"]["multiplicity_declaration"]["status"], "FAIL")
        self.assertIn("BLOCK_MULTIPLICITY", red_team_negative_rights_v2(receipt)["negative_rights"])

    def test_block_on_missing_cost_or_capacity_declaration(self):
        for field, expected in (("cost_model", "BLOCK_COST_MODEL"), ("capacity", "BLOCK_CAPACITY")):
            with self.subTest(field=field):
                fixture = _fixture()
                fixture[field]["status"] = "UNKNOWN"
                receipt = validate_economic_test_readiness(fixture)
                self.assertEqual(receipt["status"], BLOCK)
                self.assertIn(expected, red_team_negative_rights_v2(receipt)["negative_rights"])

    def test_block_on_pit_or_source_failure(self):
        fixture = _fixture()
        fixture["sources"]["pit_metadata"][0]["point_in_time_qualified"] = False
        receipt = validate_economic_test_readiness(fixture)
        self.assertEqual(receipt["checks"]["pit"]["status"], "FAIL")
        self.assertIn("BLOCK_PIT", red_team_negative_rights_v2(receipt)["negative_rights"])

        fixture = _fixture()
        fixture["sources"]["manifest_hash"] = "bad"
        receipt = validate_economic_test_readiness(fixture)
        self.assertEqual(receipt["checks"]["source_provenance"]["status"], "FAIL")
        self.assertIn("BLOCK_DATA", red_team_negative_rights_v2(receipt)["negative_rights"])

    def test_pit_requires_exact_snapshot_join(self):
        fixture = _fixture()
        fixture["sources"]["pit_metadata"][0]["snapshot_hash"] = sha256_json({"snapshot": "OTHER"})
        receipt = validate_economic_test_readiness(fixture)
        self.assertEqual(receipt["checks"]["source_provenance"]["status"], "FAIL")
        self.assertEqual(receipt["checks"]["pit"]["status"], "FAIL")

    def test_clock_rejects_information_after_decision(self):
        fixture = _fixture()
        fixture["clock"]["data_cutoff"] = "2026-10-15T10:45:00+00:00"
        receipt = validate_economic_test_readiness(fixture)
        self.assertEqual(receipt["checks"]["clock"]["status"], "FAIL")

    def test_frozen_input_binding_rejects_mutable_projection_drift(self):
        fixture = _fixture()
        fixture["clock"]["timezone"] = "Europe/Paris"
        receipt = validate_economic_test_readiness(fixture)
        self.assertEqual(receipt["checks"]["frozen_input_binding"]["status"], "FAIL")

    def test_producer_must_differ_from_validator(self):
        fixture = _fixture()
        fixture["producer_id"] = fixture["validator_id"]
        receipt = validate_economic_test_readiness(fixture)
        self.assertEqual(receipt["checks"]["producer_independence"]["status"], "FAIL")
        self.assertEqual(
            receipt["checks"]["producer_independence"]["reason_code"],
            "PRODUCER_VALIDATOR_NOT_INDEPENDENT",
        )

    def test_placeholder_validator_identity_is_not_independent(self):
        fixture = _fixture()
        fixture["validator_id"] = "UNRESOLVED"
        receipt = validate_economic_test_readiness(fixture)
        self.assertEqual(receipt["checks"]["producer_independence"]["status"], "FAIL")

    def test_candidate_immutability_and_no_signal_repair(self):
        fixture = _fixture()
        before = deepcopy(fixture["candidate"])
        receipt = validate_economic_test_readiness(fixture)
        self.assertEqual(fixture["candidate"], before)
        self.assertFalse(receipt["candidate_mutated"])

        tampered = _fixture()
        tampered["candidate"]["claim"] = "changed after freeze"
        receipt = validate_economic_test_readiness(tampered)
        self.assertEqual(receipt["checks"]["candidate_immutability"]["status"], "FAIL")

        receipt_before = deepcopy(receipt)
        red = red_team_negative_rights_v2(receipt)
        self.assertEqual(receipt, receipt_before)
        self.assertFalse(red["repair_attempted"])
        self.assertFalse(red["signal_repair_attempted"])
        self.assertFalse(red["parameters_optimized"])
        self.assertFalse(red["retuned_until_profitable"])

    def test_no_outcome_access(self):
        fixture = _fixture()
        fixture["outcome_access"]["opened"] = True
        receipt = validate_economic_test_readiness(fixture)
        self.assertEqual(receipt["checks"]["no_outcome_access"]["status"], "FAIL")
        red = red_team_negative_rights_v2(receipt)
        self.assertIn("BLOCK_LEAKAGE", red["negative_rights"])
        self.assertFalse(red["outcomes_opened"])


if __name__ == "__main__":
    unittest.main()
