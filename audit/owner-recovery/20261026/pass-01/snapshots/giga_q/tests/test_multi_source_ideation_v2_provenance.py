from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import raw_artifact
from research.research_os.ideation_cycle import raw_proposal_receipt


class ProvenanceReceiptTests(unittest.TestCase):
    def test_receipt_binds_artifact_and_provenance(self):
        a=raw_artifact(policy_kind="SYSTEMATIC_COVERAGE",status="SEED_EMITTED",context_snapshot_hash="h",artifact_kind="IDEATION_SEED",payload={"x":1})
        r1=raw_proposal_receipt(cycle_id="c",artifact=a,provenance={"packet_hash":"a"})
        r2=raw_proposal_receipt(cycle_id="c",artifact=a,provenance={"packet_hash":"b"})
        self.assertNotEqual(r1["receipt_id"],r2["receipt_id"])
        self.assertEqual(r1["artifact_hash"],r2["artifact_hash"])


if __name__ == "__main__": unittest.main()
