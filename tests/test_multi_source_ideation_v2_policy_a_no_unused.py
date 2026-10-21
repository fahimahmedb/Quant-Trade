from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import build_context_snapshot
from research.research_os.multi_source_ideation_bindings import systematic_coverage_from_frontier

class PolicyANoUnusedTests(unittest.TestCase):
    def test_both_canonical_no_source_statuses_map_to_no_admissible_novel_source(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="a",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={}); d={"action":"GENERATE_MECHANISM","executable":True}
        for status in ("NO_ADMISSIBLE_DOCUMENTARY_SOURCE","NO_UNUSED_ADMISSIBLE_SOURCE"):
            out=systematic_coverage_from_frontier(snapshot=s,frontier_decision=d,source_plan={"status":status}); self.assertEqual(out["status"],"NO_ADMISSIBLE_NOVEL_SOURCE")

if __name__ == "__main__": unittest.main()
