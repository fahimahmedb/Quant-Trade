from __future__ import annotations
import unittest

from research.research_os.multi_source_ideation import (
    BASE_SHA, DeterministicFakeBackend, ProposalLedger, barrier, build_context_snapshot,
    duplicate_check, intake, light_implementability, memory_lineage_check, policy_a,
    policy_b, policy_c, raw_artifact, side_effect_zeroes, source_claim, transition_claim,
)


def snapshot():
    return build_context_snapshot(
        ideation_cycle_id="cycle-1", created_at="2026-10-21T20:00:00Z",
        refs={k: k + ":v1" for k in (
            "memory_snapshot_ref", "ancestry_snapshot_ref", "frontier_snapshot_ref",
            "evidence_snapshot_ref", "source_catalog_snapshot_ref", "capability_snapshot_ref",
            "authority_snapshot_ref", "active_work_snapshot_ref")},
        relevant_schema_versions={"memory": "v1", "frontier": "v1"},
    )


class MultiSourceIdeationV2Tests(unittest.TestCase):
    def test_base_and_snapshot_are_frozen_and_outcome_free(self):
        self.assertEqual(BASE_SHA, "2b99d8aeb8a342f1ef32544247d366cb8a26037e")
        s = snapshot(); self.assertFalse(s["outcome_accessed"]); self.assertEqual(len(s["context_snapshot_hash"]), 64)

    def test_same_cycle_barrier_waits_for_status_not_three_proposals(self):
        s = snapshot(); h = s["context_snapshot_hash"]
        a = raw_artifact(policy_kind="SYSTEMATIC_COVERAGE", status="NO_PROPOSAL", context_snapshot_hash=h)
        b = raw_artifact(policy_kind="INFORMATION_VALUE", status="NO_ACTION", context_snapshot_hash=h)
        self.assertFalse(barrier([a, b], h)["intake_allowed"])
        c = raw_artifact(policy_kind="DIVERGENT_EXPLORATION", status="SOURCE_UNAVAILABLE", context_snapshot_hash=h)
        self.assertTrue(barrier([a, b, c], h)["intake_allowed"])

    def test_cross_context_leakage_is_rejected(self):
        s = snapshot(); h = s["context_snapshot_hash"]
        a = raw_artifact(policy_kind="SYSTEMATIC_COVERAGE", status="NO_PROPOSAL", context_snapshot_hash=h)
        b = raw_artifact(policy_kind="INFORMATION_VALUE", status="NO_ACTION", context_snapshot_hash="other")
        with self.assertRaises(ValueError): barrier([a, b], h)

    def test_frontier_quota_without_unused_qualified_source_emits_no_source(self):
        s = snapshot()
        out = policy_a(snapshot=s, frontier_decision={"action":"GENERATE_MECHANISM","executable":True}, source_plan={"status":"NO_UNUSED_ADMISSIBLE_SOURCE"})
        self.assertEqual(out["status"], "NO_ADMISSIBLE_NOVEL_SOURCE")

    def test_policy_a_direction_is_seed_and_does_not_invent_payer(self):
        s = snapshot()
        out = policy_a(snapshot=s, frontier_decision={"action":"GENERATE_MECHANISM","executable":True,"uncertainty_resolved":"find mechanism"}, source_plan={"status":"SOURCE_SELECTED","source_identity":"sec:abc"})
        self.assertEqual(out["artifact_kind"], "IDEATION_SEED"); self.assertNotIn("payer", out["payload"])

    def test_policy_b_existing_lineage_actions_do_not_invent_proposal(self):
        for action in ("NO_ACTION","NO_BUILD","REPAIR_PROTOCOL","ESCALATE_VALIDATION"):
            with self.subTest(action=action): self.assertEqual(policy_b(snapshot=snapshot(), research_decision={"action":action})["status"], "NO_ACTION")

    def test_policy_b_generate_mechanism_is_seed(self):
        out = policy_b(snapshot=snapshot(), research_decision={"action":"GENERATE_MECHANISM","decision_id":"r1"})
        self.assertEqual(out["artifact_kind"], "IDEATION_SEED")

    def test_c_backend_unavailable_fails_closed(self):
        out, receipt = policy_c(snapshot=snapshot(), backend=None, mandate={"prompt_contract_version":"v1"})
        self.assertEqual(out["status"], "SOURCE_UNAVAILABLE"); self.assertIsNone(receipt)

    def test_c_malformed_and_semantic_retry_are_visible(self):
        out, _ = policy_c(snapshot=snapshot(), backend=DeterministicFakeBackend({"bad":1}), mandate={})
        self.assertEqual(out["status"], "SOURCE_FAILED")
        response={"alternatives":[{"summary":"x"}],"selected_alternative_index":0,"semantic_retry_count":1}
        out, receipt=policy_c(snapshot=snapshot(), backend=DeterministicFakeBackend(response), mandate={})
        self.assertEqual(out["status"], "BLOCKED"); self.assertEqual(receipt["semantic_retry_count"],1)

    def test_c_model_cannot_receive_outcomes(self):
        with self.assertRaises(ValueError): policy_c(snapshot=snapshot(), backend=DeterministicFakeBackend({}), mandate={"outcome_accessed":True})

    def test_c_complete_mechanism_emits_one_proposal_and_receipt(self):
        idea={"summary":"mechanism","mechanism":"m","payer":"p","actor":"a","clock":"c","universe":"u","falsifier":"f"}
        response={"alternatives":[idea,{"summary":"alt"}],"selected_alternative_index":0,"selection_criteria":"causal","semantic_retry_count":0}
        out, receipt=policy_c(snapshot=snapshot(), backend=DeterministicFakeBackend(response), mandate={"prompt_contract_version":"v2"})
        self.assertEqual(out["artifact_kind"],"IDEA_PROPOSAL"); self.assertEqual(receipt["alternative_count"],2)

    def test_claim_identity_and_lifecycle_do_not_consume_science(self):
        h=snapshot()["context_snapshot_hash"]
        a=source_claim(source_identity="doc:1",context_snapshot_hash=h,policy_kind="SYSTEMATIC_COVERAGE")
        b=source_claim(source_identity="doc:1",context_snapshot_hash=h,policy_kind="SYSTEMATIC_COVERAGE")
        self.assertEqual(a["claim_id"],b["claim_id"])
        for target in ("RELEASED","TRANSFERRED"):
            self.assertFalse(transition_claim(a,target)["scientifically_consumed"])

    def test_blocked_unexecuted_invalid_are_not_negative(self):
        cases=(("BLOCKED","BLOCKED_DATA"),("UNEXECUTED","UNEXECUTED"),("INVALIDATED_PROTOCOL","INVALID_PROTOCOL"))
        for disp, expected in cases:
            got=memory_lineage_check({"qualified":True,"scientific_disposition":disp,"same_semantic_family":True,"same_evidence":True})
            self.assertEqual(got["classification"],expected)

    def test_wrapper_is_non_authoritative_possible_equivalence(self):
        p={"identity":{"mechanism":"m","payer":"p","actor":"a","clock":"c","universe":"u","instrument":"etf"}}
        k=[{"proposal_id":"old","identity":{"mechanism":"m","payer":"p","actor":"a","clock":"c","universe":"u","instrument":"future"}}]
        self.assertEqual(duplicate_check(p,k)["classification"],"POSSIBLE_EXPRESSION_EQUIVALENCE")

    def test_stale_snapshot_requires_requalification(self):
        art={"artifact_kind":"IDEA_PROPOSAL","context_snapshot_hash":"old"}
        got=intake(artifact=art,memory_check={"classification":"NO_QUALIFIED_MATCH"},duplicate={"classification":"DISTINCT"},implementability={"admissible":True},current_context_hash="new")
        self.assertEqual(got["decision"],"STALE_REQUALIFICATION_REQUIRED")

    def test_passive_ledger_is_idempotent_and_rejects_queue_semantics(self):
        ledger=ProposalLedger(); row={"proposal_id":"p1","status":"ELIGIBLE_FOR_DISCOVERY"}
        self.assertEqual(ledger.persist(row),ledger.persist(row)); self.assertEqual(len(ledger.rows()),1)
        with self.assertRaises(ValueError): ledger.persist({"status":"READY"})

    def test_light_implementability_and_hard_stop(self):
        payload={"mechanism":"m","falsifier":"f","universe":"u","payer":"p","actor":"a","clock":"c"}
        impl=light_implementability(payload); self.assertTrue(impl["admissible"])
        art={"artifact_kind":"IDEA_PROPOSAL","context_snapshot_hash":"h"}
        got=intake(artifact=art,memory_check={"classification":"NO_QUALIFIED_MATCH"},duplicate={"classification":"DISTINCT"},implementability=impl,current_context_hash="h")
        self.assertEqual(got["decision"],"ELIGIBLE_FOR_DISCOVERY")
        self.assertNotIn("CANDIDATE", got)

    def test_zero_operational_side_effects(self):
        self.assertEqual(set(side_effect_zeroes().values()),{0})


if __name__ == "__main__": unittest.main()
