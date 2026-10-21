from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import ancestry_check

class AncestryTests(unittest.TestCase):
    def test_lineage_intersection_is_ancestry_match(self):
        got=ancestry_check({"ancestor_ids":["root"]},[{"proposal_id":"other","ancestor_ids":["root"]}])
        self.assertEqual(got["classification"],"ANCESTRY_MATCH")
    def test_nonintersecting_explicit_lineage_is_distinct(self):
        got=ancestry_check({"ancestor_ids":["a"]},[{"proposal_id":"b","ancestor_ids":["c"]}])
        self.assertEqual(got["classification"],"DISTINCT")

if __name__ == "__main__": unittest.main()
