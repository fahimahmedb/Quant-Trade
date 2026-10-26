from __future__ import annotations

import inspect
import unittest

from research.research_os import ideation_cycle, multi_source_ideation, multi_source_ideation_bindings, multi_source_ideation_hardening


class NoSchedulerAuthorityTests(unittest.TestCase):
    def test_no_scheduler_mutation_api(self):
        text="\n".join(inspect.getsource(m).lower() for m in (ideation_cycle,multi_source_ideation,multi_source_ideation_bindings,multi_source_ideation_hardening))
        for token in ("enqueue_task(","schedule_task(","scheduler_mutation=true","ready_task_created=true"):
            self.assertNotIn(token,text)


if __name__ == "__main__": unittest.main()
