"""The closed protocol semantics, and the tests that would catch getting them wrong.

Everything here is synthetic. The point of most of these tests is not that the
code computes something, but that it computes the *closed* thing: window expiry
before session additions, distinct insider CIKs rather than filings, no repeated
formation while a window is active, entry never on the EDGAR date itself, and no
payoff substituted for an unobservable session.
"""

from __future__ import annotations

import unittest
from dataclasses import replace
from datetime import date, timedelta

from quant.dataplane.form4_parse import parse_form4_document
from quant.science import (AMBIGUOUS_EMBARGO, CLAIM_DESIGN_SENSITIVE, DESIGN_INVARIANT,
                           FormationEngine, GeometryChoice, MultiplicityBudget,
                           O3Convention, QualifyingObservation, RegimePartition,
                           SessionCalendar, admissible_geometries,
                           cluster_bootstrap_ratio, cluster_sign_flip_null,
                           design_invariance, empirical_p_value, placebo_null,
                           placebo_offsets, qualifying_events, qualifying_owner,
                           qualifying_transaction, ratio_estimate, regime_breakdown,
                           statistical_economic_verdict)
from quant.science.formation import (D19_TERMINAL_TREATMENT_REQUIRED,
                                     EXPOSURE_INTERVAL_INCOMPLETE, FORMATION_UNRESOLVED,
                                     O1_NEXT, O1_PREVIOUS, OBSERVATION_COUNT_UNRESOLVED)
from quant.science.inference import (ECONOMICALLY_DOMINATED, ESTIMATE_NO_EXPOSURE,
                                     ESTIMATE_SINGLE_CLUSTER,
                                     STATISTICALLY_DISTINGUISHABLE)
from quant.science.regimes import BEST_REGIME_IS_NOT_THE_RESULT, POST_HOC_REFUSED


def joined(problems) -> str:
    return " | ".join(problems)


def weekday_sessions(count: int, start: str = "2026-01-05") -> list[str]:
    """A synthetic regular-session calendar: weekdays only."""
    current = date.fromisoformat(start)
    sessions: list[str] = []
    while len(sessions) < count:
        if current.weekday() < 5:
            sessions.append(current.isoformat())
        current += timedelta(days=1)
    return sessions


SESSIONS = weekday_sessions(60)
CALENDAR = SessionCalendar(SESSIONS)

FULL_GEOMETRY = GeometryChoice(o1=O1_NEXT, o2_ordering="SOURCE_IDENTITY_ASCENDING",
                               o3=O3Convention("END_OF_TWENTIETH_SESSION", 20),
                               o4_overlap="DISTINCT_SIGNALS_REMAIN_DISTINCT")


def observation(owner: str, session_index: int, identity: str = "") -> QualifyingObservation:
    return QualifyingObservation(issuer_cik="0009999991", owner_cik=owner,
                                 edgar_date=SESSIONS[session_index],
                                 source_identity=identity or f"ACC-{owner}-{session_index}")


