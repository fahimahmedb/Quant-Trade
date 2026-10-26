from __future__ import annotations

import unittest

from research.research_os.scientific_memory import (
    ScientificMemoryIndex,
    append_memory_record,
    attach_owner_governance,
    normalize_legacy_record,
    supersede_with_proof,
    validate_memory_record,
)
from research.research_os.scientific_store import AppendOnlyHashLedger


MANIFEST = {
    "source_commit": "183ad65ff260b903a16548ce37948f54d47a9ec8",
    "ledger_blob_sha": "ba9b165aaf96956776672df51233bb9bf1e6cbc9",
}


def legacy_record(**overrides):
    base = {
        "RESEARCH_FAMILY_ID": "family-a",
        "HYPOTHESIS_ID": "H-A",
        "LEGACY_ID_IF_ANY": "UNKNOWN",
        "GENERATION_ID": "G1",
        "TITLE": "Historical candidate",
        "MECHANISM": "mechanism-a",
        "RESULT_OBSERVED_AT": "2026-10-08",
        "UNIVERSE": "universe-a",
        "HORIZON": "1d",
        "RESULT": "NEGATIVE_REPLICATION_CONFIRMED",
        "RESULT_ARTIFACT": "research/results/a.json",
        "RESULT_COMMIT": "0123456789abcdef",
        "RESULT_SOURCE": "historical result",
        "ECONOMIC_EVIDENCE": "NEGATIVE_AFTER_COSTS",
        "STATISTICAL_EVIDENCE": "NEGATIVE",
        "FALSIFICATION_SCOPE": "exact frozen expression",
        "RESEARCH_DECISION": "KILL",
        "KNOWN_ATTEMPTS": 10,
        "EFFECTIVE_TRIALS": 10,
        "EFFECTIVE_TRIALS_STATUS": "KNOWN",
        "KNOWN_LIMITATIONS": [],
        "OPEN_BLOCKERS": [],
        "CURRENT_REUSABILITY": "NEGATIVE_KNOWLEDGE_ONLY",
        "DATA_PROVENANCE": "historical provider family",
        "PROVENANCE": ["historical-branch:research/results/a.json"],
    }
    base.update(overrides)
    return base


