"""Calendar-flow sleeves: NYSE calendar, overnight-leg index, causality, explicit exits.

Synthetic panels here are test fixtures, never evidence.
"""

from __future__ import annotations

import unittest
from datetime import date

from quant.dataplane.calendar_legs import (build_calendar_panel, calendar_features,
                                           is_session, next_sessions, nyse_holidays,
                                           sessions_left_in_month)
from quant.dataplane.panel import PricePanel, Window
from quant.factory.evaluate import walk_forward
from quant.factory.lanes import (CALENDAR_DATASET, CALENDAR_PRIOR_TRIALS, baseline_spec,
                                 lane_definitions)
from quant.factory.signals import (FOMC_BASELINE, MONTH_END, MONTH_END_BASELINE, weights_for)


def _panel(days: list[str], moves: dict[str, list[tuple[float, float]]]) -> PricePanel:
    rows = []
    for symbol, pairs in moves.items():
        for day, (open_, close) in zip(days, pairs):
            rows.append({"date": day, "symbol": symbol, "open": open_, "high": max(open_, close),
                         "low": min(open_, close), "close": close, "adj_close": close,
                         "volume": 1e6})
    return PricePanel(rows)


class NyseCalendarTests(unittest.TestCase):
    def test_known_holidays_and_rules(self):
        self.assertIn(date(2024, 3, 29), nyse_holidays(2024))      # Good Friday
        self.assertIn(date(2022, 6, 20), nyse_holidays(2022))      # Juneteenth observed
        self.assertNotIn(date(2021, 6, 18), nyse_holidays(2021))   # before Juneteenth
        self.assertNotIn(date(2021, 12, 31), nyse_holidays(2022))  # Sat New Year not moved
        self.assertIn(date(2025, 1, 9), nyse_holidays(2025))       # day of mourning
        self.assertFalse(is_session(date(2026, 11, 26)))           # Thanksgiving
        self.assertEqual(next_sessions("2026-07-02", 2), ["2026-07-06", "2026-07-07"])

    def test_month_end_count(self):
        self.assertEqual(sessions_left_in_month("2026-09-28"), 2)  # 29, 30 remain
        self.assertEqual(sessions_left_in_month("2026-09-30"), 0)


class OvernightLegTests(unittest.TestCase):
    def test_holding_the_leg_open_to_open_earns_close_to_open(self):
        days = ["2026-01-05", "2026-01-06", "2026-01-07"]
        source = _panel(days, {"SPY": [(100, 102), (103, 101), (99, 105)],
                               "TLT": [(50, 50), (50, 50), (50, 50)]})
        panel, _ = build_calendar_panel(source, ["SPY", "TLT"], [])
        on = [panel.price(day, "SPY_ON") for day in days]
        self.assertAlmostEqual(on[1] / on[0], 103 / 102)          # close(5) -> open(6)
        self.assertAlmostEqual(on[2] / on[1], 99 / 101)
        for day in days:                                            # flat intraday
            bar = panel.bars[(day, "SPY_ON")]
            self.assertEqual(bar["open"], bar["close"])


