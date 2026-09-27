"""Settlement P&L of the passive (maker) side of Kalshi public trades (H-004).

Pure, stdlib-only logic. No network, no state. Prices are integer cents of the
YES leg (1..99); contract counts may be fractional (Kalshi prints ``count_fp``).

Sign convention (per contract, cents, held to settlement, Y = 1 if YES won):

* taker bought YES at p  -> the maker sold YES at p   -> P&L = p - 100*Y
* taker bought NO        -> the maker bought YES at p -> P&L = 100*Y - p

Maker fee (Kalshi fee schedule, https://kalshi.com/docs/kalshi-fee-schedule.pdf,
"maker fees" on markets that carry them):

    fee = round_up_to_cent(0.0175 * C * P * (1 - P))   dollars, P = price in dollars

The published rule rounds per order. Public trades do not identify orders, so
the fee is rounded up *per trade print* (one fill can only be split into more
prints, never merged), which is at least as costly as the published rule. It is
charged on every market even where Kalshi waives maker fees: conservative.

Limits: this is a measurement of the tape, not a strategy simulation. There is
no queue or fill model; a real quoter would receive only a subset of these
fills, plausibly the most adversely selected ones.
"""

from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Mapping, Sequence

MAKER_FEE_RATE = Fraction(175, 10000)  # 0.0175
FEE_SOURCE = "https://kalshi.com/docs/kalshi-fee-schedule.pdf"
FEE_FORMULA = "ceil_to_cent(0.0175 * C * P * (1 - P)) per trade print, P in dollars"

_MONTHS = {m: i + 1 for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"])}


def to_fraction(value: str | int | float | Fraction) -> Fraction:
    """Exact decimal -> Fraction (``"3.10"`` -> 31/10)."""
    if isinstance(value, Fraction):
        return value
    if isinstance(value, float):
        return Fraction(repr(value))
    return Fraction(str(value))


def price_cents(dollars: str) -> int:
    """``"0.0700"`` -> 7. Rejects sub-cent prices (weather markets are linear_cent)."""
    cents = to_fraction(dollars) * 100
    if cents.denominator != 1:
        raise ValueError(f"sub-cent price {dollars!r}")
    return int(cents)


def maker_pnl_cents(taker_side: str, yes_price: int, yes_won: bool) -> int:
    """Per-contract settlement P&L of the resting side, before fees (cents)."""
    if not 1 <= yes_price <= 99:
        raise ValueError(f"yes_price out of range: {yes_price}")
    y = 100 if yes_won else 0
    if taker_side == "yes":
        return yes_price - y
    if taker_side == "no":
        return y - yes_price
    raise ValueError(f"taker_side must be 'yes' or 'no', got {taker_side!r}")


def maker_fee_cents(count: str | Fraction | int, yes_price: int) -> int:
    """Maker fee of one trade print in whole cents, rounded up (conservative)."""
    c = to_fraction(count)
    if c <= 0:
        raise ValueError("count must be positive")
    fee = MAKER_FEE_RATE * c * yes_price * (100 - yes_price) / 100  # cents
    return math.ceil(fee)


def event_date(event_ticker: str) -> dt.date:
    """``KXHIGHNY-26JUL15`` -> 2026-07-15 (Kalshi ``YYMONDD`` suffix, optional hour)."""
    code = event_ticker.split("-")[1]
    return dt.date(2000 + int(code[:2]), _MONTHS[code[2:5]], int(code[5:7]))


def parse_ts(value: str) -> dt.datetime:
    text = value.replace("Z", "+00:00")
    if "." in text:  # normalise fractional seconds to 6 digits for fromisoformat
        head, rest = text.split(".", 1)
        frac, tz = rest[:rest.index("+")], rest[rest.index("+"):]
        text = f"{head}.{(frac + '000000')[:6]}{tz}"
    return dt.datetime.fromisoformat(text)


def trade_is_eligible(trade_time: str, close_time: str, result: str, block: bool) -> bool:
    """A print counts only if the market settled yes/no, it is a book trade and
    it printed no later than the market's close."""
    if result not in ("yes", "no") or block:
        return False
    return parse_ts(trade_time) <= parse_ts(close_time)


@dataclass(frozen=True)
class Cluster:
    """Sum of net P&L (cents) and contracts of one cluster (market or date)."""

    key: str
    pnl: float
    contracts: float


def clustered_mean(clusters: Sequence[Cluster]) -> dict[str, float]:
    """Contract-weighted mean P&L per contract with a cluster-robust SE.

    mean = sum S_g / sum N_g ;  var = G/(G-1) * sum (S_g - mean*N_g)^2 / (sum N_g)^2
    """
    g = len(clusters)
    total_n = sum(c.contracts for c in clusters)
    if g < 2 or total_n <= 0:
        return {"mean": float("nan"), "se": float("nan"), "t": float("nan"), "clusters": g}
    mean = sum(c.pnl for c in clusters) / total_n
    ss = sum((c.pnl - mean * c.contracts) ** 2 for c in clusters)
    se = math.sqrt(g / (g - 1) * ss) / total_n
    return {"mean": mean, "se": se, "t": mean / se if se > 0 else float("inf"), "clusters": g}


def aggregate(rows: Iterable[Mapping], key: str) -> list[Cluster]:
    """Group derived rows (``net_pnl_cents``/``contracts``) into clusters by ``key``."""
    pnl: dict[str, float] = {}
    n: dict[str, float] = {}
    for r in rows:
        k = str(r[key])
        pnl[k] = pnl.get(k, 0.0) + float(r["net_pnl_cents"])
        n[k] = n.get(k, 0.0) + float(r["contracts"])
    return [Cluster(k, pnl[k], n[k]) for k in sorted(pnl)]


def top_share(clusters: Sequence[Cluster], fraction: float = 0.10) -> float:
    """Share of total P&L produced by the top ``fraction`` of clusters by P&L.

    Returns +inf when total P&L is <= 0 (the concentration test cannot pass).
    """
    total = sum(c.pnl for c in clusters)
    if total <= 0:
        return float("inf")
    k = max(1, math.ceil(len(clusters) * fraction))
    top = sorted((c.pnl for c in clusters), reverse=True)[:k]
    return sum(top) / total
