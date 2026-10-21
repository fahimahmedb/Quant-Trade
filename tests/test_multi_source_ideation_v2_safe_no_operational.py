from __future__ import annotations
import inspect
import unittest
from research.research_os import policy_c_safe

class SafeBoundaryNoOperationalTests(unittest.TestCase):
    def test_safe_boundary_only_converts_runtime_failure(self):
        src=inspect.getsource(policy_c_safe).lower()
        for token in ("enqueue","ready_task","candidate_id","oracle","broker","experiment"):
            self.assertNotIn(token,src)
        self.assertIn("external_backend_failure",src)

if __name__ == "__main__": unittest.main()
