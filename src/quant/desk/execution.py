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

#: Execution phases this one authority supports. Both are the same model,
#: same cost mechanics, same fill call — only the label and the caller's
#: chosen ``execution_date`` differ. ``ENTRY`` fills at the next session's
#: open under the causal timeline already documented above. ``SCHEDULED_EXIT``
#: fills the position the science protocol's frozen holding convention
#: already determined must close, at that predetermined session's open. This
#: is the "narrow explicit execution-phase extension for the same model"
#: authorized by the frozen build spec (§5 / §2.5-2.6) precisely so a second
#: ExecutionModel is never created to carry the exit leg.
PHASE_ENTRY = "ENTRY"
PHASE_SCHEDULED_EXIT = "SCHEDULED_EXIT"
EXECUTION_PHASES = (PHASE_ENTRY, PHASE_SCHEDULED_EXIT)


class UnknownExecutionPhase(ValueError):
    """An execution phase outside :data:`EXECUTION_PHASES`. Fails closed."""


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

    def fill(self, panel: PricePanel, symbol: str, quantity: float, signal_date: str,
             execution_date: str, phase: str = PHASE_ENTRY) -> dict[str, Any]:
        """Model one order. Returns the (possibly capacity-truncated) fill.

        ``phase`` must be one of :data:`EXECUTION_PHASES`; an unrecognised
        phase fails closed with :class:`UnknownExecutionPhase` rather than
        silently defaulting to entry semantics. The mechanics are identical
        for both declared phases — the caller (Desk) is responsible for
        supplying the correct ``execution_date`` for the phase, i.e. the next
        session's open for ``ENTRY`` and the frozen scheduled-exit session's
        open for ``SCHEDULED_EXIT``.
        """
        if phase not in EXECUTION_PHASES:
            raise UnknownExecutionPhase(
                f"UNKNOWN_EXECUTION_PHASE: {phase!r} not in {EXECUTION_PHASES}")
        reference = panel.adjusted(execution_date, symbol, "open")
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
                "execution_date": execution_date, "phase": phase,
                "implementation_shortfall": abs(quantity) * abs(price - reference) + cost}
