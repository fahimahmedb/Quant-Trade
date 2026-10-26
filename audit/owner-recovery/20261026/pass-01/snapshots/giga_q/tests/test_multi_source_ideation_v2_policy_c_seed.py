from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import DeterministicFakeBackend, build_context_snapshot, policy_c

class PolicyCSeedTests(unittest.TestCase):
    def test_incomplete_selected_alternative_is_seed_with_receipt(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})
        a,r=policy_c(snapshot=s,backend=DeterministicFakeBackend({"alternatives":[{"summary":"direction"}],"selected_alternative_index":0}),mandate={})
        self.assertEqual(a["status"],"SEED_EMITTED"); self.assertIsNotNone(r); self.assertTrue(a["payload"]["needs_discovery_synthesis"])

if __name__ == "__main__": unittest.main()
