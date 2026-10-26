from __future__ import annotations

from copy import deepcopy
import unittest

from research.research_os.scientific_store import sha256_json
from research.research_os.expansion.portfolio_v2 import portfolio_diagnostics_v2
from research.research_os.expansion.scientific_adjudication import (
    CROSS_EXAMINATION_AXES,
    adjudicate_scientific_candidate,
    bind_factory_ref,
    bind_independence_ref,
    bind_red_team_ref,
    bind_validator_ref,
    build_cross_examination_ref,
)
from research.research_os.expansion.economic_lifecycle import (
    bind_economic_identity_ref,
    bind_portfolio_readiness_ref,
    validate_shadow_contract,
)
from research.research_os.expansion.wave2_scientific_economic_bridge import (
    bind_scientific_economic_handoff,
    create_d0_shadow_from_scientific_handoff,
    validate_scientific_economic_handoff,
)


def candidate(hid: str, suffix: str):
    return {
        "hypothesis_id": hid,
        "generation_id": "G1",
        "mechanism": f"mechanism-{suffix}",
        "payer": f"payer-{suffix}",
        "forced_constrained_actor": f"actor-{suffix}",
        "instrument": f"instrument-{suffix}",
        "universe": f"universe-{suffix}",
        "timing_clock": f"clock-{suffix}",
        "horizon": f"horizon-{suffix}",
        "capacity_bottleneck": f"capacity-{suffix}",
        "cost_structure": f"cost-{suffix}",
        "economic_exposure": f"exposure-{suffix}",
        "event_rule_dependency": f"rule-{suffix}",
        "source_identity": f"source-{suffix}",
        "economic_tags": [f"tag-{suffix}"],
        "trial_id": f"TRIAL-{suffix}",
        "experiment_epoch": "EPOCH-001",
        "claim": f"bounded claim {suffix}",
        "falsification_scope": [f"falsifier-{suffix}"],
        "decision_map": {"pass": "continue", "fail": "stop", "unknown": "park"},
        "provenance": {"refs": [f"ref://primary/{suffix}"], "pit": "frozen"},
        "ancestry": {"parent": f"research-intelligence-{suffix}"},
        "expression_identity": {"instrument": f"instrument-{suffix}", "wrapper": "CASH"},
        "discovery": {
            "claim_ceiling": "MECHANISM_AND_PRE_ECONOMIC_READINESS_ONLY",
            "evidence_gaps": ["future economic evidence not observed"],
        },
    }


