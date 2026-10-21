from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import memory_lineage_check


class MemoryInvalidProtocolTests(unittest.TestCase):
    def test_invalid_protocol_is_not_negative(self):
        got=memory_lineage_check({"qualified":True,"scientific_disposition":"INVALID_PROTOCOL","same_semantic_family":True,"same_evidence":True})
        self.assertEqual(got["classification"],"INVALID_PROTOCOL"); self.assertNotEqual(got["classification"],"KNOWN_EXACT_NEGATIVE")


if __name__ == "__main__": unittest.main()
