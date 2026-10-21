from __future__ import annotations

import unittest

from research.research_os.ideation_cycle import raw_proposal_receipt
from research.research_os.multi_source_ideation import raw_artifact


class ReceiptOutcomeFirewallTests(unittest.TestCase):
    def test_raw_receipt_marks_outcome_access_false(self):
        a=raw_artifact(policy_kind="INFORMATION_VALUE",status="NO_ACTION",context_snapshot_hash="h")
        r=raw_proposal_receipt(cycle_id="c",artifact=a,provenance={"decision":"r"})
        self.assertFalse(r["outcome_accessed"])


if __name__ == "__main__": unittest.main()
