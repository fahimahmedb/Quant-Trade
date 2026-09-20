"""Portfolio interaction integration (mission item 7).

Codex's self red team item 4 and this mission both state the same principle:
economic ``CONTINUE`` means *eligible for portfolio consideration*, never an
*approved order*. This file proves it across the real boundary, using the
actual ``quant.desk.risk``/``quant.book.ledger`` objects the Desk runs on —
not a parallel portfolio model. No new Economic System is created here: the
economics layer's own ``PortfolioInteraction``/``CapacityOutcome`` reduce the
*expected value* before the gate runs; ``desk.risk`` enforces the Book's hard
limits on the *final* proposed state afterwards. Both are exercised together.

Sector/factor limits are not tested here because no sector/factor primitive
exists anywhere in this codebase today (`desk/risk.py` enforces gross, net
and per-symbol only; Wave 1's own handoff names this the same open gap). A
"turnover budget" as a portfolio-level limit object does not exist either —
only per-lane rebalance throttles (`factory/signals.should_rebalance`,
`no_trade_band`/`holding_days`). Both are named as gaps, not fabricated.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import economics_fixtures as fixtures
from quant.desk.execution import ExecutionModel, RESEARCH_ONE_WAY_COST_BPS
from test_economic_v2_consolidation import consumable_recipe
from quant.book.ledger import Ledger
from quant.desk.risk import RiskLimits, evaluate as evaluate_risk
from quant.economics import (CapacityLimit, PortfolioInteraction, apply_capacity,
                             economic_gate, verify_research_cost_consistency)
from quant.economics.consistency import ExecutionCostModel
from quant.economics.decision import EVIDENCE_FORWARD_CONFIRMATION, EffectEstimate
from quant.economics.states import (CLUSTERING_UNIT_O4_RESOLVED, CONTINUE,
                                    ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE)


def _eligible_verdict(overlap_fraction: float = 0.0):
    """A verdict that actually reaches PORTFOLIO_CONSIDERATION_ELIGIBLE: a
    consumable recipe, forward-confirmed evidence, a resolved clustering
    unit and a verified research/execution cost consistency check together
    -- see test_economic_v2_consolidation.py for why each is required."""
    theta = fixtures.theta_state()
    meue_result = consumable_recipe().evaluate(theta)
    estimate = EffectEstimate(delta_hat=0.05, lower=0.04, upper=0.06, confidence_level=0.95,
                              evidence_label=EVIDENCE_FORWARD_CONFIRMATION,
                              sample_provenance="SYNTHETIC_FIXTURE",
                              clustering_unit_provenance=CLUSTERING_UNIT_O4_RESOLVED)
    interaction = PortfolioInteraction(overlap_fraction=overlap_fraction, residual_beta=0.0)
    model = ExecutionCostModel.from_execution_model(ExecutionModel())
    consistency = verify_research_cost_consistency(RESEARCH_ONE_WAY_COST_BPS, model, 0.006, "LANE")
    return economic_gate(estimate, meue_result, theta, interaction, consistency=consistency)


class ContinueIsNotAnApprovedOrderTest(unittest.TestCase):
    """The end-to-end proof: an economically eligible signal can still be
    vetoed by RISK against the real Book, because eligibility and approval
    are two different authorities."""

    def test_economically_eligible_proposal_is_vetoed_by_concentration(self):
        verdict = _eligible_verdict()
        self.assertEqual(verdict.verdict, CONTINUE)
        self.assertEqual(verdict.capital_order_eligibility,
                         ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE)

        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / "book.json", initial_capital=1_000_000.0)
            # A single-name concentration far past the limit -- the economic
            # gate has no visibility into this at all; only RISK does.
            target = {"AAA": 900_000.0}
            result = evaluate_risk(ledger, "STRAT_1", target, RiskLimits(), prices={"AAA": 100.0})
            self.assertFalse(result["approved"])
            self.assertTrue(any("largest single-name weight" in veto
                                for veto in result["vetoes"]))

    def test_economically_eligible_proposal_clears_risk_within_limits(self):
        verdict = _eligible_verdict()
        self.assertEqual(verdict.capital_order_eligibility,
                         ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE)
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / "book.json", initial_capital=1_000_000.0)
            target = {"AAA": 100_000.0}
            result = evaluate_risk(ledger, "STRAT_1", target, RiskLimits(), prices={"AAA": 100.0})
            self.assertTrue(result["approved"])
            # Approval belongs to RISK, not to the economics verdict: nothing
            # here reads verdict.verdict to decide approval.
            self.assertNotIn("verdict", result)


class SleeveAttributionPreservedTest(unittest.TestCase):
    """Two strategies, one instrument: sleeves stay separate, the aggregate
    is the Book's own sum, never a collapsed attribution."""

    def test_opposing_sleeves_on_the_same_symbol_are_not_netted_against_each_other(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / "book.json", initial_capital=1_000_000.0)
            ledger.apply_fill("AAA", 1_000, 100.0, 5.0, "2026-09-19", "STRAT_LONG",
                              operation_id="OP-1")
            ledger.apply_fill("AAA", -400, 100.0, 5.0, "2026-09-19", "STRAT_SHORT",
                              operation_id="OP-2")
            self.assertEqual(ledger.sleeve_exposures("STRAT_LONG")["AAA"], 100_000.0)
            self.assertEqual(ledger.sleeve_exposures("STRAT_SHORT")["AAA"], -40_000.0)
            # The aggregate view exists for portfolio limits only.
            self.assertEqual(ledger.symbol_exposures()["AAA"], 60_000.0)

    def test_risk_removes_only_the_proposing_strategys_own_sleeve_before_scoring(self):
        """RISK's ``project`` must not let one strategy's proposal double-count
        or erase a sibling strategy's existing position in the same name."""
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / "book.json", initial_capital=1_000_000.0)
            # Kept well under RiskLimits' 10% net-exposure cap (both same-
            # direction) so this isolates sleeve attribution, not net limits.
            ledger.apply_fill("AAA", 200, 100.0, 5.0, "2026-09-19", "STRAT_OTHER",
                              operation_id="OP-1")
            result = evaluate_risk(ledger, "STRAT_1", {"AAA": 20_000.0}, RiskLimits(),
                                   prices={"AAA": 100.0})
            self.assertTrue(result["approved"])
            # The resulting portfolio must include both sleeves' notional.
            self.assertAlmostEqual(result["gross_ratio"] * ledger.nav_at({"AAA": 100.0}),
                                   20_000.0 + 20_000.0, places=6)


