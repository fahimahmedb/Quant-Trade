from __future__ import annotations
import inspect
import unittest
from research.research_os import ideation_cycle, multi_source_ideation, multi_source_ideation_bindings, multi_source_ideation_hardening, policy_c_safe

class NoSiblingRefsTests(unittest.TestCase):
    def test_implementation_does_not_bind_sibling_builder_branches(self):
        text="\n".join(inspect.getsource(m) for m in (ideation_cycle,multi_source_ideation,multi_source_ideation_bindings,multi_source_ideation_hardening,policy_c_safe))
        for token in ("builder/mega-b","builder/mega-c0","builder/mega-d0","builder/mega-e","builder/convergence-wave2-canonical"):
            self.assertNotIn(token,text)

if __name__ == "__main__": unittest.main()
