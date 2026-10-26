from __future__ import annotations

import unittest

from research.research_os.ideation_cycle import ideation_cycle, raw_proposal_receipt
from research.research_os.multi_source_ideation import build_context_snapshot, raw_artifact


class CycleOutcomeFirewallTests(unittest.TestCase):
    def test_completed_cycle_still_has_outcome_accessed_false(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        c=build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={}); h=c["context_snapshot_hash"]
        arts=[raw_artifact(policy_kind=p,status=s,context_snapshot_hash=h) for p,s in (("SYSTEMATIC_COVERAGE","NO_PROPOSAL"),("INFORMATION_VALUE","NO_ACTION"),("DIVERGENT_EXPLORATION","SOURCE_UNAVAILABLE"))]
        rec=[raw_proposal_receipt(cycle_id="c",artifact=a,provenance={"p":1}) for a in arts]
        got=ideation_cycle(cycle_id="c",context_snapshot=c,artifacts=arts,receipts=rec)
        self.assertFalse(got["outcome_accessed"]); self.assertEqual(got["ready_tasks_created"],0)


if __name__ == "__main__": unittest.main()
