from __future__ import annotations

from copy import deepcopy
import unittest

from research.research_os.expansion.economic_test_readiness_v1 import (
    ALLOWED_RED_TEAM_RIGHTS,
    build_preoutcome_execution_plan,
    freeze_economic_test_package,
    qualify_economic_test_readiness,
    red_team_economic_test_readiness,
    validate_economic_test_readiness,
    verify_preoutcome_execution_plan,
)


class EconomicTestReadinessV1Tests(unittest.TestCase):
    def setUp(self):
        self.engine_output = {
            "engine_id": "institutional-flow-engine.v1",
            "engine_family": "INSTITUTIONAL_FLOW",
            "synthetic_only": True,
            "source_refs": ["fixture://primary-rule"],
            "candidate": {
                "hypothesis_id": "SYN-READY-001",
                "generation_id": "G1",
                "mechanism": "constrained actor creates bounded directional pressure",
                "claim": "A predeclared expression can test the mechanism without changing it after outcomes.",
                "falsification_scope": "Reject if the preregistered net metric does not meet the decision map threshold.",
                "decision_map": {"PASS": "retain for independent review", "FAIL": "reject or park"},
                "economic_tags": ["forced-flow", "institutional-constraint"],
                "horizon": "PREDECLARED",
                "research_decision": "EXPLORE",
                "evidence_timing": "UNDETERMINED",
                "observation_authorization": "NOT_AUTHORIZED",
            },
        }
        self.implementability = {
            "hypothesis_id": "SYN-READY-001",
            "status": "PASS",
            "source_available": True,
            "pit_feasible": True,
            "expression_feasible": True,
            "cost_model_feasible": True,
            "capacity_observable": True,
            "operational_complexity": "LOW",
            "blockers": [],
        }
        self.sources = [{
            "route_id": "RULE-PRIMARY-001",
            "status": "PASS",
            "blockers": [],
            "route_hash": "route-hash-001",
            "freeze_time": "2026-10-15T20:00:00Z",
            "point_in_time_qualified": True,
            "outcome_accessed": False,
            "canonical_route": {
                "route_id": "RULE-PRIMARY-001",
                "source_class": "PRIMARY_PUBLIC",
                "transport": "fixture",
                "locator": "fixture://primary-rule",
                "permission_state": "FIXTURE_ONLY",
                "pit_mode": "VERSIONED_SNAPSHOT",
                "revision_policy": "PIN_VERSION",
                "survivorship_policy": "FULL_ELIGIBLE_UNIVERSE_AT_CLOCK",
                "timezone": "UTC",
                "availability_start": "2026-10-15T00:00:00Z",
                "contains_outcome": False,
                "content_scope": "PREOUTCOME_RULE_FACTS",
            },
        }]
        self.code_sha = "a" * 40
        self.environment_fingerprint = "env-lock-sha256:abc123"
        self.specification = {
            "universe_definition": {"rule": "eligible instruments under frozen rule set"},
            "clock": {"signal_time": "official publication timestamp", "entry_time": "next admissible clock", "timezone": "UTC"},
            "entry_definition": "First admissible observation after signal clock.",
            "exit_definition": "Frozen horizon exit; no outcome-dependent extension.",
            "position_expression": "Directional expression fixed from constrained-actor mechanism.",
            "benchmark": "Frozen benchmark definition if applicable.",
            "gross_metric": "preregistered gross return metric",
            "net_metric": "same metric net of declared costs",
            "cost_assumptions": {"model": "frozen deterministic schedule", "version": "v1"},
            "capacity_assumptions": {"observable": True, "method": "predeclared liquidity proxy"},
            "sample_window": {"start": "FROZEN_START", "end": "FROZEN_END"},
            "exclusions": ["predeclared data-quality exclusion only"],
            "missing_data_policy": "fail closed; no outcome-aware imputation",
            "revision_policy": "use only point-in-time version pinned by source snapshot",
            "survivorship_policy": "reconstruct eligible universe at each clock",
            "falsification_rule": self.engine_output["candidate"]["falsification_scope"],
            "decision_map": deepcopy(self.engine_output["candidate"]["decision_map"]),
            "observed_attempt_count": 0,
            "effective_trials_estimate": "UNKNOWN",
            "multiplicity_family": "SYN-FORCED-FLOW-FAMILY-001",
            "seed": 20261015,
            "environment": {"python": "pinned", "dependencies": "locked"},
            "code_sha": self.code_sha,
            "dependency_environment_fingerprint": self.environment_fingerprint,
        }
        self.identity = {
            "hypothesis_id": "SYN-READY-001",
            "generation_id": "G1",
            "mechanism": "constrained actor creates bounded directional pressure",
            "payer": "UNKNOWN",
            "actor": "constrained institutional actor",
            "timing": "PREDECLARED",
            "instrument": "eligible instrument set",
            "expected_capacity": "BOUNDED_UNKNOWN",
            "known_cost": "DECLARED_IN_PROTOCOL",
            "empirical_correlation": "UNKNOWN",
            "return_series_consumed": False,
        }
        self.portfolio = {
            "structural_overlap": "NOT_YET_COMPARED",
            "payer_overlap": "UNKNOWN",
            "actor_overlap": "UNKNOWN",
            "mechanism_overlap": "UNKNOWN",
            "timing_overlap": "UNKNOWN",
            "instrument_overlap": "UNKNOWN",
            "expected_capacity_overlap": "UNKNOWN",
            "known_cost_overlap": "UNKNOWN",
            "empirical_correlation": "UNKNOWN",
            "marginal_contribution": "NOT_ESTIMATED",
            "capital_allocation_authorized": False,
            "position_sizing_authorized": False,
            "orders_authorized": False,
        }

    def _package_and_plan(self):
        package = freeze_economic_test_package(
            engine_output=self.engine_output,
            implementability=self.implementability,
            source_qualifications=self.sources,
            specification=self.specification,
        )
        plan = build_preoutcome_execution_plan(package)
        return package, plan

    def _replay(self, package, plan, *, candidate=None, sources=None, code_sha=None, env=None):
        return verify_preoutcome_execution_plan(
            plan=plan,
            package=package,
            current_candidate=candidate or self.engine_output["candidate"],
            current_source_qualifications=sources or self.sources,
            current_code_sha=code_sha or self.code_sha,
            current_dependency_environment_fingerprint=env or self.environment_fingerprint,
        )

    def test_full_path_reaches_owner_authorization_barrier_only(self):
        result = qualify_economic_test_readiness(
            engine_output=self.engine_output,
            implementability=self.implementability,
            source_qualifications=self.sources,
            specification=self.specification,
            current_code_sha=self.code_sha,
            current_dependency_environment_fingerprint=self.environment_fingerprint,
            economic_identity=self.identity,
            portfolio_interpretation=self.portfolio,
        )
        self.assertEqual(result["status"], "READY_FOR_OWNER_AUTHORIZED_TEST")
        self.assertTrue(result["ready_for_authorized_economic_test"])
        self.assertEqual(result["validation"]["status"], "PASS")
        self.assertEqual(result["red_team"]["status"], "PASS")
        self.assertFalse(result["economic_execution_performed"])
        self.assertFalse(result["economic_outcome_accessed"])
        self.assertFalse(result["prospective_started"])
        self.assertEqual(result["authorization_barrier"], {
            "economic_experiment_authorized": False,
            "prospective_observation_authorized": False,
            "real_capital_authorized": False,
            "live_trading_authorized": False,
        })

    def test_frozen_package_contains_complete_preoutcome_contract(self):
        package, _ = self._package_and_plan()
        self.assertEqual(package["status"], "FROZEN_READY_NO_OUTCOME")
        self.assertTrue(package["protocol_hash"])
        protocol = package["protocol_payload"]
        for field in (
            "hypothesis_id", "generation_id", "candidate_hash", "source_snapshot_hashes",
            "universe_definition", "clock", "entry_definition", "exit_definition",
            "position_expression", "benchmark", "gross_metric", "net_metric",
            "cost_assumptions", "capacity_assumptions", "sample_window", "exclusions",
            "missing_data_policy", "revision_policy", "survivorship_policy",
            "falsification_rule", "decision_map", "observed_attempt_count",
            "effective_trials_estimate", "multiplicity_family", "seed", "environment",
            "code_sha", "dependency_environment_fingerprint",
        ):
            self.assertIn(field, protocol)
        self.assertFalse(package["economic_outcome_accessed"])
        self.assertEqual(package["economic_result"], "NOT_OBSERVED")

    def test_implementability_failure_parks_instead_of_being_massaged_to_pass(self):
        blocked = deepcopy(self.implementability)
        blocked.update(status="PARK_IMPLEMENTABILITY", cost_model_feasible=False,
                       blockers=["COST_MODEL_NOT_QUALIFIED"])
        package = freeze_economic_test_package(
            engine_output=self.engine_output,
            implementability=blocked,
            source_qualifications=self.sources,
            specification=self.specification,
        )
        self.assertEqual(package["status"], "BLOCK")
        self.assertIn("IMPLEMENTABILITY_BLOCKED", package["blockers"])
        self.assertIsNone(package["protocol_hash"])

    def test_candidate_and_generation_drift_fail_closed(self):
        package, plan = self._package_and_plan()
        changed = deepcopy(self.engine_output["candidate"])
        changed["claim"] = "mutated after freeze"
        replay = self._replay(package, plan, candidate=changed)
        self.assertEqual(replay["status"], "BLOCK")
        self.assertIn("CANDIDATE_CHANGED", replay["blockers"])

        changed_generation = deepcopy(self.engine_output["candidate"])
        changed_generation["generation_id"] = "G2"
        replay = self._replay(package, plan, candidate=changed_generation)
        self.assertIn("GENERATION_CHANGED", replay["blockers"])

    def test_source_drift_fails_closed(self):
        package, plan = self._package_and_plan()
        changed_sources = deepcopy(self.sources)
        changed_sources[0]["route_hash"] = "route-hash-mutated"
        replay = self._replay(package, plan, sources=changed_sources)
        self.assertEqual(replay["status"], "BLOCK")
        self.assertIn("SOURCE_CHANGED", replay["blockers"])

    def test_protocol_and_plan_mutation_fail_closed(self):
        package, plan = self._package_and_plan()
        mutated_package = deepcopy(package)
        mutated_package["protocol_payload"]["entry_definition"] = "post-freeze mutation"
        replay = self._replay(mutated_package, plan)
        self.assertEqual(replay["status"], "BLOCK")
        self.assertIn("PROTOCOL_CHANGED", replay["blockers"])

        mutated_plan = deepcopy(plan)
        mutated_plan["binding"]["seed"] = 999
        replay = self._replay(package, mutated_plan)
        self.assertIn("EXECUTION_PLAN_MUTATED", replay["blockers"])

    def test_code_and_environment_drift_fail_closed(self):
        package, plan = self._package_and_plan()
        replay = self._replay(package, plan, code_sha="b" * 40)
        self.assertIn("CODE_BINDING_CHANGED", replay["blockers"])
        replay = self._replay(package, plan, env="env-lock-sha256:different")
        self.assertIn("ENVIRONMENT_BINDING_CHANGED", replay["blockers"])

    def test_validator_returns_explicit_blockers_without_repair(self):
        package, plan = self._package_and_plan()
        replay = self._replay(package, plan)
        broken_impl = deepcopy(self.implementability)
        broken_impl["status"] = "PARK_IMPLEMENTABILITY"
        validation = validate_economic_test_readiness(
            engine_output=self.engine_output,
            implementability=broken_impl,
            package=package,
            plan=plan,
            replay=replay,
            economic_identity=self.identity,
            portfolio_interpretation=self.portfolio,
        )
        self.assertEqual(validation["status"], "BLOCK")
        self.assertIn("IMPLEMENTABILITY", validation["blockers"])
        self.assertFalse(validation["signal_repaired"])
        self.assertFalse(validation["claim_mutated"])
        self.assertFalse(validation["economic_execution_authorized"])

    def test_red_team_is_negative_rights_only(self):
        validation = {"status": "BLOCK", "blockers": ["PIT", "CAPACITY", "REPRODUCIBILITY"]}
        red = red_team_economic_test_readiness(validation)
        self.assertEqual(red["status"], "BLOCK")
        self.assertEqual(red["negative_rights"], ["CAPACITY", "PIT", "REPRODUCIBILITY"])
        self.assertTrue(set(red["negative_rights"]).issubset(ALLOWED_RED_TEAM_RIGHTS))
        self.assertFalse(red["repair_attempted"])
        self.assertFalse(red["optimization_attempted"])
        self.assertFalse(red["claim_mutated"])

    def test_trial_accounting_and_multiplicity_are_predeclared(self):
        bad = deepcopy(self.specification)
        bad["observed_attempt_count"] = -1
        bad["effective_trials_estimate"] = None
        bad["multiplicity_family"] = "UNKNOWN"
        package = freeze_economic_test_package(
            engine_output=self.engine_output,
            implementability=self.implementability,
            source_qualifications=self.sources,
            specification=bad,
        )
        self.assertEqual(package["status"], "BLOCK")
        self.assertIn("TRIAL_ACCOUNTING_INVALID", package["blockers"])
        self.assertIn("UNQUALIFIED_MULTIPLICITY_FAMILY", package["blockers"])


if __name__ == "__main__":
    unittest.main()
