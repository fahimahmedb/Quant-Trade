from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research.research_os.archaeology import (
    ArchaeologyCatalog,
    finding_provenance_refs,
    validate_finding,
    validate_source_ref,
)


CATALOG = Path(__file__).parents[1] / "legacy" / "archaeology_source_catalog.json"


class ArchaeologyTests(unittest.TestCase):
    def setUp(self):
        self.catalog = ArchaeologyCatalog.load(CATALOG)

    def test_catalog_is_provenance_only_not_second_truth_store(self):
        report = self.catalog.report()
        self.assertFalse(report["scientific_truth_store"])
        self.assertFalse(report["single_score_computed"])
        self.assertFalse(report["outcome_accessed"])
        raw = json.loads(CATALOG.read_text())
        forbidden = {"result", "results", "pnl", "sharpe", "correlation", "score", "metrics", "economic_evidence"}
        for finding in raw["findings"]:
            self.assertFalse(forbidden & set(finding))

    def test_branch_name_alone_cannot_qualify_history(self):
        finding = {
            "archaeology_id": "x", "subject_id": "x", "subject_kind": "test",
            "mechanism": "x", "history_disposition": "REUSE_CURRENT",
            "terminal_state": "QUALIFIED_CURRENT", "memory_action": "NORMALIZE_CANONICAL_MEMORY",
            "claim_limit": "x", "source_refs": [{"kind": "BRANCH_LOCATOR", "branch": "builder/x"}],
            "blockers": [], "supersedes_subject_ids": [], "notes": "", "outcome_accessed": False,
        }
        with self.assertRaises(ValueError):
            validate_finding(finding)

    def test_qualified_sources_have_immutable_anchor(self):
        for finding in self.catalog.query(terminal_state="QUALIFIED_CURRENT"):
            refs = finding_provenance_refs(finding)
            self.assertTrue(refs, finding["archaeology_id"])
            self.assertTrue(all(x["kind"] == "ARCHAEOLOGY_IMMUTABLE_SOURCE" for x in refs))

    def test_f1_stage_a_and_b_are_distinct_generations(self):
        a = self.catalog.query(subject_id="F1-CRYPTO-CARRY-STAGE-A")[0]
        b = self.catalog.query(subject_id="F1-CRYPTO-CARRY-STAGE-B")[0]
        self.assertNotEqual(a["subject_id"], b["subject_id"])
        self.assertEqual(a["memory_action"], "PRESERVE_DISTINCT_MEMORY_GENERATIONS")
        self.assertEqual(b["memory_action"], "PRESERVE_DISTINCT_MEMORY_GENERATIONS")
        self.assertNotEqual(finding_provenance_refs(a)[0]["ref"], finding_provenance_refs(b)[0]["ref"])

    def test_box_office_stays_review_not_negative_truth(self):
        box = self.catalog.query(subject_id="BOX-OFFICE-REPLAY")[0]
        self.assertEqual(box["history_disposition"], "REVIEW_STILL_REQUIRED")
        self.assertEqual(box["terminal_state"], "PARTIAL_WITH_EXPLICIT_BLOCKER")
        self.assertEqual(box["memory_action"], "KEEP_REVIEW_ONLY")
        self.assertIn("unrecovered", " ".join(box["blockers"]).lower())

    def test_mlb_weather_gap_cannot_be_filled_by_weather_protocol_artifact(self):
        replication = self.catalog.query(subject_id="MLB-SOCCER-WEATHER-REPLICATION")[0]
        protocol = self.catalog.query(subject_id="WEATHER-FORWARD-V2-PROTOCOL")[0]
        self.assertEqual(replication["history_disposition"], "REVIEW_STILL_REQUIRED")
        self.assertEqual(protocol["history_disposition"], "REUSE_CURRENT")
        self.assertNotEqual(replication["subject_kind"], protocol["subject_kind"])
        self.assertIn("different identity", replication["notes"].lower())

    def test_eurusd_unexecuted_semantics_do_not_become_failure(self):
        eurusd = self.catalog.query(subject_id="EURUSD-FROZEN-QUOTE-PROXY")[0]
        self.assertEqual(eurusd["history_disposition"], "REVIEW_STILL_REQUIRED")
        self.assertEqual(eurusd["memory_action"], "KEEP_REVIEW_ONLY")
        self.assertIn("UNEXECUTED/UNKNOWN", eurusd["claim_limit"])
        self.assertNotIn("negative", eurusd["claim_limit"].lower())

    def test_v1_nearby_artifact_not_substituted_for_causal_timing_proof(self):
        v1 = self.catalog.query(subject_id="V1-CAUSAL-TIMING-INVALIDATION")[0]
        self.assertEqual(v1["history_disposition"], "REVIEW_STILL_REQUIRED")
        self.assertIn("not sufficient proof", v1["source_refs"][0]["note"].lower())

    def test_forced_flow_is_structural_memory_not_empirical_success(self):
        forced = self.catalog.query(subject_id="INSTITUTIONAL-FORCED-FLOWS")[0]
        self.assertEqual(forced["memory_action"], "PRESERVE_STRUCTURAL_MEMORY_ONLY")
        self.assertIn("never be promoted to empirical success", forced["claim_limit"].lower())

    def test_source_hash_validation_is_fail_closed(self):
        with self.assertRaises(ValueError):
            validate_source_ref({"kind": "GIT_BLOB", "blob_sha": "not-a-sha", "path": "x"})
        validate_source_ref({"kind": "GIT_BLOB", "blob_sha": "a" * 40, "path": "x"})

    def test_result_or_metric_fields_are_forbidden(self):
        base = self.catalog.query(subject_id="EVENT-DOCUMENTS")[0]
        base["result"] = "POSITIVE"
        with self.assertRaisesRegex(ValueError, "provenance-only"):
            validate_finding(base)

    def test_catalog_load_fails_if_it_claims_truth_store_authority(self):
        payload = json.loads(CATALOG.read_text())
        payload["scientific_truth_store"] = True
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.json"
            path.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                ArchaeologyCatalog.load(path)


if __name__ == "__main__":
    unittest.main()
