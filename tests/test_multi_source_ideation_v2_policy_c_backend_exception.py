from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import build_context_snapshot, policy_c

class FailingBackend:
    backend_identity="failing-fixture"; model_identity="fixture"
    def generate(self, mandate): raise RuntimeError("backend down")

class PolicyCBackendExceptionTests(unittest.TestCase):
    def test_backend_exception_currently_propagates_and_is_not_silently_fallbacked(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})
        with self.assertRaises(RuntimeError): policy_c(snapshot=s,backend=FailingBackend(),mandate={})

if __name__ == "__main__": unittest.main()
