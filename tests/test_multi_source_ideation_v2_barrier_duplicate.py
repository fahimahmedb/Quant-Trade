from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import barrier, raw_artifact

class BarrierDuplicateTests(unittest.TestCase):
    def test_duplicate_policy_terminal_is_invalid_even_if_identical(self):
        a=raw_artifact(policy_kind="SYSTEMATIC_COVERAGE",status="NO_PROPOSAL",context_snapshot_hash="h")
        with self.assertRaises(ValueError): barrier([a,a],"h")

if __name__ == "__main__": unittest.main()
