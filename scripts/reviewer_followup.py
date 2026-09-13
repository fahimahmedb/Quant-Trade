"""One-shot follow-up patch for independently reproduced V1 invariants."""
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"{path}: expected one match, got {text.count(old)}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


# The causal regression compares decision content, not wall-clock timestamps.
replace_once(
    "tests/test_v1_red_team.py",
    '''                ticket = summary["tickets"][0]\n                tickets.append((ticket["status"], ticket["stage"], ticket["stage_trace"]))\n                size = next((entry for entry in ticket["stage_trace"]\n''',
    '''                ticket = summary["tickets"][0]\n                stable_trace = [{key: value for key, value in entry.items() if key != "at"}\n                                for entry in ticket["stage_trace"]]\n                tickets.append((ticket["status"], ticket["stage"], stable_trace))\n                size = next((entry for entry in ticket["stage_trace"]\n''')

# A same-session mark is a restatement, so a superseded high mark cannot remain
# as a phantom peak and distort every later drawdown/risk decision.
replace_once(
    "src/quant/book/ledger.py",
    '''        self.state.last_session_date = date\n        self.state.peak_nav = max(self.state.peak_nav, nav)\n        point = {"date": date, "nav": nav, "cash": self.state.cash,\n''',
    '''        self.state.last_session_date = date\n        point = {"date": date, "nav": nav, "cash": self.state.cash,\n''')
replace_once(
    "src/quant/book/ledger.py",
    '''        else:\n            self.state.sessions += 1\n            self.state.nav_history.append(point)\n        self.save()\n        return point\n''',
    '''        else:\n            self.state.sessions += 1\n            self.state.nav_history.append(point)\n        self.state.peak_nav = max(\n            [self.state.initial_capital]\n            + [float(item["nav"]) for item in self.state.nav_history])\n        self.save()\n        return point\n''')

# Add durable adversarial proofs for the independently found phantom-peak defect
# and for multi-strategy decision-time isolation within one session.
replace_once(
    "tests/test_v1_red_team.py",
    '''class LearningRefreshTests(unittest.TestCase):\n''',
    '''class LedgerRestatementTests(unittest.TestCase):\n    def test_same_session_restatement_cannot_leave_a_phantom_peak(self):\n        with tempfile.TemporaryDirectory() as directory:\n            ledger = Ledger(Path(directory) / "book.json", initial_capital=100.0)\n            ledger.apply_fill("AAA", 1.0, 10.0, 0.0, "2025-01-01", "S", "fill")\n            ledger.mark_to_market("2025-01-01", {"AAA": 30.0})\n            self.assertEqual(ledger.state.peak_nav, 120.0)\n            ledger.mark_to_market("2025-01-01", {"AAA": 10.0})\n            self.assertEqual(ledger.state.nav_history[-1]["nav"], 100.0)\n            self.assertEqual(ledger.state.peak_nav, 100.0)\n            self.assertAlmostEqual(ledger.drawdown, 0.0)\n\n\nclass MultiStrategyDecisionBoundaryTests(unittest.TestCase):\n    def test_later_strategy_cannot_see_an_earlier_strategy_open_fill(self):\n        panel = fixture_panel(sessions=320)\n        dates = panel.aligned_dates(UNIVERSE)\n        decision_date, next_date = dates[80], dates[81]\n        with tempfile.TemporaryDirectory() as directory:\n            desk = shadow_desk(Path(directory), panel, holding_days=1, no_trade_band=0.0)\n            second = StrategyDefinition("STR-SECOND", 1, "test", fixture_spec(\n                holding_days=1, no_trade_band=0.0).to_dict())\n            second.transition("VALIDATED", "test fixture")\n            second.transition("SHADOW", "test fixture")\n            desk.strategies.upsert(second)\n\n            from quant.desk import desk as desk_module\n            original = desk_module.evaluate_risk\n            seen = {}\n\n            def checking(ledger, strategy_id, target_notional, limits, prices=None):\n                seen[strategy_id] = {\n                    "nav": ledger.nav_at(prices or {}),\n                    "exposures": ledger.symbol_exposures_at(prices or {})}\n                return original(ledger, strategy_id, target_notional, limits, prices)\n\n            target = {"AAA": 0.20, "BBB": -0.20}\n            with patch("quant.desk.desk.weights_for", return_value=target), \\\n                    patch("quant.desk.desk.evaluate_risk", side_effect=checking):\n                summary = desk.run_session(panel, decision_date, next_date)\n\n            self.assertEqual(len(seen), 2)\n            states = list(seen.values())\n            self.assertAlmostEqual(states[0]["nav"], states[1]["nav"], places=8)\n            self.assertEqual(states[0]["exposures"], states[1]["exposures"],\n                             "strategy ordering leaked open(t+1) state into a later decision")\n            self.assertTrue(any(ticket["status"] == "BOOKED" for ticket in summary["tickets"]))\n\n\nclass LearningRefreshTests(unittest.TestCase):\n''')
