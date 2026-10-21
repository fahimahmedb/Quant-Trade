"""The persistent Book.

``QUANT_NORTH_STAR.md``: the same bankroll carries forward through time, with
no fresh seed per experiment, session, restart or build task. Every number the
status surface shows about money comes from here.

Three invariants govern this module.

**Sleeves.** A position is keyed by ``(strategy_id, symbol)``, not by symbol.
Several strategies may hold the same instrument, on opposite sides, without
overwriting each other's attribution. Portfolio state is the aggregate of the
sleeves and is computed, never stored.

**Idempotence.** Every economic mutation carries a deterministic operation id.
Replaying an operation that is already applied is a no-op, so a crash between a
durable fill and the end of a session cannot double-count it on restart.

**Monotonic time.** Marking may not move backward. A mark dated before the last
marked session is a bug in the caller, and a mark repeating the last session
replaces its point rather than appending a second one.

Two ledgers share this implementation:

``CAPITAL``      the authoritative paper/shadow bankroll; only strategies in a
                 tradable lifecycle state may touch it.
``EVALUATION``   a zero-authority counterfactual ledger that records what
                 rejected opportunities would have done. It exists to measure
                 false rejects, which the North Star requires the system to
                 learn from. It never affects NAV.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from copy import deepcopy
from datetime import date as calendar_date
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

from ..state import read_json, utc_now, write_json


AUTHORITIES = ("CAPITAL", "EVALUATION")


class BackwardInTime(ValueError):
    """A mark was dated before the Book's last marked session."""


class LedgerConflict(RuntimeError):
    """Another writer changed the Book; reconsider the operation before retrying."""


