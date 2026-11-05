#!/usr/bin/env python3
"""Bounded, read-only Yahoo 1m ETF-pair economic prequalification.
No orders, no lookahead fill assumptions, no investment recommendation.
Outputs JSON + raw timestamped CSVs. Uses Python standard library only.
"""
import csv
import datetime as dt
import json
import math
import os
import pathlib
import statistics
import sys
import urllib.error
import urllib.parse
import urllib.request

SYMBOLS = ("MWRD.PA", "IWDA.AS")
OUT = pathlib.Path(os.getenv("ETF_OUTPUT_DIR", "artifacts/etf-pair"))
OUT.mkdir(parents=True, exist_ok=True)

def get(symbol):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + urllib.parse.quote(symbol) + "?range=5d&interval=1m"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as response:
        payload = json.load(response)
    error = payload.get("chart", {}).get("error")
    if error:
        raise ValueError(str(error))
    result = payload["chart"]["result"][0]
    meta = result.get("meta", {})
    quotes = result["indicators"]["quote"][0]
    rows = {}
    for i, stamp in enumerate(result.get("timestamp", [])):
        vals = {k: quotes.get(k, [None] * len(result["timestamp"]))[i] for k in ("open", "high", "low", "close", "volume")}
        if vals["close"] is None or not math.isfinite(float(vals["close"])) or float(vals["close"]) <= 0:
            continue
        rows[int(stamp)] = vals
    return meta, rows

def main():
    summary = {"status": "UNKNOWN", "source": "Yahoo Finance chart public endpoint", "interval": "1m",
               "range": "5d", "symbols": list(SYMBOLS), "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "caveat": "OHLCV bars are not executable bid/ask quotes; no proof of short availability or net profitability."}
    series = {}
    for symbol in SYMBOLS:
        try:
            meta, rows = get(symbol)
            summary[symbol] = {"status": "OK", "bars": len(rows), "currency": meta.get("currency"),
                               "exchange": meta.get("exchangeName"), "instrument_type": meta.get("instrumentType"),
                               "first_utc": dt.datetime.fromtimestamp(min(rows), dt.timezone.utc).isoformat() if rows else None,
                               "last_utc": dt.datetime.fromtimestamp(max(rows), dt.timezone.utc).isoformat() if rows else None}
            with (OUT / (symbol + ".csv")).open("w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp_utc", "open", "high", "low", "close", "volume"])
                for ts, q in sorted(rows.items()):
                    writer.writerow([dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat()] + [q[k] for k in ("open", "high", "low", "close", "volume")])
            series[symbol] = rows
        except Exception as exc:
            summary[symbol] = {"status": "UNAVAILABLE", "error": str(exc)[:350]}
    if len(series) == 2 and all(series.values()):
        a, b = (series[s] for s in SYMBOLS)
        common = sorted(set(a) & set(b))
        summary["common_bars"] = len(common)
        summary["union_bars"] = len(set(a) | set(b))
        summary["common_coverage_pct"] = round(100 * len(common) / len(set(a) | set(b)), 3)
        summary["both_currency_eur"] = all(summary[s]["currency"] == "EUR" for s in SYMBOLS)
        if len(common) >= 20 and summary["both_currency_eur"]:
            # Index normalized at first *jointly observed* minute; descriptive only.
            a0, b0 = float(a[common[0]]["close"]), float(b[common[0]]["close"])
            gaps = [10000 * (float(a[t]["close"]) / a0 - float(b[t]["close"]) / b0) for t in common]
            summary["indicative_normalized_gap_bp"] = {
                "min": round(min(gaps), 4), "max": round(max(gaps), 4),
                "median_abs": round(statistics.median(map(abs, gaps)), 4)}
            summary["status"] = "INDICATIVE_ONLY_NO_EXECUTABLE_EDGE_PROOF"
        else:
            summary["status"] = "UNKNOWN_INSUFFICIENT_COMMON_BARS_OR_CURRENCY"
    (OUT / "verdict.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    # No positive economic verdict is possible from OHLCV-only data.
    return 0 if len(series) == 2 else 2

if __name__ == "__main__":
    sys.exit(main())
