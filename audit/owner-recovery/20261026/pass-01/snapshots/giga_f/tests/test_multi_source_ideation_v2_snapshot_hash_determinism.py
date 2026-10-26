from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import build_context_snapshot

class SnapshotHashDeterminismTests(unittest.TestCase):
    def test_schema_mapping_order_does_not_change_context_hash(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref"); refs={k:k for k in keys}
        a=build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs=refs,relevant_schema_versions={"a":"1","b":"2"})
        b=build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs=refs,relevant_schema_versions={"b":"2","a":"1"})
        self.assertEqual(a["context_snapshot_hash"],b["context_snapshot_hash"])

if __name__ == "__main__": unittest.main()
