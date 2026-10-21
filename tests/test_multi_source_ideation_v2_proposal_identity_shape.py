from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import proposal_identity

class ProposalIdentityShapeTests(unittest.TestCase):
    def test_identity_contains_only_hash_bounded_provenance(self):
        p=proposal_identity(policy_kind="SYSTEMATIC_COVERAGE",context_snapshot_hash="h",payload={"x":1},provenance={"source":"s"})
        self.assertEqual(set(p),{"policy_kind","context_snapshot_hash","payload_hash","provenance_hash","proposal_id"})

if __name__ == "__main__": unittest.main()