class EligibilityTest(unittest.TestCase):
    """D07 section 2.1 is closed. These tests pin the notation trap."""

    def document(self, code: str = "P", indicator: str = "A", director: str = "1",
                 officer: str = "0", ten_percent: str = "0") -> bytes:
        return f"""<?xml version="1.0"?>
<ownershipDocument>
  <documentType>4</documentType>
  <periodOfReport>2026-01-05</periodOfReport>
  <issuer><issuerCik>0009999991</issuerCik></issuer>
  <reportingOwner>
    <reportingOwnerId><rptOwnerCik>0009999992</rptOwnerCik></reportingOwnerId>
    <reportingOwnerRelationship>
      <isDirector>{director}</isDirector>
      <isOfficer>{officer}</isOfficer>
      <isTenPercentOwner>{ten_percent}</isTenPercentOwner>
      <isOther>0</isOther>
    </reportingOwnerRelationship>
  </reportingOwner>
  <nonDerivativeTable>
    <nonDerivativeTransaction>
      <transactionDate><value>2026-01-05</value></transactionDate>
      <transactionCoding><transactionCode>{code}</transactionCode></transactionCoding>
      <transactionAmounts>
        <transactionShares><value>1000</value></transactionShares>
        <transactionPricePerShare><value>10.0</value></transactionPricePerShare>
        <transactionAcquiredDisposedCode><value>{indicator}</value></transactionAcquiredDisposedCode>
      </transactionAmounts>
    </nonDerivativeTransaction>
  </nonDerivativeTable>
</ownershipDocument>
""".encode()

    def test_code_p_with_acquired_indicator_qualifies(self):
        events, reasons = qualifying_events(parse_form4_document(self.document()))
        self.assertEqual(reasons, [])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].issuer_cik, "0009999991")

    def test_transaction_code_a_is_not_the_acquired_indicator_a(self):
        """The trap: code A is an award, indicator A means acquired."""
        events, reasons = qualifying_events(
            parse_form4_document(self.document(code="A", indicator="A")))
        self.assertEqual(events, ())
        self.assertIn("NO_QUALIFYING_TRANSACTION", joined(reasons))

    def test_disposal_does_not_qualify(self):
        events, reasons = qualifying_events(
            parse_form4_document(self.document(code="P", indicator="D")))
        self.assertEqual(events, ())
        self.assertIn("NO_QUALIFYING_TRANSACTION", joined(reasons))

    def test_ten_percent_ownership_alone_is_insufficient(self):
        events, reasons = qualifying_events(parse_form4_document(
            self.document(director="0", officer="0", ten_percent="1")))
        self.assertEqual(events, ())
        self.assertIn("NO_QUALIFYING_REPORTING_OWNER", joined(reasons))

    def test_ten_percent_owner_who_is_also_an_officer_qualifies(self):
        events, _ = qualifying_events(parse_form4_document(
            self.document(director="0", officer="1", ten_percent="1")))
        self.assertEqual(len(events), 1)
        self.assertTrue(events[0].ten_percent_owner)
        self.assertTrue(events[0].officer)

    def test_amendment_is_not_an_original_filing(self):
        document = self.document().replace(b"<documentType>4</documentType>",
                                          b"<documentType>4/A</documentType>")
        events, reasons = qualifying_events(parse_form4_document(document))
        self.assertEqual(events, ())
        self.assertIn("ORIGINAL_FORM_4_ONLY_AMENDMENT_EXCLUDED", joined(reasons))

    def test_predicates_are_usable_directly(self):
        facts = parse_form4_document(self.document())
        self.assertTrue(qualifying_owner(facts.owners[0]))
        self.assertTrue(qualifying_transaction(facts.transactions[0]))


