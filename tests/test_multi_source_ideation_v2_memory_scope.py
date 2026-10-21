from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import memory_lineage_check


class MemoryScopeTests(unittest.TestCase):
    def test_same_family_negative_with_different_evidence_is_conditional_not_exact(self):
        got=memory_lineage_check({"qualified":True,"scientific_disposition":"NEGATIVE","same_semantic_family":True,"same_evidence":False})
        self.assertEqual(got["classification"],"KNOWN_FAMILY_CONDITIONAL_NEGATIVE")

    def test_unrelated_negative_does_not_suppress(self):
        got=memory_lineage_check({"qualified":True,"scientific_disposition":"NEGATIVE","same_semantic_family":False,"same_evidence":True})
        self.assertEqual(got["classification"],"NO_QUALIFIED_MATCH")


if __name__ == "__main__": unittest.main()
