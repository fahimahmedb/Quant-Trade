"""A second research family, and the checks that keep it a second family.

Synthetic bars throughout. The important tests are the structural ones: that the
peer score never reads the asset's own return, that peer selection cannot see the
returns the signal is made of, and that a declared independence which fails
empirically is reported as collinear rather than kept.
"""

from __future__ import annotations

import math
import unittest
from datetime import datetime, timedelta

from quant.dataplane.panel import PricePanel
from quant.factory.families import (CROSS_SECTIONAL_AXES, DEFAULT_CORRELATION_WINDOW,
                                    EMPIRICALLY_COLLINEAR, FAMILY_PEER_LEAD_LAG,
                                    PEER_LEAD_LAG_AXES, SHARES_INPUT_AND_MECHANISM,
                                    STRUCTURALLY_INDEPENDENT, declared_trial_count,
                                    independence_report, lead_lag_lane_definition,
                                    peer_lead_lag_scores, weights_for_family)
from quant.factory.prioritization import (HypothesisCandidate, PriorityRanking, rank)
from quant.factory.signals import StrategySpec


UNIVERSE = ["AAA", "BBB", "CCC", "DDD", "EEE"]


def session_date(index: int) -> str:
    return (datetime(2024, 1, 1) + timedelta(days=index)).date().isoformat()


def panel_from(levels: dict[str, list[float]]) -> PricePanel:
    rows = []
    sessions = len(next(iter(levels.values())))
    for index in range(sessions):
        for symbol, series in levels.items():
            price = series[index]
            rows.append({"date": session_date(index), "symbol": symbol,
                         "open": price, "high": price, "low": price, "close": price,
                         "adj_close": price, "volume": 4_000_000.0})
    return PricePanel(rows)


def wave_panel(sessions: int = 200) -> PricePanel:
    levels: dict[str, list[float]] = {}
    for position, symbol in enumerate(UNIVERSE):
        level = 100.0
        series = []
        for index in range(sessions):
            level *= 1.0 + 0.01 * math.sin((index + position * 5) * 0.19) + 0.0002
            series.append(level)
        levels[symbol] = series
    return panel_from(levels)


def spec(family: str = FAMILY_PEER_LEAD_LAG, lookback: int = 5) -> StrategySpec:
    return StrategySpec(family=family, universe=UNIVERSE, lookback_days=lookback,
                        direction=1, min_abs_score=0.0, dataset_id="SYNTHETIC")


