from __future__ import annotations

import unittest

from research.research_os.ideation_cycle import ideation_cycle, raw_proposal_receipt
from research.research_os.multi_source_ideation import build_context_snapshot, raw_artifact


def ctx():
    keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
    return build_context_snapshot(ideation_cycle_id="right",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})


class CycleIdentityTests(unittest.TestCase):
    def test_receipts_from_other_cycle_do_not_satisfy_barrier(self):
        c=ctx(); h=c["context_snapshot_hash"]
        arts=[raw_artifact(policy_kind=p,status=s,context_snapshot_hash=h) for p,s in (("SYSTEMATIC_COVERAGE","NO_PROPOSAL"),("INFORMATION_VALUE","NO_ACTION"),("DIVERGENT_EXPLORATION","SOURCE_UNAVAILABLE"))]
        receipts=[raw_proposal_receipt(cycle_id="wrong",artifact=a,provenance={"x":1}) for a in arts]
        got=ideation_cycle(cycle_id="right",context_snapshot=c,artifacts=arts,receipts=receipts)
        self.assertEqual(got["status"],"WAITING_FOR_RECEIPTS"); self.assertFalse(got["intake_allowed"])


if __name__ == "__main__": unittest.main()
