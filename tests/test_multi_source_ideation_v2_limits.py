from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import DeterministicFakeBackend, policy_c, build_context_snapshot


def snap():
    keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
    return build_context_snapshot(ideation_cycle_id="l",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})


class IdeationBoundednessTests(unittest.TestCase):
    def test_policy_c_rejects_more_than_five_alternatives(self):
        response={"alternatives":[{"summary":str(i)} for i in range(6)],"selected_alternative_index":0}
        artifact,_=policy_c(snapshot=snap(),backend=DeterministicFakeBackend(response),mandate={})
        self.assertEqual(artifact["status"],"SOURCE_FAILED")

    def test_policy_c_emits_only_selected_alternative(self):
        complete={"summary":"chosen","mechanism":"m","payer":"p","actor":"a","clock":"c","universe":"u","falsifier":"f"}
        response={"alternatives":[{"summary":"not chosen"},complete,{"summary":"also not chosen"}],"selected_alternative_index":1}
        artifact,receipt=policy_c(snapshot=snap(),backend=DeterministicFakeBackend(response),mandate={})
        self.assertEqual(artifact["payload"]["summary"],"chosen")
        self.assertEqual(receipt["alternative_count"],3)
        self.assertEqual(receipt["selected_alternative_index"],1)


if __name__ == "__main__": unittest.main()
