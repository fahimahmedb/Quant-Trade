"""Confirmation counting binds existing assertions, not actual reviewer authenticity."""
from copy import deepcopy
import unittest

from research.research_os.scientific_store import sha256_json
from research.research_os.expansion import scientific_adjudication as c0
from tests import test_wave2_c2_scientific_adjudication as fixtures


SEMANTIC_REVIEW = "PROVEN_INDEPENDENT_SEMANTIC_REVIEW"


def rehash(ref):
    ref["ref_hash"] = sha256_json({key: value for key, value in ref.items() if key != "ref_hash"})
    return ref


class ConfirmationCountRepairTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.Wave2C2ScientificAdjudicationTests()
        self.fixture.setUp()
        self.factory = self.fixture.factory

    def bind(self, **updates):
        return c0.bind_independence_ref(self.factory, dict(fixtures.independence_record(), **updates))

    def test_structural_reconstruction_keeps_pass_but_no_semantic_confirmation(self):
        record = fixtures.independence_record()
        before = deepcopy(record)
        ref = c0.bind_independence_ref(self.factory, record)
        self.assertEqual(record, before)
        self.assertTrue(ref["structural_independence_proven"])
        self.assertEqual(ref["status"], "PASS")
        self.assertEqual(ref["semantic_diverse_review"], record["semantic_diverse_review"])
        self.assertEqual(ref["independent_confirmation_count"], 0)
        self.assertEqual(ref["record_hash"], sha256_json(record))
        self.assertEqual(ref, c0.bind_independence_ref(self.factory, record))
        c0.validate_independence_ref(ref, self.factory)

    def test_missing_unknown_null_and_false_like_semantic_states_never_count(self):
        for state in (None, "UNKNOWN", "NOT_PROVEN", "", True, False, 0, 1, [], {},
                      "PROVEN", SEMANTIC_REVIEW.lower(), " " + SEMANTIC_REVIEW):
            with self.subTest(state=state):
                ref = self.bind(semantic_diverse_review=state)
                self.assertEqual(ref["semantic_diverse_review"], state)
                self.assertEqual(ref["status"], "PASS")
                self.assertEqual(ref["independent_confirmation_count"], 0)
        record = fixtures.independence_record()
        del record["semantic_diverse_review"]
        ref = c0.bind_independence_ref(self.factory, record)
        self.assertEqual(ref["semantic_diverse_review"], "NOT_PROVEN")
        self.assertEqual(ref["independent_confirmation_count"], 0)

    def test_exact_existing_review_assertion_can_count_once_with_bound_identity(self):
        # A synthetic explicit proof STATE exercises the existing trust boundary.
        # This test does not assert a real reviewer or empirical independence.
        record = dict(fixtures.independence_record(), semantic_diverse_review=SEMANTIC_REVIEW)
        ref = c0.bind_independence_ref(self.factory, record)
        self.assertEqual(ref["independent_confirmation_count"], 1)
        self.assertEqual(ref["record_hash"], sha256_json(record))
        for key in ("hypothesis_id", "generation_id", "candidate_hash", "protocol_hash", "frozen_protocol_hash"):
            self.assertEqual(ref[key], self.factory[key])
        self.assertEqual(ref["factory_ref_hash"], self.factory["ref_hash"])
        self.assertTrue(all(ref[axis] is False for axis in c0.AUTHORITY_STATE))
        c0.validate_independence_ref(ref, self.factory)

    def test_semantic_assertion_cannot_override_duplicate_wrapper_or_unknown_support(self):
        for relation in ("DUPLICATE", "WRAPPER_EQUIVALENT", "UNKNOWN"):
            with self.subTest(relation=relation):
                ref = self.bind(semantic_diverse_review=SEMANTIC_REVIEW, support_relation=relation)
                self.assertEqual(ref["support_relation"], relation)
                self.assertEqual(ref["status"], "PASS")
                self.assertEqual(ref["independent_confirmation_count"], 0)

    def test_semantic_assertion_never_upgrades_failed_structural_axes_or_outcome_isolation(self):
        for axis in c0.INDEPENDENCE_AXES:
            for value in (False, None, 1, "true"):
                with self.subTest(axis=axis, value=value):
                    ref = self.bind(**{axis: value, "semantic_diverse_review": SEMANTIC_REVIEW})
                    self.assertEqual(ref["status"], "BLOCK")
                    self.assertFalse(ref["structural_independence_proven"])
                    self.assertEqual(ref["independent_confirmation_count"], 0)
        record = dict(fixtures.independence_record(), semantic_diverse_review=SEMANTIC_REVIEW)
        del record["outcome_accessed"]
        ref = c0.bind_independence_ref(self.factory, record)
        self.assertEqual(ref["status"], "BLOCK")
        self.assertEqual(ref["independent_confirmation_count"], 0)

    def test_rehashed_count_forgery_and_false_like_counts_fail_current_validation(self):
        for count in (1, True, False, 0.0, -1, 2, "0", None):
            ref = rehash(dict(self.bind(), independent_confirmation_count=count))
            with self.subTest(count=count), self.assertRaises(c0.ScientificAdjudicationError):
                c0.validate_independence_ref(ref, self.factory)

    def test_rehashed_positive_ref_requires_each_current_basis(self):
        ref = self.bind(semantic_diverse_review=SEMANTIC_REVIEW)
        variants = [{"status": "BLOCK"}, {"structural_independence_proven": False},
                    {"semantic_diverse_review": "UNKNOWN"}, {"support_relation": "UNKNOWN"},
                    {"outcome_accessed": None}]
        variants += [{"axes": dict(ref["axes"], **{axis: 1})} for axis in c0.INDEPENDENCE_AXES]
        for changes in variants:
            forged = rehash(dict(ref, **changes))
            with self.subTest(changes=changes), self.assertRaises(c0.ScientificAdjudicationError):
                c0.validate_independence_ref(forged, self.factory)
        missing_outcome = deepcopy(ref)
        del missing_outcome["outcome_accessed"]
        with self.assertRaises(c0.ScientificAdjudicationError):
            c0.validate_independence_ref(rehash(missing_outcome), self.factory)
        # A redundant caller-supplied boolean must not override the native state.
        forged = rehash(dict(self.bind(), semantic_independent_confirmation_proven=True,
                             independent_confirmation_count=1))
        with self.assertRaises(c0.ScientificAdjudicationError):
            c0.validate_independence_ref(forged, self.factory)

    def test_rehashed_frozen_identity_drift_is_rejected(self):
        ref = self.bind(semantic_diverse_review=SEMANTIC_REVIEW)
        for key in ("factory_ref_hash", "hypothesis_id", "generation_id", "candidate_hash",
                    "protocol_hash", "frozen_protocol_hash"):
            forged = rehash(dict(ref, **{key: "f" * 64}))
            with self.subTest(key=key), self.assertRaises(c0.ScientificAdjudicationError):
                c0.validate_independence_ref(forged, self.factory)

    def test_historical_overcount_ref_is_immutable_but_not_admissible_to_current_composition(self):
        old = c0._original_bind_independence_ref(self.factory, fixtures.independence_record())
        before = deepcopy(old)
        self.assertEqual(old["independent_confirmation_count"], 1)
        for validate in (c0.validate_independence_ref, c0._impl.validate_independence_ref):
            with self.assertRaises(c0.ScientificAdjudicationError):
                validate(old, self.factory)
        for compose in (c0.adjudicate_scientific_candidate, c0._impl.adjudicate_scientific_candidate):
            with self.assertRaises(c0.ScientificAdjudicationError):
                compose(self.factory, independence_ref=old)
        self.assertEqual(old, before)
        self.assertEqual(c0._impl.bind_independence_ref(self.factory, fixtures.independence_record()), self.bind())

    def test_composed_count_preserves_claim_ceiling_unknowns_authority_and_outcome_membrane(self):
        for state, count in (("UNKNOWN", 0), (SEMANTIC_REVIEW, 1)):
            ref = self.bind(semantic_diverse_review=state)
            result = self.fixture.adjudicate(independence_ref=ref)
            self.assertEqual(result["independent_confirmation_count"], count)
            self.assertEqual(result["scientific_posture"], "QUALIFIED_WITH_CLAIM_CEILING")
            self.assertEqual(result["claim_ceiling"], "MECHANISM_AND_PRE_ECONOMIC_READINESS_ONLY")
            self.assertEqual(result["profitability_status"], "UNKNOWN")
            self.assertTrue(result["uncertainty_state"]["unknown_preserved"])
            self.assertFalse(result["economic_identity_created"])
            self.assertEqual(result["raw_outcomes_consumed"], 0)
            self.assertTrue(all(result[key] is False for key in c0.AUTHORITY_STATE))
            c0.validate_adjudication(result)

    def test_standalone_adjudication_rejects_invalid_or_coerced_confirmation_counts(self):
        result = self.fixture.adjudicate(independence_ref=self.bind())
        for count in (True, False, 0.0, 1.0, -1, 2, 37, "0", None):
            forged = deepcopy(result)
            forged["independent_confirmation_count"] = count
            forged["adjudication_hash"] = sha256_json(
                {key: value for key, value in forged.items() if key != "adjudication_hash"}
            )
            with self.subTest(count=count), self.assertRaises(c0.ScientificAdjudicationError):
                c0.validate_adjudication(forged)


if __name__ == "__main__":
    unittest.main()
