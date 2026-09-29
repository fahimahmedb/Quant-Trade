"""H-001 (corrected, SHADOW_DIRECT k=1): automated forward evaluation.

Declared in research/fast_rail/registry.jsonl (event "shadow_direct") BEFORE any
forward decision; only quotes observed at/after ``PRISTINE_AFTER`` count.

* Statistic (per match, primary; amended 2026-09-29 after the economic red team):
  NET VENUE CLV in probability points = venue mid at its last pre-kickoff quote
  - ask - fee. Pinnacle selects the bet but does NOT score it: scoring against
  Pinnacle's own close is >= the 2-point entry gap by construction (red-team HIGH).
  Under H0 (venue price a martingale) the mean is -fee < 0. Pinnacle CLV is kept as
  a diagnostic only. 2026 fee formulas, per-order rounding, 100-contract order.
* Entry (one expression, source parameters): power devig of the same-run Pinnacle
  snapshot; buy an outcome only where the fee is below the gap and the net edge is
  at least ``MIN_NET_EDGE``; Kalshi takes priority when both venues qualify in one run.
* Test: ``event_sequential_test`` (alpha = shadow_direct_alpha(1)), H1 = source
  effect x 0.5, sigma floor = declared sigma, horizon ``MAX_MATCHES``.
* Proxy rule: FORWARD_PASS also needs a positive mean net paper P&L on the same bets
  (settled by the venue's own resolution).
Only this module's output file changes between runs; it never touches the Book.
"""

from __future__ import annotations

import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research" / "fast_rail" / "h001"))

from quant.dataplane.h001_relay import http_fetch, parse_time, read_stream  # noqa: E402
from quant.factory.sportsfair import devig_power  # noqa: E402
from quant.learning.sequential import event_sequential_test, shadow_direct_alpha  # noqa: E402
from clv import closing_snapshot, load  # noqa: E402

PRISTINE_AFTER = "2026-09-29T14:00:00+00:00"   # >= commit of the amended declaration
K = 1
ALPHA = shadow_direct_alpha(K)                  # 0.025
SOURCE_EFFECT = 0.019        # S83: EV bets vs Pinnacle, realised 1.9% ROI since 2023/24
#: ROI per stake -> probability points at a typical price p = 0.5: 0.019 x 0.5.
H1_EFFECT = SOURCE_EFFECT * 0.5 * 0.5
SIGMA_DECLARED = 0.05        # CLV sigma per bet, prob points (study R2: Buchdahl S15 at p~0.5)
H1_OVER_SIGMA = H1_EFFECT / SIGMA_DECLARED
MAX_MATCHES = 1500
MIN_SETTLED = 30
SETTLE_BUDGET_S = 120
MAX_QUOTE_AGE_S = 120        # quote fetched within 2 min of the run's Pinnacle snapshot
MIN_NET_EDGE = 0.02          # source parameter (declared min edge)
ORDER_CONTRACTS = 100        # declared paper order size (fee rounding is per order)
KALSHI_RATE = 0.07           # Kalshi general taker fee: ceil_to_cent(0.07*C*P*(1-P))
POLYMARKET_SPORTS_RATE = 0.05  # S17: fee = C*rate*p*(1-p); sports 0.05
#: ASSUMPTION: Polymarket fee rounded UP to 0.0001 USDC per order (conservative).
POLYMARKET_ROUND = 1e-4
SETTLEMENTS = "sports_quotes/settlements"
EVAL_FILE = "eval/h001_shadow_direct.json"


def _ceil(value: float, step: float) -> float:
    return math.ceil(round(value / step, 9)) * step


def fee_per_contract(venue: str, price: float, contracts: int = ORDER_CONTRACTS) -> float:
    raw = contracts * price * (1.0 - price)
    if venue == "KALSHI":
        return _ceil(KALSHI_RATE * raw, 0.01) / contracts
    return _ceil(POLYMARKET_SPORTS_RATE * raw, POLYMARKET_ROUND) / contracts


