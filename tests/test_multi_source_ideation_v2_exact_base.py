from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import BASE_SHA


class ExactBaseLawTests(unittest.TestCase):
    def test_embedded_base_law_is_wave2_immutable_base(self):
        self.assertEqual(BASE_SHA,"2b99d8aeb8a342f1ef32544247d366cb8a26037e")
        self.assertNotEqual(BASE_SHA,"97165db2faa3300cef1f23de0045ed93d25eb9cb")


if __name__ == "__main__": unittest.main()
