from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import DeterministicFakeBackend, build_context_snapshot
from research.research_os.policy_c_safe import safe_policy_c

class NoTaskFieldsPolicyCTests(unittest.TestCase):
    def test_policy_c_artifact_has_no_operational_task_identity(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})
        idea={"summary":"x","mechanism":"m","payer":"p","actor":"a","clock":"c","universe":"u","falsifier":"f"}; a,_=safe_policy_c(snapshot=s,backend=DeterministicFakeBackend({"alternatives":[idea],"selected_alternative_index":0}),mandate={})
        for forbidden in ("task_id","lease_id","worker_id","oracle_task_id","candidate_id"): self.assertNotIn(forbidden,a["payload"])

if __name__ == "__main__": unittest.main()