def find_bets(pinnacle: list[dict[str, Any]], quotes: Iterable[dict[str, Any]],
              pristine_after: str = PRISTINE_AFTER) -> list[dict[str, Any]]:
    snap = {(row["event_id"], row["observed_at"]): row for row in pinnacle}
    start = parse_time(pristine_after)
    runs: dict[str, list[dict[str, Any]]] = {}
    for quote in quotes:
        runs.setdefault(quote["observed_at"], []).append(quote)
    bets: dict[tuple[str, str], dict[str, Any]] = {}
    for stamp in sorted(runs):
        if parse_time(stamp) < start:
            continue
        # Kalshi first inside one run: priority venue when both qualify.
        for quote in sorted(runs[stamp], key=lambda q: (q["venue"] != "KALSHI", q["venue"])):
            event, ask = quote["odds_event_id"], quote.get("best_ask")
            pin = snap.get((event, stamp))
            if ask is None or not 0 < ask < 1 or pin is None:
                continue
            if parse_time(stamp) >= parse_time(pin["commence_time"]):
                continue
            fair = devig_power(pin["prices"]).get(quote["outcome"])
            if fair is None:
                continue
            if quote["venue"] != "KALSHI":
                fetched = quote.get("fetched_at")
                if fetched and (parse_time(fetched) - parse_time(stamp)).total_seconds() \
                        > MAX_QUOTE_AGE_S:
                    continue                  # stale relative to the Pinnacle snapshot
                depth = sum(size for price, size in (quote.get("asks") or [])
                            if price <= ask + 1e-9)
                if depth < ORDER_CONTRACTS:
                    continue                  # the declared order would not fill at ask
            fee = fee_per_contract(quote["venue"], ask)
            net_edge = fair - ask - fee
            slot = (event, quote["outcome"])
            if fee < fair - ask and net_edge >= MIN_NET_EDGE and slot not in bets:
                bets[slot] = {"odds_event_id": event, "outcome": quote["outcome"],
                              "venue": quote["venue"], "entry_observed_at": stamp,
                              "ask": ask, "fee": fee, "fair_at_entry": fair,
                              "net_edge_at_entry": net_edge,
                              "commence_time": pin["commence_time"],
                              "market": quote.get("ticker") or quote.get("market_id"),
                              "token_id": quote.get("token_id")}
    return list(bets.values())


def _settlement(bet: dict[str, Any], fetch: Callable[[str], Any]) -> float | None:
    """1.0 / 0.0 from the venue's own resolution, None while unresolved."""
    if bet["venue"] == "KALSHI":
        market = (fetch("https://api.elections.kalshi.com/trade-api/v2/markets/"
                        f"{bet['market']}") or {}).get("market") or {}
        result = market.get("result")
        return {"yes": 1.0, "no": 0.0}.get(result) if market.get("status") in (
            "settled", "finalized", "determined") else None
    rows = fetch(f"https://gamma-api.polymarket.com/markets?condition_ids={bet['market']}") or []
    market = rows[0] if rows else {}
    if not market.get("closed"):
        return None
    tokens = json.loads(market.get("clobTokenIds") or "[]")
    prices = json.loads(market.get("outcomePrices") or "[]")
    if bet.get("token_id") in tokens and len(prices) == len(tokens):
        value = float(prices[tokens.index(bet["token_id"])])
        return value if value in (0.0, 0.5, 1.0) else None
    return None


def _venue_close(quotes: list[dict[str, Any]], bet: dict[str, Any]) -> float | None:
    """Venue mid at its last quote strictly after entry and before kickoff."""
    kickoff = parse_time(bet["commence_time"])
    best = None
    for quote in quotes:
        if (quote["odds_event_id"], quote["outcome"], quote["venue"]) != (
                bet["odds_event_id"], bet["outcome"], bet["venue"]):
            continue
        seen = parse_time(quote["observed_at"])
        if not parse_time(bet["entry_observed_at"]) < seen < kickoff:
            continue
        bid, ask = quote.get("best_bid"), quote.get("best_ask")
        if bid is None or ask is None or not 0 <= bid <= ask <= 1:
            continue
        if best is None or seen > best[0]:
            best = (seen, (bid + ask) / 2.0)
    return None if best is None else best[1]


