from __future__ import annotations
import unittest
from research.research_os.ideation_cycle import raw_proposal_receipt
from research.research_os.multi_source_ideation import raw_artifact

class ReceiptProvenanceCopyTests(unittest.TestCase):
    def test_receipt_defensively_copies_provenance(self):
        a=raw_artifact(policy_kind="INFORMATION_VALUE",status="NO_ACTION",context_snapshot_hash="h"); p={"nested":{"x":1}}
        r=raw_proposal_receipt(cycle_id="c",artifact=a,provenance=p); p["nested"]["x"]=2
        self.assertEqual(r["provenance"]["nested"]["x"],1)

if __name__ == "__main__": unittest.main()
