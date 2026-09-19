"""Causal timeline, opening execution, sizing and research/execution consistency.

The tests that matter here are the ones that fail when something is *quietly*
wrong: an input dated after the decision that used it, an execution cost measured
against the prior close so the overnight gap is charged as slippage, a risk
approval taken against a pre-scale portfolio, and a research cost assumption
cheaper than the desk's own modelled execution.
"""

from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import economics_fixtures as fixtures
from quant.desk.execution import ExecutionModel, RESEARCH_ONE_WAY_COST_BPS
from quant.economics import (CausalEventLedger, EffectEstimate, EventTimeline,
                             ExecutionCostModel, FrictionCharge, InformationInput,
                             MarginSizingRule, NetOutcome,
                             OpeningExecutionModel, PortfolioInteraction, RiskApproval,
                             SizingPlan, SleeveTarget, aggregate_allocation_weighted,
                             combine_lanes, economic_gate, implied_participation_ceiling,
                             size_lane, verify_research_cost_consistency,
                             verify_risk_approval)
from quant.economics.decision import EVIDENCE_DEVELOPMENT
from quant.economics.opening import (MECHANISM_CONTINUOUS_AFTER_OPEN,
                                     MECHANISM_OPENING_AUCTION, REFERENCE_AUTHORIZED_OPEN,
                                     REFERENCE_PRIOR_CLOSE)
from quant.economics.states import NO_TRADE
from quant.economics.timeline import BASIS_GROSS, BASIS_NET, BASIS_TURNOVER


def joined(problems) -> str:
    return " | ".join(problems)


def timeline(**overrides) -> EventTimeline:
    fields = dict(
        event_id="EVT_1",
        public_observability_at="2026-09-17T20:35:00+00:00",
        decision_at="2026-09-17T21:00:00+00:00",
        executable_at="2026-09-18T13:30:00+00:00",
        entry_fill_at="2026-09-18T13:30:05+00:00",
        exit_decision_at="2026-09-25T20:00:00+00:00",
        exit_fill_at="2026-09-28T13:30:05+00:00",
        marked_at="2026-09-28T20:00:00+00:00",
        inputs=(InformationInput("form4_filing", "2026-09-17T20:35:00+00:00", "EDGAR"),
                InformationInput("adv_lookback", "2026-09-17", "PRICE_PANEL")),
    )
    fields.update(overrides)
    return EventTimeline(**fields)


class CausalTimelineTest(unittest.TestCase):
    def test_a_well_ordered_event_is_causal(self):
        self.assertTrue(timeline().causal)

    def test_input_dated_after_the_decision_is_lookahead(self):
        late = InformationInput("next_day_close", "2026-09-18T20:00:00+00:00", "PRICE_PANEL")
        problems = timeline(inputs=(late,)).violations()
        self.assertIn("LOOKAHEAD_INPUT_NOT_YET_AVAILABLE:next_day_close", joined(problems))

    def test_date_and_timestamp_inputs_are_compared_on_one_scale(self):
        """A bare date must not slip past a same-day timestamp comparison."""
        same_day = InformationInput("close_of_decision_day", "2026-09-18", "PRICE_PANEL")
        problems = timeline(inputs=(same_day,)).violations()
        self.assertIn("LOOKAHEAD_INPUT_NOT_YET_AVAILABLE:close_of_decision_day",
                      joined(problems))

    def test_fill_before_the_first_authorized_open_is_out_of_order(self):
        problems = timeline(entry_fill_at="2026-09-18T09:00:00+00:00").violations()
        self.assertIn("STAGE_OUT_OF_CAUSAL_ORDER:ENTRY_FILL_BEFORE_EXECUTABLE",
                      joined(problems))

    def test_entry_cannot_precede_public_observability(self):
        problems = timeline(public_observability_at="2026-09-19T20:35:00+00:00",
                            decision_at="2026-09-19T21:00:00+00:00",
                            executable_at="2026-09-18T13:30:00+00:00").violations()
        self.assertIn("ENTRY_PRECEDES_PUBLIC_OBSERVABILITY", joined(problems))

    def test_book_cannot_be_marked_before_the_fill(self):
        problems = timeline(marked_at="2026-09-18T13:00:00+00:00").violations()
        self.assertIn("BOOK_MARKED_BEFORE_FILL", joined(problems))

    def test_non_point_in_time_input_is_flagged(self):
        restated = InformationInput("restated_fundamentals", "2026-09-16", "VENDOR",
                                    point_in_time=False)
        self.assertIn("INPUT_NOT_POINT_IN_TIME:restated_fundamentals",
                      joined(timeline(inputs=(restated,)).violations()))


