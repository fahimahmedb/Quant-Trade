from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import DeterministicFakeBackend, build_context_snapshot, policy_c


class PolicyCReceiptTests(unittest.TestCase):
    def test_receipt_contains_required_backend_and_selection_proof(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})
        idea={"summary":"x","mechanism":"m","payer":"p","actor":"a","clock":"c","universe":"u","falsifier":"f"}
        _,r=policy_c(snapshot=s,backend=DeterministicFakeBackend({"alternatives":[idea],"selected_alternative_index":0,"selection_criteria":"causal"}),mandate={"prompt_contract_version":"v2"})
        for k in ("alternative_count","alternative_summaries","selection_criteria","selected_alternative_index","selected_proposal","raw_response_hash","backend_identity","model_identity","prompt_contract_version","context_snapshot_hash","semantic_retry_count"):
            self.assertIn(k,r)


if __name__ == "__main__": unittest.main()
