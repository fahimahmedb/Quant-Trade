from __future__ import annotations
import unittest
from research.research_os.ideation_cycle import raw_proposal_receipt
from research.research_os.multi_source_ideation import raw_artifact

class ReceiptHashDeterminismTests(unittest.TestCase):
    def test_provenance_key_order_does_not_change_receipt(self):
        a=raw_artifact(policy_kind="INFORMATION_VALUE",status="NO_ACTION",context_snapshot_hash="h")
        x=raw_proposal_receipt(cycle_id="c",artifact=a,provenance={"a":1,"b":2})
        y=raw_proposal_receipt(cycle_id="c",artifact=a,provenance={"b":2,"a":1})
        self.assertEqual(x["receipt_id"],y["receipt_id"])

if __name__ == "__main__": unittest.main()
