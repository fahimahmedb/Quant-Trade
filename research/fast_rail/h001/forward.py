"""H-001 (corrected, SHADOW_DIRECT k=1): automated forward evaluation.

ORDER 12 (declared 2026-09-29, registry "declared"): engagements stay in P&L until the
venue settles; >10% missing closes -> INCONCLUSIVE(data); the decision test is the
order-12b e-process (until delivered: status SHADOW_DIRECT, t-SPRT indicator only);
terminal FORWARD_PASS(PRICE) needs every engagement of the prefix settled and
P&L not significantly below CLV. It proves a PRICE edge, not a cashable gain.

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

PRISTINE_AFTER = "2026-09-29T14:00:00+00:00"   # order 12: commit time rounded up to the hour
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
            seen_at = quote.get("book_fetched_at") or quote.get("fetched_at")
            if seen_at and (parse_time(seen_at) - parse_time(stamp)).total_seconds() \
                    > MAX_QUOTE_AGE_S:
                continue                      # stale relative to the Pinnacle snapshot
            if quote["venue"] == "KALSHI" and quote.get("book_status") != "OK":
                continue                      # order 12: no readable book -> no bet
            depth = sum(size for price, size in (quote.get("asks") or [])
                        if price <= ask + 1e-9)
            if depth < ORDER_CONTRACTS:
                continue                      # the declared order would not fill at ask
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
                              "token_id": quote.get("token_id"), "depth_seen": depth,
                              "book_seen_at": seen_at}
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


MAX_MISSING_CLOSE = 0.10


def _clv_indicator(series: list[float]) -> dict[str, Any]:
    """Plug-in t-SPRT: INDICATOR ONLY since order 12 (alpha not guaranteed)."""
    return event_sequential_test(series, H1_OVER_SIGMA, ALPHA, max_observations=MAX_MATCHES,
                                 sigma_floor=SIGMA_DECLARED)


def evaluate(pinnacle: list[dict[str, Any]], quotes: Iterable[dict[str, Any]],
             settled: dict[str, float], now: datetime,
             frozen: dict[str, Any] | None = None,
             settled_at: dict[str, str] | None = None,
             decision_test: Callable[[list[float]], dict[str, Any]] | None = None
             ) -> dict[str, Any]:
    """Order 12. Every entered bet is an engagement kept until the venue settles it.

    ``decision_test`` is the order-12b anytime-valid e-process over the match CLV
    series; while it is None the status stays SHADOW_DIRECT (no decision possible).
    """
    quotes = list(quotes)
    settled_at = settled_at or {}
    kickoffs: dict[str, set[str]] = {}
    for row in pinnacle:
        kickoffs.setdefault(row["event_id"], set()).add(row["commence_time"])
    engagements, matches = [], {}
    for bet in find_bets(pinnacle, quotes):
        if parse_time(bet["commence_time"]) > now:
            continue                                  # not yet played: not scored yet
        rescheduled = len(kickoffs.get(bet["odds_event_id"], ())) > 1
        close = None if rescheduled else _venue_close(quotes, bet)
        key = f"{bet['venue']}|{bet['market']}|{bet.get('token_id')}"
        cost = bet["ask"] + bet["fee"]
        eng = {**bet, "key": key, "rescheduled": rescheduled,
               "clv": None if close is None else close - cost,
               "settlement": settled.get(key), "settled_at": settled_at.get(key)}
        eng["pnl"] = None if eng["settlement"] is None else eng["settlement"] - cost
        engagements.append(eng)
        unit = matches.setdefault(bet["odds_event_id"], {"kickoff": bet["commence_time"],
                                                         "engagements": []})
        unit["engagements"].append(eng)
    ordered = sorted(matches.items(), key=lambda item: (item[1]["kickoff"], item[0]))
    clv_series, clv_units = [], []
    for event, unit in ordered:
        clvs = [e["clv"] for e in unit["engagements"] if e["clv"] is not None]
        if clvs:
            clv_series.append(sum(clvs) / len(clvs))
            clv_units.append(event)
    missing = sum(1 for e in engagements if e["clv"] is None)
    missing_frac = missing / len(engagements) if engagements else 0.0
    indicator = _clv_indicator(clv_series)
    decision = decision_test(clv_series) if decision_test else None
    status = "SHADOW_DIRECT"
    if engagements and len(engagements) >= 20 and missing_frac > MAX_MISSING_CLOSE:
        status = "INCONCLUSIVE(DATA)"
    elif decision is not None:
        if decision["decision"] == "REJECT_EDGE":
            status = "REJECT(FORWARD)"
        elif decision["decision"] == "INCONCLUSIVE":
            status = "INCONCLUSIVE"
        elif decision["decision"] == "ACCEPT_EDGE":
            stop = set(clv_units[:decision["observations"]])
            prefix = [e for e in engagements if e["odds_event_id"] in stop]
            if any(e["pnl"] is None for e in prefix):
                status = "ACCEPT_PENDING_SETTLEMENT"      # never frozen before settlement
            else:
                pnl = [e["pnl"] for e in prefix]
                clv = [e["clv"] for e in prefix if e["clv"] is not None]
                se = _se(pnl)
                ok = (sum(pnl) / len(pnl)) >= (sum(clv) / len(clv)) - 1.96 * se
                status = "FORWARD_PASS(PRICE)" if ok else "REJECT(PNL_BELOW_CLV)"
    report = {"hypothesis": "H-001", "k": K, "alpha": ALPHA, "pristine_after": PRISTINE_AFTER,
              "statistic": "net venue CLV per match (prob points)",
              "engagements": len(engagements), "matches_with_clv": len(clv_series),
              "missing_close_fraction": missing_frac,
              "mean_net_clv": sum(clv_series) / len(clv_series) if clv_series else None,
              "decision_test": decision or "order-12b e-process not delivered: no decision",
              "t_sprt_indicator_only": indicator, "status": status,
              "economics": _economics(engagements),
              "disclaimer": ("FORWARD_PASS(PRICE) proves a price edge, not a cashable gain; "
                             "proving P&L needs about (1.96*sigma/edge)^2 ~ 2,400 bets; proof "
                             "of gain is a real micro-test, an owner decision."),
              "evaluated_at": now.isoformat(timespec="seconds")}
    terminal = ("FORWARD_PASS(PRICE)", "REJECT(FORWARD)", "INCONCLUSIVE",
                "INCONCLUSIVE(DATA)", "REJECT(PNL_BELOW_CLV)")
    if frozen and frozen.get("status") in terminal:
        return {**frozen, "evaluated_at": report["evaluated_at"], "sticky": True,
                "engagements_since": report["engagements"]}
    return report


def _se(values: list[float]) -> float:
    n = len(values)
    if n < 2:
        return float("inf")
    mean = sum(values) / n
    return math.sqrt(sum((v - mean) ** 2 for v in values) / (n - 1) / n)


def _economics(engagements: list[dict[str, Any]]) -> dict[str, Any]:
    """Reported, never a pass condition (order 12 §3). Per declared 100-contract order."""
    done = [e for e in engagements if e["pnl"] is not None and e.get("settled_at")]
    total = sum(e["pnl"] for e in done) * ORDER_CONTRACTS
    capital_years = sum((e["ask"] + e["fee"]) * ORDER_CONTRACTS
                        * max((parse_time(e["settled_at"]) - parse_time(e["entry_observed_at"])
                               ).total_seconds(), 3600.0) / (365.25 * 86400) for e in done)
    pnl = [e["pnl"] for e in done]
    mean = sum(pnl) / len(pnl) if pnl else None
    se = _se(pnl) if pnl else None
    return {"settled_engagements": len(done),
            "unsettled_engagements": sum(1 for e in engagements if e["pnl"] is None),
            "net_pnl_total_usd": total,
            "capital_locked_usd_years": capital_years,
            "annualised_return_on_locked_capital": total / capital_years if capital_years else None,
            "mean_pnl_per_contract": mean,
            "pnl_ci95_per_contract": None if mean is None or se == float("inf")
            else [mean - 1.96 * se, mean + 1.96 * se]}


def run(out: Path, now: datetime | None = None, fetch: Callable[[str], Any] | None = None
        ) -> dict[str, Any]:
    """Settle due bets (append-only stream), evaluate, write ``eval/h001_shadow_direct.json``."""
    now = now or datetime.now(timezone.utc)
    fetch = fetch or (lambda url: http_fetch(url)[0])
    pinnacle, quotes = load(out)
    items = read_stream(out, SETTLEMENTS)
    settled = {item["record"]["key"]: item["record"]["value"] for item in items}
    settled_at = {item["record"]["key"]: item["observed_at"] for item in items}
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
            settled_at[key] = now.isoformat(timespec="seconds")
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
        report = evaluate(pinnacle, quotes, settled, now, frozen, settled_at)
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
