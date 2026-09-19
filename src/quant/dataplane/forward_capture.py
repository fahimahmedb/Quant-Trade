"""Forward-capture execution: one attempt, fully accounted for.

This module is the seam the mission asks for: "Construis une interface propre
que le Control Plane pourra appeler." ``execute_forward_capture`` is a single
function that performs exactly one capture cycle -- fetch, journal the
attempt, record what validates -- and returns everything that happened. It
contains no scheduling loop, no sleep, no autonomous thread: *whether* to call
it is entirely the caller's decision, exactly the relationship
``clock.py`` already has with ``SecForm4Collector.poll_due()`` /
``.poll()`` for the P0 lane (read, never modified, to keep this contract
consistent with the one precedent this repository already has for a
Control-Plane-callable capture lane).

Today, the only caller is the manual runner in
``scripts/forward_capture_runner.py``, which calls this exact function and
nothing else. When the Control Plane is ready to own forward-capture
scheduling, a future change to ``clock.py`` (out of scope for this mission)
can add a ``_run_due_forward_capture`` tick branch that calls the same
``due`` / ``execute_forward_capture`` pair with its own injectable clock,
the same way it already does for SEC. Nothing in this module is inserted into
the existing ``PersistentQueue`` / ``ResearchTask`` machinery: that queue's
task dispatch is hard-coded in ``clock.py`` to the ``research_lane`` worker,
which this mission must not modify, so adding a phantom, permanently
unscheduled task there would only add confusing status-surface noise for no
operational benefit.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

from ..state import append_jsonl, read_json, read_jsonl, utc_now, write_json
from .adapters import DataUnavailable, fetch_yahoo_daily
from .forward_recorder import (SOURCE_TIMESTAMP_ABSENT, ForwardObservation,
                               ForwardRecorder, RecordOutcome)
from .panel import PricePanel

# -- attempt outcomes and failure states (mission section 8) ------------------

ATTEMPT_SUCCEEDED = "ATTEMPT_SUCCEEDED"
ATTEMPT_FAILED = "ATTEMPT_FAILED"

FAILURE_DNS_OR_NETWORK = "DNS_OR_NETWORK_FAILURE"
FAILURE_TIMEOUT = "TIMEOUT"
FAILURE_HTTP_ERROR = "HTTP_ERROR_INCLUDING_RATE_LIMIT"
FAILURE_MALFORMED_RESPONSE = "MALFORMED_JSON_RESPONSE"
FAILURE_SOURCE_ERROR_PAYLOAD = "SOURCE_REPORTED_ERROR_PAYLOAD"
FAILURE_SCHEMA_CHANGED = "SOURCE_SCHEMA_CHANGED"
FAILURE_TRUNCATED = "TRUNCATED_OR_PARTIAL_RESPONSE"
FAILURE_NO_USABLE_ROWS = "NO_USABLE_ROWS_RETURNED"
FAILURE_UNCLASSIFIED = "UNCLASSIFIED_ADAPTER_EXCEPTION"

# -- validation states ---------------------------------------------------------

VALIDATION_OK = "VALIDATION_OK"
VALIDATION_FAILED = "VALIDATION_FAILED"
VALIDATION_NOT_APPLICABLE = "NOT_APPLICABLE_ATTEMPT_FAILED_BEFORE_VALIDATION"


class ForwardCaptureFailure(RuntimeError):
    """Raise this from a test/fake adapter to inject an exact failure state.

    The real Yahoo-backed adapter below never raises this directly -- its
    failures are classified from the exceptions ``fetch_yahoo_daily`` actually
    raises, honestly, not from a hand-picked list. This exception exists so
    adversarial tests can exercise every named failure state (including ones
    the current real adapter cannot yet distinguish, such as a truncated
    transfer) without needing a real flaky network to reproduce them.
    """

    def __init__(self, failure_state: str, message: str) -> None:
        super().__init__(message)
        self.failure_state = failure_state


def _classify_yahoo_exception(exc: DataUnavailable) -> str:
    """Classify what `adapters.fetch_yahoo_daily` actually raises, honestly.

    ``fetch_yahoo_daily`` re-raises the underlying stdlib exception as
    ``DataUnavailable(...) from exc``, so the original type survives on
    ``__cause__`` even though the adapter's own message is just text. Two of
    its failure paths ("no adjusted close series", "no complete bars",
    "source returned error") never had an underlying exception -- they are
    the adapter's own checks -- so those are matched by message instead.
    """
    cause = exc.__cause__
    if cause is None:
        message = str(exc)
        if "source returned error" in message:
            return FAILURE_SOURCE_ERROR_PAYLOAD
        if "no adjusted close series" in message or "no complete bars" in message:
            return FAILURE_NO_USABLE_ROWS
        return FAILURE_UNCLASSIFIED
    name = type(cause).__name__
    if name == "HTTPError":
        return FAILURE_HTTP_ERROR
    if name == "URLError":
        return FAILURE_DNS_OR_NETWORK
    if name in ("TimeoutError", "timeout"):
        return FAILURE_TIMEOUT
    if name == "JSONDecodeError":
        return FAILURE_MALFORMED_RESPONSE
    if name == "OSError":
        return FAILURE_DNS_OR_NETWORK
    return FAILURE_UNCLASSIFIED


def _classify_failure(exc: Exception) -> str:
    if isinstance(exc, ForwardCaptureFailure):
        return exc.failure_state
    if isinstance(exc, DataUnavailable):
        return _classify_yahoo_exception(exc)
    if isinstance(exc, (KeyError, IndexError, TypeError)):
        # fetch_yahoo_daily does not itself catch a response whose JSON parses
        # but whose expected keys have moved -- that propagates as one of
        # these. Classifying it here, without editing the stable, already
        # tested adapters.py, is what makes schema drift a named, testable
        # failure state instead of an unhandled crash.
        return FAILURE_SCHEMA_CHANGED
    return FAILURE_UNCLASSIFIED


# -- injectable time source, declared separately from the SEC lane's ----------
# See the module docstring: the forward lane does not import the SEC
# subpackage's Timebase, to keep the two capture lanes independent.

class ForwardTimebase:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class FrozenForwardTimebase(ForwardTimebase):
    """Advances only when told to, so a test controls fetch duration exactly."""

    def __init__(self, start: datetime | None = None):
        self._now = start or datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now = self._now + timedelta(seconds=seconds)


# -- the adapter contract (mission section 4) ----------------------------------

@dataclass(frozen=True)
class CaptureAttempt:
    """One fetch attempt, fully accounted for -- every mission-required field
    present even on failure. Nothing here is optional-by-omission: an attempt
    that never got bytes back still has an ``attempt_id``, a ``fetch_started_at``
    and a ``failure_state``, never a silently absent record.
    """

    attempt_id: str
    source_id: str
    #: The adapter contract's own declared version/fingerprint -- not the
    #: payload's fingerprint, which is `payload_hash` below.
    source_version: str
    market_session: str
    symbols_requested: tuple[str, ...]
    fetch_started_at: str
    fetch_completed_at: str | None
    outcome: str
    failure_state: str | None
    schema_version: str
    #: Content hash of the exact payload this attempt received, or None if the
    #: attempt never received one.
    payload_hash: str | None
    validation_state: str
    #: One-line description of where this attempt's output goes next.
    lineage: str
    symbols_observed: tuple[str, ...] = ()
    #: Calendar session dates this attempt's payload actually covered. Empty on
    #: failure -- a failed attempt reveals nothing about which sessions it
    #: would have returned. The coverage ledger uses this, not a guessed
    #: lookback window, to decide whether a *successful* attempt was ever in a
    #: position to have produced a given session.
    sessions_observed: tuple[str, ...] = ()
    detail: str = ""

    def __post_init__(self) -> None:
        if self.outcome == ATTEMPT_FAILED and self.failure_state is None:
            raise ValueError("a failed attempt must name a failure_state")
        if self.outcome == ATTEMPT_SUCCEEDED and self.failure_state is not None:
            raise ValueError("a succeeded attempt must not carry a failure_state")

    def to_dict(self) -> dict[str, Any]:
        document = asdict(self)
        document["symbols_requested"] = list(self.symbols_requested)
        document["symbols_observed"] = list(self.symbols_observed)
        document["sessions_observed"] = list(self.sessions_observed)
        return document


class AttemptJournal:
    """Durable, append-only record of every capture attempt, success or failure.

    This is what lets the coverage ledger (``forward_coverage.py``) answer
    "what was attempted" and "when did we know" independently of whether the
    attempt ever produced an accepted observation -- a failed attempt is
    recorded exactly as durably as a successful one.
    """

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def append(self, attempt: CaptureAttempt) -> dict[str, Any]:
        document = attempt.to_dict()
        document["journaled_at"] = utc_now()
        append_jsonl(self.path, document)
        return document

    def all(self) -> list[dict[str, Any]]:
        return list(read_jsonl(self.path))

    def for_source(self, source_id: str) -> list[dict[str, Any]]:
        return [row for row in self.all() if row.get("source_id") == source_id]

    def latest(self, source_id: str) -> dict[str, Any] | None:
        rows = self.for_source(source_id)
        return rows[-1] if rows else None


# -- the scheduling-boundary contract (mission section 6) ----------------------

@dataclass(frozen=True)
class ForwardCaptureRequest:
    """What is being asked for. Declarative only -- it carries no scheduling
    decision, so building one is never itself an act of scheduling.
    """

    source_id: str
    symbols: tuple[str, ...]
    market_session: str = "REGULAR"
    min_interval_seconds: int = 3600
    schema_version: str = "yahoo_daily_chart@v1"
    #: How much history to request per attempt. Small on purpose: forward
    #: capture only needs the most recently closed session(s); the recorder's
    #: own idempotence makes re-submitting a few days of overlap harmless
    #: (DUPLICATE_IGNORED), which is what lets a runner that missed a few days
    #: catch back up without a separate backfill engine.
    lookback_range: str = "5d"

    def to_dict(self) -> dict[str, Any]:
        document = asdict(self)
        document["symbols"] = list(self.symbols)
        return document


@dataclass
class ForwardCaptureTaskState:
    """Durable, per-source capture disposition.

    Deliberately not a ``autonomous_research.runtime.ResearchTask`` inserted
    into the Control Plane's ``PersistentQueue``: ``clock.py``'s task dispatch
    is hard-coded to the ``research_lane`` worker and this mission must not
    modify ``clock.py``, so a task with any other worker name would only ever
    sit permanently ``BLOCKED`` on the status surface with no path to running --
    noise, not infrastructure. This is a small, separate, additive object a
    future Control Plane change can adopt.

    These counters are best-effort telemetry, not immutable evidence: unlike
    the ``ForwardRecorder`` ledger and the ``AttemptJournal`` (both append-only
    and safe under concurrent writers -- see their own docstrings), this is a
    single mutable JSON document. Two processes racing a `save()` here can lose
    an update to each other. That is an acceptable, named limitation for a
    bookkeeping counter; it must never be true of the observation ledger
    itself, which is why the recorder and the journal are append-only.
    """

    source_id: str
    enabled: bool = True
    attempts: int = 0
    successes: int = 0
    consecutive_failures: int = 0
    last_attempt_at: str | None = None
    last_success_at: str | None = None
    last_outcome: str | None = None
    last_failure_state: str | None = None
    blocked_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ForwardCaptureTaskStore:
    """Persistent registry of ``ForwardCaptureTaskState``, one per source."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        payload = read_json(self.path, {"version": 1, "tasks": {}}) or {"version": 1, "tasks": {}}
        self.tasks: dict[str, ForwardCaptureTaskState] = {
            key: ForwardCaptureTaskState(**value) for key, value in payload["tasks"].items()}

    def get(self, source_id: str) -> ForwardCaptureTaskState:
        return self.tasks.setdefault(source_id, ForwardCaptureTaskState(source_id=source_id))

    def save(self) -> None:
        write_json(self.path, {"version": 1,
                               "tasks": {key: task.to_dict()
                                         for key, task in sorted(self.tasks.items())}})


