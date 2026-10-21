from __future__ import annotations

import inspect
import unittest

from research.research_os import ideation_cycle, multi_source_ideation, multi_source_ideation_bindings, multi_source_ideation_hardening


class NoCrossLaneOwnershipTests(unittest.TestCase):
    def test_no_discovery_adjudication_economic_runtime_implementation_symbols(self):
        source="\n".join(inspect.getsource(m).lower() for m in (ideation_cycle,multi_source_ideation,multi_source_ideation_bindings,multi_source_ideation_hardening))
        forbidden=(
            "class candidate", "class experiment", "class validator", "class redteam",
            "economicidentity", "shadowbook", "oracleworker", "scheduler", "lease_expiry",
            "live_trading_authorized = true", "real_capital_authorized = true",
        )
        for token in forbidden:
            with self.subTest(token=token): self.assertNotIn(token,source)


if __name__ == "__main__": unittest.main()
