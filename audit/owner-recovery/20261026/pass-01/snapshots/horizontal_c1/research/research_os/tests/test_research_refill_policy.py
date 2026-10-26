from __future__ import annotations

from copy import deepcopy
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
    def test_c1_unknown_queue_states_refuse_both_legacy_and_mega_a_refill(self):
        for task in ({'task_id': 'NO-STATUS'},
                     {'task_id': 'UNKNOWN', 'status': 'UNKNOWN'},
                     {'task_id': 'FUTURE', 'status': 'UNSUPPORTED_FUTURE_STATE'}):
            for context in (None, policy_context()):
                for catalog in (None, {}):
                    with self.subTest(task=task, policy=context is not None, catalog=catalog):
                        result = derive_refill_task(
                            frontier=frontier(), tasks=[task], created_at='2026-10-21T10:00:00Z',
                            research_policy_context=context, source_catalog=catalog,
                        )
                        self.assertEqual(result['status'], 'BLOCKED_UNKNOWN_TASK_STATUS')
                        self.assertEqual(result['queue']['unknown_count'], 1)
                        self.assertIsNone(result['task'])

    def test_c1_failed_attempt_is_terminal_and_keeps_mega_a_followup_policy(self):
        result = derive_refill_task(
            frontier=frontier(), tasks=[{'task_id': 'ATTEMPT', 'status': 'FAILED'}],
            created_at='2026-10-21T10:00:00Z', research_policy_context=policy_context(),
        )
        self.assertEqual(result['queue']['terminal_count'], 1)
        self.assertEqual(result['queue']['unknown_count'], 0)
        self.assertEqual(result['status'], 'DERIVED_ONE_READY_TASK')
        self.assertFalse(result['research_intelligence']['scientific_claims']['novelty_claimed'])
        self.assertFalse(result['research_intelligence']['scheduler_mutation'])
        self.assertIn('policy_hash', result['task']['derivation']['research_intelligence'])
        self.assertTrue(all(result['task']['authority'][k] is False for k in (
            'economic_experiment_authorized', 'prospective_observation_authorized',
            'real_capital_authorized', 'live_trading_authorized')))

    def test_c1_native_v2_unknown_queue_refusal_is_durable_and_resumable(self):
        from tests.test_research_os_v2_worker_integration import V2WorkerIntegrationTests
        from research.research_os.oracle_worker_v2 import build_v2_worker
        from research.research_os.github_state import PREFIX
        helper = V2WorkerIntegrationTests()
        harness, worker = helper.real_worker()
        self.addCleanup(helper.doCleanups)
        def change_status(status):
            def mutate(snapshot):
                writes = {}
                for task in snapshot.tasks():
                    changed = deepcopy(task)
                    changed['status'] = status
                    writes[PREFIX + 'tasks/' + task['task_id'] + '.json'] = changed
                return writes
            harness.remote_change(mutate)
        before = harness.count_paths('tasks/')
        change_status('UNSUPPORTED_FUTURE_STATE')
        result = worker.wake()
        self.assertEqual(result['status'], 'BLOCKED_UNKNOWN_TASK_STATUS')
        self.assertEqual(result['queue']['unknown_count'], before)
        with harness.store.snapshot() as snapshot:
            wakes = [snapshot.read(p) for p in snapshot.blobs if '/runtime/worker_wakes/' in p]
        self.assertTrue(any(w['status'] == 'BLOCKED_UNKNOWN_TASK_STATUS' for w in wakes))
        restarted = build_v2_worker(helper.worker_config(), store=harness.store, backend=harness.model)
        restarted.now = lambda: harness.now
        self.assertEqual(restarted.wake()['status'], 'BLOCKED_UNKNOWN_TASK_STATUS')
        self.assertEqual(harness.count_paths('tasks/'), before)
        self.assertEqual(harness.model.calls, 0)
        change_status('FAILED')
        corrected = restarted.wake()
        self.assertNotEqual(corrected['status'], 'BLOCKED_UNKNOWN_TASK_STATUS')
        from research.research_os.queue_replenisher import queue_summary
        with harness.store.snapshot() as snapshot:
            summary = queue_summary(snapshot.tasks())
        self.assertEqual(summary['unknown_count'], 0)
        self.assertEqual(summary['terminal_count'], before)
        self.assertEqual(harness.model.calls, 0)

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
