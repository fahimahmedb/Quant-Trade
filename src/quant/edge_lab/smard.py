"""One calendar-only physical energy proxy; no adaptive dispatch or live orders.

SMARD data attribution: Bundesnetzagentur | SMARD.de, CC BY 4.0.
Public series are outcomes. Call capture only after durable reservation/RUNNING.
"""
import concurrent.futures
import base64
import hashlib
import json
import math
import statistics
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from .store import digest

BERLIN = ZoneInfo("Europe/Berlin")
HOUR_MS = 3600000
WINDOW = ["2024-12-31T23:00:00Z", "2025-12-31T23:00:00Z"]
MAX_FILES = 53
MAX_INPUT_BYTES = 250000
MAX_ROWS_PER_FILE = 200


class SourceError(ValueError):
    pass


def millis(value):
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)


def validate_manifest(manifest):
    files = manifest["files"]
    if (manifest["planned_window"] != WINDOW or manifest["series"] != "4169"
            or manifest["region"] != "DE" or manifest["resolution"] != "hour"
            or len(files) != MAX_FILES or sum(f["bytes"] for f in files) > MAX_INPUT_BYTES):
        raise SourceError("Unqualified full-window manifest")
    previous = None
    for f in files:
        expected = f'https://www.smard.de/app/chart_data/4169/DE/4169_DE_hour_{f["timestamp"]}.json'
        if (f["url"] != expected or f["status"] != 200 or not 0 < f["bytes"] < 10000
                or not f["etag"].startswith('"') or not f["etag"].endswith('"')
                or f.get("encoding") not in (None, "identity")
                or (previous is not None and not 6 * 86400000 < f["timestamp"] - previous < 8 * 86400000)):
            raise SourceError("Input URL/version/size/calendar bound invalid")
        previous = f["timestamp"]
    if not files[0]["timestamp"] <= millis(WINDOW[0]) < files[1]["timestamp"]:
        raise SourceError("Calendar start not covered")
    if not files[-1]["timestamp"] < millis(WINDOW[1]) < files[-1]["timestamp"] + 8 * 86400000:
        raise SourceError("Calendar end not covered")
    return files


def capture(manifest, directory, opener=urllib.request.urlopen):
    files = validate_manifest(manifest)
    directory = Path(directory)
    raw_path = directory / "inputs.jsonl"
    if raw_path.exists():
        raise SourceError("Prior capture exists; never reacquire this look")
    deadline = time.monotonic() + 95
    records = []
    def fetch(f):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise SourceError("Complete-window capture deadline")
        request = urllib.request.Request(f["url"], headers={"If-Match": f["etag"], "Accept-Encoding": "identity"})
        with opener(request, timeout=min(5, remaining)) as response:
            if (response.status != 200 or response.geturl() != f["url"]
                    or response.headers.get("ETag") != f["etag"]
                    or response.headers.get("Content-Encoding") not in (None, "identity")):
                raise SourceError("Source version changed; no replacement or retry")
            body = response.read(f["bytes"] + 1)
            record = {"url": f["url"], "etag": f["etag"], "bytes": len(body),
                      "sha256": hashlib.sha256(body).hexdigest(), "body_base64": base64.b64encode(body).decode("ascii")}
            # Preserve received bytes even when the announced size is wrong.
            record["size_valid"] = len(body) == f["bytes"]
            return record
    with raw_path.open("x") as output, concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(fetch, f) for f in files]
        try:
            for future in concurrent.futures.as_completed(futures, timeout=100):
                record = future.result()
                output.write(json.dumps(record, separators=(",", ":")) + "\n")
                output.flush()
                records.append(record)
                if not record["size_valid"] or time.monotonic() > deadline:
                    raise SourceError("Changed size or full-window deadline")
        except Exception:
            for future in futures:
                future.cancel()
            raise
    records.sort(key=lambda r: r["url"])
    summary = [{k: v for k, v in r.items() if k not in ("body", "body_base64")} for r in records]
    (directory / "input-manifest.json").write_text(json.dumps({"headers_fingerprint": digest(manifest),
        "exact_input_sha256": digest(summary), "files": summary, "attribution": "Bundesnetzagentur | SMARD.de (CC BY 4.0)"}, indent=2))
    return records, summary