class CalendarSignalTests(unittest.TestCase):
    def setUp(self):
        # every weekday session of September-October 2026, gently rising SPY
        day, days = date(2026, 9, 1), []
        while day <= date(2026, 10, 30):
            if is_session(day):
                days.append(day.isoformat())
            day = date.fromordinal(day.toordinal() + 1)
        self.days = days
        spy = [(100 + i * 0.1, 100 + i * 0.1 + 0.05) for i in range(len(days))]
        tlt = [(50 + (i % 3) * 0.01, 50 + (i % 3) * 0.01) for i in range(len(days))]
        source = _panel(days, {"SPY": spy, "TLT": tlt})
        self.fomc = ["2026-09-16", "2026-10-28"]
        self.panel, _ = build_calendar_panel(source, ["SPY", "TLT"], self.fomc)
        lanes = lane_definitions(["SPY", "TLT", "SPY_ON"], CALENDAR_DATASET)
        self.fomc_spec = lanes["calendar_fomc_overnight"]["grid"][0]
        self.month_spec = lanes["calendar_month_end_rebalance"]["grid"][0]
        self.assertEqual(lanes["calendar_fomc_overnight"]["prior_trials"], CALENDAR_PRIOR_TRIALS)

    def test_fomc_position_is_exactly_the_night_before_the_decision(self):
        held = {day for day in self.days[:-2]
                if weights_for(self.panel, self.fomc_spec, day).get("SPY_ON")}
        # decide two sessions ahead: 09-14 -> MOC 09-15 -> MOO 09-16
        self.assertEqual(held, {"2026-09-14", "2026-10-26"})
        self.assertEqual(weights_for(self.panel, self.fomc_spec, "2026-09-15"), {"SPY_ON": 0.0})

    def test_features_do_not_need_future_rows(self):
        cut = self.panel.restrict(end="2026-09-14")
        self.assertEqual(weights_for(cut, self.fomc_spec, "2026-09-14"), {"SPY_ON": 1.0})
        self.assertEqual(calendar_features("2026-09-14", self.fomc)["fomc_in_sessions"], 2.0)

    def test_month_end_leans_against_the_winner_and_exits_on_schedule(self):
        # September has no prior month-end close in the fixture: no signal, flat
        self.assertEqual(weights_for(self.panel, self.month_spec, "2026-09-28"), {"SPY": 0.0})
        decision = "2026-10-28"                           # two sessions left (29, 30)
        weight = weights_for(self.panel, self.month_spec, decision)["SPY"]
        self.assertEqual(weight, -1.0)                    # SPY beat TLT month to date
        self.assertEqual(weights_for(self.panel, self.month_spec, "2026-10-29"), {"SPY": 0.0})
        baseline = baseline_spec(self.month_spec)
        self.assertEqual(baseline.family, MONTH_END_BASELINE)
        self.assertEqual(weights_for(self.panel, baseline, decision), {"SPY": 1.0})
        self.assertEqual(baseline_spec(self.fomc_spec).family, FOMC_BASELINE)

    def test_walk_forward_holds_the_leg_for_one_interval_only(self):
        window = Window("W", self.days[0], self.days[-1])
        rows = walk_forward(self.panel, self.fomc_spec, window, 2.0)
        active = [row for row in rows if row["weights"].get("SPY_ON")]
        self.assertEqual([row["signal_date"] for row in active], ["2026-09-14", "2026-10-26"])
        entry = active[0]
        expected = (self.panel.price(entry["exit_date"], "SPY_ON")
                    / self.panel.price(entry["entry_date"], "SPY_ON") - 1.0)
        self.assertAlmostEqual(entry["gross_return"], expected)
        self.assertEqual(MONTH_END, self.month_spec.family)


if __name__ == "__main__":
    unittest.main()


class MonthEndCoverageTests(unittest.TestCase):
    """Red-team finding: zero-drift flat targets reset the holding clock and
    silently skipped months in research while the Desk traded every month."""

    def test_every_month_with_a_prior_close_trades_in_research(self):
        import random
        rng = random.Random(4)
        day, days = date(2025, 1, 1), []
        while day <= date(2025, 12, 31):
            if is_session(day):
                days.append(day.isoformat())
            day = date.fromordinal(day.toordinal() + 1)
        spy, tlt, level, bond = [], [], 100.0, 50.0
        for _ in days:
            level *= 1 + rng.gauss(0, 0.01)
            bond *= 1 + rng.gauss(0, 0.005)
            spy.append((level, level))
            tlt.append((bond, bond))
        panel, _ = build_calendar_panel(_panel(days, {"SPY": spy, "TLT": tlt}), ["SPY", "TLT"], [])
        spec = lane_definitions(["SPY", "TLT", "SPY_ON"], CALENDAR_DATASET)[
            "calendar_month_end_rebalance"]["grid"][0]
        rows = walk_forward(panel, spec, Window("W", days[0], days[-1]), 2.0)
        entries = {row["signal_date"][:7] for row in rows if row["turnover"] > 0
                   and any(abs(w) > 0 for w in row["weights"].values())}
        # January has no prior month-end close in the fixture; every other month
        # (February..December) must trade.
        self.assertEqual(len(entries), 11)
        active = sum(1 for row in rows if row["positions"] > 0)
        self.assertLess(active, 40)                       # flat days are not "active"
