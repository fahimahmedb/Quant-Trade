from __future__ import annotations
import inspect
import unittest
from research.research_os import ideation_cycle

class CycleNoReadyTests(unittest.TestCase):
    def test_cycle_coordinator_has_no_ready_state(self):
        src=inspect.getsource(ideation_cycle.ideation_cycle)
        self.assertNotIn('"READY"',src); self.assertIn('"ready_tasks_created": 0',src)

if __name__ == "__main__": unittest.main()
