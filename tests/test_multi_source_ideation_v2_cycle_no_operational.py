from __future__ import annotations
import inspect
import unittest
from research.research_os import ideation_cycle

class CycleNoOperationalTests(unittest.TestCase):
    def test_cycle_module_contains_no_queue_or_worker_primitives(self):
        src=inspect.getsource(ideation_cycle).lower()
        for token in ("lease_owner","heartbeat","retry_at","worker_owner","enqueue_task","oracle_worker"):
            self.assertNotIn(token,src)

if __name__ == "__main__": unittest.main()
