from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import DeterministicFakeBackend, build_context_snapshot, policy_c

class PolicyCSelectionCriteriaTests(unittest.TestCase):
    def test_missing_selection_criteria_is_explicit_unknown_not_invented(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})
        _,r=policy_c(snapshot=s,backend=DeterministicFakeBackend({"alternatives":[{"summary":"x"}],"selected_alternative_index":0}),mandate={})
        self.assertEqual(r["selection_criteria"],"UNKNOWN")

if __name__ == "__main__": unittest.main()