class FormationSemanticsTest(unittest.TestCase):
    def engine(self, geometry: GeometryChoice = FULL_GEOMETRY) -> FormationEngine:
        return FormationEngine(CALENDAR, geometry)

    def test_two_distinct_insiders_in_the_window_form_a_signal(self):
        result = self.engine().run([observation("A", 0), observation("B", 2)])
        self.assertEqual(result["state"], "FORMATION_RESOLVED")
        self.assertEqual(result["event_count"], 1)
        event = result["events"][0]
        self.assertEqual(event["formation_session"], SESSIONS[2])
        self.assertEqual(event["distinct_owners"], ["A", "B"])

    def test_one_insider_filing_twice_does_not_form(self):
        result = self.engine().run([observation("A", 0), observation("A", 2, "ACC-2")])
        self.assertEqual(result["event_count"], 0)

    def test_window_expiry_precedes_session_additions(self):
        """The discriminating case for WINDOW_EXPIRY_PRECEDES_SESSION_ADDITIONS.

        Owner A attaches to session 0 and owner B to session 10. At session 10 the
        window is sessions 1..10, so A has already expired when B is applied and
        the count reaches one, not two. Applying additions before expiry would
        produce a formation here.
        """
        result = self.engine().run([observation("A", 0), observation("B", 10)])
        self.assertEqual(result["event_count"], 0)

    def test_the_last_session_still_inside_the_window_does_form(self):
        result = self.engine().run([observation("A", 0), observation("B", 9)])
        self.assertEqual(result["event_count"], 1)
        self.assertEqual(result["events"][0]["formation_session"], SESSIONS[9])

    def test_no_repeated_formation_while_the_window_stays_active(self):
        result = self.engine().run([observation("A", 0), observation("B", 1),
                                    observation("C", 2)])
        self.assertEqual(result["event_count"], 1)
        self.assertEqual(result["events"][0]["formation_session"], SESSIONS[1])

    def test_re_arm_only_after_the_window_falls_below_two(self):
        result = self.engine().run([observation("A", 0), observation("B", 1),
                                    observation("C", 20), observation("D", 21)])
        self.assertEqual(result["event_count"], 2)
        self.assertEqual([event["formation_session"] for event in result["events"]],
                         [SESSIONS[1], SESSIONS[21]])

    def test_intra_session_ordering_decides_the_triggering_observation(self):
        """O2 is a real degree of freedom: it changes which filing triggered."""
        observations = [observation("A", 0),
                        QualifyingObservation("0009999991", "C", SESSIONS[3], "ACC-001"),
                        QualifyingObservation("0009999991", "B", SESSIONS[3], "ACC-002")]
        by_identity = self.engine().run(observations)
        by_owner = self.engine(replace(FULL_GEOMETRY,
                                       o2_ordering="OWNER_CIK_ASCENDING")).run(observations)
        self.assertEqual(by_identity["events"][0]["triggering"]["owner_cik"], "C")
        self.assertEqual(by_owner["events"][0]["triggering"]["owner_cik"], "B")

    def test_separate_issuers_do_not_pool(self):
        first = observation("A", 0)
        second = replace(observation("B", 1), issuer_cik="0009999993")
        self.assertEqual(self.engine().run([first, second])["event_count"], 0)

    def test_undeclared_o1_leaves_formation_unresolved(self):
        geometry = replace(FULL_GEOMETRY, o1=None)
        result = self.engine(geometry).run([observation("A", 0), observation("B", 1)])
        self.assertEqual(result["state"], FORMATION_UNRESOLVED)
        self.assertIn("O1_PROJECTION_UNDECLARED", joined(result["reasons"]))

    def test_undeclared_o2_leaves_formation_unresolved(self):
        geometry = replace(FULL_GEOMETRY, o2_ordering=None)
        result = self.engine(geometry).run([observation("A", 0)])
        self.assertIn("O2_INTRA_SESSION_ORDERING_UNDECLARED", joined(result["reasons"]))

    def test_nearest_regular_session_is_refused_by_name(self):
        geometry = replace(FULL_GEOMETRY, o1="NEAREST_REGULAR_SESSION")
        result = self.engine(geometry).run([observation("A", 0)])
        self.assertEqual(result["state"], FORMATION_UNRESOLVED)
        self.assertIn("O1_ADMISSIBLE_SET_IS_EXHAUSTIVE", joined(result["reasons"]))

    def test_observation_count_is_withheld_until_o4_is_frozen(self):
        geometry = replace(FULL_GEOMETRY, o4_overlap=None)
        result = self.engine(geometry).run([observation("A", 0), observation("B", 1)])
        self.assertEqual(result["observation_count"], OBSERVATION_COUNT_UNRESOLVED)
        self.assertEqual(result["event_count"], 1)

    def test_o1_projects_a_non_session_edgar_date_both_ways(self):
        saturday = "2026-01-10"
        self.assertNotIn(saturday, CALENDAR)
        previous = FormationEngine(CALENDAR, replace(FULL_GEOMETRY, o1=O1_PREVIOUS))
        following = FormationEngine(CALENDAR, replace(FULL_GEOMETRY, o1=O1_NEXT))
        self.assertEqual(previous.formation_session(saturday), "2026-01-09")
        self.assertEqual(following.formation_session(saturday), "2026-01-12")

    def test_an_edgar_date_that_is_a_session_leaves_no_o1_choice(self):
        for convention in (O1_PREVIOUS, O1_NEXT):
            engine = FormationEngine(CALENDAR, replace(FULL_GEOMETRY, o1=convention))
            self.assertEqual(engine.formation_session(SESSIONS[5]), SESSIONS[5])


