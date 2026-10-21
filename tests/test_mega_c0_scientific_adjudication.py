from __future__ import annotations

from copy import deepcopy
import unittest

from research.research_os.scientific_store import sha256_json
from research.research_os.expansion.scientific_adjudication import (
    AUTHORITY_STATE,
    ScientificAdjudicationError,
    adjudicate_scientific_candidate,
    authority_state,
    bind_factory_ref,
    bind_independence_ref,
    bind_qualified_negative_ref,
    bind_red_team_ref,
    bind_validator_ref,
    build_cross_examination_ref,
    validate_adjudication,
    validate_cross_examination_ref,
    validate_factory_ref,
    validate_independence_ref,
    validate_qualified_negative_ref,
    validate_red_team_ref,
    validate_validator_ref,
)


def candidate(hypothesis="H-C0-001", generation="G1", mechanism="bounded-mechanism"):
    return {
        "hypothesis_id": hypothesis,
        "generation_id": generation,
        "mechanism": mechanism,
        "falsification_scope": ["clock mismatch", "source contradiction"],
        "decision_map": {"pass": "continue", "fail": "stop"},
    }


def infrastructure(c, protocol_label="P1"):
    candidate_hash = sha256_json(c)
    protocol_hash = sha256_json({"protocol": protocol_label, "candidate_hash": candidate_hash})
    frozen_protocol = {
        "candidate_hash": candidate_hash,
        "protocol_hash": protocol_hash,
        "protocol_version": protocol_label,
        "outcome_opened": False,
    }
    frozen_hash = sha256_json(frozen_protocol)
    registry = {
        "registry_id": f"REG-{protocol_label}",
        "candidate_hash": candidate_hash,
        "protocol_hash": protocol_hash,
        "frozen_protocol_hash": frozen_hash,
    }
    frozen_registry = deepcopy(registry)
    body = {
        "status": "PASS",
        "blockers": [],
        "registry": registry,
        "frozen_registry": frozen_registry,
        "frozen_protocol": frozen_protocol,
        "outcome_accessed": False,
        "economic_result": "NOT_OBSERVED",
        "economic_experiment_authorized": False,
        "prospective_observation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
    }
    body["infrastructure_hash"] = sha256_json(body)
    return body


def cross_axes(default="PASS"):
    names = (
        "identity_ambiguity",
        "timing_ambiguity",
        "source_ambiguity",
        "pit_integrity",
        "implementation_assumptions",
        "duplicate_expression",
    )
    return {name: {"status": default, "reason_codes": []} for name in names}


def validator_receipt(factory, status="READY_FOR_AUTHORIZED_ECONOMIC_TEST"):
    ready = status == "READY_FOR_AUTHORIZED_ECONOMIC_TEST"
    return {
        "hypothesis_id": factory["hypothesis_id"],
        "generation_id": factory["generation_id"],
        "validator": "independent-validator.fixture",
        "producer_id": "producer.fixture",
        "status": status,
        "ready_for_authorized_economic_test": ready,
        "checks": {"candidate_immutability": {"status": "PASS" if ready else "FAIL"}},
        "block_reasons": [] if ready else [{"code": "CANDIDATE_IMMUTABILITY_FAILED"}],
        "candidate_hash": factory["candidate_hash"],
        "protocol_hash": factory["protocol_hash"],
        "economic_test_authorized": False,
        "economic_claim_authorized": False,
        "outcome_access_authorized": False,
        "candidate_mutated": False,
        "signal_repair_attempted": False,
        "parameter_optimization_attempted": False,
    }


def red_team_receipt(factory, status="PASS", blockers=None):
    blockers = [] if blockers is None else list(blockers)
    return {
        "hypothesis_id": factory["hypothesis_id"],
        "generation_id": factory["generation_id"],
        "red_team": "red-team.fixture",
        "status": status,
        "negative_rights": blockers,
        "repair_attempted": False,
        "signal_repair_attempted": False,
        "candidate_mutated": False,
        "validator_receipt_mutated": False,
        "parameters_optimized": False,
        "outcomes_opened": False,
        "retuned_until_profitable": False,
        "economic_test_authorized": False,
        "capital_authorized": False,
    }


