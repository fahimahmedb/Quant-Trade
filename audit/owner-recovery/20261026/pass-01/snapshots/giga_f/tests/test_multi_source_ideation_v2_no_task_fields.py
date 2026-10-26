from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import build_context_snapshot
from research.research_os.multi_source_ideation_bindings import information_value_from_research_intelligence, systematic_coverage_from_frontier

class NoTaskFieldsTests(unittest.TestCase):
    def test_policy_a_and_b_artifacts_have_no_operational_task_identity(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})
        rows=[systematic_coverage_from_frontier(snapshot=s,frontier_decision={"action":"GENERATE_MECHANISM","executable":True},source_plan={"status":"SOURCE_SELECTED","source":{"packet_hash":"p"}}),information_value_from_research_intelligence(snapshot=s,decision={"action":"RUN_PRODUCER","executable":True})]
        for row in rows:
            for forbidden in ("task_id","lease_id","worker_id","oracle_task_id"): self.assertNotIn(forbidden,row.get("payload",{}))

if __name__ == "__main__": unittest.main()
