from __future__ import annotations

from copy import deepcopy
import unittest

from research.research_os.scientific_store import sha256_json
from research.research_os.expansion.scientific_adjudication import (
    AUTHORITY_STATE,
    CROSS_EXAMINATION_AXES,
    QUALIFIED_HISTORICAL_C0_SOURCE_BLOB,
    WAVE2_IMMUTABLE_BASE_SHA,
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
    validate_factory_ref,
    validate_qualified_negative_ref,
)


CANONICAL_BASE = "2b99d8aeb8a342f1ef32544247d366cb8a26037e"


def candidate(*, claim_ceiling="MECHANISM_AND_PRE_ECONOMIC_READINESS_ONLY"):
    return {
        "hypothesis_id": "H-C2-C0-001",
        "generation_id": "G1",
        "mechanism": "bounded-causal-mechanism",
        "payer": "constrained-counterparty",
        "universe": "bounded-universe",
        "trial_id": "TRIAL-001",
        "experiment_epoch": "EPOCH-001",
        "falsification_scope": ["clock mismatch", "source contradiction", "payer contradiction"],
        "decision_map": {"pass": "continue", "fail": "stop", "unknown": "park"},
        "provenance": {"refs": ["ref://primary/1"], "pit": "frozen"},
        "ancestry": {"parent": "research-intelligence-candidate"},
        "expression_identity": {"instrument": "FIXTURE", "wrapper": "CASH"},
        "discovery": {
            "claim_ceiling": claim_ceiling,
            "evidence_gaps": ["future economic evidence not observed"],
        },
    }


