from __future__ import annotations
import inspect
import unittest
from research.research_os import multi_source_ideation

class CoreNoOperationalTests(unittest.TestCase):
    def test_core_does_not_execute_tasks_producers_or_trades(self):
        src=inspect.getsource(multi_source_ideation).lower()
        for token in ("enqueue_task(","run_producer(","execute_experiment(","place_order(","oracle_worker"):
            self.assertNotIn(token,src)

if __name__ == "__main__": unittest.main()
