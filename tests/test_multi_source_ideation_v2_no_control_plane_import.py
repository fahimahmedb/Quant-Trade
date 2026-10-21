from __future__ import annotations
import inspect
import unittest
from research.research_os import ideation_cycle, multi_source_ideation, multi_source_ideation_bindings, multi_source_ideation_hardening, policy_c_safe

class NoControlPlaneImportTests(unittest.TestCase):
    def test_no_direct_control_plane_dependency(self):
        text="\n".join(inspect.getsource(m).lower() for m in (ideation_cycle,multi_source_ideation,multi_source_ideation_bindings,multi_source_ideation_hardening,policy_c_safe))
        self.assertNotIn("from control_plane",text); self.assertNotIn("import control_plane",text)

if __name__ == "__main__": unittest.main()
