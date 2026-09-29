"""Offline tests for H-011's niche-league extension of the H-001 planner.

All prices, teams-at-times, ids and keys below are INVENTED FIXTURES, not market data.
No network is used: fetchers are stubbed.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from quant.dataplane import h001_relay as R  # noqa: E402

NOW = datetime(2026, 10, 3, 22, 0, tzinfo=timezone.utc)


def niche_odds_payload(sport: str, kick: str):
    return [{"id": f"evt-{sport}", "sport_key": sport, "commence_time": kick,
             "home_team": "Home FC", "away_team": "Away FC",
             "bookmakers": [{"key": "pinnacle", "last_update": "2026-10-03T21:55:00Z",
                             "markets": [{"key": "h2h", "outcomes": [
                                 {"name": "Home FC", "price": 1.8},
                                 {"name": "Away FC", "price": 2.1}]}]}]}]


class NicheSportsConstants(unittest.TestCase):
    def test_niche_sports_are_the_ex_ante_list(self):
        self.assertEqual(R.NICHE_SPORTS,
                         ("soccer_korea_kleague1", "soccer_mexico_ligamx",
                          "americanfootball_ncaaf"))
        self.assertEqual(R.ALL_SPORTS, R.SPORTS + R.NICHE_SPORTS)

    def test_anchor_hours_by_sport_matches_the_mission(self):
        for sport in R.SPORTS:
            self.assertEqual(R.ANCHOR_HOURS_BY_SPORT[sport], R.ANCHOR_HOURS)
        for sport in R.NICHE_SPORTS:
            self.assertEqual(R.ANCHOR_HOURS_BY_SPORT[sport], 24.0)
        self.assertGreater(R.NICHE_ANCHOR_HOURS, R.ANCHOR_HOURS)

    def test_hard_caps_unchanged_by_niche_addition(self):
        # the mission requires every existing cap untouched
        self.assertEqual(R.MAX_PER_RUN, 2)
        self.assertEqual(R.DAILY_MAX, 14)
        self.assertEqual(R.MONTHLY_MAX, 430)
        self.assertEqual(R.REMAINING_FLOOR, 25)


class PerSportAnchor(unittest.TestCase):
    def test_niche_sport_not_yet_due_at_12h_but_h001_sport_is(self):
        """At 13h since last fetch: an H-001 sport (12h anchor) is due, a niche
        sport (24h anchor) is not, when both are offered together."""
        last = (NOW - timedelta(hours=13)).isoformat()
        ledger = [{"fetched_at": last, "sport": s, "status": "OK", "charged": True,
                  "remaining": 300} for s in R.ALL_SPORTS]
        plan, _ = R.plan_requests(NOW, ledger, [], R.ALL_SPORTS,
                                  anchor_hours=R.ANCHOR_HOURS_BY_SPORT)
        planned = {s for s, _ in plan}
        self.assertTrue(planned & set(R.SPORTS), "an H-001 sport should be due at 13h")
        self.assertFalse(planned & set(R.NICHE_SPORTS), "no niche sport is due before 24h")

    def test_niche_sport_due_at_25h(self):
        last = (NOW - timedelta(hours=25)).isoformat()
        ledger = [{"fetched_at": last, "sport": s, "status": "OK", "charged": True,
                  "remaining": 300} for s in R.ALL_SPORTS]
        plan, _ = R.plan_requests(NOW, ledger, [], R.ALL_SPORTS,
                                  anchor_hours=R.ANCHOR_HOURS_BY_SPORT, max_per_run=10)
        planned = {s for s, _ in plan}
        self.assertTrue(planned & set(R.NICHE_SPORTS))

    def test_bare_anchor_hours_float_still_works(self):
        """Backward compatibility: a plain float still applies to every sport."""
        plan, _ = R.plan_requests(NOW, [], [], R.SPORTS, anchor_hours=6.0)
        self.assertEqual({s for s, _ in plan}, set(R.SPORTS))

    def test_combined_five_sports_still_capped_at_max_per_run(self):
        """All 5 sports wanting a request at once is still capped at MAX_PER_RUN."""
        plan, _ = R.plan_requests(NOW, [], [], R.ALL_SPORTS,
                                  anchor_hours=R.ANCHOR_HOURS_BY_SPORT)
        self.assertLessEqual(len(plan), R.MAX_PER_RUN)
        # H-001 sports keep priority when the shared budget is scarce
        self.assertEqual([s for s, _ in plan], list(R.SPORTS))


class NicheSportDoesNotCrashTheRun(unittest.TestCase):
    """Regression: PM_TAG/KALSHI_SERIES only cover H-001's own sports; a niche
    sport with a 'live' event must degrade to unmatched, never raise KeyError
    and truncate the whole run (which would also lose that run's EPL/NBA data)."""

    def test_venue_quotes_does_not_raise_for_an_unwired_sport(self):
        event = {"event_id": "evt-x", "sport": "soccer_korea_kleague1",
                 "commence_time": (NOW + timedelta(hours=2)).isoformat(),
                 "home": "Ulsan", "away": "Jeonbuk"}
        records = list(R._venue_quotes("soccer_korea_kleague1", [event], NOW,
                                       NOW.isoformat(timespec="seconds"), lambda url: []))
        matches = {(key.split("|")[1]): record for _, key, record in records
                  if _ == "sports_quotes/matches.jsonl"}
        # "unreachable" is the same status a real network failure gets; the reason
        # tells the two apart, and neither raises.
        self.assertEqual(matches["POLYMARKET"]["status"], "unreachable")
        self.assertIn("not wired", matches["POLYMARKET"]["reason"])
        self.assertEqual(matches["KALSHI"]["status"], "unreachable")
        self.assertIn("not wired", matches["KALSHI"]["reason"])

    def test_full_collect_with_all_sports_does_not_crash(self):
        kick = (NOW + timedelta(hours=1)).isoformat().replace("+00:00", "Z")

        class Stub:
            def fetch(self, url):
                for sport in R.ALL_SPORTS:
                    if f"/{sport}/odds" in url:
                        payload = niche_odds_payload(sport, kick)
                        return payload, {"x-requests-remaining": "300", "x-requests-used": "5",
                                        "x-requests-last": "1"}
                raise AssertionError(f"unexpected url {url}")

            def get(self, url):
                return [] if "gamma-api" in url else {"markets": []}

        stub = Stub()
        with tempfile.TemporaryDirectory() as tmp:
            items = list(R.collect(Path(tmp), NOW, key="FIXTURE-KEY", fetch=stub.fetch,
                                   get=stub.get, sports=R.ALL_SPORTS,
                                   anchor_hours=R.ANCHOR_HOURS_BY_SPORT))
        # H-001 sports win the shared 2/run budget; niche sports still degrade cleanly
        # rather than raising, whenever they do get a turn.
        self.assertTrue(any(s.startswith("odds/pinnacle") for s, _, _ in items))


if __name__ == "__main__":
    unittest.main()
