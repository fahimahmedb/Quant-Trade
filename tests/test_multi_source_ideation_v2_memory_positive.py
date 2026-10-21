from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import memory_lineage_check

class MemoryPositiveTests(unittest.TestCase):
    def test_positive_related_history_is_not_promoted_to_truth(self):
        got=memory_lineage_check({"qualified":True,"scientific_disposition":"POSITIVE","same_semantic_family":True,"same_evidence":True})
        self.assertEqual(got["classification"],"RELATED_NOT_DISPOSITIVE")

if __name__ == "__main__": unittest.main()
