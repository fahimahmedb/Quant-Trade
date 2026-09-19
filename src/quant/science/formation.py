"""The closed signal geometry, with D07's open dimensions left open.

``governance/D07_OPEN_SPACE_BOUNDARY.md`` closes a great deal and this module
implements exactly that, no more:

* rolling formation window ``W(S) = {S and the preceding 9 regular sessions}``;
* state is the set of *distinct qualifying insider CIKs* in that window;
* threshold crossing ``<2 -> >=2``;
* no repeated formation while the window remains active, re-arm only once the
  window falls below two;
* ``WINDOW_EXPIRY_PRECEDES_SESSION_ADDITIONS`` — expiry is a session-boundary
  transition, evaluated before any observation attached to that session, and no
  further expiry happens inside the session;
* entry at the first regular-session open strictly after the EDGAR date, never
  same day;
* hold of 20 regular sessions.

Four dimensions stay open, and this module refuses to choose any of them:

* **O1** — the projection of an EDGAR date with no regular session onto the
  calendar. The admissible set is exhaustive and frozen:
  ``{PREVIOUS_REGULAR_SESSION, NEXT_REGULAR_SESSION}``. ``NEAREST_REGULAR_SESSION``
  is inadmissible and is refused by name.
* **O2** — intra-session application order and the logical crossing instant. The
  caller supplies a declared deterministic ordering key; this module does not
  enumerate an admissible O2 set, because D07 does not.
* **O3** — interval identification/indexing for the closed 20-session hold. The
  caller declares the convention; the holding length is not negotiable and no
  payoff substitute is ever produced for a terminal or absent observation, which
  routes to D19 instead.
* **O4** — overlap geometry, which alone can change the meaning and cardinality
  of an *observation*. Until it is declared, an observation count is
  ``D05_B_UNTIL_O4_FROZEN`` rather than a number.

An undeclared dimension produces a state, never a default.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Iterable, Sequence


#: Exhaustive admissible O1 set (``O1_ADMISSIBLE_SET_IS_EXHAUSTIVE``).
O1_PREVIOUS = "PREVIOUS_REGULAR_SESSION"
O1_NEXT = "NEXT_REGULAR_SESSION"
O1_ADMISSIBLE = (O1_PREVIOUS, O1_NEXT)

#: Named and excluded by D07 section 3 (O1). Refused rather than ignored.
O1_INADMISSIBLE = {
    "NEAREST_REGULAR_SESSION": "O1_ADMISSIBLE_SET_IS_EXHAUSTIVE",
    "DAY_OF_WEEK_HYBRID": "O1_ADMISSIBLE_SET_IS_EXHAUSTIVE",
    "ISSUER_DEPENDENT": "O1_ADMISSIBLE_SET_IS_EXHAUSTIVE",
    "FILING_DEPENDENT": "O1_ADMISSIBLE_SET_IS_EXHAUSTIVE",
}

#: Closed constants. Not parameters.
FORMATION_WINDOW_SESSIONS = 10
FORMATION_THRESHOLD = 2
HOLD_SESSIONS = 20

FORMATION_UNRESOLVED = "FORMATION_GEOMETRY_UNRESOLVED"
OBSERVATION_COUNT_UNRESOLVED = "D05_B_UNTIL_O4_FROZEN"
D19_TERMINAL_TREATMENT_REQUIRED = "D19_TERMINAL_TREATMENT_REQUIRED"
EXPOSURE_INTERVAL_INCOMPLETE = "EXPOSURE_INTERVAL_INCOMPLETE"


class SessionCalendar:
    """The regular market session calendar, in order."""

    def __init__(self, sessions: Sequence[str]) -> None:
        ordered = sorted(set(sessions))
        if list(ordered) != list(sessions):
            self.sessions = tuple(ordered)
        else:
            self.sessions = tuple(sessions)
        self._index = {session: position for position, session in enumerate(self.sessions)}

    def __contains__(self, session: object) -> bool:
        return session in self._index

    def __len__(self) -> int:
        return len(self.sessions)

    def index_of(self, session: str) -> int | None:
        return self._index.get(session)

    def at(self, position: int) -> str | None:
        if 0 <= position < len(self.sessions):
            return self.sessions[position]
        return None

    def previous_session(self, date: str) -> str | None:
        """Latest regular session strictly before ``date``."""
        candidates = [session for session in self.sessions if session < date]
        return candidates[-1] if candidates else None

    def next_session(self, date: str) -> str | None:
        """Earliest regular session strictly after ``date``."""
        for session in self.sessions:
            if session > date:
                return session
        return None

    def window(self, session: str, length: int = FORMATION_WINDOW_SESSIONS) -> tuple[str, ...]:
        """``{S and the preceding length-1 regular sessions}``."""
        position = self.index_of(session)
        if position is None:
            return ()
        start = max(0, position - (length - 1))
        return self.sessions[start:position + 1]


@dataclass(frozen=True)
class O3Convention:
    """A declared O3 interval-indexing convention.

    The 20-session hold is closed; only the indexing is open, so the convention
    carries a name and the exit index offset it implies. An offset that would
    change the holding length is refused.
    """

    name: str
    #: Sessions from the entry session index to the exit session index.
    exit_index_offset: int = HOLD_SESSIONS

    def violations(self) -> list[str]:
        problems: list[str] = []
        if not self.name:
            problems.append("O3_CONVENTION_UNNAMED")
        if self.exit_index_offset not in (HOLD_SESSIONS - 1, HOLD_SESSIONS):
            problems.append("O3_CANNOT_CHANGE_THE_CLOSED_TWENTY_SESSION_HOLD")
        return problems

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GeometryChoice:
    """One point in the D07 open space. ``None`` means undeclared, not default."""

    o1: str | None = None
    #: Declared name of the deterministic intra-session ordering rule.
    o2_ordering: str | None = None
    o3: O3Convention | None = None
    #: Declared name of the overlap representation rule.
    o4_overlap: str | None = None

    def violations(self) -> list[str]:
        problems: list[str] = []
        if self.o1 is not None:
            if self.o1 in O1_INADMISSIBLE:
                problems.append(f"O1_INADMISSIBLE:{self.o1}:{O1_INADMISSIBLE[self.o1]}")
            elif self.o1 not in O1_ADMISSIBLE:
                problems.append(f"O1_NOT_IN_EXHAUSTIVE_ADMISSIBLE_SET:{self.o1}")
        if self.o3 is not None:
            problems.extend(self.o3.violations())
        return problems

    @property
    def formation_resolved(self) -> bool:
        return self.o1 is not None and self.o2_ordering is not None

    @property
    def exposure_resolved(self) -> bool:
        return self.o3 is not None

    @property
    def observation_cardinality_resolved(self) -> bool:
        return self.o4_overlap is not None

    def to_dict(self) -> dict[str, Any]:
        return {"o1": self.o1, "o2_ordering": self.o2_ordering,
                "o3": self.o3.to_dict() if self.o3 else None,
                "o4_overlap": self.o4_overlap}


@dataclass(frozen=True)
class QualifyingObservation:
    """One qualifying filing/owner pair attached to a formation session."""

    issuer_cik: str
    owner_cik: str
    #: The frozen source temporal fact. Never redefined by O1.
    edgar_date: str
    #: Deterministic tie-break identity for O2 ordering (e.g. an accession).
    source_identity: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExposureInterval:
    """The closed 20-session exposure, indexed under a declared O3 convention."""

    entry_session: str | None
    exit_session: str | None
    state: str
    o3_name: str | None = None
    detail: str = ""

    @property
    def resolved(self) -> bool:
        return self.state == "EXPOSURE_INTERVAL_RESOLVED"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FormationEvent:
    """A threshold crossing ``<2 -> >=2`` at one formation session."""

    issuer_cik: str
    formation_session: str
    #: The observation whose application produced the crossing.
    triggering: QualifyingObservation
    #: Distinct qualifying insider CIKs in the window after the crossing.
    distinct_owners: tuple[str, ...]
    #: Position of the triggering observation inside the session's application
    #: order, which is an O2 consequence.
    intra_session_position: int
    exposure: ExposureInterval | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"issuer_cik": self.issuer_cik, "formation_session": self.formation_session,
                "triggering": self.triggering.to_dict(),
                "distinct_owners": list(self.distinct_owners),
                "intra_session_position": self.intra_session_position,
                "exposure": self.exposure.to_dict() if self.exposure else None}


#: Deterministic ordering keys a caller may declare for O2. This module does not
#: claim the set is exhaustive: D07 leaves O2 open without enumerating it.
ORDERING_KEYS: dict[str, Callable[[QualifyingObservation], tuple]] = {
    "SOURCE_IDENTITY_ASCENDING": lambda item: (item.source_identity, item.owner_cik),
    "OWNER_CIK_ASCENDING": lambda item: (item.owner_cik, item.source_identity),
}


class FormationEngine:
    """Applies the closed formation semantics under one declared geometry."""

    def __init__(self, calendar: SessionCalendar, geometry: GeometryChoice,
                 ordering_keys: dict[str, Callable[[QualifyingObservation], tuple]] | None
                 = None) -> None:
        self.calendar = calendar
        self.geometry = geometry
        self.ordering_keys = ordering_keys or ORDERING_KEYS

    # -- O1 -------------------------------------------------------------------

    def formation_session(self, edgar_date: str) -> str | None:
        """Project a frozen EDGAR date onto a formation session.

        When the EDGAR date is itself a regular session, no choice remains. Only
        a date with no regular session consumes the O1 convention.
        """
        if edgar_date in self.calendar:
            return edgar_date
        if self.geometry.o1 == O1_PREVIOUS:
            return self.calendar.previous_session(edgar_date)
        if self.geometry.o1 == O1_NEXT:
            return self.calendar.next_session(edgar_date)
        return None

    # -- O3 -------------------------------------------------------------------

    def exposure(self, edgar_date: str,
                 observable: Callable[[str], bool] | None = None) -> ExposureInterval:
        """Entry at the first session strictly after the EDGAR date, hold 20."""
        if not self.geometry.exposure_resolved:
            return ExposureInterval(None, None, FORMATION_UNRESOLVED,
                                    detail="O3_INTERVAL_CONVENTION_UNDECLARED")
        convention = self.geometry.o3
        assert convention is not None
        problems = convention.violations()
        if problems:
            return ExposureInterval(None, None, FORMATION_UNRESOLVED,
                                    convention.name, ";".join(problems))
        entry = self.calendar.next_session(edgar_date)
        if entry is None:
            return ExposureInterval(None, None, EXPOSURE_INTERVAL_INCOMPLETE,
                                    convention.name, "NO_SESSION_AFTER_EDGAR_DATE")
        entry_index = self.calendar.index_of(entry)
        assert entry_index is not None
        exit_session = self.calendar.at(entry_index + convention.exit_index_offset)
        if exit_session is None:
            return ExposureInterval(entry, None, EXPOSURE_INTERVAL_INCOMPLETE,
                                    convention.name,
                                    "CALENDAR_ENDS_BEFORE_THE_TWENTIETH_SESSION")
        if observable is not None:
            span = self.calendar.sessions[entry_index:entry_index
                                          + convention.exit_index_offset + 1]
            absent = [session for session in span if not observable(session)]
            if absent:
                # D07-O3 defines no payoff substitute; D19 owns the treatment.
                return ExposureInterval(entry, exit_session,
                                        D19_TERMINAL_TREATMENT_REQUIRED, convention.name,
                                        f"sessions not observable: {absent[:5]}")
        return ExposureInterval(entry, exit_session, "EXPOSURE_INTERVAL_RESOLVED",
                                convention.name)

    # -- formation ------------------------------------------------------------

    def run(self, observations: Iterable[QualifyingObservation],
            observable: Callable[[str], bool] | None = None
            ) -> dict[str, Any]:
        """Apply the closed semantics issuer by issuer.

        Returns a document carrying either the formation events or the reason no
        geometry was available to produce them.
        """
        problems = self.geometry.violations()
        if problems:
            return {"state": FORMATION_UNRESOLVED, "events": [],
                    "reasons": sorted(set(problems))}
        if not self.geometry.formation_resolved:
            reasons = []
            if self.geometry.o1 is None:
                reasons.append("O1_PROJECTION_UNDECLARED")
            if self.geometry.o2_ordering is None:
                reasons.append("O2_INTRA_SESSION_ORDERING_UNDECLARED")
            return {"state": FORMATION_UNRESOLVED, "events": [], "reasons": reasons}
        ordering = self.ordering_keys.get(self.geometry.o2_ordering)
        if ordering is None:
            return {"state": FORMATION_UNRESOLVED, "events": [],
                    "reasons": [f"O2_ORDERING_RULE_NOT_SUPPLIED:{self.geometry.o2_ordering}"]}

        attached: dict[str, dict[str, list[QualifyingObservation]]] = {}
        unattached: list[dict[str, Any]] = []
        for observation in observations:
            session = self.formation_session(observation.edgar_date)
            if session is None:
                unattached.append({"observation": observation.to_dict(),
                                   "reason": "NO_FORMATION_SESSION_UNDER_DECLARED_O1"})
                continue
            attached.setdefault(observation.issuer_cik, {}).setdefault(
                session, []).append(observation)

        events: list[FormationEvent] = []
        for issuer_cik in sorted(attached):
            events.extend(self._run_issuer(issuer_cik, attached[issuer_cik], ordering,
                                          observable))
        return {"state": "FORMATION_RESOLVED", "geometry": self.geometry.to_dict(),
                "events": [event.to_dict() for event in events],
                "event_count": len(events),
                "unattached": unattached,
                "observation_count": self.observation_count(events)}

    def _run_issuer(self, issuer_cik: str,
                    by_session: dict[str, list[QualifyingObservation]],
                    ordering: Callable[[QualifyingObservation], tuple],
                    observable: Callable[[str], bool] | None) -> list[FormationEvent]:
        #: (formation_session, owner_cik) pairs currently inside the window.
        live: list[tuple[str, str, QualifyingObservation]] = []
        armed = True
        events: list[FormationEvent] = []
        first = min(by_session)
        last = max(by_session)
        start = self.calendar.index_of(first)
        end = self.calendar.index_of(last)
        if start is None or end is None:
            return events
        for position in range(start, end + 1):
            session = self.calendar.at(position)
            assert session is not None
            # 1. session-boundary expiry, before anything attached to this session.
            window = set(self.calendar.window(session))
            live = [entry for entry in live if entry[0] in window]
            # 2. recompute, 3. re-arm caused by that expiry step.
            if not armed and len({entry[1] for entry in live}) < FORMATION_THRESHOLD:
                armed = True
            # 4. apply this session's observations, in the declared O2 order.
            todays = sorted(by_session.get(session, []), key=ordering)
            for index, observation in enumerate(todays):
                before = len({entry[1] for entry in live})
                live.append((session, observation.owner_cik, observation))
                after = len({entry[1] for entry in live})
                if (armed and before < FORMATION_THRESHOLD
                        and after >= FORMATION_THRESHOLD):
                    exposure = (self.exposure(observation.edgar_date, observable)
                                if self.geometry.exposure_resolved else None)
                    events.append(FormationEvent(
                        issuer_cik=issuer_cik, formation_session=session,
                        triggering=observation,
                        distinct_owners=tuple(sorted({entry[1] for entry in live})),
                        intra_session_position=index, exposure=exposure))
                    armed = False
            # 5. no further expiry inside the session.
        return events

    # -- O4 -------------------------------------------------------------------

    def observation_count(self, events: Sequence[FormationEvent]) -> Any:
        """Observation cardinality is an O4 consequence, not a count of events."""
        if not self.geometry.observation_cardinality_resolved:
            return OBSERVATION_COUNT_UNRESOLVED
        return len(events)
