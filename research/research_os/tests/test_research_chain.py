from __future__ import annotations

import unittest

from research.research_os.research_chain import UNKNOWN, plan_research_chain


def _candidate(
    candidate_id: str,
    mechanism: str,
    *,
    priority=None,
    information_value=None,
    cost=1,
    **extra,
):
    candidate = {
        "candidate_id": candidate_id,
        "identity": {
            "mechanism": mechanism,
            "payer": "payer",
            "constrained_actor": "actor",
            "timing_clock": "clock",
            "universe": "universe",
            "economic_exposure": "exposure",
        },
        "actions": [
            {
                "action": "GENERATE_MECHANISM",
                "cost_units": cost,
                "depth": "WIDE",
                "is_falsifier": True,
                "information_value": information_value,
            }
        ],
    }
    if priority is not None:
        candidate["hypothesis_priority"] = priority
    if information_value is not None:
        candidate["information_value"] = information_value
    candidate.update(extra)
    return candidate


def _plan(candidates, **overrides):
    kwargs = {
        "memory_records": [],
        "archaeology": {},
        "current_frontier": {},
        "evidence_gaps": [],
        "capability_registry": {"capabilities": []},
        "workflow_lanes": {"lanes": []},
        "authority": {},
        "budget_context": {"remaining_units": 100},
        "queue_active_count": 0,
        "search_space_complete": False,
        "archaeology_complete": False,
    }
    kwargs.update(overrides)
    return plan_research_chain(candidates, **kwargs)


