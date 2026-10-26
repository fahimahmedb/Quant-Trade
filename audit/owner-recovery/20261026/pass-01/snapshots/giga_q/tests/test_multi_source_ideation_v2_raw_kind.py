from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import raw_artifact

class RawKindTests(unittest.TestCase):
    def test_candidate_kind_is_rejected(self):
        with self.assertRaises(ValueError): raw_artifact(policy_kind="DIVERGENT_EXPLORATION",status="PROPOSAL_EMITTED",context_snapshot_hash="h",artifact_kind="CANDIDATE")

if __name__ == "__main__": unittest.main()
