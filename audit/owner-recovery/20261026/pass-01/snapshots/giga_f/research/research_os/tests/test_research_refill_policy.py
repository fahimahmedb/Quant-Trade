from __future__ import annotations

import unittest

from research.research_os.queue_replenisher import derive_refill_task, validate_derived_task
from research.research_os.research_refill_policy import evaluate_frontier_mandates


def frontier():
    return {
        "schema_version": "research-frontier-v1",
        "status": "ACTIVE",
        "selection_policy": "LOWEST_ISSUED_COUNT_THEN_HIGHEST_PRIORITY_THEN_FRONTIER_ID",
        "max_new_tasks_per_refill": 1,
        "max_issued_per_frontier": 1,
        "require_global_queue_empty": True,
        "require_legacy_screen_before_freeze": True,
        "producer_execution_same_refill_wake": False,
        "recursive_refill_same_wake": False,
        "authority": {
            "economic_experiment_authorized": False,
            "prospective_observation_authorized": False,
            "real_capital_authorized": False,
            "live_trading_authorized": False,
        },
        "frontiers": [{
            "frontier_id": "F1",
            "enabled": True,
            "priority": 70,
            "task_type": "QUANT_MECHANISM",
            "required_capability": "quant_mechanisms",
            "target_lane": "market_discovery",
            "objective": "generate one bounded mechanism identity",
            "allowed_actions": ["research mechanism", "legacy duplicate check", "freeze hypothesis"],
            "forbidden_actions": ["backtest", "capital allocation", "live trading"],
            "success_condition": "one candidate or durable no-candidate",
        }],
    }


def registry(active=True):
    return {
        "capabilities": [{
            "capability_id": "quant_mechanisms",
            "production_enabled": active,
        }]
    }


def lanes(active=True):
    return {
        "lanes": [{
            "lane_id": "market_discovery",
            "enabled": active,
            "capabilities": ["quant_mechanisms"],
        }]
    }


def policy_context(*, route_active=True, search_complete=False, archaeology_complete=False):
    return {
        "capability_registry": registry(),
        "workflow_lanes": lanes(route_active),
        "search_space_complete": search_complete,
        "archaeology_complete": archaeology_complete,
    }


