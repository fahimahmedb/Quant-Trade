from __future__ import annotations

import unittest

from research.research_os.legacy import LegacyKnowledgeBase
from research.research_os.scientific_memory_feedback import (
    qualified_legacy_memory_view,
    scientific_memory_feedback,
)


def historical(*, disposition: str, mechanism: str = "forced rebalance pressure", hypothesis: str = "OLD-H", protocol_generation: str = "G1", payer: str = "index trackers", actor: str = "passive funds", clock: str = "close auction", universe: str = "index additions", exposure: str = "temporary price pressure"):
    record = {
        "RESEARCH_FAMILY_ID": "family-old-label",
        "MECHANISM": mechanism,
        "HYPOTHESIS_ID": hypothesis,
        "GENERATION_ID": protocol_generation,
        "UNIVERSE": universe,
        "INSTRUMENT": "equities",
        "TIMING_CLOCK": clock,
        "HORIZON": "1d",
        "RESULT_ARTIFACT": "artifacts/result.json",
        "RESULT_COMMIT": "a" * 40,
        "RESULT_OBSERVED_AT": "2026-01-01T00:00:00Z",
        "PAYER": payer,
        "CONSTRAINED_ACTOR": actor,
        "ECONOMIC_EXPOSURE": exposure,
        "PROVENANCE": ["historical://qualified/source"],
        "KNOWN_ATTEMPTS": 1,
        "ECONOMIC_EVIDENCE": "NONE",
        "STATISTICAL_EVIDENCE": "NONE",
        "DATA_INTEGRITY": "PASS",
        "OPERATIONAL_READINESS": "UNKNOWN",
        "CURRENT_REUSABILITY": "UNKNOWN",
        "POINT_IN_TIME_STATUS": "UNKNOWN",
        "RESULT": "UNKNOWN",
        "FALSIFICATION_SCOPE": "UNKNOWN",
        "OPEN_BLOCKERS": [],
        "MECHANISM_EVIDENCE": "UNKNOWN",
        "KNOWN_LIMITATIONS": [],
        "RESEARCH_DECISION": "UNKNOWN",
    }
    if disposition == "NEGATIVE":
        record.update(RESULT="FAMILY_REJECTED", ECONOMIC_EVIDENCE="NEGATIVE_AFTER_COSTS")
    elif disposition == "BLOCKED":
        record.update(RESULT="BLOCKED_DATA_PERMISSION", OPEN_BLOCKERS=["permission"])
    elif disposition == "UNEXECUTED":
        record.update(RESULT="UNEXECUTED", KNOWN_ATTEMPTS=0)
    elif disposition == "INVALIDATED_PROTOCOL":
        record.update(RESULT="PROTOCOL_INVALID", DATA_INTEGRITY="FAILED", KNOWN_LIMITATIONS=["capture invalid"])
    elif disposition == "POSITIVE_BUT_INSUFFICIENT":
        record.update(RESULT="POSITIVE_BUT_INSUFFICIENT", ECONOMIC_EVIDENCE="RETROSPECTIVE_INDICATIVE")
    else:
        raise AssertionError(disposition)
    return record


def candidate(*, mechanism: str = "forced rebalance pressure", hypothesis: str = "RENAMED-H", payer: str = "index trackers", actor: str = "passive funds", clock: str = "close auction", universe: str = "index additions", exposure: str = "temporary price pressure"):
    return {
        "hypothesis_id": hypothesis,
        "generation_id": "G1",
        "mechanism": mechanism,
        "economic_tags": ["rebalancing", "pressure"],
        "identity": {
            "mechanism": mechanism,
            "payer": payer,
            "constrained_actor": actor,
            "timing_clock": clock,
            "universe": universe,
            "economic_exposure": exposure,
            "instrument": "equities",
            "source_family": "documentary",
            "evidence_identity": "new-evidence",
        },
    }


def manifest():
    return {
        "schema_version": "legacy-test-v1",
        "source_commit": "b" * 40,
        "ledger_blob_sha": "c" * 40,
        "reconciliation_status": "TEST",
        "historical_research_items_found": 1,
        "known_duplicate_or_variant_items": 0,
        "prospective_validated": False,
        "global_effective_trials": "UNKNOWN",
        "recovered_source_reviews": [],
    }


