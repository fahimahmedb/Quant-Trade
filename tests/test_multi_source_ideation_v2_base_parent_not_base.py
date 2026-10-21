from __future__ import annotations
from pathlib import Path
import unittest
from research.research_os.multi_source_ideation import BASE_SHA

class ParentNotBaseTests(unittest.TestCase):
    def test_historical_parent_is_not_embedded_as_base(self):
        self.assertEqual(BASE_SHA,"2b99d8aeb8a342f1ef32544247d366cb8a26037e")
        self.assertNotEqual(BASE_SHA,"97165db2faa3300cef1f23de0045ed93d25eb9cb")

if __name__ == "__main__": unittest.main()
