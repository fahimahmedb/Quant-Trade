from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import barrier, raw_artifact


class BarrierStatusTests(unittest.TestCase):
    def test_three_nonproposal_terminal_states_complete_barrier(self):
        h="h"; rows=[
            raw_artifact(policy_kind="SYSTEMATIC_COVERAGE",status="NO_ADMISSIBLE_NOVEL_SOURCE",context_snapshot_hash=h),
            raw_artifact(policy_kind="INFORMATION_VALUE",status="NO_ACTION",context_snapshot_hash=h),
            raw_artifact(policy_kind="DIVERGENT_EXPLORATION",status="SOURCE_FAILED",context_snapshot_hash=h),
        ]
        got=barrier(rows,h); self.assertEqual(got["status"],"BARRIER_COMPLETE"); self.assertTrue(got["intake_allowed"])


if __name__ == "__main__": unittest.main()