class ScientificMemoryFeedbackTests(unittest.TestCase):
    def view(self, record):
        result = qualified_legacy_memory_view([record], manifest())
        self.assertEqual(result["canonical_count"], 1)
        self.assertFalse(result["persistent_store_created"])
        return result["canonical_records"]

    def test_negative_family_resurfaces_under_renamed_hypothesis_id(self):
        feedback = scientific_memory_feedback(candidate(), self.view(historical(disposition="NEGATIVE")))
        self.assertEqual(feedback["action"], "NO_BUILD")
        self.assertFalse(feedback["allow_candidate_progress"])
        self.assertEqual(feedback["scientific_equivalence"], "ESTABLISHED_SAME_SEMANTIC_FAMILY")

    def test_blocked_is_park_not_negative(self):
        feedback = scientific_memory_feedback(candidate(), self.view(historical(disposition="BLOCKED")))
        self.assertEqual(feedback["action"], "PARK")
        self.assertNotIn("KNOWN_NEGATIVE_SAME_SEMANTIC_FAMILY", feedback["reason_codes"])

    def test_unexecuted_is_not_failed(self):
        feedback = scientific_memory_feedback(candidate(), self.view(historical(disposition="UNEXECUTED")))
        self.assertTrue(feedback["allow_candidate_progress"])
        self.assertEqual(feedback["action"], "NO_ACTION")
        self.assertIn("HISTORICAL_UNEXECUTED_IS_NOT_FAILURE", feedback["reason_codes"])

    def test_invalidated_protocol_requires_changed_protocol(self):
        same_protocol_candidate = candidate(hypothesis="OLD-H")
        feedback = scientific_memory_feedback(same_protocol_candidate, self.view(historical(disposition="INVALIDATED_PROTOCOL")))
        self.assertEqual(feedback["action"], "REPAIR_PROTOCOL")
        self.assertFalse(feedback["allow_candidate_progress"])

    def test_positive_insufficient_redirects_to_validation_not_promotion(self):
        feedback = scientific_memory_feedback(candidate(), self.view(historical(disposition="POSITIVE_BUT_INSUFFICIENT")))
        self.assertEqual(feedback["action"], "ESCALATE_VALIDATION")
        self.assertFalse(feedback["allow_candidate_progress"])

    def test_unknown_identity_is_not_novel(self):
        raw = {"hypothesis_id": "H", "generation_id": "G1", "mechanism": "new mechanism", "economic_tags": ["new"]}
        feedback = scientific_memory_feedback(raw, [])
        self.assertEqual(feedback["action"], "ARCHAEOLOGY_LOOKUP")
        self.assertFalse(feedback["allow_candidate_progress"])
        self.assertIn("UNKNOWN_IDENTITY_IS_NOT_NOVELTY", feedback["reason_codes"])

    def test_wrong_semantic_identity_cannot_influence_search(self):
        feedback = scientific_memory_feedback(candidate(actor="discretionary traders"), self.view(historical(disposition="NEGATIVE")))
        self.assertTrue(feedback["allow_candidate_progress"])
        self.assertEqual(feedback["scientific_equivalence"], "NOT_ESTABLISHED")

    def test_lexical_overlap_is_review_metadata_not_scientific_duplicate(self):
        record = historical(disposition="UNEXECUTED", mechanism="forced rebalance pressure old variant")
        kb = LegacyKnowledgeBase(manifest(), {"records": [record]})
        distinct = candidate(mechanism="forced rebalance pressure new mechanism", actor="market makers")
        result = kb.screen_candidate(distinct)
        self.assertTrue(result["lexical_review_required"])
        self.assertEqual(result["lexical_review_status"], "REVIEW_LEGACY_OVERLAP")
        self.assertEqual(result["status"], "NO_EXACT_LEGACY_CONFLICT")
        self.assertEqual(result["scientific_memory"]["feedback"]["scientific_equivalence"], "NOT_ESTABLISHED")

    def test_model_commentary_never_enters_memory_feedback(self):
        feedback = scientific_memory_feedback(candidate(), self.view(historical(disposition="UNEXECUTED")))
        self.assertFalse(feedback["model_commentary_used_as_evidence"])
        self.assertFalse(feedback["empirical_similarity_computed"])
        self.assertEqual(feedback["empirical_correlation"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
