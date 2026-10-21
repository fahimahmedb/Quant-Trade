from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import barrier, raw_artifact


class MaxThreePolicyArtifactTests(unittest.TestCase):
    def test_duplicate_policy_cannot_create_fourth_artifact(self):
        h="h"
        rows=[
            raw_artifact(policy_kind="SYSTEMATIC_COVERAGE",status="NO_PROPOSAL",context_snapshot_hash=h),
            raw_artifact(policy_kind="INFORMATION_VALUE",status="NO_ACTION",context_snapshot_hash=h),
            raw_artifact(policy_kind="DIVERGENT_EXPLORATION",status="SOURCE_UNAVAILABLE",context_snapshot_hash=h),
            raw_artifact(policy_kind="DIVERGENT_EXPLORATION",status="NO_PROPOSAL",context_snapshot_hash=h),
        ]
        with self.assertRaises(ValueError): barrier(rows,h)


if __name__ == "__main__": unittest.main()
