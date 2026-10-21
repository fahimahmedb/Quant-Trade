from __future__ import annotations

from copy import deepcopy
import unittest

from research.research_os.scientific_store import sha256_json
from research.research_os.expansion.portfolio_v2 import portfolio_diagnostics_v2
from research.research_os.expansion.economic_lifecycle import (
    AUTHORITY_STATE,
    WAVE2_IMMUTABLE_BASE_SHA,
    apply_review_decision,
    authority_state,
    bind_economic_identity_ref,
    bind_portfolio_readiness_ref,
    build_replacement_lineage,
    classify_review_evidence,
    create_shadow_contract,
    decay_evidence_contract,
    initial_lifecycle_state,
    lifecycle_contract_summary,
    review_decision,
    validate_decay_evidence_ref,
    validate_economic_identity_ref,
    validate_lifecycle_state,
    validate_portfolio_readiness_ref,
    validate_shadow_contract,
)


def _identity(hid: str, generation: str, suffix: str):
    candidate = {
        "hypothesis_id": hid,
        "generation_id": generation,
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
    }
    candidate_hash = sha256_json(candidate)
    return {
        "hypothesis_id": hid,
        "generation_id": generation,
        "mechanism": candidate["mechanism"],
        "payer": candidate["payer"],
        "forced_constrained_actor": candidate["forced_constrained_actor"],
        "instrument": candidate["instrument"],
        "universe": candidate["universe"],
        "timing_clock": candidate["timing_clock"],
        "horizon": candidate["horizon"],
        "capacity_bottleneck": candidate["capacity_bottleneck"],
        "cost_structure": candidate["cost_structure"],
        "economic_exposure": candidate["economic_exposure"],
        "event_rule_dependency": candidate["event_rule_dependency"],
        "source_identity": candidate["source_identity"],
        "candidate_binding": {
            "hypothesis_id": hid,
            "generation_id": generation,
            "candidate_hash": candidate_hash,
        },
        "candidate_snapshot": deepcopy(candidate),
        "identity_provenance": {
            "candidate_hash": candidate_hash,
            "candidate_binding": {
                "hypothesis_id": hid,
                "generation_id": generation,
                "candidate_hash": candidate_hash,
            },
            "source_hash": sha256_json({"source": suffix}),
            "dossier_hash": "UNKNOWN",
            "source_refs": [],
        },
    }


def _policy():
    return {
        "policy_id": "D0-REVIEW",
        "policy_version": "v1",
        "cadence_kind": "HYBRID",
        "review_interval": 30,
        "minimum_admissible_observations": 20,
        "minimum_distinct_review_windows": 2,
        "regime_context_required": True,
        "implementation_context_required": True,
        "cost_capacity_context_required": True,
    }


def _evidence_ref(contract, kind, *, admissibility="ADMISSIBLE_EXTERNAL_EVALUATOR", observations=20, windows=2):
    payload = {
        "schema_version": "qualified-decay-evidence-ref-v1",
        "evidence_ref_id": f"FIXTURE-{kind}",
        "evidence_kind": kind,
        "admissibility": admissibility,
        "observation_identity": contract["observation_identity"],
        "evaluation_protocol_hash": sha256_json({"protocol": "external-review-v1"}),
        "evidence_hash": sha256_json({"opaque": kind, "fixture_only": True}),
        "review_window_count": windows,
        "admissible_observation_count": observations,
        "reason_codes": [f"FIXTURE_{kind}"],
        "scope": "EXACT_OBSERVATION_IDENTITY_ONLY",
        "outcome_accessed_by_d0": False,
        "raw_outcomes_included": False,
    }
    payload["ref_hash"] = sha256_json(payload)
    return payload


