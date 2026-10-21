from __future__ import annotations
import inspect
import unittest
from research.research_os import multi_source_ideation_hardening

class HardeningNoOperationalTests(unittest.TestCase):
    def test_hardening_module_contains_no_worker_runtime(self):
        src=inspect.getsource(multi_source_ideation_hardening).lower()
        for token in ("heartbeat(","lease_expiry","worker_loop","oracle_worker","enqueue_task("):
            self.assertNotIn(token,src)

if __name__ == "__main__": unittest.main()
