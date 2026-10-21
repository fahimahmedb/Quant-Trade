from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import DeterministicFakeBackend, build_context_snapshot, policy_c


class PolicyCHashTests(unittest.TestCase):
    def test_response_hash_changes_when_model_output_changes(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="h",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})
        def receipt(summary):
            idea={"summary":summary,"mechanism":"m","payer":"p","actor":"a","clock":"c","universe":"u","falsifier":"f"}
            return policy_c(snapshot=s,backend=DeterministicFakeBackend({"alternatives":[idea],"selected_alternative_index":0}),mandate={})[1]
        self.assertNotEqual(receipt("a")["raw_response_hash"],receipt("b")["raw_response_hash"])


if __name__ == "__main__": unittest.main()
