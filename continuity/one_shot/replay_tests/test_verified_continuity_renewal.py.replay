import unittest

from research.research_os.idea_feed.primitives import bind_identity
from research.research_os.renewal_policy import RenewalContractError, evaluate_successor, validate_contract


CLOSED = {
    "economic_experiment_authorized": False,
    "prospective_observation_authorized": False,
    "real_capital_authorized": False,
    "live_trading_authorized": False,
}
ROOT_BOUND = {"authorized_source": "runtime/RESEARCH_FRONTIER.json:max_issued_per_frontier", "max_issued_per_frontier": 12}
VARIANT_BOUND = {"authorized_source": "NO_SEPARATE_VARIANT_BUDGET", "state": "NO_NEW_VARIANT_BUDGET_AUTHORIZED"}
PROGRAM_BOUND = {"max_new_tasks_per_refill": 1, "max_issued_per_frontier": 12}
VALIDATION_CAPACITY = {"source": "EXISTING_CONTROL_PLANE_CAPABILITY", "new_capacity_authorized": False}


class VerifiedRenewalTests(unittest.TestCase):
    def contract(self, *, cohort="C1", predecessor="C0", sources=None, epoch="E1", exposure=None,
                 question=None, outcome_exposed=False):
        return {
            "PROGRAM_ID": "verified-continuity-fixture-program",
            "COHORT_ID": cohort,
            "PREDECESSOR_COHORT_ID": predecessor,
            "PREDECESSOR_CLOSURE_RECEIPT": "fixture://predecessor-closure",
            "CLOSURE_REASON": "BOUNDED_COHORT_CLOSED",
            "SUCCESSOR_ELIGIBILITY_REASON": "FIXED_POLICY_HAS_REMAINING_AUTHORIZED_FRONTIER_CAPACITY",
            "POLICY_MODE": "FIXED_PREREGISTERED",
            "INFORMATION_CUTOFF": "2026-10-20T00:00:00Z",
            "QUALIFIED_SOURCE_VERSIONS": ["fixture-qualified-source-v1"] if sources is None else sources,
            "QUESTION_DISTRIBUTION": question or {"INSTITUTIONAL_FLOW_DISTINCT_MECHANISM": 1},
            "SOURCE_FAMILY_DISTRIBUTION": {"PUBLIC_DOCUMENTARY": 1},
            "ROOT_BUDGET": ROOT_BOUND,
            "VARIANT_BUDGET": VARIANT_BOUND,
            "CUMULATIVE_PROGRAM_BUDGET": PROGRAM_BOUND,
            "CUMULATIVE_EXPOSURE": ["exposure:already-charged-1"] if exposure is None else exposure,
            "VALIDATION_CAPACITY": VALIDATION_CAPACITY,
            "STOP_RULES": ["STOP_ON_AUTHORITY_BLOCK", "STOP_ON_NO_ADMISSIBLE_SOURCE", "STOP_ON_AUTHORIZED_BOUND_EXHAUSTION"],
            "REOPEN_RULES": ["REOPEN_ONLY_ON_OBSERVABLE_SOURCE_OR_AUTHORITY_PREDICATE"],
            "PROTECTED_OUTCOME_BOUNDARY": "SEALED",
            "AUTHORITY_SCOPE": CLOSED,
            "EFFECTIVE_CLOCK": "2026-10-21T00:00:00Z",
            "SCIENTIFIC_EPOCH_ID": epoch,
            "IDEMPOTENCY_KEY": f"verified-program-{cohort}",
            "OUTCOME_EXPOSURE_CHARGED": outcome_exposed,
            "COUNTS_AS_INDEPENDENT_CONFIRMATION": False,
            "OPERATIONALLY_ENABLED": False,
        }

    def predecessor(self, **kwargs):
        row = self.contract(cohort="C0", predecessor="PROGRAM_START", **kwargs)
        row["PREDECESSOR_CLOSURE_RECEIPT"] = "fixture://program-start"
        return validate_contract(row)

    def test_same_root_survives_new_cohort_and_successor_is_not_activated(self):
        identity = {
            "mechanism": "forced dealer balance-sheet constraint", "actor": "primary dealers",
            "universe": "UST", "clock": "auction clock", "horizon": "auction to settlement",
            "payer": "UNKNOWN", "economic_exposure": "UNKNOWN", "instrument": "UST",
        }
        before = bind_identity(identity, parameters={"window": "fixed"})
        after = bind_identity(identity, parameters={"window": "fixed"})
        self.assertEqual(before["root_hypothesis_id"], after["root_hypothesis_id"])
        self.assertEqual(before["variant_id"], after["variant_id"])

        prior = self.predecessor()
        successor = self.contract(cohort="C1", predecessor="C0")
        result = evaluate_successor(successor, predecessor=prior, expected_policy_hash=prior["POLICY_HASH"])
        self.assertEqual(result["status"], "BOUNDED_SUCCESSOR_ELIGIBLE_NOT_ACTIVATED")
        self.assertFalse(result["operationally_enabled"])
        self.assertFalse(result["scheduler_mutation"])
        self.assertFalse(result["authority_expanded"])
        self.assertEqual(result, evaluate_successor(successor, predecessor=prior, expected_policy_hash=prior["POLICY_HASH"]))

    def test_budget_or_capacity_change_requires_owner_policy_decision(self):
        prior = self.predecessor()
        successor = self.contract(cohort="C1", predecessor="C0")
        successor["ROOT_BUDGET"] = {**ROOT_BOUND, "max_issued_per_frontier": 13}
        with self.assertRaisesRegex(RenewalContractError, "OWNER_POLICY_DECISION_REQUIRED:ROOT_BUDGET"):
            validate_contract(successor, predecessor=prior)

    def test_exposure_cannot_reset_and_cohort_never_counts_as_independent_confirmation(self):
        prior = self.predecessor()
        successor = self.contract(cohort="C1", predecessor="C0", exposure=["different-exposure"])
        with self.assertRaisesRegex(RenewalContractError, "EXPOSURE_RESET"):
            validate_contract(successor, predecessor=prior)
        successor = self.contract(cohort="C1", predecessor="C0")
        successor["COUNTS_AS_INDEPENDENT_CONFIRMATION"] = True
        with self.assertRaisesRegex(RenewalContractError, "NOT_INDEPENDENT_CONFIRMATION"):
            validate_contract(successor, predecessor=prior)

    def test_unavailable_source_parks_without_scheduler_mutation(self):
        prior = self.predecessor()
        successor = self.contract(cohort="C1", predecessor="C0", sources=[])
        result = evaluate_successor(successor, predecessor=prior, expected_policy_hash=prior["POLICY_HASH"])
        self.assertEqual(result["status"], "PARK")
        self.assertEqual(result["reason"], "NO_ADMISSIBLE_QUALIFIED_SOURCE_VERSION")
        self.assertFalse(result["scheduler_mutation"])
        self.assertFalse(result["operationally_enabled"])

    def test_stale_policy_hash_fails_closed(self):
        prior = self.predecessor()
        successor = self.contract(cohort="C1", predecessor="C0")
        with self.assertRaisesRegex(RenewalContractError, "STALE_RENEWAL_POLICY_HASH"):
            validate_contract(successor, predecessor=prior, expected_policy_hash="0" * 64)

    def test_post_outcome_policy_change_requires_charged_new_epoch(self):
        prior = self.predecessor(outcome_exposed=True)
        changed_question = {"INSTITUTIONAL_FLOW_DISTINCT_MECHANISM": 1, "EVENT_DOCUMENT_DISTINCT_MECHANISM": 1}
        successor = self.contract(cohort="C1", predecessor="C0", question=changed_question, epoch="E1")
        with self.assertRaisesRegex(RenewalContractError, "NEW_SCIENTIFIC_EPOCH"):
            validate_contract(successor, predecessor=prior)
        successor["SCIENTIFIC_EPOCH_ID"] = "E2"
        successor["EPOCH_TRIGGERING_INFORMATION_SET"] = "fixture://policy-change-after-exposure"
        normalized = validate_contract(successor, predecessor=prior)
        self.assertEqual(normalized["SCIENTIFIC_EPOCH_ID"], "E2")
        self.assertFalse(normalized["COUNTS_AS_INDEPENDENT_CONFIRMATION"])


if __name__ == "__main__":
    unittest.main()
