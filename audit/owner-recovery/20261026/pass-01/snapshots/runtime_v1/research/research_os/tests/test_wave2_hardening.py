from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from research.research_os.expansion.experiment_runner import DryRunExperimentRunner
from research.research_os.expansion.forward_v2 import ForwardRegistryV2
from research.research_os.expansion.source_qualification import ImmutableSourceRouteRegistry, qualify_source_route
from research.research_os.expansion.wave2_hardening import build_wave2_hardening


class Wave2HardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = Path("research/research_os")
        cls.base_fixture = json.loads((cls.base / "simulations" / "aggressive_architecture_fixture.json").read_text())
        cls.wave2_fixture = json.loads((cls.base / "simulations" / "wave2_hardening_fixture.json").read_text())
        cls.legacy_path = cls.base / "legacy" / "LEGACY_RESEARCH_LEDGER.imported.json"

    def build(self):
        return build_wave2_hardening(
            self.base_fixture,
            self.wave2_fixture,
            legacy_ledger_path=self.legacy_path if self.legacy_path.exists() else None,
        )

    def test_system_passes_while_blocking_unready_candidate(self) -> None:
        result = self.build()
        self.assertEqual(result["hardening_status"], "PASS")
        self.assertFalse(result["unsafe_access_detected"])
        self.assertEqual(result["source_registry"]["entry_count"], 5)
        self.assertTrue(all(item["status"] == "PASS" for item in result["source_qualifications"].values()))
        self.assertEqual(result["reproducibility"]["ready_count"], 4)
        self.assertEqual(result["reproducibility"]["blocked_count"], 1)
        self.assertEqual(result["dry_run_experiments"]["SYN-FLOW-001"]["status"], "BLOCK")
        self.assertEqual(result["validator_v2"]["SYN-FLOW-001"]["status"], "BLOCK")
        self.assertIn("protocol_frozen", result["validator_v2"]["SYN-FLOW-001"]["critical_failures"])
        self.assertEqual(result["validator_summary"]["pass_count"], 4)
        self.assertEqual(result["validator_summary"]["block_count"], 1)

    def test_no_empirical_portfolio_or_forward_authority(self) -> None:
        result = self.build()
        portfolio = result["portfolio_v2"]
        self.assertFalse(portfolio["return_series_consumed"])
        self.assertEqual(portfolio["statistical_correlation_matrix"], "UNAVAILABLE_BY_DESIGN")
        self.assertFalse(portfolio["capital_allocation_authorized"])
        self.assertFalse(portfolio["position_sizing_authorized"])
        self.assertFalse(portfolio["orders_authorized"])
        forward = result["forward_registry_v2"]
        self.assertEqual(forward["authorized_count"], 0)
        self.assertEqual(forward["observation_count"], 0)
        self.assertEqual(forward["future_outcomes_consumed"], 0)

    def test_outcome_bearing_source_route_is_blocked(self) -> None:
        route = copy.deepcopy(self.wave2_fixture["source_routes"]["SYN-QUANT-001"])
        route["contains_outcome"] = True
        qualification = qualify_source_route(route, freeze_time=self.wave2_fixture["freeze_time"])
        self.assertEqual(qualification["status"], "BLOCK")
        self.assertIn("UNAUTHORIZED_OUTCOME_BEARING_ROUTE", qualification["blockers"])
        self.assertFalse(qualification["outcome_accessed"])

    def test_source_route_registry_rejects_mutation(self) -> None:
        registry = ImmutableSourceRouteRegistry()
        route = self.wave2_fixture["source_routes"]["SYN-QUANT-001"]
        first = qualify_source_route(route, freeze_time=self.wave2_fixture["freeze_time"])
        registry.register(first)
        changed_route = copy.deepcopy(route)
        changed_route["revision_policy"] = "DIFFERENT_POLICY"
        changed = qualify_source_route(changed_route, freeze_time=self.wave2_fixture["freeze_time"])
        with self.assertRaises(ValueError):
            registry.register(changed)

    def test_dry_run_replay_rejects_plan_mutation(self) -> None:
        result = self.build()
        plan = copy.deepcopy(result["dry_run_experiments"]["SYN-QUANT-001"])
        runner = DryRunExperimentRunner()
        self.assertEqual(runner.replay(plan)["status"], "REPLAY_MATCH")
        plan["plan"]["seed"] = 999
        with self.assertRaises(ValueError):
            runner.replay(plan)

    def test_forward_observation_refused_without_owner_authority(self) -> None:
        result = self.build()
        registry = ForwardRegistryV2()
        contract = result["forward_contracts_v2"]["SYN-QUANT-001"]
        registry.register(contract)
        with self.assertRaises(PermissionError):
            registry.validate_observation_candidate(
                contract["contract_id"],
                {
                    "observed_at": "2026-10-17T00:00:00Z",
                    "scope": self.wave2_fixture["forward"]["SYN-QUANT-001"]["scope"],
                },
            )

    def test_wave2_is_deterministic(self) -> None:
        left = self.build()
        right = self.build()
        self.assertEqual(left, right)


if __name__ == "__main__":
    unittest.main()
