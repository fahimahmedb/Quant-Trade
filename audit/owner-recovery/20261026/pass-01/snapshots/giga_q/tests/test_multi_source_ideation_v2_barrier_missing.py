from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import barrier, raw_artifact


class BarrierMissingTests(unittest.TestCase):
    def test_missing_policy_is_reported_deterministically(self):
        h="h"; a=raw_artifact(policy_kind="SYSTEMATIC_COVERAGE",status="NO_PROPOSAL",context_snapshot_hash=h)
        got=barrier([a],h)
        self.assertEqual(got["status"],"WAITING_FOR_TERMINAL_STATES")
        self.assertEqual(got["missing"],["DIVERGENT_EXPLORATION","INFORMATION_VALUE"])


if __name__ == "__main__": unittest.main()