class MegaD0EconomicLifecycleContracts(unittest.TestCase):
    def setUp(self):
        self.identity_a = _identity("H-D0-A", "G1", "a")
        self.identity_b = _identity("H-D0-B", "G1", "b")
        self.diagnostics = portfolio_diagnostics_v2([self.identity_a, self.identity_b])
        self.econ_ref = bind_economic_identity_ref(self.identity_a)
        self.readiness_ref = bind_portfolio_readiness_ref(self.diagnostics, self.econ_ref)
        self.contract = create_shadow_contract(
            self.econ_ref,
            self.readiness_ref,
            prospective_start_boundary="2026-11-01T00:00:00Z",
            implementation_version="impl-fixture-v1",
            review_policy=_policy(),
            metadata={"purpose": "contract-only-fixture"},
        )

    def test_authority_membrane_is_closed_and_copy_only(self):
        observed = authority_state()
        self.assertEqual(observed, AUTHORITY_STATE)
        self.assertTrue(all(value is False for value in observed.values()))
        observed["real_capital_authorized"] = True
        self.assertFalse(authority_state()["real_capital_authorized"])

    def test_economic_identity_ref_is_exact_and_tamper_evident(self):
        self.assertEqual(self.econ_ref["wave2_base_sha"], WAVE2_IMMUTABLE_BASE_SHA)
        validate_economic_identity_ref(self.econ_ref)
        tampered = deepcopy(self.econ_ref)
        tampered["generation_id"] = "G2"
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            validate_economic_identity_ref(tampered)

    def test_portfolio_readiness_ref_consumes_canonical_sealed_boundary(self):
        validate_portfolio_readiness_ref(self.readiness_ref, self.econ_ref)
        self.assertEqual(self.readiness_ref["empirical_layer_status"], "SEALED_BY_AUTHORITY")
        self.assertFalse(self.readiness_ref["return_series_consumed"])
        self.assertEqual(self.readiness_ref["pre_outcome_decision_status"], "QUALIFIED_CURRENT")

    def test_portfolio_readiness_cannot_reopen_authority(self):
        bad = deepcopy(self.diagnostics)
        bad["real_capital_authorized"] = True
        with self.assertRaisesRegex(ValueError, "real_capital_authorized"):
            bind_portfolio_readiness_ref(bad, self.econ_ref)

    def test_shadow_contract_is_pre_outcome_and_not_profitability(self):
        validate_shadow_contract(self.contract)
        self.assertEqual(self.contract["initial_lifecycle_state"], "SHADOW_READY_AWAITING_AUTHORITY")
        self.assertEqual(self.contract["profitability_status"], "UNKNOWN")
        self.assertFalse(self.contract["shadow_status_implies_profitability"])
        self.assertFalse(self.contract["observation_started"])
        self.assertEqual(self.contract["future_observations_consumed"], 0)
        self.assertFalse(self.contract["prospective_observation_authorized"])
        self.assertFalse(self.contract["real_capital_authorized"])
        self.assertFalse(self.contract["live_trading_authorized"])
        self.assertFalse(self.contract["outcome_accessed"])

    def test_outcome_bearing_metadata_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "outcome-bearing"):
            create_shadow_contract(
                self.econ_ref,
                self.readiness_ref,
                prospective_start_boundary="2026-11-01T00:00:00Z",
                implementation_version="impl-fixture-v1",
                review_policy=_policy(),
                metadata={"pnl": 123.0},
            )

    def test_material_change_produces_new_contract_and_observation_identity(self):
        changed = create_shadow_contract(
            self.econ_ref,
            self.readiness_ref,
            prospective_start_boundary="2026-11-01T00:00:00Z",
            implementation_version="impl-fixture-v2",
            review_policy=_policy(),
        )
        self.assertNotEqual(changed["contract_id"], self.contract["contract_id"])
        self.assertNotEqual(changed["observation_identity"], self.contract["observation_identity"])

    def test_retrospective_core_rewrite_is_detected(self):
        tampered = deepcopy(self.contract)
        tampered["immutable_core"]["prospective_start_boundary"] = "2026-10-01T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "immutable core hash mismatch"):
            validate_shadow_contract(tampered)

    def test_review_policy_is_metadata_not_scheduler(self):
        evidence_contract = decay_evidence_contract(_policy())
        self.assertTrue(evidence_contract["external_evaluator_required"])
        self.assertFalse(evidence_contract["raw_outcomes_accepted_by_d0"])
        self.assertFalse(self.contract["scheduler_owned_by_d0"])
        self.assertFalse(self.contract["runtime_owned_by_d0"])

    def test_no_evidence_is_insufficient_not_negative(self):
        result = classify_review_evidence(self.contract)
        self.assertEqual(result["status"], "INSUFFICIENT_EVIDENCE")
        self.assertFalse(result["decay_claim_supported"])
        self.assertFalse(result["negative_claim_supported"])
        self.assertIn("PARK", result["eligible_actions"])
        self.assertNotIn("RETIRE", result["eligible_actions"])

    def test_regime_mismatch_is_not_decay(self):
        result = classify_review_evidence(self.contract, _evidence_ref(self.contract, "REGIME_MISMATCH"))
        self.assertEqual(result["status"], "REGIME_MISMATCH")
        self.assertFalse(result["decay_claim_supported"])
        self.assertFalse(result["negative_claim_supported"])

    def test_implementation_degradation_is_distinct_from_edge_decay(self):
        result = classify_review_evidence(self.contract, _evidence_ref(self.contract, "IMPLEMENTATION_DEGRADATION"))
        self.assertEqual(result["status"], "IMPLEMENTATION_DEGRADATION")
        self.assertFalse(result["decay_claim_supported"])
        self.assertIn("RESIZE_ELIGIBLE", result["eligible_actions"])
        self.assertIn("REPLACE", result["eligible_actions"])

    def test_cost_capacity_deterioration_is_distinct_from_edge_decay(self):
        result = classify_review_evidence(self.contract, _evidence_ref(self.contract, "COST_CAPACITY_DETERIORATION"))
        self.assertEqual(result["status"], "COST_CAPACITY_DETERIORATION")
        self.assertFalse(result["decay_claim_supported"])

    def test_edge_decay_requires_admissibility_and_minimum_evidence(self):
        insufficient = _evidence_ref(self.contract, "EDGE_DECAY", observations=19, windows=2)
        result = classify_review_evidence(self.contract, insufficient)
        self.assertEqual(result["status"], "INSUFFICIENT_EVIDENCE")
        self.assertFalse(result["decay_claim_supported"])
        admissible = _evidence_ref(self.contract, "EDGE_DECAY", observations=20, windows=2)
        result = classify_review_evidence(self.contract, admissible)
        self.assertEqual(result["status"], "DECAY_EVIDENCE_ADMISSIBLE")
        self.assertTrue(result["decay_claim_supported"])
        self.assertTrue(result["negative_claim_supported"])
        self.assertFalse(result["outcome_accessed"])

    def test_evidence_ref_must_bind_exact_observation_identity(self):
        evidence = _evidence_ref(self.contract, "EDGE_DECAY")
        evidence["observation_identity"] = "0" * 64
        evidence["ref_hash"] = sha256_json({k: v for k, v in evidence.items() if k != "ref_hash"})
        with self.assertRaisesRegex(ValueError, "exact observation identity"):
            validate_decay_evidence_ref(evidence, self.contract)

    def test_raw_outcomes_cannot_enter_evidence_ref(self):
        evidence = _evidence_ref(self.contract, "EDGE_DECAY")
        evidence["raw_outcomes_included"] = True
        evidence["ref_hash"] = sha256_json({k: v for k, v in evidence.items() if k != "ref_hash"})
        with self.assertRaisesRegex(ValueError, "raw outcomes"):
            validate_decay_evidence_ref(evidence, self.contract)

    def test_resize_eligible_does_not_authorize_sizing_or_capital(self):
        decision = review_decision(
            self.contract,
            requested_disposition="RESIZE_ELIGIBLE",
            evidence_ref=_evidence_ref(self.contract, "COST_CAPACITY_DETERIORATION"),
        )
        self.assertTrue(decision["resize_eligibility_only"])
        self.assertFalse(decision["position_sizing_authorized"])
        self.assertFalse(decision["capital_allocation_authorized"])
        self.assertFalse(decision["real_capital_authorized"])
        self.assertFalse(decision["live_trading_authorized"])

    def test_park_on_insufficient_evidence_is_not_failure_or_negative(self):
        state = initial_lifecycle_state(self.contract)
        decision = review_decision(self.contract, requested_disposition="PARK")
        updated = apply_review_decision(state, self.contract, decision)
        self.assertEqual(updated["current_state"], "PARKED")
        self.assertEqual(updated["decay_claim_status"], "NOT_CLAIMED")
        self.assertFalse(decision["negative_claim"])
        validate_lifecycle_state(updated, self.contract)

    def test_retire_requires_supported_evidence_class(self):
        with self.assertRaisesRegex(ValueError, "not supported"):
            review_decision(self.contract, requested_disposition="RETIRE")
        decision = review_decision(
            self.contract,
            requested_disposition="RETIRE",
            evidence_ref=_evidence_ref(self.contract, "IMPLEMENTATION_DEGRADATION"),
        )
        state = apply_review_decision(initial_lifecycle_state(self.contract), self.contract, decision)
        self.assertEqual(state["current_state"], "RETIRED")
        self.assertEqual(state["decay_claim_status"], "NOT_CLAIMED")

    def test_edge_decay_retirement_records_external_decay_claim_only(self):
        decision = review_decision(
            self.contract,
            requested_disposition="RETIRE",
            evidence_ref=_evidence_ref(self.contract, "EDGE_DECAY"),
        )
        self.assertTrue(decision["decay_claim"])
        state = apply_review_decision(initial_lifecycle_state(self.contract), self.contract, decision)
        self.assertEqual(state["decay_claim_status"], "SUPPORTED_BY_EXTERNAL_ADMISSIBLE_EVIDENCE")
        self.assertFalse(state["outcome_accessed"])

    def test_transition_history_is_append_only_hash_chained(self):
        state = initial_lifecycle_state(self.contract)
        parked = apply_review_decision(state, self.contract, review_decision(self.contract, requested_disposition="PARK"))
        held = apply_review_decision(parked, self.contract, review_decision(self.contract, requested_disposition="HOLD"))
        self.assertEqual(len(held["transition_history"]), 2)
        self.assertEqual(held["transition_history"][1]["previous_event_hash"], held["transition_history"][0]["event_hash"])
        validate_lifecycle_state(held, self.contract)

    def test_state_tampering_is_detected(self):
        state = initial_lifecycle_state(self.contract)
        state["profitability_status"] = "PROFITABLE"
        with self.assertRaisesRegex(ValueError, "infer profitability"):
            validate_lifecycle_state(state, self.contract)

    def test_replacement_lineage_preserves_predecessor_and_bounded_negative_scope(self):
        successor_identity = _identity("H-D0-C", "G1", "c")
        successor_diagnostics = portfolio_diagnostics_v2([successor_identity, self.identity_b])
        successor_econ = bind_economic_identity_ref(successor_identity)
        successor_ready = bind_portfolio_readiness_ref(successor_diagnostics, successor_econ)
        lineage = build_replacement_lineage(
            self.contract,
            successor_econ,
            successor_ready,
            replacement_kind="NEW_MECHANISM",
            reason="mechanism replacement fixture",
            blocker_or_evidence_class="FIXTURE_BLOCKER",
            negative_knowledge_scope="PREDECESSOR_IDENTITY_ONLY",
        )
        self.assertEqual(lineage["predecessor_contract_id"], self.contract["contract_id"])
        self.assertEqual(lineage["predecessor_identity_hash"], self.econ_ref["identity_hash"])
        self.assertEqual(lineage["successor_identity_hash"], successor_econ["identity_hash"])
        self.assertFalse(lineage["negative_knowledge_global"])
        self.assertFalse(lineage["automatic_negative_knowledge_transfer"])
        self.assertFalse(lineage["outcome_accessed"])

    def test_replacement_rejects_exact_same_identity(self):
        with self.assertRaisesRegex(ValueError, "exact predecessor identity"):
            build_replacement_lineage(
                self.contract,
                self.econ_ref,
                self.readiness_ref,
                replacement_kind="IMPLEMENTATION_REVISION",
                reason="invalid exact replay",
                blocker_or_evidence_class="FIXTURE_BLOCKER",
            )

    def test_replacement_negative_scope_cannot_be_global(self):
        successor_identity = _identity("H-D0-C", "G1", "c")
        successor_diagnostics = portfolio_diagnostics_v2([successor_identity, self.identity_b])
        successor_econ = bind_economic_identity_ref(successor_identity)
        successor_ready = bind_portfolio_readiness_ref(successor_diagnostics, successor_econ)
        with self.assertRaisesRegex(ValueError, "explicit and bounded"):
            build_replacement_lineage(
                self.contract,
                successor_econ,
                successor_ready,
                replacement_kind="NEW_WRAPPER",
                reason="wrapper fixture",
                blocker_or_evidence_class="FIXTURE_BLOCKER",
                negative_knowledge_scope="GLOBAL",
            )

    def test_summary_remains_narrow_and_outcome_blind(self):
        summary = lifecycle_contract_summary(self.contract)
        self.assertEqual(summary["profitability_status"], "UNKNOWN")
        self.assertFalse(summary["shadow_status_implies_profitability"])
        self.assertFalse(summary["outcome_accessed"])
        self.assertFalse(summary["prospective_observation_authorized"])
        self.assertFalse(summary["real_capital_authorized"])
        self.assertFalse(summary["live_trading_authorized"])


if __name__ == "__main__":
    unittest.main()
