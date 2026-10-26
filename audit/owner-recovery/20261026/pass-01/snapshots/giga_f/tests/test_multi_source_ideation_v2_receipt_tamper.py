from __future__ import annotations

import unittest

from research.research_os.ideation_cycle import raw_proposal_receipt
from research.research_os.multi_source_ideation import raw_artifact


class ReceiptTamperEvidenceTests(unittest.TestCase):
    def test_artifact_mutation_changes_receipt_identity(self):
        a=raw_artifact(policy_kind="DIVERGENT_EXPLORATION",status="SEED_EMITTED",context_snapshot_hash="h",artifact_kind="IDEATION_SEED",payload={"mechanism":"m"})
        r1=raw_proposal_receipt(cycle_id="c",artifact=a,provenance={"backend":"fixture"})
        a["payload"]["mechanism"]="changed"
        r2=raw_proposal_receipt(cycle_id="c",artifact=a,provenance={"backend":"fixture"})
        self.assertNotEqual(r1["artifact_hash"],r2["artifact_hash"]); self.assertNotEqual(r1["receipt_id"],r2["receipt_id"])


if __name__ == "__main__": unittest.main()
