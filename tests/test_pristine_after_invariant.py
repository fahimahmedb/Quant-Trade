"""Invariant 6: forward evidence must postdate the rule that trades on it.

Red-team HIGH (2026-09-27): the calendar lanes were first committed on
2026-09-25 but declared ``pristine_after = 2026-09-11``, so the 2026-09-16
FOMC trade counted as prospective evidence. These tests fail if any lane's
``pristine_after`` precedes its declaration date or its first commit.
"""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

from quant.factory.lanes import (CALENDAR_DATASET, FUTURES_BROAD_DATASET, FUTURES_DATASET,
                                 LANE_DECLARED_ON, PERP_DATASET, PERP_DYDX_DATASET,
                                 declared_pristine_after, lane_definitions)

ROOT = Path(__file__).resolve().parents[1]
DATASETS = [CALENDAR_DATASET, FUTURES_DATASET, FUTURES_BROAD_DATASET, PERP_DATASET,
            PERP_DYDX_DATASET, "us_sector_etf_daily"]


def _all_lanes():
    for dataset in DATASETS:
        for name, definition in lane_definitions([], dataset).items():
            yield dataset, name, definition


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                              text=True, timeout=60).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


class PristineAfterInvariantTests(unittest.TestCase):
    def test_every_lane_is_declared_and_gated_no_earlier_than_its_declaration(self):
        seen = set()
        for _, name, definition in _all_lanes():
            seen.add(name)
            self.assertIn(name, LANE_DECLARED_ON)
            self.assertTrue(definition.get("pristine_after"), name)
            self.assertGreaterEqual(definition["pristine_after"], LANE_DECLARED_ON[name], name)
        self.assertEqual(seen, set(LANE_DECLARED_ON))

    def test_pristine_after_never_precedes_the_lanes_first_commit(self):
        if _git("rev-parse", "--is-shallow-repository") != "false":
            self.skipTest("shallow clone: first-commit dates are only upper bounds")
        for _, name, definition in _all_lanes():
            dates = _git("log", "--reverse", "--format=%cs", f"-S\"{name}\"", "--",
                         "src/quant/factory/lanes.py").splitlines()
            if dates:
                self.assertGreaterEqual(definition["pristine_after"], dates[0], name)

    def test_calendar_lanes_exclude_the_2026_09_16_fomc_event(self):
        for name, definition in lane_definitions([], CALENDAR_DATASET).items():
            self.assertGreater(definition["pristine_after"], "2026-09-16", name)

    def test_registered_strategies_are_rebound_to_the_corrected_date(self):
        # A strategy persisted with the old (earlier) date must pick up the new one.
        self.assertEqual(declared_pristine_after(
            CALENDAR_DATASET, "STR-CALENDAR-FOMC-OVERNIGHT-calendar_fomc_overnight_x1_h1"),
            "2026-09-25")
        self.assertIsNone(declared_pristine_after(CALENDAR_DATASET, "STR-UNKNOWN-x"))


if __name__ == "__main__":
    unittest.main()
