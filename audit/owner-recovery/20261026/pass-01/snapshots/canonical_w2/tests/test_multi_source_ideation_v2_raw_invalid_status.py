from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import raw_artifact

class RawInvalidStatusTests(unittest.TestCase):
    def test_operational_status_is_rejected(self):
        for status in ("READY","RUNNING","LEASED"):
            with self.subTest(status=status):
                with self.assertRaises(ValueError): raw_artifact(policy_kind="SYSTEMATIC_COVERAGE",status=status,context_snapshot_hash="h")

if __name__ == "__main__": unittest.main()