class NetOutcomeTest(unittest.TestCase):
    def outcome(self, **overrides) -> NetOutcome:
        fields = dict(event_id="EVT_1", notional=100_000.0, security_return=0.03,
                      benchmark_return=0.01,
                      charges=(FrictionCharge("F1_EXPLICIT_FEES", 0.5, BASIS_TURNOVER),
                               FrictionCharge("F2_OPEN_ENTRY_CROSSING", 1.0)),
                      research_charge_bps=5.0)
        fields.update(overrides)
        return NetOutcome(**fields)

    def test_excess_is_gross_spy_relative(self):
        self.assertAlmostEqual(self.outcome().excess_return, 0.02, places=12)

    def test_net_pnl_subtracts_the_charged_frictions(self):
        outcome = self.outcome()
        self.assertAlmostEqual(outcome.executed_charge_bps, 2.0, places=12)
        self.assertAlmostEqual(outcome.friction_cost, 20.0, places=12)
        self.assertAlmostEqual(outcome.net_pnl, 2_000.0 - 20.0, places=12)

    def test_net_of_friction_return_is_refused_as_the_coordinate(self):
        problems = self.outcome(return_basis=BASIS_NET).violations()
        self.assertIn("DELTA_IS_GROSS_OF_FORM4_DEPLOYMENT_FRICTIONS", joined(problems))

    def test_research_cheaper_than_execution_is_refused(self):
        problems = self.outcome(research_charge_bps=1.0).violations()
        self.assertIn("RESEARCH_EVIDENCE_CHEAPER_THAN_EXECUTION", joined(problems))

    def test_duplicate_friction_class_is_refused(self):
        charges = (FrictionCharge("F2_OPEN_ENTRY_CROSSING", 1.0),
                   FrictionCharge("F2_OPEN_ENTRY_CROSSING", 1.0))
        self.assertIn("DUPLICATE_FRICTION_CHARGE_CLASS",
                      joined(self.outcome(charges=charges).violations()))

    def test_benchmark_substitution_is_refused(self):
        self.assertIn("SCIENTIFIC_BENCHMARK_REMAINS_SPY",
                      joined(self.outcome(benchmark_symbol="QQQ").violations()))

    def test_aggregation_is_exposure_weighted_with_a_reported_denominator(self):
        big = self.outcome(event_id="BIG", notional=900_000.0, security_return=0.011,
                           benchmark_return=0.01)
        small = self.outcome(event_id="SMALL", notional=100_000.0, security_return=0.10,
                             benchmark_return=0.01)
        result = aggregate_allocation_weighted([big, small])
        # Unweighted mean of the excesses would be 4.55%; the deployment-weighted
        # coordinate is 0.99%, and the difference is the whole point of EC1 s5.
        self.assertAlmostEqual(result["delta_hat"], 0.0099, places=10)
        self.assertEqual(result["denominator"], 1_000_000.0)
        self.assertEqual(result["event_count"], 2)

    def test_aggregation_with_no_exposure_reports_a_state_not_a_number(self):
        result = aggregate_allocation_weighted([self.outcome(notional=0.0)])
        self.assertIsNone(result["delta_hat"])
        self.assertEqual(result["state"], "NO_DEPLOYED_EXPOSURE")

    def test_aggregation_surfaces_member_violations(self):
        result = aggregate_allocation_weighted([self.outcome(return_basis=BASIS_NET)])
        self.assertIn("DELTA_IS_GROSS_OF_FORM4_DEPLOYMENT_FRICTIONS",
                      joined(result["violations"]))


