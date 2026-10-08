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


def get_json(path, params=None, tries=5, tolerate=False):
    """GET JSON. 401/403 stop the run; repeated 429 stops it; with tolerate=True a persistent
    other HTTP error returns (url, b'', None) so one bad ticker cannot block the stage."""
    url = BASE + urllib.parse.quote(path, safe="/") + (("?" + urllib.parse.urlencode(params)) if params else "")
    delay, n429 = 2.0, 0
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
            if e.code == 404:
                return url, b"", None
            if e.code == 429:
                n429 += 1
                if n429 >= 3:
                    raise RuntimeError(f"HTTP 429 repeated for {url}; stopping")
                ra = e.headers.get("Retry-After") if e.headers else None
                time.sleep(float(ra) if ra and ra.replace(".", "", 1).isdigit() else delay)
                delay *= 2
                continue
            last = e.code
            time.sleep(delay)
            delay *= 2
        except (urllib.error.URLError, TimeoutError):
            last = "network"
            time.sleep(delay)
            delay *= 2
    if tolerate:
        return url, b"", None
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
    """Atomic, no-overwrite write: temp file, fsync, hard link into place."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "xb") as f:
        f.write(body)
        f.flush()
        os.fsync(f.fileno())
    try:
        os.link(tmp, path)
    finally:
        os.remove(tmp)
    return hashlib.sha256(body).hexdigest()


def stage_list(out_dir, fetch=None):
    fetch = fetch or get_json
    cutoff0 = (fetch("/historical/cutoff")[2] or {})
    seen, dups = set(), 0
    pages, rows_all, cursor, n = [], [], "", 0
    tot = {"input": 0, "no_settlement": 0, "outside_window": 0, "not_binary": 0, "open_lt_24h": 0, "kept": 0}
    # NOTE: not resumable by design. A crash leaves raw/ pages; wipe the output directory and rerun.
    while True:
        params = {"limit": 1000, "mve_filter": "exclude"}
        if cursor:
            params["cursor"] = cursor
        url, body, data = fetch("/historical/markets", params)
        if data is None or "markets" not in data:
            raise RuntimeError("unexpected historical markets response")
        h = save_once(f"{out_dir}/raw/markets_page_{n:05d}.json", body)
        pages.append({"url": url, "sha256": h, "bytes": len(body), "n": len(data["markets"]),
                      "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        page_rows, c = blind_filter(data["markets"])   # outcome fields never read; page is not retained in memory
        for r in page_rows:
            if r["ticker"] in seen:
                dups += 1
            else:
                seen.add(r["ticker"])
                rows_all.append(r)
        for k in tot:
            tot[k] += c[k]
        cursor = data.get("cursor") or ""
        n += 1
        if not cursor:
            break
    cutoff1 = (fetch("/historical/cutoff")[2] or {})
    if cutoff0 != cutoff1:
        raise RuntimeError(f"historical cutoff moved during listing: {cutoff0} -> {cutoff1}; wipe the directory and rerun")
    tot["duplicates_dropped"] = dups
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
        json.dump({"cutoff": cutoff0, "pages": pages, "counts": counts, "projected_hours": hours, "subsampled": subsampled,
                   "kept_after_subsample": len(rows)}, f, indent=1)
    return counts


def read_manifest_rows(out_dir):
    with open(f"{out_dir}/blinded_manifest.jsonl") as f:
        return [json.loads(l) for l in f if l.strip()]


def stage_candles(out_dir, fetch=None):
    """Resumable: existing files are validated (JSON parses, has `candlesticks`) and back-filled into
    the manifest if missing; a corrupt file is removed and refetched. Persistent non-429 errors are
    recorded as status=error and the stage continues."""
    fetch = fetch or get_json
    mpath = f"{out_dir}/candles_manifest.jsonl"
    recorded = set()
    if os.path.exists(mpath):
        with open(mpath) as f:
            recorded = {json.loads(l)["ticker"] for l in f if l.strip()}
    fetched = 0
    for r in read_manifest_rows(out_dir):
        t = r["ticker"]
        path = f"{out_dir}/raw/candles/{t}.json"
        if os.path.exists(path):
            with open(path, "rb") as f:
                body = f.read()
            try:
                ok = "candlesticks" in json.loads(body)
            except ValueError:
                ok = False
            if ok:
                if t not in recorded:
                    with open(mpath, "a") as f:
                        f.write(json.dumps({"ticker": t, "sha256": hashlib.sha256(body).hexdigest(), "status": "backfilled"}, sort_keys=True) + "\n")
                    recorded.add(t)
                continue
            os.remove(path)
        url, body, data = fetch(f"/historical/markets/{t}/candlesticks", candle_params(r["close_time"]), tolerate=True) if fetch is get_json else fetch(f"/historical/markets/{t}/candlesticks", candle_params(r["close_time"]))
        if data is None or "candlesticks" not in data:
            body, status = b'{"candlesticks": []}', "error_or_missing"
        else:
            status = "ok"
        h = save_once(path, body)
        with open(mpath, "a") as f:
            f.write(json.dumps({"ticker": t, "url": url, "sha256": h, "status": status,
                                "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, sort_keys=True) + "\n")
        recorded.add(t)
        fetched += 1
    return fetched


def stage_meta(out_dir, fetch=None):
    fetch = fetch or get_json
    rows = read_manifest_rows(out_dir)
    ev_series, cats, overrides = {}, {}, {}
    for e in sorted({r["event_ticker"] for r in rows}):
        url, body, data = fetch(f"/events/{e}")
        if data is None or "event" not in data or not data["event"].get("series_ticker"):
            ev_series[e] = None
        else:
            ev_series[e] = data["event"]["series_ticker"]
            ev = data["event"]
            if ev.get("fee_type_override") or ev.get("fee_multiplier_override"):
                overrides[e] = {"fee_type_override": ev.get("fee_type_override"),
                                "fee_multiplier_override": ev.get("fee_multiplier_override")}
            save_once(f"{out_dir}/raw/events/{e}.json", body)
    for ser in sorted({v for v in ev_series.values() if v}):
        url, body, data = fetch(f"/series/{ser}")
        if data is None or "series" not in data or "category" not in data["series"]:
            raise RuntimeError(f"series {ser} has no category field; F2 stops and the category rule is re-registered")
        cats[ser] = data["series"]["category"]
        save_once(f"{out_dir}/raw/series/{ser}.json", body)
    url, body, data = fetch("/series/fee_changes", {"show_historical": "true"})
    if data is None or "series_fee_change_arr" not in data:
        raise RuntimeError("unexpected fee_changes response")
    h = save_once(f"{out_dir}/raw/fee_changes.json", body)
    table = {"default_multiplier": 1.0, "series": {}}
    for it in data["series_fee_change_arr"]:
        table["series"].setdefault(it["series_ticker"], []).append([it["scheduled_ts"], it["fee_multiplier"], it["fee_type"]])
    for v in table["series"].values():
        v.sort(key=lambda x: x[0])
    for name, obj in (("event_series.json", ev_series), ("series_category.json", cats), ("fee_table.json", table),
                      ("event_overrides.json", overrides)):
        save_once(f"{out_dir}/{name}", json.dumps(obj, sort_keys=True).encode())
    return {"events": len(ev_series), "series": len(cats), "event_overrides": len(overrides), "fee_changes_sha256": h}


def stage_assemble(out_dir, analysis_dir):
    """Join full market objects (incl. `result`) for manifest tickers: the only stage that touches outcomes."""
    want = {r["ticker"] for r in read_manifest_rows(out_dir)}
    os.makedirs(f"{analysis_dir}/candles", exist_ok=True)
    n = 0
    with open(f"{analysis_dir}/markets.jsonl", "x") as out:
        for fn in sorted(os.listdir(f"{out_dir}/raw")):
            if not fn.startswith("markets_page_"):
                continue
            with open(f"{out_dir}/raw/{fn}") as f:
                for m in json.load(f)["markets"]:
                    if m["ticker"] in want:
                        out.write(json.dumps(m, sort_keys=True) + "\n")
                        n += 1
    for t in want:
        p = f"{out_dir}/raw/candles/{t}.json"
        if os.path.exists(p):
            with open(p, "rb") as src, open(f"{analysis_dir}/candles/{t}.json", "xb") as dst:
                dst.write(src.read())
    for name in ("event_series.json", "series_category.json", "fee_table.json", "event_overrides.json"):
        with open(f"{out_dir}/{name}", "rb") as src, open(f"{analysis_dir}/{name}", "xb") as dst:
            dst.write(src.read())
    return n


if __name__ == "__main__":
    stage = sys.argv[1]
    if stage == "list":
        print(json.dumps(stage_list(sys.argv[2])))
    elif stage == "candles":
        print(stage_candles(sys.argv[2]))
    elif stage == "meta":
        print(json.dumps(stage_meta(sys.argv[2])))
    elif stage == "assemble":
        print(stage_assemble(sys.argv[2], sys.argv[3]))
    else:
        raise SystemExit("unknown stage")
