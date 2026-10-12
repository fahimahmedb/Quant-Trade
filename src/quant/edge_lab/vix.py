"""Frozen 2013–2021 quarterly VX settlement expression; call only after durable CAS.

Raw Cboe payloads and acquisition receipts stay private. No Quant runtime boots here.
"""
import csv
import hashlib
import io
import json
import math
import os
import random
import re
import signal
import statistics
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

EXPERIMENT = "disc-cfe-vix-term-premium-l1-v1"
DESIGN = {"entry_days":45, "exit_days":15, "endpoint_tolerance_days":4,
          "central_cost_points":0.10, "stress_cost_points":0.25,
          "multiplier_usd_per_point":1000, "bootstrap_draws":2000, "bootstrap_seed":41011}
MAX_FILE, MAX_TOTAL, MAX_JOB = 262144, 2 * 1024 * 1024, 120
METADATA_RESERVE = 262144
EXPIRIES = (
    "2013-03-20 2013-06-19 2013-09-18 2013-12-18 "
    "2014-03-18 2014-06-18 2014-09-17 2014-12-17 "
    "2015-03-18 2015-06-17 2015-09-16 2015-12-16 "
    "2016-03-16 2016-06-15 2016-09-21 2016-12-21 "
    "2017-03-22 2017-06-21 2017-09-20 2017-12-20 "
    "2018-03-21 2018-06-20 2018-09-19 2018-12-19 "
    "2019-03-19 2019-06-19 2019-09-18 2019-12-18 "
    "2020-03-18 2020-06-17 2020-09-16 2020-12-16 "
    "2021-03-17 2021-06-16 2021-09-15 2021-12-22"
).split()
NAMES = [f"{q}{year}" for year in range(2013, 2022) for q in "HMUZ"]


class SourceError(ValueError):
    pass


class _JobDeadline(BaseException):
    pass


def validate_manifest(manifest, contract):
    files = manifest["files"]
    if (manifest["experiment_id"] != EXPERIMENT or contract.get("claim_ceiling") != "PROMOTE_EXPRESSION"
            or contract.get("experiment_id", EXPERIMENT) != EXPERIMENT
            or contract.get("design") != DESIGN or len(files) != 36
            or [f["contract"] for f in files] != NAMES):
        raise SourceError("Frozen expression, source order or complete population changed")
    for f, expiry in zip(files, EXPIRIES):
        d = date.fromisoformat(expiry)
        url = (f'https://cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_{f["contract"][0]}13_VX.csv'
               if d.year == 2013 else
               f'https://cdn.cboe.com/data/us/futures/market_statistics/historical_data/VX/VX_{expiry}.csv')
        if (f["expiry"] != expiry or f["entry_target"] != (d-timedelta(days=45)).isoformat()
                or f["exit_target"] != (d-timedelta(days=15)).isoformat() or f["url"] != url
                or type(f["payload_bytes"]) is not int or not 0 < f["payload_bytes"] < MAX_FILE
                or not re.fullmatch(r"[0-9a-f]{64}", f["sha256"])
                or f.get("prior_status", 200) != 200):
            raise SourceError("Pinned successful source, version, size or calendar changed")
    if (sum(f["payload_bytes"] for f in files) > MAX_TOTAL-METADATA_RESERVE
            or len(json.dumps(manifest).encode())+len(json.dumps(contract).encode()) > 32768):
        raise SourceError("Complete input exceeds total byte ceiling")
    return files


def _verified(f, body):
    if (not isinstance(body, bytes) or len(body) != f["payload_bytes"]
            or hashlib.sha256(body).hexdigest() != f["sha256"]):
        raise SourceError("Pinned payload size or SHA256 mismatch")


