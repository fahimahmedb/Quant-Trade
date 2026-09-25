"""Collect external feeds into append-only, de-duplicated JSONL files.

    python3 scripts/fetch_feeds.py probe                 # reachability report (JSON)
    python3 scripts/fetch_feeds.py collect [--out DIR]   # append new records

Designed to run where the network is open (the GitHub Actions workflow
``data-feeds.yml``, or an operator machine). Each stream is
``<out>/<connector>/<stream>.jsonl``; every record carries ``observed_at`` (UTC
time it was fetched) and a ``key``. A key already present is never rewritten:
the first observation of a value is the point-in-time one, and a later
restatement (for example Yahoo's retroactive dividend adjustment) is kept as a
separate ``restatement`` record instead of overwriting history.

A failing source never stops the others; the run manifest ``_runs.jsonl``
records what each connector did.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.dataplane import connectors as c  # noqa: E402
from quant.dataplane.adapters import DataUnavailable  # noqa: E402

ETF_SYMBOLS = ["SPY", "TLT", "GLD", "XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV",
               "XLY"]
FUTURES_PROXIES = ["ES=F", "NQ=F", "ZN=F", "ZB=F", "GC=F", "CL=F", "6E=F", "6J=F"]
FRED_SERIES = ["DGS3MO", "DGS2", "DGS10"]
FUNDING_COINS = 40          # Hyperliquid coins by 24h notional volume
POLYMARKET_BOOKS = 20       # order-book snapshots per run (repository growth budget)


def session_closed(day: str, now: datetime) -> bool:
    """A US session's daily bar is final only after the close (21:00 UTC in
    winter, 20:00 in summer) plus a buffer; earlier it is an intraday partial
    that would otherwise become the 'first observation' of that day."""
    close = datetime.fromisoformat(day).replace(tzinfo=timezone.utc) + timedelta(hours=22)
    return now >= close


class Stream:
    """Append-only JSONL with an in-memory key index."""

    def __init__(self, path: Path):
        self.path = path
        self.keys: dict[str, str] = {}
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue            # a torn last line from a killed run
                self.keys[record["key"]] = record.get("digest", "")

    def add(self, key: str, record: dict, observed_at: str) -> str:
        digest = json.dumps(record, sort_keys=True)
        previous = self.keys.get(key)
        if previous == digest:
            return "duplicate"
        kind = "observation" if previous is None else "restatement"
        if kind == "restatement":
            key = f"{key}#restated@{observed_at}"
            if key in self.keys:
                return "duplicate"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"key": key, "kind": kind, "observed_at": observed_at,
                                     "digest": digest, "record": record},
                                    sort_keys=True) + "\n")
        self.keys[key] = digest
        return kind


def _collect(out: Path, now: datetime) -> dict:
    stamp = now.isoformat(timespec="seconds")
    report: dict[str, dict] = {}

    def run(name: str, work) -> None:
        counts = {"observation": 0, "restatement": 0, "duplicate": 0}
        try:
            for stream, key, record in work():
                counts[streams.setdefault(stream, Stream(out / stream)).add(key, record, stamp)] += 1
            report[name] = {"status": "OK", **counts}
        except DataUnavailable as exc:
            report[name] = {"status": "UNREACHABLE", "error": str(exc)[:200], **counts}
        except Exception as exc:  # noqa: BLE001 - a parser change must not stop others
            report[name] = {"status": "ERROR", "error": f"{type(exc).__name__}: {exc}"[:200],
                            **counts}

    streams: dict[str, Stream] = {}

    def yahoo():
        for symbol in ETF_SYMBOLS + FUTURES_PROXIES:
            for bar in c.fetch_yahoo(symbol, "1mo"):
                if session_closed(bar["date"], now):
                    yield "yahoo/daily_bars.jsonl", f"{bar['date']}|{symbol}", bar

    def fred():
        for series in FRED_SERIES:
            for item in c.fetch_fred(series)[-30:]:
                yield "fred/series.jsonl", f"{item['date']}|{series}", item

    def fomc():
        for item in c.fetch_fomc_calendar():
            yield "fomc/scheduled.jsonl", item["decision_date"], item

    def crypto():
        universe = sorted(c.fetch_hyperliquid_universe(),
                          key=lambda item: -(item["day_notional_volume"] or 0))
        hour = now.strftime("%Y-%m-%dT%H")
        for item in universe:
            yield "hyperliquid/universe.jsonl", f"{hour}|{item['coin']}", item
        since = int((now - timedelta(days=3)).timestamp() * 1000)
        for item in universe[:FUNDING_COINS]:
            coin = item["coin"]
            for rate in c.fetch_hyperliquid_funding(coin, since):
                yield "funding/rates.jsonl", f"HL|{coin}|{rate['time_ms']}", rate
            for fetch, venue in ((c.fetch_bybit_funding, "BYBIT"),
                                 (c.fetch_binance_funding, "BINANCE"),
                                 (c.fetch_okx_funding, "OKX"),
                                 (c.fetch_dydx_funding, "DYDX")):
                try:
                    for rate in fetch(coin):
                        yield "funding/rates.jsonl", f"{venue}|{coin}|{rate['time_ms']}", rate
                except DataUnavailable:
                    continue      # coin not listed there, or venue geo-blocked

    def polymarket():
        markets = c.fetch_polymarket_markets(500)
        hour = now.strftime("%Y-%m-%dT%H")
        for item in markets:
            yield "polymarket/markets.jsonl", f"{hour}|{item['market_id']}", item
        liquid = sorted(markets, key=lambda item: -(item["volume_24h"] or 0))[:POLYMARKET_BOOKS]
        for item in liquid:
            for token in item["tokens"][:1]:
                book = c.fetch_polymarket_book(token["token_id"])
                if book:
                    yield ("polymarket/books.jsonl", f"{stamp}|{token['token_id']}",
                           {**book, "market_id": item["market_id"]})

    def kalshi():
        hour = now.strftime("%Y-%m-%dT%H")
        for item in c.fetch_kalshi_markets(1000):
            yield "kalshi/markets.jsonl", f"{hour}|{item['market_id']}", item

    def odds():
        for sport in ("soccer_epl", "soccer_spain_la_liga", "basketball_nba",
                      "americanfootball_nfl"):
            for item in c.fetch_odds(sport):
                yield ("odds/h2h.jsonl", f"{item['event_id']}|{item['bookmaker']}|"
                       f"{item['quote_time']}", item)

    for name, work in (("yahoo_chart", yahoo), ("fred", fred), ("fomc_calendar", fomc),
                       ("crypto_funding", crypto), ("polymarket", polymarket),
                       ("kalshi", kalshi), ("odds_api", odds)):
        run(name, work)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("probe", "collect"))
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "feeds")
    args = parser.parse_args()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    if args.command == "probe":
        print(json.dumps(c.probe_all(), indent=2, sort_keys=True))
        return
    report = _collect(args.out, now)
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "_runs.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"run_at": now.isoformat(), "report": report},
                                sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