def independence_record(relation="PRIMARY_SOURCE_RECONSTRUCTION", axes=True):
    return {
        "information_isolation": axes,
        "retrieval_independence": axes,
        "cognitive_independence": axes,
        "state_isolation": axes,
        "retrieval": {"reconstructed_v2_candidate_hash": "a" * 64},
        "information_scope": "PRIMARY_SOURCE_AND_FROZEN_CANDIDATE_NO_PRODUCER_MODEL_COMMENTARY",
        "cognitive_scope": "R0_DETERMINISTIC_STRUCTURAL_CHECKS_ONLY",
        "semantic_diverse_review": "NOT_PROVEN_NO_SEMANTIC_PASS_GRANTED",
        "support_relation": relation,
        "outcome_accessed": False,
    }


def negative_record(factory, **overrides):
    value = {
        "status": "QUALIFIED_NEGATIVE",
        "disposition": "KILL",
        "hypothesis_id": factory["hypothesis_id"],
        "generation_id": factory["generation_id"],
        "candidate_hash": factory["candidate_hash"],
        "protocol_hash": factory["protocol_hash"],
        "frozen_protocol_hash": factory["frozen_protocol_hash"],
        "evidence_hash": "b" * 64,
        "evaluator_id": "external-scientific-evaluator.fixture",
        "negative_knowledge_scope": "EXACT_CANDIDATE_PROTOCOL_ONLY",
        "negative_knowledge_global": False,
        "issued_by_c0": False,
        "raw_outcomes_included": False,
        "outcome_accessed_by_c0": False,
        "economic_experiment_authorized": False,
        "prospective_observation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
        "outcome_accessed": False,
    }
    value.update(overrides)
    return value


