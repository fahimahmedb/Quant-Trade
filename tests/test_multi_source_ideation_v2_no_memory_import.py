from __future__ import annotations
import inspect
import unittest
from research.research_os import multi_source_ideation, multi_source_ideation_hardening

class NoMemoryImportTests(unittest.TestCase):
    def test_memory_screen_is_consumed_as_data_not_reimplemented_store(self):
        text="\n".join(inspect.getsource(m).lower() for m in (multi_source_ideation,multi_source_ideation_hardening))
        self.assertNotIn("scientificmemorystore",text); self.assertNotIn("create_memory",text)

if __name__ == "__main__": unittest.main()
