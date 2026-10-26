"""The desk journal: a write-ahead transaction log for desk sessions.

Deterministic operation ids stop a fill being applied twice, but they are not
sufficient on their own. If a crash lands between applying fills and finishing
the session, a naive replay re-runs the decision against a Book that already
contains those fills, sees no drift, and concludes NO_TRADE. The money would be
right and the history would be wrong.

So a session that is about to move money records its *intent* first:

``begin(plan) -> apply fills (idempotent by operation id) -> commit(outcome)``

On restart, an opportunity with a pending plan is not re-decided. Its recorded
fills are re-applied, which the ledger recognises as already applied, and the
outcome is committed exactly as originally decided.

Outcomes that move no money need no write-ahead record and commit in one write.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from copy import deepcopy
from functools import wraps
import fcntl
import os
import threading

from ..state import read_json, write_json
from .opportunity import TERMINAL


EMPTY_STATS = {"sessions": 0, "tickets": 0, "booked": 0, "no_trade": 0,
               "vetoed": 0, "blocked": 0, "last_rebalance_date": None}


class JournalConflict(RuntimeError):
    """Journal state or frozen intent differs; caller must reconsider/recover."""


def _serialized_access(method):
    @wraps(method)
    def serialized(self, *args, **kwargs):
        with self._mutation_lock:
            return method(self, *args, **kwargs)
    return serialized


class DeskJournal:
    def __init__(self, path: Path):
        if not hasattr(self, "_mutation_lock"):
            self._mutation_lock = threading.RLock()
        self.path = path
        observed = read_json(path)
        self._persisted = deepcopy(observed)
        payload = observed or {}
        self.processed: set[str] = set(payload.get("processed", []))
        self.pending: dict[str, dict[str, Any]] = payload.get("pending", {})
        self.stats: dict[str, dict[str, Any]] = payload.get("stats", {})
        self.last_session_date: str | None = payload.get("last_session_date")
        self.outcomes: dict[str, dict[str, Any]] = payload.get("outcomes", {})
        self.decision_snapshots: dict[str, dict[str, Any]] = payload.get(
            "decision_snapshots", {})

    @_serialized_access
    def save(self) -> None:
        fd = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(self.path.with_name(self.path.name + ".lock"), os.O_CREAT | os.O_RDWR, 0o600)
            fcntl.flock(fd, fcntl.LOCK_EX)
            if read_json(self.path) != self._persisted:
                raise JournalConflict("DESK_JOURNAL_CHANGED_SINCE_READ")
            document = {"version": 2, "processed": sorted(self.processed),
                        "pending": self.pending, "stats": self.stats,
                        "outcomes": self.outcomes,
                        "decision_snapshots": self.decision_snapshots,
                        "last_session_date": self.last_session_date}
            write_json(self.path, document)
            self._persisted = deepcopy(document)
        except BaseException:
            # Includes lock setup and publication success followed by ACK loss.
            self.__init__(self.path)
            raise
        finally:
            if fd is not None:
                os.close(fd)

    # --- queries -----------------------------------------------------------
    @_serialized_access
    def is_processed(self, opportunity_id: str) -> bool:
        return opportunity_id in self.processed

    @_serialized_access
    def pending_plan(self, opportunity_id: str) -> dict[str, Any] | None:
        return deepcopy(self.pending.get(opportunity_id))

    @_serialized_access
    def stats_for(self, strategy_id: str) -> dict[str, Any]:
        return deepcopy(self.stats.get(strategy_id, EMPTY_STATS))

    @_serialized_access
    def decision_snapshot(self, session_date: str) -> dict[str, Any] | None:
        return deepcopy(self.decision_snapshots.get(session_date))

    @_serialized_access
    def begin_session(self, session_date: str, capital: dict[str, Any],
                      evaluation: dict[str, Any]) -> dict[str, Any]:
        """Freeze the close-time Book before any open(t+1) fill is modelled."""
        existing = self.decision_snapshots.get(session_date)
        if existing is not None:
            return deepcopy(existing)
        snapshot = deepcopy({"CAPITAL": capital, "EVALUATION": evaluation})
        self.decision_snapshots[session_date] = snapshot
        self.save()
        return deepcopy(snapshot)

    @_serialized_access
    def close_session(self, session_date: str) -> None:
        if self.decision_snapshots.pop(session_date, None) is not None:
            self.save()

    # --- transaction -------------------------------------------------------
    @_serialized_access
    def begin(self, opportunity_id: str, strategy_id: str, session_date: str,
              ticket: dict[str, Any], fills: list[dict[str, Any]]) -> None:
        """Durably record what this session is about to do, before it does it."""
        if opportunity_id in self.processed:
            raise JournalConflict("COMPLETED_OPPORTUNITY_CANNOT_REOPEN")
        self._bind_ticket(ticket, opportunity_id, strategy_id, session_date)
        plan = deepcopy({"strategy_id": strategy_id, "session_date": session_date,
                         "ticket": ticket, "fills": fills})
        if opportunity_id in self.pending:
            if self.pending[opportunity_id] != plan:
                raise JournalConflict("FROZEN_DESK_INTENT_CHANGED")
            return
        self.pending[opportunity_id] = plan
        self.save()

    @_serialized_access
    def commit(self, opportunity_id: str, strategy_id: str, status: str,
               session_date: str, rebalanced: bool,
               ticket: dict[str, Any] | None = None) -> None:
        """Finish the opportunity: clear any intent and update the counters, atomically."""
        if status not in TERMINAL:
            raise ValueError("unknown terminal desk status")
        if ticket is not None:
            self._bind_ticket(ticket, opportunity_id, strategy_id, session_date)
            if "status" in ticket and ticket["status"] != status:
                raise JournalConflict("DESK_OUTCOME_STATUS_MISMATCH")
        if opportunity_id in self.processed:
            return
        pending = self.pending.get(opportunity_id)
        if pending is not None:
            if (pending["strategy_id"] != strategy_id or pending["session_date"] != session_date
                    or status != "BOOKED" or rebalanced is not True
                    or (ticket is not None and "fills" in ticket and ticket["fills"] != pending["fills"])):
                raise JournalConflict("DESK_COMPLETION_INTENT_MISMATCH")
        self.pending.pop(opportunity_id, None)
        if ticket is not None:
            self.outcomes[opportunity_id] = deepcopy(ticket)
        stats = self.stats.setdefault(strategy_id, dict(EMPTY_STATS))
        stats["sessions"] += 1
        stats["tickets"] += 1
        key = {"BOOKED": "booked", "NO_TRADE": "no_trade",
               "VETOED": "vetoed", "BLOCKED": "blocked"}.get(status)
        if key:
            stats[key] += 1
        if rebalanced:
            previous = stats["last_rebalance_date"]
            stats["last_rebalance_date"] = max(previous, session_date) if previous else session_date
        self.processed.add(opportunity_id)
        if self.last_session_date is None or session_date > self.last_session_date:
            self.last_session_date = session_date
        self.save()

    @staticmethod
    def _bind_ticket(ticket: dict[str, Any], opportunity_id: str,
                     strategy_id: str, session_date: str) -> None:
        if not isinstance(ticket, dict):
            raise ValueError("desk ticket must be an object")
        for key, expected in (("opportunity_id", opportunity_id), ("strategy_id", strategy_id),
                              ("session_date", session_date)):
            if key in ticket and ticket[key] != expected:
                raise JournalConflict("DESK_TICKET_IDENTITY_MISMATCH:" + key)

    #: An outcome that moves no money commits directly.
    record = commit