def infrastructure(c, protocol_label="P-C2"):
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
    body = {
        "status": "PASS",
        "blockers": [],
        "registry": registry,
        "frozen_registry": deepcopy(registry),
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
    return {
        name: {"status": default, "reason_codes": []}
        for name in CROSS_EXAMINATION_AXES
    }


def validator_receipt(factory, *, status="READY_FOR_AUTHORIZED_ECONOMIC_TEST", **overrides):
    ready = status == "READY_FOR_AUTHORIZED_ECONOMIC_TEST"
    value = {
        "hypothesis_id": factory["hypothesis_id"],
        "generation_id": factory["generation_id"],
        "validator": "independent-validator.c2",
        "producer_id": "producer.fixture",
        "status": status,
        "ready_for_authorized_economic_test": ready,
        "checks": {"frozen_identity": {"status": "PASS" if ready else "FAIL"}},
        "block_reasons": [] if ready else [{"code": "FROZEN_IDENTITY_FAILED"}],
        "candidate_hash": factory["candidate_hash"],
        "protocol_hash": factory["protocol_hash"],
        "frozen_protocol_hash": factory["frozen_protocol_hash"],
        "economic_test_authorized": False,
        "economic_claim_authorized": False,
        "outcome_access_authorized": False,
        "candidate_mutated": False,
        "validator_independent": True,
        "self_validation": False,
        "outcome_accessed": False,
        "post_outcome_mutation": False,
    }
    value.update(overrides)
    return value


def red_team_receipt(factory, *, status="PASS", blockers=None, **overrides):
    blockers = [] if blockers is None else list(blockers)
    value = {
        "hypothesis_id": factory["hypothesis_id"],
        "generation_id": factory["generation_id"],
        "candidate_hash": factory["candidate_hash"],
        "protocol_hash": factory["protocol_hash"],
        "frozen_protocol_hash": factory["frozen_protocol_hash"],
        "red_team": "independent-red-team.c2",
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
        "red_team_independent": True,
        "self_red_team": False,
        "outcome_accessed": False,
        "post_outcome_mutation": False,
    }
    value.update(overrides)
    return value


def independence_record(*, relation="PRIMARY_SOURCE_RECONSTRUCTION", axes=True):
    return {
        "information_isolation": axes,
        "retrieval_independence": axes,
        "cognitive_independence": axes,
        "state_isolation": axes,
        "retrieval": {"reconstructed_v2_candidate_hash": "a" * 64},
        "information_scope": "PRIMARY_SOURCE_AND_FROZEN_CANDIDATE_NO_PRODUCER_COMMENTARY",
        "cognitive_scope": "DETERMINISTIC_STRUCTURAL_CHECKS_ONLY",
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
        "evaluator_authority_kind": "GIT_COMMIT_PATH",
        "evaluator_authority_commit_sha": "c" * 40,
        "evaluator_authority_path": "evidence/external/qualified-negative.json",
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


class Wave2C2ScientificAdjudicationTests(unittest.TestCase):
    def setUp(self):
        self.candidate = candidate()
        self.factory = bind_factory_ref(self.candidate, infrastructure(self.candidate))
        self.cross = build_cross_examination_ref(
            self.factory,
            cross_axes(),
            examiner_id="independent-cross-exam.c2",
            provenance_refs=["ref://primary/1", "ref://pit/frozen"],
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

    def test_canonical_base_and_preserved_source_are_explicit(self):
        self.assertEqual(WAVE2_IMMUTABLE_BASE_SHA, CANONICAL_BASE)
        self.assertEqual(QUALIFIED_HISTORICAL_C0_SOURCE_BLOB, "3f0e1b7bae53e9513f0061cabcfae2505a6795f3")
        self.assertEqual(self.factory["wave2_base_sha"], CANONICAL_BASE)
        self.assertEqual(self.factory["qualified_historical_source_blob"], QUALIFIED_HISTORICAL_C0_SOURCE_BLOB)

    def test_authority_membrane_remains_closed_and_immutable(self):
        self.assertTrue(all(value is False for value in authority_state().values()))
        with self.assertRaises(TypeError):
            AUTHORITY_STATE["real_capital_authorized"] = True
        result = self.adjudicate()
        for key in AUTHORITY_STATE:
            self.assertFalse(result[key])

    def test_factory_ref_preserves_trial_epoch_expression_provenance_and_claim_ceiling(self):
        validate_factory_ref(self.factory)
        context = self.factory["scientific_context"]
        self.assertEqual(context["trial_id"], "TRIAL-001")
        self.assertEqual(context["experiment_epoch"], "EPOCH-001")
        self.assertNotEqual(context["frozen_expression_hash"], "UNKNOWN")
        self.assertNotEqual(context["provenance_hash"], "UNKNOWN")
        self.assertEqual(context["claim_ceiling"], "MECHANISM_AND_PRE_ECONOMIC_READINESS_ONLY")

    def test_factory_ref_hash_tamper_fails(self):
        bad = deepcopy(self.factory)
        bad["scientific_context"]["trial_id"] = "TRIAL-TAMPERED"
        with self.assertRaisesRegex(ScientificAdjudicationError, "hash mismatch"):
            validate_factory_ref(bad)

    def test_cross_examination_requires_all_canonical_axes(self):
        axes = cross_axes()
        axes.pop("factor_beta_exposure")
        with self.assertRaisesRegex(ScientificAdjudicationError, "axes are incomplete"):
            build_cross_examination_ref(
                self.factory, axes, examiner_id="cross.c2", provenance_refs=["ref://primary/1"]
            )

    def test_unknown_cross_exam_is_inconclusive_not_negative(self):
        axes = cross_axes()
        axes["factor_beta_exposure"] = {"status": "UNKNOWN", "reason_codes": ["BETA_UNRESOLVED"]}
        cross = build_cross_examination_ref(
            self.factory, axes, examiner_id="cross.c2", provenance_refs=["ref://primary/1"]
        )
        result = self.adjudicate(cross_examination_ref=cross)
        self.assertEqual(result["verdict"], "PARK")
        self.assertEqual(result["scientific_posture"], "INCONCLUSIVE")
        self.assertFalse(result["scientific_negative_claim"])
        self.assertTrue(result["uncertainty_state"]["unknown_preserved"])

    def test_evidence_contradiction_blocks_but_does_not_become_negative(self):
        axes = cross_axes()
        axes["evidence_contradictions"] = {"status": "CONFLICTED", "reason_codes": ["PRIMARY_SOURCE_CONFLICT"]}
        cross = build_cross_examination_ref(
            self.factory, axes, examiner_id="cross.c2", provenance_refs=["ref://primary/1"]
        )
        result = self.adjudicate(cross_examination_ref=cross)
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertEqual(result["scientific_posture"], "BLOCKED")
        self.assertFalse(result["scientific_negative_claim"])

    def test_missing_components_are_blocked_not_negative(self):
        result = adjudicate_scientific_candidate(self.factory)
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertEqual(result["scientific_posture"], "BLOCKED")
        self.assertFalse(result["scientific_negative_claim"])
        self.assertFalse(result["unexecuted_is_negative"])

    def test_validator_self_validation_is_rejected(self):
        receipt = validator_receipt(
            self.factory,
            producer_id="independent-validator.c2",
            self_validation=True,
        )
        with self.assertRaises(ScientificAdjudicationError):
            bind_validator_ref(self.factory, receipt)

    def test_validator_freeze_mismatch_is_rejected(self):
        receipt = validator_receipt(self.factory, frozen_protocol_hash="0" * 64)
        with self.assertRaisesRegex(ScientificAdjudicationError, "frozen protocol hash mismatch"):
            bind_validator_ref(self.factory, receipt)

    def test_validator_post_outcome_mutation_is_rejected(self):
        receipt = validator_receipt(self.factory, post_outcome_mutation=True)
        with self.assertRaisesRegex(ScientificAdjudicationError, "post-outcome mutation"):
            bind_validator_ref(self.factory, receipt)

    def test_red_team_must_be_distinct_from_validator(self):
        receipt = red_team_receipt(self.factory, red_team=self.validator["validator_id"])
        with self.assertRaisesRegex(ScientificAdjudicationError, "may not be the Validator"):
            bind_red_team_ref(self.factory, self.validator, receipt)

    def test_red_team_exact_frozen_identity_mismatch_is_rejected(self):
        receipt = red_team_receipt(self.factory, candidate_hash="0" * 64)
        with self.assertRaisesRegex(ScientificAdjudicationError, "candidate_hash mismatch"):
            bind_red_team_ref(self.factory, self.validator, receipt)

    def test_cross_examiner_may_not_be_validator(self):
        cross = build_cross_examination_ref(
            self.factory,
            cross_axes(),
            examiner_id=self.validator["validator_id"],
            provenance_refs=["ref://primary/1"],
        )
        with self.assertRaisesRegex(ScientificAdjudicationError, "must be distinct"):
            self.adjudicate(cross_examination_ref=cross)

    def test_raw_outcome_alias_is_rejected_recursively(self):
        bad = infrastructure(self.candidate)
        bad["audit"] = {"nested": [{"return_series": [0.01]}]}
        bad["infrastructure_hash"] = sha256_json({k: v for k, v in bad.items() if k != "infrastructure_hash"})
        with self.assertRaisesRegex(ScientificAdjudicationError, "outcome-bearing"):
            bind_factory_ref(self.candidate, bad)

    def test_negative_evidence_requires_immutable_external_authority(self):
        record = negative_record(self.factory)
        record.pop("evaluator_authority_commit_sha")
        with self.assertRaisesRegex(ScientificAdjudicationError, "commit"):
            bind_qualified_negative_ref(self.factory, record)

    def test_negative_evidence_rejects_non_git_authority(self):
        with self.assertRaisesRegex(ScientificAdjudicationError, "immutable evaluator authority"):
            bind_qualified_negative_ref(
                self.factory,
                negative_record(self.factory, evaluator_authority_kind="COMMENTARY"),
            )

    def test_negative_knowledge_scope_cannot_be_global(self):
        with self.assertRaisesRegex(ScientificAdjudicationError, "global"):
            bind_qualified_negative_ref(
                self.factory,
                negative_record(
                    self.factory,
                    negative_knowledge_scope="GLOBAL",
                    negative_knowledge_global=False,
                ),
            )

    def test_qualified_scoped_negative_can_reject_without_c0_outcome_access(self):
        negative = bind_qualified_negative_ref(self.factory, negative_record(self.factory))
        validate_qualified_negative_ref(negative, self.factory)
        result = self.adjudicate(qualified_negative_ref=negative)
        self.assertEqual(result["verdict"], "KILL")
        self.assertEqual(result["scientific_posture"], "REJECT")
        self.assertEqual(result["negative_knowledge_scope"], "EXACT_CANDIDATE_PROTOCOL_ONLY")
        self.assertFalse(result["outcome_accessed"])
        self.assertEqual(result["raw_outcomes_consumed"], 0)

    def test_promote_maps_to_qualified_with_claim_ceiling_only(self):
        result = self.adjudicate()
        validate_adjudication(result)
        self.assertEqual(result["verdict"], "PROMOTE")
        self.assertEqual(result["scientific_posture"], "QUALIFIED_WITH_CLAIM_CEILING")
        self.assertEqual(result["claim_ceiling"], "MECHANISM_AND_PRE_ECONOMIC_READINESS_ONLY")
        self.assertEqual(result["promotion_target"], "ECONOMIC_IDENTITY")
        self.assertFalse(result["economic_identity_created"])
        self.assertEqual(result["profitability_status"], "UNKNOWN")
        self.assertEqual(result["downstream_binding_required"], [
            "ECONOMIC_IDENTITY_REF", "PORTFOLIO_READINESS_REF", "ECONOMIC_LIFECYCLE_D0"
        ])

    def test_unknown_claim_ceiling_cannot_receive_favorable_posture(self):
        c = candidate(claim_ceiling="UNKNOWN")
        factory = bind_factory_ref(c, infrastructure(c))
        cross = build_cross_examination_ref(
            factory, cross_axes(), examiner_id="cross.c2", provenance_refs=["ref://primary/1"]
        )
        validator = bind_validator_ref(factory, validator_receipt(factory))
        red = bind_red_team_ref(factory, validator, red_team_receipt(factory))
        independence = bind_independence_ref(factory, independence_record())
        result = adjudicate_scientific_candidate(
            factory,
            cross_examination_ref=cross,
            validator_ref=validator,
            red_team_ref=red,
            independence_ref=independence,
        )
        self.assertEqual(result["verdict"], "PARK")
        self.assertEqual(result["scientific_posture"], "INCONCLUSIVE")
        self.assertIn("CLAIM_CEILING_UNRESOLVED", result["reason_codes"])

    def test_duplicate_independence_never_counts_as_independent_confirmation(self):
        ref = bind_independence_ref(
            self.factory, independence_record(relation="DUPLICATE")
        )
        self.assertEqual(ref["independent_confirmation_count"], 0)


if __name__ == "__main__":
    unittest.main()
