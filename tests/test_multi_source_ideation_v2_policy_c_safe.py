from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import build_context_snapshot
from research.research_os.policy_c_safe import safe_policy_c

class FailingBackend:
    backend_identity="failing-fixture"; model_identity="fixture"
    def generate(self, mandate): raise RuntimeError("backend down")

class PolicyCSafeTests(unittest.TestCase):
    def test_external_runtime_exception_becomes_source_failed_without_fallback(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})
        a,r=safe_policy_c(snapshot=s,backend=FailingBackend(),mandate={})
        self.assertEqual(a["status"],"SOURCE_FAILED"); self.assertEqual(a["reason"],"EXTERNAL_BACKEND_FAILURE:RuntimeError"); self.assertIsNone(r)

if __name__ == "__main__": unittest.main()
