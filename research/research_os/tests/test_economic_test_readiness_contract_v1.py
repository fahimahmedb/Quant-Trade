from __future__ import annotations

import unittest

from research.research_os.expansion.economic_test_readiness_v1 import implementability_contract


class EconomicTestReadinessContractV1Tests(unittest.TestCase):
    def test_pass_contract_exposes_all_required_fields_and_no_blocking_reason(self):
        raw = {
            "status": "PASS",
            "source_available": True,
            "pit_feasible": True,
            "expression_feasible": True,
            "cost_model_feasible": True,
            "capacity_observable": True,
            "operational_complexity": "LOW",
            "blockers": [],
        }
        frozen = implementability_contract(raw)
        self.assertEqual(frozen["status"], "PASS")
        for field in (
            "source_available", "pit_feasible", "expression_feasible",
            "cost_model_feasible", "capacity_observable", "operational_complexity",
            "blocking_reason",
        ):
            self.assertIn(field, frozen)
        self.assertIsNone(frozen["blocking_reason"])

    def test_park_contract_preserves_first_blocker_as_blocking_reason(self):
        raw = {
            "status": "PARK_IMPLEMENTABILITY",
            "source_available": True,
            "pit_feasible": True,
            "expression_feasible": True,
            "cost_model_feasible": False,
            "capacity_observable": False,
            "operational_complexity": "MEDIUM",
            "blockers": ["COST_MODEL_NOT_QUALIFIED", "CAPACITY_NOT_OBSERVABLE"],
        }
        frozen = implementability_contract(raw)
        self.assertEqual(frozen["status"], "PARK_IMPLEMENTABILITY")
        self.assertEqual(frozen["blocking_reason"], "COST_MODEL_NOT_QUALIFIED")
        self.assertEqual(frozen["blockers"], raw["blockers"])


if __name__ == "__main__":
    unittest.main()
