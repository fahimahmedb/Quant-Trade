"""Offline tests for H-011's R2 (trades) and H-013's R4 (rewards) collectors, both
extending ``h001_relay``. All prices, ids, tickers and keys below are INVENTED
FIXTURES, not market data. No network is used: fetchers are stubbed.
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
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("fetch_feeds", ROOT / "scripts" / "fetch_feeds.py")
fetch_feeds = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fetch_feeds)

NOW = datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc)


def write(out: Path, stream: str, key: str, record: dict, observed_at: str) -> None:
    # ``Stream`` must be built from the SAME "<stream>.jsonl" spelling collect()
    # yields (see its own module docstring): that keeps its legacy-file check
    # (``path``, with the suffix) distinct from its shard directory (``self.base``,
    # without it) -- passing the bare stream name here collapses the two and makes
    # a second write see the first write's shard directory as a "legacy" flat file.
    fetch_feeds.Stream(out / f"{stream}.jsonl").add(key, record, observed_at)


def seed_matched_pm_quote(out: Path, market_id: str, event_id: str, outcome: str,
                          kickoff: str, observed_at: str) -> None:
    write(out, R.QUOTES_PM, f"{observed_at}|{event_id}|{outcome}",
         {"odds_event_id": event_id, "sport": "basketball_nba", "commence_time": kickoff,
          "venue": "POLYMARKET", "outcome": outcome, "market_id": market_id,
          "token_id": f"tok-{outcome}", "best_bid": 0.5, "best_ask": 0.52}, observed_at)


def seed_matched_kalshi_quote(out: Path, ticker: str, event_id: str, outcome: str,
                              kickoff: str, observed_at: str) -> None:
    write(out, R.QUOTES_KALSHI, f"{observed_at}|{event_id}|{outcome}",
         {"odds_event_id": event_id, "sport": "basketball_nba", "commence_time": kickoff,
          "venue": "KALSHI", "outcome": outcome, "ticker": ticker,
          "best_bid": 0.40, "best_ask": 0.42}, observed_at)


# =====================================================================================
# R2: trades
# =====================================================================================
class LatestMatchedMarkets(unittest.TestCase):
    def test_dedups_across_snapshots_and_carries_both_venues(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            seed_matched_pm_quote(out, "0xabc", "evt1", "Heat", "2026-10-10T00:00:00Z",
                                  "2026-10-09T12:00:00+00:00")
            seed_matched_pm_quote(out, "0xabc", "evt1", "Heat", "2026-10-10T00:00:00Z",
                                  "2026-10-09T18:00:00+00:00")   # later snapshot, same market
            seed_matched_kalshi_quote(out, "KXNBA-HEAT", "evt1", "Heat",
                                      "2026-10-10T00:00:00Z", "2026-10-09T18:00:00+00:00")
            markets = R._latest_matched_markets(out)
            self.assertEqual(len(markets), 2)      # one PM, one Kalshi -- not 3
            venues = {venue for venue, _, _ in markets}
            self.assertEqual(venues, {"POLYMARKET", "KALSHI"})


class PolymarketTradesParsing(unittest.TestCase):
    def test_drops_prints_with_no_id_price_or_size(self):
        payload = [{"id": "t1", "price": "0.55", "size": "10", "side": "BUY",
                   "timestamp": 1760000000},
                  {"id": "t2", "price": None, "size": "10", "timestamp": 1760000001},
                  {"price": "0.5", "size": "5", "timestamp": 1760000002},   # no id at all
                  {"id": "t3", "price": "0.5", "size": "0", "timestamp": 1760000003}]
        parsed = R.parse_polymarket_trades(payload)
        self.assertEqual([t["trade_id"] for t in parsed], ["t1"])
        self.assertEqual(parsed[0]["price"], 0.55)
        self.assertEqual(parsed[0]["size"], 10.0)

    def test_pagination_stops_on_short_page(self):
        pages = {0: [{"id": f"t{i}", "price": "0.5", "size": "1", "timestamp": 1}
                    for i in range(3)],
                 3: []}

        def get(url):
            offset = int(url.split("offset=")[1].split("&")[0])
            return pages.get(offset, [])

        trades = R.fetch_polymarket_trades("0xabc", get=get, page_size=3, max_pages=5)
        self.assertEqual(len(trades), 3)


class KalshiTradesParsing(unittest.TestCase):
    def test_cursor_pagination(self):
        pages = {"": {"trades": [{"trade_id": "a", "yes_price": 40, "taker_side": "yes",
                                  "created_time": "2026-10-10T00:00:00Z"}], "cursor": "p2"},
                 "p2": {"trades": [{"trade_id": "b", "yes_price": 41, "taker_side": "no",
                                    "created_time": "2026-10-10T00:01:00Z"}], "cursor": None}}

        def get(url):
            cursor = url.split("cursor=")[1] if "cursor=" in url else ""
            return pages[cursor]

        trades = R.fetch_kalshi_trades("KXNBA-HEAT", get=get)
        self.assertEqual([t["trade_id"] for t in trades], ["a", "b"])

    def test_missing_trade_id_dropped(self):
        trades, cursor = R.parse_kalshi_trades({"trades": [{"yes_price": 40}], "cursor": None})
        self.assertEqual(trades, [])
        self.assertIsNone(cursor)


class CollectTrades(unittest.TestCase):
    KICKOFF = "2026-10-10T00:00:00Z"   # 12h before NOW

    def seed(self, out: Path) -> None:
        seed_matched_pm_quote(out, "0xabc", "evt1", "Heat", self.KICKOFF,
                              "2026-10-09T12:00:00+00:00")
        seed_matched_kalshi_quote(out, "KXNBA-HEAT", "evt1", "Heat", self.KICKOFF,
                                  "2026-10-09T12:00:00+00:00")

    def test_sweeps_a_market_1_72h_post_kickoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.seed(out)

            def get(url):
                if "polymarket" in url:
                    return [{"id": "pmt1", "price": "0.6", "size": "20", "side": "BUY",
                            "timestamp": 1760000000}] if "offset=0" in url else []
                return {"trades": [{"trade_id": "kt1", "yes_price": 60, "taker_side": "yes",
                                    "created_time": "2026-10-10T01:00:00Z"}], "cursor": None}

            items = list(R.collect_trades(out, NOW, get=get))
            trades = [r for s, _, r in items if s == f"{R.TRADES}.jsonl"]
            ledger = [r for s, _, r in items if s == f"{R.TRADES_LEDGER}.jsonl"]
            self.assertEqual({t["trade_id"] for t in trades}, {"pmt1", "kt1"})
            self.assertEqual(len(ledger), 2)
            for row in ledger:
                self.assertEqual(row["status"], "OK")
                self.assertEqual(row["odds_event_id"], "evt1")

    def test_already_fetched_market_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.seed(out)
            write(out, R.TRADES_LEDGER, "POLYMARKET|0xabc",
                 {"venue": "POLYMARKET", "market_id": "0xabc", "status": "OK"},
                 "2026-10-10T06:00:00+00:00")

            def get(url):
                if "polymarket" in url:
                    raise AssertionError("must not fetch an already-swept market")
                return {"trades": [], "cursor": None}

            items = list(R.collect_trades(out, NOW, get=get))
            # only the still-unswept Kalshi side should attempt anything
            touched_venues = {r["venue"] for s, _, r in items if s == f"{R.TRADES_LEDGER}.jsonl"}
            self.assertNotIn("POLYMARKET", touched_venues)
            self.assertIn("KALSHI", touched_venues)

    def test_too_soon_after_kickoff_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            kickoff = (NOW - timedelta(minutes=30)).isoformat().replace("+00:00", "Z")
            seed_matched_pm_quote(out, "0xabc", "evt1", "Heat", kickoff,
                                  "2026-10-10T11:00:00+00:00")

            def get(url):
                raise AssertionError("must not fetch before TRADE_MIN_AGE_H")

            items = list(R.collect_trades(out, NOW, get=get))
            self.assertEqual(items, [])

    def test_too_long_after_kickoff_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            kickoff = (NOW - timedelta(hours=100)).isoformat().replace("+00:00", "Z")
            seed_matched_pm_quote(out, "0xabc", "evt1", "Heat", kickoff,
                                  "2026-10-06T00:00:00+00:00")

            def get(url):
                raise AssertionError("must not fetch past TRADE_MAX_AGE_H, ever")

            items = list(R.collect_trades(out, NOW, get=get))
            self.assertEqual(items, [])

    def test_trade_ids_dedup_via_the_shared_stream_writer(self):
        """Same market fetched via two separate collect_trades() generators (as two
        separate runs would) must not duplicate a trade already stored."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.seed(out)
            calls = {"n": 0}

            def get(url):
                calls["n"] += 1
                if "polymarket" in url and "offset=0" in url:
                    return [{"id": "pmt1", "price": "0.6", "size": "20", "side": "BUY",
                            "timestamp": 1760000000}]
                if "polymarket" in url:
                    return []
                return {"trades": [], "cursor": None}

            items = list(R.collect_trades(out, NOW, get=get))
            streams: dict[str, "fetch_feeds.Stream"] = {}
            for stream, key, record in items:
                streams.setdefault(stream, fetch_feeds.Stream(out / stream)).add(
                    key, record, NOW.isoformat(timespec="seconds"))
            stored = fetch_feeds.Stream(out / f"{R.TRADES}.jsonl").keys
            self.assertEqual(len(stored), 1)


