from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import build_context_snapshot

class SnapshotSchemaVersionTests(unittest.TestCase):
    def test_context_schema_version_is_explicit(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={}); self.assertEqual(s["schema_version"],"multi-source-ideation-context-v2")

if __name__ == "__main__": unittest.main()
