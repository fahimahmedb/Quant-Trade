from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import DeterministicFakeBackend, policy_c, build_context_snapshot


def snap():
    keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
    return build_context_snapshot(ideation_cycle_id="g",created_at="2026-10-21T20:00:00Z",refs={k:k+":v" for k in keys},relevant_schema_versions={})


class PolicyCGptOssTruthTests(unittest.TestCase):
    def test_missing_runtime_is_explicit_source_unavailable(self):
        artifact, receipt=policy_c(snapshot=snap(),backend=None,mandate={"prompt_contract_version":"v2"})
        self.assertEqual(artifact["status"],"SOURCE_UNAVAILABLE")
        self.assertEqual(artifact["reason"],"EXTERNAL_RUNTIME_MISSING")
        self.assertIsNone(receipt)

    def test_fake_backend_identifies_itself_as_fixture_not_gpt_oss(self):
        idea={"summary":"x","mechanism":"m","payer":"p","actor":"a","clock":"c","universe":"u","falsifier":"f"}
        artifact, receipt=policy_c(snapshot=snap(),backend=DeterministicFakeBackend({"alternatives":[idea],"selected_alternative_index":0}),mandate={"prompt_contract_version":"v2"})
        self.assertEqual(receipt["backend_identity"],"deterministic-fake")
        self.assertEqual(receipt["model_identity"],"fixture-v1")
        self.assertNotIn("gpt-oss",receipt["backend_identity"].lower())
        self.assertEqual(artifact["status"],"PROPOSAL_EMITTED")


if __name__ == "__main__": unittest.main()