class ExposureIntervalTest(unittest.TestCase):
    def engine(self, geometry: GeometryChoice = FULL_GEOMETRY) -> FormationEngine:
        return FormationEngine(CALENDAR, geometry)

    def test_entry_is_never_the_edgar_date_itself(self):
        interval = self.engine().exposure(SESSIONS[0])
        self.assertTrue(interval.resolved)
        self.assertEqual(interval.entry_session, SESSIONS[1])

    def test_hold_is_twenty_sessions_under_the_declared_indexing(self):
        interval = self.engine().exposure(SESSIONS[0])
        self.assertEqual(interval.exit_session, SESSIONS[21])

    def test_o3_cannot_change_the_closed_holding_length(self):
        geometry = replace(FULL_GEOMETRY, o3=O3Convention("LONGER", 25))
        interval = self.engine(geometry).exposure(SESSIONS[0])
        self.assertEqual(interval.state, FORMATION_UNRESOLVED)
        self.assertIn("O3_CANNOT_CHANGE_THE_CLOSED_TWENTY_SESSION_HOLD", interval.detail)

    def test_alternative_indexing_inside_the_closed_hold_is_admissible(self):
        geometry = replace(FULL_GEOMETRY, o3=O3Convention("CLOSE_OF_TWENTIETH", 19))
        interval = self.engine(geometry).exposure(SESSIONS[0])
        self.assertTrue(interval.resolved)
        self.assertEqual(interval.exit_session, SESSIONS[20])

    def test_undeclared_o3_yields_no_interval(self):
        interval = self.engine(replace(FULL_GEOMETRY, o3=None)).exposure(SESSIONS[0])
        self.assertEqual(interval.state, FORMATION_UNRESOLVED)

    def test_calendar_ending_early_is_incomplete_not_truncated(self):
        interval = self.engine().exposure(SESSIONS[-2])
        self.assertEqual(interval.state, EXPOSURE_INTERVAL_INCOMPLETE)
        self.assertIsNone(interval.exit_session)

    def test_unobservable_session_routes_to_d19_without_a_payoff_substitute(self):
        missing = SESSIONS[10]
        interval = self.engine().exposure(SESSIONS[0],
                                          observable=lambda session: session != missing)
        self.assertEqual(interval.state, D19_TERMINAL_TREATMENT_REQUIRED)
        self.assertIn(missing, interval.detail)


