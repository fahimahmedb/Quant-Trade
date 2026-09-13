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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def adv(self, panel: PricePanel, symbol: str, date: str) -> float:
        """Average daily traded notional over the lookback, in adjusted terms."""
        available = panel.dates_for(symbol)
        recent = [value for value in available if value <= date][-self.adv_lookback_days:]
        if not recent:
            return 0.0
        return sum(panel.price(day, symbol, "close") * panel.price(day, symbol, "volume")
                   for day in recent) / len(recent)

    @staticmethod
    def adjusted(panel: PricePanel, date: str, symbol: str, field: str) -> float:
        """Put raw open/high/low on the same adjusted basis as ``adj_close``.

        Marks and fills must share one price basis or the Book drifts against
        its own returns whenever a dividend or split lands.
        """
        close = panel.price(date, symbol, "close")
        if close <= 0:
            return panel.price(date, symbol, "adj_close")
        factor = panel.price(date, symbol, "adj_close") / close
        return panel.price(date, symbol, field) * factor

    def fill(self, panel: PricePanel, symbol: str, quantity: float, signal_date: str,
             execution_date: str) -> dict[str, Any]:
        """Model one order. Returns the (possibly capacity-truncated) fill."""
        reference = self.adjusted(panel, execution_date, symbol, "open")
        capacity = self.adv(panel, symbol, signal_date) * self.max_participation
        requested_notional = abs(quantity) * reference
        truncated = False
        if capacity > 0 and requested_notional > capacity:
            quantity = math.copysign(capacity / reference, quantity)
            requested_notional = capacity
            truncated = True
        participation = (requested_notional / self.adv(panel, symbol, signal_date)
                         if self.adv(panel, symbol, signal_date) > 0 else 0.0)
        impact_bps = self.impact_bps_at_full_participation * math.sqrt(
            min(participation, 1.0) / self.max_participation) if participation > 0 else 0.0
        side = 1.0 if quantity > 0 else -1.0
        slippage_bps = self.half_spread_bps + impact_bps
        price = reference * (1.0 + side * slippage_bps / 10_000.0)
        cost = abs(quantity) * price * self.commission_bps / 10_000.0
        return {"symbol": symbol, "quantity": quantity, "reference_price": reference,
                "fill_price": price, "commission": cost,
                "slippage_bps": slippage_bps, "impact_bps": impact_bps,
                "participation": participation, "capacity_truncated": truncated,
                "notional": abs(quantity) * price, "signal_date": signal_date,
                "execution_date": execution_date,
                "implementation_shortfall": abs(quantity) * abs(price - reference) + cost}
