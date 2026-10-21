from __future__ import annotations
import inspect
import unittest
from research.research_os import policy_c_safe

class SafeNoAuthorityTests(unittest.TestCase):
    def test_safe_boundary_has_no_operational_authority(self):
        src=inspect.getsource(policy_c_safe).lower()
        for token in ("enqueue","scheduler","oracle","candidate","experiment","trade","portfolio"):
            self.assertNotIn(token,src)

if __name__ == "__main__": unittest.main()
