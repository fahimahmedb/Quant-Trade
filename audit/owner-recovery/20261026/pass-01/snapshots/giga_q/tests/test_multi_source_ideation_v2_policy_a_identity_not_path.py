from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import build_context_snapshot
from research.research_os.multi_source_ideation_bindings import systematic_coverage_from_frontier

class PolicyAIdentityNotPathTests(unittest.TestCase):
    def test_renaming_source_path_does_not_change_content_identity(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="a",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={}); d={"action":"GENERATE_MECHANISM","executable":True}
        def emit(path): return systematic_coverage_from_frontier(snapshot=s,frontier_decision=d,source_plan={"status":"SOURCE_SELECTED","source":{"path":path,"packet_hash":"same"}})
        self.assertEqual(emit("a")["payload"]["source_identity"],emit("b")["payload"]["source_identity"])

if __name__ == "__main__": unittest.main()
