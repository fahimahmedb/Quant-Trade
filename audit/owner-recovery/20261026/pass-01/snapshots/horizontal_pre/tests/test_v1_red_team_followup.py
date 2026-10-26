"""Final adversarial regressions found during the independent V1 review."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quant.book.ledger import Ledger
from quant.factory.strategies import StrategyDefinition

from test_quant_system import UNIVERSE, fixture_panel, fixture_spec, shadow_desk


class LedgerRestatementTests(unittest.TestCase):
    def test_same_session_restatement_cannot_leave_a_phantom_peak(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / "book.json", initial_capital=100.0)
            ledger.apply_fill("AAA", 1.0, 10.0, 0.0, "2025-01-01", "S", "fill")
            ledger.mark_to_market("2025-01-01", {"AAA": 30.0})
            self.assertEqual(ledger.state.peak_nav, 120.0)

            # A repeated mark is a restatement of the same economic session,
            # not a second observation. The superseded 120 NAV must therefore
            # disappear from the drawdown baseline as well as nav_history.
            ledger.mark_to_market("2025-01-01", {"AAA": 10.0})
            self.assertEqual(ledger.state.nav_history[-1]["nav"], 100.0)
            self.assertEqual(ledger.state.peak_nav, 100.0)
            self.assertAlmostEqual(ledger.drawdown, 0.0)


class MultiStrategyDecisionBoundaryTests(unittest.TestCase):
    def test_later_strategy_cannot_see_an_earlier_strategy_next_open_fill(self):
        panel = fixture_panel(sessions=320)
        dates = panel.aligned_dates(UNIVERSE)
        decision_date, next_date = dates[80], dates[81]

        with tempfile.TemporaryDirectory() as directory:
            desk = shadow_desk(Path(directory), panel, holding_days=1, no_trade_band=0.0)
            second = StrategyDefinition(
                "STR-SECOND", 1, "test",
                fixture_spec(holding_days=1, no_trade_band=0.0).to_dict())
            second.transition("VALIDATED", "test fixture")
            second.transition("SHADOW", "test fixture")
            desk.strategies.upsert(second)

            from quant.desk import desk as desk_module
            original = desk_module.evaluate_risk
            seen = {}

            def checking(ledger, strategy_id, target_notional, limits, prices=None):
                seen[strategy_id] = {
                    "nav": ledger.nav_at(prices or {}),
                    "exposures": ledger.symbol_exposures_at(prices or {}),
                }
                return original(ledger, strategy_id, target_notional, limits, prices)

            target = {"AAA": 0.20, "BBB": -0.20}
            with patch("quant.desk.desk.weights_for", return_value=target), \
                    patch("quant.desk.desk.evaluate_risk", side_effect=checking):
                summary = desk.run_session(panel, decision_date, next_date)

            self.assertEqual(set(seen), {"STR-TEST", "STR-SECOND"})
            states = list(seen.values())
            self.assertAlmostEqual(states[0]["nav"], states[1]["nav"], places=8)
            self.assertEqual(
                states[0]["exposures"], states[1]["exposures"],
                "strategy ordering leaked open(t+1) state into a close(t) decision")
            self.assertTrue(any(ticket["status"] == "BOOKED" for ticket in summary["tickets"]))


if __name__ == "__main__":
    unittest.main()