def _parse_instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def due(task: ForwardCaptureTaskState, request: ForwardCaptureRequest, now: datetime) -> bool:
    """Pure predicate a future Control Plane tick (or a manual runner) can call.

    Not a loop, a thread or a sleep -- it only answers whether the declared
    minimum interval has elapsed since the last attempt. Deciding *when* to
    call it is entirely the caller's job, exactly the relationship ``clock.py``
    already has with ``SecForm4Collector.poll_due()``.
    """
    if not task.enabled:
        return False
    if task.last_attempt_at is None:
        return True
    elapsed = (now - _parse_instant(task.last_attempt_at)).total_seconds()
    return elapsed >= request.min_interval_seconds


@dataclass(frozen=True)
class ForwardCaptureResult:
    attempt: CaptureAttempt
    record_outcomes: tuple[RecordOutcome, ...]
    task_state: ForwardCaptureTaskState

    @property
    def accepted_count(self) -> int:
        return sum(1 for outcome in self.record_outcomes if outcome.accepted)

    def to_dict(self) -> dict[str, Any]:
        return {"attempt": self.attempt.to_dict(),
                "record_outcomes": [outcome.to_dict() for outcome in self.record_outcomes],
                "accepted_count": self.accepted_count,
                "task_state": self.task_state.to_dict()}


