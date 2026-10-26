from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import DeterministicFakeBackend, build_context_snapshot, policy_c


def snap():
    keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
    return build_context_snapshot(ideation_cycle_id="ps",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})


class ProposalVsSeedTests(unittest.TestCase):
    def test_incomplete_causal_identity_is_seed_not_proposal(self):
        incomplete={"summary":"x","mechanism":"m","universe":"u","falsifier":"f"}
        a,_=policy_c(snapshot=snap(),backend=DeterministicFakeBackend({"alternatives":[incomplete],"selected_alternative_index":0}),mandate={})
        self.assertEqual(a["status"],"SEED_EMITTED"); self.assertEqual(a["artifact_kind"],"IDEATION_SEED")
        self.assertTrue(a["payload"]["needs_discovery_synthesis"])


if __name__ == "__main__": unittest.main()
