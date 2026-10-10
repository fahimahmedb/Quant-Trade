"""Synthetic-tested FX sizing/fill primitives; not an economic backtest runner.

No download, price-file reader, parameter search, result rerun or trade route.
PREREGISTRATION.md governs. Complete signal/lifecycle harness remains a gate.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import floor, isfinite
from zoneinfo import ZoneInfo

PIP = 0.0001
LATENCY_MS = 1000
OPEN_DEADLINE_MS = 5000


@dataclass(frozen=True)
class Quote:
    time_ms: int
    bid: float
    ask: float

    def __post_init__(self):
        if (not isinstance(self.time_ms, int) or isinstance(self.time_ms, bool)
                or not isfinite(self.bid) or not isfinite(self.ask)
                or self.bid <= 0 or self.ask < self.bid):
            raise ValueError("invalid quote")

    @property
    def mid(self):
        return (self.bid + self.ask) / 2


@dataclass(frozen=True)
class Costs:
    spread_multiplier: float
    commission: float
    slippage: float
    rollover_pips: float


CENTRAL = Costs(1.0, .5 * PIP, .25 * PIP, 1.0)
STRESS = Costs(2.0, 1.0 * PIP, .5 * PIP, 2.0)


def source_time_utc(value: str) -> datetime:
    """HistData fixed EST, deliberately not America/New_York."""
    if len(value) != 18 or value[8] != " ":
        raise ValueError("timestamp schema")
    base = datetime.strptime(value[:15], "%Y%m%d %H%M%S")
    # Format has eight date + space + six time + three millisecond digits.
    if not value[15:].isdigit() or len(value[15:]) != 3:
        raise ValueError("milliseconds")
    return (base.replace(microsecond=int(value[15:]) * 1000,
                         tzinfo=timezone(timedelta(hours=-5)))
            .astimezone(timezone.utc))


def envelope(group: list[Quote]) -> Quote:
    if not group or any(q.time_ms != group[0].time_ms for q in group):
        raise ValueError("not a single timestamp group")
    return Quote(group[0].time_ms, min(q.bid for q in group),
                 max(q.ask for q in group))


def sides(quote: Quote, costs: Costs) -> tuple[float, float]:
    half = (quote.ask - quote.bid) / 2 * costs.spread_multiplier
    return quote.mid - half, quote.mid + half


def _direction(direction: int):
    if direction not in (-1, 1):
        raise ValueError("direction")


def opening_fill(trigger: Quote, delayed: Quote, direction: int, costs: Costs):
    """Trigger carries intent time and then-known sides; None cancels expiry.

    Caller separately retains the underlying source timestamp and rejects an
    initial quote older than five seconds. Never use its old time as intent.
    """
    _direction(direction)
    elapsed = delayed.time_ms - trigger.time_ms
    if elapsed < LATENCY_MS:
        raise ValueError("pre-latency opening")
    if elapsed > LATENCY_MS + OPEN_DEADLINE_MS:
        return None
    b0, a0 = sides(trigger, costs)
    b1, a1 = sides(delayed, costs)
    return (max(a0, a1) + costs.slippage if direction == 1
            else min(b0, b1) - costs.slippage)


def closing_fill(trigger: Quote, delayed: Quote, direction: int, costs: Costs,
                 *, stop: float | None = None):
    """Closes do not expire; stale/stop closes can include the fixed stop bound."""
    _direction(direction)
    if delayed.time_ms - trigger.time_ms < LATENCY_MS:
        raise ValueError("pre-latency closing")
    b0, a0 = sides(trigger, costs)
    b1, a1 = sides(delayed, costs)
    if stop is not None and (not isfinite(stop) or stop <= 0):
        raise ValueError("stop")
    values = [b0, b1] if direction == 1 else [a0, a1]
    if stop is not None:
        values.append(stop)
    return (min(values) - costs.slippage if direction == 1
            else max(values) + costs.slippage)


def planned_quantity(equity: float, anchor: float, spacing: float,
                     risk: float, rungs: int) -> int:
    if (rungs not in (1, 3) or any(not isfinite(x) or x <= 0
            for x in (equity, anchor, spacing, risk)) or risk > .0025 * equity
            or anchor <= 3 * spacing):
        raise ValueError("invalid finite basket plan")
    per_unit_loss = sum((3-k)*spacing + PIP
                        + 2*(STRESS.commission+STRESS.slippage)
                        for k in range(rungs))
    return floor(min(risk / per_unit_loss,
                     equity / (rungs*(anchor+3*spacing+2*PIP))))


def fill_admissible(entries: list[tuple[int, float]], quantity: int,
                    entry_price: float, stop: float, direction: int,
                    paid_commission: float, risk: float,
                    marked_equity: float, marked_mid: float) -> bool:
    """Never reduce a rung to force a fill. Gap loss can still exceed the plan."""
    _direction(direction)
    if (quantity < 1 or len(entries) >= 3 or marked_equity <= 0
            or marked_mid <= 0 or paid_commission < 0):
        return False
    all_entries = entries + [(quantity, entry_price)]
    if any(q < 1 or not isfinite(p) or p <= 0
           or direction*(p-stop) < 0 for q, p in all_entries):
        return False
    total_q = sum(q for q, _ in all_entries)
    # Actual opening slippage is in p; commission is paid separately.
    loss = (sum(q*direction*(p-stop) for q, p in all_entries)
            + paid_commission + quantity*STRESS.commission
            + total_q*(STRESS.commission+STRESS.slippage))
    gross = total_q * marked_mid
    margin = gross / 30
    return loss <= risk and gross <= marked_equity and margin <= .05*marked_equity


def stale_trigger(last: Quote, next_quote: Quote) -> Quote | None:
    if next_quote.time_ms < last.time_ms:
        raise ValueError("nonmonotone source")
    if next_quote.time_ms - last.time_ms > 5000:
        return Quote(last.time_ms + 5000, last.bid, last.ask)
    return None


def rollover_charge(entry: datetime, exit: datetime, quantity: int,
                    costs: Costs) -> tuple[float, int]:
    """Includes exit-at-rollover, excludes entry-at-rollover. Wed triple."""
    if entry.tzinfo is None or exit.tzinfo is None or exit < entry or quantity < 0:
        raise ValueError("rollover interval")
    ny = ZoneInfo("America/New_York")
    day = entry.astimezone(ny).date()
    end = exit.astimezone(ny).date()
    charge, count = 0.0, 0
    while day <= end:
        roll = datetime(day.year, day.month, day.day, 17, tzinfo=ny)
        if entry < roll <= exit:
            charge += quantity*costs.rollover_pips*PIP*(3 if day.weekday()==2 else 1)
            count += 1
        day += timedelta(days=1)
    return charge, count
