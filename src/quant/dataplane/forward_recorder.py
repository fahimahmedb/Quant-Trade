"""Passive forward market recorder.

Every historical result this system can produce is development evidence: the data
was already there when the hypothesis was written.  The only way to obtain
evidence that is out of sample *by construction* is to start recording market
state now and use it later, which is what this module does.

Four properties make the record worth something afterwards.

1. **Forward-only in wall clock.** An observation whose ``recorded_at`` precedes
   the latest one already stored is refused. Back-dating a record after the
   outcome is known is precisely the fabrication the store exists to prevent.
2. **Immutable.** A second observation for the same (symbol, session, field set)
   with different values does not overwrite: it is written as a conflict record,
   so a vendor restatement is visible instead of silently replacing history. This
   promise is a per-*key* promise, so it must hold even when two independent
   recorder processes race on the same file — see ``race_conflicts`` below.
3. **Point-in-time readable.** :meth:`ForwardRecorder.as_of` returns only what
   had been recorded before a given instant, so research cannot see a value that
   arrived after the decision it claims to have made.
4. **Honest about time.** ``recorded_at`` is this process's own clock at the
   instant the ledger accepted the write. It is not, and must never be presented
   as, an externally attested timestamp: a caller with a wrong system clock still
   produces a write that succeeds. Forward-only monotonicity is what makes
   back-dated fabrication structurally hard; it is not proof that any individual
   ``recorded_at`` is truthful. See :meth:`ForwardObservation.time_provenance` for
   every time concept this module can and cannot vouch for.

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
#: A second writer's ACCEPTED row for a key another writer already claimed,
#: detected on replay. Never written as a record's own ``state`` -- each writer
#: honestly journaled ACCEPTED at the time it wrote -- this is a read-time
#: reclassification. See ``ForwardRecorder.race_conflicts``.
RECORD_RACE = "TWO_WRITER_RACE_DETECTED_AT_READ_TIME"

#: Whether a source-declared instant for this datum was supplied. Absence is a
#: state, never an invitation to substitute ``recorded_at`` or invent one.
SOURCE_TIMESTAMP_PRESENT = "SOURCE_TIMESTAMP_PRESENT"
SOURCE_TIMESTAMP_ABSENT = "SOURCE_TIMESTAMP_ABSENT"
SOURCE_TIMESTAMP_STATES = (SOURCE_TIMESTAMP_PRESENT, SOURCE_TIMESTAMP_ABSENT)

#: The only time-authority this module can honestly claim for ``recorded_at``:
#: this process's own clock, unattested by anything external. Naming it is what
#: stops a reader from mistaking forward-only monotonicity for a truthfulness
#: guarantee it does not provide.
TIME_AUTHORITY_UNATTESTED_LOCAL_CLOCK = "UNATTESTED_LOCAL_PROCESS_CLOCK"


def _instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class ForwardObservation:
    """One recorded market observation with its provenance.

    Time provenance is deliberately several fields, not one timestamp, because
    the mission's own red team found that a single caller-supplied
    ``recorded_at`` is not proof of time. Six distinct time concepts exist and
    are kept distinct rather than collapsed:

    * **source event time** -- ``session_date`` (the calendar identity of what
      was observed) and ``source_timestamp`` when the source actually publishes
      one for this datum;
    * **market session** -- ``market_session`` (e.g. regular trading session);
    * **fetch start / fetch end** -- ``fetch_started_at`` / ``fetch_completed_at``,
      this process's own clock around the network attempt;
    * **system-recorded receipt time** -- ``recorded_at``, this process's own
      clock at ledger-append time. Unattested; see module docstring point 4;
    * **vendor publication/update time** -- carried in ``source_timestamp`` only
      when ``source_timestamp_state`` is ``SOURCE_TIMESTAMP_PRESENT`` and the
      adapter documents that is what the field means for that source. Most
      sources this project can reach do not publish one, and absence is
      reported as a state (``SOURCE_TIMESTAMP_ABSENT``), never silently filled
      from another field.
    """

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
    #: Which exchange session this datum belongs to. Daily regular-session bars
    #: are the only kind this project captures today; the field exists so an
    #: extended-hours or multi-session source cannot be silently folded into a
    #: regular-session record later.
    market_session: str = "REGULAR"
    #: This process's own clock immediately before the fetch attempt began.
    fetch_started_at: str | None = None
    #: This process's own clock immediately after the response was fully
    #: received. ``None`` only when the fetch never completed, which an accepted
    #: observation cannot have -- see ``violations``.
    fetch_completed_at: str | None = None
    #: A source-declared instant for this specific datum, when one exists.
    source_timestamp: str | None = None
    source_timestamp_state: str = SOURCE_TIMESTAMP_ABSENT

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
        if not self.market_session:
            problems.append("MARKET_SESSION_UNDECLARED")
        for name, value in self.fields.items():
            if not isinstance(value, (int, float)) or value != value:
                problems.append(f"FIELD_NOT_FINITE:{name}")
        try:
            _instant(self.recorded_at)
        except ValueError:
            problems.append("RECORDED_AT_NOT_ISO8601")
        parsed: dict[str, datetime] = {}
        for field_name, value in (("fetch_started_at", self.fetch_started_at),
                                  ("fetch_completed_at", self.fetch_completed_at),
                                  ("source_timestamp", self.source_timestamp)):
            if value is None:
                continue
            try:
                parsed[field_name] = _instant(value)
            except ValueError:
                problems.append(f"{field_name.upper()}_NOT_ISO8601")
        if self.fetch_completed_at is not None and self.fetch_started_at is None:
            problems.append("FETCH_STARTED_AT_MISSING_WITH_COMPLETED")
        if "fetch_started_at" in parsed and "fetch_completed_at" in parsed:
            if parsed["fetch_completed_at"] < parsed["fetch_started_at"]:
                problems.append("FETCH_COMPLETED_BEFORE_STARTED")
        if self.source_timestamp_state not in SOURCE_TIMESTAMP_STATES:
            problems.append("SOURCE_TIMESTAMP_STATE_NOT_RECOGNISED")
        elif self.source_timestamp_state == SOURCE_TIMESTAMP_PRESENT and not self.source_timestamp:
            problems.append("SOURCE_TIMESTAMP_STATE_PRESENT_BUT_VALUE_MISSING")
        elif self.source_timestamp_state == SOURCE_TIMESTAMP_ABSENT and self.source_timestamp:
            problems.append("SOURCE_TIMESTAMP_STATE_ABSENT_BUT_VALUE_GIVEN")
        return problems

    def time_provenance(self) -> dict[str, Any]:
        """Every time concept this observation carries, and its trust level.

        Nothing returned here is an externally attested timestamp. Presenting
        ``recorded_at`` as one would be exactly the fabrication the mission's
        red team warned about; naming the authority explicitly is the honest
        alternative to silently upgrading its trust level.
        """
        return {
            "source_event_session": self.session_date,
            "market_session": self.market_session,
            "source_timestamp": self.source_timestamp,
            "source_timestamp_state": self.source_timestamp_state,
            "fetch_started_at": self.fetch_started_at,
            "fetch_completed_at": self.fetch_completed_at,
            "system_recorded_at": self.recorded_at,
            "system_recorded_at_authority": TIME_AUTHORITY_UNATTESTED_LOCAL_CLOCK,
        }

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
        #: key -> content address of the first accepted observation for that key.
        self._first: dict[str, str] = {}
        self._latest_recorded_at: str | None = None
        self._count = 0
        accepted_rows, _races, all_addresses = self._replay()
        self._addresses: set[str] = all_addresses
        for record in accepted_rows:
            address = str(record.get("content_address", ""))
            key = str(record.get("key", ""))
            self._first[key] = address
            recorded_at = str(record.get("recorded_at", ""))
            if recorded_at and (self._latest_recorded_at is None
                                or recorded_at > self._latest_recorded_at):
                self._latest_recorded_at = recorded_at
            self._count += 1

    def _replay(self) -> tuple[list[dict[str, Any]], list[dict[str, Any]], set[str]]:
        """Replay the journal once, enforcing first-accepted-per-key at read time.

        Two independent ``ForwardRecorder`` instances (two processes, or a crash
        and restart racing a still-running writer) can each accept a genuinely
        new key before either has seen the other's write: neither has the other
        in its in-memory guard yet. The file can then durably hold two different
        ``ACCEPTED`` rows for the same key. Immutability is a per-key promise, so
        replay -- which every reader and a fresh ``__init__`` both go through --
        keeps only the first accepted content address per key, in append order,
        and reports every later, differently-addressed row for that key as a
        detected race (``race_conflicts``) instead of silently returning it as a
        second valid observation. Neither writer did anything wrong locally;
        this is what keeps the *history* coherent anyway.
        """
        accepted_rows: list[dict[str, Any]] = []
        races: list[dict[str, Any]] = []
        all_addresses: set[str] = set()
        first_address_for_key: dict[str, str] = {}
        for record in read_jsonl(self.path):
            if record.get("state") != RECORD_ACCEPTED:
                continue
            address = str(record.get("content_address", ""))
            key = str(record.get("key", ""))
            if address in all_addresses:
                continue  # the exact same accepted row, encountered again
            all_addresses.add(address)
            existing = first_address_for_key.get(key)
            if existing is None:
                first_address_for_key[key] = address
                accepted_rows.append(record)
            else:
                races.append(record)
        return accepted_rows, races, all_addresses

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
        """The authoritative accepted observation for every key.

        Goes through :meth:`_replay`, so a second writer's race for an
        already-claimed key is excluded here -- see ``race_conflicts`` -- rather
        than returned as if it were a second valid observation.
        """
        return self._replay()[0]

    def conflicts(self) -> list[dict[str, Any]]:
        return [record for record in read_jsonl(self.path)
                if record.get("state") == RECORD_CONFLICT]

    def race_conflicts(self) -> list[dict[str, Any]]:
        """Rows a second writer accepted for a key another writer already won.

        Each of these was honestly journaled ``ACCEPTED`` by the process that
        wrote it -- at that instant it had no way to know the key was already
        taken. Only the first one in append order is authoritative; the rest are
        surfaced here rather than silently merged into :meth:`accepted`, so a
        two-writer race is a visible, auditable event instead of an inconsistent
        history nobody notices.
        """
        return self._replay()[1]

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
            "race_conflicts": len(self.race_conflicts()),
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

    def ledger_fingerprint(self) -> str | None:
        """Content fingerprint of the whole accepted ledger, order-independent.

        Changes whenever the accepted set changes, and is stable across
        restarts and re-ordered replay since it hashes the sorted,
        deduplicated content addresses -- the same contract
        ``DatasetRecord.fingerprint`` gives a committed CSV snapshot, extended
        to an ever-growing forward ledger. ``None`` only when nothing has been
        accepted yet.
        """
        addresses = sorted(str(record.get("content_address")) for record in self.accepted())
        if not addresses:
            return None
        return "sha256:" + hashlib.sha256("|".join(addresses).encode("utf-8")).hexdigest()

    def earliest_recorded_at(self) -> str | None:
        """The instant this ledger's oldest accepted write was appended.

        This is what admissibility's forward-confirmation rule should compare
        a protocol freeze against, not any session's calendar label: a session
        date is whatever the caller supplies, but ``recorded_at`` is bound by
        this recorder's own forward-only monotonicity and cannot be moved
        earlier after the fact.
        """
        recorded_ats = [str(record.get("recorded_at")) for record in self.accepted()
                        if record.get("recorded_at")]
        return min(recorded_ats) if recorded_ats else None

    def __len__(self) -> int:
        return self._count
