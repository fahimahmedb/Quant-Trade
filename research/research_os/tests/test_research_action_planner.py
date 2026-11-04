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


    def test_documentary_rescue_reaches_bounded_planner_handoff(self):
        selected = {"action": "ACQUIRE_EVIDENCE_INTENT", "required_capability": "source_qualification",
                    "target_lane": "evidence_data", "cost_units": 0,
                    "decision_changing_evidence": "verify actual transfer-agent eligibility",
                    "rescue_for": "EXTERNAL_ACCESS_REQUIRED"}
        f = feedback("ACQUIRE_EVIDENCE_INTENT")
        f["selected_action"] = selected
        f["blockers"] = ["EXTERNAL_ACCESS_BLOCKED"]
        r = plan_research_action(f, context())
        self.assertEqual(r["next_action"], "ACQUIRE_EVIDENCE_INTENT")
        self.assertFalse(r["task_created"])
        self.assertFalse(r["scheduler_mutation"])
        self.assertFalse(r["decision_enactable_in_current_screen"])
        self.assertIn("FOLLOW_UP_TASK_AUTHORITY_NOT_PROVEN_BY_SCREEN", r["blockers"])
        self.assertEqual(r["original_implementation_blockers"], ["EXTERNAL_ACCESS_BLOCKED"])
        self.assertFalse(r["mechanism_falsified"])

    def test_unbound_documentary_action_does_not_obtain_authority(self):
        r = plan_research_action(feedback("ACQUIRE_EVIDENCE_INTENT"), context())
        self.assertEqual(r["next_action"], "PARK")
        self.assertFalse(r["task_created"])
        self.assertIn("UNBOUND_DOCUMENTARY_ACTION", r["blockers"])

    def test_reuse_existing_evidence_never_creates_task(self):
        f = feedback("REUSE_EXISTING_EVIDENCE")
        f["selected_action"] = {"action": "REUSE_EXISTING_EVIDENCE", "cost_units": 0}
        r = plan_research_action(f, context())
        self.assertEqual(r["next_action"], "REUSE_EXISTING_EVIDENCE")
        self.assertFalse(r["requires_new_task"])
        self.assertFalse(r["task_created"])
        self.assertFalse(r["mechanism_falsified"])

    def test_park_receipt_preserves_implementation_vs_mechanism(self):
        r = plan_research_action(feedback("PARK"), context())
        self.assertEqual(r["next_action"], "PARK")
        self.assertEqual(r["rescue_status"], "NO_BOUNDED_AUTHORIZED_DOCUMENTARY_ROUTE_SELECTED")
        self.assertEqual(r["cheapest_candidate_action"], "QUALIFY_ONE_DECISION_CHANGING_DOCUMENTARY_REOPEN_ROUTE_WITHIN_MANDATE")
        self.assertFalse(r["mechanism_falsified"])
        self.assertTrue(r["exact_reopen_evidence"])


if __name__ == "__main__":
    unittest.main()