class ScientificMemoryTests(unittest.TestCase):
    def test_f2_blocked_prelook_remains_unknown_and_not_negative(self):
        f2 = legacy_record(
            RESEARCH_FAMILY_ID="kalshi-favorite-longshot",
            HYPOTHESIS_ID="F2-KALSHI-FLB-OOS",
            GENERATION_ID="G1-BLOCKED",
            MECHANISM="behavioral mispricing",
            UNIVERSE="Kalshi binary markets",
            HORIZON="T-24h to settlement",
            RESULT="BLOCKED_DATA_PERMISSION",
            RESULT_ARTIFACT="research/kalshi_flb_f2/TERMS_DECISION_2026-10-09.md",
            RESULT_COMMIT="UNKNOWN",
            ECONOMIC_EVIDENCE="NONE_NEW",
            STATISTICAL_EVIDENCE="NONE_NEW",
            KNOWN_ATTEMPTS=0,
            EFFECTIVE_TRIALS=0,
            OPEN_BLOCKERS=["documented rights and allowed route"],
            CURRENT_REUSABILITY="BLOCKED_PROTOCOL_MEMORY",
            PROVENANCE=["research/f2-primary-terms-decision-2026-10-09:research/kalshi_flb_f2/TERMS_DECISION_2026-10-09.md"],
        )
        record = normalize_legacy_record(f2, MANIFEST)
        self.assertTrue(record["canonical"])
        self.assertEqual(record["scientific_disposition"], "BLOCKED")
        self.assertEqual(record["epistemic_status"], "UNKNOWN")
        self.assertEqual(record["claim_ceiling"], "UNKNOWN_ONLY")

        ledger = AppendOnlyHashLedger()
        append_memory_record(ledger, record)
        index = ScientificMemoryIndex.from_ledger(ledger)
        self.assertEqual(index.query(scientific_disposition="NEGATIVE"), [])
        self.assertEqual(len(index.query(scientific_disposition="BLOCKED")), 1)

    def test_unexecuted_eurusd_is_unknown_not_failed(self):
        eurusd = legacy_record(
            RESEARCH_FAMILY_ID="eurusd-frozen-quote-proxy",
            HYPOTHESIS_ID="EURUSD-FROZEN-QUOTE",
            GENERATION_ID="G1-FROZEN",
            MECHANISM="fx quote response",
            UNIVERSE="EURUSD",
            HORIZON="event",
            RESULT="UNEXECUTED_FROZEN_PROXY",
            ECONOMIC_EVIDENCE="NONE",
            STATISTICAL_EVIDENCE="NONE",
            KNOWN_ATTEMPTS=0,
            OPEN_BLOCKERS=[],
        )
        record = normalize_legacy_record(eurusd, MANIFEST)
        self.assertEqual(record["scientific_disposition"], "UNEXECUTED")
        self.assertEqual(record["epistemic_status"], "UNKNOWN")
        self.assertNotEqual(record["scientific_disposition"], "NEGATIVE")

    def test_secondary_positive_signal_cannot_become_proven_edge(self):
        weather = legacy_record(
            RESEARCH_FAMILY_ID="weather-secondary-replication",
            HYPOTHESIS_ID="WEATHER-SECONDARY",
            MECHANISM="weather-linked market response",
            UNIVERSE="secondary replicated universe",
            RESULT="RETROSPECTIVE_POSITIVE_STRICT_NET",
            ECONOMIC_EVIDENCE="PROMISING_BUT_UNDERPROVED",
            STATISTICAL_EVIDENCE="INDICATIVE_AFTER_CAMPAIGN_MULTIPLICITY",
            RESEARCH_DECISION="EXPLORE",
        )
        record = normalize_legacy_record(weather, MANIFEST)
        self.assertEqual(record["scientific_disposition"], "POSITIVE_BUT_INSUFFICIENT")
        self.assertEqual(record["epistemic_status"], "KNOWN_POSITIVE_INSUFFICIENT")
        self.assertEqual(record["claim_ceiling"], "SIGNAL_NOT_PROOF")
        self.assertNotIn("PROVEN", record["claim_ceiling"])

    def test_protocol_invalidation_is_not_economic_failure(self):
        v1 = legacy_record(
            RESEARCH_FAMILY_ID="v1-cross-sectional",
            HYPOTHESIS_ID="V1-CAUSAL-TIMING",
            MECHANISM="cross-sectional reversal",
            RESULT="NEGATIVE_AFTER_CAUSAL_TIMING_PROTOCOL_INVALID",
            ECONOMIC_EVIDENCE="UNKNOWN",
            STATISTICAL_EVIDENCE="INVALID_PROTOCOL",
            DATA_INTEGRITY="FAILED",
            FALSIFICATION_SCOPE="protocol invalid; economics not interpretable",
        )
        record = normalize_legacy_record(v1, MANIFEST)
        self.assertEqual(record["scientific_disposition"], "INVALIDATED_PROTOCOL")
        self.assertEqual(record["epistemic_status"], "PROTOCOL_INVALID")
        self.assertEqual(record["claim_ceiling"], "PROTOCOL_WEAKNESS_ONLY")

    def test_same_label_or_path_cannot_merge_different_mechanisms(self):
        first = normalize_legacy_record(legacy_record(MECHANISM="forced flow"), MANIFEST)
        second = normalize_legacy_record(legacy_record(MECHANISM="behavioral reversal"), MANIFEST)
        self.assertNotEqual(first["semantic_key"], second["semantic_key"])
        self.assertNotEqual(first["memory_id"], second["memory_id"])

    def test_branch_name_does_not_duplicate_same_semantics(self):
        a = normalize_legacy_record(legacy_record(PROVENANCE=["branch-a:research/results/a.json"]), MANIFEST)
        b = normalize_legacy_record(legacy_record(PROVENANCE=["branch-b:research/results/a.json"]), MANIFEST)
        self.assertEqual(a["semantic_key"], b["semantic_key"])
        self.assertEqual(a["memory_id"], b["memory_id"])
        index = ScientificMemoryIndex([a, b])
        self.assertEqual(len(index.records), 1)

    def test_supersession_preserves_original_provenance_and_requires_proof(self):
        record = normalize_legacy_record(legacy_record(), MANIFEST)
        before = list(record["provenance"])
        with self.assertRaises(ValueError):
            supersede_with_proof(record, superseding_memory_id="smem:new", proof_refs=[], reason="new protocol")
        superseded = supersede_with_proof(record, superseding_memory_id="smem:new", proof_refs=["commit:deadbeef"], reason="new evidence-bound protocol supersedes interpretation")
        self.assertEqual(superseded["record_status"], "SUPERSEDED_WITH_PROOF")
        self.assertEqual(superseded["provenance"], before)
        self.assertEqual(superseded["scientific_disposition"], record["scientific_disposition"])

    def test_owner_governance_cannot_overwrite_scientific_evidence(self):
        record = normalize_legacy_record(legacy_record(), MANIFEST)
        governed = attach_owner_governance(record, decision_ref="owner/OD-17", action="PRESERVE_AS_MEMORY", reason="do not repeat spent protocol")
        self.assertEqual(governed["record_status"], "OWNER_GOVERNANCE_NORMALIZED")
        self.assertEqual(governed["scientific_disposition"], record["scientific_disposition"])
        self.assertEqual(governed["evidence"], record["evidence"])
        self.assertEqual(len(governed["governance_refs"]), 1)

    def test_unknown_is_explicit_not_false_or_negative(self):
        blocked = normalize_legacy_record(legacy_record(RESULT="BLOCKED_BY_DATA", ECONOMIC_EVIDENCE="NONE", STATISTICAL_EVIDENCE="NONE", OPEN_BLOCKERS=["source permission"]), MANIFEST)
        self.assertEqual(blocked["epistemic_status"], "UNKNOWN")
        self.assertIsInstance(blocked["epistemic_status"], str)
        self.assertNotEqual(blocked["epistemic_status"], False)
        self.assertNotEqual(blocked["scientific_disposition"], "NEGATIVE")

    def test_missing_identity_or_only_owner_assertion_cannot_be_canonical(self):
        missing_identity = normalize_legacy_record(legacy_record(MECHANISM="UNKNOWN", RESULT_ARTIFACT="UNKNOWN", RESULT_COMMIT="UNKNOWN", PROVENANCE=["owner mission input"]), MANIFEST)
        self.assertFalse(missing_identity["canonical"])
        self.assertEqual(missing_identity["record_status"], "REVIEW_STILL_REQUIRED")
        with self.assertRaises(ValueError):
            validate_memory_record(missing_identity, require_canonical=True)
        with self.assertRaises(ValueError):
            append_memory_record(AppendOnlyHashLedger(), missing_identity)

    def test_invalid_capture_is_protocol_memory_not_negative(self):
        capture = legacy_record(
            RESEARCH_FAMILY_ID="crypto-orderbook-pressure",
            HYPOTHESIS_ID="disc-crypto-book-pressure-prospective-l1-v0",
            MECHANISM="order-book imbalance",
            RESULT="PARK_DATA_CAPTURE_INVALID_ZERO_VALID_TRADES",
            ECONOMIC_EVIDENCE="NONE_VALID",
            STATISTICAL_EVIDENCE="NONE_VALID",
            DATA_INTEGRITY="FAILED",
            FALSIFICATION_SCOPE="none; failed implementation does not kill mechanism",
            CURRENT_REUSABILITY="NEGATIVE_IMPLEMENTATION_KNOWLEDGE",
            OPEN_BLOCKERS=["valid capture route"],
        )
        record = normalize_legacy_record(capture, MANIFEST)
        self.assertEqual(record["scientific_disposition"], "INVALIDATED_PROTOCOL")
        self.assertEqual(record["claim_ceiling"], "PROTOCOL_WEAKNESS_ONLY")

    def test_structural_retrieval_never_computes_empirical_similarity(self):
        record = normalize_legacy_record(legacy_record(MECHANISM="forced flow"), MANIFEST)
        index = ScientificMemoryIndex([record])
        matches = index.structural_retrieval({"mechanism": "forced flow", "universe": "universe-a"})
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["similarity_kind"], "STRUCTURAL_FACET_OVERLAP_ONLY")
        self.assertFalse(matches[0]["empirical_similarity_computed"])
        self.assertEqual(matches[0]["empirical_correlation"], "UNKNOWN")
        self.assertNotIn("score", matches[0])

    def test_memory_uses_existing_hash_ledger_and_detects_tamper(self):
        record = normalize_legacy_record(legacy_record(), MANIFEST)
        ledger = AppendOnlyHashLedger()
        append_memory_record(ledger, record)
        self.assertTrue(ledger.verify())
        ledger.entries[0]["payload"]["evidence"]["historical_result"] = "TAMPERED"
        self.assertFalse(ledger.verify())


if __name__ == "__main__":
    unittest.main()
