"""H-001 per-bet CLV (primary KPI) and net P&L (confirmation) from the relay streams.

Inputs are the stored items of ``odds/pinnacle_h2h`` and ``sports_quotes/{polymarket,
kalshi}`` flattened as ``{**record, "observed_at": ...}`` (see ``load``). Pure: no I/O
beyond ``load``.

* Signal: at a run's ``observed_at``, a venue ask whose fee-inclusive cost is below
  Pinnacle's power-devigged probability *from the same run* (identical
  ``observed_at``; a quote without that Pinnacle snapshot is never used) by at least
  ``threshold`` (per-dollar edge). One bet per (event, outcome, venue): the first.
* Closing fair value: the LAST Pinnacle snapshot with ``observed_at`` strictly before
  ``commence_time``. Snapshots at/after kickoff are ignored. The snapshot-to-kickoff
  lag is reported and bets are flagged when it exceeds ``CLOSE_LAG_FLAG_MIN``.
* CLV: ``clv_prob = p_close - cost`` and ``clv_return = (p_close - cost) / cost`` per $1
  contract (positive = bought below closing fair value).
* Net P&L per contract: ``1{won} - cost`` once ``results`` names the winner.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any, Callable, Iterable

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from quant.dataplane.h001_relay import (CLOSE_LAG_FLAG_MIN, PINNACLE, QUOTES_KALSHI,  # noqa: E402
                                        QUOTES_PM, parse_time, read_stream)
from quant.factory.sportsfair import devig_power  # noqa: E402

#: ASSUMPTION (verify against the venue schedule before a verdict): Polymarket sports
#: taker fee modelled like Kalshi's, rate * p * (1 - p) per contract.
POLYMARKET_FEE_RATE = 0.05   # S17 sports rate (diagnostic module; forward.py is authoritative)
KALSHI_FEE_RATE = 0.07


def fee_per_contract(venue: str, price: float) -> float:
    rate = KALSHI_FEE_RATE if venue == "KALSHI" else POLYMARKET_FEE_RATE
    return rate * price * (1.0 - price)


def load(out: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    flat = lambda stream: [{**item["record"], "observed_at": item["observed_at"]}  # noqa: E731
                           for item in read_stream(out, stream)]
    return flat(PINNACLE), flat(QUOTES_PM) + flat(QUOTES_KALSHI)


def closing_snapshot(pinnacle: Iterable[dict[str, Any]], event_id: str) -> dict[str, Any] | None:
    """Latest pre-kickoff Pinnacle snapshot of ``event_id`` (None if there is none)."""
    best = None
    for row in pinnacle:
        if row["event_id"] != event_id:
            continue
        seen, kickoff = parse_time(row["observed_at"]), parse_time(row["commence_time"])
        if seen >= kickoff:
            continue
        if best is None or seen > parse_time(best["observed_at"]):
            best = row
    if best is None:
        return None
    lag = (parse_time(best["commence_time"]) - parse_time(best["observed_at"])).total_seconds() / 60
    return {**best, "closing_lag_min": round(lag, 1), "closing_stale": lag > CLOSE_LAG_FLAG_MIN}


def bet_clv(cost: float, closing_probability: float) -> dict[str, float]:
    return {"clv_prob": closing_probability - cost,
            "clv_return": (closing_probability - cost) / cost}


def find_bets(pinnacle: list[dict[str, Any]], quotes: Iterable[dict[str, Any]],
              threshold: float = 0.02,
              fee: Callable[[str, float], float] = fee_per_contract) -> list[dict[str, Any]]:
    snap = {(row["event_id"], row["observed_at"]): row for row in pinnacle}
    bets: dict[tuple[str, str, str], dict[str, Any]] = {}
    for quote in sorted(quotes, key=lambda q: q["observed_at"]):
        ask = quote.get("best_ask")
        event = quote["odds_event_id"]
        pin = snap.get((event, quote["observed_at"]))       # same run only
        if ask is None or not 0 < ask < 1 or pin is None:
            continue
        if parse_time(quote["observed_at"]) >= parse_time(pin["commence_time"]):
            continue
        fair = devig_power(pin["prices"]).get(quote["outcome"])
        if fair is None:
            continue
        cost = ask + fee(quote["venue"], ask)
        edge = (fair - cost) / cost
        slot = (event, quote["outcome"], quote["venue"])
        if edge >= threshold and slot not in bets:
            bets[slot] = {"odds_event_id": event, "outcome": quote["outcome"],
                          "venue": quote["venue"], "entry_observed_at": quote["observed_at"],
                          "ask": ask, "cost": cost, "fair_at_entry": fair, "edge_at_entry": edge,
                          "commence_time": pin["commence_time"]}
    return list(bets.values())


def evaluate(pinnacle: list[dict[str, Any]], quotes: Iterable[dict[str, Any]],
             results: dict[str, str] | None = None, threshold: float = 0.02,
             fee: Callable[[str, float], float] = fee_per_contract) -> dict[str, Any]:
    """Per-bet CLV and P&L plus a per-event-clustered summary."""
    results = results or {}
    rows = []
    for bet in find_bets(pinnacle, quotes, threshold, fee):
        close = closing_snapshot(pinnacle, bet["odds_event_id"])
        row = dict(bet)
        if close is None:
            row.update({"clv_prob": None, "clv_return": None, "closing_observed_at": None})
        else:
            p_close = devig_power(close["prices"])[bet["outcome"]]
            row.update({"closing_observed_at": close["observed_at"], "p_close": p_close,
                        "closing_lag_min": close["closing_lag_min"],
                        "closing_stale": close["closing_stale"],
                        "entry_is_closing": close["observed_at"] == bet["entry_observed_at"],
                        **bet_clv(bet["cost"], p_close)})
        winner = results.get(bet["odds_event_id"])
        row["pnl"] = None if winner is None else (1.0 if winner == bet["outcome"] else 0.0) - bet["cost"]
        rows.append(row)
    return {"bets": rows, "summary": {"clv_return": _clustered([r for r in rows
                                                               if r["clv_return"] is not None],
                                                              "clv_return"),
                                      "clv_return_fresh_close": _clustered(
                                          [r for r in rows if r["clv_return"] is not None
                                           and not r["closing_stale"]], "clv_return"),
                                      "pnl_per_dollar": _clustered(
                                          [{**r, "ret": r["pnl"] / r["cost"]} for r in rows
                                           if r["pnl"] is not None], "ret")}}


def _clustered(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    """Mean and t of per-event means (outcomes/venues of one match are one unit)."""
    events: dict[str, list[float]] = {}
    for row in rows:
        events.setdefault(row["odds_event_id"], []).append(row[field])
    units = [sum(v) / len(v) for v in events.values()]
    n = len(units)
    if n == 0:
        return {"bets": 0, "events": 0, "mean": None, "t": None}
    mean = sum(units) / n
    if n < 2:
        return {"bets": len(rows), "events": n, "mean": mean, "t": None}
    sd = math.sqrt(sum((u - mean) ** 2 for u in units) / (n - 1))
    return {"bets": len(rows), "events": n, "mean": mean,
            "t": mean / (sd / math.sqrt(n)) if sd > 0 else None}
