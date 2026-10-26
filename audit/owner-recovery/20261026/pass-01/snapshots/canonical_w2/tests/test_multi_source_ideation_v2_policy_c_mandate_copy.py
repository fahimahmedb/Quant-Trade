from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import build_context_snapshot, policy_c

class MutatingBackend:
    backend_identity="mutating-fixture"; model_identity="fixture"
    def generate(self, mandate):
        mandate["nested"]["x"]=999
        return {"alternatives":[{"summary":"x"}],"selected_alternative_index":0}

class PolicyCMandateCopyTests(unittest.TestCase):
    def test_backend_cannot_mutate_caller_mandate(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={}); mandate={"nested":{"x":1}}
        policy_c(snapshot=s,backend=MutatingBackend(),mandate=mandate); self.assertEqual(mandate["nested"]["x"],1)

if __name__ == "__main__": unittest.main()
