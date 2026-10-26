from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import DeterministicFakeBackend, build_context_snapshot
from research.research_os.policy_c_safe import safe_policy_c

class NoOutcomeMandateTests(unittest.TestCase):
    def test_truthy_outcome_access_flag_is_rejected(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})
        for value in (True,1,"yes"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError): safe_policy_c(snapshot=s,backend=DeterministicFakeBackend({}),mandate={"outcome_accessed":value})

if __name__ == "__main__": unittest.main()
