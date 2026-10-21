from copy import deepcopy
import unittest

from research.research_os.expansion.economic_lifecycle_v1 import (
    AUTHORITY_CLOSED,
    EconomicLifecycleError,
    apply_review,
    assert_contract_invariants,
    build_economic_identity_ref,
    build_portfolio_readiness_ref,
    classify_decay_evidence,
    create_shadow_contract,
    rebind_material_change,
    request_self_authorization,
    supersede_with_replacement,
)


def structural(hypothesis="H1", generation="G1", suffix="a"):
    return {
        "hypothesis_id": hypothesis,
        "generation_id": generation,
        "identity_hash": (suffix * 64)[:64],
        "candidate_binding": {"status": "BOUND", "candidate_hash": ((suffix + "c") * 64)[:64]},
        "identity_readiness": {"status": "QUALIFIED_CURRENT", "blockers": []},
        "fields": {"payer": {"status": "KNOWN", "value": "payer"}},
    }


def portfolio(clear=True, unknown=False):
    status = "QUALIFIED_CURRENT" if clear else "PARTIAL_WITH_EXPLICIT_BLOCKER"
    blockers = [] if clear else (["RELATIONSHIP_UNKNOWN"] if unknown else ["SAME_EXPOSURE_REVIEW_REQUIRED"])
    return {
        "portfolio_engine": "portfolio-diagnostics.v2",
        "portfolio_readiness": {
            "structural_mapping": {"status": status, "blockers": list(blockers)},
            "pre_outcome_decision": {"status": status, "blockers": list(blockers)},
            "empirical_layer": {
                "status": "SEALED_BY_AUTHORITY",
                "blockers": ["NO_ADMISSIBLE_RETURN_SERIES_CONSUMED"],
            },
        },
        "return_series_consumed": False,
        "economic_experiment_authorized": False,
        "prospective_observation_authorized": False,
        "capital_allocation_authorized": False,
        "position_sizing_authorized": False,
        "orders_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
        "portfolio_optimization_authorized": False,
    }


def contract(clear=True):
    return create_shadow_contract(
        structural(), portfolio(clear=clear), protocol_ref="PROTO-001",
        review_policy={"cadence": "every-20-qualified-observations"},
    )


def evidence(c, disposition="CONTINUE", klass="MECHANISM", **extra):
    value = {
        "evidence_id": f"EVID-{disposition}",
        "evidence_hash": (disposition.lower() + "f" * 64)[:64],
        "lifecycle_contract_id": c["contract_id"],
        "prospective_identity_hash": c["prospective_observation_identity"]["identity_hash"],
        "evidence_class": klass,
        "scientific_disposition": disposition,
        "observed_under_authority": True,
        "authority_receipt_ref": "OWNER-AUTH-RECEIPT-001",
        "source_refs": ["evidence://qualified/reference/1"],
        "outcome_payload_included": False,
        "negative_knowledge": [],
    }
    value.update(extra)
    return value


