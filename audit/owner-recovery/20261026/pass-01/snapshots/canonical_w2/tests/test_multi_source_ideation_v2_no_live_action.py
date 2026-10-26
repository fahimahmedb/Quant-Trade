from __future__ import annotations

import inspect
import unittest

from research.research_os import ideation_cycle, multi_source_ideation, multi_source_ideation_bindings, multi_source_ideation_hardening


class NoLiveActionTests(unittest.TestCase):
    def test_no_broker_order_or_live_execution_calls(self):
        text="\n".join(inspect.getsource(m).lower() for m in (ideation_cycle,multi_source_ideation,multi_source_ideation_bindings,multi_source_ideation_hardening))
        for token in ("place_order(","submit_order(","broker.","trade_republic","interactive_brokers","live_execution("):
            self.assertNotIn(token,text)


if __name__ == "__main__": unittest.main()