def infrastructure(c):
    candidate_hash = sha256_json(c)
    protocol_hash = sha256_json({"protocol": "P-SEAM", "candidate_hash": candidate_hash})
    frozen_protocol = {
        "candidate_hash": candidate_hash,
        "protocol_hash": protocol_hash,
        "protocol_version": "P-SEAM",
        "outcome_opened": False,
    }
    frozen_hash = sha256_json(frozen_protocol)
    registry = {
        "registry_id": "REG-SEAM",
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


def promoted_adjudication(c):
    factory = bind_factory_ref(c, infrastructure(c))
    axes = {name: {"status": "PASS", "reason_codes": []} for name in CROSS_EXAMINATION_AXES}
    cross = build_cross_examination_ref(
        factory, axes, examiner_id="cross.seam", provenance_refs=["ref://primary/seam"]
    )
    validator = bind_validator_ref(factory, {
        "hypothesis_id": factory["hypothesis_id"],
        "generation_id": factory["generation_id"],
        "validator": "validator.seam",
        "producer_id": "producer.seam",
        "status": "READY_FOR_AUTHORIZED_ECONOMIC_TEST",
        "ready_for_authorized_economic_test": True,
        "checks": {"frozen_identity": {"status": "PASS"}},
        "block_reasons": [],
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
    })
    red = bind_red_team_ref(factory, validator, {
        "hypothesis_id": factory["hypothesis_id"],
        "generation_id": factory["generation_id"],
        "candidate_hash": factory["candidate_hash"],
        "protocol_hash": factory["protocol_hash"],
        "frozen_protocol_hash": factory["frozen_protocol_hash"],
        "red_team": "red-team.seam",
        "status": "PASS",
        "negative_rights": [],
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
    })
    independence = bind_independence_ref(factory, {
        "information_isolation": True,
        "retrieval_independence": True,
        "cognitive_independence": True,
        "state_isolation": True,
        "retrieval": {"reconstructed_v2_candidate_hash": "a" * 64},
        "information_scope": "PRIMARY_SOURCE_ONLY",
        "cognitive_scope": "STRUCTURAL_CHECKS_ONLY",
        "semantic_diverse_review": "NOT_PROVEN_NO_SEMANTIC_PASS_GRANTED",
        "support_relation": "PRIMARY_SOURCE_RECONSTRUCTION",
        "outcome_accessed": False,
    })
    return adjudicate_scientific_candidate(
        factory,
        cross_examination_ref=cross,
        validator_ref=validator,
        red_team_ref=red,
        independence_ref=independence,
    )


def w1_identity(c):
    binding = {
        "hypothesis_id": c["hypothesis_id"],
        "generation_id": c["generation_id"],
        "candidate_hash": sha256_json(c),
    }
    return {
        "hypothesis_id": c["hypothesis_id"],
        "generation_id": c["generation_id"],
        "mechanism": c["mechanism"],
        "payer": c["payer"],
        "forced_constrained_actor": c["forced_constrained_actor"],
        "instrument": c["instrument"],
        "universe": c["universe"],
        "timing_clock": c["timing_clock"],
        "horizon": c["horizon"],
        "capacity_bottleneck": c["capacity_bottleneck"],
        "cost_structure": c["cost_structure"],
        "economic_exposure": c["economic_exposure"],
        "event_rule_dependency": c["event_rule_dependency"],
        "source_identity": c["source_identity"],
        "economic_tags": list(c["economic_tags"]),
        "candidate_binding": deepcopy(binding),
        "candidate_snapshot": deepcopy(c),
        "identity_provenance": {
            "candidate_hash": binding["candidate_hash"],
            "candidate_binding": deepcopy(binding),
            "source_hash": sha256_json({"source_identity": c["source_identity"]}),
            "dossier_hash": "UNKNOWN",
            "source_refs": [f"ref://{c['source_identity']}"],
        },
    }


def review_policy():
    return {
        "policy_id": "W2-C2-SEAM-REVIEW",
        "policy_version": "v1",
        "cadence_kind": "HYBRID",
        "review_interval": 30,
        "minimum_admissible_observations": 20,
        "minimum_distinct_review_windows": 2,
        "regime_context_required": True,
        "implementation_context_required": True,
        "cost_capacity_context_required": True,
    }


class Wave2C2ScientificEconomicD0SeamTests(unittest.TestCase):
    def setUp(self):
        self.a = candidate("H-SEAM-A", "a")
        self.b = candidate("H-SEAM-B", "b")
        self.adjudication = promoted_adjudication(self.a)
        self.identity_a = w1_identity(self.a)
        self.identity_b = w1_identity(self.b)
        self.diagnostics = portfolio_diagnostics_v2([self.identity_a, self.identity_b])
        self.econ_ref = bind_economic_identity_ref(self.identity_a)
        self.readiness_ref = bind_portfolio_readiness_ref(self.diagnostics, self.econ_ref)
        self.handoff = bind_scientific_economic_handoff(
            self.adjudication, self.econ_ref, self.readiness_ref
        )

    def test_exact_candidate_identity_flows_across_all_three_owners(self):
        candidate_hash = sha256_json(self.a)
        self.assertEqual(self.adjudication["identity"]["candidate_hash"], candidate_hash)
        self.assertEqual(self.econ_ref["candidate_hash"], candidate_hash)
        self.assertEqual(self.readiness_ref["candidate_hash"], candidate_hash)
        self.assertEqual(self.handoff["candidate_hash"], candidate_hash)
        validate_scientific_economic_handoff(
            self.handoff, self.adjudication, self.econ_ref, self.readiness_ref
        )

    def test_scientific_promotion_does_not_create_economic_identity_or_profitability(self):
        self.assertFalse(self.adjudication["economic_identity_created"])
        self.assertEqual(self.adjudication["profitability_status"], "UNKNOWN")
        self.assertFalse(self.handoff["scientific_result_is_profitability"])
        self.assertFalse(self.handoff["economic_readiness_is_profitability"])

    def test_complete_w1_structural_map_reaches_d0_ready_without_opening_authority(self):
        self.assertEqual(self.econ_ref["identity_readiness_status"], "QUALIFIED_CURRENT")
        self.assertEqual(self.readiness_ref["structural_mapping_status"], "QUALIFIED_CURRENT")
        self.assertEqual(self.readiness_ref["pre_outcome_decision_status"], "QUALIFIED_CURRENT")
        contract = create_d0_shadow_from_scientific_handoff(
            self.handoff,
            self.adjudication,
            self.econ_ref,
            self.readiness_ref,
            prospective_start_boundary="2026-11-01T00:00:00Z",
            implementation_version="impl-seam-v1",
            review_policy=review_policy(),
        )
        validate_shadow_contract(contract)
        self.assertEqual(contract["initial_lifecycle_state"], "SHADOW_READY_AWAITING_AUTHORITY")
        self.assertEqual(contract["profitability_status"], "UNKNOWN")
        self.assertFalse(contract["prospective_observation_authorized"])
        self.assertFalse(contract["real_capital_authorized"])
        self.assertFalse(contract["live_trading_authorized"])
        self.assertFalse(contract["outcome_accessed"])
        metadata = contract["immutable_core"]["metadata"]
        self.assertEqual(metadata["scientific_adjudication_hash"], self.adjudication["adjudication_hash"])
        self.assertEqual(metadata["scientific_economic_handoff_hash"], self.handoff["handoff_hash"])

    def test_candidate_hash_mismatch_is_fail_closed(self):
        other_ref = bind_economic_identity_ref(self.identity_b)
        with self.assertRaisesRegex(ValueError, "binding mismatch"):
            bind_scientific_economic_handoff(
                self.adjudication,
                other_ref,
                bind_portfolio_readiness_ref(self.diagnostics, other_ref),
            )

    def test_non_promote_scientific_state_cannot_cross_seam(self):
        blocked = deepcopy(self.adjudication)
        blocked["verdict"] = "BLOCK"
        blocked["scientific_posture"] = "BLOCKED"
        blocked["promotion_target"] = None
        blocked["reason_codes"] = ["FIXTURE_BLOCK"]
        blocked["adjudication_hash"] = sha256_json({k: v for k, v in blocked.items() if k != "adjudication_hash"})
        with self.assertRaisesRegex(ValueError, "not promotable"):
            bind_scientific_economic_handoff(blocked, self.econ_ref, self.readiness_ref)

    def test_handoff_tamper_is_detected(self):
        bad = deepcopy(self.handoff)
        bad["claim_ceiling"] = "EXPANDED_AFTER_ADJUDICATION"
        with self.assertRaises(ValueError):
            validate_scientific_economic_handoff(
                bad, self.adjudication, self.econ_ref, self.readiness_ref
            )

    def test_shadow_metadata_cannot_override_canonical_scientific_lineage(self):
        with self.assertRaisesRegex(ValueError, "may not override canonical lineage"):
            create_d0_shadow_from_scientific_handoff(
                self.handoff,
                self.adjudication,
                self.econ_ref,
                self.readiness_ref,
                prospective_start_boundary="2026-11-01T00:00:00Z",
                implementation_version="impl-seam-v1",
                review_policy=review_policy(),
                metadata={"scientific_adjudication_hash": "0" * 64},
            )

    def test_raw_outcome_metadata_is_rejected_by_d0_at_the_seam(self):
        with self.assertRaisesRegex(ValueError, "outcome-bearing"):
            create_d0_shadow_from_scientific_handoff(
                self.handoff,
                self.adjudication,
                self.econ_ref,
                self.readiness_ref,
                prospective_start_boundary="2026-11-01T00:00:00Z",
                implementation_version="impl-seam-v1",
                review_policy=review_policy(),
                metadata={"nested": {"return_series": [0.01]}},
            )


if __name__ == "__main__":
    unittest.main()
