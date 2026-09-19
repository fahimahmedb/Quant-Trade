"""Forward Coverage Ledger: what was expected, attempted, observed, valid, in
conflict, missing, or genuinely unknown -- and when each became knowable.

The mission is explicit that these are different things and must stay
different: *"UNKNOWN != MISSING. MISSING != ZERO."* A cell this ledger has
never even declared an expectation for is ``UNKNOWN``, not ``MISSING``: saying
``MISSING`` would assert an authoritative calendar/universe this module does
not have unless a caller declared one. A cell whose session has not even
closed yet is also ``UNKNOWN``, for the same reason -- it is not yet
meaningful to ask whether it was captured. Only a declared, closed,
repeatedly-attempted-and-failed cell earns ``MISSING``.

No trading calendar is invented here. ``ExpectedCalendar`` sessions and
universe are both explicit, durable, append-only declarations a caller makes;
:func:`seed_expected_sessions_from_dataset` bootstraps the session dimension
from an already-validated dataset's own aligned session list (the
``us_sector_etf_daily`` panel already went through `validation.validate_panel`),
which is evidence already in the repository, not a hand-authored holiday
calendar this Builder session would otherwise have to invent.

Universe declarations are versioned by ``effective_from`` so a later universe
change is never applied retroactively: a symbol added today does not turn
yesterday's silence about it into ``MISSING``, and a symbol dropped today does
not erase yesterday's genuine expectation of it. Session declarations are
simpler -- an idempotent, monotonically growing set -- because a calendar date
does not itself change meaning over time the way universe membership does.

Attempt attribution to a specific session is necessarily approximate for a
*failed* attempt: a failure reveals nothing about which sessions it would have
returned, so this ledger can only say a source-wide failure happened after a
given session's conservative close, not that it specifically targeted that
session. This is named here rather than hidden behind false per-cell
precision; see ``ForwardCoverageLedger.classify``'s docstring.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Sequence

from ..state import append_jsonl, read_jsonl, utc_now
from .forward_capture import ATTEMPT_SUCCEEDED, AttemptJournal
from .forward_recorder import ForwardRecorder
from .panel import PricePanel

# -- per-cell disposition (mission section 5) ----------------------------------

CELL_UNKNOWN = "UNKNOWN"
CELL_EXPECTED = "EXPECTED"
CELL_ATTEMPTED = "ATTEMPTED"
CELL_OBSERVED = "OBSERVED"
CELL_VALID = "VALID"
CELL_CONFLICT = "CONFLICT"
CELL_MISSING = "MISSING"

CELL_STATES = (CELL_UNKNOWN, CELL_EXPECTED, CELL_ATTEMPTED, CELL_OBSERVED,
              CELL_VALID, CELL_CONFLICT, CELL_MISSING)

#: How long after a session's conservative close a run of failed attempts (or
#: a success that did not contain the cell) must persist before the ledger
#: calls a cell MISSING rather than still-ATTEMPTED. This is an assumed
#: operational parameter, not a derived SLA -- named explicitly as such (the
#: same class of gap Wave 1's ECON-002 flagged for an unrelated timeout
#: default) so a future reviewer does not mistake it for calibrated fact.
DEFAULT_MISSING_GRACE_HOURS = 24.0


def _session_close_bound(session: str) -> datetime:
    """A conservative instant by which `session` is certainly closed.

    Exchange close is somewhere around 20:00-21:00 UTC on the session's own
    calendar date; using the *next* UTC midnight is deliberately later than
    that, so this never calls a session "closed" before it plausibly could be.
    """
    return datetime.fromisoformat(session).replace(tzinfo=timezone.utc) + timedelta(days=1)


@dataclass(frozen=True)
class UniverseDeclaration:
    symbols: tuple[str, ...]
    effective_from: str
    declared_at: str
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        document = asdict(self)
        document["symbols"] = list(self.symbols)
        return document


class ExpectedCalendar:
    """Append-only, point-in-time-correct declarations of what should exist.

    Never mutates a prior declaration. A universe or session-list change is a
    new, later-effective declaration layered on top of history, never an edit
    to it -- exactly the immutability discipline the recorder itself enforces
    for observations, applied here to the *expectations* the ledger judges
    observations against.
    """

    def __init__(self, sessions_path: Path, universe_path: Path) -> None:
        self.sessions_path = Path(sessions_path)
        self.universe_path = Path(universe_path)

    def declare_sessions(self, sessions: Sequence[str], note: str = "") -> int:
        """Add sessions to the expected set. Returns how many were new."""
        existing = self.expected_sessions()
        new = sorted(set(sessions) - existing)
        if not new:
            return 0
        append_jsonl(self.sessions_path,
                    {"sessions": new, "declared_at": utc_now(), "note": note})
        return len(new)

    def expected_sessions(self) -> set[str]:
        sessions: set[str] = set()
        for row in read_jsonl(self.sessions_path):
            sessions.update(row.get("sessions", []))
        return sessions

    def declare_universe(self, symbols: Sequence[str], effective_from: str,
                         note: str = "") -> UniverseDeclaration:
        declaration = UniverseDeclaration(symbols=tuple(sorted(set(symbols))),
                                          effective_from=effective_from,
                                          declared_at=utc_now(), note=note)
        append_jsonl(self.universe_path, declaration.to_dict())
        return declaration

    def universe_declarations(self) -> list[dict[str, Any]]:
        return sorted(read_jsonl(self.universe_path), key=lambda row: row["effective_from"])

    def expected_symbols_for(self, session: str) -> set[str] | None:
        """The universe in effect for `session`, or None if none existed yet.

        None is returned rather than an empty set so a caller can distinguish
        "declared empty" from "no declaration reaches this far back" -- the
        latter is what keeps a symbol universe change from being asserted
        retroactively.
        """
        applicable = [row for row in self.universe_declarations()
                     if row["effective_from"] <= session]
        if not applicable:
            return None
        return set(applicable[-1]["symbols"])


def seed_expected_sessions_from_dataset(calendar: ExpectedCalendar, dataset_path: Path,
                                        symbols: Sequence[str] | None = None) -> int:
    """Bootstrap expected sessions from an already-validated dataset.

    Not an invented trading calendar: `dataset_path` is expected to be a panel
    that already passed `validation.validate_panel` (e.g. the committed
    `us_sector_etf_daily` snapshot), so every date in it is a session that
    genuinely existed and was already checked for internal consistency. This
    is a starting point, not a claim of completeness going forward -- new
    sessions still need `declare_sessions` as they close.
    """
    panel = PricePanel.load(dataset_path)
    sessions = panel.aligned_dates(symbols) if symbols else panel.dates
    return calendar.declare_sessions(
        sessions, note=f"seeded from validated dataset snapshot {dataset_path.name}")


@dataclass(frozen=True)
class CoverageCell:
    session: str
    symbol: str
    state: str
    known_since: str | None
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ForwardCoverageLedger:
    """Answers, for one (session, symbol) cell: what do we actually know?

    Precedence, most to least authoritative:

    1. Not declared expected (no calendar/universe authority reaches this
       cell) -> ``UNKNOWN``. Completeness is never asserted without an
       authoritative declaration, per the recorder's own founding rule.
    2. A conflicting observation was refused -> ``CONFLICT``, checked *before*
       ``VALID`` even though a conflict can only exist for a key that already
       has an accepted value (the recorder only refuses a second, differing
       write for an already-claimed key) -- surfacing the dispute takes
       priority over quietly reporting the first-accepted value as if nothing
       had ever disagreed with it.
    3. An accepted observation is on file, no conflict against it -> ``VALID``.
    4. A successful attempt's payload covered this exact (session, symbol) but
       no recorder entry exists for it -> ``OBSERVED``. This names the crash
       window between a validated fetch and its durable commit; with
       `execute_forward_capture`'s actual write order (record, then journal)
       this specific window is not reachable through that function today, but
       the disposition is kept and tested because it is a real, nameable state
       for any adapter that might not preserve that ordering.
    5. The session has not closed yet (see `_session_close_bound`) ->
       ``UNKNOWN``: too early to say anything.
    6. No attempt exists after the session closed -> ``EXPECTED``: declared,
       due, never yet tried.
    7. At least one attempt after close exists, all either failed or (on
       success) did not contain this cell: ``MISSING`` once
       `missing_grace_hours` has elapsed since the most recent such attempt,
       otherwise still ``ATTEMPTED``.

    Attempt attribution is source-wide, not symbol-specific, because the only
    adapter this mission wires up (`forward_capture.yahoo_forward_adapter`)
    fetches all requested symbols in one call and fails the whole attempt
    together; see the module docstring.
    """

    def __init__(self, calendar: ExpectedCalendar, recorder: ForwardRecorder,
                journal: AttemptJournal, source_id: str,
                missing_grace_hours: float = DEFAULT_MISSING_GRACE_HOURS) -> None:
        self.calendar = calendar
        self.recorder = recorder
        self.journal = journal
        self.source_id = source_id
        self.missing_grace_hours = missing_grace_hours

    def classify(self, session: str, symbol: str, now: datetime) -> CoverageCell:
        expected_symbols = self.calendar.expected_symbols_for(session)
        if (expected_symbols is None or symbol not in expected_symbols
                or session not in self.calendar.expected_sessions()):
            return CoverageCell(session, symbol, CELL_UNKNOWN, None,
                                "no authoritative expected-calendar/universe "
                                "declaration covers this cell")

        # Checked before VALID, deliberately: a CONFLICT record can only ever
        # exist for a key that already has an accepted observation (the
        # recorder only refuses a *second*, differing write for an
        # already-claimed key), so if precedence checked VALID first, CONFLICT
        # would be structurally unreachable. Surfacing the dispute takes
        # priority over quietly reporting the first-accepted value as if
        # nothing had ever disagreed with it.
        for record in self.recorder.conflicts():
            if record.get("symbol") == symbol and record.get("session_date") == session:
                return CoverageCell(session, symbol, CELL_CONFLICT,
                                    record.get("journaled_at"),
                                    "a later differing observation was refused, "
                                    "not silently applied; the first-accepted "
                                    "value is still on file and unchanged")
        for record in self.recorder.accepted():
            if record.get("symbol") == symbol and record.get("session_date") == session:
                return CoverageCell(session, symbol, CELL_VALID,
                                    record.get("journaled_at"),
                                    "accepted observation on file")

        attempts = self.journal.for_source(self.source_id)
        succeeded_covering = [
            row for row in attempts
            if row.get("outcome") == ATTEMPT_SUCCEEDED
            and session in row.get("sessions_observed", [])
            and symbol in row.get("symbols_observed", [])]
        if succeeded_covering:
            latest = max(succeeded_covering, key=lambda row: row.get("journaled_at", ""))
            return CoverageCell(session, symbol, CELL_OBSERVED, latest.get("journaled_at"),
                                "a validated attempt's payload covered this cell but "
                                "no durable observation is on file yet")

        close_bound = _session_close_bound(session)
        if now < close_bound:
            return CoverageCell(session, symbol, CELL_UNKNOWN, None,
                                "session has not yet closed; not yet meaningful "
                                "to call this missing")

        close_bound_text = close_bound.isoformat()
        after_close = [row for row in attempts
                      if row.get("journaled_at", "") >= close_bound_text]
        if not after_close:
            return CoverageCell(session, symbol, CELL_EXPECTED, None,
                                "declared expected and closed; no attempt on "
                                "file since close")

        latest = max(after_close, key=lambda row: row.get("journaled_at", ""))
        grace_bound = close_bound + timedelta(hours=self.missing_grace_hours)
        if now >= grace_bound:
            return CoverageCell(session, symbol, CELL_MISSING, latest.get("journaled_at"),
                                f"{len(after_close)} post-close attempt(s) on this "
                                "source, none produced this cell, grace period elapsed")
        return CoverageCell(session, symbol, CELL_ATTEMPTED, latest.get("journaled_at"),
                            f"{len(after_close)} post-close attempt(s) so far, none "
                            "produced this cell yet; still within grace period")

    def summary(self, now: datetime) -> dict[str, Any]:
        """Full funnel across every declared (session, symbol) cell.

        This is the answer to the mission's six questions: what was expected
        (the declared universe), attempted/observed/valid/conflicting/missing
        (the per-cell disposition), and when each became knowable
        (`known_since`, taken from the record that actually determined it --
        never the summary's own generation time).
        """
        counts = {state: 0 for state in CELL_STATES}
        cells: list[dict[str, Any]] = []
        for session in sorted(self.calendar.expected_sessions()):
            for symbol in sorted(self.calendar.expected_symbols_for(session) or ()):
                cell = self.classify(session, symbol, now)
                counts[cell.state] += 1
                cells.append(cell.to_dict())
        return {"generated_at": utc_now(), "source_id": self.source_id,
               "missing_grace_hours": self.missing_grace_hours,
               "counts": counts, "cells": cells}
