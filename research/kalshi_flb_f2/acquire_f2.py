"""F2 acquisition for KALSHI-FLB-OOS-001 (Revision 1 + R16 of the pre-registration).

NOT TO BE RUN until the gates in the pre-registration are cleared (Codex
challenge window closed, Kalshi Developer Agreement read, harness frozen).
Stages (each a separate invocation; every response body is hashed):

    list     paginate GET /historical/markets -> raw pages + BLINDED manifest
    candles  GET /historical/markets/{ticker}/candlesticks for manifest tickers
    meta     events -> series_ticker, series -> category, fee changes
    assemble build the analysis input directory (joins `result` only here)

Only the standard library; generic User-Agent; at most 5 requests per second.
"""
import hashlib
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import datetime as dt

sys.dont_write_bytecode = True

BASE = "https://api.elections.kalshi.com/trade-api/v2"
UA = "quant-research-paper-shadow/0.1"
MAX_RPS = 5.0
WIN_LO = dt.datetime(2025, 5, 1, tzinfo=dt.timezone.utc)
WIN_HI = dt.datetime(2026, 8, 1, tzinfo=dt.timezone.utc)
BLIND_FIELDS = ("ticker", "event_ticker", "market_type", "open_time", "close_time", "settlement_ts", "can_close_early")
MAX_HOURS = 12.0

_lock, _next = threading.Lock(), [0.0]


def _pace():
    with _lock:
        now = time.monotonic()
        t = max(now, _next[0])
        _next[0] = t + 1.0 / MAX_RPS
    if t > now:
        time.sleep(t - now)


def get_json(path, params=None, tries=5):
    url = BASE + path + (("?" + urllib.parse.urlencode(params)) if params else "")
    delay, bad = 2.0, 0
    for _ in range(tries):
        _pace()
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read()
                return url, body, json.loads(body)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise RuntimeError(f"HTTP {e.code} (authentication/permission) for {url}; stop and re-route F2")
            if e.code == 429:
                bad += 1
                if bad >= 3:
                    raise RuntimeError(f"HTTP 429 repeated for {url}; stopping")
            if e.code == 404:
                return url, b"", None
            time.sleep(delay)
            delay *= 2
        except (urllib.error.URLError, TimeoutError):
            time.sleep(delay)
            delay *= 2
    raise RuntimeError(f"giving up on {url}")


def parse_t(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def blind_filter(markets):
    """List-only filters (no outcome field is used) -> (blinded rows, counts)."""
    rows, counts = [], {"input": len(markets), "no_settlement": 0, "outside_window": 0, "not_binary": 0, "open_lt_24h": 0}
    for m in markets:
        st = m.get("settlement_ts")
        if not st:
            counts["no_settlement"] += 1
            continue
        if not (WIN_LO <= parse_t(st) < WIN_HI):
            counts["outside_window"] += 1
            continue
        if m.get("market_type") != "binary":
            counts["not_binary"] += 1
            continue
        if (parse_t(m["close_time"]) - parse_t(m["open_time"])).total_seconds() < 24 * 3600:
            counts["open_lt_24h"] += 1
            continue
        rows.append({k: m.get(k) for k in BLIND_FIELDS})
    counts["kept"] = len(rows)
    return rows, counts


def projected_hours(n_markets, n_events, n_series):
    """Requests: one candle call per market + one event call per event + one series call per series + fees."""
    return (n_markets + n_events + n_series + 2) / MAX_RPS / 3600.0


def subsample_events(rows):
    keep = [r for r in rows if hashlib.sha256(r["event_ticker"].encode("utf-8")).digest()[0] < 0x80]
    return keep


def candle_params(close_time_iso):
    t = parse_t(close_time_iso)
    return {"start_ts": int((t - dt.timedelta(hours=25)).timestamp()) + 1,
            "end_ts": int((t - dt.timedelta(hours=24)).timestamp()),
            "period_interval": 60}


def save_once(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "xb") as f:
        f.write(body)
    return hashlib.sha256(body).hexdigest()


def stage_list(out_dir):
    pages, rows_all, cursor, n = [], [], "", 0
    tot = {"input": 0, "no_settlement": 0, "outside_window": 0, "not_binary": 0, "open_lt_24h": 0, "kept": 0}
    while True:
        params = {"limit": 1000, "mve_filter": "exclude"}
        if cursor:
            params["cursor"] = cursor
        url, body, data = get_json("/historical/markets", params)
        if data is None or "markets" not in data:
            raise RuntimeError("unexpected historical markets response")
        h = save_once(f"{out_dir}/raw/markets_page_{n:05d}.json", body)
        pages.append({"url": url, "sha256": h, "bytes": len(body), "n": len(data["markets"]),
                      "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        page_rows, c = blind_filter(data["markets"])   # outcome fields never read; page is not retained in memory
        rows_all.extend(page_rows)
        for k in tot:
            tot[k] += c[k]
        cursor = data.get("cursor") or ""
        n += 1
        if not cursor:
            break
    rows, counts = rows_all, tot
    events = {r["event_ticker"] for r in rows}
    hours = projected_hours(len(rows), len(events), len(events))
    subsampled = False
    if hours > MAX_HOURS:
        rows = subsample_events(rows)
        subsampled = True
    with open(f"{out_dir}/blinded_manifest.jsonl", "x") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    with open(f"{out_dir}/list_manifest.json", "x") as f:
        json.dump({"pages": pages, "counts": counts, "projected_hours": hours, "subsampled": subsampled,
                   "kept_after_subsample": len(rows)}, f, indent=1)
    return counts


if __name__ == "__main__":
    if sys.argv[1] == "list":
        print(json.dumps(stage_list(sys.argv[2])))
    else:
        raise SystemExit("stage not implemented in this draft: candles/meta/assemble follow once the list stage is reviewed")
