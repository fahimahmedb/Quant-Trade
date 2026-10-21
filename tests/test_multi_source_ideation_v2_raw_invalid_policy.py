from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import raw_artifact

class RawInvalidPolicyTests(unittest.TestCase):
    def test_unknown_policy_is_rejected(self):
        with self.assertRaises(ValueError): raw_artifact(policy_kind="FOURTH_POLICY",status="NO_PROPOSAL",context_snapshot_hash="h")

if __name__ == "__main__": unittest.main()
