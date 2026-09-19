"""Operational failure modes, modelled rather than hoped away.

A paper system that assumes clean data and cooperative brokers is measuring a
market that does not exist.  The failures here are the ones that silently corrupt
economic state rather than crash loudly:

* a **stale quote** used to mark or to size, which values a position at a price
  nobody could trade;
* a **missing bar** forward-filled into a decision, which invents an observation;
* a **duplicate order** after a restart, which doubles an exposure and its cost;
* an **overfill** accumulated past the intended quantity;
* a **broker outage** resolved by assuming the order did, or did not, fill.

Every one of these is refused with a named state. The last is the important one:
after an outage the honest answer is ``RECONCILIATION_UNKNOWN``, and a system that
guesses will book a position it does not have or miss one it does.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from ..state import append_jsonl, read_jsonl, utc_now


FAILURE_MODES = ("STALE_QUOTE", "MISSING_BAR", "TRADING_HALT", "PARTIAL_FILL",
                 "DUPLICATE_ORDER", "BROKER_OUTAGE", "LATE_FILL", "CANCEL_REJECT")

QUOTE_FRESH = "QUOTE_FRESH"
QUOTE_STALE = "STALE_QUOTE"
QUOTE_TIMESTAMP_MISSING = "QUOTE_TIMESTAMP_MISSING"

BAR_PRESENT = "BAR_PRESENT"
BAR_MISSING = "MISSING_BAR_BLOCKS_DECISION"
BAR_HALTED = "TRADING_HALT_BLOCKS_DECISION"

ORDER_RESERVED = "ORDER_RESERVED"
ORDER_SENT = "ORDER_SENT"
ORDER_DUPLICATE_SUPPRESSED = "DUPLICATE_ORDER_SUPPRESSED"
ORDER_UNKNOWN_AFTER_OUTAGE = "RECONCILIATION_UNKNOWN"

FILL_ACCEPTED = "FILL_ACCEPTED"
FILL_DUPLICATE_IGNORED = "FILL_DUPLICATE_IGNORED"
FILL_OVERFILL_REFUSED = "OVERFILL_REFUSED"
FILL_UNKNOWN_ORDER = "FILL_FOR_UNKNOWN_ORDER"


def _instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class QuoteCheck:
    state: str
    age_seconds: float | None
    limit_seconds: float
    detail: str = ""

    @property
    def usable(self) -> bool:
        return self.state == QUOTE_FRESH

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def check_quote(quoted_at: str | None, as_of: str, limit_seconds: float = 300.0) -> QuoteCheck:
    """Is this quote fresh enough to mark or size against ``as_of``?

    A quote from the future is stale too: a timestamp ahead of the valuation
    instant means the clocks disagree, and trusting it would value a position on
    information the decision could not have had.
    """
    if not quoted_at:
        return QuoteCheck(QUOTE_TIMESTAMP_MISSING, None, limit_seconds,
                          "a quote with no timestamp cannot be shown to be fresh")
    try:
        age = (_instant(as_of) - _instant(quoted_at)).total_seconds()
    except ValueError as error:
        return QuoteCheck(QUOTE_TIMESTAMP_MISSING, None, limit_seconds, str(error))
    if age < 0:
        return QuoteCheck(QUOTE_STALE, age, limit_seconds,
                          "quote timestamp is ahead of the valuation instant")
    if age > limit_seconds:
        return QuoteCheck(QUOTE_STALE, age, limit_seconds, "quote older than the limit")
    return QuoteCheck(QUOTE_FRESH, age, limit_seconds)


def check_bar(bar: Mapping[str, Any] | None, halted: bool = False) -> str:
    """A missing bar blocks the decision; it is never forward-filled into one."""
    if halted:
        return BAR_HALTED
    if not bar:
        return BAR_MISSING
    for field_name in ("open", "close", "volume"):
        value = bar.get(field_name)
        if value is None or not isinstance(value, (int, float)) or value != value:
            return BAR_MISSING
    return BAR_PRESENT


@dataclass(frozen=True)
class OrderIntent:
    """One intended order, identified before anything is sent."""

    client_order_id: str
    symbol: str
    quantity: float
    strategy_id: str
    session_date: str
    created_at: str = field(default_factory=utc_now)

    def violations(self) -> list[str]:
        problems: list[str] = []
        if not self.client_order_id:
            problems.append("CLIENT_ORDER_ID_MISSING")
        if self.quantity == 0:
            problems.append("ZERO_QUANTITY_ORDER")
        if not self.symbol:
            problems.append("SYMBOL_MISSING")
        return problems

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SubmissionOutcome:
    state: str
    intent: OrderIntent
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"state": self.state, "detail": self.detail, **self.intent.to_dict()}


class OrderSubmissionLedger:
    """Write-ahead, idempotent record of order intents and their fills.

    The reservation is written *before* the order is sent, so a crash in between
    leaves evidence that the order may exist. On restart the id is already
    reserved and a second submission is suppressed: an exposure doubled by a
    restart costs twice the frictions and breaks the sleeve accounting.
    """

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._reserved: dict[str, dict[str, Any]] = {}
        self._sent: set[str] = set()
        self._fills: dict[str, dict[str, float]] = {}
        for record in read_jsonl(self.path):
            state = record.get("state")
            order_id = str(record.get("client_order_id", ""))
            if state == ORDER_RESERVED and order_id:
                self._reserved[order_id] = dict(record)
            elif state == ORDER_SENT and order_id:
                self._sent.add(order_id)
            elif state == FILL_ACCEPTED and order_id:
                fill_id = str(record.get("fill_id", ""))
                self._fills.setdefault(order_id, {})[fill_id] = float(
                    record.get("quantity", 0.0))

    # -- submission -----------------------------------------------------------

    def reserve(self, intent: OrderIntent) -> SubmissionOutcome:
        problems = intent.violations()
        if problems:
            return SubmissionOutcome("ORDER_INTENT_INVALID", intent, ";".join(problems))
        if intent.client_order_id in self._reserved:
            return SubmissionOutcome(ORDER_DUPLICATE_SUPPRESSED, intent,
                                     "client order id already reserved")
        append_jsonl(self.path, {**intent.to_dict(), "state": ORDER_RESERVED,
                                 "journaled_at": utc_now()})
        self._reserved[intent.client_order_id] = intent.to_dict()
        return SubmissionOutcome(ORDER_RESERVED, intent)

    def mark_sent(self, client_order_id: str) -> str:
        if client_order_id not in self._reserved:
            return "ORDER_NOT_RESERVED"
        if client_order_id in self._sent:
            return ORDER_DUPLICATE_SUPPRESSED
        append_jsonl(self.path, {"client_order_id": client_order_id, "state": ORDER_SENT,
                                 "journaled_at": utc_now()})
        self._sent.add(client_order_id)
        return ORDER_SENT

    # -- fills ----------------------------------------------------------------

    def record_fill(self, client_order_id: str, fill_id: str, quantity: float) -> str:
        """Accumulate a partial fill, refusing duplicates and overfills."""
        intent = self._reserved.get(client_order_id)
        if intent is None:
            return FILL_UNKNOWN_ORDER
        existing = self._fills.setdefault(client_order_id, {})
        if fill_id in existing:
            return FILL_DUPLICATE_IGNORED
        intended = abs(float(intent.get("quantity", 0.0)))
        filled = sum(abs(value) for value in existing.values())
        if filled + abs(quantity) > intended + 1e-9:
            return FILL_OVERFILL_REFUSED
        append_jsonl(self.path, {"client_order_id": client_order_id, "fill_id": fill_id,
                                 "quantity": quantity, "state": FILL_ACCEPTED,
                                 "journaled_at": utc_now()})
        existing[fill_id] = quantity
        return FILL_ACCEPTED

    def filled_quantity(self, client_order_id: str) -> float:
        return sum(self._fills.get(client_order_id, {}).values())

    def outstanding(self, client_order_id: str) -> float | None:
        intent = self._reserved.get(client_order_id)
        if intent is None:
            return None
        return float(intent.get("quantity", 0.0)) - self.filled_quantity(client_order_id)

    # -- reconciliation -------------------------------------------------------

    def reconcile(self, broker_orders: Mapping[str, Mapping[str, Any]] | None
                  ) -> dict[str, Any]:
        """Compare local intents with the broker's view after an outage.

        ``broker_orders`` of ``None`` means the broker could not be reached. Every
        reserved-but-unconfirmed order is then ``RECONCILIATION_UNKNOWN``; the
        ledger does not decide that an unreachable order filled, or that it did
        not.
        """
        rows: list[dict[str, Any]] = []
        unknown = 0
        for order_id, intent in sorted(self._reserved.items()):
            local_filled = self.filled_quantity(order_id)
            if broker_orders is None:
                rows.append({"client_order_id": order_id, "state": ORDER_UNKNOWN_AFTER_OUTAGE,
                             "local_filled": local_filled, "broker_filled": None})
                unknown += 1
                continue
            broker = broker_orders.get(order_id)
            if broker is None:
                state = ("ORDER_UNKNOWN_TO_BROKER" if order_id in self._sent
                         else "ORDER_NEVER_SENT")
                if order_id in self._sent:
                    unknown += 1
                rows.append({"client_order_id": order_id, "state": state,
                             "local_filled": local_filled, "broker_filled": None})
                continue
            broker_filled = float(broker.get("filled_quantity", 0.0))
            state = ("RECONCILED" if abs(broker_filled - local_filled) <= 1e-9
                     else "FILL_QUANTITY_MISMATCH")
            rows.append({"client_order_id": order_id, "state": state,
                         "local_filled": local_filled, "broker_filled": broker_filled,
                         "intended": float(intent.get("quantity", 0.0))})
        return {"orders": rows, "unknown": unknown,
                "broker_reachable": broker_orders is not None,
                "mismatches": sum(1 for row in rows
                                  if row["state"] == "FILL_QUANTITY_MISMATCH")}

    def __len__(self) -> int:
        return len(self._reserved)


@dataclass(frozen=True)
class FailureInjection:
    """A declared operational scenario, so handling can be tested not assumed."""

    mode: str
    description: str
    expected_state: str

    def violations(self) -> list[str]:
        problems: list[str] = []
        if self.mode not in FAILURE_MODES:
            problems.append(f"{self.mode}: FAILURE_MODE_NOT_DECLARED")
        if not self.expected_state:
            problems.append(f"{self.mode}: EXPECTED_STATE_UNDECLARED")
        return problems

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def coverage_report(scenarios: Iterable[FailureInjection]) -> dict[str, Any]:
    """Which declared failure modes have a scenario, and which do not."""
    declared = [scenario for scenario in scenarios]
    covered = {scenario.mode for scenario in declared}
    missing = [mode for mode in FAILURE_MODES if mode not in covered]
    problems: list[str] = []
    for scenario in declared:
        problems.extend(scenario.violations())
    return {"covered": sorted(covered), "missing": missing,
            "complete": not missing and not problems,
            "violations": sorted(set(problems))}
