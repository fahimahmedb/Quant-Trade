from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import DeterministicFakeBackend, build_context_snapshot, policy_c


def snap():
    keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
    return build_context_snapshot(ideation_cycle_id="m",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})


class PolicyCMalformedTests(unittest.TestCase):
    def test_empty_alternatives_fail(self):
        a,_=policy_c(snapshot=snap(),backend=DeterministicFakeBackend({"alternatives":[],"selected_alternative_index":0}),mandate={})
        self.assertEqual(a["status"],"SOURCE_FAILED")

    def test_out_of_range_selection_fails(self):
        a,_=policy_c(snapshot=snap(),backend=DeterministicFakeBackend({"alternatives":[{"summary":"x"}],"selected_alternative_index":1}),mandate={})
        self.assertEqual(a["status"],"SOURCE_FAILED")

    def test_non_mapping_selected_alternative_fails(self):
        a,_=policy_c(snapshot=snap(),backend=DeterministicFakeBackend({"alternatives":["x"],"selected_alternative_index":0}),mandate={})
        self.assertEqual(a["status"],"SOURCE_FAILED")


if __name__ == "__main__": unittest.main()
