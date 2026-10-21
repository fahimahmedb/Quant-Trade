from __future__ import annotations

from copy import deepcopy
import unittest

from research.research_os.scientific_store import sha256_json
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
    protocol_payload = {
        "hypothesis_id": candidate["hypothesis_id"],
        "generation_id": candidate["generation_id"],
        "candidate": candidate,
        "source_snapshot_hashes": source_hashes,
        "outcome_access": "CLOSED",
    }
    protocol_hash = sha256_json(protocol_payload)
    expression_spec = {
        "instrument_rule": "fixture-instrument",
        "side_rule": "fixture-side",
        "entry_rule": "fixture-entry",
        "exit_rule": "fixture-exit",
        "horizon_rule": "fixture-horizon",
        "sizing_rule": "fixture-size",
    }
    binding_payload = {
        "candidate_hash": candidate_hash,
        "protocol_hash": protocol_hash,
        "source_snapshot_hashes": source_hashes,
    }
    return {
        "candidate": candidate,
        "candidate_hash": candidate_hash,
        "producer_id": "candidate-producer.v1",
        "validator_id": "independent-validator.v3",
        "legacy_screening": {
            "status": "PASS",
            "evidence_hash": sha256_json({"legacy": "screened"}),
        },
        "sources": {
            "manifest_hash": sha256_json({"manifest": source_hashes}),
            "snapshot_hashes": source_hashes,
            "pit_metadata": [
                {
                    "source_id": "SRC-1",
                    "snapshot_hash": source_hashes[0],
                    "point_in_time_qualified": True,
                    "available_at": "2026-10-15T09:00:00+00:00",
                    "route_available_at": "2026-10-15T09:00:00+00:00",
                }
            ],
        },
        "clock": {
            "timezone": "UTC",
            "data_cutoff": "2026-10-15T10:00:00+00:00",
            "decision_time": "2026-10-15T10:30:00+00:00",
            "freeze_time": "2026-10-15T11:00:00+00:00",
        },
        "universe": {
            "status": "DEFINED",
            "universe_id": "U-1",
            "definition_hash": sha256_json({"universe": "fixture"}),
            "membership_policy": "point-in-time-membership",
        },
        "economic_expression": {
            "status": "COMPLETE",
            "spec": expression_spec,
            "expression_hash": sha256_json(expression_spec),
        },
        "implementability": {
            "status": "PASS",
            "declaration_hash": sha256_json({"implementability": "PASS"}),
        },
        "protocol": {
            "status": "FROZEN_READY_NO_OUTCOME",
            "protocol_hash": protocol_hash,
            "protocol_payload": protocol_payload,
            "candidate_hash": candidate_hash,
            "outcome_opened": False,
        },
        "reproducibility": {
            "status": "BOUND",
            "binding_payload": binding_payload,
            "binding_hash": sha256_json(binding_payload),
            "outcome_accessed": False,
        },
        "multiplicity": {
            "declared": True,
            "method": "all attempts counted before outcome access",
        },
        "trial_accounting": {
            "observed_attempt_count": 0,
            "effective_trials_status": "UNKNOWN",
            "estimated_effective_trials": None,
        },
        "cost_model": {
            "status": "DECLARED",
            "model_id": "COST-FIXTURE-V1",
            "declaration_hash": sha256_json({"cost_model": "fixture"}),
        },
        "capacity": {
            "status": "DECLARED",
            "model_id": "CAPACITY-FIXTURE-V1",
            "declaration_hash": sha256_json({"capacity": "fixture"}),
        },
        "outcome_access": {
            "opened": False,
            "consumed": False,
            "result": "NOT_OBSERVED",
        },
    }


class EconomicReadinessValidationTests(unittest.TestCase):
    def test_pass_when_every_precondition_is_present(self):
        receipt = validator_economic_readiness_v3(readiness_bundle=_fixture())
        self.assertEqual(receipt["status"], READY)
        self.assertTrue(receipt["ready_for_authorized_economic_test"])
        self.assertFalse(receipt["economic_test_authorized"])
        self.assertEqual(receipt["block_reasons"], [])
        red = red_team_negative_rights_v2(receipt)
        self.assertEqual(red["status"], "PASS")
        self.assertEqual(red["negative_rights"], [])

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

    def test_producer_must_differ_from_validator(self):
        fixture = _fixture()
        fixture["producer_id"] = fixture["validator_id"]
        receipt = validate_economic_test_readiness(fixture)
        self.assertEqual(receipt["checks"]["producer_independence"]["status"], "FAIL")
        self.assertEqual(
            receipt["checks"]["producer_independence"]["reason_code"],
            "PRODUCER_VALIDATOR_NOT_INDEPENDENT",
        )

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
