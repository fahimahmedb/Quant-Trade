from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import proposal_identity

class HashDeterminismTests(unittest.TestCase):
    def test_mapping_key_order_does_not_change_proposal_identity(self):
        a=proposal_identity(policy_kind="SYSTEMATIC_COVERAGE",context_snapshot_hash="h",payload={"a":1,"b":2},provenance={"x":1,"y":2})
        b=proposal_identity(policy_kind="SYSTEMATIC_COVERAGE",context_snapshot_hash="h",payload={"b":2,"a":1},provenance={"y":2,"x":1})
        self.assertEqual(a["proposal_id"],b["proposal_id"])

if __name__ == "__main__": unittest.main()
