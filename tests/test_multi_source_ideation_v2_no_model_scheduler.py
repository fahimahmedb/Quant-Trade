from __future__ import annotations
import inspect
import unittest
from research.research_os import multi_source_ideation, policy_c_safe

class NoModelSchedulerTests(unittest.TestCase):
    def test_model_backend_and_safe_boundary_have_no_scheduler_methods(self):
        text=inspect.getsource(multi_source_ideation.ModelBackend).lower()+inspect.getsource(policy_c_safe.safe_policy_c).lower()
        for token in ("enqueue","schedule","lease","heartbeat","worker","oracle"):
            self.assertNotIn(token,text)

if __name__ == "__main__": unittest.main()
