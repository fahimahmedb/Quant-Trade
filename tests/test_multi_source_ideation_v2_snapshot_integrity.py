from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import build_context_snapshot, validate_policy_input


class SnapshotIntegrityTests(unittest.TestCase):
    def test_mutation_after_freeze_is_detected(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="i",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={"a":"1"})
        validate_policy_input(s)
        s["memory_snapshot_ref"]="changed"
        with self.assertRaises(ValueError): validate_policy_input(s)


if __name__ == "__main__": unittest.main()
