from __future__ import annotations

import unittest

from research.research_os.legacy import LegacyKnowledgeBase


MANIFEST = {
    "schema_version": "legacy-test-v1",
    "source_commit": "a" * 40,
    "ledger_blob_sha": "b" * 40,
    "reconciliation_status": "TEST",
    "historical_research_items_found": 1,
    "known_duplicate_or_variant_items": 0,
    "prospective_validated": False,
    "global_effective_trials": "UNKNOWN",
    "recovered_source_reviews": [],
}


def sparse_record():
    return {
        "HYPOTHESIS_ID": "OLD-1",
        "RESEARCH_FAMILY_ID": "old-family",
        "MECHANISM": "forced rebalance pressure",
        "RESULT": "UNKNOWN",
        "RESEARCH_DECISION": "UNKNOWN",
    }


class LegacyMemoryCompatibilityTests(unittest.TestCase):
    def test_exact_id_retains_operational_duplicate_block_without_scientific_equivalence_claim(self):
        kb = LegacyKnowledgeBase(MANIFEST, {"records": [sparse_record()]})
        result = kb.screen_candidate({"hypothesis_id": "OLD-1"})
        self.assertEqual(result["status"], "BLOCK_EXACT_LEGACY_DUPLICATE")
        self.assertEqual(result["identifier_collision_scientific_equivalence"], "NOT_ESTABLISHED_BY_IDENTIFIER_ALONE")

    def test_sparse_unknown_identity_without_collision_is_not_labelled_novel_or_blocked_duplicate(self):
        kb = LegacyKnowledgeBase(MANIFEST, {"records": [sparse_record()]})
        result = kb.screen_candidate({"hypothesis_id": "NEW-1", "mechanism": "unrelated inventory timing"})
        self.assertEqual(result["status"], "NO_EXACT_LEGACY_CONFLICT")
        self.assertEqual(result["novelty_status"], "UNRESOLVED_NOT_CLAIMED")
        self.assertEqual(result["scientific_memory"]["feedback"]["action"], "ARCHAEOLOGY_LOOKUP")

    def test_sparse_overlap_routes_to_scoped_review_not_scientific_kill(self):
        kb = LegacyKnowledgeBase(MANIFEST, {"records": [sparse_record()]})
        result = kb.screen_candidate({"hypothesis_id": "NEW-2", "mechanism": "forced rebalance pressure variant"})
        self.assertEqual(result["status"], "REVIEW_LEGACY_OVERLAP")
        self.assertEqual(result["matches"][0]["scientific_equivalence"], "NOT_ESTABLISHED_BY_TOKEN_OVERLAP")
        self.assertEqual(result["novelty_status"], "UNRESOLVED_NOT_CLAIMED")


if __name__ == "__main__":
    unittest.main()
