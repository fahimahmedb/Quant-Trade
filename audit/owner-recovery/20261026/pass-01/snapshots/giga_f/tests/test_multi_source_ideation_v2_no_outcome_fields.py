from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import DeterministicFakeBackend, build_context_snapshot, policy_c


def snap():
    keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
    return build_context_snapshot(ideation_cycle_id="o",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})


class OutcomeFirewallTests(unittest.TestCase):
    def test_policy_c_receipt_contains_no_empirical_outcome_claims(self):
        idea={"summary":"x","mechanism":"m","payer":"p","actor":"a","clock":"c","universe":"u","falsifier":"f"}
        _, receipt=policy_c(snapshot=snap(),backend=DeterministicFakeBackend({"alternatives":[idea],"selected_alternative_index":0}),mandate={})
        forbidden={"pnl","return","sharpe","profit","outcome","economic_result","win_rate"}
        self.assertTrue(forbidden.isdisjoint({str(k).lower() for k in receipt.keys()}))


if __name__ == "__main__": unittest.main()