class DesignInvarianceTest(unittest.TestCase):
    def space(self):
        return admissible_geometries(
            o2_orderings=("SOURCE_IDENTITY_ASCENDING", "OWNER_CIK_ASCENDING"),
            o3_conventions=(O3Convention("END_OF_TWENTIETH_SESSION", 20),
                            O3Convention("CLOSE_OF_TWENTIETH", 19)),
            o4_overlaps=("DISTINCT_SIGNALS_REMAIN_DISTINCT", "MERGE_OVERLAPPING"))

    def test_space_is_the_full_cross_product(self):
        self.assertEqual(len(self.space()), 2 * 2 * 2 * 2)

    def test_a_geometry_independent_quantity_is_d05a_eligible(self):
        observations = [observation("A", 0), observation("B", 1)]
        verdict = design_invariance(
            lambda geometry: len(observations), self.space(), "qualifying_filing_count")
        self.assertEqual(verdict.classification, DESIGN_INVARIANT)
        self.assertTrue(verdict.d05a_eligible)

    def test_a_quantity_that_moves_with_o1_is_design_sensitive(self):
        """A weekend EDGAR date can straddle the formation window boundary.

        Owner A attaches to session 0. The Saturday below projects to session 9
        under PREVIOUS_REGULAR_SESSION, where A is still inside the ten-session
        window, and to session 10 under NEXT_REGULAR_SESSION, where it is not.
        One admissible convention produces a formation and the other does not, so
        the event count is CLAIM-DESIGN-SENSITIVE and belongs to D05-B.
        """
        saturday = "2026-01-17"
        self.assertEqual(CALENDAR.previous_session(saturday), SESSIONS[9])
        self.assertEqual(CALENDAR.next_session(saturday), SESSIONS[10])
        observations = [QualifyingObservation("0009999991", "A", SESSIONS[0], "ACC-1"),
                        QualifyingObservation("0009999991", "B", saturday, "ACC-2")]

        def event_count(geometry):
            return FormationEngine(CALENDAR, geometry).run(observations)["event_count"]

        wide = admissible_geometries(
            o2_orderings=("SOURCE_IDENTITY_ASCENDING",),
            o3_conventions=(O3Convention("END_OF_TWENTIETH_SESSION", 20),),
            o4_overlaps=("DISTINCT_SIGNALS_REMAIN_DISTINCT",))
        counts = {description: event_count(geometry)
                  for description, geometry in zip(
                      ("previous", "next"), wide)}
        self.assertEqual(sorted(counts.values()), [0, 1])
        verdict = design_invariance(event_count, wide, "formation_event_count")
        self.assertEqual(verdict.classification, CLAIM_DESIGN_SENSITIVE)

    def test_an_unresolved_quantity_is_ambiguous_not_invariant(self):
        space = admissible_geometries(
            o2_orderings=("SOURCE_IDENTITY_ASCENDING",),
            o3_conventions=(O3Convention("END_OF_TWENTIETH_SESSION", 20),),
            o4_overlaps=("DISTINCT_SIGNALS_REMAIN_DISTINCT",))
        stripped = tuple(replace(geometry, o4_overlap=None) for geometry in space)
        verdict = design_invariance(
            lambda geometry: FormationEngine(CALENDAR, geometry)
            .run([observation("A", 0), observation("B", 1)])["observation_count"],
            stripped, "observation_count")
        self.assertEqual(verdict.classification, AMBIGUOUS_EMBARGO)

    def test_an_empty_space_cannot_establish_invariance(self):
        verdict = design_invariance(lambda geometry: 1, (), "anything")
        self.assertEqual(verdict.classification, AMBIGUOUS_EMBARGO)

    def test_a_quantity_that_raises_is_ambiguous(self):
        def broken(geometry):
            raise RuntimeError("undefined here")

        verdict = design_invariance(broken, self.space(), "broken")
        self.assertEqual(verdict.classification, AMBIGUOUS_EMBARGO)
        self.assertIn("QUANTITY_UNDEFINED_UNDER", joined(verdict.reasons))

    def test_the_space_actually_used_is_reported(self):
        verdict = design_invariance(lambda geometry: 1, self.space(), "constant")
        self.assertEqual(verdict.space["combinations"], 16)
        self.assertEqual(verdict.space["o1"], ["NEXT_REGULAR_SESSION",
                                               "PREVIOUS_REGULAR_SESSION"])


