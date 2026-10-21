from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import memory_lineage_check


class MemoryBlockedTests(unittest.TestCase):
    def test_blocked_is_blocked_data_not_negative(self):
        got=memory_lineage_check({"qualified":True,"scientific_disposition":"BLOCKED","same_semantic_family":True,"same_evidence":True})
        self.assertEqual(got["classification"],"BLOCKED_DATA"); self.assertNotEqual(got["classification"],"KNOWN_EXACT_NEGATIVE")


if __name__ == "__main__": unittest.main()
