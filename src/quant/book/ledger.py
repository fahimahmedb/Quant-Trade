"""The persistent Book.

``QUANT_NORTH_STAR.md``: the same bankroll carries forward through time, with
no fresh seed per experiment, session, restart or build task. Every number the
status surface shows about money comes from here.

Two ledgers exist, sharing this implementation:

``CAPITAL``      the authoritative paper/shadow bankroll; only strategies in a
                 tradable lifecycle state may touch it.
``EVALUATION``   a zero-authority counterfactual ledger that records what
                 rejected opportunities would have done. It exists to measure
                 false rejects, which the North Star requires the system to
                 learn from. It never affects NAV.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ..state import read_json, utc_now, write_json


AUTHORITIES = ("CAPITAL", "EVALUATION")


@dataclass
class Position:
    symbol: str
    quantity: float = 0.0
    average_price: float = 0.0
    last_price: float = 0.0
    realized_pnl: float = 0.0
    opened_at: str | None = None
    strategy_id: str | None = None

    @property
    def market_value(self) -> float:
        return self.quantity * self.last_price

    @property
    def unrealized_pnl(self) -> float:
        return self.quantity * (self.last_price - self.average_price)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LedgerState:
    ledger_id: str
    authority: str = "CAPITAL"
    mode: str = "paper_shadow"
    currency: str = "USD"
    initial_capital: float = 1_000_000.0
    cash: float = 1_000_000.0
    inception: str = field(default_factory=utc_now)
    inception_date: str | None = None
    last_session_date: str | None = None
    sessions: int = 0
    realized_pnl: float = 0.0
    fees_paid: float = 0.0
    positions: dict[str, dict[str, Any]] = field(default_factory=dict)
    nav_history: list[dict[str, Any]] = field(default_factory=list)
    attribution: dict[str, dict[str, float]] = field(default_factory=dict)
    peak_nav: float = 1_000_000.0
    fills: int = 0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class Ledger:
    """Restart-safe double-entry-lite accounting over a persistent JSON document."""

    def __init__(self, path: Path, ledger_id: str = "quant-shadow-book",
                 authority: str = "CAPITAL", initial_capital: float = 1_000_000.0):
        if authority not in AUTHORITIES:
            raise ValueError(f"unknown ledger authority: {authority}")
        self.path = path
        payload = read_json(path)
        if payload is None:
            self.state = LedgerState(ledger_id=ledger_id, authority=authority,
                                     initial_capital=initial_capital, cash=initial_capital,
                                     peak_nav=initial_capital)
            self.save()
        else:
            self.state = LedgerState(**payload)
        self.positions: dict[str, Position] = {
            symbol: Position(**value) for symbol, value in self.state.positions.items()}

    # --- persistence -------------------------------------------------------
    def save(self) -> None:
        self.state.positions = {symbol: position.to_dict()
                                for symbol, position in getattr(self, "positions", {}).items()
                                if abs(position.quantity) > 1e-9}
        write_json(self.path, self.state.to_dict())

    # --- accounting --------------------------------------------------------
    def apply_fill(self, symbol: str, quantity: float, price: float, cost: float,
                   date: str, strategy_id: str | None = None) -> dict[str, Any]:
        """Book a fill. ``quantity`` is signed; ``cost`` is the total frictional charge."""
        position = self.positions.setdefault(symbol, Position(symbol=symbol, opened_at=date,
                                                              strategy_id=strategy_id))
        realized = 0.0
        if position.quantity != 0 and (position.quantity > 0) != (quantity > 0):
            closing = min(abs(quantity), abs(position.quantity))
            direction = 1.0 if position.quantity > 0 else -1.0
            realized = direction * closing * (price - position.average_price)
            position.realized_pnl += realized
            self.state.realized_pnl += realized
        new_quantity = position.quantity + quantity
        if position.quantity == 0 or (position.quantity > 0) == (quantity > 0):
            total = position.average_price * position.quantity + price * quantity
            position.average_price = total / new_quantity if new_quantity else 0.0
        elif abs(new_quantity) > 1e-9 and (new_quantity > 0) != (position.quantity > 0):
            position.average_price = price  # Position flipped; the new side starts here.
        position.quantity = new_quantity
        position.last_price = price
        if strategy_id:
            position.strategy_id = strategy_id
        if abs(position.quantity) <= 1e-9:
            position.quantity = 0.0
            position.average_price = 0.0
        self.state.cash -= quantity * price
        self.state.cash -= cost
        self.state.fees_paid += cost
        self.state.fills += 1
        if strategy_id:
            bucket = self.state.attribution.setdefault(
                strategy_id, {"realized_pnl": 0.0, "costs": 0.0, "fills": 0.0, "notional": 0.0})
            bucket["realized_pnl"] += realized
            bucket["costs"] += cost
            bucket["fills"] += 1
            bucket["notional"] += abs(quantity * price)
        # A fill changes economic reality, so it is durable before it is reported:
        # a process killed between the fill and the next mark must not lose it.
        self.save()
        return {"symbol": symbol, "quantity": quantity, "price": price, "cost": cost,
                "realized_pnl": realized, "cash_after": self.state.cash}

    def mark_to_market(self, date: str, prices: dict[str, float]) -> dict[str, Any]:
        """Revalue open positions and append one point to the persistent NAV history."""
        for symbol, position in self.positions.items():
            if symbol in prices:
                position.last_price = prices[symbol]
        market_value = sum(position.market_value for position in self.positions.values())
        unrealized = sum(position.unrealized_pnl for position in self.positions.values())
        nav = self.state.cash + market_value
        gross = sum(abs(position.market_value) for position in self.positions.values())
        net = market_value
        if self.state.inception_date is None:
            self.state.inception_date = date
        self.state.last_session_date = date
        self.state.sessions += 1
        self.state.peak_nav = max(self.state.peak_nav, nav)
        point = {"date": date, "nav": nav, "cash": self.state.cash,
                 "market_value": market_value, "unrealized_pnl": unrealized,
                 "realized_pnl": self.state.realized_pnl, "fees_paid": self.state.fees_paid,
                 "gross_exposure": gross, "net_exposure": net,
                 "open_positions": sum(1 for p in self.positions.values() if p.quantity)}
        self.state.nav_history.append(point)
        self.save()
        return point

    # --- reporting ---------------------------------------------------------
    @property
    def nav(self) -> float:
        return self.state.cash + sum(position.market_value for position in self.positions.values())

    @property
    def drawdown(self) -> float:
        peak = max(self.state.peak_nav, self.state.initial_capital)
        return self.nav / peak - 1.0 if peak else 0.0

    @property
    def total_return(self) -> float:
        return self.nav / self.state.initial_capital - 1.0 if self.state.initial_capital else 0.0

    def exposures(self) -> dict[str, float]:
        nav = self.nav or 1.0
        gross = sum(abs(position.market_value) for position in self.positions.values())
        net = sum(position.market_value for position in self.positions.values())
        return {"gross": gross, "net": net, "gross_ratio": gross / nav, "net_ratio": net / nav}

    def open_positions(self) -> list[dict[str, Any]]:
        return sorted((position.to_dict() | {"market_value": position.market_value,
                                             "unrealized_pnl": position.unrealized_pnl}
                       for position in self.positions.values() if position.quantity),
                      key=lambda item: item["symbol"])

    def summary(self) -> dict[str, Any]:
        exposures = self.exposures()
        return {"ledger_id": self.state.ledger_id, "authority": self.state.authority,
                "mode": self.state.mode, "currency": self.state.currency,
                "initial_capital": self.state.initial_capital, "nav": self.nav,
                "cash": self.state.cash, "total_return": self.total_return,
                "realized_pnl": self.state.realized_pnl,
                "unrealized_pnl": sum(p.unrealized_pnl for p in self.positions.values()),
                "fees_paid": self.state.fees_paid, "drawdown": self.drawdown,
                "sessions": self.state.sessions, "fills": self.state.fills,
                "inception_date": self.state.inception_date,
                "last_session_date": self.state.last_session_date,
                "open_positions": len(self.open_positions()),
                "gross_exposure_ratio": exposures["gross_ratio"],
                "net_exposure_ratio": exposures["net_ratio"],
                "attribution": self.state.attribution}