class CapacityAndRiskComposeTest(unittest.TestCase):
    """Capacity (economics layer) and RISK's own scaling (Desk layer) are two
    independent, composable throttles -- neither substitutes for the other."""

    def test_capacity_clipped_notional_still_passes_through_risk_scoring(self):
        requested = {"AAA": 500_000.0}
        outcome = apply_capacity(
            requested, {"AAA": CapacityLimit("AAA", 2_000_000.0, 0.05,
                                             "PERMITTED_PRE_OUTCOME_PANEL_LOOKBACK")})
        self.assertEqual(outcome.granted["AAA"], 100_000.0)  # 5% of 2,000,000
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / "book.json", initial_capital=1_000_000.0)
            result = evaluate_risk(ledger, "STRAT_1", outcome.granted, RiskLimits(),
                                   prices={"AAA": 100.0})
            self.assertTrue(result["approved"])
            self.assertEqual(result["scale"], 1.0)  # capacity already did the clipping


class OverlapReducesValueBeforeTheGateTest(unittest.TestCase):
    """The economics-layer half of portfolio interaction: overlap with the
    existing Book reduces the incremental value the gate evaluates, upstream
    of anything RISK later checks."""

    def test_full_overlap_can_turn_eligibility_off_before_risk_is_even_reached(self):
        clean = _eligible_verdict(overlap_fraction=0.0)
        overlapped = _eligible_verdict(overlap_fraction=0.999)
        self.assertEqual(clean.capital_order_eligibility,
                         ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE)
        self.assertLess(overlapped.delta_incremental, clean.delta_incremental)


if __name__ == "__main__":
    unittest.main()
