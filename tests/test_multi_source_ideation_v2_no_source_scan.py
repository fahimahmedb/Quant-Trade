from __future__ import annotations
import inspect
import unittest
from research.research_os import multi_source_ideation_bindings

class NoSourceScanTests(unittest.TestCase):
    def test_policy_a_does_not_scan_repository_for_sources(self):
        src=inspect.getsource(multi_source_ideation_bindings.systematic_coverage_from_frontier).lower()
        for token in ("pathlib","os.walk","glob","github","requests.get","open("):
            self.assertNotIn(token,src)

if __name__ == "__main__": unittest.main()