def _panel_payload_hash(panel: PricePanel) -> str:
    """Content hash of exactly the bars this fetch returned.

    This becomes both the attempt's ``payload_hash`` and every resulting
    observation's ``source_fingerprint`` -- the fingerprint of the exact
    payload the source returned for this attempt, per
    ``ForwardObservation``'s own contract.
    """
    canonical = "|".join(
        f"{date}:{symbol}:" + ",".join(f"{name}={bar[name]!r}" for name in PricePanel.FIELDS)
        for (date, symbol), bar in sorted(panel.bars.items()))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _observations_from_panel(panel: PricePanel, fetch_started_at: str, fetch_completed_at: str,
                             market_session: str, source_id: str,
                             payload_hash: str) -> list[ForwardObservation]:
    """Every (session, symbol) bar the fetch returned, and nothing invented.

    ``PricePanel`` only ever holds bars where every required field was present
    as a finite number -- ``fetch_yahoo_daily`` drops a partial bar rather than
    filling it, and this function copies bars through unchanged. No missing
    field is ever coerced into 0.0 here.
    """
    return [
        ForwardObservation(
            symbol=symbol, session_date=date, fields=dict(bar),
            source=source_id, source_fingerprint=payload_hash,
            market_session=market_session,
            fetch_started_at=fetch_started_at, fetch_completed_at=fetch_completed_at,
            source_timestamp=None, source_timestamp_state=SOURCE_TIMESTAMP_ABSENT,
            note=f"forward capture attempt payload {payload_hash}")
        for (date, symbol), bar in sorted(panel.bars.items())
    ]


