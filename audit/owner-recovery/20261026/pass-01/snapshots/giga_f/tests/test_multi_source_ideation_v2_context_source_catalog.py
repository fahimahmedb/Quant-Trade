from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import build_context_snapshot

class ContextSourceCatalogTests(unittest.TestCase):
    def test_source_catalog_ref_is_mandatory_for_same_cycle_source_truth(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref"); refs={k:k for k in keys}; refs["source_catalog_snapshot_ref"]=None
        with self.assertRaises(ValueError): build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs=refs,relevant_schema_versions={})

if __name__ == "__main__": unittest.main()
