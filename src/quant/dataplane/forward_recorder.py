"""Passive forward market recorder.

Every historical result this system can produce is development evidence: the data
was already there when the hypothesis was written.  The only way to obtain
evidence that is out of sample *by construction* is to start recording market
state now and use it later, which is what this module does.

Three properties make the record worth something afterwards.

1. **Forward-only in wall clock.** An observation whose ``recorded_at`` precedes
   the latest one already stored is refused. Back-dating a record after the
   outcome is known is precisely the fabrication the store exists to prevent.
2. **Immutable.** A second observation for the same (symbol, session, field set)
   with different values does not overwrite: it is written as a conflict record,
   so a vendor restatement is visible instead of silently replacing history.
3. **Point-in-time readable.** :meth:`ForwardRecorder.as_of` returns only what
   had been recorded before a given instant, so research cannot see a value that
   arrived after the decision it claims to have made.

The recorder never invents data. It stores observations handed to it, each with a
source and a source fingerprint, and it reports ``COVERAGE_UNKNOWN`` unless an
independent expected-session calendar is supplied.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from ..state import append_jsonl, read_jsonl, utc_now


#: Coverage states. Absence of a claim is a state, not a gap to paper over.
COVERAGE_UNKNOWN = "COVERAGE_UNKNOWN"
COVERAGE_COMPLETE = "COVERAGE_COMPLETE_AGAINST_DECLARED_CALENDAR"
COVERAGE_INCOMPLETE = "COVERAGE_INCOMPLETE_AGAINST_DECLARED_CALENDAR"

RECORD_ACCEPTED = "ACCEPTED"
RECORD_DUPLICATE = "DUPLICATE_IGNORED"
RECORD_CONFLICT = "IMMUTABLE_OBSERVATION_REVISION_REFUSED"
RECORD_BACKDATED = "FORWARD_RECORDER_IS_APPEND_ONLY_IN_WALL_CLOCK"
RECORD_INVALID = "OBSERVATION_INVALID"


def _instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class ForwardObservation:
    """One recorded market observation with its provenance."""

    symbol: str
    session_date: str
    #: Field name -> value, e.g. {"open": 101.2, "close": 100.4, "volume": 1.2e6}.
    fields: Mapping[str, float]
    source: str
    #: Fingerprint of the exact payload the source returned.
    source_fingerprint: str
    recorded_at: str = field(default_factory=utc_now)
    #: Free-form note, e.g. the vendor request that produced it.
    note: str = ""

    def violations(self) -> list[str]:
        problems: list[str] = []
        if not self.symbol:
            problems.append("SYMBOL_MISSING")
        if not self.session_date:
            problems.append("SESSION_DATE_MISSING")
        if not self.fields:
            problems.append("NO_OBSERVED_FIELDS")
        if not self.source:
            problems.append("SOURCE_UNDECLARED")
        if not self.source_fingerprint:
            problems.append("SOURCE_FINGERPRINT_UNDECLARED")
        for name, value in self.fields.items():
            if not isinstance(value, (int, float)) or value != value:
                problems.append(f"FIELD_NOT_FINITE:{name}")
        try:
            _instant(self.recorded_at)
        except ValueError:
            problems.append("RECORDED_AT_NOT_ISO8601")
        return problems

    @property
    def key(self) -> str:
        return f"{self.symbol}|{self.session_date}|{','.join(sorted(self.fields))}"

    @property
    def content_address(self) -> str:
        payload = "|".join([self.symbol, self.session_date,
                            ";".join(f"{name}={self.fields[name]!r}"
                                     for name in sorted(self.fields)),
                            self.source, self.source_fingerprint])
        return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        document = asdict(self)
        document["fields"] = dict(sorted(self.fields.items()))
        document["content_address"] = self.content_address
        document["key"] = self.key
        return document


@dataclass(frozen=True)
class RecordOutcome:
    state: str
    observation: ForwardObservation
    detail: str = ""

    @property
    def accepted(self) -> bool:
        return self.state == RECORD_ACCEPTED

    def to_dict(self) -> dict[str, Any]:
        return {"state": self.state, "detail": self.detail,
                "content_address": self.observation.content_address,
                "key": self.observation.key}


class ForwardRecorder:
    """Append-only forward store of market observations."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._addresses: set[str] = set()
        #: key -> content address of the first accepted observation for that key.
        self._first: dict[str, str] = {}
        self._latest_recorded_at: str | None = None
        self._count = 0
        for record in read_jsonl(self.path):
            if record.get("state") != RECORD_ACCEPTED:
                continue
            address = str(record.get("content_address", ""))
            key = str(record.get("key", ""))
            self._addresses.add(address)
            self._first.setdefault(key, address)
            recorded_at = str(record.get("recorded_at", ""))
            if recorded_at and (self._latest_recorded_at is None
                                or recorded_at > self._latest_recorded_at):
                self._latest_recorded_at = recorded_at
            self._count += 1

    # -- writing --------------------------------------------------------------

    def record(self, observation: ForwardObservation) -> RecordOutcome:
        """Store one observation, or say precisely why it was not stored."""
        problems = observation.violations()
        if problems:
            return self._journal(RECORD_INVALID, observation, ";".join(problems))
        if observation.content_address in self._addresses:
            return self._journal(RECORD_DUPLICATE, observation,
                                 "identical observation already recorded")
        existing = self._first.get(observation.key)
        if existing is not None:
            return self._journal(RECORD_CONFLICT, observation,
                                 f"key already recorded as {existing}")
        if (self._latest_recorded_at is not None
                and _instant(observation.recorded_at) < _instant(self._latest_recorded_at)):
            return self._journal(RECORD_BACKDATED, observation,
                                 f"latest recorded_at is {self._latest_recorded_at}")
        outcome = self._journal(RECORD_ACCEPTED, observation, "")
        self._addresses.add(observation.content_address)
        self._first[observation.key] = observation.content_address
        self._latest_recorded_at = observation.recorded_at
        self._count += 1
        return outcome

    def record_many(self, observations: Iterable[ForwardObservation]) -> list[RecordOutcome]:
        return [self.record(observation) for observation in observations]

    def _journal(self, state: str, observation: ForwardObservation,
                 detail: str) -> RecordOutcome:
        document = observation.to_dict()
        document["state"] = state
        document["detail"] = detail
        document["journaled_at"] = utc_now()
        append_jsonl(self.path, document)
        return RecordOutcome(state, observation, detail)

    # -- reading --------------------------------------------------------------

    def accepted(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        seen: set[str] = set()
        for record in read_jsonl(self.path):
            if record.get("state") != RECORD_ACCEPTED:
                continue
            address = str(record.get("content_address", ""))
            if address in seen:
                continue
            seen.add(address)
            rows.append(record)
        return rows

    def conflicts(self) -> list[dict[str, Any]]:
        return [record for record in read_jsonl(self.path)
                if record.get("state") == RECORD_CONFLICT]

    def as_of(self, recorded_before: str, symbols: Sequence[str] | None = None
              ) -> list[dict[str, Any]]:
        """Point-in-time view: only what was recorded strictly before an instant.

        This is the accessor research is supposed to use. Reading the store
        without a cut-off is how a value that arrived after the decision ends up
        inside it.
        """
        cut = _instant(recorded_before)
        wanted = set(symbols) if symbols else None
        rows = []
        for record in self.accepted():
            if wanted is not None and record.get("symbol") not in wanted:
                continue
            recorded_at = str(record.get("recorded_at", ""))
            if not recorded_at:
                continue
            if _instant(recorded_at) < cut:
                rows.append(record)
        return sorted(rows, key=lambda row: (row.get("session_date", ""),
                                             row.get("symbol", "")))

    # -- state ----------------------------------------------------------------

    def symbols(self) -> list[str]:
        return sorted({str(record.get("symbol")) for record in self.accepted()})

    def sessions(self) -> list[str]:
        return sorted({str(record.get("session_date")) for record in self.accepted()})

    def session_seal(self, session_date: str) -> str | None:
        """Hash of every accepted observation for one session, in canonical order.

        Publishing this before an outcome window opens is how the record proves,
        later, that it existed beforehand.
        """
        addresses = sorted(str(record.get("content_address"))
                           for record in self.accepted()
                           if record.get("session_date") == session_date)
        if not addresses:
            return None
        payload = "|".join([session_date] + addresses)
        return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def coverage(self, expected_sessions: Sequence[str] | None = None,
                 expected_symbols: Sequence[str] | None = None) -> dict[str, Any]:
        """Report what is recorded, and refuse to claim completeness unasked."""
        recorded_sessions = self.sessions()
        recorded_symbols = self.symbols()
        document: dict[str, Any] = {
            "state": COVERAGE_UNKNOWN,
            "accepted_observations": len(self.accepted()),
            "conflicts": len(self.conflicts()),
            "symbols": recorded_symbols,
            "sessions_recorded": len(recorded_sessions),
            "first_session": recorded_sessions[0] if recorded_sessions else None,
            "last_session": recorded_sessions[-1] if recorded_sessions else None,
            "latest_recorded_at": self._latest_recorded_at,
        }
        if expected_sessions is None or expected_symbols is None:
            document["reason"] = ("no independent expected calendar/universe supplied; "
                                 "completeness cannot be asserted")
            return document
        missing: list[str] = []
        present = {(str(record.get("session_date")), str(record.get("symbol")))
                   for record in self.accepted()}
        for session in expected_sessions:
            for symbol in expected_symbols:
                if (session, symbol) not in present:
                    missing.append(f"{session}:{symbol}")
        document["missing"] = sorted(missing)[:50]
        document["missing_count"] = len(missing)
        document["state"] = COVERAGE_COMPLETE if not missing else COVERAGE_INCOMPLETE
        return document

    def __len__(self) -> int:
        return self._count
