from __future__ import annotations
import inspect
import unittest
from research.research_os import ideation_cycle

class CycleNoCandidateTests(unittest.TestCase):
    def test_cycle_coordinator_creates_zero_candidates(self):
        src=inspect.getsource(ideation_cycle.ideation_cycle)
        self.assertIn('"candidates_created": 0',src)
        self.assertNotIn("create_candidate",src.lower())

if __name__ == "__main__": unittest.main()
