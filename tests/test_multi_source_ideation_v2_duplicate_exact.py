from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import duplicate_check


class DuplicateExactTests(unittest.TestCase):
    def test_normalized_exact_identity_is_duplicate(self):
        p={"identity":{"mechanism":" M ","payer":"P","actor":"A","clock":"C","universe":"U"}}
        known=[{"proposal_id":"old","identity":{"mechanism":"m","payer":"p","actor":"a","clock":"c","universe":"u"}}]
        got=duplicate_check(p,known); self.assertEqual(got["classification"],"EXACT_DUPLICATE"); self.assertEqual(got["match_id"],"old")


if __name__ == "__main__": unittest.main()
