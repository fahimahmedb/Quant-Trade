from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import DeterministicFakeBackend, build_context_snapshot, policy_c

class PolicyCUnknownFieldsTests(unittest.TestCase):
    def test_unknown_causal_field_downgrades_to_seed(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={}); idea={"summary":"x","mechanism":"m","payer":"p","actor":"a","clock":"UNKNOWN","universe":"u","falsifier":"f"}
        a,_=policy_c(snapshot=s,backend=DeterministicFakeBackend({"alternatives":[idea],"selected_alternative_index":0}),mandate={}); self.assertEqual(a["artifact_kind"],"IDEATION_SEED")

if __name__ == "__main__": unittest.main()
