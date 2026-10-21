from __future__ import annotations

from copy import deepcopy
import unittest

from research.research_os.scientific_store import sha256_json
from research.research_os.expansion.portfolio_v2 import portfolio_diagnostics_v2
from research.research_os.expansion.economic_lifecycle import (
    AUTHORITY_STATE, WAVE2_IMMUTABLE_BASE_SHA,
    apply_review_decision, authority_state, bind_economic_identity_ref,
    bind_portfolio_readiness_ref, build_replacement_lineage,
    classify_review_evidence, create_shadow_contract, decay_evidence_contract,
    initial_lifecycle_state, lifecycle_contract_summary, review_decision,
    shadow_book_state, validate_decay_evidence_ref, validate_economic_identity_ref,
    validate_lifecycle_state, validate_portfolio_readiness_ref,
    validate_shadow_contract,
)


def identity(hid: str, suffix: str):
    candidate = {
        "hypothesis_id": hid, "generation_id": "G1",
        "mechanism": f"mechanism-{suffix}", "payer": f"payer-{suffix}",
        "forced_constrained_actor": f"actor-{suffix}",
        "instrument": f"instrument-{suffix}", "universe": f"universe-{suffix}",
        "timing_clock": f"clock-{suffix}", "horizon": f"horizon-{suffix}",
        "capacity_bottleneck": f"capacity-{suffix}",
        "cost_structure": f"cost-{suffix}",
        "economic_exposure": f"exposure-{suffix}",
        "event_rule_dependency": f"rule-{suffix}",
        "source_identity": f"source-{suffix}", "economic_tags": [f"tag-{suffix}"],
    }
    ch = sha256_json(candidate)
    out = deepcopy(candidate)
    out.update(
        candidate_binding={"hypothesis_id": hid, "generation_id": "G1", "candidate_hash": ch},
        candidate_snapshot=deepcopy(candidate),
        identity_provenance={
            "candidate_hash": ch,
            "candidate_binding": {"hypothesis_id": hid, "generation_id": "G1", "candidate_hash": ch},
            "source_hash": sha256_json({"source": suffix}),
            "dossier_hash": "UNKNOWN", "source_refs": [],
        },
    )
    return out


def policy():
    return {
        "policy_id": "D0-REVIEW", "policy_version": "v1", "cadence_kind": "HYBRID",
        "review_interval": 30, "minimum_admissible_observations": 20,
        "minimum_distinct_review_windows": 2, "regime_context_required": True,
        "implementation_context_required": True, "cost_capacity_context_required": True,
    }


def evidence(contract, kind, observations=20, windows=2, admissibility="ADMISSIBLE_EXTERNAL_EVALUATOR"):
    ref = {
        "schema_version": "qualified-decay-evidence-ref-v1",
        "evidence_ref_id": f"FIXTURE-{kind}", "evidence_kind": kind,
        "admissibility": admissibility,
        "observation_identity": contract["observation_identity"],
        "evaluation_protocol_hash": sha256_json({"protocol": "external-v1"}),
        "evidence_hash": sha256_json({"opaque_fixture": kind}),
        "review_window_count": windows, "admissible_observation_count": observations,
        "reason_codes": [f"FIXTURE_{kind}"], "scope": "EXACT_OBSERVATION_IDENTITY_ONLY",
        "evaluator_authority_kind": "GIT_COMMIT_PATH",
        "evaluator_authority_commit_sha": "a" * 40,
        "evaluator_authority_path": "future/external/decay-evaluator.md",
        "issued_by_d0": False, "outcome_accessed_by_d0": False,
        "raw_outcomes_included": False,
    }
    ref["ref_hash"] = sha256_json(ref)
    return ref