AdapterCallable = Callable[[Sequence[str]], "tuple[PricePanel, dict[str, Any]]"]


def yahoo_forward_adapter(range_: str = "5d") -> AdapterCallable:
    """Build an adapter callable over the already-authorized Yahoo source.

    Thin: it calls the existing, tested ``adapters.fetch_yahoo_daily`` and
    returns exactly what it returns. No retry, no coercion, no new network
    logic -- the stable adapter is reused unmodified, per the source
    inventory's evidence trail.
    """

    def _fetch(symbols: Sequence[str]) -> tuple[PricePanel, dict[str, Any]]:
        return fetch_yahoo_daily(list(symbols), range_=range_)

    return _fetch


def execute_forward_capture(request: ForwardCaptureRequest, recorder: ForwardRecorder,
                            journal: AttemptJournal, task_store: ForwardCaptureTaskStore,
                            adapter: AdapterCallable, timebase: ForwardTimebase,
                            attempt_id: str | None = None) -> ForwardCaptureResult:
    """Exactly one capture cycle: fetch, journal the attempt, record what validates.

    This is the entire contract a future Control Plane tick needs to call, and
    the same function today's manual runner (``scripts/forward_capture_runner.py``)
    calls -- no divergent logic between the two. Deciding *whether* to call it
    is ``due``'s job and the caller's; this function only ever performs the
    work of one already-decided call, and it always journals an attempt, on
    both success and failure.
    """
    task = task_store.get(request.source_id)
    fetch_started_at = timebase.now().isoformat()
    attempt_id = attempt_id or hashlib.sha256(
        f"{request.source_id}|{fetch_started_at}|{','.join(request.symbols)}"
        .encode("utf-8")).hexdigest()[:16]

    try:
        panel, _provenance = adapter(request.symbols)
    except Exception as exc:
        failure_state = _classify_failure(exc)
        attempt = CaptureAttempt(
            attempt_id=attempt_id, source_id=request.source_id,
            source_version=request.schema_version, market_session=request.market_session,
            symbols_requested=tuple(request.symbols), fetch_started_at=fetch_started_at,
            fetch_completed_at=None, outcome=ATTEMPT_FAILED, failure_state=failure_state,
            schema_version=request.schema_version, payload_hash=None,
            validation_state=VALIDATION_NOT_APPLICABLE,
            lineage=f"{request.source_id}->forward_capture->attempt_failed:{failure_state}",
            detail=f"{type(exc).__name__}: {exc}"[:500])
        journal.append(attempt)
        task.attempts += 1
        task.consecutive_failures += 1
        task.last_attempt_at = fetch_started_at
        task.last_outcome = ATTEMPT_FAILED
        task.last_failure_state = failure_state
        task_store.save()
        return ForwardCaptureResult(attempt, (), task)

    fetch_completed_at = timebase.now().isoformat()
    payload_hash = _panel_payload_hash(panel)
    observations = _observations_from_panel(panel, fetch_started_at, fetch_completed_at,
                                            request.market_session, request.source_id,
                                            payload_hash)
    outcomes = tuple(recorder.record_many(observations))
    accepted = sum(1 for outcome in outcomes if outcome.accepted)

    attempt = CaptureAttempt(
        attempt_id=attempt_id, source_id=request.source_id,
        source_version=request.schema_version, market_session=request.market_session,
        symbols_requested=tuple(request.symbols), fetch_started_at=fetch_started_at,
        fetch_completed_at=fetch_completed_at, outcome=ATTEMPT_SUCCEEDED, failure_state=None,
        schema_version=request.schema_version, payload_hash=payload_hash,
        validation_state=VALIDATION_OK if observations else VALIDATION_FAILED,
        lineage=f"{request.source_id}->forward_capture->{len(outcomes)}_submitted_{accepted}_accepted",
        symbols_observed=tuple(sorted({observation.symbol for observation in observations})),
        sessions_observed=tuple(sorted({observation.session_date for observation in observations})),
        detail=f"{accepted}/{len(outcomes)} observations newly accepted")
    journal.append(attempt)
    task.attempts += 1
    task.last_attempt_at = fetch_started_at
    task.last_outcome = ATTEMPT_SUCCEEDED
    task.last_failure_state = None
    if observations:
        task.successes += 1
        task.consecutive_failures = 0
        task.last_success_at = fetch_completed_at
    else:
        task.consecutive_failures += 1
    task_store.save()
    return ForwardCaptureResult(attempt, outcomes, task)
