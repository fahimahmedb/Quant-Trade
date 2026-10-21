from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import build_context_snapshot
from research.research_os.multi_source_ideation_bindings import information_value_from_research_intelligence

class PolicyBMissingTests(unittest.TestCase):
    def test_missing_action_is_no_action_not_invented(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="b",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})
        out=information_value_from_research_intelligence(snapshot=s,decision={}); self.assertEqual(out["status"],"NO_ACTION"); self.assertIsNone(out["artifact_kind"])

if __name__ == "__main__": unittest.main()