class EconomicLifecycleV1Tests(unittest.TestCase):
    def test_exact_refs_are_bound_without_recomputing_w1_economics(self):
        identity = structural()
        diagnostics = portfolio()
        iref = build_economic_identity_ref(identity)
        pref = build_portfolio_readiness_ref(diagnostics)
        self.assertEqual(iref["identity_hash"], identity["identity_hash"])
        self.assertEqual(iref["candidate_hash"], identity["candidate_binding"]["candidate_hash"])
        self.assertTrue(pref["current_clearance"])
        self.assertEqual(pref["empirical_layer_status"], "SEALED_BY_AUTHORITY")

    def test_contract_is_deterministic_immutable_identity_and_authority_closed(self):
        a = contract()
        b = contract()
        self.assertEqual(a, b)
        self.assertEqual(a["state"], "READY_AWAITING_OWNER_AUTHORITY")
        self.assertEqual(a["authority"], AUTHORITY_CLOSED)
        self.assertFalse(a["outcome_accessed"])
        self.assertEqual(a["economic_result"], "NOT_OBSERVED")
        self.assertFalse(a["prospective_observation_identity"]["observation_started"])
        self.assertEqual(a["prospective_observation_identity"]["future_outcomes_consumed"], 0)
        self.assertEqual(a["prospective_observation_identity"]["start_boundary"], "UNBOUND_UNTIL_EXTERNAL_AUTHORITY")
        self.assertFalse(a["review_policy"]["scheduler_owned"])
        assert_contract_invariants(a)

    def test_blocked_upstream_is_blocked_not_failed_and_unknown_is_preserved(self):
        c = create_shadow_contract(structural(), portfolio(clear=False, unknown=True), protocol_ref="PROTO-001")
        self.assertEqual(c["state"], "BLOCKED_BY_UPSTREAM_READINESS")
        self.assertEqual(c["status_class"], "BLOCKED")
        self.assertNotEqual(c["status_class"], "FAILED")
        self.assertIn("RELATIONSHIP_UNKNOWN", c["portfolio_readiness_ref"]["upstream_blockers"])
        self.assertTrue(c["semantic_guards"]["unknown_preserved"])

    def test_self_authorization_is_impossible(self):
        c = contract()
        with self.assertRaises(PermissionError):
            request_self_authorization(c, prospective_observation_authorized=True)
        tampered = deepcopy(c)
        tampered["authority"]["prospective_observation_authorized"] = True
        with self.assertRaises(EconomicLifecycleError):
            assert_contract_invariants(tampered)

    def test_raw_outcome_payload_is_rejected_without_access(self):
        c = contract()
        e = evidence(c, pnl=123.0, return_series=[0.1, -0.2])
        r = classify_decay_evidence(c, e)
        self.assertEqual(r["status"], "BLOCKED")
        self.assertEqual(r["reason"], "RAW_OUTCOME_PAYLOAD_FORBIDDEN")
        self.assertFalse(r["outcome_accessed"])
        self.assertEqual(r["decay_conclusion"], "UNKNOWN")

    def test_missing_or_wrong_evidence_stays_unknown_or_blocked_not_negative(self):
        c = contract()
        missing = classify_decay_evidence(c, None)
        self.assertEqual(missing["status"], "UNKNOWN")
        self.assertEqual(missing["decay_conclusion"], "UNKNOWN")
        wrong = evidence(c)
        wrong["prospective_identity_hash"] = "wrong"
        r = classify_decay_evidence(c, wrong)
        self.assertEqual(r["status"], "BLOCKED")
        self.assertIn("PROSPECTIVE_IDENTITY_BINDING_MISMATCH", r["blockers"])

    def test_admissible_reference_is_metadata_only_not_a_decay_computation(self):
        c = contract()
        r = classify_decay_evidence(c, evidence(c, "RETIRE", "IMPLEMENTATION"))
        self.assertEqual(r["status"], "ADMISSIBLE_REFERENCE_ONLY")
        self.assertEqual(r["scientific_disposition"], "RETIRE")
        self.assertEqual(r["decay_conclusion"], "NOT_COMPUTED_BY_D0")
        self.assertFalse(r["outcome_accessed"])

    def test_review_state_machine_is_bounded_and_resize_never_grants_sizing(self):
        expected = {
            "CONTINUE": "READY_AWAITING_OWNER_AUTHORITY",
            "RESIZE": "RESIZE_ELIGIBLE",
            "PARK": "PARKED",
            "RETIRE": "RETIRED",
            "REPLACE": "REPLACEMENT_REQUIRED",
            "INCONCLUSIVE": "REVIEW_REQUIRED",
        }
        for disposition, state in expected.items():
            with self.subTest(disposition=disposition):
                c = contract()
                r = apply_review(c, evidence(c, disposition))
                self.assertEqual(r["state"], state)
                self.assertEqual(r["authority"], AUTHORITY_CLOSED)
                self.assertFalse(r["outcome_accessed"])
                self.assertFalse(r["authority"]["position_sizing_authorized"])
                self.assertFalse(r["authority"]["real_capital_authorized"])

    def test_continue_or_resize_cannot_bypass_upstream_portfolio_blocker(self):
        c = create_shadow_contract(structural(), portfolio(clear=False), protocol_ref="PROTO-001")
        for disposition in ("CONTINUE", "RESIZE"):
            r = apply_review(c, evidence(c, disposition))
            self.assertEqual(r["state"], "BLOCKED_BY_UPSTREAM_READINESS")
            self.assertEqual(r["status_class"], "BLOCKED")

    def test_negative_knowledge_must_be_explicitly_scoped_and_non_global(self):
        c = contract()
        bad = evidence(c, "PARK", negative_knowledge=[{
            "knowledge_id": "K1", "scope_kind": "MECHANISM", "global": True,
        }])
        r = classify_decay_evidence(c, bad)
        self.assertEqual(r["status"], "BLOCKED")
        self.assertIn("GLOBAL_NEGATIVE_KNOWLEDGE_FORBIDDEN", r["blockers"])

    def test_material_change_creates_new_version_and_observation_identity(self):
        c = contract()
        r = rebind_material_change(
            c, protocol_ref="PROTO-002", change_class="IMPLEMENTATION", reason_ref="CHANGE-001"
        )
        s = r["successor"]
        self.assertEqual(s["lifecycle_version"], c["lifecycle_version"] + 1)
        self.assertNotEqual(
            s["prospective_observation_identity"]["identity_hash"],
            c["prospective_observation_identity"]["identity_hash"],
        )
        self.assertEqual(s["lineage"]["predecessor_contract_id"], c["contract_id"])
        self.assertEqual(s["authority"], AUTHORITY_CLOSED)
        with self.assertRaises(EconomicLifecycleError):
            rebind_material_change(c, protocol_ref="PROTO-001", change_class="IMPLEMENTATION", reason_ref="CHANGE-001")

    def test_replacement_preserves_lineage_and_only_applicable_negative_knowledge(self):
        c = contract()
        replace_ref = evidence(c, "REPLACE", "IMPLEMENTATION", negative_knowledge=[
            {"knowledge_id": "K-IMPL", "scope_kind": "IMPLEMENTATION", "global": False},
            {"knowledge_id": "K-MECH", "scope_kind": "MECHANISM", "global": False},
        ])
        predecessor = apply_review(c, replace_ref)
        self.assertEqual(predecessor["state"], "REPLACEMENT_REQUIRED")
        out = supersede_with_replacement(
            predecessor,
            structural(hypothesis="H1", generation="G2", suffix="b"),
            portfolio(),
            successor_protocol_ref="PROTO-002",
            reason_ref="REPLACE-001",
            distinction="IMPLEMENTATION",
            trigger_evidence_ref=replace_ref,
        )
        self.assertEqual(out["predecessor"]["state"], "SUPERSEDED")
        self.assertEqual(out["successor"]["lineage"]["predecessor_contract_id"], predecessor["contract_id"])
        self.assertEqual(out["lineage"]["mechanism_wrapper_implementation_distinction"], "IMPLEMENTATION")
        self.assertEqual(out["lineage"]["transferred_negative_knowledge_ids"], ["K-IMPL"])
        self.assertEqual(out["lineage"]["withheld_negative_knowledge_ids"], ["K-MECH"])
        self.assertFalse(out["lineage"]["global_negative_knowledge_transfer"])
        self.assertNotEqual(
            out["successor"]["prospective_observation_identity"]["identity_hash"],
            predecessor["prospective_observation_identity"]["identity_hash"],
        )
        self.assertEqual(out["successor"]["authority"], AUTHORITY_CLOSED)

    def test_replacement_cannot_be_cosmetic_reuse_of_same_identity_and_protocol(self):
        c = contract()
        ref = evidence(c, "REPLACE", "WRAPPER")
        predecessor = apply_review(c, ref)
        with self.assertRaises(EconomicLifecycleError):
            supersede_with_replacement(
                predecessor, structural(), portfolio(), successor_protocol_ref="PROTO-001",
                reason_ref="REPLACE-COSMETIC", distinction="WRAPPER", trigger_evidence_ref=ref,
            )

    def test_terminal_state_cannot_be_reopened_by_review(self):
        c = contract()
        retired = apply_review(c, evidence(c, "RETIRE"))
        with self.assertRaises(EconomicLifecycleError):
            apply_review(retired, evidence(retired, "CONTINUE"))


if __name__ == "__main__":
    unittest.main()