class PeerLeadLagTest(unittest.TestCase):
    def setUp(self):
        self.panel = wave_panel()
        self.asof = session_date(150)

    def test_scores_are_produced_for_every_name(self):
        scores = peer_lead_lag_scores(self.panel, UNIVERSE, self.asof, 5)
        self.assertEqual(sorted(scores), sorted(UNIVERSE))

    def test_insufficient_history_returns_no_signal_not_zero(self):
        early = session_date(DEFAULT_CORRELATION_WINDOW)
        self.assertEqual(peer_lead_lag_scores(self.panel, UNIVERSE, early, 5), {})

    def test_universe_too_small_for_peer_selection_returns_no_signal(self):
        small = UNIVERSE[:3]
        self.assertEqual(peer_lead_lag_scores(self.panel, small, self.asof, 5,
                                             peer_count=3), {})

    def test_score_ignores_the_name_own_return(self):
        """Move one name violently in the signal window; its own score must not follow.

        The score for a name is built from its peers, so a shock confined to the
        name itself can only reach that name's score through the cross-sectional
        demeaning of *other* names' scores, never through its own return.
        """
        sessions = 200
        base = wave_panel(sessions)
        levels: dict[str, list[float]] = {}
        for symbol in UNIVERSE:
            levels[symbol] = [base.price(session_date(index), symbol)
                              for index in range(sessions)]
        # AAA jumps 30% inside the signal window only.
        for index in range(146, sessions):
            levels["AAA"][index] *= 1.30
        shocked = panel_from(levels)
        before = peer_lead_lag_scores(base, UNIVERSE, self.asof, 5)
        after = peer_lead_lag_scores(shocked, UNIVERSE, self.asof, 5)
        own_change = abs(after["AAA"] - before["AAA"])
        peer_change = max(abs(after[symbol] - before[symbol])
                          for symbol in UNIVERSE if symbol != "AAA")
        # AAA's own shock shows up in its peers' scores, not predominantly in its own.
        self.assertGreater(peer_change, 0.0)
        self.assertLessEqual(own_change, peer_change + 1e-12)

    def test_peer_selection_window_ends_before_the_signal_window(self):
        """A change confined to the signal window cannot alter peer selection.

        If the correlation window overlapped the signal window, perturbing only
        the signal window could reorder peers. The scores may move (the peers'
        returns changed) but the selected peer sets must not.
        """
        from quant.factory.families import _most_correlated  # noqa: PLC0415

        sessions = 200
        base = wave_panel(sessions)
        levels = {symbol: [base.price(session_date(index), symbol)
                           for index in range(sessions)] for symbol in UNIVERSE}
        for index in range(146, sessions):
            levels["BBB"][index] *= 1.25
        shocked = panel_from(levels)

        def peer_sets(panel: PricePanel) -> dict[str, list[str]]:
            dates = panel.aligned_dates(UNIVERSE)
            position = panel.aligned_index(UNIVERSE, self.asof)
            correlation_end = position - 5
            window = dates[correlation_end - DEFAULT_CORRELATION_WINDOW:correlation_end + 1]
            daily = {}
            for symbol in UNIVERSE:
                daily[symbol] = [panel.price(later, symbol) / panel.price(earlier, symbol) - 1.0
                                 for earlier, later in zip(window, window[1:])]
            return {symbol: _most_correlated(symbol, UNIVERSE, daily, 3)
                    for symbol in UNIVERSE}

        self.assertEqual(peer_sets(base), peer_sets(shocked))
        self.assertNotEqual(peer_lead_lag_scores(base, UNIVERSE, self.asof, 5),
                            peer_lead_lag_scores(shocked, UNIVERSE, self.asof, 5))

    def test_weights_are_dollar_neutral(self):
        weights = weights_for_family(self.panel, spec(), self.asof)
        self.assertTrue(weights)
        self.assertAlmostEqual(sum(weights.values()), 0.0, places=9)

    def test_unknown_family_yields_no_weights(self):
        self.assertEqual(weights_for_family(self.panel, spec(family="not_a_family"),
                                            self.asof), {})

    def test_cross_sectional_family_still_routes_correctly(self):
        weights = weights_for_family(self.panel, spec(family="cross_sectional"), self.asof)
        self.assertTrue(weights)
        self.assertAlmostEqual(sum(weights.values()), 0.0, places=9)


class IndependenceTest(unittest.TestCase):
    def test_a_family_compared_with_itself_shares_its_mechanism(self):
        report = independence_report(CROSS_SECTIONAL_AXES, CROSS_SECTIONAL_AXES)
        self.assertEqual(report.verdict, SHARES_INPUT_AND_MECHANISM)
        self.assertFalse(report.independent)

    def test_declared_axes_differ_between_the_two_families(self):
        report = independence_report(CROSS_SECTIONAL_AXES, PEER_LEAD_LAG_AXES)
        self.assertIn("uses_own_return", report.distinct_axes)
        self.assertIn("uses_peer_returns", report.distinct_axes)
        self.assertIn("exposure_construction", report.shared_axes)

    def test_declared_independence_is_checked_against_realised_scores(self):
        panel = wave_panel(240)
        sessions = [session_date(index) for index in range(150, 170)]
        report = independence_report(CROSS_SECTIONAL_AXES, PEER_LEAD_LAG_AXES, panel,
                                     UNIVERSE, sessions, lookback_days=5)
        self.assertGreater(report.sessions_compared, 0)
        self.assertIsNotNone(report.realised_correlation)
        self.assertIn(report.verdict, (STRUCTURALLY_INDEPENDENT, EMPIRICALLY_COLLINEAR))

    def test_a_collinear_pair_is_refused_even_when_declared_independent(self):
        panel = wave_panel(240)
        sessions = [session_date(index) for index in range(150, 170)]
        report = independence_report(CROSS_SECTIONAL_AXES, PEER_LEAD_LAG_AXES, panel,
                                     UNIVERSE, sessions, lookback_days=5, threshold=-1.0)
        self.assertEqual(report.verdict, EMPIRICALLY_COLLINEAR)


