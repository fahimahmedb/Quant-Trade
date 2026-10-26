"""Additional malformed-market-data regressions from the independent V1 review."""

import unittest

from quant.dataplane.panel import PricePanel
from quant.dataplane.validation import validate_panel

from test_quant_system import UNIVERSE, fixture_panel


class MarketBarIntegrityTests(unittest.TestCase):
    def test_invalid_session_date_is_not_accepted_as_market_time(self):
        panel = fixture_panel(sessions=300)
        rows = [{"date": date, "symbol": symbol, **bar}
                for (date, symbol), bar in panel.bars.items()]
        rows[0]["date"] = "2025-99-99"
        verdict = validate_panel(PricePanel(rows), UNIVERSE)
        self.assertFalse(verdict["passed"])
        self.assertTrue(any("invalid ISO session dates" in problem
                            for problem in verdict["problems"]))

    def test_open_outside_daily_range_is_rejected(self):
        panel = fixture_panel(sessions=300)
        rows = [{"date": date, "symbol": symbol, **bar}
                for (date, symbol), bar in panel.bars.items()]
        rows[10]["open"] = rows[10]["high"] * 2.0
        verdict = validate_panel(PricePanel(rows), UNIVERSE)
        self.assertFalse(verdict["passed"])
        self.assertTrue(any("impossible OHLC bars" in problem
                            for problem in verdict["problems"]))


if __name__ == "__main__":
    unittest.main()
