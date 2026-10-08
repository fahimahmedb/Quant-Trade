#!/usr/bin/env python3
"""Read-only Polymarket negative-risk parity collector.

Network surface is intentionally limited to public GET metadata and public POST
order-book reads. There is no wallet, authentication, order, conversion, or
settlement-outcome path in this module.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, InvalidOperation
from typing import Any, Iterable

GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
UA = "quant-trade-neg-risk-read-only/0.1"
D0 = Decimal("0")
D1 = Decimal("1")
FEE_QUANTUM = Decimal("0.00001")
DEFAULT_MAX_EVENT_TOKENS = 100  # local safety cap; not an exchange limit claim
DEFAULT_MAX_SKEW_MS = 1000


class DataContractError(RuntimeError):
    pass


@dataclass(frozen=True)
class FeeSchedule:
    rate: Decimal
    exponent: Decimal


@dataclass(frozen=True)
class MarketSpec:
    market_id: str
    condition_id: str
    title: str
    yes_token: str
    no_token: str
    fee: FeeSchedule


@dataclass(frozen=True)
class EventSpec:
    event_id: str
    title: str
    markets: tuple[MarketSpec, ...]

    @property
    def token_ids(self) -> tuple[str, ...]:
        out: list[str] = []
        for m in self.markets:
            out.extend((m.yes_token, m.no_token))
        return tuple(out)


@dataclass(frozen=True)
class Fill:
    shares: Decimal
    gross: Decimal
    fee: Decimal


@dataclass(frozen=True)
class RouteResult:
    event_id: str
    source_market_id: str
    q: Decimal
    buy_cost: Decimal
    sell_proceeds: Decimal
    taker_fees: Decimal
    gap: Decimal
    gross_traded_notional: Decimal
    threshold: Decimal
    violation: bool


def dec(x: Any, field: str) -> Decimal:
    try:
        d = Decimal(str(x))
    except (InvalidOperation, ValueError, TypeError) as e:
        raise DataContractError(f"invalid decimal {field}={x!r}") from e
    if not d.is_finite():
        raise DataContractError(f"non-finite decimal {field}={x!r}")
    return d


def parse_json_array(x: Any, field: str) -> list[Any]:
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        try:
            v = json.loads(x)
        except json.JSONDecodeError as e:
            raise DataContractError(f"invalid JSON array in {field}") from e
        if isinstance(v, list):
            return v
    raise DataContractError(f"{field} is not an array")


def _fee_from_market(m: dict[str, Any]) -> FeeSchedule:
    enabled = m.get("feesEnabled")
    if enabled is False:
        return FeeSchedule(D0, D1)
    if enabled is not True:
        raise DataContractError("feesEnabled must be explicit")
    s = m.get("feeSchedule")
    if not isinstance(s, dict):
        raise DataContractError("feeSchedule missing on fee-enabled market")
    rate = dec(s.get("rate"), "feeSchedule.rate")
    exponent = dec(s.get("exponent"), "feeSchedule.exponent")
    if rate < 0 or exponent <= 0:
        raise DataContractError("invalid fee schedule")
    if s.get("takerOnly") is not True:
        raise DataContractError("screen only supports taker-only fee schedules")
    return FeeSchedule(rate, exponent)


def normalize_standard_neg_risk_event(event: dict[str, Any]) -> EventSpec:
    """Fail-closed normalization of one *standard*, complete-at-creation neg-risk event.

    A literal market/outcome label containing 'Other' is allowed here. What is
    forbidden is augmented negative risk, because in that regime placeholders
    can be clarified later and the semantic coverage of Other changes.
    """
    if event.get("enableNegRisk") is not True:
        raise DataContractError("event enableNegRisk is not true")
    if event.get("negRiskAugmented") is not False:
        raise DataContractError("augmented or unknown negative-risk semantics")
    raw_markets = event.get("markets")
    if not isinstance(raw_markets, list) or len(raw_markets) < 3:
        raise DataContractError("need at least three component markets")

    markets: list[MarketSpec] = []
    seen_conditions: set[str] = set()
    seen_tokens: set[str] = set()
    for m in raw_markets:
        if not isinstance(m, dict):
            raise DataContractError("market entry is not an object")
        required_true = ("active", "acceptingOrders", "enableOrderBook", "negRisk")
        if any(m.get(k) is not True for k in required_true):
            raise DataContractError("component market is not fully live/neg-risk")
        if m.get("closed") is not False or m.get("archived") is True:
            raise DataContractError("component market is closed/archived")

        outcomes = parse_json_array(m.get("outcomes"), "outcomes")
        tids = parse_json_array(m.get("clobTokenIds"), "clobTokenIds")
        if [str(x).lower() for x in outcomes] != ["yes", "no"] or len(tids) != 2:
            raise DataContractError("component market must be binary YES/NO")
        yes, no = str(tids[0]), str(tids[1])
        cid = str(m.get("conditionId") or "")
        mid = str(m.get("id") or "")
        if not cid or not mid or not yes or not no or yes == no:
            raise DataContractError("missing/duplicate market identifiers")
        if cid in seen_conditions or yes in seen_tokens or no in seen_tokens:
            raise DataContractError("duplicate condition/token across event")
        seen_conditions.add(cid)
        seen_tokens.update((yes, no))

        title = str(m.get("groupItemTitle") or m.get("question") or mid)
        markets.append(MarketSpec(mid, cid, title, yes, no, _fee_from_market(m)))

    return EventSpec(str(event.get("id") or ""), str(event.get("title") or ""), tuple(markets))


def fee_usdc(shares: Decimal, price: Decimal, schedule: FeeSchedule) -> Decimal:
    if shares <= 0 or not (D0 < price < D1):
        raise DataContractError("invalid fee inputs")
    if schedule.rate == 0:
        return D0
    component = price * (D1 - price)
    # Decimal supports non-integral powers only poorly; current documented
    # schedules use integer exponent. Fail closed otherwise.
    if schedule.exponent != schedule.exponent.to_integral_value():
        raise DataContractError("non-integral fee exponent unsupported")
    e = int(schedule.exponent)
    raw = shares * schedule.rate * (component ** e)
    # Conservative screen: round taker cost upward to documented 5-decimal precision.
    return raw.quantize(FEE_QUANTUM, rounding=ROUND_CEILING)


def _sorted_levels(levels: Any, is_ask: bool) -> list[tuple[Decimal, Decimal]]:
    if not isinstance(levels, list):
        raise DataContractError("book levels must be a list")
    out: list[tuple[Decimal, Decimal]] = []
    for row in levels:
        if not isinstance(row, dict):
            raise DataContractError("bad book level")
        p, s = dec(row.get("price"), "price"), dec(row.get("size"), "size")
        if not (D0 < p < D1) or s <= 0:
            raise DataContractError("invalid book level")
        out.append((p, s))
    out.sort(key=lambda z: z[0], reverse=not is_ask)
    return out


def walk_book(levels: Any, q: Decimal, is_ask: bool, fee: FeeSchedule) -> Fill | None:
    if q <= 0:
        raise DataContractError("q must be positive")
    remaining = q
    gross = D0
    fees = D0
    for price, size in _sorted_levels(levels, is_ask):
        take = min(remaining, size)
        gross += take * price
        fees += fee_usdc(take, price, fee)
        remaining -= take
        if remaining == 0:
            return Fill(q, gross, fees)
    return None


def timestamp_ms(book: dict[str, Any]) -> int:
    raw = int(str(book.get("timestamp")))
    return raw if raw >= 10**12 else raw * 1000


def index_books(payload: Any, expected_tokens: Iterable[str]) -> dict[str, dict[str, Any]]:
    if not isinstance(payload, list):
        raise DataContractError("/books response must be a list")
    expected = set(expected_tokens)
    out: dict[str, dict[str, Any]] = {}
    for b in payload:
        if not isinstance(b, dict):
            raise DataContractError("book is not an object")
        token = str(b.get("asset_id") or "")
        if token not in expected or token in out:
            raise DataContractError("unexpected or duplicate book token")
        if b.get("neg_risk") is not True:
            raise DataContractError("book no longer reports neg_risk=true")
        dec(b.get("min_order_size"), "min_order_size")
        timestamp_ms(b)
        out[token] = b
    if set(out) != expected:
        raise DataContractError("missing book in batch response")
    return out


def evaluate_routes(event: EventSpec, books_payload: Any, max_skew_ms: int = DEFAULT_MAX_SKEW_MS) -> list[RouteResult]:
    books = index_books(books_payload, event.token_ids)
    ts = [timestamp_ms(b) for b in books.values()]
    if max(ts) - min(ts) > max_skew_ms:
        raise DataContractError("cross-leg snapshot skew exceeds cap")

    results: list[RouteResult] = []
    for src in event.markets:
        no_book = books[src.no_token]
        leg_books = [books[m.yes_token] for m in event.markets if m.market_id != src.market_id]
        # CLOB min_order_size is treated as share quantity; require a common q.
        q = max([dec(no_book["min_order_size"], "min_order_size")] +
                [dec(b["min_order_size"], "min_order_size") for b in leg_books])
        buy = walk_book(no_book.get("asks"), q, True, src.fee)
        if buy is None:
            continue
        sell_gross, sell_fees = D0, D0
        ok = True
        for m in event.markets:
            if m.market_id == src.market_id:
                continue
            f = walk_book(books[m.yes_token].get("bids"), q, False, m.fee)
            if f is None:
                ok = False
                break
            sell_gross += f.gross
            sell_fees += f.fee
        if not ok:
            continue
        all_fees = buy.fee + sell_fees
        gap = sell_gross - sell_fees - buy.gross - buy.fee
        gross_notional = buy.gross + sell_gross
        threshold = max(Decimal("0.10"), gross_notional * Decimal("0.001"))
        results.append(RouteResult(
            event.event_id, src.market_id, q, buy.gross, sell_gross,
            all_fees, gap, gross_notional, threshold, gap >= threshold,
        ))
    return results


def _request(method: str, url: str, body: Any = None, timeout: int = 30) -> tuple[bytes, Any]:
    data = None if body is None else json.dumps(body, separators=(",", ":")).encode()
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    return raw, json.loads(raw)


def list_open_events(limit: int = 100, max_pages: int = 20) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for page in range(max_pages):
        params = urllib.parse.urlencode({
            "closed": "false", "order": "id", "ascending": "true",
            "limit": limit, "offset": page * limit,
        })
        _, payload = _request("GET", f"{GAMMA}/events?{params}")
        if not isinstance(payload, list):
            raise DataContractError("Gamma events response is not a list")
        events.extend(payload)
        if len(payload) < limit:
            break
    return events


def refetch_event(event_id: str) -> EventSpec:
    _, payload = _request("GET", f"{GAMMA}/events/{urllib.parse.quote(event_id, safe='')}")
    if not isinstance(payload, dict):
        raise DataContractError("Gamma event detail is not an object")
    return normalize_standard_neg_risk_event(payload)


def select_events(events: Iterable[dict[str, Any]], max_events: int, max_event_tokens: int) -> tuple[list[EventSpec], dict[str, int]]:
    candidates: list[EventSpec] = []
    rejected: dict[str, int] = {}
    for e in events:
        try:
            s = normalize_standard_neg_risk_event(e)
            if len(s.token_ids) > max_event_tokens:
                raise DataContractError("event exceeds local batch-token safety cap")
            candidates.append(s)
        except DataContractError as ex:
            key = str(ex)
            rejected[key] = rejected.get(key, 0) + 1
    def key(s: EventSpec):
        return (0, int(s.event_id)) if s.event_id.isdigit() else (1, s.event_id)
    candidates.sort(key=key)
    return candidates[:max_events], rejected


def snapshot_event(event: EventSpec) -> tuple[bytes, Any]:
    body = [{"token_id": t} for t in event.token_ids]
    return _request("POST", f"{CLOB}/books", body)


def atomic_write_bytes(path: str, blob: bytes) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "xb") as f:
        f.write(blob)
        f.flush()
        os.fsync(f.fileno())


def atomic_write_json(path: str, obj: Any) -> None:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()
    atomic_write_bytes(path, blob)


def collect(out_dir: str, snapshots: int, interval_s: float, max_events: int, max_event_tokens: int) -> dict[str, Any]:
    # Discovery reads metadata only. No settlement/result endpoint is used.
    events_payload = list_open_events()
    selected0, rejected = select_events(events_payload, max_events, max_event_tokens)
    selected: list[EventSpec] = []
    for first in selected0:
        current = refetch_event(first.event_id)
        if {m.condition_id for m in current.markets} != {m.condition_id for m in first.markets}:
            raise DataContractError(f"event component set changed during discovery: {first.event_id}")
        if len(current.token_ids) > max_event_tokens:
            raise DataContractError(f"event exceeds local batch-token cap after refetch: {first.event_id}")
        selected.append(current)
    gamma_fingerprint = hashlib.sha256(
        json.dumps(events_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    manifest = {
        "collector": "READ_ONLY",
        "real_capital_authorized": False,
        "live_trading_authorized": False,
        "gamma_discovery_fingerprint_sha256": gamma_fingerprint,
        "selected_event_ids": [e.event_id for e in selected],
        "rejections": rejected,
        "snapshots_requested": snapshots,
        "interval_s": interval_s,
        "max_event_tokens_local_cap": max_event_tokens,
    }
    atomic_write_json(os.path.join(out_dir, "manifest.json"), manifest)
    for n in range(snapshots):
        started = time.time_ns()
        for event in selected:
            raw, payload = snapshot_event(event)
            routes = evaluate_routes(event, payload)
            raw_path = os.path.join(out_dir, "raw", f"{n:04d}_{event.event_id}.json")
            atomic_write_bytes(raw_path, raw)
            record = {
                "n": n,
                "request_started_ns": started,
                "event_id": event.event_id,
                "raw_path": os.path.relpath(raw_path, out_dir),
                "raw_sha256": hashlib.sha256(raw).hexdigest(),
                "routes": [r.__dict__ for r in routes],
            }
            atomic_write_json(os.path.join(out_dir, "snapshots", f"{n:04d}_{event.event_id}.json"), record)
        if n + 1 < snapshots and interval_s > 0:
            time.sleep(interval_s)
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--snapshots", type=int, default=60)
    ap.add_argument("--interval-s", type=float, default=10.0)
    ap.add_argument("--max-events", type=int, default=10)
    ap.add_argument("--max-event-tokens", type=int, default=DEFAULT_MAX_EVENT_TOKENS)
    args = ap.parse_args()
    if args.snapshots < 1 or args.interval_s < 0 or args.max_events < 1:
        raise SystemExit("invalid bounds")
    print(json.dumps(collect(args.out_dir, args.snapshots, args.interval_s, args.max_events, args.max_event_tokens), indent=2))


if __name__ == "__main__":
    main()
