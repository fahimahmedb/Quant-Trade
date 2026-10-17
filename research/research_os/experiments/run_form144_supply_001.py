#!/usr/bin/env python3
"""Single-use bounded historical economic look for QUANT-FORM144-SUPPLY-001:G1.

The economic parameters are read from the already-frozen protocol JSON. This runner
does not tune thresholds/horizons, does not place orders, and never enables live trading.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_PATH = ROOT / "research/research_os/experiments/FORM144_SUPPLY_001_PROTOCOL.json"
USER_AGENT = "Quant-Trade-research/1.0 fahimahmedb@users.noreply.github.com"
SEC_MIN_INTERVAL = 0.12
_last_sec_request = 0.0

DERA_345 = (
    "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/2023q4_form345.zip",
    "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/2024q1_form345.zip",
)

BAD_SECURITY_TOKENS = ("PREFERRED", " ADR", "ADS", " UNIT", "OPTION", "NOTE", "BOND", "DEBT", "WARRANT", "TRUST")
SIMPLE_TICKER = re.compile(r"^[A-Z]{1,5}$")


class SourceError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _request(url: str, *, sec: bool = False, attempts: int = 3, timeout: int = 45) -> bytes:
    global _last_sec_request
    headers = {"User-Agent": USER_AGENT, "Accept-Encoding": "identity", "Accept": "*/*"}
    for attempt in range(attempts):
        if sec:
            delay = SEC_MIN_INTERVAL - (time.monotonic() - _last_sec_request)
            if delay > 0:
                time.sleep(delay)
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = response.read()
            if sec:
                _last_sec_request = time.monotonic()
            return data
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            if sec:
                _last_sec_request = time.monotonic()
            if attempt + 1 == attempts:
                raise SourceError(f"GET failed after {attempts} attempts: {url}: {type(exc).__name__}") from exc
            time.sleep(1.5 * (attempt + 1))
    raise AssertionError("unreachable")


def sec_get(url: str) -> bytes:
    return _request(url, sec=("sec.gov" in urllib.parse.urlsplit(url).netloc))


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def first_text(node: ET.Element, names: tuple[str, ...]) -> str | None:
    wanted = {x.lower() for x in names}
    for elem in node.iter():
        if local(elem.tag).lower() in wanted and elem.text and elem.text.strip():
            return elem.text.strip()
    return None


def as_float(value: str | None) -> float | None:
    if value is None:
        return None
    clean = re.sub(r"[^0-9eE+.\-]", "", value)
    if clean in ("", ".", "-", "+"):
        return None
    try:
        return float(clean)
    except ValueError:
        return None


def extract_xml(submission_text: str) -> str | None:
    match = re.search(r"(<\?xml\b.*?</edgarSubmission>)", submission_text, re.I | re.S)
    return match.group(1) if match else None


def acceptance_local(submission_text: str, fallback_date: str) -> str:
    for pattern in (r"<ACCEPTANCE-DATETIME>\s*(\d{14})", r"ACCEPTANCE-DATETIME:\s*(\d{14})"):
        match = re.search(pattern, submission_text, re.I)
        if match:
            raw = match.group(1)
            return f"{raw[0:4]}-{raw[4:6]}-{raw[6:8]}T{raw[8:10]}:{raw[10:12]}:{raw[12:14]}"
    return fallback_date + "T23:59:59"


def accession_from_filename(filename: str) -> str:
    stem = Path(filename).name
    return stem[:-4] if stem.endswith(".txt") else stem


def parse_form144(xml_text: str, accession: str, filing_date: str, accepted_local: str) -> dict[str, Any] | None:
    root = ET.fromstring(xml_text)
    issuer_cik = first_text(root, ("issuerCik",))
    seller_cik = None
    for creds in root.iter():
        if local(creds.tag).lower() == "filercredentials":
            seller_cik = first_text(creds, ("cik",))
            break
    if not issuer_cik or not seller_cik:
        return None

    eligible_rows: list[dict[str, Any]] = []
    for block in root.iter():
        if local(block.tag).lower() != "securitiesinformation":
            continue
        title = first_text(block, ("securitiesClassTitle",)) or ""
        upper = " " + title.upper() + " "
        if "COMMON" not in upper or any(token in upper for token in BAD_SECURITY_TOKENS):
            continue
        proposed = as_float(first_text(block, ("noOfUnitsSold", "unitsToBeSold", "numberOfUnitsToBeSold")))
        outstanding = as_float(first_text(block, ("noOfUnitsOutstanding", "unitsOutstanding")))
        market_value = as_float(first_text(block, ("aggregateMarketValue",)))
        exchange = (first_text(block, ("securitiesExchangeName",)) or "").strip().upper()
        if proposed is None or outstanding is None or proposed <= 0 or outstanding <= 0:
            continue
        eligible_rows.append({
            "title": title.strip(), "proposed_shares": proposed, "shares_outstanding": outstanding,
            "aggregate_market_value": market_value, "exchange": exchange,
            "approx_sale_date": first_text(block, ("approxSaleDate",)),
        })
    if len(eligible_rows) != 1:
        return None
    row = eligible_rows[0]
    row.update({
        "accession": accession, "filing_date": filing_date, "accepted_local": accepted_local,
        "issuer_cik": issuer_cik.zfill(10), "seller_cik": seller_cik.zfill(10),
        "signal_ratio": row["proposed_shares"] / row["shares_outstanding"],
    })
    return row


def parse_master_index(text: str, start_date: str, end_date: str, excluded: set[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        if "|" not in line:
            continue
        parts = line.split("|")
        if len(parts) != 5:
            continue
        _, form, _, filed, filename = [x.strip() for x in parts]
        if form != "144" or not (start_date <= filed < end_date):
            continue
        accession = accession_from_filename(filename)
        if accession in excluded:
            continue
        rows.append({"filing_date": filed, "filename": filename, "accession": accession})
    return rows


def archive_url(filename: str) -> str:
    return "https://www.sec.gov/Archives/" + filename.lstrip("/")


def get_documentary_events(protocol: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    start = protocol["sample"]["event_window_utc_half_open"][0][:10]
    end = protocol["sample"]["event_window_utc_half_open"][1][:10]
    excluded = set(protocol["sample"]["excluded_accessions"])
    index_url = protocol["source_contract"]["event_index_url"]
    index_bytes = sec_get(index_url)
    index_rows = parse_master_index(index_bytes.decode("latin-1", errors="replace"), start, end, excluded)
    counters = {"index_form144_rows": len(index_rows), "submission_fetch_errors": 0,
                "xml_parse_or_schema_exclusions": 0, "exchange_exclusions": 0, "below_signal_threshold": 0}
    allow_exchanges = {x.upper() for x in protocol["sample"]["issuer_exchange_allowlist"]}
    threshold = float(protocol["sample"]["signal_threshold"])
    events: list[dict[str, Any]] = []
    selected_source_hashes: dict[str, str] = {}

    for item in index_rows:
        try:
            raw = sec_get(archive_url(item["filename"]))
        except SourceError:
            counters["submission_fetch_errors"] += 1
            continue
        text = raw.decode("utf-8", errors="replace")
        xml_text = extract_xml(text)
        if xml_text is None:
            directory = item["filename"].rsplit("/", 1)[0]
            try:
                xml_raw = sec_get(f"https://www.sec.gov/Archives/{directory}/primary_doc.xml")
                xml_text = xml_raw.decode("utf-8", errors="replace")
            except SourceError:
                counters["xml_parse_or_schema_exclusions"] += 1
                continue
        try:
            event = parse_form144(xml_text, item["accession"], item["filing_date"], acceptance_local(text, item["filing_date"]))
        except (ET.ParseError, ValueError):
            event = None
        if event is None:
            counters["xml_parse_or_schema_exclusions"] += 1
            continue
        if event["exchange"] not in allow_exchanges:
            counters["exchange_exclusions"] += 1
            continue
        if event["signal_ratio"] < threshold:
            counters["below_signal_threshold"] += 1
            continue
        selected_source_hashes[event["accession"]] = sha256_bytes(raw)
        events.append(event)

    events.sort(key=lambda x: (x["filing_date"], x["accepted_local"], x["accession"]))
    lineage: dict[tuple[str, str], datetime] = {}
    deduped: list[dict[str, Any]] = []
    lineage_exclusions = 0
    for event in events:
        key = (event["issuer_cik"], event["seller_cik"])
        day = datetime.strptime(event["filing_date"], "%Y-%m-%d")
        prior = lineage.get(key)
        if prior is not None and (day - prior).days < 30:
            lineage_exclusions += 1
            continue
        lineage[key] = day
        deduped.append(event)

    counters["signal_events_before_lineage_dedup"] = len(events)
    counters["lineage_exclusions"] = lineage_exclusions
    counters["lineage_events"] = len(deduped)
    provenance = {"master_index_url": index_url, "master_index_sha256": sha256_bytes(index_bytes),
                  "selected_submission_sha256": selected_source_hashes, "counters": counters}
    return deduped, provenance


def parse_sec_date(value: str) -> datetime:
    value = value.strip()
    for fmt in ("%d-%b-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    raise ValueError(value)


def load_pit_ticker_history(event_start_date: str) -> tuple[dict[str, list[tuple[datetime, str]]], dict[str, str]]:
    history: dict[str, list[tuple[datetime, str]]] = {}
    hashes: dict[str, str] = {}
    cutoff = datetime.strptime(event_start_date, "%Y-%m-%d")
    for url in DERA_345:
        data = sec_get(url)
        hashes[url] = sha256_bytes(data)
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            submission_name = next((n for n in zf.namelist() if n.lower().endswith("submission.tsv")), None)
            if submission_name is None:
                raise SourceError(f"SUBMISSION.tsv missing from {url}")
            with zf.open(submission_name) as raw:
                reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace"), delimiter="\t")
                for row in reader:
                    if (row.get("DOCUMENT_TYPE") or "").strip().upper() not in {"4", "4/A"}:
                        continue
                    cik = (row.get("ISSUERCIK") or "").strip().zfill(10)
                    ticker = (row.get("ISSUERTRADINGSYMBOL") or "").strip().upper()
                    filing = (row.get("FILING_DATE") or "").strip()
                    if not cik or not ticker or not filing or not SIMPLE_TICKER.fullmatch(ticker):
                        continue
                    try:
                        dt = parse_sec_date(filing)
                    except ValueError:
                        continue
                    if dt <= cutoff + timedelta(days=100):
                        history.setdefault(cik, []).append((dt, ticker))
    for values in history.values():
        values.sort()
    return history, hashes


def pit_ticker(history: dict[str, list[tuple[datetime, str]]], issuer_cik: str, event_date: str) -> str | None:
    event_day = datetime.strptime(event_date, "%Y-%m-%d")
    prior = [item for item in history.get(issuer_cik, []) if item[0] < event_day]
    return max(prior, key=lambda x: x[0])[1] if prior else None


def stooq_symbol(ticker: str) -> str:
    return ticker.lower() + ".us"


def get_stooq_daily(ticker: str, d1: str, d2: str) -> list[dict[str, Any]]:
    symbol = stooq_symbol(ticker) if ticker != "SPY" else "spy.us"
    url = "https://stooq.com/q/d/l/?" + urllib.parse.urlencode({"s": symbol, "d1": d1.replace("-", ""), "d2": d2.replace("-", ""), "i": "d"})
    raw = _request(url, sec=False, attempts=3, timeout=30)
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig", errors="replace")))
    rows: list[dict[str, Any]] = []
    for row in reader:
        try:
            day = datetime.strptime(row["Date"], "%Y-%m-%d")
            op, close, volume = float(row["Open"]), float(row["Close"]), float(row["Volume"])
        except (KeyError, TypeError, ValueError):
            continue
        if op > 0 and close > 0 and volume >= 0:
            rows.append({"date": day, "open": op, "close": close, "volume": volume})
    rows.sort(key=lambda x: x["date"])
    if not rows:
        raise SourceError(f"No Stooq daily data for {ticker}")
    return rows


def event_return(event: dict[str, Any], stock_rows: list[dict[str, Any]], spy_by_date: dict[datetime, dict[str, Any]], protocol: dict[str, Any]) -> dict[str, Any] | None:
    event_day = datetime.strptime(event["filing_date"], "%Y-%m-%d")
    pre = [r for r in stock_rows if r["date"] < event_day]
    lookback = int(protocol["sample"]["pre_event_market_filters"]["adv_lookback_sessions"])
    if len(pre) < lookback:
        return None
    pre20 = pre[-lookback:]
    pre_close = pre20[-1]["close"]
    adv = statistics.mean(r["close"] * r["volume"] for r in pre20)
    filters = protocol["sample"]["pre_event_market_filters"]
    if pre_close < float(filters["price_floor_usd"]) or adv < float(filters["minimum_average_daily_dollar_volume_usd"]):
        return {"eligible_market_filter": False, "pre_close": pre_close, "adv_usd": adv}
    post = [r for r in stock_rows if r["date"] > event_day]
    if len(post) < 5:
        return None
    entry, exit_row = post[0], post[4]
    spy_entry, spy_exit = spy_by_date.get(entry["date"]), spy_by_date.get(exit_row["date"])
    if not spy_entry or not spy_exit:
        return None
    stock_ret = exit_row["close"] / entry["open"] - 1.0
    spy_ret = spy_exit["close"] / spy_entry["open"] - 1.0
    gross_short_excess = -(stock_ret - spy_ret)
    cost = float(protocol["economic_expression"]["round_trip_cost_bps"]) / 10000.0
    return {"eligible_market_filter": True, "entry_date": entry["date"].strftime("%Y-%m-%d"),
            "exit_date": exit_row["date"].strftime("%Y-%m-%d"), "pre_close": pre_close, "adv_usd": adv,
            "stock_return": stock_ret, "benchmark_return": spy_ret,
            "gross_short_excess_return": gross_short_excess, "net_short_excess_return": gross_short_excess - cost}


def classify(protocol: dict[str, Any], documentary_n: int, mapped_market_n: int, returns: list[dict[str, Any]]) -> tuple[str, str]:
    coverage_floor = float(protocol["source_contract"]["minimum_pit_symbol_and_market_coverage"])
    coverage = mapped_market_n / documentary_n if documentary_n else 0.0
    if documentary_n == 0 or coverage < coverage_floor:
        return "SOURCE_UNUSABLE", f"PIT ticker+market coverage {coverage:.3f} below {coverage_floor:.3f} or no documentary signal events."
    n = len(returns)
    min_n = int(protocol["sample"]["minimum_valid_events_for_economic_decision"])
    if n < min_n:
        return "INSUFFICIENT_POWER", f"Only {n} valid predeclared events after eligibility filters; minimum is {min_n}."
    values = [x["net_short_excess_return"] for x in returns]
    mean = statistics.mean(values)
    if mean <= 0:
        return "NEGATIVE", f"Mean net short excess return is {mean:.6f} <= 0 under the frozen expression."
    sd = statistics.stdev(values)
    t_stat = math.inf if sd == 0 and mean > 0 else (mean / (sd / math.sqrt(n)) if sd > 0 else -math.inf)
    threshold = float(protocol["statistics"]["positive_threshold_t"])
    if t_stat >= threshold:
        return "POSITIVE_EXPLORATORY", f"Mean net short excess return is positive and one-sided t={t_stat:.3f} >= {threshold:.3f}."
    return "INSUFFICIENT_POWER", f"Mean net is positive but one-sided t={t_stat:.3f} < {threshold:.3f}."


def run(output_path: Path) -> dict[str, Any]:
    protocol_bytes = PROTOCOL_PATH.read_bytes()
    protocol = json.loads(protocol_bytes)
    if protocol["authority"]["economic_experiment_authorized"] is not True:
        raise RuntimeError("Economic experiment is not Owner-authorized in frozen protocol")
    if protocol["authority"]["real_capital_authorized"] is not False or protocol["authority"]["live_trading_authorized"] is not False:
        raise RuntimeError("This historical runner refuses real capital/live trading")
    start_date = protocol["sample"]["event_window_utc_half_open"][0][:10]
    end_date = protocol["sample"]["event_window_utc_half_open"][1][:10]
    documentary_events, sec_provenance = get_documentary_events(protocol)
    ticker_history, dera_hashes = load_pit_ticker_history(start_date)
    d1 = (datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=45)).strftime("%Y-%m-%d")
    d2 = (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=15)).strftime("%Y-%m-%d")
    try:
        spy_rows = get_stooq_daily("SPY", d1, d2)
    except SourceError as exc:
        result = {"schema": 1, "protocol_id": protocol["protocol_id"], "protocol_sha256": sha256_bytes(protocol_bytes),
                  "runner_sha256": sha256_file(Path(__file__)), "kind": "SOURCE_UNUSABLE",
                  "lesson": f"Benchmark market source unavailable: {exc}", "economic_outcome_accessed": False,
                  "real_capital_used": False, "live_trading_used": False, "documentary_event_count": len(documentary_events),
                  "provenance": {"sec": sec_provenance, "dera_zip_sha256": dera_hashes}}
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return result
    spy_by_date = {r["date"]: r for r in spy_rows}
    market_cache: dict[str, list[dict[str, Any]] | None] = {}
    mapped_market_n = 0
    filtered_liquidity_n = 0
    valid_returns: list[dict[str, Any]] = []
    event_receipts: list[dict[str, Any]] = []
    for event in documentary_events:
        ticker = pit_ticker(ticker_history, event["issuer_cik"], event["filing_date"])
        receipt = {"accession": event["accession"], "issuer_cik": event["issuer_cik"], "seller_cik": event["seller_cik"],
                   "filing_date": event["filing_date"], "accepted_local": event["accepted_local"],
                   "signal_ratio": event["signal_ratio"], "ticker_pit": ticker}
        if not ticker:
            receipt["status"] = "NO_PIT_TICKER"; event_receipts.append(receipt); continue
        if ticker not in market_cache:
            try:
                market_cache[ticker] = get_stooq_daily(ticker, d1, d2)
            except SourceError:
                market_cache[ticker] = None
        stock_rows = market_cache[ticker]
        if stock_rows is None:
            receipt["status"] = "NO_MARKET_DATA"; event_receipts.append(receipt); continue
        mapped_market_n += 1
        computed = event_return(event, stock_rows, spy_by_date, protocol)
        if computed is None:
            receipt["status"] = "INCOMPLETE_MARKET_WINDOW"; event_receipts.append(receipt); continue
        if computed.get("eligible_market_filter") is False:
            filtered_liquidity_n += 1
            receipt.update({"status": "PRE_EVENT_MARKET_FILTER_EXCLUDED", **computed}); event_receipts.append(receipt); continue
        receipt.update({"status": "VALID_OUTCOME", **computed})
        event_receipts.append(receipt); valid_returns.append(receipt)
    kind, lesson = classify(protocol, len(documentary_events), mapped_market_n, valid_returns)
    values = [x["net_short_excess_return"] for x in valid_returns]
    gross = [x["gross_short_excess_return"] for x in valid_returns]
    stats: dict[str, Any] = {"n": len(values), "mean_net_short_excess_return": statistics.mean(values) if values else None,
        "median_net_short_excess_return": statistics.median(values) if values else None,
        "positive_net_hit_rate": (sum(v > 0 for v in values) / len(values)) if values else None,
        "mean_gross_short_excess_return": statistics.mean(gross) if gross else None,
        "sample_sd_net": statistics.stdev(values) if len(values) >= 2 else None, "one_sided_t_stat": None}
    if len(values) >= 2 and stats["sample_sd_net"] is not None:
        sd, mean = stats["sample_sd_net"], stats["mean_net_short_excess_return"]
        stats["one_sided_t_stat"] = math.inf if sd == 0 and mean > 0 else (mean / (sd / math.sqrt(len(values))) if sd > 0 else None)
    coverage = mapped_market_n / len(documentary_events) if documentary_events else 0.0
    result = {"schema": 1, "protocol_id": protocol["protocol_id"], "candidate_id": protocol["candidate_id"],
        "generation_id": protocol["generation_id"], "protocol_sha256": sha256_bytes(protocol_bytes),
        "runner_sha256": sha256_file(Path(__file__)), "kind": kind, "lesson": lesson, "decision_map_applied": True,
        "economic_outcome_accessed": bool(valid_returns), "real_capital_used": False, "live_trading_used": False,
        "documentary_event_count": len(documentary_events), "pit_ticker_and_market_count": mapped_market_n,
        "pit_ticker_and_market_coverage": coverage, "pre_event_market_filter_exclusions": filtered_liquidity_n,
        "statistics": stats, "events": event_receipts,
        "provenance": {"sec": sec_provenance, "dera_zip_sha256": dera_hashes,
            "stooq_symbol_rule": protocol["source_contract"]["market_symbol_rule"], "benchmark": "SPY.US", "market_window": [d1, d2]},
        "frozen_parameters": {"signal_threshold": protocol["sample"]["signal_threshold"], "entry": protocol["clock"]["entry"],
            "exit": protocol["clock"]["exit"], "round_trip_cost_bps": protocol["economic_expression"]["round_trip_cost_bps"],
            "minimum_n": protocol["sample"]["minimum_valid_events_for_economic_decision"],
            "positive_t_threshold": protocol["statistics"]["positive_threshold_t"]}}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return result


def self_test() -> None:
    xml = """<?xml version="1.0"?><edgarSubmission xmlns="http://www.sec.gov/edgar/ownership"><headerData><submissionType>144</submissionType><filerInfo><filer><filerCredentials><cik>123</cik></filerCredentials></filer></filerInfo></headerData><formData><issuerInfo><issuerCik>456</issuerCik><issuerName>X</issuerName></issuerInfo><securitiesInformation><securitiesClassTitle>Common Stock</securitiesClassTitle><noOfUnitsSold>1000</noOfUnitsSold><aggregateMarketValue>100000</aggregateMarketValue><noOfUnitsOutstanding>500000</noOfUnitsOutstanding><approxSaleDate>03/04/2024</approxSaleDate><securitiesExchangeName>NYSE</securitiesExchangeName></securitiesInformation></formData></edgarSubmission>"""
    parsed = parse_form144(xml, "0000000000-24-000001", "2024-03-04", "2024-03-04T12:00:00")
    assert parsed is not None and parsed["issuer_cik"] == "0000000456" and parsed["seller_cik"] == "0000000123"
    assert abs(parsed["signal_ratio"] - 0.002) < 1e-12
    idx = "A|144|123|2024-03-04|edgar/data/123/000000000024000001/0000000000-24-000001.txt"
    assert len(parse_master_index(idx, "2024-03-01", "2024-04-01", set())) == 1
    print("SELF_TEST_PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="research/research_os/experiments/results/FORM144_SUPPLY_001_RESULT.json")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test(); return 0
    result = run((ROOT / args.output).resolve())
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
