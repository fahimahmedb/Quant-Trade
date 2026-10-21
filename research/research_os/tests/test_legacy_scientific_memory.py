from __future__ import annotations

import unittest

from research.research_os.legacy import LegacyKnowledgeBase


MANIFEST = {
    "source_commit": "183ad65ff260b903a16548ce37948f54d47a9ec8",
    "ledger_blob_sha": "ba9b165aaf96956776672df51233bb9bf1e6cbc9",
    "reconciliation_status": "PARTIAL_WITH_EXPLICIT_GAPS",
    "historical_research_items_found": 3,
    "known_duplicate_or_variant_items": 0,
    "prospective_validated": 0,
    "global_effective_trials": "UNKNOWN",
}


def record(hid: str, mechanism: str, result: str, economic: str, **overrides):
    value = {
        "RESEARCH_FAMILY_ID": f"family-{hid.lower()}",
        "HYPOTHESIS_ID": hid,
        "LEGACY_ID_IF_ANY": "UNKNOWN",
        "GENERATION_ID": "G1",
        "TITLE": hid,
        "MECHANISM": mechanism,
        "RESULT_OBSERVED_AT": "2026-10-09",
        "UNIVERSE": "test-universe",
        "HORIZON": "1d",
        "RESULT": result,
        "RESULT_SOURCE": "historical result",
        "RESULT_COMMIT": "abcdef123456",
        "RESULT_ARTIFACT": f"research/{hid}.json",
        "ECONOMIC_EVIDENCE": economic,
        "STATISTICAL_EVIDENCE": "NONE" if economic == "NONE" else economic,
        "DATA_INTEGRITY": "ADEQUATE",
        "RESEARCH_DECISION": "PARK",
        "FALSIFICATION_SCOPE": "exact expression",
        "KNOWN_ATTEMPTS": 1,
        "EFFECTIVE_TRIALS": "UNKNOWN",
        "EFFECTIVE_TRIALS_STATUS": "UNKNOWN",
        "KNOWN_LIMITATIONS": [],
        "OPEN_BLOCKERS": [],
        "CURRENT_REUSABILITY": "SCIENTIFIC_MEMORY_ONLY",
        "DATA_PROVENANCE": "historical-source-family",
        "NEXT_LEGITIMATE_STEP": "review memory before new work",
        "PROVENANCE": [f"historical:{hid}.json"],
    }
    value.update(overrides)
    return value


class LegacyScientificMemoryIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.f2 = record(
            "F2-KALSHI-FLB-OOS",
            "behavioral mispricing",
            "BLOCKED_DATA_PERMISSION",
            "NONE_NEW",
            KNOWN_ATTEMPTS=0,
            OPEN_BLOCKERS=["documented rights and allowed route"],
            CURRENT_REUSABILITY="BLOCKED_PROTOCOL_MEMORY",
        )
        self.negative = record(
            "B2-SECTOR-XREV",
            "sector cross-sectional reversal",
            "NEGATIVE_REPLICATION_CONFIRMED",
            "NEGATIVE_AFTER_COSTS",
            RESEARCH_DECISION="KILL",
        )
        self.review = record(
            "BOX-OFFICE-REPLAY",
            "UNKNOWN",
            "UNKNOWN",
            "UNKNOWN",
            GENERATION_ID="UNKNOWN",
            RESULT_COMMIT="UNKNOWN",
            RESULT_ARTIFACT="UNKNOWN",
            RESULT_SOURCE="primary artifact not recovered",
            PROVENANCE=["owner mission input"],
            KNOWN_LIMITATIONS=["provenance missing"],
            CURRENT_REUSABILITY="PROVENANCE_GAP",
        )
        ledger = {
            "schema_version": "legacy-research-ledger-v1",
            "governance": {"historical_result_immutability": True},
            "records": [self.f2, self.negative, self.review],
        }
        self.base = LegacyKnowledgeBase(MANIFEST, ledger)

    def test_exact_duplicate_uses_memory_as_scientific_authority(self):
        screen = self.base.screen_candidate({"hypothesis_id": "F2-KALSHI-FLB-OOS", "mechanism": "behavioral mispricing"})
        self.assertEqual(screen["status"], "BLOCK_EXACT_LEGACY_DUPLICATE")
        self.assertFalse(screen["historical_result_is_scientific_authority"])
        self.assertEqual(screen["scientific_memory"]["scientific_disposition"], "BLOCKED")
        self.assertEqual(screen["scientific_memory"]["epistemic_status"], "UNKNOWN")
        self.assertEqual(screen["scientific_memory"]["claim_ceiling"], "UNKNOWN_ONLY")

    def test_negative_query_excludes_blocked(self):
        index = self.base.scientific_memory_index()
        negatives = index.query(scientific_disposition="NEGATIVE")
        self.assertEqual(len(negatives), 1)
        self.assertEqual(negatives[0]["source_identity"]["hypothesis_id"], "B2-SECTOR-XREV")

    def test_unrecovered_primary_artifact_stays_review_only(self):
        all_records = self.base.scientific_memory_records(include_review=True)
        box = next(x for x in all_records if x["source_identity"]["hypothesis_id"] == "BOX-OFFICE-REPLAY")
        self.assertFalse(box["canonical"])
        self.assertEqual(box["scientific_disposition"], "REVIEW_STILL_REQUIRED")
        canonical_ids = {x["source_identity"]["hypothesis_id"] for x in self.base.scientific_memory_records()}
        self.assertNotIn("BOX-OFFICE-REPLAY", canonical_ids)

    def test_normalization_report_is_vector_not_score(self):
        report = self.base.memory_normalization_report()
        self.assertEqual(report["source_record_count"], 3)
        self.assertEqual(report["canonical_memory_count"], 2)
        self.assertEqual(report["review_memory_count"], 1)
        self.assertFalse(report["single_score_computed"])
        self.assertFalse(report["empirical_similarity_computed"])
        self.assertEqual(report["empirical_correlation"], "UNKNOWN")
        self.assertEqual(report["scientific_dispositions"]["BLOCKED"], 1)
        self.assertEqual(report["scientific_dispositions"]["NEGATIVE"], 1)
        self.assertEqual(report["scientific_dispositions"]["REVIEW_STILL_REQUIRED"], 1)

    def test_nonexact_overlap_is_explicit_review_hint_only(self):
        screen = self.base.screen_candidate({
            "hypothesis_id": "NEW-1",
            "mechanism": "sector cross-sectional reversal",
            "economic_tags": ["sector", "reversal"],
        })
        self.assertEqual(screen["status"], "REVIEW_LEGACY_OVERLAP")
        self.assertFalse(screen["structural_overlap_is_empirical_correlation"])
        self.assertEqual(screen["empirical_correlation"], "UNKNOWN")
        self.assertTrue(screen["legacy_overlap_hints"])
        hint = screen["legacy_overlap_hints"][0]
        self.assertEqual(hint["similarity_kind"], "LEGACY_TOKEN_OVERLAP_REVIEW_HINT_ONLY")
        self.assertFalse(hint["empirical_similarity_computed"])
        self.assertFalse(hint["historical_result_is_scientific_authority"])

    def test_summary_surfaces_memory_health_without_mutating_source(self):
        original = [dict(x) for x in self.base.records]
        summary = self.base.summary()
        self.assertIn("scientific_memory", summary)
        self.assertTrue(summary["read_only"])
        self.assertEqual(self.base.records, original)


if __name__ == "__main__":
    unittest.main()
