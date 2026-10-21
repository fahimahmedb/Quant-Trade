from __future__ import annotations
import unittest
from research.research_os.ideation_cycle import ideation_cycle
from research.research_os.multi_source_ideation import build_context_snapshot

class CycleSchemaTests(unittest.TestCase):
    def test_waiting_cycle_schema_version_is_explicit(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        c=build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={}); got=ideation_cycle(cycle_id="c",context_snapshot=c,artifacts=[],receipts=[])
        self.assertEqual(got["schema_version"],"ideation-cycle-v2"); self.assertFalse(got["intake_allowed"])

if __name__ == "__main__": unittest.main()
