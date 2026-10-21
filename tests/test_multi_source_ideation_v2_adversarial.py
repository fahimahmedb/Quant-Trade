from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import (
    DeterministicFakeBackend, barrier, build_context_snapshot, duplicate_check,
    memory_lineage_check, policy_c, raw_artifact,
)
from research.research_os.multi_source_ideation_hardening import DurableProposalLedger, qualify_for_discovery


def snap(cycle="a"):
    keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
    return build_context_snapshot(ideation_cycle_id=cycle,created_at="2026-10-21T20:00:00Z",refs={k:k+":"+cycle for k in keys},relevant_schema_versions={"x":"1"})


class IdeationAdversarialTests(unittest.TestCase):
    def test_cycle_leakage_rejected_even_when_policy_names_are_valid(self):
        a=snap("a"); b=snap("b")
        artifacts=[
            raw_artifact(policy_kind="SYSTEMATIC_COVERAGE",status="NO_PROPOSAL",context_snapshot_hash=a["context_snapshot_hash"]),
            raw_artifact(policy_kind="INFORMATION_VALUE",status="NO_ACTION",context_snapshot_hash=a["context_snapshot_hash"]),
            raw_artifact(policy_kind="DIVERGENT_EXPLORATION",status="SOURCE_UNAVAILABLE",context_snapshot_hash=b["context_snapshot_hash"]),
        ]
        with self.assertRaises(ValueError): barrier(artifacts,a["context_snapshot_hash"])

    def test_unknown_memory_is_not_negative(self):
        got=memory_lineage_check({"qualified":False,"scientific_disposition":"NEGATIVE","same_semantic_family":True,"same_evidence":True})
        self.assertEqual(got["classification"],"UNKNOWN")

    def test_expression_equivalence_is_not_exact_duplicate(self):
        p={"identity":{"mechanism":"m","payer":"p","actor":"a","clock":"c","universe":"u","wrapper":"etf"}}
        known=[{"proposal_id":"x","identity":{"mechanism":"m","payer":"p","actor":"a","clock":"c","universe":"u","wrapper":"future"}}]
        self.assertEqual(duplicate_check(p,known)["classification"],"POSSIBLE_EXPRESSION_EQUIVALENCE")

    def test_unknown_duplicate_fails_closed_before_discovery(self):
        got=qualify_for_discovery(proposal={"artifact_kind":"IDEA_PROPOSAL","context_snapshot_hash":"h"},context_snapshot_hash="h",memory={"classification":"NO_QUALIFIED_MATCH"},duplicate={"classification":"UNKNOWN"},implementability={"admissible":True})
        self.assertEqual(got["decision"],"REVIEW_REQUIRED"); self.assertFalse(got["eligible_for_discovery"])

    def test_model_cannot_smuggle_outcome_access_flag(self):
        with self.assertRaises(ValueError):
            policy_c(snapshot=snap(),backend=DeterministicFakeBackend({"alternatives":[],"selected_alternative_index":0}),mandate={"outcome_accessed":True})

    def test_operational_fields_are_rejected_case_insensitively(self):
        ledger=DurableProposalLedger()
        for row in ({"proposal_id":"x","lease_owner":"w"},{"proposal_id":"x","scheduler_state":"READY"},{"proposal_id":"x","status":"running"}):
            with self.subTest(row=row):
                with self.assertRaises(ValueError): ledger.persist(row)


if __name__ == "__main__": unittest.main()
