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

from ..state import read_json, write_json


EMPTY_STATS = {"sessions": 0, "tickets": 0, "booked": 0, "no_trade": 0,
               "vetoed": 0, "blocked": 0, "last_rebalance_date": None}


class DeskJournal:
    def __init__(self, path: Path):
        self.path = path
        payload = read_json(path, {}) or {}
        self.processed: set[str] = set(payload.get("processed", []))
        self.pending: dict[str, dict[str, Any]] = payload.get("pending", {})
        self.stats: dict[str, dict[str, Any]] = payload.get("stats", {})
        self.last_session_date: str | None = payload.get("last_session_date")

    def save(self) -> None:
        write_json(self.path, {"version": 1, "processed": sorted(self.processed),
                               "pending": self.pending, "stats": self.stats,
                               "last_session_date": self.last_session_date})

    # --- queries -----------------------------------------------------------
    def is_processed(self, opportunity_id: str) -> bool:
        return opportunity_id in self.processed

    def pending_plan(self, opportunity_id: str) -> dict[str, Any] | None:
        return self.pending.get(opportunity_id)

    def stats_for(self, strategy_id: str) -> dict[str, Any]:
        return self.stats.get(strategy_id, dict(EMPTY_STATS))

    # --- transaction -------------------------------------------------------
    def begin(self, opportunity_id: str, strategy_id: str, session_date: str,
              ticket: dict[str, Any], fills: list[dict[str, Any]]) -> None:
        """Durably record what this session is about to do, before it does it."""
        self.pending[opportunity_id] = {"strategy_id": strategy_id,
                                        "session_date": session_date,
                                        "ticket": ticket, "fills": fills}
        self.save()

    def commit(self, opportunity_id: str, strategy_id: str, status: str,
               session_date: str, rebalanced: bool) -> None:
        """Finish the opportunity: clear any intent and update the counters, atomically."""
        self.pending.pop(opportunity_id, None)
        stats = self.stats.setdefault(strategy_id, dict(EMPTY_STATS))
        stats["sessions"] += 1
        stats["tickets"] += 1
        key = {"BOOKED": "booked", "NO_TRADE": "no_trade",
               "VETOED": "vetoed", "BLOCKED": "blocked"}.get(status)
        if key:
            stats[key] += 1
        if rebalanced:
            stats["last_rebalance_date"] = session_date
        self.processed.add(opportunity_id)
        if self.last_session_date is None or session_date > self.last_session_date:
            self.last_session_date = session_date
        self.save()

    #: An outcome that moves no money commits directly.
    record = commit
