from __future__ import annotations

import threading
import unittest

from research.research_os.multi_source_ideation_hardening import (
    DurableProposalLedger, SourceClaimLedger, ancestry_check, combine_duplicate_evidence,
    proposal_identity, qualify_for_discovery,
)


class MultiSourceIdeationV2HardeningTests(unittest.TestCase):
    def test_proposal_identity_binds_policy_context_payload_and_provenance(self):
        a = proposal_identity(policy_kind="SYSTEMATIC_COVERAGE", context_snapshot_hash="h", payload={"x": 1}, provenance={"source": "s"})
        b = proposal_identity(policy_kind="SYSTEMATIC_COVERAGE", context_snapshot_hash="h", payload={"x": 1}, provenance={"source": "s"})
        self.assertEqual(a, b)
        self.assertNotEqual(a["proposal_id"], proposal_identity(policy_kind="SYSTEMATIC_COVERAGE", context_snapshot_hash="h2", payload={"x": 1}, provenance={"source": "s"})["proposal_id"])

    def test_explicit_ancestry_is_dispositive_without_label_matching(self):
        got = ancestry_check({"ancestor_ids": ["old-1"]}, [{"proposal_id": "old-1", "label": "totally different"}])
        self.assertEqual(got["classification"], "ANCESTRY_MATCH")
        combined = combine_duplicate_evidence(semantic={"classification": "DISTINCT"}, ancestry=got)
        self.assertEqual(combined["classification"], "ANCESTRY_MATCH")

    def test_unknown_ancestry_is_not_invented_distinct(self):
        self.assertEqual(ancestry_check({}, [])["classification"], "UNKNOWN")

    def test_source_claim_is_atomic_and_not_a_lease(self):
        ledger = SourceClaimLedger()
        first = ledger.claim(source_identity="doc:1", context_snapshot_hash="h", policy_kind="SYSTEMATIC_COVERAGE")
        self.assertNotIn("lease", first)
        self.assertFalse(first["scientifically_consumed"])
        self.assertEqual(first, ledger.claim(source_identity="doc:1", context_snapshot_hash="h", policy_kind="SYSTEMATIC_COVERAGE"))
        with self.assertRaises(ValueError):
            ledger.claim(source_identity="doc:1", context_snapshot_hash="h", policy_kind="DIVERGENT_EXPLORATION")
        released = ledger.transition(first["claim_id"], "RELEASED")
        self.assertFalse(released["scientifically_consumed"])

    def test_concurrent_claim_has_single_winner(self):
        ledger = SourceClaimLedger(); outcomes = []
        def run(policy):
            try: outcomes.append((policy, "OK", ledger.claim(source_identity="doc:x", context_snapshot_hash="h", policy_kind=policy)["claim_id"]))
            except ValueError: outcomes.append((policy, "BLOCKED", None))
        threads = [threading.Thread(target=run, args=(p,)) for p in ("SYSTEMATIC_COVERAGE", "DIVERGENT_EXPLORATION")]
        for t in threads: t.start()
        for t in threads: t.join()
        self.assertEqual(sum(x[1] == "OK" for x in outcomes), 1)
        self.assertEqual(sum(x[1] == "BLOCKED" for x in outcomes), 1)

    def test_durable_ledger_restart_and_idempotency(self):
        row = {"proposal_id": "p1", "status": "ELIGIBLE_FOR_DISCOVERY", "context_snapshot_hash": "h"}
        a = DurableProposalLedger(); self.assertEqual(a.persist(row), "p1"); self.assertEqual(a.persist(row), "p1")
        b = DurableProposalLedger(a.snapshot()); self.assertEqual(b.persist(row), "p1"); self.assertEqual(len(b.snapshot()), 1)
        with self.assertRaises(ValueError): b.persist({"proposal_id": "p1", "status": "OTHER"})
        with self.assertRaises(ValueError): b.persist({"proposal_id": "q", "status": "READY"})

    def test_final_boundary_never_creates_task_or_candidate(self):
        p = {"artifact_kind": "IDEA_PROPOSAL", "context_snapshot_hash": "h"}
        got = qualify_for_discovery(proposal=p, context_snapshot_hash="h", memory={"classification": "NO_QUALIFIED_MATCH"}, duplicate={"classification": "DISTINCT"}, implementability={"admissible": True})
        self.assertEqual(got["decision"], "ELIGIBLE_FOR_DISCOVERY")
        self.assertFalse(got["ready_task_created"]); self.assertFalse(got["candidate_created"])

    def test_stale_duplicate_and_unknown_fail_closed(self):
        base = {"artifact_kind": "IDEA_PROPOSAL", "context_snapshot_hash": "h"}
        common = {"context_snapshot_hash": "h", "memory": {"classification": "NO_QUALIFIED_MATCH"}, "implementability": {"admissible": True}}
        self.assertEqual(qualify_for_discovery(proposal=base, duplicate={"classification": "ANCESTRY_MATCH"}, **common)["decision"], "NOT_ELIGIBLE")
        self.assertEqual(qualify_for_discovery(proposal=base, duplicate={"classification": "UNKNOWN"}, **common)["decision"], "REVIEW_REQUIRED")
        self.assertEqual(qualify_for_discovery(proposal=base, context_snapshot_hash="new", memory=common["memory"], duplicate={"classification": "DISTINCT"}, implementability=common["implementability"])["decision"], "STALE_REQUALIFICATION_REQUIRED")


if __name__ == "__main__":
    unittest.main()