def parse(records):
    quotes = {}
    duplicate_count = 0
    total_rows = 0
    for record in records:
        body = base64.b64decode(record["body_base64"], validate=True) if "body_base64" in record else record["body"]
        data = json.loads(body)
        series = data.get("series")
        if not isinstance(series, list) or not 1 <= len(series) <= MAX_ROWS_PER_FILE:
            raise SourceError("Series schema/row bound invalid")
        previous = None
        for pair in series:
            if not isinstance(pair, list) or len(pair) != 2:
                raise SourceError("Expected timestamp/value pair")
            stamp, price = pair
            total_rows += 1
            if (type(stamp) is not int or stamp % HOUR_MS or (previous is not None and stamp < previous)
                    or type(price) not in (int, float) or not math.isfinite(price)):
                raise SourceError("Missing/nonfinite price or invalid timestamp; no interpolation")
            previous = stamp
            if stamp in quotes:
                if quotes[stamp] != price:
                    raise SourceError("Conflicting same-time revision")
                duplicate_count += 1
            quotes[stamp] = float(price)
    start, end = map(millis, WINDOW)
    expected = set(range(start, end, HOUR_MS))
    if not expected <= set(quotes):
        raise SourceError("Full calendar has gaps; no dropping days or shortened window")
    return quotes, {"raw_rows": total_rows, "unique_hours_full_calendar": len(expected),
                    "duplicates_identical": duplicate_count,
                    "acquired_min_timestamp": min(quotes), "acquired_max_timestamp": max(quotes)}


def day_spreads(quotes):
    results = []
    day = datetime(2025, 1, 1)
    while day.year == 2025:
        buy = day.replace(hour=3, tzinfo=BERLIN)
        sell = day.replace(hour=18, tzinfo=BERLIN)
        b, s = int(buy.timestamp() * 1000), int(sell.timestamp() * 1000)
        # A fixed 1MWh input / 0.8MWh output schedule committed before the auction.
        results.append({"day": day.date().isoformat(), "buy_ms": b, "sell_ms": s,
                        "gross_eur_per_input_mwh": 0.8 * quotes[s] - quotes[b]})
        day += timedelta(days=1)
    return results


def mean_interval(values):
    """Descriptive 95% interval for daily mean, HAC lag 7, fixed before results.

    One year is not independent validation; normal approximation/seasonality limit it.
    """
    n = len(values)
    mean = statistics.fmean(values)
    residuals = [v - mean for v in values]
    variance = sum(x * x for x in residuals) / n
    for lag in range(1, 8):
        variance += 2 * (1 - lag / 8) * sum(residuals[i] * residuals[i-lag] for i in range(lag, n)) / n
    half = 1.96 * math.sqrt(max(variance, 0) / n)
    return [mean - half, mean + half]


def calculate(quotes):
    days = day_spreads(quotes)
    gross = [d["gross_eur_per_input_mwh"] for d in days]
    paths = {}
    for name, cost in (("central", 100.0), ("stress", 150.0)):
        values = [v - cost for v in gross]
        paths[name] = {"all_in_assumed_eur_per_input_mwh": cost, "mean_net_eur_per_input_mwh": statistics.fmean(values),
            "annual_net_eur_per_1mwh_device": sum(values), "daily_mean_hac7_95pct_interval": mean_interval(values),
            "worst_day_eur": min(values), "negative_days": sum(v < 0 for v in values)}
    if paths["central"]["daily_mean_hac7_95pct_interval"][1] < 0:
        kind = "NEGATIVE"
    elif paths["stress"]["daily_mean_hac7_95pct_interval"][0] > 0:
        kind = "POSITIVE_EXPLORATORY"
    else:
        kind = "INSUFFICIENT_POWER"
    return kind, paths, {"mean_gross_break_even_all_in_cost_eur_per_input_mwh": statistics.fmean(gross),
                         "gross_mean_hac7_95pct_interval": mean_interval(gross)}, days