def evaluate(pinnacle: list[dict[str, Any]], quotes: Iterable[dict[str, Any]],
             settled: dict[str, float], now: datetime,
             frozen: dict[str, Any] | None = None) -> dict[str, Any]:
    quotes = list(quotes)
    kickoffs: dict[str, set[str]] = {}
    for row in pinnacle:
        kickoffs.setdefault(row["event_id"], set()).add(row["commence_time"])
    matches: dict[str, dict[str, Any]] = {}
    for bet in find_bets(pinnacle, quotes):
        if len(kickoffs.get(bet["odds_event_id"], ())) > 1:
            continue                      # rescheduled match: dropped from CLV and P&L
        if parse_time(bet["commence_time"]) > now:
            continue
        close = _venue_close(quotes, bet)
        if close is None:
            continue                      # no later venue quote: never scored at entry
        unit = matches.setdefault(bet["odds_event_id"], {"kickoff": bet["commence_time"],
                                                         "clv": [], "pnl": []})
        unit["clv"].append(close - bet["ask"] - bet["fee"])
        key = f"{bet['venue']}|{bet['market']}|{bet.get('token_id')}"
        if key in settled:
            unit["pnl"].append(settled[key] - bet["ask"] - bet["fee"])
    ordered = sorted(matches.items(), key=lambda item: (item[1]["kickoff"], item[0]))
    series = [sum(u["clv"]) / len(u["clv"]) for _, u in ordered]
    test = event_sequential_test(series, H1_OVER_SIGMA, ALPHA, max_observations=MAX_MATCHES,
                                 sigma_floor=SIGMA_DECLARED)
    # Proxy P&L frozen at the SPRT stopping point (no optional stopping on the gate).
    prefix = ordered[:test["observations"]] if test["decision"] != "CONTINUE" else ordered
    pnl = [value for _, u in prefix for value in u["pnl"]]
    pnl_mean = sum(pnl) / len(pnl) if pnl else None
    if test["decision"] == "ACCEPT_EDGE":
        status = ("FORWARD_PASS" if len(pnl) >= MIN_SETTLED and (pnl_mean or 0) > 0
                  else "ACCEPT_PENDING_PNL")
    else:
        status = {"REJECT_EDGE": "REJECT(FORWARD)", "INCONCLUSIVE": "INCONCLUSIVE",
                  "CONTINUE": "SHADOW_DIRECT"}[test["decision"]]
    report = {"hypothesis": "H-001", "k": K, "alpha": ALPHA, "pristine_after": PRISTINE_AFTER,
              "statistic": "net venue CLV per match (prob points)", "matches": len(series),
              "mean_net_clv": sum(series) / len(series) if series else None,
              "settled_bets": len(pnl), "mean_net_pnl": pnl_mean, "t_sprt": test,
              "status": status, "evaluated_at": now.isoformat(timespec="seconds")}
    # Sticky: a terminal decision is never re-decided by later or late-arriving data.
    if frozen and frozen.get("status") in ("FORWARD_PASS", "REJECT(FORWARD)", "INCONCLUSIVE"):
        return {**frozen, "evaluated_at": report["evaluated_at"], "sticky": True,
                "matches_since": report["matches"]}
    return report


def run(out: Path, now: datetime | None = None, fetch: Callable[[str], Any] | None = None
        ) -> dict[str, Any]:
    """Settle due bets (append-only stream), evaluate, write ``eval/h001_shadow_direct.json``."""
    now = now or datetime.now(timezone.utc)
    fetch = fetch or (lambda url: http_fetch(url)[0])
    pinnacle, quotes = load(out)
    settled = {item["record"]["key"]: item["record"]["value"]
               for item in read_stream(out, SETTLEMENTS)}
    new = []
    deadline = datetime.now(timezone.utc).timestamp() + SETTLE_BUDGET_S
    for bet in find_bets(pinnacle, quotes):
        if datetime.now(timezone.utc).timestamp() > deadline:
            break                          # bounded: never hold the collection commit
        key = f"{bet['venue']}|{bet['market']}|{bet.get('token_id')}"
        if key in settled or (now - parse_time(bet["commence_time"])).total_seconds() < 6 * 3600:
            continue
        try:
            value = _settlement(bet, fetch)
        except Exception:                 # network: retry next run, never fill in
            value = None
        if value is not None:
            settled[key] = value
            new.append({"key": key, "value": value})
    if new:
        path = out / SETTLEMENTS / f"{now:%Y-%m}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.stat().st_size and not path.read_bytes().endswith(b"\n"):
            with path.open("a") as handle:
                handle.write("\n")        # isolate a torn line left by a killed run
        with path.open("a") as handle:
            for record in new:
                handle.write(json.dumps({"key": record["key"], "kind": "observation",
                                         "observed_at": now.isoformat(timespec="seconds"),
                                         "record": record}, sort_keys=True) + "\n")
    target = out / EVAL_FILE
    frozen = json.loads(target.read_text()) if target.exists() else None
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        report = evaluate(pinnacle, quotes, settled, now, frozen)
    except Exception as exc:                # visible in the eval file, not only _runs
        report = {**(frozen or {}), "status": "EVAL_ERROR",
                  "error": f"{type(exc).__name__}: {exc}"[:200],
                  "evaluated_at": now.isoformat(timespec="seconds")}
    tmp = target.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    os.replace(tmp, target)                 # atomic
    return report


if __name__ == "__main__":
    print(json.dumps(run(Path(sys.argv[1] if len(sys.argv) > 1 else "data/feeds")), indent=1))