class CausalEventLedgerTest(unittest.TestCase):
    def test_recording_the_same_stage_twice_is_a_no_op(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            ledger = CausalEventLedger(path)
            self.assertTrue(ledger.record("EVT_1", "ENTRY_FILL", {"price": 10.0}))
            self.assertFalse(ledger.record("EVT_1", "ENTRY_FILL", {"price": 10.0}))
            self.assertEqual(len(path.read_text().strip().splitlines()), 1)

    def test_replay_after_restart_reaches_the_same_state(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            first = CausalEventLedger(path)
            first.record("EVT_1", "DECISION", {"weight": 0.1})
            first.record("EVT_1", "ENTRY_FILL", {"price": 10.0})
            reopened = CausalEventLedger(path)
            self.assertFalse(reopened.record("EVT_1", "ENTRY_FILL", {"price": 99.0}))
            state = reopened.replay()
            self.assertEqual(state["EVT_1"]["ENTRY_FILL"], {"price": 10.0})
            self.assertEqual(len(reopened), 2)

    def test_torn_final_append_is_recovered_not_duplicated(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            ledger = CausalEventLedger(path)
            ledger.record("EVT_1", "DECISION", {"weight": 0.1})
            with path.open("a", encoding="utf-8") as handle:
                handle.write('{"operation_id": "torn", "event_id": "EVT_2"')
            reopened = CausalEventLedger(path)
            self.assertTrue(reopened.record("EVT_2", "DECISION", {"weight": 0.2}))
            self.assertEqual(len(reopened.replay()), 2)

    def test_unknown_stage_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = CausalEventLedger(Path(directory) / "events.jsonl")
            with self.assertRaises(ValueError):
                ledger.record("EVT_1", "PROFIT", {})


class OpeningExecutionTest(unittest.TestCase):
    def model(self, **overrides) -> OpeningExecutionModel:
        fields = dict(mechanism=MECHANISM_OPENING_AUCTION, half_spread_bps=1.0,
                      impact_bps_at_reference=10.0, reference_participation=0.05,
                      calibration_regime=MECHANISM_OPENING_AUCTION,
                      provenance="ASSUMED_V1_EXECUTION_PARAMETER")
        fields.update(overrides)
        return OpeningExecutionModel(**fields)

    def test_overnight_gap_is_reported_but_not_charged(self):
        fill = self.model().fill(101.0, 1_000.0, 50_000_000.0, prior_close=100.0)
        self.assertEqual(fill["violations"], [])
        self.assertAlmostEqual(fill["overnight_gap_bps"], 100.0, places=9)
        self.assertEqual(fill["overnight_gap_classification"],
                         "MARKET_RETURN_NOT_EXECUTION_COST")
        # The 100 bps gap must not appear in the execution loss.
        self.assertLess(fill["execution_loss_bps"], 5.0)
        self.assertEqual(fill["reference_price"], 101.0)

    def test_measuring_against_prior_close_double_counts_market_return(self):
        fill = self.model().fill(101.0, 1_000.0, 50_000_000.0, prior_close=100.0,
                                 reference_basis=REFERENCE_PRIOR_CLOSE)
        self.assertIn("OPEN_EXECUTION_COST_MUST_NOT_DOUBLE_COUNT_MARKET_RETURN",
                      joined(fill["violations"]))

    def test_intraday_calibration_is_not_automatic_opening_authority(self):
        model = self.model(calibration_regime=MECHANISM_CONTINUOUS_AFTER_OPEN)
        self.assertIn("GENERIC_INTRADAY_SPREAD_IS_NOT_AUTOMATIC_OPEN_CALIBRATION",
                      joined(model.violations()))

    def test_capacity_truncation_is_reported(self):
        fill = self.model().fill(100.0, 1_000_000.0, 10_000_000.0)
        self.assertTrue(fill["capacity_truncated"])
        self.assertAlmostEqual(fill["notional"], 500_000.0, places=6)
        self.assertAlmostEqual(fill["participation"], 0.05, places=12)

    def test_impact_grows_with_participation(self):
        model = self.model()
        self.assertLess(model.impact_bps(0.01), model.impact_bps(0.04))
        self.assertAlmostEqual(model.impact_bps(0.05), 10.0, places=12)

    def test_fill_price_moves_against_the_side(self):
        model = self.model()
        buy = model.fill(100.0, 1_000.0, 50_000_000.0)
        sell = model.fill(100.0, -1_000.0, 50_000_000.0)
        self.assertGreater(buy["fill_price"], 100.0)
        self.assertLess(sell["fill_price"], 100.0)


class ResearchExecutionConsistencyTest(unittest.TestCase):
    """Defect ECON-001, reproduced from the shipped V1 constants."""

    def setUp(self):
        self.execution = ExecutionModel()
        self.model = ExecutionCostModel.from_execution_model(self.execution)

    def test_v1_research_assumption_does_not_cover_modelled_execution_at_max_size(self):
        check = verify_research_cost_consistency(
            RESEARCH_ONE_WAY_COST_BPS, self.model, self.execution.max_participation,
            "V1_DESK_AT_MAX_PARTICIPATION")
        self.assertFalse(check.consistent)
        self.assertAlmostEqual(check.modelled_cost_bps, 11.5, places=9)
        self.assertAlmostEqual(check.understatement_bps, 6.5, places=9)
        self.assertIn("RESEARCH_EVIDENCE_CHEAPER_THAN_EXECUTION", joined(check.violations()))

    def test_implied_participation_ceiling_is_far_below_the_desk_limit(self):
        ceiling = implied_participation_ceiling(RESEARCH_ONE_WAY_COST_BPS, self.model)
        self.assertAlmostEqual(ceiling, 0.006125, places=9)
        self.assertLess(ceiling, self.execution.max_participation)

    def test_below_the_ceiling_the_research_evidence_is_consistent(self):
        check = verify_research_cost_consistency(RESEARCH_ONE_WAY_COST_BPS, self.model,
                                                0.006, "SMALL_SIZE")
        self.assertTrue(check.consistent)

    def test_no_positive_participation_when_fixed_costs_already_exceed_research(self):
        expensive = replace(self.model, commission_bps=4.0, half_spread_bps=2.0)
        self.assertEqual(implied_participation_ceiling(RESEARCH_ONE_WAY_COST_BPS, expensive),
                         0.0)

    def test_inconsistent_evidence_blocks_the_economic_gate(self):
        recipe = fixtures.meue_recipe()
        theta = fixtures.theta_state()
        effect = EffectEstimate(delta_hat=0.05, lower=0.04, upper=0.06, confidence_level=0.95,
                                evidence_label=EVIDENCE_DEVELOPMENT,
                                sample_provenance="SYNTHETIC_FIXTURE")
        check = verify_research_cost_consistency(RESEARCH_ONE_WAY_COST_BPS, self.model,
                                                self.execution.max_participation, "LANE")
        verdict = economic_gate(effect, recipe.evaluate(theta), theta,
                                PortfolioInteraction(0.0, residual_beta=0.0),
                                consistency=check)
        self.assertEqual(verdict.verdict, NO_TRADE)
        self.assertIn("RESEARCH_EVIDENCE_CHEAPER_THAN_EXECUTION", joined(verdict.violations))
        self.assertIn("RESEARCH_EXECUTION_CONSISTENCY",
                      [step["step"] for step in verdict.chain])


class SizingTest(unittest.TestCase):
    def rule(self) -> MarginSizingRule:
        return MarginSizingRule("MARGIN_LINEAR_TEST", reference_margin=0.01,
                                max_fraction=0.25, minimum_margin=0.0)

    def test_no_margin_means_no_exposure(self):
        plan = size_lane("PLAN_1", self.rule(), 0.0, 1_000_000.0, {"AAA": 1.0}, "S1")
        self.assertEqual(plan.gross_notional, 0.0)

    def test_size_is_monotone_in_the_margin_of_safety(self):
        rule = self.rule()
        small = size_lane("P", rule, 0.002, 1_000_000.0, {"AAA": 1.0}, "S1")
        large = size_lane("P", rule, 0.008, 1_000_000.0, {"AAA": 1.0}, "S1")
        self.assertLess(small.gross_notional, large.gross_notional)

    def test_size_is_capped_at_the_declared_maximum(self):
        plan = size_lane("P", self.rule(), 10.0, 1_000_000.0, {"AAA": 1.0}, "S1")
        self.assertAlmostEqual(plan.gross_notional, 250_000.0, places=6)

    def test_relative_weights_survive_sizing(self):
        plan = size_lane("P", self.rule(), 0.01, 1_000_000.0, {"AAA": 2.0, "BBB": 1.0}, "S1")
        aggregate = plan.aggregate()
        self.assertAlmostEqual(aggregate["AAA"] / aggregate["BBB"], 2.0, places=12)

    def test_sleeves_stay_separate_when_two_strategies_share_an_instrument(self):
        first = size_lane("P1", self.rule(), 0.01, 1_000_000.0, {"AAA": 1.0}, "S1")
        second = size_lane("P2", self.rule(), 0.005, 1_000_000.0, {"AAA": 1.0}, "S2")
        merged = combine_lanes("PORTFOLIO", [first, second])
        sleeves = merged.by_strategy()
        self.assertEqual(sorted(sleeves), ["S1", "S2"])
        self.assertAlmostEqual(merged.aggregate()["AAA"],
                               sleeves["S1"]["AAA"] + sleeves["S2"]["AAA"], places=9)

    def test_risk_approval_is_bound_to_the_final_state(self):
        plan = size_lane("P", self.rule(), 0.01, 1_000_000.0, {"AAA": 1.0}, "S1").finalise()
        approval = RiskApproval(True, plan.final_state_hash(), "RISK_STAGE")
        self.assertEqual(verify_risk_approval(plan, approval), [])

    def test_approval_of_a_pre_scale_portfolio_is_refused(self):
        plan = size_lane("P", self.rule(), 0.01, 1_000_000.0, {"AAA": 1.0}, "S1")
        stale = RiskApproval(True, plan.final_state_hash(), "RISK_STAGE")
        scaled = plan.transformed(
            "THROTTLE", [replace(target, notional=target.notional * 0.5)
                         for target in plan.sleeves]).finalise()
        problems = verify_risk_approval(scaled, stale)
        self.assertIn("RISK_APPROVAL_MUST_DESCRIBE_FINAL_PORTFOLIO", joined(problems))

    def test_a_final_plan_cannot_be_transformed_again(self):
        plan = size_lane("P", self.rule(), 0.01, 1_000_000.0, {"AAA": 1.0}, "S1").finalise()
        with self.assertRaises(ValueError):
            plan.transformed("SNEAKY_SCALE", plan.sleeves)

    def test_unfinalised_plan_cannot_be_approved(self):
        plan = size_lane("P", self.rule(), 0.01, 1_000_000.0, {"AAA": 1.0}, "S1")
        problems = verify_risk_approval(plan, RiskApproval(True, plan.final_state_hash(), "R"))
        self.assertIn("PLAN_NOT_MARKED_FINAL", joined(problems))

    def test_transform_history_is_part_of_the_final_identity(self):
        base = SizingPlan("P", (SleeveTarget("S1", "AAA", 100.0),))
        renamed = base.transformed("SCALE", base.sleeves)
        self.assertNotEqual(base.final_state_hash(), renamed.final_state_hash())


if __name__ == "__main__":
    unittest.main()
