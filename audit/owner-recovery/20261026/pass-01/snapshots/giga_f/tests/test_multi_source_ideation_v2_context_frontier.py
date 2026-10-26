from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import build_context_snapshot

class ContextFrontierTests(unittest.TestCase):
    def test_frontier_and_evidence_refs_are_mandatory(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref"); refs={k:k for k in keys}
        for missing in ("frontier_snapshot_ref","evidence_snapshot_ref"):
            x=dict(refs); x[missing]=""
            with self.subTest(missing=missing):
                with self.assertRaises(ValueError): build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs=x,relevant_schema_versions={})

if __name__ == "__main__": unittest.main()
