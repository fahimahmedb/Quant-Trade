from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import build_context_snapshot
from research.research_os.multi_source_ideation_bindings import (
    canonical_source_identity, information_value_from_research_intelligence,
    systematic_coverage_from_frontier,
)


def snap():
    keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
    return build_context_snapshot(ideation_cycle_id="x",created_at="2026-10-21T20:00:00Z",refs={k:k+":v" for k in keys},relevant_schema_versions={"memory":"scientific-memory-v1"})


class CanonicalIdeationBindingTests(unittest.TestCase):
    def test_source_identity_prefers_packet_content_over_path(self):
        self.assertEqual(canonical_source_identity({"path":"renamed.json","packet_hash":"abc","record_hash":"r"}),"packet_hash:abc")

    def test_policy_a_accepts_actual_frontier_source_planner_shape(self):
        plan={"status":"SOURCE_SELECTED","frontier_id":"F1","family":"EVENT_DOCUMENT","source":{"path":"p","packet_hash":"abc","record_hash":"r","blob_sha":"b","source_ref":"s"}}
        decision={"action":"GENERATE_MECHANISM","executable":True,"uncertainty_resolved":"identity"}
        out=systematic_coverage_from_frontier(snapshot=snap(),frontier_decision=decision,source_plan=plan)
        self.assertEqual(out["status"],"SEED_EMITTED"); self.assertEqual(out["payload"]["source_identity"],"packet_hash:abc")
        self.assertTrue(out["payload"]["needs_discovery_synthesis"])

    def test_policy_a_preserves_canonical_no_unused_source_semantics(self):
        for status in ("NO_ADMISSIBLE_DOCUMENTARY_SOURCE","NO_UNUSED_ADMISSIBLE_SOURCE"):
            out=systematic_coverage_from_frontier(snapshot=snap(),frontier_decision={"action":"GENERATE_MECHANISM","executable":True},source_plan={"status":status})
            self.assertEqual(out["status"],"NO_ADMISSIBLE_NOVEL_SOURCE")

    def test_policy_b_does_not_create_second_ranking_truth(self):
        decision={"action":"RUN_PRODUCER","executable":True,"candidate_id":"c","reason_codes":["CHEAPEST_ADMISSIBLE_FALSIFIER"],"uncertainty_resolved":"u","selected_action":{"action":"RUN_PRODUCER","cost_units":1}}
        out=information_value_from_research_intelligence(snapshot=snap(),decision=decision)
        self.assertEqual(out["artifact_kind"],"IDEATION_SEED")
        self.assertEqual(out["payload"]["ranking_authority"],"RESEARCH_INTELLIGENCE_REUSED_NOT_REIMPLEMENTED")
        self.assertEqual(out["payload"]["selected_action"],decision["selected_action"])

    def test_non_executable_research_decision_is_no_action(self):
        out=information_value_from_research_intelligence(snapshot=snap(),decision={"action":"RUN_PRODUCER","executable":False})
        self.assertEqual(out["status"],"NO_ACTION")


if __name__ == "__main__": unittest.main()