# =====================================================================================
# R4: rewards
# =====================================================================================
class KalshiIncentivePrograms(unittest.TestCase):
    def test_extracts_and_keeps_raw(self):
        payload = {"incentive_programs": [
            {"series_ticker": "KXNBAGAME", "start_date": "2026-01-01", "end_date": "2027-01-01",
             "daily_pool_dollars": 500}]}
        out = R.parse_kalshi_incentive_programs(payload)
        self.assertEqual(out[0]["program_key"], "KXNBAGAME")
        self.assertEqual(out[0]["daily_pool_dollars"], 500.0)
        self.assertEqual(out[0]["raw"]["series_ticker"], "KXNBAGAME")

    def test_bare_list_payload_also_accepted(self):
        out = R.parse_kalshi_incentive_programs([{"ticker": "T1", "daily_pool_dollars": 10}])
        self.assertEqual(out[0]["program_key"], "T1")

    def test_program_with_no_identifying_key_is_dropped(self):
        out = R.parse_kalshi_incentive_programs({"incentive_programs": [{"daily_pool_dollars": 1}]})
        self.assertEqual(out, [])


class PolymarketRewardsParsing(unittest.TestCase):
    def test_extracts_min_size_and_max_spread(self):
        payload = {"data": [{"condition_id": "0xabc",
                             "rewards_config": {"rewards_min_size": 100, "rewards_max_spread": 0.03},
                             "rewards_daily_rate": 50}], "next_cursor": None}
        out, cursor = R.parse_polymarket_rewards(payload)
        self.assertEqual(out[0]["market_id"], "0xabc")
        self.assertEqual(out[0]["min_size"], 100.0)
        self.assertEqual(out[0]["max_spread"], 0.03)
        self.assertIsNone(cursor)

    def test_pagination_stops_at_lte_cursor(self):
        pages = {"": {"data": [{"condition_id": "0x1"}], "next_cursor": "c2"},
                 "c2": {"data": [{"condition_id": "0x2"}], "next_cursor": "LTE="}}

        def get(url):
            cursor = url.split("next_cursor=")[1] if "next_cursor=" in url else ""
            return pages[cursor]

        out = R.fetch_polymarket_rewards(get=get)
        self.assertEqual({r["market_id"] for r in out}, {"0x1", "0x2"})

    def test_market_with_no_id_dropped(self):
        out, _ = R.parse_polymarket_rewards({"data": [{"rewards_daily_rate": 1}]})
        self.assertEqual(out, [])