class ResearchRefillPolicyTests(unittest.TestCase):
    def test_generation_mandate_does_not_claim_unknown_identity_novel(self):
        entry = frontier()["frontiers"][0]
        result = evaluate_frontier_mandates(
            [entry],
            capability_registry=registry(),
            workflow_lanes=lanes(),
        )
        self.assertEqual(result["frontier_state"]["state"], "ACTIVE_ACTIONABLE")
        decision = result["decisions"][0]
        self.assertEqual(decision["action"], "GENERATE_MECHANISM")
        self.assertTrue(decision["executable"])
        self.assertEqual(decision["novelty_status"], "UNRESOLVED_NOT_CLAIMED")
        self.assertFalse(decision["identity"]["resolved"])
        self.assertIn("UNKNOWN_IDENTITY_IS_NOT_NOVELTY", decision["reason_codes"])
        self.assertFalse(decision["scheduler_mutation"])
        self.assertFalse(result["scientific_claims"]["novelty_claimed"])

    def test_declared_capability_with_inactive_route_is_not_available(self):
        entry = frontier()["frontiers"][0]
        result = evaluate_frontier_mandates(
            [entry],
            capability_registry=registry(),
            workflow_lanes=lanes(False),
        )
        self.assertEqual(result["frontier_state"]["state"], "CAPABILITY_MISSING")
        self.assertEqual(result["noop_status"], "NOOP_CAPABILITY_MISSING")
        self.assertFalse(result["decisions"][0]["executable"])
        self.assertIn("ROUTE_INACTIVE", result["decisions"][0]["blockers"])

    def test_missing_source_is_a_source_block_not_scientific_exhaustion(self):
        entry = frontier()["frontiers"][0]
        result = evaluate_frontier_mandates(
            [entry],
            capability_registry=registry(),
            workflow_lanes=lanes(),
            source_plans={"F1": {"status": "NO_UNUSED_ADMISSIBLE_SOURCE", "source": None}},
        )
        self.assertEqual(result["frontier_state"]["state"], "SOURCE_MISSING")
        self.assertEqual(result["noop_status"], "NOOP_SOURCE_MISSING")
        self.assertFalse(result["frontier_state"]["scientifically_exhausted"])

    def test_empty_search_is_not_exhausted_without_explicit_completion(self):
        result = evaluate_frontier_mandates(
            [],
            capability_registry=registry(),
            workflow_lanes=lanes(),
        )
        self.assertEqual(result["frontier_state"]["state"], "SEARCH_SPACE_INCOMPLETE")
        self.assertEqual(result["noop_status"], "NOOP_SEARCH_SPACE_INCOMPLETE")
        self.assertFalse(result["frontier_state"]["scientifically_exhausted"])

    def test_true_exhaustion_requires_search_and_archaeology_completion(self):
        result = evaluate_frontier_mandates(
            [],
            capability_registry=registry(),
            workflow_lanes=lanes(),
            search_space_complete=True,
            archaeology_complete=True,
        )
        self.assertEqual(result["frontier_state"]["state"], "SCIENTIFICALLY_EXHAUSTED")
        self.assertEqual(result["noop_status"], "NOOP_FRONTIER_SCIENTIFICALLY_EXHAUSTED")
        self.assertTrue(result["frontier_state"]["scientifically_exhausted"])

    def test_queue_replenisher_binds_policy_without_becoming_scheduler(self):
        result = derive_refill_task(
            frontier=frontier(),
            tasks=[],
            created_at="2026-10-21T10:00:00Z",
            research_policy_context=policy_context(),
        )
        self.assertEqual(result["status"], "DERIVED_ONE_READY_TASK")
        self.assertFalse(result["research_intelligence"]["scheduler_mutation"])
        task = result["task"]
        contract = task["inputs"]["research_intelligence_contract"]
        self.assertEqual(contract["action_class"], "GENERATE_MECHANISM")
        self.assertEqual(contract["novelty_status"], "UNRESOLVED_NOT_CLAIMED")
        self.assertTrue(contract["semantic_identity_required_before_novelty"])
        self.assertFalse(task["derivation"]["research_intelligence"]["decision"]["scheduler_mutation"])
        validate_derived_task(task)

    def test_issue_limit_is_not_relabelled_scientific_exhaustion(self):
        prior = {
            "task_id": "OLD",
            "status": "COMPLETE",
            "derivation": {"frontier_id": "F1", "derivation_key": "old"},
        }
        result = derive_refill_task(
            frontier=frontier(),
            tasks=[prior],
            created_at="2026-10-21T10:00:00Z",
            research_policy_context=policy_context(),
        )
        self.assertEqual(result["status"], "NOOP_SEARCH_SPACE_INCOMPLETE")
        self.assertFalse(result["research_intelligence"]["frontier_state"]["scientifically_exhausted"])

    def test_explicit_completion_can_seal_exhaustion_but_production_does_not_invent_it(self):
        prior = {
            "task_id": "OLD",
            "status": "COMPLETE",
            "derivation": {"frontier_id": "F1", "derivation_key": "old"},
        }
        result = derive_refill_task(
            frontier=frontier(),
            tasks=[prior],
            created_at="2026-10-21T10:00:00Z",
            research_policy_context=policy_context(search_complete=True, archaeology_complete=True),
        )
        self.assertEqual(result["status"], "NOOP_FRONTIER_SCIENTIFICALLY_EXHAUSTED")
        self.assertTrue(result["research_intelligence"]["frontier_state"]["scientifically_exhausted"])


if __name__ == "__main__":
    unittest.main()