def _endpoints(f, body):
    reader = csv.DictReader(io.StringIO(body.decode("utf-8-sig")), strict=True)
    if (not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames))
            or not {"Trade Date", "Settle"} <= set(reader.fieldnames)):
        raise SourceError("Required CSV date/settlement schema missing or ambiguous")
    rows, previous, direction = [], None, None
    for row in reader:
        if None in row or any(v is None for v in row.values()):
            raise SourceError("Malformed or missing CSV fields")
        try:
            text = row["Trade Date"].strip()
            d = date.fromisoformat(text) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text) else datetime.strptime(text, "%m/%d/%Y").date()
            value = Decimal(row["Settle"].strip())
            valid = value.is_finite() and value >= 0 and math.isfinite(float(value))
        except (ValueError, ArithmeticError):
            raise SourceError("Invalid date or settlement number") from None
        step = None if previous is None else (1 if d > previous else -1)
        if not valid or d == previous or (direction is not None and step != direction):
            raise SourceError("Nonfinite/negative settlement, duplicate date or source order failure")
        if previous is not None:
            direction = step
        previous = d
        rows.append((d, value))
    if direction == -1:
        rows.reverse()  # Presentation order never changes chronological endpoint selection.
    selected = []
    for key in ("entry_target", "exit_target"):
        target = date.fromisoformat(f[key])
        endpoint = next(((d, v) for d, v in rows if d >= target and v > 0), None)
        if endpoint is None or (endpoint[0]-target).days > 4:
            raise SourceError("Missing positive endpoint within fixed four-day tolerance")
        selected.append(endpoint)
    if selected[0][0] >= selected[1][0]:
        raise SourceError("Entry must precede exit")
    return selected


def _park(reason):
    return {"experiment_id":EXPERIMENT, "label":"EXPLORATORY", "decision":"PARK_DATA",
            "typed_verdict":"PARK_DATA", "economics_computed":False, "failed_criteria":[reason],
            "adequacy_passed":False, "red_team":{"executed":False, "passed":False},
            "claim_ceiling":"PROMOTE_EXPRESSION", "prior_exposures":"PRIVATE_UNKNOWN"}


def _summary(values):
    cumulative = peak = Decimal(0)
    drawdown = Decimal(0)
    for value in values:
        cumulative += value
        peak = max(peak, cumulative)
        drawdown = min(drawdown, cumulative-peak)
    totals = {str(y):sum(values[(y-2013)*4:(y-2012)*4]) for y in range(2013, 2022)}
    numbers = {"mean":sum(values)/36, "median":statistics.median(values),
               "worst_trade":min(values), "endpoint_drawdown":drawdown}
    return {**{k+"_points":float(v) for k, v in numbers.items()},
            **{k+"_usd":float(v*1000) for k, v in numbers.items()},
            "year_totals_points":{y:float(v) for y,v in totals.items()},
            "year_totals_usd":{y:float(v*1000) for y,v in totals.items()}}


