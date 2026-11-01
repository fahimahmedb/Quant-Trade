from __future__ import annotations

import hashlib
import json
import math
import statistics
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

EXPERIMENT_ID = "disc-binance-extreme-funding-reversal-l1-v1"
INVOCATION_ID = "owner-manual-20261012-a1"
PREDECLARATION_COMMIT = "99e94a37e9b580189042c686f385ea17bf6a0b11"
CLAIM_COMMIT = "38e3d97cefc90cc99397ea4bb40db71806bc62b9"
BASE = "https://fapi.binance.com"
SYMBOLS = ["BTCUSDT", "ETHUSDT"]
START_MS = int(datetime(2021, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
END_MS = int(datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc).timestamp() * 1000)
THRESHOLD = 0.0005
COST = 0.0010
HORIZON_MS = 8 * 60 * 60 * 1000
RESULT = Path(__file__).with_name("disc-binance-extreme-funding-reversal-l1-v1.result.json")
USER_AGENT = "Quant-Edge-Lab/1.0 research-only"


def get_json(path: str, params: dict[str, object], timeout: int = 20):
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
    return json.loads(body), body, url


def fetch_funding(symbol: str):
    rows = []
    raw_hasher = hashlib.sha256()
    cursor = START_MS
    calls = 0
    while cursor <= END_MS:
        payload, raw, _ = get_json(
            "/fapi/v1/fundingRate",
            {"symbol": symbol, "startTime": cursor, "endTime": END_MS, "limit": 1000},
        )
        calls += 1
        if not isinstance(payload, list):
            raise RuntimeError(f"fundingRate non-list response for {symbol}: {payload!r}")
        raw_hasher.update(raw)
        if not payload:
            break
        clean = [r for r in payload if START_MS <= int(r["fundingTime"]) <= END_MS]
        rows.extend(clean)
        last = int(payload[-1]["fundingTime"])
        if last < cursor:
            raise RuntimeError("funding pagination failed to advance")
        cursor = last + 1
        if len(payload) < 1000:
            break
        time.sleep(0.08)
    dedup = {}
    for r in rows:
        dedup[int(r["fundingTime"])] = r
    ordered = [dedup[k] for k in sorted(dedup)]
    return ordered, raw_hasher.hexdigest(), calls


def fetch_price_endpoints(symbol: str, funding_time: int):
    target = funding_time + HORIZON_MS
    payload, raw, url = get_json(
        "/fapi/v1/klines",
        {
            "symbol": symbol,
            "interval": "5m",
            "startTime": funding_time,
            "endTime": target + 5 * 60 * 1000,
            "limit": 110,
        },
    )
    if not isinstance(payload, list) or not payload:
        raise RuntimeError(f"empty/non-list klines for {symbol} {funding_time}: {payload!r}")
    bars = []
    for b in payload:
        bars.append(
            {
                "open_time": int(b[0]),
                "close": float(b[4]),
                "close_time": int(b[6]),
            }
        )
    entry_candidates = [b for b in bars if b["open_time"] >= funding_time]
    if not entry_candidates:
        raise RuntimeError("entry bar missing")
    entry = min(entry_candidates, key=lambda b: b["open_time"])
    exit_candidates = [b for b in bars if b["close_time"] <= target + 5 * 60 * 1000]
    if not exit_candidates:
        raise RuntimeError("exit bar missing")
    exit_bar = min(exit_candidates, key=lambda b: (abs(b["close_time"] - target), b["close_time"]))
    return entry, exit_bar, hashlib.sha256(raw).hexdigest(), url


def safe_mean(xs):
    return statistics.fmean(xs) if xs else None


def safe_median(xs):
    return statistics.median(xs) if xs else None


def iso(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()


def write_result(obj: dict):
    RESULT.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    if RESULT.exists():
        raise SystemExit("result already exists; replay forbidden")

    base = {
        "experiment_id": EXPERIMENT_ID,
        "invocation_id": INVOCATION_ID,
        "predeclaration_commit": PREDECLARATION_COMMIT,
        "claim_commit": CLAIM_COMMIT,
        "attempt": 1,
        "replay_allowed": False,
        "label": "EXPLORATORY",
        "real_capital_authorized": False,
        "live_trading_authorized": False,
        "paid_usd": 0,
        "frozen": {
            "symbols": SYMBOLS,
            "start_utc": "2021-01-01T00:00:00+00:00",
            "end_utc": "2025-12-31T23:59:59+00:00",
            "abs_funding_threshold": THRESHOLD,
            "horizon_hours": 8,
            "roundtrip_cost": COST,
            "funding_endpoint": "/fapi/v1/fundingRate",
            "price_endpoint": "/fapi/v1/klines",
            "interval": "5m",
        },
    }

    try:
        funding_by_symbol = {}
        source = {}
        for symbol in SYMBOLS:
            rows, digest, calls = fetch_funding(symbol)
            funding_by_symbol[symbol] = rows
            source[symbol] = {
                "funding_records": len(rows),
                "funding_raw_sha256": digest,
                "funding_calls": calls,
            }
    except Exception as e:
        base.update(
            {
                "typed_verdict": "PARK_DATA",
                "decision": "PARK_DATA",
                "economics_computed": False,
                "edge_validated": False,
                "source_access": "FUNDING_ENDPOINT_FAILED",
                "error": f"{type(e).__name__}: {e}",
                "reason": "Frozen official Binance funding source could not be retrieved in the one-shot execution; no threshold or source substitution is allowed.",
            }
        )
        write_result(base)
        return

    qualifying = []
    for symbol, rows in funding_by_symbol.items():
        for r in rows:
            rate = float(r["fundingRate"])
            if abs(rate) >= THRESHOLD:
                qualifying.append((symbol, int(r["fundingTime"]), rate))
    qualifying.sort(key=lambda x: (x[1], x[0]))

    events = []
    endpoint_failures = []
    for symbol, ft, rate in qualifying:
        try:
            entry, exit_bar, digest, url = fetch_price_endpoints(symbol, ft)
            signal = -1 if rate > 0 else 1
            gross = signal * (exit_bar["close"] / entry["close"] - 1.0)
            net = gross - COST
            events.append(
                {
                    "symbol": symbol,
                    "funding_time": ft,
                    "funding_time_utc": iso(ft),
                    "funding_rate": rate,
                    "signal": signal,
                    "entry_open_time": entry["open_time"],
                    "entry_close": entry["close"],
                    "exit_close_time": exit_bar["close_time"],
                    "exit_close": exit_bar["close"],
                    "signed_gross_return": gross,
                    "signed_net_return": net,
                    "kline_response_sha256": digest,
                }
            )
        except Exception as e:
            endpoint_failures.append(
                {
                    "symbol": symbol,
                    "funding_time": ft,
                    "error": f"{type(e).__name__}: {e}",
                }
            )
        time.sleep(0.06)

    qual_counts = {s: sum(1 for x in qualifying if x[0] == s) for s in SYMBOLS}
    observed_counts = {s: sum(1 for x in events if x["symbol"] == s) for s in SYMBOLS}
    coverage = len(events) / len(qualifying) if qualifying else 0.0
    base["source"] = source
    base["adequacy"] = {
        "qualifying_events": len(qualifying),
        "qualifying_by_symbol": qual_counts,
        "observed_events": len(events),
        "observed_by_symbol": observed_counts,
        "endpoint_failures": len(endpoint_failures),
        "coverage": coverage,
        "requires_total_at_least": 30,
        "requires_each_symbol_at_least": 5,
        "requires_coverage_at_least": 0.90,
    }

    adequate = (
        len(qualifying) >= 30
        and all(qual_counts[s] >= 5 for s in SYMBOLS)
        and coverage >= 0.90
    )
    if not adequate:
        base.update(
            {
                "typed_verdict": "PARK_DATA",
                "decision": "PARK_DATA",
                "economics_computed": False,
                "edge_validated": False,
                "reason": "Frozen adequacy gate failed; threshold/sample/source will not be tuned after access.",
                "endpoint_failures": endpoint_failures[:25],
            }
        )
        write_result(base)
        return

    gross = [x["signed_gross_return"] for x in events]
    net = [x["signed_net_return"] for x in events]
    by_symbol_gross = {
        s: safe_mean([x["signed_gross_return"] for x in events if x["symbol"] == s])
        for s in SYMBOLS
    }
    primary = {
        "mean_signed_gross_return": safe_mean(gross),
        "mean_signed_net_return": safe_mean(net),
        "median_signed_net_return": safe_median(net),
        "net_hit_rate": sum(1 for x in net if x > 0) / len(net),
        "mean_signed_gross_return_by_symbol": by_symbol_gross,
        "worst_signed_net_return": min(net),
        "best_signed_net_return": max(net),
    }
    base["economics_computed"] = True
    base["primary"] = primary

    if primary["mean_signed_net_return"] <= 0:
        decision = "KILL_EXPRESSION"
        red_team = {"executed": False, "passed": False, "reason": "primary kill"}
    else:
        passes_primary = (
            primary["mean_signed_gross_return"] >= 0.0020
            and primary["median_signed_net_return"] > 0
            and primary["net_hit_rate"] >= 0.55
            and all(by_symbol_gross[s] is not None and by_symbol_gross[s] > 0 for s in SYMBOLS)
        )
        if passes_primary:
            month_sums = defaultdict(float)
            for x in events:
                month = x["funding_time_utc"][:7]
                month_sums[month] += x["signed_net_return"]
            remove_month = sorted(month_sums, key=lambda m: (-month_sums[m], m))[0]
            remaining = [x["signed_net_return"] for x in events if x["funding_time_utc"][:7] != remove_month]
            remaining_mean = safe_mean(remaining)
            passed = remaining_mean is not None and remaining_mean > 0
            red_team = {
                "executed": True,
                "test": "remove UTC calendar month with largest positive net sum",
                "removed_month": remove_month,
                "removed_month_net_sum": month_sums[remove_month],
                "remaining_events": len(remaining),
                "remaining_mean_signed_net_return": remaining_mean,
                "passed": passed,
            }
            decision = "PROMOTE_EXPRESSION" if passed else "PARK_ECONOMICS"
        else:
            decision = "PARK_ECONOMICS"
            red_team = {"executed": False, "passed": False, "reason": "primary promotion hurdle not met"}

    base.update(
        {
            "typed_verdict": decision,
            "decision": decision,
            "edge_validated": False,
            "claim_ceiling": "PROMOTE_EXPRESSION",
            "red_team": red_team,
            "limits": {
                "close_to_close_proxy_not_fills": True,
                "funding_cashflow_included": False,
                "historical_fee_proof": False,
                "capacity": "UNKNOWN",
                "causal_identification": False,
                "alpha_validated": False,
            },
            "events": events,
            "endpoint_failures": endpoint_failures[:25],
        }
    )
    write_result(base)


if __name__ == "__main__":
    main()