class KalshiOrderbookParsing(unittest.TestCase):
    def test_no_bids_become_yes_asks(self):
        payload = {"orderbook": {"yes": [[40, 100], [38, 50]], "no": [[57, 80], [55, 40]]}}
        book = R.parse_kalshi_orderbook(payload, "KXNBA-HEAT")
        self.assertAlmostEqual(book["best_bid"], 0.40)
        self.assertAlmostEqual(book["best_ask"], 0.43)     # 1 - 0.57
        self.assertEqual(book["venue"], "KALSHI")
        self.assertAlmostEqual(book["bid_depth"], 150.0)

    def test_empty_book_returns_none(self):
        self.assertIsNone(R.parse_kalshi_orderbook({"orderbook": {"yes": [], "no": []}}, "T"))
        self.assertIsNone(R.parse_kalshi_orderbook({}, "T"))


class CollectRewards(unittest.TestCase):
    def stub_get(self, kalshi_programs=None, pm_rewards=None, pm_book=None, kalshi_book=None):
        kalshi_programs = kalshi_programs if kalshi_programs is not None else {
            "incentive_programs": [{"series_ticker": "KXNBAGAME", "daily_pool_dollars": 500}]}
        pm_rewards = pm_rewards if pm_rewards is not None else {
            "data": [{"condition_id": "0xabc", "rewards_max_spread": 0.03}], "next_cursor": None}

        def get(url):
            if "incentive_programs" in url:
                return kalshi_programs
            if "rewards/markets/current" in url:
                return pm_rewards
            if "clob.polymarket.com/book" in url:
                return pm_book or {"bids": [{"price": "0.5", "size": "10"}],
                                   "asks": [{"price": "0.52", "size": "10"}]}
            if "orderbook" in url:
                return kalshi_book or {"orderbook": {"yes": [[40, 10]], "no": [[55, 10]]}}
            raise AssertionError(f"unexpected url {url}")
        return get

    def test_program_and_reward_snapshots_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            items = list(R.collect_rewards(Path(tmp), NOW, get=self.stub_get()))
            kalshi_rows = [r for s, _, r in items if s == f"{R.REWARDS_KALSHI}.jsonl"]
            pm_rows = [r for s, _, r in items if s == f"{R.REWARDS_POLYMARKET}.jsonl"]
            self.assertEqual(kalshi_rows[0]["program_key"], "KXNBAGAME")
            self.assertEqual(pm_rows[0]["market_id"], "0xabc")

    def test_orderbook_only_for_matched_markets_within_horizon(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            seed_matched_pm_quote(out, "0xabc", "evt1", "Heat",
                                  (NOW + timedelta(hours=40)).isoformat(), "2026-10-10T00:00:00+00:00")
            seed_matched_kalshi_quote(out, "KXNBA-HEAT", "evt2", "Bulls",
                                      (NOW + timedelta(hours=60)).isoformat(),  # outside 48h
                                      "2026-10-10T00:00:00+00:00")
            items = list(R.collect_rewards(out, NOW, get=self.stub_get()))
            books = [(r["odds_event_id"]) for s, _, r in items if s == f"{R.REWARDS_ORDERBOOKS}.jsonl"]
            self.assertEqual(books, ["evt1"])       # evt2's market kicks off too far out

    def test_past_kickoff_market_gets_no_orderbook(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            seed_matched_pm_quote(out, "0xabc", "evt1", "Heat",
                                  (NOW - timedelta(hours=1)).isoformat(), "2026-10-09T00:00:00+00:00")
            items = list(R.collect_rewards(out, NOW, get=self.stub_get()))
            books = [r for s, _, r in items if s == f"{R.REWARDS_ORDERBOOKS}.jsonl"]
            self.assertEqual(books, [])

    def test_a_fetch_failure_yields_nothing_for_that_venue_but_not_the_other(self):
        def get(url):
            if "incentive_programs" in url:
                raise R.DataUnavailable("kalshi is down")
            if "rewards/markets/current" in url:
                return {"data": [{"condition_id": "0xabc"}], "next_cursor": None}
            raise AssertionError(url)

        with tempfile.TemporaryDirectory() as tmp:
            items = list(R.collect_rewards(Path(tmp), NOW, get=get))
        self.assertEqual([r for s, _, r in items if s == f"{R.REWARDS_KALSHI}.jsonl"], [])
        self.assertEqual(len([r for s, _, r in items if s == f"{R.REWARDS_POLYMARKET}.jsonl"]), 1)

    def test_unchanged_program_terms_are_a_duplicate_not_a_restatement(self):
        """Stable keys are the whole point: an unmoved program across two runs must
        not bloat the stream with an identical row every 6h."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            get = self.stub_get()
            stream = fetch_feeds.Stream(out / f"{R.REWARDS_KALSHI}.jsonl")
            first_run = [r for s, k, r in R.collect_rewards(out, NOW, get=get)
                        if s == f"{R.REWARDS_KALSHI}.jsonl"]
            for r in first_run:
                self.assertEqual(stream.add(r["program_key"], r, NOW.isoformat(timespec="seconds")),
                                 "observation")
            later = NOW + timedelta(hours=6)
            second_run = [r for s, k, r in R.collect_rewards(out, later, get=get)
                         if s == f"{R.REWARDS_KALSHI}.jsonl"]
            for r in second_run:
                self.assertEqual(stream.add(r["program_key"], r, later.isoformat(timespec="seconds")),
                                 "duplicate")

    def test_changed_pool_is_a_restatement(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            stream = fetch_feeds.Stream(out / f"{R.REWARDS_KALSHI}.jsonl")
            first = next(r for s, k, r in R.collect_rewards(out, NOW, get=self.stub_get())
                        if s == f"{R.REWARDS_KALSHI}.jsonl")
            stream.add(first["program_key"], first, NOW.isoformat(timespec="seconds"))
            raised_pool = self.stub_get(kalshi_programs={
                "incentive_programs": [{"series_ticker": "KXNBAGAME", "daily_pool_dollars": 900}]})
            later = NOW + timedelta(hours=6)
            second = next(r for s, k, r in R.collect_rewards(out, later, get=raised_pool)
                         if s == f"{R.REWARDS_KALSHI}.jsonl")
            self.assertEqual(stream.add(second["program_key"], second,
                                        later.isoformat(timespec="seconds")), "restatement")


if __name__ == "__main__":
    unittest.main()
