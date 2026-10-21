from __future__ import annotations
import inspect
import unittest
from research.research_os import multi_source_ideation_bindings

class BindingsNoOperationalTests(unittest.TestCase):
    def test_bindings_do_not_execute_source_or_research_actions(self):
        src=inspect.getsource(multi_source_ideation_bindings).lower()
        for token in ("run_producer(","acquire_evidence(","create_task(","execute_action(","enqueue"):
            self.assertNotIn(token,src)

if __name__ == "__main__": unittest.main()