class MegaC0ScientificAdjudicationTests(unittest.TestCase):
    def setUp(self):
        self.candidate = candidate()
        self.factory = bind_factory_ref(self.candidate, infrastructure(self.candidate))
        self.cross = build_cross_examination_ref(
            self.factory, cross_axes(), examiner_id="cross-exam.fixture", provenance_refs=["ref://primary/1"]
        )
        self.validator = bind_validator_ref(self.factory, validator_receipt(self.factory))
        self.red_team = bind_red_team_ref(
            self.factory, self.validator, red_team_receipt(self.factory)
        )
        self.independence = bind_independence_ref(self.factory, independence_record())

    def adjudicate(self, **overrides):
        args = {
            "cross_examination_ref": self.cross,
            "validator_ref": self.validator,
            "red_team_ref": self.red_team,
            "independence_ref": self.independence,
        }
        args.update(overrides)
        return adjudicate_scientific_candidate(self.factory, **args)

    def test_authority_membrane_is_immutable_and_closed(self):
        self.assertTrue(all(value is False for value in authority_state().values()))
        with self.assertRaises(TypeError):
            AUTHORITY_STATE["real_capital_authorized"] = True
        result = self.adjudicate()
        for key in AUTHORITY_STATE:
            self.assertFalse(result[key])

    def test_factory_ref_binds_candidate_protocol_and_freeze(self):
        validate_factory_ref(self.factory)
        self.assertEqual(self.factory["candidate_hash"], sha256_json(self.candidate))
        self.assertEqual(self.factory["economic_result"], "NOT_OBSERVED")
        self.assertFalse(self.factory["outcome_accessed"])

    def test_factory_candidate_hash_drift_is_rejected(self):
        bad = infrastructure(self.candidate)
        bad["frozen_protocol"]["candidate_hash"] = "0" * 64
        bad["infrastructure_hash"] = sha256_json({k: v for k, v in bad.items() if k != "infrastructure_hash"})
        with self.assertRaisesRegex(ScientificAdjudicationError, "candidate hash mismatch"):
            bind_factory_ref(self.candidate, bad)

    def test_factory_frozen_protocol_hash_drift_is_rejected(self):
        bad = infrastructure(self.candidate)
        bad["registry"]["frozen_protocol_hash"] = "0" * 64
        bad["infrastructure_hash"] = sha256_json({k: v for k, v in bad.items() if k != "infrastructure_hash"})
        with self.assertRaisesRegex(ScientificAdjudicationError, "frozen protocol hash mismatch"):
            bind_factory_ref(self.candidate, bad)

    def test_factory_ref_tamper_is_hash_detected(self):
        bad = deepcopy(self.factory)
        bad["generation_id"] = "G2"
        with self.assertRaisesRegex(ScientificAdjudicationError, "hash mismatch"):
            validate_factory_ref(bad)

    def test_raw_outcome_alias_is_rejected_recursively(self):
        bad = infrastructure(self.candidate)
        bad["audit_metadata"] = {"nested": [{"return_series": [0.01]}]}
        bad["infrastructure_hash"] = sha256_json({k: v for k, v in bad.items() if k != "infrastructure_hash"})
        with self.assertRaisesRegex(ScientificAdjudicationError, "outcome-bearing"):
            bind_factory_ref(self.candidate, bad)

    def test_cross_exam_all_pass_is_pass(self):
        self.assertEqual(self.cross["status"], "PASS")
        self.assertFalse(self.cross["negative_claim_supported"])
        validate_cross_examination_ref(self.cross, self.factory)

    def test_cross_exam_unknown_is_bounded_park_not_negative(self):
        axes = cross_axes()
        axes["source_ambiguity"] = {"status": "UNKNOWN", "reason_codes": ["SOURCE_SCOPE_UNRESOLVED"]}
        ref = build_cross_examination_ref(
            self.factory, axes, examiner_id="cross-exam.fixture", provenance_refs=["ref://primary/1"]
        )
        self.assertEqual(ref["status"], "PARK")
        result = self.adjudicate(cross_examination_ref=ref)
        self.assertEqual(result["verdict"], "PARK")
        self.assertFalse(result["scientific_negative_claim"])

    def test_cross_exam_conflict_blocks(self):
        axes = cross_axes()
        axes["timing_ambiguity"] = {"status": "CONFLICTED", "reason_codes": ["CLOCK_CONFLICT"]}
        ref = build_cross_examination_ref(
            self.factory, axes, examiner_id="cross-exam.fixture", provenance_refs=["ref://primary/1"]
        )
        result = self.adjudicate(cross_examination_ref=ref)
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertIn("CROSS_EXAM_timing_ambiguity", result["reason_codes"])

    def test_cross_exam_ref_tamper_is_detected(self):
        bad = deepcopy(self.cross)
        bad["status"] = "BLOCK"
        with self.assertRaisesRegex(ScientificAdjudicationError, "hash mismatch"):
            validate_cross_examination_ref(bad, self.factory)

    def test_validator_ready_ref_is_exactly_bound(self):
        validate_validator_ref(self.validator, self.factory)
        self.assertEqual(self.validator["candidate_hash"], self.factory["candidate_hash"])
        self.assertEqual(self.validator["protocol_hash"], self.factory["protocol_hash"])

    def test_validator_generation_mismatch_is_rejected(self):
        receipt = validator_receipt(self.factory)
        receipt["generation_id"] = "G2"
        with self.assertRaisesRegex(ScientificAdjudicationError, "generation_id mismatch"):
            bind_validator_ref(self.factory, receipt)

    def test_validator_block_prevents_promote(self):
        validator = bind_validator_ref(
            self.factory, validator_receipt(self.factory, status="BLOCK")
        )
        red = bind_red_team_ref(
            self.factory, validator,
            red_team_receipt(self.factory, status="BLOCK", blockers=["BLOCK_REPRODUCIBILITY"]),
        )
        result = self.adjudicate(validator_ref=validator, red_team_ref=red)
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertFalse(result["scientific_negative_claim"])

    def test_red_team_pass_is_negative_rights_clear(self):
        validate_red_team_ref(self.red_team, self.factory, self.validator)
        self.assertEqual(self.red_team["negative_rights"], [])
        self.assertFalse(self.red_team["negative_claim_supported"])

    def test_red_team_block_prevents_promote_but_does_not_kill(self):
        red = bind_red_team_ref(
            self.factory, self.validator,
            red_team_receipt(self.factory, status="BLOCK", blockers=["BLOCK_LEAKAGE"]),
        )
        result = self.adjudicate(red_team_ref=red)
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertFalse(result["scientific_negative_claim"])

    def test_red_team_cannot_emit_unknown_negative_right(self):
        receipt = red_team_receipt(self.factory, status="BLOCK", blockers=["KILL_IT"])
        with self.assertRaisesRegex(ScientificAdjudicationError, "outside negative-rights"):
            bind_red_team_ref(self.factory, self.validator, receipt)

    def test_independence_primary_reconstruction_counts_once(self):
        validate_independence_ref(self.independence, self.factory)
        self.assertEqual(self.independence["status"], "PASS")
        self.assertEqual(self.independence["independent_confirmation_count"], 1)

    def test_duplicate_support_does_not_count_as_independent_confirmation(self):
        ref = bind_independence_ref(self.factory, independence_record("DUPLICATE"))
        validate_independence_ref(ref, self.factory)
        self.assertEqual(ref["independent_confirmation_count"], 0)

    def test_wrapper_equivalent_support_does_not_count_as_independent_confirmation(self):
        ref = bind_independence_ref(self.factory, independence_record("WRAPPER_EQUIVALENT"))
        self.assertEqual(ref["independent_confirmation_count"], 0)

    def test_unproven_independence_blocks(self):
        ref = bind_independence_ref(self.factory, independence_record(axes=False))
        result = self.adjudicate(independence_ref=ref)
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertIn("VALIDATOR_INDEPENDENCE_NOT_PROVEN", result["reason_codes"])

    def test_missing_cross_exam_is_unexecuted_block_not_negative(self):
        result = self.adjudicate(cross_examination_ref=None)
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertIn("CROSS_EXAMINATION_UNEXECUTED", result["reason_codes"])
        self.assertFalse(result["unexecuted_is_negative"])
        self.assertFalse(result["scientific_negative_claim"])

    def test_missing_validator_is_block_not_failure_or_negative(self):
        result = adjudicate_scientific_candidate(
            self.factory,
            cross_examination_ref=self.cross,
            validator_ref=None,
            red_team_ref=None,
            independence_ref=self.independence,
        )
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertFalse(result["blocked_is_failed"])
        self.assertFalse(result["scientific_negative_claim"])

    def test_complete_clear_composition_promotes_only_to_economic_identity(self):
        result = self.adjudicate()
        self.assertEqual(result["verdict"], "PROMOTE")
        self.assertEqual(result["promotion_target"], "ECONOMIC_IDENTITY")
        self.assertFalse(result["economic_identity_created"])
        self.assertEqual(result["profitability_status"], "UNKNOWN")
        self.assertFalse(result["ready_is_profitable"])
        self.assertEqual(result["economic_result"], "NOT_OBSERVED")

    def test_qualified_scoped_external_negative_is_only_kill_path(self):
        negative = bind_qualified_negative_ref(self.factory, negative_record(self.factory))
        result = self.adjudicate(qualified_negative_ref=negative)
        self.assertEqual(result["verdict"], "KILL")
        self.assertTrue(result["scientific_negative_claim"])
        self.assertFalse(result["negative_knowledge_global"])
        self.assertEqual(result["raw_outcomes_consumed"], 0)

    def test_qualified_negative_cannot_bypass_validator_block(self):
        negative = bind_qualified_negative_ref(self.factory, negative_record(self.factory))
        validator = bind_validator_ref(self.factory, validator_receipt(self.factory, status="BLOCK"))
        red = bind_red_team_ref(
            self.factory, validator,
            red_team_receipt(self.factory, status="BLOCK", blockers=["BLOCK_CLAIM_LEVEL"]),
        )
        result = self.adjudicate(
            validator_ref=validator, red_team_ref=red, qualified_negative_ref=negative
        )
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertFalse(result["scientific_negative_claim"])

    def test_c0_cannot_self_issue_negative_ref(self):
        with self.assertRaisesRegex(ScientificAdjudicationError, "self-issue"):
            bind_qualified_negative_ref(
                self.factory, negative_record(self.factory, issued_by_c0=True)
            )

    def test_global_negative_knowledge_is_rejected(self):
        with self.assertRaisesRegex(ScientificAdjudicationError, "global"):
            bind_qualified_negative_ref(
                self.factory,
                negative_record(
                    self.factory,
                    negative_knowledge_scope="GLOBAL",
                    negative_knowledge_global=True,
                ),
            )

    def test_raw_outcome_cannot_cross_negative_ref(self):
        record = negative_record(self.factory)
        record["nested"] = {"pnl_series": [1.0]}
        with self.assertRaisesRegex(ScientificAdjudicationError, "outcome-bearing"):
            bind_qualified_negative_ref(self.factory, record)

    def test_negative_ref_tamper_is_detected(self):
        ref = bind_qualified_negative_ref(self.factory, negative_record(self.factory))
        bad = deepcopy(ref)
        bad["negative_knowledge_scope"] = "OTHER_SCOPE"
        with self.assertRaisesRegex(ScientificAdjudicationError, "hash mismatch"):
            validate_qualified_negative_ref(bad, self.factory)

    def test_replay_is_deterministic(self):
        first = self.adjudicate()
        second = self.adjudicate()
        self.assertEqual(first, second)
        validate_adjudication(first)

    def test_protocol_material_change_creates_new_adjudication_identity(self):
        changed_factory = bind_factory_ref(self.candidate, infrastructure(self.candidate, protocol_label="P2"))
        changed_cross = build_cross_examination_ref(
            changed_factory, cross_axes(), examiner_id="cross-exam.fixture", provenance_refs=["ref://primary/1"]
        )
        changed_validator = bind_validator_ref(changed_factory, validator_receipt(changed_factory))
        changed_red = bind_red_team_ref(
            changed_factory, changed_validator, red_team_receipt(changed_factory)
        )
        changed_independence = bind_independence_ref(changed_factory, independence_record())
        changed = adjudicate_scientific_candidate(
            changed_factory,
            cross_examination_ref=changed_cross,
            validator_ref=changed_validator,
            red_team_ref=changed_red,
            independence_ref=changed_independence,
        )
        original = self.adjudicate()
        self.assertNotEqual(changed_factory["protocol_hash"], self.factory["protocol_hash"])
        self.assertNotEqual(changed_factory["frozen_protocol_hash"], self.factory["frozen_protocol_hash"])
        self.assertNotEqual(changed["adjudication_identity"], original["adjudication_identity"])

    def test_candidate_generation_change_creates_new_adjudication_identity(self):
        changed_candidate = candidate(generation="G2")
        changed_factory = bind_factory_ref(changed_candidate, infrastructure(changed_candidate))
        changed_cross = build_cross_examination_ref(
            changed_factory, cross_axes(), examiner_id="cross-exam.fixture", provenance_refs=["ref://primary/1"]
        )
        changed_validator = bind_validator_ref(changed_factory, validator_receipt(changed_factory))
        changed_red = bind_red_team_ref(changed_factory, changed_validator, red_team_receipt(changed_factory))
        changed_independence = bind_independence_ref(changed_factory, independence_record())
        changed = adjudicate_scientific_candidate(
            changed_factory,
            cross_examination_ref=changed_cross,
            validator_ref=changed_validator,
            red_team_ref=changed_red,
            independence_ref=changed_independence,
        )
        self.assertNotEqual(changed["adjudication_identity"], self.adjudicate()["adjudication_identity"])

    def test_adjudication_tamper_is_detected(self):
        result = self.adjudicate()
        bad = deepcopy(result)
        bad["verdict"] = "KILL"
        bad["promotion_target"] = None
        with self.assertRaisesRegex(ScientificAdjudicationError, "hash mismatch"):
            validate_adjudication(bad)


if __name__ == "__main__":
    unittest.main()