def run(root, protocol_id, look_id):
    state = json.loads((root / "research/edge_lab/STATE.json").read_text())
    p, look = state["protocols"][protocol_id], state["looks"][look_id]
    if (look["status"] != "RUNNING_SPENT" or p["window"] != WINDOW
            or p["design"] != {"charge_local_hour":3,"discharge_local_hour":18,"input_mwh":1,
                               "round_trip_efficiency":0.8,"central_all_in_eur":100,"stress_all_in_eur":150}):
        raise ValueError("Exact frozen schedule and RUNNING reservation required")
    directory = root / "research/edge_lab/receipts" / digest(look_id)
    manifest = json.loads((root / p["input_manifest"]).read_text())
    if digest(manifest) != look["data_fingerprint"]:
        raise ValueError("Input version differs from admission")
    observations = {"days":0,"independent_unit":"calendar day; serial dependence retained"}
    paths = {name:{"net":None,"reason":"source not acquired/QA incomplete"} for name in p["cost_paths"]}
    effect = None
    try:
        records, hashes = capture(manifest, directory)
        quotes, qa = parse(records)
        kind, paths, effect, days = calculate(quotes)
        observations.update(days=len(days),source_qa=qa,input_files=hashes)
        nature = "EXPLORATORY_BACKTEST"
        failed = ["Authentic dispatch/plant/counterparty/tariffs unavailable; proxy only",
                  "Private history UNKNOWN; one-year historical normal/HAC interval is descriptive"]
        lesson = ("Fixed calendar storage must pay efficiency loss and asset cost; preserve exact costed result and break-even cost. "
                  "No dispatch-hour replacement, grid search or profit claim for another asset/market.")
    except (SourceError, KeyError, ValueError, OSError, TimeoutError) as exc:
        kind, nature = "SOURCE_UNUSABLE", "SOURCE_FAILURE"
        failed = [type(exc).__name__ + ": " + str(exc)[:180]]
        lesson = "Source capture/complete-calendar QA failed; not an economic rejection; reserved exposure remains spent."
    status = {"NEGATIVE":"REJECTED_EXACT_PROXY_POLICY", "POSITIVE_EXPLORATORY":"VALIDATION_REQUIRED_PROXY_ONLY",
              "INSUFFICIENT_POWER":"INCONCLUSIVE_WAIT", "SOURCE_UNUSABLE":"BLOCKED_DATA_ACCESS"}[kind]
    next_action = ("Close this exact fixed policy; no alternative-hour winner or automatic rerun."
                   if kind == "NEGATIVE" else "Qualify distinct physical/execution evidence before any further look; no automatic rerun.")
    uncertainty = {"method":"normal 95% daily-mean Newey-West/Bartlett HAC with lag7 fixed before results",
                   "intervals":{k:v.get("daily_mean_hac7_95pct_interval") for k,v in paths.items()},
                   "limits":"One calendar year; seasonality, tail risk, publication revisions, private exposure UNKNOWN; not confirmation."}
    verdict = {"RESULT":kind,"EFFECT_SIZE":effect if effect else "NOT_ESTIMABLE_SOURCE_FAILURE",
        "UNCERTAINTY":uncertainty,"POWER_LIMITATION":"365 scheduled days, not365 independent experiments; one year, unobserved tail/regime history",
        "ECONOMIC_SIGNIFICANCE":"EUR/input-MWh under explicit assumed100/150EUR all-in costs; hourly auction average proxy, no executable quote/plant eligibility proved",
        "FAILED_CRITERIA":failed,"LESSON":lesson,"FAMILY_STATUS":status,"NEXT_DECISION":next_action}
    return {"look_id":look_id,"kind":kind,"nature":nature,"protocol_hash":p["hash"],
        "data_fingerprint":look["data_fingerprint"],"primary":p["primary"],"benchmark":"no device/no order, incremental PnL0",
        "observations":observations,"net_after_costs":paths,"expression_results":{p["primary"]:paths},
        "uncertainty":uncertainty,"risk_exposures":{"capacity":"1MW input,1MWh energy,0.8MWh output,one cycle/day",
        "risk":"15h holding, auction price tails/failed physical dispatch/credit/grid fees not established; costs explicitly hypothetical"},
        "capacity":"Only1MWh proxy; no scaling/market impact or live claim", "lesson":lesson,"next_decision":next_action,
        "verdict":verdict,"attribution":"Bundesnetzagentur | SMARD.de, CC BY4.0"}
