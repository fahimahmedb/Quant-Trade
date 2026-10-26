from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import combine_duplicate_evidence

class DuplicateCombineTests(unittest.TestCase):
    def test_unrecognized_semantic_class_requires_review(self):
        got=combine_duplicate_evidence(semantic={"classification":"MAGIC"},ancestry={"classification":"DISTINCT"})
        self.assertEqual(got["classification"],"REVIEW_REQUIRED")
    def test_explicit_ancestry_overrides_semantic_distinct(self):
        got=combine_duplicate_evidence(semantic={"classification":"DISTINCT"},ancestry={"classification":"ANCESTRY_MATCH"})
        self.assertEqual(got["classification"],"ANCESTRY_MATCH")

if __name__ == "__main__": unittest.main()
