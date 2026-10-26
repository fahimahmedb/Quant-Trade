from __future__ import annotations

import unittest

from research.research_os.ideation_cycle import raw_proposal_receipt
from research.research_os.multi_source_ideation import raw_artifact


class ReceiptCycleTests(unittest.TestCase):
    def test_cycle_identity_changes_receipt_identity(self):
        a=raw_artifact(policy_kind="INFORMATION_VALUE",status="NO_ACTION",context_snapshot_hash="h")
        x=raw_proposal_receipt(cycle_id="a",artifact=a,provenance={"s":1})
        y=raw_proposal_receipt(cycle_id="b",artifact=a,provenance={"s":1})
        self.assertNotEqual(x["receipt_id"],y["receipt_id"])


if __name__ == "__main__": unittest.main()
