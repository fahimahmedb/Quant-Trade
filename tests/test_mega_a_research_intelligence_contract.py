"""Canonical unittest bridge for Mega-A Research Intelligence adversarial contracts.

The SEC gate discovers only root tests/.  Mega-A's deep module tests live under
research/research_os/tests; this bridge deliberately reuses those exact cases so
one source of scientific semantics is enforced by the canonical CI without adding
another scheduler, workflow, or duplicate truth implementation.
"""
from __future__ import annotations

import unittest

from research.research_os.tests.test_legacy_memory_compatibility import (
    LegacyMemoryCompatibilityTests,
)
from research.research_os.tests.test_research_action_planner import (
    ResearchActionPlannerTests,
)
from research.research_os.tests.test_research_refill_policy import (
    ResearchRefillPolicyTests,
)
from research.research_os.tests.test_scientific_memory_feedback import (
    ScientificMemoryFeedbackTests,
)
from research.research_os.tests import test_research_intelligence as intelligence_cases


ADVERSARIAL_CASES = (
    intelligence_cases.test_negative_family_resurfaces_under_rename_is_suppressed,
    intelligence_cases.test_blocked_never_becomes_negative_and_can_reopen,
    intelligence_cases.test_unexecuted_is_not_failed,
    intelligence_cases.test_invalid_protocol_cannot_rerun_unchanged,
    intelligence_cases.test_invalid_protocol_changed_can_continue,
    intelligence_cases.test_unknown_identity_is_not_novelty,
    intelligence_cases.test_same_evidence_under_new_path_reused_not_new,
    intelligence_cases.test_cheap_falsifier_before_expensive_deep_action,
    intelligence_cases.test_declared_capability_without_route_is_not_available,
    intelligence_cases.test_authority_sealed_action_is_not_selected_executable,
    intelligence_cases.test_queue_empty_is_not_false_exhaustion,
    intelligence_cases.test_only_duplicates_is_distinct_from_exhausted,
    intelligence_cases.test_two_distinct_mechanisms_with_same_label_are_not_merged,
    intelligence_cases.test_positive_but_insufficient_does_not_promote_to_producer,
    intelligence_cases.test_model_commentary_unqualified_memory_cannot_be_evidence,
    intelligence_cases.test_wrong_semantic_identity_memory_does_not_influence_search_even_if_id_matches,
    intelligence_cases.test_stale_capability_does_not_drive_priority,
    intelligence_cases.test_search_engine_never_creates_second_scheduler,
    intelligence_cases.test_deep_action_without_justification_fails_closed,
    intelligence_cases.test_budget_unknown_does_not_fabricate_budget_availability,
    intelligence_cases.test_external_access_blocked_is_distinct_frontier_state,
    intelligence_cases.test_true_exhaustion_requires_explicit_complete_search_and_archaeology,
    intelligence_cases.test_choose_next_action_is_pure_and_cost_ordered,
    intelligence_cases.test_capability_route_requires_both_surfaces,
)


class ResearchIntelligenceAdversarialBridgeTests(unittest.TestCase):
    def test_full_adversarial_matrix(self):
        for case in ADVERSARIAL_CASES:
            with self.subTest(case=case.__name__):
                case()


if __name__ == "__main__":
    unittest.main()