def calculate(manifest, raw_by_contract, contract):
    """Pure complete-population calculation; failures have no partial economics."""
    try:
        files = validate_manifest(manifest, contract)
        if set(raw_by_contract) != set(NAMES):
            raise SourceError("All and only 36 frozen raw contracts required")
        for f in files:
            _verified(f, raw_by_contract[f["contract"]])
        gross, trades, last_exit = [], [], None
        for f in files:
            (entry, buy), (exit_, cover) = _endpoints(f, raw_by_contract[f["contract"]])
            if last_exit is not None and entry <= last_exit:
                raise SourceError("Overlapping constant-contract exposures")
            last_exit = exit_
            value = buy-cover
            gross.append(value)
            trades.append({"contract":f["contract"], "entry_date":entry.isoformat(), "exit_date":exit_.isoformat(),
                "gross_points":float(value), "gross_usd":float(value*1000),
                "central_net_points":float(value-Decimal(".10")), "stress_net_points":float(value-Decimal(".25"))})
        central, stress = [[v-cost for v in gross] for cost in (Decimal(".10"), Decimal(".25"))]
        mean = lambda xs:sum(xs)/len(xs)
        blocks = {"2013-2018":mean(central[:24]), "2019-2021":mean(central[24:])}
        decision = ("KILL_EXPRESSION" if mean(gross) <= 0 or mean(stress) <= 0 else
                    "PROMOTE_EXPRESSION" if mean(central) >= Decimal(".25") and all(v > 0 for v in blocks.values()) else
                    "PARK_ECONOMICS")
        primary, adversary = decision, {"executed":False, "passed":False}
        if primary == "PROMOTE_EXPRESSION":
            best = max(range(9), key=lambda y:sum(central[y*4:y*4+4]))
            rest = [v for i,v in enumerate(gross) if i//4 != best]
            surviving = {name:mean([v-cost for v in rest]) for name,cost in
                         (("central",Decimal(".10")), ("stress",Decimal(".25")))}
            passed = all(v > 0 for v in surviving.values())
            adversary = {"executed":True, "test":"remove_highest_central_net_calendar_year",
                         "removed_year":2013+best, "remaining_trades":32, "passed":passed,
                         "remaining_mean_net_points":{k:float(v) for k,v in surviving.items()}}
            if not passed:
                decision = "PARK_ECONOMICS"
        rng = random.Random(41011)
        totals = [sum(gross[y*4:y*4+4]) for y in range(9)]
        draws = sorted(float(sum(rng.choice(totals) for _ in range(9))/36) for _ in range(2000))
        def quantile(p):
            index = (len(draws)-1)*p
            lower = int(index)
            return draws[lower]+(draws[min(lower+1, len(draws)-1)]-draws[lower])*(index-lower)
        interval = [quantile(.025), quantile(.975)]
        result = {"experiment_id":EXPERIMENT, "label":"EXPLORATORY", "decision":decision,
            "typed_verdict":decision, "primary_decision":primary, "economics_computed":True,
            "adequacy_passed":True, "red_team":adversary,
            "claim_ceiling":"PROMOTE_EXPRESSION", "observations":{"trades":36, "calendar_year_clusters":9},
            "trades":trades, "summary":{name:_summary(values) for name,values in
                (("gross",gross), ("central",central), ("stress",stress))},
            "fixed_block_central_mean_points":{k:float(v) for k,v in blocks.items()}, "adversary":adversary,
            "uncertainty":{"method":"Descriptive calendar-year-cluster bootstrap", "draws":2000, "seed":41011,
                "confidence_level":.95, "gross_mean_points_interval":interval, "statistical_confirmation":False},
            "unit_economics":{"break_even_friction_points":float(mean(gross)),
                "break_even_friction_usd":float(mean(gross)*1000), "frequency_per_year":4,
                "central_round_trip_cost_points":.10, "stress_round_trip_cost_points":.25,
                "central_round_trip_cost_usd":100, "stress_round_trip_cost_usd":250, "multiplier_usd_per_point":1000},
            "prior_exposures":{"private":"PRIVATE_UNKNOWN", "old_acquired_files":36, "prior_access_attempt":"KNOWN", "effective_trials":"UNKNOWN"},
            "limits":{"scope":"2013–2021 costed quarterly settlement expression only", "margin":"UNKNOWN",
                "intratrade_detail":"UNKNOWN", "current_2022_2026":"UNKNOWN", "settlements_are_fills":False,
                "risk_premium_attribution":"UNKNOWN", "capital_denominator":"ABSENT"}}
        json.dumps(result, allow_nan=False)  # Derived USD/totals must also remain finite.
        return result
    except (SourceError, KeyError, TypeError, ValueError, ArithmeticError, csv.Error, UnicodeError) as exc:
        return _park(str(exc) if isinstance(exc, SourceError) else "Invalid frozen source or input schema")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


@contextmanager
def _budget(seconds, job=False):
    def expired(*_):
        if job or (old and old <= seconds):
            raise _JobDeadline()
        raise SourceError("Acquisition/job wall deadline; no retry")
    old, interval = signal.getitimer(signal.ITIMER_REAL)
    previous = signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, min(seconds, old) if old else seconds)
    started = time.monotonic()
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
        remaining = old-(time.monotonic()-started)
        if old and remaining > 0:
            signal.setitimer(signal.ITIMER_REAL, remaining, interval)


def _private(path, data):
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as out:
        out.write(data)


