from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import DeterministicFakeBackend, build_context_snapshot, policy_c

class PolicyCPromptContractTests(unittest.TestCase):
    def test_prompt_contract_version_is_receipted(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="p",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})
        _,r=policy_c(snapshot=s,backend=DeterministicFakeBackend({"alternatives":[{"summary":"x"}],"selected_alternative_index":0}),mandate={"prompt_contract_version":"divergent-v2"})
        self.assertEqual(r["prompt_contract_version"],"divergent-v2")

if __name__ == "__main__": unittest.main()
