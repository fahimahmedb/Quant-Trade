"""Offline tests for the fast-rail H-001 collector and CLV.

All prices, teams-at-times, ids and keys below are INVENTED FIXTURES, not market data.
No network is used: fetchers are stubbed.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from quant.dataplane import h001_relay as R  # noqa: E402
from quant.dataplane.adapters import DataUnavailable  # noqa: E402
from research.fast_rail.h001 import clv as C  # noqa: E402
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("fetch_feeds", ROOT / "scripts" / "fetch_feeds.py")
fetch_feeds = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fetch_feeds)

SECRET = "FIXTURE-SECRET-KEY-123"
NOW = datetime(2026, 10, 3, 22, 0, tzinfo=timezone.utc)
KICK = "2026-10-03T23:00:00Z"


def odds_payload(kick=KICK, home="Toronto Raptors", away="Miami Heat", prices=(1.8, 2.1)):
    return [{"id": "evtA", "sport_key": "basketball_nba", "commence_time": kick,
             "home_team": home, "away_team": away,
             "bookmakers": [{"key": "pinnacle", "last_update": "2026-10-03T21:55:00Z",
                             "markets": [{"key": "h2h", "outcomes": [
                                 {"name": home, "price": prices[0]},
                                 {"name": away, "price": prices[1]}]}]}]}]


PM_EVENTS = [{"slug": "nba-mia-tor-2026-10-03", "startTime": "2026-10-03T23:00:00Z",
              "markets": [{"sportsMarketType": "moneyline", "conditionId": "0xc",
                           "outcomes": '["Heat", "Raptors"]', "clobTokenIds": '["tH", "tR"]',
                           "gameStartTime": "2026-10-03 23:00:00+00"}]}]
KALSHI = {"markets": [
    {"ticker": "KXNBAGAME-26OCT03MIATOR-MIA", "event_ticker": "KXNBAGAME-26OCT03MIATOR",
     "yes_bid_dollars": "0.40", "yes_ask_dollars": "0.42"},
    {"ticker": "KXNBAGAME-26OCT03MIATOR-TOR", "event_ticker": "KXNBAGAME-26OCT03MIATOR",
     "yes_bid_dollars": "0.56", "yes_ask_dollars": "0.58"}]}
BOOK = {"bids": [{"price": "0.50", "size": "100"}], "asks": [{"price": "0.52", "size": "80"}]}


class Stub:
    def __init__(self, remaining=400, last=1, status=None):
        self.calls, self.remaining, self.last, self.status = [], remaining, last, status

    def fetch(self, url):
        self.calls.append(url)
        headers = {"x-requests-remaining": str(self.remaining), "x-requests-used": "5",
                   "x-requests-last": str(self.last)}
        if self.status:
            raise R.OddsHTTPError(f"{url.split('?')[0]}: HTTP {self.status}", headers)
        return odds_payload(), headers

    def get(self, url):
        self.calls.append(url)
        if "gamma-api" in url:
            return PM_EVENTS
        if "kalshi" in url:
            return KALSHI
        return BOOK


def run_collect(out, now=NOW, stub=None):
    stub = stub or Stub()
    return list(R.collect(out, now, key=SECRET, fetch=stub.fetch, get=stub.get)), stub


def store(out, items, stamp):
    streams = {}
    for stream, key, record in items:
        streams.setdefault(stream, fetch_feeds.Stream(out / stream)).add(key, record, stamp)


class KeyNeverStored(unittest.TestCase):
    def test_strip_key(self):
        url = R.ODDS_URL.format(sport="soccer_epl", key=SECRET)
        self.assertNotIn(SECRET, R.strip_key(url))
        self.assertIn("bookmakers=pinnacle", R.strip_key(url))

    def test_full_run_writes_no_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            items, _ = run_collect(out)
            store(out, items, NOW.isoformat(timespec="seconds"))
            blob = "".join(p.read_text() for p in out.rglob("*.jsonl"))
            self.assertTrue(blob)
            self.assertNotIn(SECRET, blob)
            self.assertNotIn("apiKey", blob)

    def test_error_message_has_no_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            items, _ = run_collect(Path(tmp), stub=Stub(status=401))
            self.assertNotIn(SECRET, json.dumps(items))

    def test_no_key_no_request(self):
        stub = Stub()
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(DataUnavailable):
            list(R.collect(Path(tmp), NOW, key="", fetch=stub.fetch, get=stub.get))
        self.assertEqual(stub.calls, [])


class BudgetGuard(unittest.TestCase):
    def ledger(self, n, day="2026-10-03", remaining=300):
        return [{"fetched_at": f"{day}T{h:02d}:00:00+00:00", "sport": "soccer_epl",
                 "charged": True, "remaining": remaining} for h in range(n)]

    def test_first_run_anchors_both_sports(self):
        plan, _ = R.plan_requests(NOW, [], [])
        self.assertEqual([s for s, _ in plan], list(R.SPORTS))

    def test_daily_cap(self):
        plan, info = R.plan_requests(NOW, self.ledger(R.DAILY_MAX), [])
        self.assertEqual(plan, [])
        plan, _ = R.plan_requests(NOW, self.ledger(R.DAILY_MAX - 1), [])
        self.assertEqual(len(plan), 1)

    def test_remaining_floor(self):
        plan, info = R.plan_requests(NOW, self.ledger(1, remaining=R.REMAINING_FLOOR), [])
        self.assertEqual(plan, [])
        self.assertIn("floor", info["blocked"])
        plan, _ = R.plan_requests(NOW, self.ledger(1, remaining=R.REMAINING_FLOOR + 1), [])
        self.assertEqual(len(plan), 1)

    def test_monthly_cap(self):
        old = [{"fetched_at": f"2026-10-0{1 + i % 2}T00:00:00+00:00", "sport": "x",
                "charged": True, "remaining": 300} for i in range(R.MONTHLY_MAX)]
        plan, _ = R.plan_requests(NOW, old, [], daily_max=10 ** 6)
        self.assertEqual(plan, [])

    def test_recent_snapshot_no_request_but_closing_window_requests(self):
        snaps = [{"sport": "basketball_nba", "observed_at": "2026-10-03T20:00:00+00:00",
                  "commence_time": KICK},
                 {"sport": "soccer_epl", "observed_at": "2026-10-03T20:00:00+00:00",
                  "commence_time": "2026-10-04T14:00:00Z"}]
        plan, _ = R.plan_requests(datetime(2026, 10, 3, 21, 0, tzinfo=timezone.utc), [], snaps)
        self.assertEqual(plan, [])                        # 2h before tip: wait
        plan, _ = R.plan_requests(NOW, [], snaps)          # 60 min before tip
        self.assertEqual(plan, [("basketball_nba", f"closing:{R.parse_time(KICK).isoformat()}")])
        snaps.append({"sport": "basketball_nba", "observed_at": "2026-10-03T22:10:00+00:00",
                      "commence_time": KICK})
        plan, _ = R.plan_requests(datetime(2026, 10, 3, 22, 20, tzinfo=timezone.utc), [], snaps)
        self.assertEqual(plan, [])                        # closing already captured

    def test_collect_respects_budget_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            items, stub = run_collect(out)
            store(out, items, NOW.isoformat(timespec="seconds"))
            odds_calls = [u for u in stub.calls if "the-odds-api" in u]
            self.assertEqual(len(odds_calls), 2)
            later = datetime(2026, 10, 3, 22, 30, tzinfo=timezone.utc)
            items, stub = run_collect(out, later)          # snapshot at 22:00 covers the tip
            self.assertEqual([u for u in stub.calls if "the-odds-api" in u], [])

    def test_empty_sport_does_not_reanchor_every_run(self):
        """Off-season: a sport with no events still counts as fetched (ledger)."""
        ledger = [{"fetched_at": "2026-10-03T21:00:00+00:00", "sport": s, "status": "OK",
                   "charged": True, "remaining": 300} for s in R.SPORTS]
        plan, _ = R.plan_requests(NOW, ledger, [])
        self.assertEqual(plan, [])


class SharedObservedAtAndMatching(unittest.TestCase):
    def test_same_run_quotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            items, _ = run_collect(Path(tmp))
        streams = {s.split("/")[0] + "/" + s.split("/")[1] for s, _, _ in items}
        self.assertIn("sports_quotes/polymarket.jsonl", streams)
        self.assertIn("sports_quotes/kalshi.jsonl", streams)
        stamp = NOW.isoformat(timespec="seconds")
        keyed = [k for s, k, _ in items if s.startswith(("sports_quotes/polymarket",
                                                          "sports_quotes/kalshi",
                                                          "odds/pinnacle"))]
        self.assertTrue(all(k.startswith(stamp + "|") for k in keyed))
        pm = [r for s, _, r in items if s.startswith("sports_quotes/polymarket")]
        self.assertEqual({r["outcome"] for r in pm}, {"Toronto Raptors", "Miami Heat"})
        self.assertEqual({r["token_id"] for r in pm if r["outcome"] == "Miami Heat"}, {"tH"})
        kal = {r["outcome"]: r["best_ask"] for s, _, r in items
               if s.startswith("sports_quotes/kalshi")}
        self.assertEqual(kal, {"Miami Heat": 0.42, "Toronto Raptors": 0.58})
        pin = [r for s, _, r in items if s.startswith("odds/pinnacle")]
        self.assertEqual(pin[0]["snapshot_to_kickoff_min"], 60.0)

    def test_unknown_team_is_not_fuzzy_matched(self):
        event = {"sport": "basketball_nba", "home": "Toronto Raptorz", "away": "Miami Heat",
                 "commence_time": KICK}
        mapped, info = R.match_polymarket(event, PM_EVENTS)
        self.assertEqual(mapped, {})
        self.assertEqual(info["reason"], "team not in table")

    def test_kickoff_skew_rejects_other_fixture(self):
        event = {"sport": "basketball_nba", "home": "Toronto Raptors", "away": "Miami Heat",
                 "commence_time": "2026-10-05T23:00:00Z"}
        self.assertEqual(R.match_polymarket(event, PM_EVENTS)[0], {})
        self.assertEqual(R.match_kalshi(event, KALSHI["markets"])[0], {})


def pin(observed, prices, kick=KICK):
    return {"event_id": "evtA", "commence_time": kick, "observed_at": observed,
            "prices": prices}


def quote(observed, outcome, ask, venue="POLYMARKET"):
    return {"odds_event_id": "evtA", "observed_at": observed, "outcome": outcome,
            "best_ask": ask, "venue": venue}


class CLV(unittest.TestCase):
    P1 = {"Home": 1.80, "Away": 2.10}          # fair(Home) ~ 0.53
    PCLOSE = {"Home": 1.60, "Away": 2.50}      # line moved toward Home ~ 0.60

    def test_closing_is_last_pre_kickoff_only(self):
        rows = [pin("2026-10-03T12:00:00+00:00", self.P1),
                pin("2026-10-03T22:30:00+00:00", self.PCLOSE),
                pin("2026-10-03T23:00:00+00:00", {"Home": 1.1, "Away": 8.0}),   # at kickoff
                pin("2026-10-03T23:40:00+00:00", {"Home": 1.01, "Away": 30.0})]  # in-play
        close = C.closing_snapshot(rows, "evtA")
        self.assertEqual(close["observed_at"], "2026-10-03T22:30:00+00:00")
        self.assertEqual(close["closing_lag_min"], 30.0)
        self.assertFalse(close["closing_stale"])

    def test_stale_closing_flagged(self):
        close = C.closing_snapshot([pin("2026-10-03T12:00:00+00:00", self.P1)], "evtA")
        self.assertTrue(close["closing_stale"])

    def test_clv_sign(self):
        rows = [pin("2026-10-03T12:00:00+00:00", self.P1),
                pin("2026-10-03T22:30:00+00:00", self.PCLOSE)]
        quotes = [quote("2026-10-03T12:00:00+00:00", "Home", 0.45),
                  quote("2026-10-03T12:00:00+00:00", "Away", 0.30)]
        out = C.evaluate(rows, quotes, results={"evtA": "Away"})
        bets = {b["outcome"]: b for b in out["bets"]}
        self.assertGreater(bets["Home"]["clv_return"], 0)     # bought below closing fair
        self.assertGreater(bets["Home"]["edge_at_entry"], 0)
        self.assertLess(bets["Home"]["pnl"], 0)               # lost: P&L is confirmation only
        self.assertGreater(bets["Away"]["pnl"], 0)
        away_close = C.devig_power(self.PCLOSE)["Away"]
        self.assertAlmostEqual(bets["Away"]["clv_prob"], away_close - bets["Away"]["cost"])

    def test_negative_clv(self):
        rows = [pin("2026-10-03T12:00:00+00:00", self.PCLOSE),
                pin("2026-10-03T22:30:00+00:00", self.P1)]
        out = C.evaluate(rows, [quote("2026-10-03T12:00:00+00:00", "Home", 0.55)])
        self.assertLess(out["bets"][0]["clv_return"], 0)

    def test_quote_without_same_run_pinnacle_is_ignored(self):
        rows = [pin("2026-10-03T12:00:00+00:00", self.P1)]
        out = C.evaluate(rows, [quote("2026-10-03T12:00:01+00:00", "Home", 0.10)])
        self.assertEqual(out["bets"], [])

    def test_post_kickoff_quote_is_not_a_bet(self):
        rows = [pin("2026-10-03T23:30:00+00:00", self.P1)]
        out = C.evaluate(rows, [quote("2026-10-03T23:30:00+00:00", "Home", 0.10)])
        self.assertEqual(out["bets"], [])

    def test_kalshi_fee_reduces_clv(self):
        rows = [pin("2026-10-03T22:30:00+00:00", self.P1)]
        pm = C.evaluate(rows, [quote("2026-10-03T22:30:00+00:00", "Home", 0.45)])["bets"][0]
        ks = C.evaluate(rows, [quote("2026-10-03T22:30:00+00:00", "Home", 0.45, "KALSHI")])
        self.assertLess(ks["bets"][0]["clv_return"], pm["clv_return"])


if __name__ == "__main__":
    unittest.main()