@dataclass
class Position:
    """One strategy's holding in one instrument. A sleeve entry, not a symbol total."""

    symbol: str
    strategy_id: str
    quantity: float = 0.0
    average_price: float = 0.0
    last_price: float = 0.0
    realized_pnl: float = 0.0
    opened_at: str | None = None

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
    #: strategy_id -> symbol -> position document
    sleeves: dict[str, dict[str, dict[str, Any]]] = field(default_factory=dict)
    nav_history: list[dict[str, Any]] = field(default_factory=list)
    attribution: dict[str, dict[str, float]] = field(default_factory=dict)
    peak_nav: float = 1_000_000.0
    fills: int = 0
    #: Deterministic ids of every mutation already applied, so replay is a no-op.
    applied_operations: list[str] = field(default_factory=list)
    #: Optional for legacy Books; new fills bind their full economic identity.
    operation_fingerprints: dict[str, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.operation_fingerprints, dict) or any(
                not isinstance(operation, str) or not operation.strip()
                or operation not in self.applied_operations
                or not isinstance(digest, str) or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)
                for operation, digest in self.operation_fingerprints.items()):
            raise ValueError("invalid Book operation identity bindings")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class Ledger:
    """Restart-safe, idempotent accounting over a persistent JSON document."""

    def __init__(self, path: Path, ledger_id: str = "quant-shadow-book",
                 authority: str = "CAPITAL", initial_capital: float = 1_000_000.0):
        if authority not in AUTHORITIES:
            raise ValueError(f"unknown ledger authority: {authority}")
        self.path = path
        self._detached = False
        payload = read_json(path)
        self._persisted = deepcopy(payload)
        if payload is None:
            self.state = LedgerState(ledger_id=ledger_id, authority=authority,
                                     initial_capital=initial_capital, cash=initial_capital,
                                     peak_nav=initial_capital)
            self.sleeves: dict[str, dict[str, Position]] = {}
            self.save()
        else:
            self.state = LedgerState(**payload)
            self.sleeves = {strategy: {symbol: Position(**document)
                                       for symbol, document in holdings.items()}
                            for strategy, holdings in self.state.sleeves.items()}
        self._applied = set(self.state.applied_operations)

    @classmethod
    def from_document(cls, document: dict[str, Any]) -> "Ledger":
        """Build a detached read-only view of a previously persisted Book state.

        The Capital Desk journals one such document at the decision boundary so
        every strategy in a session sees the same close(t) portfolio even if an
        earlier strategy has already modelled an open(t+1) fill, or after a
        crash/restart midway through the session.
        """
        ledger = cls.__new__(cls)
        ledger.path = Path("__detached_decision_ledger__")
        ledger._detached = True
        ledger.state = LedgerState(**deepcopy(document))
        ledger.sleeves = {
            strategy: {symbol: Position(**position)
                       for symbol, position in holdings.items()}
            for strategy, holdings in ledger.state.sleeves.items()}
        ledger._applied = set(ledger.state.applied_operations)
        return ledger

    # --- persistence -------------------------------------------------------
    def _assert_writable(self) -> None:
        if self._detached:
            raise RuntimeError("DETACHED_LEDGER_IS_READ_ONLY")

    def _restore(self, document: dict[str, Any]) -> None:
        self._persisted = deepcopy(document)
        self.state = LedgerState(**deepcopy(document))
        self.sleeves = {
            strategy: {symbol: Position(**position) for symbol, position in holdings.items()}
            for strategy, holdings in self.state.sleeves.items()}
        self._applied = set(self.state.applied_operations)

    def save(self) -> None:
        self._assert_writable()
        self.state.sleeves = {
            strategy: {symbol: position.to_dict() for symbol, position in holdings.items()
                       if abs(position.quantity) > 1e-9}
            for strategy, holdings in self.sleeves.items()}
        self.state.sleeves = {strategy: holdings
                              for strategy, holdings in self.state.sleeves.items() if holdings}
        # Atomic replacement alone does not prevent a stale writer from erasing
        # acknowledged fills. Compare the complete observed state under the same
        # lock used for publication; a conflict requires a fresh caller decision.
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.path.with_name(self.path.name + ".lock"), os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            try:
                if read_json(self.path) != self._persisted:
                    raise LedgerConflict("BOOK_CHANGED_SINCE_READ")
                document = self.state.to_dict()
                write_json(self.path, document)
                self._persisted = deepcopy(document)
            except BaseException:
                # A failed write may precede replacement or follow it (lost
                # acknowledgement). Recover the actual durable state in either
                # case, including the idempotency set, before permitting retry.
                durable = read_json(self.path)
                if durable is not None:
                    self._restore(durable)
                raise
        finally:
            os.close(fd)

    def has_applied(self, operation_id: str) -> bool:
        return operation_id in self._applied

    # --- accounting --------------------------------------------------------
    def apply_fill(self, symbol: str, quantity: float, price: float, cost: float,
                   date: str, strategy_id: str, operation_id: str) -> dict[str, Any]:
        """Book a fill into one strategy's sleeve.

        ``quantity`` is signed and ``cost`` is the total frictional charge.
        ``operation_id`` must be deterministic for the economic event, so that a
        replay after a crash is recognised rather than applied twice.
        """
        self._assert_writable()
        for label, value in (("symbol", symbol), ("strategy_id", strategy_id),
                             ("operation_id", operation_id)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"invalid fill {label}")
        self._validate_date(date)
        for label, value in (("quantity", quantity), ("price", price), ("cost", cost)):
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError(f"invalid fill {label}")
        if quantity == 0 or price <= 0 or cost < 0:
            raise ValueError("fill requires nonzero quantity, positive price and nonnegative cost")
        fingerprint = self._fill_fingerprint(symbol, quantity, price, cost, date, strategy_id)
        if operation_id in self._applied:
            prior = self.state.operation_fingerprints.get(operation_id)
            if prior is None:
                raise LedgerConflict("LEGACY_OPERATION_PAYLOAD_UNVERIFIABLE")
            if prior != fingerprint:
                raise LedgerConflict("OPERATION_IDENTITY_PAYLOAD_MISMATCH")
            return {"symbol": symbol, "quantity": 0.0, "price": price, "cost": 0.0,
                    "realized_pnl": 0.0, "cash_after": self.state.cash,
                    "operation_id": operation_id, "replayed": True}

        holdings = self.sleeves.setdefault(strategy_id, {})
        position = holdings.setdefault(symbol, Position(symbol=symbol, strategy_id=strategy_id,
                                                        opened_at=date))
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
            position.average_price = price
        position.quantity = new_quantity
        position.last_price = price
        if abs(position.quantity) <= 1e-9:
            position.quantity = 0.0
            position.average_price = 0.0
        self.state.cash -= quantity * price
        self.state.cash -= cost
        self.state.fees_paid += cost
        self.state.fills += 1
        bucket = self.state.attribution.setdefault(
            strategy_id, {"realized_pnl": 0.0, "costs": 0.0, "fills": 0.0, "notional": 0.0})
        bucket["realized_pnl"] += realized
        bucket["costs"] += cost
        bucket["fills"] += 1
        bucket["notional"] += abs(quantity * price)

        self._applied.add(operation_id)
        self.state.applied_operations.append(operation_id)
        self.state.operation_fingerprints[operation_id] = fingerprint
        self.save()
        return {"symbol": symbol, "quantity": quantity, "price": price, "cost": cost,
                "realized_pnl": realized, "cash_after": self.state.cash,
                "operation_id": operation_id, "replayed": False}

    def mark_to_market(self, date: str, prices: dict[str, float]) -> dict[str, Any]:
        """Revalue every sleeve and record one point in the persistent NAV history."""
        self._assert_writable()
        self._validate_date(date)
        if any(type(value) not in (int, float) or not math.isfinite(value) or value <= 0
               for value in prices.values()):
            raise ValueError("marks require finite positive prices")
        if self.state.last_session_date and date < self.state.last_session_date:
            raise BackwardInTime(
                f"cannot mark {date}: the Book is already marked through "
                f"{self.state.last_session_date}")
        repeat = date == self.state.last_session_date

        for holdings in self.sleeves.values():
            for symbol, position in holdings.items():
                if symbol in prices:
                    position.last_price = prices[symbol]
        market_value = sum(position.market_value for position in self._positions())
        unrealized = sum(position.unrealized_pnl for position in self._positions())
        nav = self.state.cash + market_value
        gross = sum(abs(value) for value in self.symbol_exposures().values())
        net = sum(self.symbol_exposures().values())
        if self.state.inception_date is None:
            self.state.inception_date = date
        self.state.last_session_date = date
        point = {"date": date, "nav": nav, "cash": self.state.cash,
                 "market_value": market_value, "unrealized_pnl": unrealized,
                 "realized_pnl": self.state.realized_pnl, "fees_paid": self.state.fees_paid,
                 "gross_exposure": gross, "net_exposure": net,
                 "open_positions": len(self.aggregate_positions()),
                 "open_sleeves": len(self._open_sleeves())}
        if repeat:
            self.state.nav_history[-1] = point
        else:
            self.state.sessions += 1
            self.state.nav_history.append(point)
        self.state.peak_nav = max(
            [self.state.initial_capital]
            + [float(item["nav"]) for item in self.state.nav_history])
        self.save()
        return point

    @staticmethod
    def _validate_date(value: str) -> None:
        if not isinstance(value, str) or calendar_date.fromisoformat(value).isoformat() != value:
            raise ValueError("ledger date must be ISO YYYY-MM-DD")

    def _fill_fingerprint(self, symbol: str, quantity: float, price: float, cost: float,
                          date: str, strategy_id: str) -> str:
        def number(value):
            # Treat 1 and 1.0 (and signed zero) as the same amount without
            # rounding distinct large integer inputs through float conversion.
            return str(int(value)) if type(value) is int or value.is_integer() else value.hex()

        payload = {"schema": "book-fill-identity-v1", "ledger_id": self.state.ledger_id,
                   "authority": self.state.authority, "mode": self.state.mode,
                   "currency": self.state.currency, "symbol": symbol,
                   "strategy_id": strategy_id, "date": date,
                   "quantity": number(quantity), "price": number(price), "cost": number(cost)}
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        return hashlib.sha256(encoded.encode()).hexdigest()

    # --- views -------------------------------------------------------------
    def _positions(self) -> list[Position]:
        return [position for holdings in self.sleeves.values()
                for position in holdings.values()]

    def _open_sleeves(self) -> list[Position]:
        return [position for position in self._positions() if position.quantity]

    def sleeve_positions(self, strategy_id: str) -> list[dict[str, Any]]:
        return sorted((position.to_dict() | {"market_value": position.market_value,
                                             "unrealized_pnl": position.unrealized_pnl}
                       for position in self.sleeves.get(strategy_id, {}).values()
                       if position.quantity), key=lambda item: item["symbol"])

    def sleeve_exposures(self, strategy_id: str) -> dict[str, float]:
        return {symbol: position.market_value
                for symbol, position in self.sleeves.get(strategy_id, {}).items()
                if position.quantity}

    def sleeve_exposures_at(self, strategy_id: str,
                            prices: dict[str, float]) -> dict[str, float]:
        """Value one sleeve at supplied point-in-time prices without mutating the Book."""
        return {symbol: position.quantity * prices.get(symbol, position.last_price)
                for symbol, position in self.sleeves.get(strategy_id, {}).items()
                if position.quantity}

    def symbol_exposures(self) -> dict[str, float]:
        totals: dict[str, float] = {}
        for position in self._open_sleeves():
            totals[position.symbol] = totals.get(position.symbol, 0.0) + position.market_value
        return {symbol: value for symbol, value in totals.items() if abs(value) > 1e-9}

    def symbol_exposures_at(self, prices: dict[str, float]) -> dict[str, float]:
        """Aggregate portfolio exposure at supplied prices without changing persistent marks."""
        totals: dict[str, float] = {}
        for position in self._open_sleeves():
            value = position.quantity * prices.get(position.symbol, position.last_price)
            totals[position.symbol] = totals.get(position.symbol, 0.0) + value
        return {symbol: value for symbol, value in totals.items() if abs(value) > 1e-9}

    def nav_at(self, prices: dict[str, float]) -> float:
        """NAV at supplied prices, used for pre-fill risk after an overnight gap."""
        return self.state.cash + sum(self.symbol_exposures_at(prices).values())

    def aggregate_positions(self) -> list[dict[str, Any]]:
        rows: dict[str, dict[str, Any]] = {}
        for position in self._open_sleeves():
            row = rows.setdefault(position.symbol, {
                "symbol": position.symbol, "quantity": 0.0, "market_value": 0.0,
                "unrealized_pnl": 0.0, "last_price": position.last_price, "strategies": []})
            row["quantity"] += position.quantity
            row["market_value"] += position.market_value
            row["unrealized_pnl"] += position.unrealized_pnl
            row["last_price"] = position.last_price
            row["strategies"].append(position.strategy_id)
        for row in rows.values():
            row["strategies"] = sorted(set(row["strategies"]))
        return sorted(rows.values(), key=lambda item: item["symbol"])

    def open_positions(self) -> list[dict[str, Any]]:
        return self.aggregate_positions()

    @property
    def nav(self) -> float:
        return self.state.cash + sum(position.market_value for position in self._positions())

    @property
    def drawdown(self) -> float:
        peak = max(self.state.peak_nav, self.state.initial_capital)
        return self.nav / peak - 1.0 if peak else 0.0

    @property
    def total_return(self) -> float:
        return self.nav / self.state.initial_capital - 1.0 if self.state.initial_capital else 0.0

    def exposures(self) -> dict[str, float]:
        nav = self.nav or 1.0
        values = self.symbol_exposures()
        gross = sum(abs(value) for value in values.values())
        net = sum(values.values())
        return {"gross": gross, "net": net, "gross_ratio": gross / nav, "net_ratio": net / nav}

    def summary(self) -> dict[str, Any]:
        exposures = self.exposures()
        return {"ledger_id": self.state.ledger_id, "authority": self.state.authority,
                "mode": self.state.mode, "currency": self.state.currency,
                "initial_capital": self.state.initial_capital, "nav": self.nav,
                "cash": self.state.cash, "total_return": self.total_return,
                "realized_pnl": self.state.realized_pnl,
                "unrealized_pnl": sum(p.unrealized_pnl for p in self._positions()),
                "fees_paid": self.state.fees_paid, "drawdown": self.drawdown,
                "sessions": self.state.sessions, "fills": self.state.fills,
                "inception_date": self.state.inception_date,
                "last_session_date": self.state.last_session_date,
                "open_positions": len(self.aggregate_positions()),
                "open_sleeves": len(self._open_sleeves()),
                "strategies_with_exposure": sorted(
                    strategy for strategy, holdings in self.sleeves.items()
                    if any(position.quantity for position in holdings.values())),
                "operations_applied": len(self.state.applied_operations),
                "gross_exposure_ratio": exposures["gross_ratio"],
                "net_exposure_ratio": exposures["net_ratio"],
                "attribution": self.state.attribution}