def _run(manifest, contract, cache_dir):
    """Sequential pinned acquisition, bounded locally; caller owns reservation/CAS."""
    started, total, receipts, raw = time.monotonic(), 0, [], {}
    result_path = None
    try:
        files = validate_manifest(manifest, contract)
        directory = Path(cache_dir)
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(directory, 0o700)
        result_path = directory/(EXPERIMENT+".result.json")
        fingerprint = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
        if result_path.exists():
            saved = json.loads(result_path.read_text())
            if saved.get("manifest_sha256") != fingerprint:
                raise SourceError("Prior durable result binds a different source version")
            return saved
        opener = urllib.request.build_opener(_NoRedirect())
        for f in files:
            name = f["contract"]
            path, intent, receipt = [directory/(name+s) for s in (".csv", ".intent.json", ".receipt.json")]
            remaining = MAX_JOB-(time.monotonic()-started)
            if remaining <= 0:
                raise SourceError("Whole-job wall ceiling")
            if path.exists():
                if intent.exists() or receipt.exists():
                    if not receipt.exists():
                        raise SourceError("Prior intent has no completed receipt; no retry")
                    prior = json.loads(receipt.read_text())
                    if prior.get("error") is not None or prior.get("status") != 200:
                        raise SourceError("Prior failed receipt cannot be reused; no retry")
                with path.open("rb") as cached:
                    body = cached.read(MAX_FILE)
                total += len(body)
                _verified(f, body)
                record = {"contract":name, "reused":True, "payload_bytes":len(body), "sha256":f["sha256"]}
            else:
                if intent.exists() or receipt.exists():
                    raise SourceError("Prior attempt lacks complete pinned cache; no retry")
                _private(intent, json.dumps({**f, "experiment_id":EXPERIMENT, "retries":0}).encode())
                body, record = b"", {"contract":name, "url":f["url"], "status":None, "reused":False, "error":None}
                _private(path, b"")
                job_expired = False
                try:
                    with _budget(min(15, remaining)):
                        request = urllib.request.Request(f["url"], headers={"User-Agent":"QuantTrade personal research", "Accept-Encoding":"identity"})
                        with opener.open(request, timeout=min(15, remaining)) as response:
                            record["status"] = response.status
                            if (response.status != 200 or response.geturl() != f["url"]
                                    or response.headers.get("Content-Encoding") not in (None, "identity")):
                                raise SourceError("Non-200, redirect or encoded source; no retry")
                            while len(body) <= f["payload_bytes"]:
                                chunk = response.read(min(32768, f["payload_bytes"]+1-len(body)))
                                if not chunk:
                                    break
                                body += chunk
                                with path.open("ab") as partial:
                                    partial.write(chunk)
                            _verified(f, body)
                            _endpoints(f, body)
                            record["qa_passed"] = True
                except _JobDeadline:
                    job_expired = True
                    raise
                except Exception as exc:
                    if isinstance(exc, urllib.error.HTTPError):
                        record["status"] = exc.code
                    record["error"] = str(exc) if isinstance(exc, SourceError) else type(exc).__name__
                    raise SourceError(record["error"]) from None
                finally:
                    if not job_expired:
                        record.update(payload_bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
                        _private(receipt, json.dumps(record).encode())
                        receipts.append(record)
                        total += len(body)
            if total > MAX_TOTAL:
                raise SourceError("Total byte ceiling")
            _endpoints(f, body)  # Source QA only; stop before acquiring another bad file.
            raw[name] = body
            if record["reused"]:
                receipts.append(record)
        remaining = MAX_JOB-(time.monotonic()-started)
        if remaining <= 0:
            raise SourceError("Whole-job wall ceiling")
        with _budget(remaining):
            result = calculate(manifest, raw, contract)
    except (SourceError, KeyError, TypeError, ValueError, ArithmeticError, csv.Error, UnicodeError, OSError) as exc:
        result = _park(str(exc) if isinstance(exc, SourceError) else "Frozen source acquisition failed")
    result["acquisition"] = {"receipts":receipts, "payload_bytes":total,
                             "paid_usd":0, "wall_seconds":time.monotonic()-started, "raw_cache_private":True}
    if result_path is not None and not result_path.exists():
        result["manifest_sha256"] = fingerprint
        encoded = json.dumps(result, allow_nan=False).encode()
        if len(encoded) > 65536:
            return _park("Private result exceeds metadata reserve")
        try:
            _private(result_path, encoded)
        except OSError:
            return _park("Private result persistence failed")
    return result


def run(manifest, contract, cache_dir):
    """Hard whole-job ceiling includes cache IO, source QA and private persistence."""
    try:
        with _budget(MAX_JOB, job=True):
            return _run(manifest, contract, cache_dir)
    except (_JobDeadline, SourceError, ValueError, OSError):
        return _park("Whole-job deadline or local execution environment failure")
