"""H-005 pure analysis: fade new Hyperliquid perp listings (paper/shadow research only).

No I/O, no network. Inputs are parsed raw API rows; outputs are per-event returns
and statistics. Pre-registered grid (do not change): holding_days {7,14,30} x
hedge {none, long BTC equal notional}.

Point-in-time rules
* Listing day L = first daily candle with trades (n > 0). Zero-volume rows that
  precede it are venue backfill of an external index, not trading, and are ignored.
* Venue start = earliest listing day in the universe. Coins listed ON that day were
  present at the start of the data and are not new listings (excluded).
* Entry = open of day L+1 (never the listing-day candle, which is partial and is the
  day the listing becomes known). Exit = open of day L+1+H.
* Delisted before exit: exit at the last available close, flagged; nothing filled.
* Not delisted but exit day beyond the data horizon: event incomplete for that H.
"""
from __future__ import annotations

import datetime as dt
import math
import statistics
from typing import Any

DAY_MS = 86_400_000
GRID = [(h, hedge) for h in (7, 14, 30) for hedge in ("none", "btc")]
COST_ALT = 0.0015   # 15 bp one-way taker + slippage, new-listing leg
COST_BTC = 0.0005   # 5 bp one-way, BTC leg
SPLIT = (0.55, 0.30)  # discovery, validation; remaining 15% untouched


def day_of(ms: int) -> dt.date:
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).date()


def day_ms(day: dt.date) -> int:
    return int(dt.datetime(day.year, day.month, day.day, tzinfo=dt.timezone.utc).timestamp() * 1000)


