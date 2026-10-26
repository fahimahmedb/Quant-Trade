from __future__ import annotations

import unittest

from research.research_os.research_action_planner import plan_research_action


def context(*, legacy_enabled=True, identity_enabled=True, validator_enabled=True):
    return {
        "capability_registry": {"capabilities": [
            {"capability_id": "legacy_recovery", "production_enabled": legacy_enabled},
            {"capability_id": "economic_identity", "production_enabled": identity_enabled},
            {"capability_id": "validator", "production_enabled": validator_enabled},
        ]},
        "workflow_lanes": {"lanes": [
            {"lane_id": "evidence_data", "capabilities": ["legacy_recovery"]},
            {"lane_id": "integrator_portfolio", "capabilities": ["economic_identity"]},
            {"lane_id": "independent_challenge", "capabilities": ["validator"]},
        ]},
        "control_plane": {
            "task_selection": {"follow_up_task_creation_authorized_only_when_current_task_explicitly_allows": True},
            "queue_replenishment": {"free_form_task_invention_forbidden": True},
        },
    }


def feedback(action, missing=None):
    return {
        "action": action,
        "identity": {"missing_core_dimensions": list(missing or [])},
    }


class ResearchActionPlannerTests(unittest.TestCase):
    def test_unknown_identity_prefers_cheap_archaeology_before_deep_identity(self):
        result = plan_research_action(feedback("ARCHAEOLOGY_LOOKUP", ["payer", "timing_clock"]), context())
        self.assertEqual(result["next_action"], "ARCHAEOLOGY_LOOKUP")
        self.assertEqual(result["required_capability"], "legacy_recovery")
        self.assertEqual(result["target_lane"], "evidence_data")
        self.assertEqual(result["cheapest_candidate_action"]["relative_depth"], "WIDE_CHEAP_FIRST")
        self.assertEqual(result["deep_escalation_if_still_unresolved"]["required_capability"], "economic_identity")
        self.assertEqual(result["budget_units"], "UNKNOWN")
        self.assertFalse(result["task_created"])
        self.assertFalse(result["scheduler_mutation"])
        self.assertIn("FOLLOW_UP_TASK_AUTHORITY_NOT_PROVEN_BY_SCREEN", result["blockers"])

    def test_declared_but_inactive_archaeology_capability_is_blocker(self):
        result = plan_research_action(feedback("ARCHAEOLOGY_LOOKUP", ["payer"]), context(legacy_enabled=False))
        self.assertFalse(result["capability_route"]["available"])
        self.assertTrue(any(item.startswith("ARCHAEOLOGY_CAPABILITY_OR_ROUTE_UNAVAILABLE") for item in result["blockers"]))

    def test_known_negative_no_build_needs_no_new_task(self):
        result = plan_research_action(feedback("NO_BUILD"), context())
        self.assertEqual(result["next_action"], "NO_BUILD")
        self.assertFalse(result["requires_new_task"])
        self.assertTrue(result["decision_enactable_in_current_screen"])
        self.assertEqual(result["blockers"], [])

    def test_blocked_memory_parks_without_becoming_failure(self):
        result = plan_research_action(feedback("PARK"), context())
        self.assertEqual(result["next_action"], "PARK")
        self.assertIn("HISTORICAL_BLOCKER_UNRESOLVED", result["blockers"])
        self.assertEqual(result["economic_result"], "NOT_OBSERVED")

    def test_invalid_protocol_cannot_rerun_unchanged(self):
        result = plan_research_action(feedback("REPAIR_PROTOCOL"), context())
        self.assertEqual(result["next_action"], "REPAIR_PROTOCOL")
        self.assertFalse(result["decision_enactable_in_current_screen"])
        self.assertIn("PRODUCER_FAMILY_AND_FOLLOW_UP_AUTHORITY_MUST_BE_REACQUIRED", result["blockers"])

    def test_positive_insufficient_validation_is_not_immediately_executable(self):
        result = plan_research_action(feedback("ESCALATE_VALIDATION"), context())
        self.assertEqual(result["required_capability"], "validator")
        self.assertTrue(result["capability_route"]["available"])
        self.assertIn("FROZEN_HYPOTHESIS_REQUIRED_BEFORE_VALIDATION_HANDOFF", result["blockers"])
        self.assertFalse(result["decision_enactable_in_current_screen"])

    def test_no_action_allows_existing_lineage_only(self):
        result = plan_research_action(feedback("NO_ACTION"), context())
        self.assertEqual(result["next_action"], "NO_ACTION")
        self.assertEqual(result["cheapest_candidate_action"], "CONTINUE_EXISTING_LINEAGE")
        self.assertFalse(result["task_created"])


if __name__ == "__main__":
    unittest.main()