class RatioInferenceTest(unittest.TestCase):
    def test_point_estimate_is_exposure_weighted(self):
        estimate = ratio_estimate([900_000.0, 100_000.0], [0.001, 0.09])
        self.assertAlmostEqual(estimate.point, 0.0099, places=10)
        self.assertEqual(estimate.denominator, 1_000_000.0)

    def test_no_exposure_is_a_state_not_a_number(self):
        estimate = ratio_estimate([0.0, 0.0], [0.01, 0.02])
        self.assertEqual(estimate.state, ESTIMATE_NO_EXPOSURE)
        self.assertIsNone(estimate.point)

    def test_one_cluster_cannot_identify_a_variance(self):
        estimate = ratio_estimate([1.0, 1.0], [0.01, 0.02], clusters=["X", "X"])
        self.assertEqual(estimate.state, ESTIMATE_SINGLE_CLUSTER)
        self.assertIsNone(estimate.standard_error)
        self.assertIsNotNone(estimate.point)

    def test_clustering_correlated_observations_widens_the_interval(self):
        """Treating overlapping exposures as independent buys a bigger t for free."""
        weights = [1.0] * 12
        outcomes = ([0.05] * 3 + [-0.03] * 3) * 2
        clusters = ["A", "A", "A", "B", "B", "B", "C", "C", "C", "D", "D", "D"]
        independent = ratio_estimate(weights, outcomes)
        clustered = ratio_estimate(weights, outcomes, clusters=clusters)
        self.assertGreater(clustered.standard_error, independent.standard_error)
        self.assertEqual(clustered.clusters, 4)
        self.assertEqual(independent.clusters, 12)

    def test_interval_brackets_the_point_estimate(self):
        estimate = ratio_estimate([1.0] * 5, [0.01, 0.02, -0.01, 0.03, 0.0])
        self.assertLess(estimate.lower, estimate.point)
        self.assertGreater(estimate.upper, estimate.point)

    def test_bootstrap_is_reproducible_under_its_declared_seed(self):
        weights = [1.0] * 8
        outcomes = [0.02, -0.01, 0.03, 0.0, 0.01, 0.04, -0.02, 0.01]
        first = cluster_bootstrap_ratio(weights, outcomes, draws=200, seed=7)
        second = cluster_bootstrap_ratio(weights, outcomes, draws=200, seed=7)
        third = cluster_bootstrap_ratio(weights, outcomes, draws=200, seed=8)
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertNotEqual(first.lower, third.lower)

    def test_multiplicity_budget_cannot_shrink(self):
        budget = MultiplicityBudget(declared_trials=24)
        with self.assertRaises(ValueError):
            budget.narrow(10)

    def test_disclosing_more_trials_raises_the_threshold(self):
        budget = MultiplicityBudget(declared_trials=24)
        before = budget.threshold()
        budget.widen(100, "additional expressions searched")
        self.assertGreater(budget.threshold(), before)

    def test_charging_more_trials_than_declared_is_a_violation(self):
        budget = MultiplicityBudget(declared_trials=4)
        budget.charge(10, "grid")
        self.assertIn("TRIALS_CHARGED_EXCEED_DECLARED_BUDGET", joined(budget.violations()))

    def test_significant_but_economically_dominated_is_reported_as_both(self):
        estimate = ratio_estimate([1.0] * 40, [0.0005] * 39 + [0.0006])
        verdict = statistical_economic_verdict(estimate, meue=0.01,
                                               budget=MultiplicityBudget(1))
        self.assertEqual(verdict.statistical, STATISTICALLY_DISTINGUISHABLE)
        self.assertEqual(verdict.economic, ECONOMICALLY_DOMINATED)
        self.assertFalse(verdict.both_satisfied)

    def test_missing_economic_threshold_cannot_be_treated_as_satisfied(self):
        estimate = ratio_estimate([1.0] * 10, [0.02] * 10)
        verdict = statistical_economic_verdict(estimate, None, MultiplicityBudget(1))
        self.assertFalse(verdict.both_satisfied)
        self.assertIn("ECONOMIC_THRESHOLD_UNAVAILABLE", joined(verdict.violations))


class NullModelTest(unittest.TestCase):
    def test_placebo_offsets_inside_the_true_exposure_are_refused(self):
        admissible, refused = placebo_offsets(CALENDAR, [SESSIONS[25]], [0, 5, 20, 25, -25])
        self.assertNotIn(5, admissible)
        self.assertNotIn(20, admissible)
        self.assertIn(25, admissible)
        self.assertIn("PLACEBO_OFFSET_OVERLAPS_TRUE_EXPOSURE", joined(refused))

    def test_off_calendar_offsets_are_refused(self):
        admissible, refused = placebo_offsets(CALENDAR, [SESSIONS[-1]], [25])
        self.assertEqual(admissible, [])
        self.assertIn("PLACEBO_OFFSET_OFF_CALENDAR", joined(refused))

    def test_placebo_null_produces_one_draw_per_admissible_offset(self):
        entries = [SESSIONS[25], SESSIONS[26]]
        measured = {session: 0.001 * index for index, session in enumerate(SESSIONS)}
        draws = placebo_null([1.0, 1.0], entries, lambda session: measured[session],
                             CALENDAR, [21, 22, -21])
        self.assertEqual(len(draws.draws), 3)

    def test_empirical_p_value_is_never_zero(self):
        self.assertGreater(empirical_p_value(10.0, [0.0] * 100), 0.0)
        self.assertAlmostEqual(empirical_p_value(10.0, [0.0] * 99), 1.0 / 100.0, places=12)

    def test_p_value_is_none_without_draws(self):
        self.assertIsNone(empirical_p_value(1.0, []))

    def test_sign_flip_null_needs_more_than_one_cluster(self):
        draws = cluster_sign_flip_null([1.0, 1.0], [0.01, 0.02], clusters=["A", "A"])
        self.assertEqual(draws.draws, ())
        self.assertIn("VARIANCE_UNIDENTIFIED_FROM_ONE_CLUSTER", joined(draws.refused))

    def test_sign_flip_null_is_centred_near_zero(self):
        draws = cluster_sign_flip_null([1.0] * 6, [0.03, -0.01, 0.02, 0.0, -0.02, 0.01],
                                       clusters=["A", "A", "B", "B", "C", "C"], draws=500)
        mean = sum(draws.draws) / len(draws.draws)
        self.assertLess(abs(mean), 0.01)