def parse_candles(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = [{"day": day_of(r["t"]), "t": int(r["t"]), "T": int(r["T"]), "o": float(r["o"]),
            "c": float(r["c"]), "v": float(r["v"]), "n": int(r["n"])} for r in rows]
    out.sort(key=lambda r: r["t"])
    return out


def listing_day(candles: list[dict[str, Any]]) -> dt.date | None:
    for row in candles:
        if row["n"] > 0:
            return row["day"]
    return None


def build_events(universe: dict[str, list[dict[str, Any]]], delisted: set[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Every coin first traded strictly after the venue start, time-ordered by listing day."""
    listed = {coin: listing_day(c) for coin, c in universe.items()}
    listed = {k: v for k, v in listed.items() if v is not None}
    venue_start = min(listed.values())
    events, excluded = [], []
    for coin, day in listed.items():
        if day <= venue_start:
            excluded.append(coin)
            continue
        events.append({"coin": coin, "listing_day": day, "delisted": coin in delisted,
                       "backfill_prefix": universe[coin][0]["n"] == 0})
    events.sort(key=lambda e: (e["listing_day"], e["coin"]))
    return events, {"venue_start": venue_start.isoformat(), "excluded_present_at_start": sorted(excluded)}


def split_events(events: list[dict[str, Any]]) -> tuple[list, list, list]:
    """Chronological split. The last 15% is returned only so callers can count it."""
    n = len(events)
    n_disc, n_val = int(n * SPLIT[0]), int(n * SPLIT[1])
    return events[:n_disc], events[n_disc:n_disc + n_val], events[n_disc + n_val:]


def window(candles: list[dict[str, Any]], listing: dt.date, holding_days: int,
           delisted: bool) -> dict[str, Any] | None:
    """Entry/exit prices for one event, or None if not evaluable (with no fill-in)."""
    by_day = {r["day"]: r for r in candles}
    entry_day = listing + dt.timedelta(days=1)
    exit_day = entry_day + dt.timedelta(days=holding_days)
    entry = by_day.get(entry_day)
    if entry is None:
        return None  # no entry candle: never substitute the listing day or a later day
    last = candles[-1]
    ex = by_day.get(exit_day)
    if ex is not None:
        return {"entry": entry, "p0": entry["o"], "p1": ex["o"], "t0": entry["t"], "t1": ex["t"],
                "exit_kind": "open", "hold": [r for r in candles if entry["t"] <= r["t"] < ex["t"]]}
    later = [r for r in candles if r["day"] > exit_day]
    if later:  # interior gap: next traded open, flagged
        ex = later[0]
        return {"entry": entry, "p0": entry["o"], "p1": ex["o"], "t0": entry["t"], "t1": ex["t"],
                "exit_kind": "gap_next_open", "hold": [r for r in candles if entry["t"] <= r["t"] < ex["t"]]}
    if delisted and last["day"] >= entry_day:
        return {"entry": entry, "p0": entry["o"], "p1": last["c"], "t0": entry["t"], "t1": last["T"] + 1,
                "exit_kind": "delisted_last_close", "hold": [r for r in candles if r["t"] >= entry["t"]]}
    return None  # still listed but window beyond data horizon: incomplete


def price_at(candles_by_day: dict[dt.date, dict[str, Any]], ms: int) -> float | None:
    row = candles_by_day.get(day_of(ms))
    return row["o"] if row else None


def funding_sum(rows: list[dict[str, Any]], t0: int, t1: int, p0: float,
                candles_by_day: dict[dt.date, dict[str, Any]]) -> tuple[float, int]:
    """Sum of hourly funding rates in [t0, t1) weighted by notional drift (day open / entry).

    Positive = longs pay shorts. Returned as the amount a LONG pays per unit of
    entry notional; a short receives the same amount.
    """
    total, count, last_px = 0.0, 0, p0
    seen = set()
    for r in rows:
        t = int(r["time"])
        if not (t0 <= t < t1) or t in seen:
            continue
        seen.add(t)
        px = price_at(candles_by_day, t) or last_px
        last_px = px
        total += float(r["fundingRate"]) * px / p0
        count += 1
    return total, count


def event_returns(ev: dict[str, Any], candles: list[dict[str, Any]], funding: list[dict[str, Any]],
                  btc: list[dict[str, Any]], btc_funding: list[dict[str, Any]], holding_days: int,
                  cost_mult: float = 1.0) -> dict[str, Any] | None:
    w = window(candles, ev["listing_day"], holding_days, ev["delisted"])
    if w is None:
        return None
    ca, cb = COST_ALT * cost_mult, COST_BTC * cost_mult
    by_day = {r["day"]: r for r in candles}
    btc_by_day = {r["day"]: r for r in btc}
    rel = w["p1"] / w["p0"]
    f_alt, n_f = funding_sum(funding, w["t0"], w["t1"], w["p0"], by_day)
    short_net = (1 - rel) - ca * (1 + rel) + f_alt
    b0 = btc_by_day[day_of(w["t0"])]["o"]
    if w["exit_kind"] == "delisted_last_close":
        b1 = btc_by_day[day_of(w["t1"] - 1)]["c"]  # same timestamp as the alt exit
    else:
        b1 = btc_by_day[day_of(w["t1"])]["o"]
    brel = b1 / b0
    f_btc, _ = funding_sum(btc_funding, w["t0"], w["t1"], b0, btc_by_day)
    btc_long = (brel - 1) - cb * (1 + brel) - f_btc
    short_btc = (1 - brel) - cb * (1 + brel) + f_btc
    notional = [r["v"] * r["c"] for r in w["hold"]]
    return {"coin": ev["coin"], "listing_day": ev["listing_day"].isoformat(), "H": holding_days,
            "exit_kind": w["exit_kind"], "gross_short": 1 - rel, "funding_short": f_alt,
            "funding_hours": n_f, "short_net": short_net, "hedged_net": short_net + btc_long,
            "short_btc_net": short_btc,
            "capacity_usd": 0.01 * statistics.median(notional) if notional else 0.0}


# ---------------------------------------------------------------- statistics
def t_event(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    sd = statistics.stdev(xs)
    return statistics.fmean(xs) / (sd / math.sqrt(len(xs))) if sd else 0.0


def listing_week(day: str) -> tuple[int, int]:
    iso = dt.date.fromisoformat(day).isocalendar()
    return (iso[0], iso[1])


def t_clustered(xs: list[float], clusters: list[Any]) -> float:
    """CR1 cluster-robust t of the mean (clusters = listing ISO week)."""
    n = len(xs)
    groups: dict[Any, float] = {}
    if n < 2:
        return 0.0
    m = statistics.fmean(xs)
    for x, g in zip(xs, clusters):
        groups[g] = groups.get(g, 0.0) + (x - m)
    G = len(groups)
    if G < 2:
        return 0.0
    var = G / (G - 1) * sum(s * s for s in groups.values()) / (n * n)
    return m / math.sqrt(var) if var > 0 else 0.0


def summarize(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    xs = [r[key] for r in rows]
    weeks = [listing_week(r["listing_day"]) for r in rows]
    te, tc = t_event(xs), t_clustered(xs, weeks)
    return {"n": len(xs), "clusters": len(set(weeks)), "mean": statistics.fmean(xs) if xs else 0.0,
            "median": statistics.median(xs) if xs else 0.0,
            "hit_rate": sum(x > 0 for x in xs) / len(xs) if xs else 0.0,
            "t_event": te, "t_cluster": tc, "t": min(te, tc)}


def top_decile_share(xs: list[float]) -> float:
    """Share of total net P&L contributed by the best 10% of events (inf if total <= 0)."""
    total = sum(xs)
    if total <= 0:
        return math.inf
    k = max(1, math.ceil(0.10 * len(xs)))
    return sum(sorted(xs, reverse=True)[:k]) / total
