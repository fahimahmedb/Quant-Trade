from __future__ import annotations

import inspect
import unittest

from research.research_os import ideation_cycle, multi_source_ideation, multi_source_ideation_bindings, multi_source_ideation_hardening


class NoSecondMemoryTests(unittest.TestCase):
    def test_no_scientific_memory_store_is_created(self):
        names=[]
        for m in (ideation_cycle,multi_source_ideation,multi_source_ideation_bindings,multi_source_ideation_hardening): names.extend(n.lower() for n,_ in inspect.getmembers(m))
        for forbidden in ("scientificmemorystore","scientific_memory_store","memory_registry","second_memory"):
            self.assertNotIn(forbidden,names)


if __name__ == "__main__": unittest.main()