class MegaD0EconomicLifecycleContracts(unittest.TestCase):
    def setUp(self):
        self.a, self.b = identity("H-D0-A", "a"), identity("H-D0-B", "b")
        self.diag = portfolio_diagnostics_v2([self.a, self.b])
        self.econ = bind_economic_identity_ref(self.a)
        self.ready = bind_portfolio_readiness_ref(self.diag, self.econ)
        self.contract = create_shadow_contract(
            self.econ, self.ready,
            prospective_start_boundary="2026-11-01T00:00:00Z",
            implementation_version="impl-v1", review_policy=policy(),
            metadata={"purpose": "contract-only-fixture"},
        )

    def test_authority_membrane_is_immutable(self):
        self.assertTrue(all(v is False for v in authority_state().values()))
        with self.assertRaises(TypeError):
            AUTHORITY_STATE["real_capital_authorized"] = True
        copy = authority_state()
        copy["real_capital_authorized"] = True
        self.assertFalse(authority_state()["real_capital_authorized"])

    def test_identity_ref_is_bound_to_wave2_and_tamper_evident(self):
        self.assertEqual(self.econ["wave2_base_sha"], WAVE2_IMMUTABLE_BASE_SHA)
        validate_economic_identity_ref(self.econ)
        bad = deepcopy(self.econ); bad["generation_id"] = "G2"
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            validate_economic_identity_ref(bad)

    def test_readiness_ref_reuses_sealed_canonical_portfolio(self):
        validate_portfolio_readiness_ref(self.ready, self.econ)
        self.assertEqual(self.ready["empirical_layer_status"], "SEALED_BY_AUTHORITY")
        self.assertFalse(self.ready["return_series_consumed"])
        self.assertEqual(self.ready["pre_outcome_decision_status"], "QUALIFIED_CURRENT")

    def test_readiness_cannot_reopen_authority(self):
        bad = deepcopy(self.diag); bad["real_capital_authorized"] = True
        with self.assertRaisesRegex(ValueError, "real_capital_authorized"):
            bind_portfolio_readiness_ref(bad, self.econ)

    def test_shadow_contract_is_ready_not_profitable(self):
        validate_shadow_contract(self.contract)
        self.assertEqual(self.contract["initial_lifecycle_state"], "SHADOW_READY_AWAITING_AUTHORITY")
        self.assertEqual(self.contract["profitability_status"], "UNKNOWN")
        self.assertFalse(self.contract["shadow_status_implies_profitability"])
        self.assertFalse(self.contract["prospective_observation_authorized"])
        self.assertFalse(self.contract["real_capital_authorized"])
        self.assertFalse(self.contract["live_trading_authorized"])
        self.assertFalse(self.contract["outcome_accessed"])

    def test_shadow_book_is_identity_lifecycle_only(self):
        state = initial_lifecycle_state(self.contract)
        book = shadow_book_state(self.contract, state)
        self.assertEqual(book["book_kind"], "IDENTITY_LIFECYCLE_ONLY_NO_POSITIONS")
        self.assertEqual(book["position_state"], "NOT_OWNED_BY_D0")
        self.assertEqual(book["order_state"], "NOT_OWNED_BY_D0")
        self.assertEqual(book["profitability_status"], "UNKNOWN")
        self.assertFalse(book["outcome_accessed"])

    def test_future_evaluation_is_exactly_bound(self):
        b = self.contract["future_evaluation_binding"]
        self.assertEqual(b["observation_identity"], self.contract["observation_identity"])
        self.assertTrue(b["exact_pre_outcome_state_required"])
        self.assertTrue(b["external_evidence_evaluator_required"])
        self.assertFalse(b["raw_outcomes_accepted_by_d0"])

    def test_outcome_metadata_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "outcome-bearing"):
            create_shadow_contract(
                self.econ, self.ready, prospective_start_boundary="2026-11-01T00:00:00Z",
                implementation_version="impl-v1", review_policy=policy(), metadata={"pnl": 1.0},
            )

    def test_material_change_creates_new_observation_identity(self):
        changed = create_shadow_contract(
            self.econ, self.ready, prospective_start_boundary="2026-11-01T00:00:00Z",
            implementation_version="impl-v2", review_policy=policy(),
        )
        self.assertNotEqual(changed["contract_id"], self.contract["contract_id"])
        self.assertNotEqual(changed["observation_identity"], self.contract["observation_identity"])

    def test_retrospective_rewrite_fails(self):
        bad = deepcopy(self.contract)
        bad["immutable_core"]["prospective_start_boundary"] = "2026-10-01T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "immutable core hash mismatch"):
            validate_shadow_contract(bad)

    def test_review_policy_does_not_own_scheduler(self):
        c = decay_evidence_contract(policy())
        self.assertTrue(c["external_evaluator_required"])
        self.assertTrue(c["immutable_evaluator_authority_required"])
        self.assertFalse(c["raw_outcomes_accepted_by_d0"])
        self.assertFalse(self.contract["scheduler_owned_by_d0"])

    def test_no_evidence_is_insufficient_not_negative(self):
        r = classify_review_evidence(self.contract)
        self.assertEqual(r["status"], "INSUFFICIENT_EVIDENCE")
        self.assertFalse(r["decay_claim_supported"])
        self.assertFalse(r["negative_claim_supported"])
        self.assertNotIn("RETIRE", r["eligible_actions"])

    def test_underpowered_edge_decay_is_not_decay(self):
        r = classify_review_evidence(self.contract, evidence(self.contract, "EDGE_DECAY", observations=19))
        self.assertEqual(r["status"], "INSUFFICIENT_EVIDENCE")
        self.assertFalse(r["decay_claim_supported"])

    def test_regime_mismatch_is_not_decay(self):
        r = classify_review_evidence(self.contract, evidence(self.contract, "REGIME_MISMATCH"))
        self.assertEqual(r["status"], "REGIME_MISMATCH")
        self.assertFalse(r["decay_claim_supported"])

    def test_implementation_degradation_is_not_edge_decay(self):
        r = classify_review_evidence(self.contract, evidence(self.contract, "IMPLEMENTATION_DEGRADATION"))
        self.assertEqual(r["status"], "IMPLEMENTATION_DEGRADATION")
        self.assertFalse(r["decay_claim_supported"])
        self.assertIn("RESIZE_ELIGIBLE", r["eligible_actions"])

    def test_cost_capacity_deterioration_is_not_edge_decay(self):
        r = classify_review_evidence(self.contract, evidence(self.contract, "COST_CAPACITY_DETERIORATION"))
        self.assertEqual(r["status"], "COST_CAPACITY_DETERIORATION")
        self.assertFalse(r["decay_claim_supported"])

    def test_admissible_edge_decay_can_support_scoped_negative_claim(self):
        r = classify_review_evidence(self.contract, evidence(self.contract, "EDGE_DECAY"))
        self.assertEqual(r["status"], "DECAY_EVIDENCE_ADMISSIBLE")
        self.assertTrue(r["decay_claim_supported"])
        self.assertTrue(r["negative_claim_supported"])
        self.assertFalse(r["outcome_accessed"])

    def test_evidence_must_bind_observation_identity(self):
        ref = evidence(self.contract, "EDGE_DECAY")
        ref["observation_identity"] = "0" * 64
        ref["ref_hash"] = sha256_json({k: v for k, v in ref.items() if k != "ref_hash"})
        with self.assertRaisesRegex(ValueError, "exact observation identity"):
            validate_decay_evidence_ref(ref, self.contract)

    def test_d0_cannot_self_issue_evidence(self):
        ref = evidence(self.contract, "EDGE_DECAY")
        ref["issued_by_d0"] = True
        ref["ref_hash"] = sha256_json({k: v for k, v in ref.items() if k != "ref_hash"})
        with self.assertRaisesRegex(ValueError, "may not issue"):
            validate_decay_evidence_ref(ref, self.contract)

    def test_raw_outcomes_cannot_cross_evidence_boundary(self):
        ref = evidence(self.contract, "EDGE_DECAY")
        ref["raw_outcomes_included"] = True
        ref["ref_hash"] = sha256_json({k: v for k, v in ref.items() if k != "ref_hash"})
        with self.assertRaisesRegex(ValueError, "raw outcomes"):
            validate_decay_evidence_ref(ref, self.contract)

    def test_resize_is_eligibility_only(self):
        d = review_decision(
            self.contract, requested_disposition="RESIZE_ELIGIBLE",
            evidence_ref=evidence(self.contract, "COST_CAPACITY_DETERIORATION"),
        )
        self.assertTrue(d["resize_eligibility_only"])
        self.assertFalse(d["position_sizing_authorized"])
        self.assertFalse(d["capital_allocation_authorized"])
        self.assertFalse(d["real_capital_authorized"])

    def test_park_on_insufficient_evidence_is_not_negative(self):
        d = review_decision(self.contract, requested_disposition="PARK")
        state = apply_review_decision(initial_lifecycle_state(self.contract), self.contract, d)
        self.assertEqual(state["current_state"], "PARKED")
        self.assertEqual(state["decay_claim_status"], "NOT_CLAIMED")
        self.assertFalse(d["negative_claim"])

    def test_retire_needs_supported_evidence_class(self):
        with self.assertRaisesRegex(ValueError, "not supported"):
            review_decision(self.contract, requested_disposition="RETIRE")
        d = review_decision(
            self.contract, requested_disposition="RETIRE",
            evidence_ref=evidence(self.contract, "IMPLEMENTATION_DEGRADATION"),
        )
        state = apply_review_decision(initial_lifecycle_state(self.contract), self.contract, d)
        self.assertEqual(state["current_state"], "RETIRED")
        self.assertEqual(state["decay_claim_status"], "NOT_CLAIMED")

    def test_edge_decay_retirement_keeps_d0_outcome_blind(self):
        d = review_decision(
            self.contract, requested_disposition="RETIRE",
            evidence_ref=evidence(self.contract, "EDGE_DECAY"),
        )
        state = apply_review_decision(initial_lifecycle_state(self.contract), self.contract, d)
        self.assertEqual(state["decay_claim_status"], "SUPPORTED_BY_EXTERNAL_ADMISSIBLE_EVIDENCE")
        self.assertFalse(state["outcome_accessed"])

    def test_transition_history_is_hash_chained(self):
        s0 = initial_lifecycle_state(self.contract)
        s1 = apply_review_decision(s0, self.contract, review_decision(self.contract, requested_disposition="PARK"))
        s2 = apply_review_decision(s1, self.contract, review_decision(self.contract, requested_disposition="HOLD"))
        self.assertEqual(s2["transition_history"][1]["previous_event_hash"], s2["transition_history"][0]["event_hash"])
        validate_lifecycle_state(s2, self.contract)

    def test_state_profitability_tamper_fails(self):
        state = initial_lifecycle_state(self.contract); state["profitability_status"] = "PROFITABLE"
        with self.assertRaisesRegex(ValueError, "infer profitability"):
            validate_lifecycle_state(state, self.contract)

    def successor(self):
        c = identity("H-D0-C", "c")
        diag = portfolio_diagnostics_v2([c, self.b])
        ref = bind_economic_identity_ref(c)
        return ref, bind_portfolio_readiness_ref(diag, ref)

    def test_new_mechanism_lineage_preserves_predecessor_and_scope(self):
        ref, ready = self.successor()
        line = build_replacement_lineage(
            self.contract, ref, ready, successor_implementation_version="impl-v2",
            replacement_kind="NEW_MECHANISM", reason="fixture",
            blocker_or_evidence_class="FIXTURE_BLOCKER",
            negative_knowledge_scope="PREDECESSOR_IDENTITY_ONLY",
        )
        self.assertEqual(line["predecessor_identity_hash"], self.econ["identity_hash"])
        self.assertEqual(line["successor_identity_hash"], ref["identity_hash"])
        self.assertFalse(line["negative_knowledge_global"])
        self.assertFalse(line["automatic_negative_knowledge_transfer"])

    def test_implementation_revision_can_keep_economic_identity(self):
        line = build_replacement_lineage(
            self.contract, self.econ, self.ready, successor_implementation_version="impl-v2",
            replacement_kind="IMPLEMENTATION_REVISION", reason="fixture",
            blocker_or_evidence_class="FIXTURE_BLOCKER",
        )
        self.assertFalse(line["economic_identity_changed"])
        self.assertEqual(line["predecessor_implementation_version"], "impl-v1")
        self.assertEqual(line["successor_implementation_version"], "impl-v2")

    def test_implementation_revision_requires_new_version(self):
        with self.assertRaisesRegex(ValueError, "new implementation version"):
            build_replacement_lineage(
                self.contract, self.econ, self.ready, successor_implementation_version="impl-v1",
                replacement_kind="IMPLEMENTATION_REVISION", reason="fixture",
                blocker_or_evidence_class="FIXTURE_BLOCKER",
            )

    def test_new_wrapper_cannot_be_exact_relabel(self):
        with self.assertRaisesRegex(ValueError, "changed economic identity"):
            build_replacement_lineage(
                self.contract, self.econ, self.ready, successor_implementation_version="impl-v2",
                replacement_kind="NEW_WRAPPER", reason="fixture",
                blocker_or_evidence_class="FIXTURE_BLOCKER",
            )

    def test_negative_knowledge_scope_cannot_be_global(self):
        ref, ready = self.successor()
        with self.assertRaisesRegex(ValueError, "explicit and bounded"):
            build_replacement_lineage(
                self.contract, ref, ready, successor_implementation_version="impl-v2",
                replacement_kind="NEW_WRAPPER", reason="fixture",
                blocker_or_evidence_class="FIXTURE_BLOCKER", negative_knowledge_scope="GLOBAL",
            )

    def test_summary_is_narrow_and_outcome_blind(self):
        s = lifecycle_contract_summary(self.contract)
        self.assertEqual(s["shadow_book_kind"], "IDENTITY_LIFECYCLE_ONLY_NO_POSITIONS")
        self.assertEqual(s["profitability_status"], "UNKNOWN")
        self.assertFalse(s["outcome_accessed"])
        self.assertFalse(s["prospective_observation_authorized"])
        self.assertFalse(s["real_capital_authorized"])
        self.assertFalse(s["live_trading_authorized"])


if __name__ == "__main__":
    unittest.main()