class ResearchChainTests(unittest.TestCase):
    def test_higher_explicit_hypothesis_priority_beats_cheaper_candidate(self):
        result = _plan(
            [
                _candidate("high", "m-high", priority=10, information_value=1, cost=9),
                _candidate("cheap", "m-cheap", priority=5, information_value=100, cost=1),
            ]
        )
        self.assertEqual(result["next_action"]["candidate_id"], "high")
        self.assertIn("HYPOTHESIS_PRIORITY_THEN_INFORMATION_VALUE_THEN_COST", result["next_action"]["reason_codes"])
        self.assertEqual(result["selection_state"], "RANKED_SELECTION")

    def test_information_value_breaks_equal_priority_before_cost(self):
        result = _plan(
            [
                _candidate("informative", "m-info", priority=10, information_value=9, cost=8),
                _candidate("cheap", "m-cheap-2", priority=10, information_value=2, cost=1),
            ]
        )
        self.assertEqual(result["next_action"]["candidate_id"], "informative")

    def test_cost_breaks_equal_priority_and_information_value(self):
        result = _plan(
            [
                _candidate("expensive", "m-exp", priority=10, information_value=9, cost=8),
                _candidate("cheap", "m-cheap-3", priority=10, information_value=9, cost=1),
            ]
        )
        self.assertEqual(result["next_action"]["candidate_id"], "cheap")

    def test_unknown_ranking_metadata_is_not_fabricated_for_single_executable(self):
        result = _plan([_candidate("unknown", "m-unknown", cost=0)])
        ranking = result["decisions"][0]["research_ranking"]
        self.assertEqual(ranking["hypothesis_priority"], UNKNOWN)
        self.assertEqual(ranking["information_value"], UNKNOWN)
        self.assertFalse(result["ranking_complete"])
        self.assertEqual(result["next_action"]["candidate_id"], "unknown")
        self.assertEqual(result["selection_state"], "SINGLE_EXECUTABLE_NO_COMPARISON")
        self.assertIn("RANKING_METADATA_INCOMPLETE_UNKNOWN_NOT_INFERRED", result["next_action"]["reason_codes"])
        self.assertIn("SINGLE_EXECUTABLE_ACTION_NO_CROSS_CANDIDATE_RANKING_REQUIRED", result["next_action"]["reason_codes"])

    def test_multiple_executable_candidates_with_unknown_ranking_fail_closed(self):
        result = _plan(
            [
                _candidate("known", "m-known", priority=5, information_value=5, cost=1),
                _candidate("unknown", "m-unknown-2", priority=None, information_value=None, cost=0),
            ]
        )
        self.assertEqual(result["next_action"]["action"], "NO_ACTION")
        self.assertIsNone(result["next_action"]["candidate_id"])
        self.assertFalse(result["next_action"]["executable"])
        self.assertEqual(result["selection_state"], "RANKING_BLOCKED")
        self.assertFalse(result["ranking_complete"])
        self.assertIn("MULTI_CANDIDATE_RANKING_INCOMPLETE_FAIL_CLOSED", result["next_action"]["reason_codes"])
        self.assertIn("UNKNOWN_RANKING_METADATA_NOT_INFERRED", result["next_action"]["reason_codes"])
        self.assertEqual(result["frontier"]["state"], "ACTIVE_ACTIONABLE")
        self.assertFalse(result["scheduler_mutation"])

    def test_blocked_high_priority_candidate_never_wins(self):
        result = _plan(
            [
                _candidate(
                    "blocked",
                    "m-blocked",
                    priority=100,
                    information_value=100,
                    cost=0,
                    external_access_required=True,
                    external_access_available=False,
                ),
                _candidate("open", "m-open", priority=1, information_value=1, cost=0),
            ]
        )
        self.assertEqual(result["next_action"]["candidate_id"], "open")
        blocked = next(item for item in result["decisions"] if item["candidate_id"] == "blocked")
        self.assertEqual(blocked["action"], "PARK")

    def test_outcome_fields_are_reported_but_cannot_drive_ranking(self):
        result = _plan(
            [
                _candidate("z", "m-z", priority=1, information_value=1, cost=0, alpha=999, sharpe=999),
                _candidate("a", "m-a", priority=1, information_value=1, cost=0, alpha=-999, sharpe=-999),
            ]
        )
        self.assertEqual(result["next_action"]["candidate_id"], "a")
        z = next(item for item in result["decisions"] if item["candidate_id"] == "z")
        self.assertEqual(z["research_ranking"]["outcome_fields_present_but_ignored"], ["alpha", "sharpe"])
        self.assertFalse(result["outcome_accessed"])

    def test_missing_chain_context_fails_closed_without_scheduler_mutation(self):
        result = _plan([_candidate("x", "m-x", priority=1, information_value=1, cost=0)], archaeology=None)
        self.assertEqual(result["next_action"]["action"], "NO_ACTION")
        self.assertIn("CHAIN_CONTEXT_INCOMPLETE", result["next_action"]["reason_codes"])
        self.assertFalse(result["scheduler_mutation"])

    def test_queue_empty_is_not_scientific_exhaustion(self):
        result = _plan([], queue_active_count=0, search_space_complete=False, archaeology_complete=False)
        self.assertEqual(result["frontier"]["state"], "SEARCH_SPACE_INCOMPLETE")
        self.assertFalse(result["frontier"]["scientifically_exhausted"])

    def test_true_exhaustion_requires_both_explicit_completion_facts(self):
        result = _plan([], queue_active_count=0, search_space_complete=True, archaeology_complete=True)
        self.assertEqual(result["frontier"]["state"], "SCIENTIFICALLY_EXHAUSTED")
        self.assertTrue(result["frontier"]["scientifically_exhausted"])

    def test_receipt_preserves_all_fixed_chain_inputs_and_no_mutation(self):
        result = _plan([_candidate("x", "m-contract", priority=1, information_value=1, cost=0)])
        self.assertEqual(result["fixed_chain"][0:5], [
            "SCIENTIFIC_MEMORY",
            "ARCHAEOLOGY",
            "CURRENT_FRONTIER",
            "EVIDENCE_GAPS",
            "AVAILABLE_CAPABILITIES",
        ])
        self.assertEqual(result["fixed_chain"][-2:], ["FRONTIER_EXHAUSTION_NOOP", "FEEDBACK"])
        self.assertFalse(result["scheduler_mutation"])
        self.assertFalse(result["feedback"]["persistent_memory_mutation"])


if __name__ == "__main__":
    unittest.main()
