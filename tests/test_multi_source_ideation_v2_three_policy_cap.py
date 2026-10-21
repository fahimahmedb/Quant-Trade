from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import POLICIES, barrier, raw_artifact

class ThreePolicyCapTests(unittest.TestCase):
    def test_exactly_one_terminal_artifact_per_policy_is_complete_cycle(self):
        h="h"; rows=[raw_artifact(policy_kind=p,status="NO_PROPOSAL",context_snapshot_hash=h) for p in POLICIES]
        got=barrier(rows,h); self.assertTrue(got["intake_allowed"]); self.assertEqual(len(got["artifacts"]),3)

if __name__ == "__main__": unittest.main()
