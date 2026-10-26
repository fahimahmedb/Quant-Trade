"""Execution modelling (FILLS).

A paper system that fills at the signal price is not paper trading, it is
wishful thinking. This model charges commission, half the quoted spread and a
size-dependent impact, fills at the *next* session's open rather than the price
that generated the signal, and refuses to pretend it can trade more than a
plausible share of a day's volume.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import date
from typing import Any

from ..dataplane.panel import PricePanel


#: One-way cost per unit of notional assumed by the Research Factory. The desk
#: model below is calibrated to land at or under this, so research evidence is
#: conservative relative to modelled execution rather than flattering.
RESEARCH_ONE_WAY_COST_BPS = 5.0


@dataclass(frozen=True)
class ExecutionModel:
    commission_bps: float = 0.5
    half_spread_bps: float = 1.0
    impact_bps_at_full_participation: float = 10.0
    max_participation: float = 0.05
    adv_lookback_days: int = 20

    def __post_init__(self) -> None:
        for value in (self.commission_bps, self.half_spread_bps,
                      self.impact_bps_at_full_participation, self.max_participation):
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise ValueError("execution parameters must be finite and nonnegative")
        if not 0 < self.max_participation <= 1:
            raise ValueError("execution participation must be in (0, 1]")
        if type(self.adv_lookback_days) is not int or self.adv_lookback_days < 1:
            raise ValueError("ADV lookback must be a positive integer")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def adv(self, panel: PricePanel, symbol: str, date: str) -> float:
        """Average daily traded notional over the lookback, in adjusted terms."""
        available = panel.dates_for(symbol)
        recent = [value for value in available if value <= date][-self.adv_lookback_days:]
        if not recent:
            return 0.0
        notionals = []
        for day in recent:
            close, volume = panel.price(day, symbol, "close"), panel.price(day, symbol, "volume")
            if (not math.isfinite(close) or close <= 0
                    or not math.isfinite(volume) or volume < 0):
                raise ValueError("ADV requires finite positive prices and nonnegative volume")
            notionals.append(close * volume)
        return sum(notionals) / len(recent)

    def fill(self, panel: PricePanel, symbol: str, quantity: float, signal_date: str,
             execution_date: str) -> dict[str, Any]:
        """Model one order. Returns the (possibly capacity-truncated) fill."""
        if date.fromisoformat(execution_date) <= date.fromisoformat(signal_date):
            raise ValueError("execution must occur after the signal session")
        if type(quantity) not in (int, float) or not math.isfinite(quantity):
            raise ValueError("execution quantity must be finite")
        reference = panel.adjusted(execution_date, symbol, "open")
        adv = self.adv(panel, symbol, signal_date)
        if not math.isfinite(reference) or reference <= 0 or not math.isfinite(adv) or adv <= 0:
            raise ValueError("execution requires a positive finite reference and signal-time ADV")
        capacity = adv * self.max_participation
        requested_notional = abs(quantity) * reference
        truncated = False
        if capacity > 0 and requested_notional > capacity:
            quantity = math.copysign(capacity / reference, quantity)
            requested_notional = capacity
            truncated = True
        participation = requested_notional / adv
        impact_bps = self.impact_bps_at_full_participation * math.sqrt(
            min(participation, 1.0) / self.max_participation) if participation > 0 else 0.0
        side = 1.0 if quantity > 0 else -1.0
        slippage_bps = self.half_spread_bps + impact_bps
        price = reference * (1.0 + side * slippage_bps / 10_000.0)
        cost = abs(quantity) * price * self.commission_bps / 10_000.0
        if not math.isfinite(price) or price <= 0 or not math.isfinite(cost):
            raise ValueError("execution produced an invalid price or commission")
        return {"symbol": symbol, "quantity": quantity, "reference_price": reference,
                "fill_price": price, "commission": cost,
                "slippage_bps": slippage_bps, "impact_bps": impact_bps,
                "participation": participation, "capacity_truncated": truncated,
                "notional": abs(quantity) * price, "signal_date": signal_date,
                "execution_date": execution_date,
                "implementation_shortfall": abs(quantity) * abs(price - reference) + cost}