class RegimeTest(unittest.TestCase):
    def partition(self, **overrides) -> RegimePartition:
        fields = dict(partition_id="VOL_REGIME_V1", regimes=("LOW_VOL", "HIGH_VOL"),
                      declared_at="2026-09-01T00:00:00+00:00",
                      derived_from=("BENCHMARK_REALISED_VOLATILITY",),
                      assign=lambda session: "LOW_VOL" if session < SESSIONS[5]
                      else "HIGH_VOL")
        fields.update(overrides)
        return RegimePartition(**fields)

    def test_partition_derived_from_outcomes_is_refused(self):
        problems = self.partition(derived_from=("TARGET_OUTCOMES",)).violations()
        self.assertIn(POST_HOC_REFUSED, joined(problems))

    def test_partition_declared_after_outcome_observation_is_refused(self):
        problems = self.partition().violations(outcome_observed_at="2026-08-01T00:00:00+00:00")
        self.assertIn("DECLARED_AT_OR_AFTER_OUTCOME_OBSERVATION", joined(problems))

    def test_single_regime_is_not_a_partition(self):
        self.assertIn("PARTITION_NEEDS_AT_LEAST_TWO_REGIMES",
                      joined(self.partition(regimes=("ONLY",)).violations()))

    def test_breakdown_reports_pooled_as_the_headline(self):
        keys = SESSIONS[:10]
        weights = [1.0] * 10
        outcomes = [0.05] * 5 + [-0.01] * 5
        breakdown = regime_breakdown(self.partition(), keys, weights, outcomes)
        self.assertEqual(breakdown.violations, ())
        self.assertAlmostEqual(breakdown.headline.point, 0.02, places=12)
        self.assertEqual(sorted(breakdown.counts), ["HIGH_VOL", "LOW_VOL"])
        self.assertAlmostEqual(breakdown.spread(), 0.06, places=12)
        self.assertEqual(breakdown.to_dict()["headline_rule"], BEST_REGIME_IS_NOT_THE_RESULT)

    def test_refused_partition_still_reports_the_pooled_estimate(self):
        breakdown = regime_breakdown(self.partition(derived_from=("STRATEGY_PNL",)),
                                     SESSIONS[:4], [1.0] * 4, [0.01, 0.02, 0.0, 0.03])
        self.assertIn(POST_HOC_REFUSED, joined(breakdown.violations))
        self.assertEqual(breakdown.by_regime, {})
        self.assertIsNotNone(breakdown.pooled.point)

    def test_undeclared_regime_label_is_reported(self):
        partition = self.partition(assign=lambda session: "SIDEWAYS")
        breakdown = regime_breakdown(partition, SESSIONS[:3], [1.0] * 3, [0.01, 0.0, 0.02])
        self.assertIn("REGIME_LABEL_NOT_DECLARED:SIDEWAYS", joined(breakdown.violations))


if __name__ == "__main__":
    unittest.main()
