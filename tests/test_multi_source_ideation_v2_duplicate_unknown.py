from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import duplicate_check


class DuplicateUnknownTests(unittest.TestCase):
    def test_missing_identity_is_unknown_not_distinct(self):
        self.assertEqual(duplicate_check({},[])["classification"],"UNKNOWN")
        self.assertEqual(duplicate_check({"identity":{"mechanism":"UNKNOWN"}},[])["classification"],"UNKNOWN")


if __name__ == "__main__": unittest.main()
