from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import build_context_snapshot


class SnapshotSchemaTests(unittest.TestCase):
    def test_schema_versions_are_part_of_frozen_snapshot(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        a=build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={"memory":"v1"})
        b=build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={"memory":"v2"})
        self.assertNotEqual(a["context_snapshot_hash"],b["context_snapshot_hash"])


if __name__ == "__main__": unittest.main()