class DeclaredLaneTest(unittest.TestCase):
    def test_the_grid_is_declared_and_countable_before_running(self):
        self.assertEqual(declared_trial_count(UNIVERSE, "SYNTHETIC"), 6 * 2 * 2 * 2)

    def test_the_lane_states_its_mechanism_and_falsification(self):
        definition = lead_lag_lane_definition(UNIVERSE, "SYNTHETIC")
        entry = definition["peer_lead_lag_diffusion"]
        self.assertIn("different speeds", entry["mechanism"])
        self.assertIn("double those costs", entry["falsification"])
        self.assertEqual(entry["independence_claim"]["family"], FAMILY_PEER_LEAD_LAG)

    def test_every_grid_member_belongs_to_the_declared_family(self):
        grid = lead_lag_lane_definition(UNIVERSE, "SYNTHETIC")["peer_lead_lag_diffusion"]["grid"]
        self.assertTrue(all(item.family == FAMILY_PEER_LEAD_LAG for item in grid))


class PrioritizationTest(unittest.TestCase):
    def candidate(self, **overrides) -> HypothesisCandidate:
        fields = dict(hypothesis_id="H1", family="peer_lead_lag", information_value=0.6,
                      builder_days=2.0, sessions_to_falsification=40,
                      capital_potential=500_000.0,
                      priority_inputs=("PUBLISHED_MECHANISM_LITERATURE",
                                       "BUILDER_EFFORT_ESTIMATE"))
        fields.update(overrides)
        return HypothesisCandidate(**fields)

    def test_admissible_candidate_scores(self):
        self.assertIsNotNone(self.candidate().score)

    def test_p0_reservoir_can_never_be_a_priority_signal(self):
        candidate = self.candidate(
            priority_inputs=("PUBLISHED_MECHANISM_LITERATURE", "P0_PROSPECTIVE_FILING_COUNT"))
        self.assertIn("P0_RESERVOIR_IS_NEVER_A_PRIORITY_SIGNAL",
                      " | ".join(candidate.violations()))
        self.assertIsNone(candidate.score)

    def test_undeclared_priority_inputs_are_refused(self):
        self.assertIn("PRIORITY_INPUTS_UNDECLARED",
                      " | ".join(self.candidate(priority_inputs=()).violations()))

    def test_ranking_orders_by_value_over_cost(self):
        cheap = self.candidate(hypothesis_id="CHEAP", builder_days=1.0)
        expensive = self.candidate(hypothesis_id="EXPENSIVE", builder_days=20.0)
        ranking = rank("R1", [expensive, cheap])
        self.assertEqual(ranking.order(), ["CHEAP", "EXPENSIVE"])

    def test_inadmissible_candidate_is_refused_not_ranked_low(self):
        bad = self.candidate(hypothesis_id="LEAK",
                             priority_inputs=("P0_PROSPECTIVE_OUTCOMES",))
        ranking = rank("R2", [self.candidate(), bad])
        self.assertEqual(ranking.order(), ["H1"])
        self.assertEqual([item.hypothesis_id for item in ranking.refused], ["LEAK"])

    def test_unsatisfied_prerequisite_refuses_the_candidate(self):
        blocked = self.candidate(hypothesis_id="BLOCKED",
                                 prerequisites=("D07_GEOMETRY_FROZEN",))
        ranking = rank("R3", [blocked])
        self.assertEqual(ranking.order(), [])
        self.assertIn("PREREQUISITES_UNSATISFIED:D07_GEOMETRY_FROZEN",
                      " | ".join(ranking.violations))

    def test_satisfied_prerequisite_admits_the_candidate(self):
        blocked = self.candidate(hypothesis_id="READY",
                                 prerequisites=("D07_GEOMETRY_FROZEN",))
        ranking = rank("R4", [blocked], satisfied_prerequisites=["D07_GEOMETRY_FROZEN"])
        self.assertEqual(ranking.order(), ["READY"])

    def test_ranking_carries_its_rule_hash(self):
        ranking = rank("R5", [self.candidate()])
        self.assertTrue(ranking.to_dict()["rule_hash"].startswith("sha256:"))
        self.assertIsInstance(ranking, PriorityRanking)


if __name__ == "__main__":
    unittest.main()
