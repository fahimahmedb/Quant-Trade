"""Offline tests for the external connectors' pure parsers and the feed collector.

Fixtures reproduce each provider's documented response *shape* with made-up
numbers; they are never market evidence.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from quant.dataplane import connectors as c

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


class EquityParsers(unittest.TestCase):
    def test_yahoo_drops_incomplete_bars_and_uses_exchange_date(self):
        payload = {"chart": {"error": None, "result": [{
            "meta": {"gmtoffset": -14400},
            "timestamp": [1726147800, 1726234200, 1726320600],
            "indicators": {"quote": [{"open": [10, None, 12], "high": [11, 12, 13],
                                      "low": [9, 10, 11], "close": [10.5, 11.5, 12.5],
                                      "volume": [100, 200, 300]}],
                           "adjclose": [{"adjclose": [10.4, 11.4, 12.4]}]}}]}}
        rows = c.parse_yahoo_chart(payload, "SPY")
        self.assertEqual([r["date"] for r in rows], ["2024-09-12", "2024-09-14"])
        self.assertEqual(rows[1]["adj_close"], 12.4)
        self.assertEqual(c.parse_yahoo_chart({"chart": {"error": {"code": "x"}}}, "SPY"), [])

    def test_stooq_and_fred(self):
        rows = c.parse_stooq_csv("Date,Open,High,Low,Close,Volume\n2026-09-01,1,2,0.5,1.5,10\n"
                                 "2026-09-02,,2,0.5,1.5,10\n", "SPY")
        self.assertEqual(len(rows), 1)
        fred = c.parse_fred_csv("observation_date,DGS3MO\n2026-09-01,4.1\n2026-09-02,.\n",
                                "DGS3MO")
        self.assertEqual(fred, [{"series": "DGS3MO", "date": "2026-09-01", "value": 4.1}])


class CalendarParser(unittest.TestCase):
    HTML = ('<h4><a>2026 FOMC Meetings</a></h4>'
            '<div class="fomc-meeting__month col-xs-5"><strong>January</strong></div>'
            '<div class="fomc-meeting__date col-xs-4">27-28</div>'
            '<div class="fomc-meeting__month"><strong>Apr/May</strong></div>'
            '<div class="fomc-meeting__date">30-1*</div>'
            '<div class="fomc-meeting__month"><strong>August</strong></div>'
            '<div class="fomc-meeting__date">16 (unscheduled)</div>'
            '<h4>2025 FOMC Meetings</h4>'
            '<div class="fomc-meeting__month"><strong>Dec/Jan</strong></div>'
            '<div class="fomc-meeting__date">31-1</div>')

    def test_decision_day_is_last_day_and_unscheduled_excluded(self):
        days = [item["decision_date"] for item in c.parse_fomc_calendar(self.HTML)]
        self.assertEqual(days, ["2026-01-01", "2026-01-28", "2026-05-01"])
        self.assertTrue(next(i for i in c.parse_fomc_calendar(self.HTML)
                             if i["decision_date"] == "2026-05-01")["projections"])


class CryptoParsers(unittest.TestCase):
    def test_funding_parsers_normalise_venue_coin_and_interval(self):
        hl = c.parse_hyperliquid_funding([{"coin": "ETH", "fundingRate": "0.0000125",
                                           "premium": "0.0001", "time": 1727000000000},
                                          {"coin": "ETH", "fundingRate": "x", "time": 1}])
        self.assertEqual(hl, [{"venue": "HYPERLIQUID", "coin": "ETH", "time_ms": 1727000000000,
                               "rate": 0.0000125, "interval_hours": 1}])
        by = c.parse_bybit_funding({"retCode": 0, "result": {"list": [
            {"symbol": "ETHUSDT", "fundingRate": "0.0001", "fundingRateTimestamp": "1727000000000"},
            {"symbol": "ETHUSDC", "fundingRate": "0.0001", "fundingRateTimestamp": "1"}]}})
        self.assertEqual([(r["coin"], r["interval_hours"]) for r in by], [("ETH", 8)])
        self.assertEqual(c.parse_bybit_funding({"retCode": 10001, "result": {}}), [])
        bn = c.parse_binance_funding([{"symbol": "BTCUSDT", "fundingTime": 1727000000000,
                                       "fundingRate": "-0.0002", "markPrice": "60000"}])
        self.assertEqual(bn[0]["rate"], -0.0002)

    def test_hyperliquid_universe(self):
        payload = [{"universe": [{"name": "BTC"}, {"name": "HYPE"}]},
                   [{"dayNtlVlm": "1e9", "markPx": "60000", "funding": "0.00001"},
                    {"dayNtlVlm": "5e7", "markPx": "20", "funding": "-0.0001"}]]
        coins = c.parse_hyperliquid_universe(payload)
        self.assertEqual([item["coin"] for item in coins], ["BTC", "HYPE"])
        self.assertEqual(c.parse_hyperliquid_universe({"bad": 1}), [])


class PredictionMarketParsers(unittest.TestCase):
    def test_polymarket_markets_and_book(self):
        markets = c.parse_polymarket_markets([{
            "conditionId": "0xabc", "question": "Will X?", "category": "Sports",
            "clobTokenIds": json.dumps(["111", "222"]), "outcomes": json.dumps(["Yes", "No"]),
            "outcomePrices": json.dumps(["0.61", "0.39"]), "negRisk": False,
            "volume24hr": 1234.5, "liquidity": "5000", "events": [{"slug": "x"}]},
            {"conditionId": "0xbad", "clobTokenIds": "not json"}])
        self.assertEqual(len(markets), 1)
        self.assertEqual(markets[0]["tokens"][0], {"token_id": "111", "outcome": "Yes",
                                                   "price": 0.61})
        book = c.parse_order_book({"bids": [{"price": "0.60", "size": "100"},
                                            {"price": "0.61", "size": "5"}],
                                   "asks": [{"price": "0.63", "size": "0"},
                                            {"price": "0.64", "size": "50"}]},
                                  "POLYMARKET", "111")
        self.assertEqual((book["best_bid"], book["best_ask"]), (0.61, 0.64))
        self.assertIsNone(c.parse_order_book({"bids": [], "asks": []}, "POLYMARKET", "x"))

    def test_kalshi_prices_are_converted_from_cents(self):
        markets = c.parse_kalshi_markets({"markets": [{"ticker": "T-1", "yes_bid": 41,
                                                       "yes_ask": 44, "volume_24h": 10}]})
        self.assertEqual((markets[0]["yes_bid"], markets[0]["yes_ask"]), (0.41, 0.44))


class OddsParser(unittest.TestCase):
    def test_h2h_prices_and_invalid_prices_dropped(self):
        payload = [{"id": "e1", "sport_key": "soccer_epl", "commence_time": "2026-09-27T14:00:00Z",
                    "home_team": "A", "away_team": "B", "bookmakers": [
                        {"key": "pinnacle", "last_update": "2026-09-26T10:00:00Z", "markets": [
                            {"key": "h2h", "outcomes": [{"name": "A", "price": 2.1},
                                                        {"name": "B", "price": 3.6},
                                                        {"name": "Draw", "price": 3.4}]}]},
                        {"key": "bad", "markets": [{"key": "h2h", "outcomes": [
                            {"name": "A", "price": 0.9}]}]}]}]
        rows = c.parse_odds_api(payload)
        self.assertEqual([r["bookmaker"] for r in rows], ["pinnacle"])
        self.assertEqual(rows[0]["prices"]["Draw"], 3.4)


class TransportAndCollector(unittest.TestCase):
    def test_unreachable_source_is_data_unavailable_not_a_crash(self):
        from quant.dataplane.adapters import DataUnavailable
        with self.assertRaises(DataUnavailable):
            c.get_json("http://127.0.0.1:9/never", retries=0, timeout=1)
        report = c.probe_all()
        self.assertEqual(set(report), set(c.CONNECTORS))
        self.assertTrue(all("status" in item for item in report.values()))

    def test_stream_is_append_only_and_keeps_restatements_separately(self):
        import fetch_feeds
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "s.jsonl"
            stream = fetch_feeds.Stream(path)
            self.assertEqual(stream.add("k", {"v": 1}, "t1"), "observation")
            self.assertEqual(stream.add("k", {"v": 1}, "t2"), "duplicate")
            self.assertEqual(stream.add("k", {"v": 2}, "t3"), "restatement")
            with path.open("a") as handle:
                handle.write('{"torn": ')           # a killed run's partial line
            reopened = fetch_feeds.Stream(path)
            self.assertEqual(reopened.add("k", {"v": 1}, "t4"), "duplicate")
            lines = [json.loads(line) for line in path.read_text().splitlines()[:2]]
            self.assertEqual([line["kind"] for line in lines], ["observation", "restatement"])
            self.assertEqual(lines[0]["record"], {"v": 1})


if __name__ == "__main__":
    unittest.main()


class VenueParsers(unittest.TestCase):
    def test_okx_and_dydx(self):
        okx = c.parse_okx_funding({"code": "0", "data": [
            {"instId": "ETH-USDT-SWAP", "fundingRate": "0.0001", "realizedRate": "0.00009",
             "fundingTime": "1727000000000"}]})
        self.assertEqual((okx[0]["coin"], okx[0]["rate"]), ("ETH", 0.00009))
        self.assertEqual(c.parse_okx_funding({"code": "51001", "data": []}), [])
        dydx = c.parse_dydx_funding({"historicalFunding": [
            {"ticker": "BTC-USD", "rate": "0.0000125", "effectiveAt": "2026-09-24T10:00:00.000Z"},
            {"ticker": "BTC-USD", "rate": "0.1", "effectiveAt": "not a date"}]})
        self.assertEqual(len(dydx), 1)
        self.assertEqual(dydx[0]["venue"], "DYDX")


class SessionClosedTests(unittest.TestCase):
    def test_partial_us_session_is_not_recorded(self):
        import fetch_feeds
        from datetime import datetime, timezone
        self.assertFalse(fetch_feeds.session_closed(
            "2026-09-25", datetime(2026, 9, 25, 18, 17, tzinfo=timezone.utc)))
        self.assertTrue(fetch_feeds.session_closed(
            "2026-09-24", datetime(2026, 9, 25, 0, 17, tzinfo=timezone.utc)))
