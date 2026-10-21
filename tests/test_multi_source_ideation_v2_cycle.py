from __future__ import annotations

import unittest

from research.research_os.ideation_cycle import ideation_cycle, proposal_disposition, raw_proposal_receipt
from research.research_os.multi_source_ideation import build_context_snapshot, raw_artifact


def context():
    keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
    return build_context_snapshot(ideation_cycle_id="cycle",created_at="2026-10-21T20:00:00Z",refs={k:k+":v" for k in keys},relevant_schema_versions={"memory":"v1"})


class IdeationCycleV2Tests(unittest.TestCase):
    def test_cycle_requires_all_terminal_receipts(self):
        c=context(); h=c["context_snapshot_hash"]
        artifacts=[
            raw_artifact(policy_kind="SYSTEMATIC_COVERAGE",status="NO_PROPOSAL",context_snapshot_hash=h),
            raw_artifact(policy_kind="INFORMATION_VALUE",status="NO_ACTION",context_snapshot_hash=h),
            raw_artifact(policy_kind="DIVERGENT_EXPLORATION",status="SOURCE_UNAVAILABLE",context_snapshot_hash=h),
        ]
        receipts=[raw_proposal_receipt(cycle_id="cycle",artifact=a,provenance={"source":"test"}) for a in artifacts[:2]]
        got=ideation_cycle(cycle_id="cycle",context_snapshot=c,artifacts=artifacts,receipts=receipts)
        self.assertEqual(got["status"],"WAITING_FOR_RECEIPTS"); self.assertFalse(got["intake_allowed"])
        receipts.append(raw_proposal_receipt(cycle_id="cycle",artifact=artifacts[2],provenance={"source":"runtime-unavailable"}))
        got=ideation_cycle(cycle_id="cycle",context_snapshot=c,artifacts=artifacts,receipts=receipts)
        self.assertEqual(got["status"],"BARRIER_COMPLETE"); self.assertTrue(got["intake_allowed"])
        self.assertEqual(got["ready_tasks_created"],0); self.assertEqual(got["candidates_created"],0)

    def test_receipt_is_deterministic_and_outcome_free(self):
        c=context(); a=raw_artifact(policy_kind="SYSTEMATIC_COVERAGE",status="NO_PROPOSAL",context_snapshot_hash=c["context_snapshot_hash"])
        x=raw_proposal_receipt(cycle_id="cycle",artifact=a,provenance={"source":"s"})
        y=raw_proposal_receipt(cycle_id="cycle",artifact=a,provenance={"source":"s"})
        self.assertEqual(x,y); self.assertFalse(x["outcome_accessed"])

    def test_disposition_is_not_operational_or_scientific_admission(self):
        got=proposal_disposition(proposal_id="p",intake_decision={"decision":"ELIGIBLE_FOR_DISCOVERY","eligible_for_discovery":True},lineage={"classification":"NO_QUALIFIED_MATCH"},duplicate={"classification":"DISTINCT"},implementability={"admissible":True})
        self.assertTrue(got["eligible_for_discovery"]); self.assertFalse(got["operational_admission"])
        self.assertEqual(got["scientific_verdict"],"NOT_PERFORMED"); self.assertEqual(got["economic_result"],"NOT_OBSERVED")


if __name__ == "__main__": unittest.main()
