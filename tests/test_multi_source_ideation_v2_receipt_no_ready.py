from __future__ import annotations
import unittest
from research.research_os.ideation_cycle import raw_proposal_receipt
from research.research_os.multi_source_ideation import raw_artifact

class ReceiptNoReadyTests(unittest.TestCase):
    def test_receipt_has_no_operational_admission_fields(self):
        a=raw_artifact(policy_kind="INFORMATION_VALUE",status="NO_ACTION",context_snapshot_hash="h"); r=raw_proposal_receipt(cycle_id="c",artifact=a,provenance={})
        for forbidden in ("ready","task_id","lease_id","worker_id","candidate_id"): self.assertNotIn(forbidden,r)

if __name__ == "__main__": unittest.main()
