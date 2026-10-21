from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import DeterministicFakeBackend, build_context_snapshot
from research.research_os.policy_c_safe import safe_policy_c

class SafeMalformedTests(unittest.TestCase):
    def test_malformed_output_preserves_source_failed_semantics(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})
        a,r=safe_policy_c(snapshot=s,backend=DeterministicFakeBackend({"bad":1}),mandate={})
        self.assertEqual(a["status"],"SOURCE_FAILED"); self.assertIsNone(r)

if __name__ == "__main__": unittest.main()
