"""The P0 Form-4 collector: request attempt -> bytes -> envelope -> coverage.

The collector is the only place SEC traffic originates, which is what makes the
frozen policy enforceable: discovery, filing acquisition, reconciliation and
every retry go through one ``_request`` method and therefore one global budget.

Its two hard invariants, both from the Astra audit, are stated once in code:

``NO_NEW_DATA`` is *earned*, never defaulted. It requires a discovery response
that parsed and validated as a correctly completed query **and** coverage
continuity that was actually established. Any other outcome is an error or
``COVERAGE_UNKNOWN``; see ``assert_no_new_data_earned``.

Coverage is a claim with a proof. Continuity means this poll walked back to the
exact identity the last validated poll reached. If it could not, the affected
cursor/page range is recorded as an open gap and coverage is
``COVERAGE_UNKNOWN`` until something proves otherwise. A healthy heartbeat never
upgrades coverage.

Steady-state cost is deliberately one small request per poll: the Latest Filings
Ownership page is walked only while entries are still unseen, and an identity
whose envelope is already durable costs zero requests.
"""

from __future__ import annotations

import uuid
import hashlib
import re
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from typing import Any, Callable

from ...paths import QuantPaths
from ...state import (append_jsonl, create_json_once, parse_ts, read_json, read_jsonl,
                      write_json)
from .budget import SecCooldownActive, SecTrafficBudget, seconds_from_retry_after
from .calendar import is_edgar_business_day
from .fingerprint import acquisition_critical_fingerprint, build_manifest, compute_fingerprint
from .scheduler import (ACTION_DISCOVERY, ACTION_FILING, ACTION_RECONCILE,
                        AWAITING_POLL, BACKOFF, BACKOFF_ENTERED, BLOCKED_NOT_CONFIGURED,
                        CONFIG_FAIL_CLOSED, COOLDOWN, COOLDOWN_OBSERVED, DISABLED,
                        DRAIN_COMPLETED, DRAINING, LANE_DISABLED, LANE_ENABLED,
                        POLL_COMPLETED, POLL_DUE, POLL_FAILED, RECONCILE_COMPLETED,
                        RECONCILIATION_SCHEDULED, RECONCILING, SERVICE_START,
                        SchedulerJournal, SchedulerTransition, WORK_ENQUEUED)
from .supervisor import MANUAL_START, UNATTESTED, host_boot_id, lifecycle_provenance
from .discovery import (DailyIndexPage, DiscoveryEntry, DiscoveryInvalid, DiscoveryPage,
                        daily_index_path, daily_index_url, discovery_path, discovery_url,
                        endpoint_class_for, parse_daily_index, parse_discovery_page)
from .policy import (DISCOVERY_ENDPOINT_CLASS, FILING_ENDPOINT_CLASS, SecAccessPolicy,
                     SecPolicyNotConfigured, policy_from_environment)
from .store import (ACCESS_FORBIDDEN, CAPTURED_OK, COOLDOWN_SUPPRESSED, DEDUPLICATED,
                    DISCOVERY_INVALID, HUNG_REQUEST, INCOMPLETE_TRANSFER, NEW_ITEMS,
                    NO_NEW_DATA, PERMANENT_CLIENT_ERROR, RATE_LIMITED, REQUEST_FAILED,
                    SERVER_ERROR, STORAGE_FAILED, SecAcquisitionEnvelope, SecAttemptRecord,
                    SecCaptureStore, SecRawObjectRecord, SecStorageFailure, digest_text)
from .timebase import Timebase
from .visibility import firewall_safe_storage
from .transport import (DEADLINE_EXCEEDED, RequestPermit, SecHttpResponse,
                        SecHttpTransport, SecTransportError, decode_body)


#: Coverage vocabulary. Only these two states may ever be reported.
COMPLETE = "COMPLETE"
COVERAGE_UNKNOWN = "COVERAGE_UNKNOWN"

#: Gap kinds. Every one of them keeps coverage at COVERAGE_UNKNOWN until resolved.
CURSOR_FELL_OUT_OF_WINDOW = "CURSOR_FELL_OUT_OF_DISCOVERY_WINDOW"
PAGE_BUDGET_EXHAUSTED = "DISCOVERY_PAGE_BUDGET_EXHAUSTED"
PAGE_FETCH_FAILED = "DISCOVERY_PAGE_FETCH_FAILED"
PAGINATION_INTERRUPTED = "PAGINATION_INTERRUPTED_BY_RESTART"
FILING_ACQUISITION_FAILED = "FILING_ACQUISITION_FAILED"
DAILY_INDEX_GAP = "DAILY_INDEX_EXPECTED_FILING_NOT_CAPTURED"
DAILY_INDEX_UNAVAILABLE = "DAILY_INDEX_UNAVAILABLE"

#: Collector liveness, derived from the attempt journal rather than asserted.
RUNNING = "RUNNING"
STALE = "STALE"
NEVER_RAN = "COLLECTOR_DID_NOT_RUN"

#: EDGAR business-day authority. Filing/index dates are Eastern Time, not UTC.
EDGAR_TIMEZONE = ZoneInfo("America/New_York")
EDGAR_BUSINESS_DAY_CLOSE_HOUR = 22

#: How long after a day closes its daily index is expected to be published.
DAILY_INDEX_SETTLE_HOURS = 30


def _edgar_business_date(stamp: datetime) -> date:
    """Map an aware instant to the EDGAR Eastern-Time business calendar date."""
    if stamp.tzinfo is None:
        raise ValueError("EDGAR_BUSINESS_DATE_REQUIRES_AWARE_TIME")
    return stamp.astimezone(EDGAR_TIMEZONE).date()


def _daily_index_settled_at_utc(day: date) -> datetime:
    """Earliest instant a closed business day may be treated as settled.

    The existing 30-hour policy is elapsed time after EDGAR closes that business
    day at 22:00 Eastern. Convert the close to UTC before adding the duration so
    daylight-saving transitions cannot shorten or lengthen the real wait.
    """
    close_local = datetime.combine(
        day, time(hour=EDGAR_BUSINESS_DAY_CLOSE_HOUR), tzinfo=EDGAR_TIMEZONE)
    return close_local.astimezone(timezone.utc) + timedelta(hours=DAILY_INDEX_SETTLE_HOURS)

MAX_FILING_ATTEMPTS = 4


class FalseSuccessPrevented(AssertionError):
    """A ``NO_NEW_DATA`` was about to be emitted without having earned it."""


def assert_no_new_data_earned(valid_discovery: bool, coverage_state: str,
                              new_identities: int) -> None:
    """The single guard standing between a healthy poll and a false success."""
    if not valid_discovery:
        raise FalseSuccessPrevented(
            "NO_NEW_DATA requires a validated discovery response")
    if coverage_state != COMPLETE:
        raise FalseSuccessPrevented(
            f"NO_NEW_DATA requires proven coverage continuity, not {coverage_state}")
    if new_identities:
        raise FalseSuccessPrevented("NO_NEW_DATA contradicts newly discovered items")


@dataclass
class CollectorState:
    """Firewall-safe durable collector state: no accession, no locator, no title."""

    enabled: bool = False
    polls: int = 0
    validated_polls: int = 0
    attempts: int = 0
    captures: int = 0
    deduplications: int = 0
    conflicts: int = 0
    last_attempt_at_utc: str | None = None
    last_poll_started_at_utc: str | None = None
    last_poll_completed_at_utc: str | None = None
    last_validated_discovery_at_utc: str | None = None
    last_capture_at_utc: str | None = None
    last_result_state: str | None = None
    last_error_class: str | None = None
    blocked_reason: str | None = None
    #: Continuity anchor, stored as an opaque digest of the source identity.
    cursor_identity_digest: str | None = None
    cursor_feed_updated_at_utc: str | None = None
    cursor_advanced_at_utc: str | None = None
    #: Where the cursor will move once every task of the proving poll is
    #: acknowledged. Held durably so the advance survives a restart mid-drain.
    pending_cursor_identity_digest: str | None = None
    pending_cursor_feed_updated_at_utc: str | None = None
    bootstrap_started_at_utc: str | None = None
    #: Where captured history begins. The discovery feed is a rolling window with
    #: no beginning to walk back to, so the first poll defines the scope instead
    #: of crawling the window, and anything older is explicitly out of captured
    #: scope until the reconciliation/backfill engine addresses it.
    bootstrap_scope_from_utc: str | None = None
    bootstrap_scope_note: str | None = None
    coverage_state: str = COVERAGE_UNKNOWN
    coverage_detail: str | None = "no validated discovery poll has completed yet"
    open_gaps: list[dict[str, Any]] = field(default_factory=list)
    resolved_gaps: list[dict[str, Any]] = field(default_factory=list)
    active_poll: dict[str, Any] | None = None
    pending_tasks: list[dict[str, Any]] = field(default_factory=list)
    reconciled_days: list[str] = field(default_factory=list)
    unreconciled_days: list[str] = field(default_factory=list)
    #: The obligation currently outstanding, so the next transition can declare
    #: prospectively that it replaces this one. Durable, because a restart must
    #: not orphan an obligation the audit is still expecting an answer for.
    open_obligation_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PollOutcome:
    """What one discovery poll established. Every field is firewall-safe."""

    poll_id: str
    result_state: str
    valid_discovery: bool
    coverage_state: str
    heartbeat_durable: bool
    pages_walked: int = 0
    discovery_object_sha256: str | None = None
    error_class: str | None = None
    gap_ids: list[str] = field(default_factory=list)
    #: Internal only: never rendered on a status surface (it is a filing count).
    new_identities: int = 0
    enqueued: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class _AttemptResult:
    attempt_id: str
    result_state: str
    response: SecHttpResponse | None = None
    error_class: str | None = None
    raw_object_sha256: str | None = None
    byte_length: int | None = None
    deduplicated: bool = False
    request_attempted_at_utc: str = ""
    response_received_at_utc: str | None = None

    @property
    def ok(self) -> bool:
        return self.response is not None and self.response.status == 200 \
            and self.response.complete and self.raw_object_sha256 is not None


class SecForm4Collector:
    """Durable, policy-compliant SEC Form-4 raw capture."""

    def __init__(self, paths: QuantPaths, *, policy: SecAccessPolicy | None = None,
                 transport: SecHttpTransport | None = None,
                 timebase: Timebase | None = None,
                 store: SecCaptureStore | None = None,
                 budget: SecTrafficBudget | None = None,
                 root: Path | None = None,
                 emit: Callable[..., Any] | None = None,
                 environ: dict[str, str] | None = None):
        self.paths = paths.ensure_sec()
        self.root = root or paths.root
        self.timebase = timebase or Timebase()
        self.emit = emit
        self.policy_error: str | None = None
        if policy is None:
            try:
                policy = policy_from_environment(environ)
            except SecPolicyNotConfigured as exc:
                # Fail closed: the lane exists, describes why it cannot run, and
                # makes no request. It is BLOCKED, not broken.
                self.policy_error = str(exc)
                policy = None
        self.policy = policy
        self.store = store or SecCaptureStore(paths, root=self.root)
        self.budget = (budget if budget is not None else
                       (SecTrafficBudget(paths.sec_budget, policy, timebase=self.timebase)
                        if policy else None))
        self.transport = transport
        if self.transport is None and policy is not None:
            self.transport = SecHttpTransport(policy, timebase=self.timebase)
        self.state = self._load_state()
        self._committed: dict[str, str] | None = None
        self.scheduler = SchedulerJournal(self.paths.sec_scheduler)
        self.lifecycle = lifecycle_provenance(environ)
        self._operator_mutation_depth = 0
        self._internal_budget_mutation_depth = 0
        # Process-local qualifying markers are transport, not authority. The
        # live child earns mutation authority only after record_service_start()
        # binds this exact instance to one durable external launch event.
        self._qualifying_mutation_authority_claimed = False
        if self.budget is not None:
            self.budget.bind_mutation_authority(self._authorize_budget_mutation)
        # The fingerprint is computed from the frozen membership, not stored and
        # trusted: a deployment whose code or policy moved must not be able to
        # present the previous window's fingerprint.
        self.fingerprint: str | None = None
        self._environ = environ
        if self.policy is not None:
            self.fingerprint = acquisition_critical_fingerprint(
                self.policy, root=self.root, environ=environ)

    # --- qualifying mutation authority ------------------------------------
    def _qualifying_history_exists(self) -> bool:
        return any(record.get("qualifying_service_mode")
                   for record in read_jsonl(self.paths.sec_lifecycle))

    def _current_process_is_qualifying(self) -> bool:
        return bool(self._qualifying_mutation_authority_claimed
                    and self.lifecycle.get("qualifying_service_mode")
                    and self.lifecycle.get("externally_attested")
                    and self.lifecycle.get("service_managed"))

    def _claim_qualifying_mutation_authority(self) -> bool:
        """Claim one externally authorized child launch for this collector instance.

        Environment markers can be copied into another SecForm4Collector, so
        they cannot by themselves authorize qualifying durable mutation. The
        service start must match exactly one external CHILD_LAUNCH_AUTHORIZED
        record, and the same launch identity may not already have been claimed
        by a prior qualifying lifecycle record.
        """
        if not self.lifecycle.get("qualifying_service_mode"):
            return False
        events_path = self.paths.sec / "supervisor_events.jsonl"
        try:
            events = list(read_jsonl(events_path))
            lifecycle_rows = list(read_jsonl(self.paths.sec_lifecycle))
        except (OSError, ValueError, TypeError, AttributeError):
            return False
        matches = [
            event for event in events
            if event.get("event") == "CHILD_LAUNCH_AUTHORIZED"
            and event.get("supervisor_id") == self.lifecycle.get("supervisor_id")
            and event.get("supervisor_invocation_id")
                == self.lifecycle.get("service_invocation_id")
            and event.get("child_boot_id") == self.lifecycle.get("boot_id")
            and event.get("lifecycle_cause") == self.lifecycle.get("lifecycle_cause")
            and event.get("fingerprint") == self.fingerprint
            and bool(event.get("qualifying_mode"))
            and (event.get("deployment_authority_nonce") or None)
                == (self.lifecycle.get("launch_authority_nonce") or None)
        ]
        if len(matches) != 1:
            return False

        already_claimed = any(
            row.get("qualifying_service_mode")
            and row.get("supervisor_id") == self.lifecycle.get("supervisor_id")
            and row.get("service_invocation_id")
                == self.lifecycle.get("service_invocation_id")
            and row.get("boot_id") == self.lifecycle.get("boot_id")
            and row.get("acquisition_critical_fingerprint") == self.fingerprint
            for row in lifecycle_rows
        )
        return not already_claimed

    def _guard_public_mutation(self, action: str) -> None:
        """Record a lower-level manual mutation once qualifying evidence exists."""
        if self._operator_mutation_depth or self._current_process_is_qualifying():
            return
        if self._qualifying_history_exists():
            self.record_operator_intervention(f"direct:{action}")

    @contextmanager
    def operator_mutation(self, command: str):
        """One durable provenance record for an explicit operator mutation."""
        self.record_operator_intervention(command)
        self._operator_mutation_depth += 1
        try:
            yield
        finally:
            self._operator_mutation_depth -= 1

    @contextmanager
    def _internal_budget_mutation(self):
        self._internal_budget_mutation_depth += 1
        try:
            yield
        finally:
            self._internal_budget_mutation_depth -= 1

    def _authorize_budget_mutation(self, operation: str) -> None:
        if self._internal_budget_mutation_depth or self._operator_mutation_depth:
            return
        if self._qualifying_history_exists():
            self.record_operator_intervention(f"direct:budget:{operation}")

    # --- scheduler provenance ---------------------------------------------
    def record_transition(self, state: str, cause: str, *, next_due_at: str | None,
                          detail: str | None = None,
                          required_action_kind: str | None = None) -> SchedulerTransition:
        """Say prospectively what the lane will do next, and when.

        The audit reconstructs the expected attempt sequence from these records.
        It must never infer that nothing was due merely because nothing was
        attempted, so a transition is written whenever the next expected action
        changes - including when the lane is blocked and nothing will happen.
        """
        budget_state = self.budget.load() if self.budget else None
        # A transition that commits to a next action creates a *named*
        # obligation, and simultaneously declares which still-open obligation it
        # replaces. Both halves are written before the new due time arrives, so
        # the audit can tell a genuine re-plan from a hole papered over later.
        obligation_id = uuid.uuid4().hex[:16] if next_due_at else None
        superseded = self.state.open_obligation_id
        transition = SchedulerTransition(
            transition_id=uuid.uuid4().hex[:16],
            recorded_at_utc=self.timebase.now_iso(),
            state=state, cause=cause, next_due_at_utc=next_due_at,
            acquisition_critical_fingerprint=self.fingerprint or "UNAVAILABLE",
            obligation_id=obligation_id,
            supersedes_obligation_id=superseded,
            required_action_kind=(required_action_kind
                                  or self._main_required_action_kind()),
            boot_id=self.lifecycle.get("boot_id"),
            lifecycle_cause=self.lifecycle.get("lifecycle_cause"),
            cooldown_until_utc=budget_state.cooldown_until_utc if budget_state else None,
            cooldown_reason=budget_state.cooldown_reason if budget_state else None,
            backoff_step=budget_state.backoff_step if budget_state else None,
            coverage_state=self.state.coverage_state,
            work_in_flight=bool(self.state.pending_tasks),
            detail=detail)
        self.scheduler.record(transition)
        self.state.open_obligation_id = obligation_id
        self.save()
        return transition

    def _main_required_action_kind(self) -> str:
        return ACTION_FILING if self.state.pending_tasks else ACTION_DISCOVERY

    def _next_reconciliation_target(self) -> date | None:
        start = self.state.bootstrap_started_at_utc
        if start is None or not self.configured or not self.state.enabled:
            return None
        day = _edgar_business_date(parse_ts(start))
        while True:
            if is_edgar_business_day(day) and day.isoformat() not in self.state.reconciled_days:
                return day
            day = day + timedelta(days=1)

    def _ensure_reconciliation_obligation(self) -> str | None:
        """Materialize source-calendar reconciliation independently of Clock."""
        day = self._next_reconciliation_target()
        if day is None:
            return None
        detail = f"daily_index:{day.isoformat()}"
        attempted = {record.get("obligation_id") for record in self.store.attempts()}
        candidates = [
            record for record in self.scheduler.all()
            if record.get("required_action_kind") == ACTION_RECONCILE
            and record.get("detail") == detail
            and record.get("obligation_id")
            and record.get("obligation_id") not in attempted
        ]
        if candidates:
            return candidates[-1]["obligation_id"]

        due = _daily_index_settled_at_utc(day)
        now = self.timebase.now().astimezone(timezone.utc)
        if due < now:
            due = now
        if self.cooldown_remaining() > 0 and self.budget is not None:
            cooldown = self.budget.load().cooldown_until_utc
            if cooldown and parse_ts(cooldown) > due:
                due = parse_ts(cooldown)
        transition = SchedulerTransition(
            transition_id=uuid.uuid4().hex[:16],
            recorded_at_utc=self.timebase.now_iso(),
            state=RECONCILING,
            cause=RECONCILIATION_SCHEDULED,
            next_due_at_utc=due.isoformat(),
            acquisition_critical_fingerprint=self.fingerprint or "UNAVAILABLE",
            obligation_id=uuid.uuid4().hex[:16],
            supersedes_obligation_id=None,
            required_action_kind=ACTION_RECONCILE,
            boot_id=self.lifecycle.get("boot_id"),
            lifecycle_cause=self.lifecycle.get("lifecycle_cause"),
            coverage_state=self.state.coverage_state,
            work_in_flight=bool(self.state.pending_tasks),
            detail=detail)
        self.scheduler.record(transition)
        return transition.obligation_id

    def next_due_at(self) -> str | None:
        """When the next acquisition action becomes due, from durable state."""
        if not self.configured or not self.state.enabled:
            return None
        cooldown = self.cooldown_remaining()
        if cooldown > 0:
            budget_state = self.budget.load()
            return budget_state.cooldown_until_utc
        if self.state.pending_tasks:
            return self.timebase.now_iso()
        last = self.state.last_poll_started_at_utc
        if last is None:
            return self.timebase.now_iso()
        due = parse_ts(last) + timedelta(seconds=self.policy.discovery_poll_seconds)
        return due.isoformat()

    def scheduler_state(self) -> str:
        if not self.configured:
            return BLOCKED_NOT_CONFIGURED
        if not self.state.enabled:
            return DISABLED
        if self.cooldown_remaining() > 0:
            budget_state = self.budget.load()
            reason = (budget_state.cooldown_reason or "")
            return COOLDOWN if reason.startswith("http_") else BACKOFF
        if self.state.pending_tasks:
            return DRAINING
        if self.poll_due():
            return POLL_DUE
        return AWAITING_POLL

    def record_current_state(self, cause: str, detail: str | None = None) -> SchedulerTransition:
        self._ensure_reconciliation_obligation()
        return self.record_transition(
            self.scheduler_state(), cause, next_due_at=self.next_due_at(),
            detail=detail, required_action_kind=self._main_required_action_kind())

    def record_operator_intervention(self, command: str) -> dict[str, Any]:
        """Durably mark a one-shot operator mutation as qualification-invalidating.

        Manual CLI commands are useful diagnostics, but they are not the
        service-managed acquisition process. If one is run during a qualifying
        window, the retrospective audit must see the intervention instead of
        mistaking its requests/transitions for continuous service evidence.
        """
        record = {
            "boot_id": host_boot_id(),
            "lifecycle_cause": MANUAL_START,
            "lifecycle_cause_declared": MANUAL_START,
            "boot_at_utc": None,
            "supervisor_id": None,
            "launch_authority_nonce": None,
            "externally_attested": False,
            "invalidates_observation_window": True,
            "service_manager": None,
            "service_managed": False,
            "service_invocation_id": None,
            "qualifying_service_mode": False,
            "effective_service_configuration": {},
            "recorded_at_utc": self.timebase.now_iso(),
            "acquisition_critical_fingerprint": self.fingerprint or "UNAVAILABLE",
            "collector_version": self.store.collector_version,
            "git_commit": self.store.git_commit,
            "operator_command": command,
        }
        append_jsonl(self.paths.sec_lifecycle, record)
        return record

    def record_service_start(self) -> dict[str, Any]:
        """Bind this process's externally attested lifecycle to the journal."""
        if (self.lifecycle.get("qualifying_service_mode")
                and not self._qualifying_mutation_authority_claimed):
            self._qualifying_mutation_authority_claimed = (
                self._claim_qualifying_mutation_authority()
            )
        record = dict(self.lifecycle,
                      recorded_at_utc=self.timebase.now_iso(),
                      acquisition_critical_fingerprint=self.fingerprint or "UNAVAILABLE",
                      collector_version=self.store.collector_version,
                      git_commit=self.store.git_commit)
        append_jsonl(self.paths.sec_lifecycle, record)
        self._ensure_reconciliation_obligation()
        # A process start cannot rewrite an existing prospective commitment.
        # Initial enable() records the first obligation once the lane is active.
        if not self.configured or (self.state.enabled and not self.state.open_obligation_id):
            cause = SERVICE_START if self.configured else CONFIG_FAIL_CLOSED
            self.record_current_state(cause, detail=self.lifecycle.get("lifecycle_cause"))
        return record

    def _external_lifecycle_binding_error(self) -> str | None:
        """Bind qualifying child claims to state written by the external supervisor.

        Environment variables are transport for provenance, not authority by
        themselves. The supervisor writes this state durably before spawning
        the child; copied environment markers cannot buy t0 readiness.
        """
        if not self.lifecycle.get("qualifying_service_mode"):
            return None
        path = self.paths.sec / "supervisor_state.json"
        try:
            state = read_json(path)
        except (OSError, ValueError, TypeError):
            return "EXTERNAL_SUPERVISOR_STATE_INVALID"
        if not isinstance(state, dict):
            return "EXTERNAL_SUPERVISOR_STATE_MISSING"
        if state.get("schema") != "p0_supervisor/v2":
            return "EXTERNAL_SUPERVISOR_STATE_INVALID"
        expected = {
            "supervisor_id": self.lifecycle.get("supervisor_id"),
            "child_boot_id": self.lifecycle.get("boot_id"),
            "supervisor_invocation_id": self.lifecycle.get("service_invocation_id"),
            "lifecycle_cause": self.lifecycle.get("lifecycle_cause"),
            "fingerprint": self.fingerprint,
        }
        if any(state.get(key) != value for key, value in expected.items()):
            return "EXTERNAL_SUPERVISOR_BINDING_MISMATCH"
        if not state.get("supervisor_running") or not state.get("service_managed"):
            return "EXTERNAL_SUPERVISOR_NOT_ACTIVE"
        if not state.get("qualifying_mode"):
            return "EXTERNAL_SUPERVISOR_NOT_QUALIFYING"
        expected_nonce = self.lifecycle.get("launch_authority_nonce") or None
        if (state.get("deployment_authority_nonce") or None) != expected_nonce:
            return "EXTERNAL_LAUNCH_AUTHORITY_MISMATCH"
        return None

    def t0_readiness(self) -> dict[str, Any]:
        """Whether the pre-t0 instrumentation is in place. Blue decides t0, not this.

        Reported, never acted on: the collector does not start or stop an
        observation window, it only says what is and is not yet true.
        """
        blockers: list[str] = []
        if (self.paths.sec / "integrity_fault.json").exists():
            blockers.append("DURABLE_INTEGRITY_FAULT")
        if not self.configured:
            blockers.append("SEC_IDENTITY_NOT_CONFIGURED")
        if self.fingerprint is None:
            blockers.append("ACQUISITION_FINGERPRINT_UNAVAILABLE")
        if not self.lifecycle.get("externally_attested"):
            blockers.append("LIFECYCLE_CAUSE_UNATTESTED")
        if not self.lifecycle.get("service_managed"):
            # No recognised service manager launched this process, so its start
            # cause rests on the operator's word rather than on provenance.
            blockers.append("LAUNCH_NOT_SERVICE_MANAGED")
        if not self.lifecycle.get("qualifying_service_mode"):
            blockers.append("NOT_QUALIFYING_SERVICE_MODE")
        if self.lifecycle.get("invalidates_observation_window"):
            blockers.append("INVALIDATING_LIFECYCLE_CAUSE")
        if not self.lifecycle.get("boot_id") or not self.lifecycle.get("supervisor_id"):
            blockers.append("LIFECYCLE_IDENTITY_INCOMPLETE")
        effective_service = self.lifecycle.get("effective_service_configuration") or {}
        if (self.lifecycle.get("qualifying_service_mode")
                and not effective_service.get("effective_unit_digest")):
            blockers.append("EFFECTIVE_SERVICE_DEFINITION_UNATTESTED")
        if (self.lifecycle.get("lifecycle_cause") == "DEPLOYMENT_RESTART"
                and not self.lifecycle.get("launch_authority_nonce")):
            blockers.append("DEPLOYMENT_AUTHORITY_MISSING")
        external_lifecycle_error = self._external_lifecycle_binding_error()
        if external_lifecycle_error:
            blockers.append(external_lifecycle_error)
        if self.lifecycle.get("qualifying_service_mode"):
            from .audit import audit_observation_window
            if not audit_observation_window(self)["accountable"]:
                blockers.append("ACQUISITION_AUDIT_NOT_ACCOUNTABLE")
        if not self.scheduler.all():
            blockers.append("NO_SCHEDULER_PROVENANCE")
        if self.configured and not self.state.enabled:
            blockers.append("COLLECTOR_DISABLED")
        if self.configured and self.state.enabled:
            if self.liveness() != RUNNING:
                blockers.append("COLLECTOR_NOT_LIVE")
            if self.state.coverage_state != COMPLETE:
                blockers.append("COVERAGE_NOT_COMPLETE")
            if self.state.open_gaps:
                blockers.append("OPEN_COVERAGE_GAPS")
            if not self.store.attempts():
                blockers.append("NO_DURABLE_ACQUISITION_ATTEMPT")
        materialized, materialized_error = self._validated_materialization()
        if materialized_error:
            blockers.append(materialized_error)
        return {"instrumentation_ready": not blockers,
                "blockers": blockers,
                "acquisition_critical_fingerprint": self.fingerprint,
                "materialized_fingerprint": materialized,
                "fingerprint_matches_materialized": (
                    materialized_error is None and materialized == self.fingerprint),
                "lifecycle_cause": self.lifecycle.get("lifecycle_cause"),
                "boot_id": self.lifecycle.get("boot_id"),
                "service_managed": self.lifecycle.get("service_managed"),
                "qualifying_service_mode": self.lifecycle.get("qualifying_service_mode"),
                "effective_service_configuration": self.lifecycle.get(
                    "effective_service_configuration"),
                "scheduler_provenance_present": bool(self.scheduler.all()),
                # This lane never declares t0 or closes the continuity state.
                "t0_authority": "BLUE_TEAM",
                "p0_continuous_service_state": "OPEN / NOT_YET_PROVEN_CONTINUOUS"}

    def _materialization_host_binding(self) -> str:
        """Bind a freeze to the host without making the semantic fingerprint host-specific."""
        machine_id = Path("/etc/machine-id")
        try:
            identity = machine_id.read_text(encoding="utf-8").strip()
        except OSError:
            from .supervisor import host_boot_id
            identity = host_boot_id() or "UNAVAILABLE"
        return digest_text(identity)

    def _validated_materialization(self) -> tuple[str | None, str | None]:
        """Return (fingerprint, error).  No repair is performed here."""
        if not self.paths.sec_fingerprint.exists():
            return None, "FINGERPRINT_NOT_MATERIALIZED"
        try:
            payload = read_json(self.paths.sec_fingerprint)
            if not isinstance(payload, dict):
                return None, "FINGERPRINT_MATERIALIZED_INVALID"
            manifest = payload["manifest"]
            stored = payload["acquisition_critical_fingerprint"]
            if payload.get("schema") != "p0_materialized_fingerprint/v2":
                return stored, "FINGERPRINT_MATERIALIZED_SCHEMA_MISMATCH"
            if payload.get("host_identity_digest") != self._materialization_host_binding():
                return stored, "FINGERPRINT_MATERIALIZED_OTHER_HOST"
            if compute_fingerprint(manifest) != stored:
                return stored, "FINGERPRINT_MATERIALIZED_SELF_MISMATCH"
            active_manifest = build_manifest(
                self.policy, root=self.root, environ=self._environ)
            if manifest != active_manifest or stored != self.fingerprint:
                return stored, "FINGERPRINT_MATERIALIZED_MISMATCH"
            if payload.get("git_commit") != self.store.git_commit:
                return stored, "FINGERPRINT_MATERIALIZED_COMMIT_MISMATCH"
            if payload.get("collector_version") != self.store.collector_version:
                return stored, "FINGERPRINT_MATERIALIZED_VERSION_MISMATCH"
            return stored, None
        except (OSError, ValueError, KeyError, TypeError):
            return None, "FINGERPRINT_MATERIALIZED_INVALID"

    def materialized_fingerprint(self) -> str | None:
        fingerprint, _ = self._validated_materialization()
        return fingerprint

    def require_active_materialization(self) -> None:
        """Qualifying service cannot emit a request under stale/unbound semantics."""
        if (self.paths.sec / "integrity_fault.json").exists():
            raise SecStorageFailure("DURABLE_INTEGRITY_FAULT")
        if not self.lifecycle.get("qualifying_service_mode"):
            return
        fingerprint, error = self._validated_materialization()
        if error or fingerprint != self.fingerprint:
            self._latch_integrity_fault(error or "FINGERPRINT_MATERIALIZED_MISMATCH")
            raise SecStorageFailure(error or "FINGERPRINT_MATERIALIZED_MISMATCH")

    def _latch_integrity_fault(self, reason: str) -> None:
        try:
            create_json_once(self.paths.sec / "integrity_fault.json", {
                "reason": reason, "recorded_at_utc": self.timebase.now_iso()})
        except FileExistsError:
            pass

    def materialize_fingerprint(self) -> dict[str, Any]:
        """Freeze once. Existing content is validated, never silently rewritten."""
        if (self.paths.sec / "integrity_fault.json").exists():
            raise SecStorageFailure("DURABLE_INTEGRITY_FAULT")
        if self.policy is None:
            raise SecPolicyNotConfigured(self.policy_error or "SEC access is not configured")
        if self.paths.sec_fingerprint.exists():
            fingerprint, error = self._validated_materialization()
            if error or fingerprint != self.fingerprint:
                self._latch_integrity_fault(error or "FINGERPRINT_MATERIALIZED_MISMATCH")
                raise SecStorageFailure(error or "FINGERPRINT_MATERIALIZED_MISMATCH")
            payload = read_json(self.paths.sec_fingerprint)
            assert isinstance(payload, dict)
            return payload
        if self._qualifying_history_exists() and not self._operator_mutation_depth:
            self.record_operator_intervention("direct:materialize_fingerprint")
        manifest = build_manifest(self.policy, root=self.root, environ=self._environ)
        fingerprint = compute_fingerprint(manifest)
        payload = {
            "schema": "p0_materialized_fingerprint/v2",
            "acquisition_critical_fingerprint": fingerprint,
            "host_identity_digest": self._materialization_host_binding(),
            "materialized_at_utc": self.timebase.now_iso(),
            "collector_version": self.store.collector_version,
            "git_commit": self.store.git_commit,
            "manifest": manifest,
        }
        try:
            create_json_once(self.paths.sec_fingerprint, payload)
        except FileExistsError:
            # Concurrent materializers race only to the validator; neither may
            # overwrite the winner.
            existing, error = self._validated_materialization()
            if error or existing != fingerprint:
                raise SecStorageFailure(error or "FINGERPRINT_MATERIALIZED_MISMATCH")
            payload = read_json(self.paths.sec_fingerprint)
        self.fingerprint = fingerprint
        return payload

    # --- durable state -----------------------------------------------------
    def _state_commit_path(self) -> Path:
        return self.paths.sec / "collector_state.commits.jsonl"

    def _load_state(self) -> CollectorState:
        payload = read_json(self.paths.sec_collector_state)
        commits = list(read_jsonl(self._state_commit_path()))
        if payload is None:
            history_paths = (
                self.paths.sec_attempts, self.paths.sec_scheduler,
                self.paths.sec_lifecycle, self.paths.sec_coverage,
                self.paths.sec_raw_manifest, self.paths.sec_budget,
                self.paths.sec_locators, self.paths.sec_envelopes,
                self.paths.sec_source_versions,
                self.paths.sec / "request_intents.jsonl",
            )
            history_present = any(
                path.exists() and path.stat().st_size > 0 for path in history_paths)
            if not history_present:
                history_present = any(
                    path.is_file()
                    for directory in (
                        self.paths.sec_raw_objects,
                        self.paths.sec_incomplete_objects,
                        self.paths.sec_staging,
                    )
                    for path in directory.rglob("*"))
            if commits or history_present:
                raise SecStorageFailure("COLLECTOR_STATE_MISSING_WITH_HISTORY")
            return CollectorState()
        if not isinstance(payload, dict):
            raise SecStorageFailure("COLLECTOR_STATE_INVALID")
        expected = set(CollectorState().to_dict())
        actual = set(payload)
        if actual != expected:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            raise SecStorageFailure(
                f"COLLECTOR_STATE_SCHEMA_MISMATCH:missing={missing}:extra={extra}")
        digest = compute_fingerprint(payload)
        if not commits:
            raise SecStorageFailure("COLLECTOR_STATE_UNCOMMITTED_OR_LEGACY")
        if commits[-1].get("state_digest") != digest:
            raise SecStorageFailure("COLLECTOR_STATE_UNCOMMITTED_OR_ROLLED_BACK")
        return CollectorState(**payload)

    def save(self) -> None:
        payload = self.state.to_dict()
        write_json(self.paths.sec_collector_state, payload)
        append_jsonl(self._state_commit_path(), {
            "event": "STATE_COMMITTED",
            "state_digest": compute_fingerprint(payload),
            "recorded_at_utc": self.timebase.now_iso(),
        })

    @property
    def configured(self) -> bool:
        return self.policy is not None

    def committed_identities(self) -> dict[str, str]:
        """Acknowledged identities. The envelope journal is the authority."""
        if self._committed is None:
            self._committed = self.store.committed_identities()
        return self._committed

    def enable(self) -> None:
        self._guard_public_mutation("enable")
        if not self.configured:
            raise SecPolicyNotConfigured(self.policy_error or "SEC access is not configured")
        self.state.enabled = True
        self.state.blocked_reason = None
        if self.state.bootstrap_started_at_utc is None:
            self.state.bootstrap_started_at_utc = self.timebase.now_iso()
        self.save()
        self.record_current_state(LANE_ENABLED)

    def disable(self, reason: str | None = None) -> None:
        self._guard_public_mutation("disable")
        self.state.enabled = False
        self.state.blocked_reason = reason
        self.save()
        self.record_current_state(LANE_DISABLED, detail=reason)

    # --- scheduling --------------------------------------------------------
    def cooldown_remaining(self) -> float:
        return self.budget.cooldown_remaining() if self.budget else 0.0

    def poll_due(self) -> bool:
        if not self.configured or not self.state.enabled:
            return False
        if self.cooldown_remaining() > 0:
            return False
        last = self.state.last_poll_started_at_utc
        if last is None:
            return True
        elapsed = (self.timebase.now() - parse_ts(last)).total_seconds()
        # A wall-clock regression or future/corrupt prior timestamp must never
        # buy silence. Poll immediately; the durable audit can then flag the
        # reversed timestamps instead of losing a rolling-feed observation.
        if elapsed < 0:
            return True
        return elapsed >= self.policy.discovery_poll_seconds

    def has_pending_work(self) -> bool:
        return bool(self.state.pending_tasks) and self.cooldown_remaining() <= 0

    def reconciliation_due(self) -> date | None:
        """The oldest closed day whose daily index has not been compared yet."""
        if not self.configured or not self.state.enabled:
            return None
        if self.cooldown_remaining() > 0:
            return None
        start = self.state.bootstrap_started_at_utc
        if start is None:
            return None
        now = self.timebase.now()
        if now.tzinfo is None:
            raise ValueError("SEC_RECONCILIATION_REQUIRES_AWARE_TIME")
        now_utc = now.astimezone(timezone.utc)
        day = _edgar_business_date(parse_ts(start))
        today_edgar = _edgar_business_date(now)
        while day <= today_edgar:
            key = day.isoformat()
            if (key not in self.state.reconciled_days
                    and is_edgar_business_day(day)
                    and now_utc >= _daily_index_settled_at_utc(day)):
                return day
            day = day + timedelta(days=1)
        return None

    def liveness(self) -> str:
        """Derived from the attempt journal: the three cases must be separable."""
        if self.state.last_attempt_at_utc is None:
            return NEVER_RAN
        if not self.configured or not self.state.enabled:
            return STALE
        elapsed = (self.timebase.now() - parse_ts(self.state.last_attempt_at_utc)).total_seconds()
        allowance = max(self.policy.discovery_poll_seconds * 3, self.cooldown_remaining() + 60)
        return RUNNING if 0 <= elapsed <= allowance else STALE

    # --- the single SEC request path ---------------------------------------
    def _request(self, *args: Any, **kwargs: Any) -> _AttemptResult:
        """Serialize the complete request window across every SEC consumer."""
        self.require_active_materialization()
        if self.budget is None:
            raise SecStorageFailure("SEC_TRAFFIC_BUDGET_UNAVAILABLE")
        with self.budget.network_slot():
            return self._request_serialized(*args, **kwargs)

    def _request_serialized(self, kind: str, path: str, url: str, *,
                            poll_id: str | None = None,
                            page_start: int | None = None,
                            source_identity: str | None = None,
                            source_published_at_utc: str | None = None,
                            store_bytes: bool = True,
                            obligation_id: str | None = None) -> _AttemptResult:
        """Issue one SEC request and leave a durable attempt record, always.

        The caller holds the process-shared network lease before reserve() and
        until this method has durably journalled the outcome.
        """
        endpoint_class = endpoint_class_for(kind)
        attempt_id = self.store.new_attempt_id()
        if obligation_id is None:
            obligation_id = self.state.open_obligation_id
        intent_path = self.paths.sec / "request_intents.jsonl"
        append_jsonl(intent_path, {
            "event": "INTENT", "attempt_id": attempt_id,
            "obligation_id": obligation_id, "endpoint_class": endpoint_class,
            "recorded_at_utc": self.timebase.now_iso(),
        })
        locator_digest = self.store.record_locator(
            locator=url, source_identity=source_identity, endpoint_class=endpoint_class,
            observed_at_utc=self.timebase.now_iso(), poll_id=poll_id,
            source_published_at_utc=source_published_at_utc)

        def finish(result_state: str, **extra: Any) -> _AttemptResult:
            record = SecAttemptRecord(
                attempt_id=attempt_id, attempt_kind=kind, endpoint_class=endpoint_class,
                source_locator_digest=locator_digest,
                request_attempted_at_utc=extra.pop("attempted_at", self.timebase.now_iso()),
                result_state=result_state, collector_version=self.store.collector_version,
                git_commit=self.store.git_commit, poll_id=poll_id, page_start=page_start,
                obligation_id=obligation_id, **extra)
            self.store.record_attempt(record)
            append_jsonl(intent_path, {
                "event": "FINISHED", "attempt_id": attempt_id,
                "recorded_at_utc": self.timebase.now_iso(),
            })
            self.state.attempts += 1
            self.state.last_attempt_at_utc = record.request_attempted_at_utc
            self.state.last_result_state = result_state
            self.state.last_error_class = record.error_class
            self.save()
            return _AttemptResult(
                attempt_id=attempt_id, result_state=result_state,
                error_class=record.error_class,
                raw_object_sha256=record.raw_object_sha256, byte_length=record.byte_length,
                request_attempted_at_utc=record.request_attempted_at_utc,
                response_received_at_utc=record.response_received_at_utc)

        try:
            with self._internal_budget_mutation():
                reservation = self.budget.reserve(endpoint_class)
        except SecCooldownActive as cooldown:
            return finish(COOLDOWN_SUPPRESSED, error_class=f"cooldown:{cooldown.reason}",
                          retry_after_seconds=cooldown.remaining_seconds)

        # One reservation mints exactly one permit, carrying the attempt id that
        # will journal the outcome. The transport cannot send without it and
        # cannot send twice with it, so
        # ONE_BUDGET_RESERVATION == ONE_NETWORK_REQUEST_ATTEMPT == ONE_ATTEMPT_ID
        # holds by construction rather than by inspection of the transport.
        append_jsonl(intent_path, {
            "event": "RESERVED", "attempt_id": attempt_id,
            "obligation_id": obligation_id,
            "reserved_at_utc": reservation["reserved_at_utc"],
        })
        permit = RequestPermit(attempt_id=attempt_id,
                               reserved_at_utc=reservation["reserved_at_utc"],
                               endpoint_class=endpoint_class)
        attempted_at_dt = self.timebase.now()
        attempted_at = attempted_at_dt.isoformat()
        try:
            response = self.transport.fetch(path, permit)
        except SecTransportError as exc:
            hung = exc.outcome == DEADLINE_EXCEEDED
            incomplete_id = None
            if exc.partial:
                try:
                    incomplete_id = self.store.put_object(
                        exc.partial, incomplete=True).raw_object_sha256
                except SecStorageFailure:
                    return finish(STORAGE_FAILED, attempted_at=attempted_at,
                                  error_class="partial_evidence_storage_failed",
                                  limiter_waited_seconds=reservation["waited_seconds"],
                                  duration_seconds=self._elapsed(attempted_at_dt))
            self._enter_transient_cooldown(f"transport:{exc.error_class}")
            return finish(HUNG_REQUEST if hung else REQUEST_FAILED, attempted_at=attempted_at,
                          error_class=exc.error_class, transfer_outcome=exc.outcome,
                          incomplete_object_sha256=incomplete_id,
                          limiter_waited_seconds=reservation["waited_seconds"],
                          duration_seconds=self._elapsed(attempted_at_dt))
        received_at = self.timebase.now_iso()
        append_jsonl(intent_path, {
            "event": "RECEIVED", "attempt_id": attempt_id,
            "recorded_at_utc": received_at,
            "raw_object_sha256": "sha256:" + hashlib.sha256(response.body).hexdigest(),
            "byte_length": len(response.body),
            "http_status": response.status,
            "transfer_outcome": response.transfer_outcome,
        })
        metadata = response.transport_metadata()
        common = {"attempted_at": attempted_at, "response_received_at_utc": received_at,
                  "http_status": response.status, "media_type": response.media_type,
                  "content_encoding": response.content_encoding,
                  "declared_content_length": response.declared_content_length,
                  "transfer_outcome": response.transfer_outcome,
                  "limiter_waited_seconds": reservation["waited_seconds"],
                  "duration_seconds": self._elapsed(attempted_at_dt)}

        # Preserve the exact response bytes before semantic classification,
        # including 403/429/5xx bodies.  Error responses are still acquisition
        # evidence; discarding them can make a later incident unreconstructible.
        raw_object_sha256 = None
        incomplete_id = None
        deduplicated = False
        if store_bytes:
            try:
                if response.complete:
                    written = self.store.put_object(response.body)
                    raw_object_sha256 = written.raw_object_sha256
                    deduplicated = written.deduplicated
                    if not deduplicated:
                        self.store.record_raw_object(SecRawObjectRecord(
                            raw_object_sha256=raw_object_sha256,
                            byte_length=written.byte_length,
                            first_received_at_utc=received_at,
                            endpoint_class=endpoint_class,
                            media_type=response.media_type,
                            content_encoding=response.content_encoding,
                            declared_content_length=response.declared_content_length,
                            collector_version=self.store.collector_version))
                else:
                    incomplete_id = self.store.put_object(
                        response.body, incomplete=True).raw_object_sha256
            except SecStorageFailure as exc:
                return finish(STORAGE_FAILED, error_class=str(exc), **common)

        evidence = {}
        if raw_object_sha256 is not None:
            evidence["raw_object_sha256"] = raw_object_sha256
        if incomplete_id is not None:
            evidence["incomplete_object_sha256"] = incomplete_id

        if response.status == 429:
            seconds = self._authoritative_cooldown(response, self.policy.rate_limit_cooldown_seconds)
            with self._internal_budget_mutation():
                self.budget.enter_cooldown(seconds, "http_429_rate_limited")
            self.record_transition(COOLDOWN, COOLDOWN_OBSERVED,
                                   next_due_at=self.budget.load().cooldown_until_utc,
                                   detail="http_429_rate_limited")
            return finish(RATE_LIMITED, error_class="http_429", retry_after_seconds=seconds,
                          byte_length=response.byte_length, **evidence, **common)
        if response.status == 403:
            # Consistent with automated-access control: long cooldown, no loop.
            seconds = self._authoritative_cooldown(response, self.policy.forbidden_cooldown_seconds)
            with self._internal_budget_mutation():
                self.budget.enter_cooldown(seconds, "http_403_access_controlled")
            self.state.blocked_reason = "SEC returned 403; extended cooldown in force"
            self.record_transition(COOLDOWN, COOLDOWN_OBSERVED,
                                   next_due_at=self.budget.load().cooldown_until_utc,
                                   detail="http_403_access_controlled")
            return finish(ACCESS_FORBIDDEN, error_class="http_403", retry_after_seconds=seconds,
                          byte_length=response.byte_length, **evidence, **common)
        if 500 <= response.status < 600:
            retry_after = seconds_from_retry_after(
                response.retry_after, self.timebase.now()) or 0.0
            self._enter_transient_cooldown(
                f"http_{response.status}", floor_seconds=retry_after)
            return finish(SERVER_ERROR, error_class=f"http_{response.status}",
                          retry_after_seconds=retry_after or None,
                          byte_length=response.byte_length, **evidence, **common)
        if response.status != 200:
            # Filing drain and daily reconciliation can otherwise select the
            # same permanent 4xx again on the very next Control Plane tick.
            retry_after = seconds_from_retry_after(
                response.retry_after, self.timebase.now()) or 0.0
            self._enter_transient_cooldown(
                f"http_{response.status}_client_error",
                floor_seconds=retry_after)
            return finish(PERMANENT_CLIENT_ERROR,
                          error_class=f"http_{response.status}",
                          retry_after_seconds=retry_after or None,
                          byte_length=response.byte_length, **evidence, **common)
        if not response.complete:
            self._enter_transient_cooldown(f"incomplete:{response.transfer_outcome}")
            return finish(INCOMPLETE_TRANSFER, error_class=f"transfer_{response.transfer_outcome}",
                          incomplete_object_sha256=incomplete_id,
                          byte_length=response.byte_length, **common)

        # A complete 200 is already durable above.
        with self._internal_budget_mutation():
            self.budget.reset_backoff()
        result = finish(DEDUPLICATED if deduplicated else CAPTURED_OK,
                        raw_object_sha256=raw_object_sha256,
                        byte_length=response.byte_length, **common)
        result.response = response
        result.raw_object_sha256 = raw_object_sha256
        result.byte_length = response.byte_length
        result.deduplicated = deduplicated
        result.response_received_at_utc = received_at
        return result

    def _decoded(self, attempt: _AttemptResult) -> bytes:
        """Bytes to parse: read back from the store, verified, then decoded.

        Reading through the store re-checks the content address, so a page is
        parsed only from bytes that are provably the ones preserved. Decoding is
        applied to a copy, using the transport encoding actually received, so the
        stored object and its hash keep describing the wire bytes.
        """
        stored = self.store.read_object(attempt.raw_object_sha256)
        encoding = attempt.response.content_encoding if attempt.response else None
        return decode_body(stored, encoding)

    def _elapsed(self, since: datetime) -> float:
        return round((self.timebase.now() - since).total_seconds(), 3)

    def _authoritative_cooldown(self, response: SecHttpResponse, floor: float) -> float:
        """Never retry sooner than the source asked, and never sooner than policy."""
        supplied = seconds_from_retry_after(response.retry_after, self.timebase.now())
        return max(floor, supplied or 0.0)

    def _enter_transient_cooldown(self, reason: str,
                                  floor_seconds: float = 0.0) -> None:
        with self._internal_budget_mutation():
            seconds = max(self.budget.next_backoff_seconds(), floor_seconds)
            self.budget.enter_cooldown(seconds, reason)
        self.record_transition(BACKOFF, BACKOFF_ENTERED,
                               next_due_at=self.budget.load().cooldown_until_utc,
                               detail=reason)

    # --- coverage bookkeeping ---------------------------------------------
    def _open_gap(self, kind: str, detail: dict[str, Any]) -> str:
        gap_id = uuid.uuid4().hex[:16]
        record = {"gap_id": gap_id, "kind": kind, "opened_at_utc": self.timebase.now_iso(),
                  **detail}
        self.state.open_gaps.append(record)
        append_jsonl(self.paths.sec_coverage, {"event": "gap_opened", **record})
        self._set_coverage(COVERAGE_UNKNOWN, f"{kind} ({gap_id})")
        self._emit("sec_coverage_unknown", severity="WARN", gap_id=gap_id, gap_kind=kind,
                   **{key: value for key, value in detail.items() if key != "identities"})
        return gap_id

    def _resolve_gaps(self, kind: str, reason: str) -> list[str]:
        """Resolve only what has been proved, and keep the record append-only."""
        remaining, resolved = [], []
        for gap in self.state.open_gaps:
            if gap["kind"] != kind:
                remaining.append(gap)
                continue
            closed = dict(gap, resolved_at_utc=self.timebase.now_iso(), resolution=reason)
            self.state.resolved_gaps.append(closed)
            append_jsonl(self.paths.sec_coverage, {"event": "gap_resolved", **closed})
            resolved.append(gap["gap_id"])
        self.state.open_gaps = remaining
        return resolved

    def _set_coverage(self, coverage_state: str, detail: str | None) -> None:
        self.state.coverage_state = coverage_state
        self.state.coverage_detail = detail

    def _recompute_coverage(self, continuity: bool, detail: str) -> str:
        """Coverage is COMPLETE only with continuity *and* no open gap."""
        if not continuity:
            return self.state.coverage_state
        if self.state.open_gaps:
            kinds = sorted({gap["kind"] for gap in self.state.open_gaps})
            self._set_coverage(COVERAGE_UNKNOWN, f"open gaps: {', '.join(kinds)}")
        else:
            self._set_coverage(COMPLETE, detail)
        return self.state.coverage_state

    # --- discovery poll ----------------------------------------------------
    def poll(self) -> PollOutcome:
        """One discovery poll: validate, walk only what is needed, stay honest."""
        self._guard_public_mutation("poll")
        self._ensure_reconciliation_obligation()
        if not self.configured:
            return PollOutcome(poll_id="", result_state=COOLDOWN_SUPPRESSED,
                               valid_discovery=False,
                               coverage_state=self.state.coverage_state,
                               heartbeat_durable=False,
                               error_class="sec_access_not_configured")
        interrupted = self._close_interrupted_poll()
        poll_id = uuid.uuid4().hex[:16]
        started_at = self.timebase.now_iso()
        self.state.polls += 1
        self.state.last_poll_started_at_utc = started_at
        self.state.active_poll = {"poll_id": poll_id, "started_at_utc": started_at,
                                 "pages": [], "continuity": False, "closed": False,
                                 "task_ids": [], "newest_identity_digest": None,
                                 "newest_feed_updated": None}
        self.save()

        pages_walked = 0
        first_object: str | None = None
        gap_ids = list(interrupted)
        new_identities: list[tuple[DiscoveryEntry, str, int]] = []
        enqueued = 0
        continuity = False
        start = 0
        page_size = self.policy.discovery_page_size

        while pages_walked < self.policy.max_discovery_pages_per_poll:
            attempt = self._request("DISCOVERY", discovery_path(start, page_size),
                                    discovery_url(start, page_size), poll_id=poll_id,
                                    page_start=start)
            if not attempt.ok:
                gap_ids.append(self._open_gap(PAGE_FETCH_FAILED, {
                    "poll_id": poll_id, "page_start": start,
                    "page_range_end": start + page_size,
                    "result_state": attempt.result_state,
                    "error_class": attempt.error_class}))
                return self._close_poll(
                    poll_id, attempt.result_state, False,
                    pages_walked, first_object, gap_ids,
                    attempt.error_class, new_identities, enqueued=enqueued)
            first_object = first_object or attempt.raw_object_sha256
            try:
                page = parse_discovery_page(self._decoded(attempt),
                                            requested_start=start, requested_count=page_size)
            except (DiscoveryInvalid, SecTransportError) as invalid:
                invalid = (invalid if isinstance(invalid, DiscoveryInvalid)
                           else DiscoveryInvalid(invalid.error_class))
                # Nominal HTTP success, unusable semantics. Never NO_NEW_DATA.
                gap_ids.append(self._open_gap(PAGE_FETCH_FAILED, {
                    "poll_id": poll_id, "page_start": start,
                    "page_range_end": start + page_size,
                    "result_state": DISCOVERY_INVALID, "error_class": invalid.reason}))
                self._emit("sec_discovery_invalid", severity="WARN", poll_id=poll_id,
                           page_start=start, error_class=invalid.reason)
                return self._close_poll(
                    poll_id, DISCOVERY_INVALID, False, pages_walked + 1,
                    first_object, gap_ids, invalid.reason, new_identities,
                    enqueued=enqueued)
            pages_walked += 1
            self.state.active_poll["pages"].append({
                "page_start": start, "raw_object_sha256": attempt.raw_object_sha256,
                "page_full": page.page_full, **page.pagination_metadata()})
            if self.state.active_poll["newest_feed_updated"] is None:
                self.state.active_poll["newest_feed_updated"] = page.feed_updated
            self.save()

            continuity, fresh = self._scan_page(
                page, poll_id, attempt.raw_object_sha256, start)
            new_identities.extend(fresh)
            # A successful page is durable acquisition evidence. Persist every
            # newly observed filing before issuing the next page request.
            enqueued += self._enqueue(fresh, poll_id)
            if continuity:
                break
            if self.state.cursor_identity_digest is None:
                # Bootstrap. There is no anchor to walk back to, and the feed is
                # a rolling window with no beginning, so paging deeper would be a
                # crawl that buys no continuity. Page one defines the scope; the
                # daily index is what addresses anything older.
                continuity = True
                self._record_bootstrap_scope(poll_id, page)
                break
            if not page.page_full:
                # The feed ended before the anchor was reached.
                if self.state.cursor_identity_digest is None:
                    # First ever poll: the window itself is the bootstrap scope.
                    continuity = True
                else:
                    gap_ids.append(self._open_gap(CURSOR_FELL_OUT_OF_WINDOW, {
                        "poll_id": poll_id, "page_start": 0,
                        "page_range_end": start + page.entry_count,
                        "from_cursor_identity_digest": self.state.cursor_identity_digest,
                        "from_cursor_feed_updated_at_utc":
                            self.state.cursor_feed_updated_at_utc}))
                break
            start = page.next_start
        else:
            gap_ids.append(self._open_gap(PAGE_BUDGET_EXHAUSTED, {
                "poll_id": poll_id, "page_start": 0, "page_range_end": start,
                "pages_walked": pages_walked,
                "from_cursor_identity_digest": self.state.cursor_identity_digest}))

        if continuity:
            # A completed walk back to the anchor also proves the range an
            # interrupted poll had been trying to cover.
            self._resolve_gaps(PAGINATION_INTERRUPTED, "continuity re-established")
        self._recompute_coverage(
            continuity,
            "continuity established from the last validated poll"
            + (f"; captured scope begins {self.state.bootstrap_scope_from_utc}"
               if self.state.bootstrap_scope_from_utc else ""))
        self.state.validated_polls += 1
        self.state.last_validated_discovery_at_utc = self.timebase.now_iso()
        result_state = self._summarize(True, self.state.coverage_state, len(new_identities))
        return self._close_poll(poll_id, result_state, True, pages_walked, first_object,
                                gap_ids, None, new_identities, enqueued=enqueued,
                                continuity=continuity)

    def _record_bootstrap_scope(self, poll_id: str, page: DiscoveryPage) -> None:
        """State plainly where captured history begins, rather than implying it."""
        if self.state.bootstrap_scope_from_utc is not None:
            return
        self.state.bootstrap_scope_from_utc = page.feed_updated or self.timebase.now_iso()
        self.state.bootstrap_scope_note = (
            "captured history begins at the first discovery page; filings older than "
            "the bootstrap point were never in scope and are the reconciliation/"
            "backfill engine's work, not a claim of coverage")
        append_jsonl(self.paths.sec_coverage, {
            "event": "bootstrap_scope_established", "poll_id": poll_id,
            "observed_at_utc": self.timebase.now_iso(),
            "scope_from_feed_updated": self.state.bootstrap_scope_from_utc,
            "page_start": page.requested_start, "page_size": page.requested_count})
        self.save()

    def _scan_page(self, page: DiscoveryPage, poll_id: str, object_sha256: str,
                   start: int) -> tuple[bool, list[tuple[DiscoveryEntry, str, int]]]:
        """Walk entries newest-first, stopping at the continuity anchor.

        This is the dedup short-circuit: in steady state the anchor is on page
        one, so the poll costs exactly one request and an already-captured
        identity costs none.
        """
        anchor = self.state.cursor_identity_digest
        committed = self.committed_identities()
        # EDGAR's Latest Filings feed lists one accession once per filer, so the
        # same Form 4 legitimately appears as several entries. Identity, not entry
        # position, is what deduplicates - including within a single page.
        seen = {task["identity_digest"] for task in self.state.pending_tasks}
        fresh: list[tuple[DiscoveryEntry, str, int]] = []
        for entry in page.entries:
            identity_digest = digest_text(entry.accession)
            if anchor is not None and identity_digest == anchor:
                return True, fresh
            if self.state.active_poll["newest_identity_digest"] is None:
                self.state.active_poll["newest_identity_digest"] = identity_digest
                self.state.active_poll["newest_feed_updated"] = page.feed_updated
            if not entry.is_form_4:
                continue
            if entry.accession in committed or identity_digest in seen:
                continue  # already acknowledged, or already queued by this walk
            seen.add(identity_digest)
            fresh.append((entry, object_sha256, start))
        return False, fresh

    def _enqueue(self, discovered: list[tuple[DiscoveryEntry, str, int]],
                 poll_id: str) -> int:
        """Bind each filing task to the discovery page that produced it.

        The locator is written to the restricted journal *before* the task is
        queued, so a crash here loses a task that the unadvanced cursor will
        rediscover, never a task that cannot be resolved.
        """
        enqueued = 0
        for entry, object_sha256, page_start in discovered:
            identity_digest = digest_text(entry.accession)
            locator_digest = self.store.record_locator(
                locator=entry.raw_document_url, source_identity=entry.accession,
                endpoint_class=FILING_ENDPOINT_CLASS,
                observed_at_utc=self.timebase.now_iso(), poll_id=poll_id,
                source_published_at_utc=entry.source_published_at_utc)
            self.state.pending_tasks.append({
                "task_id": identity_digest[7:23], "identity_digest": identity_digest,
                "locator_digest": locator_digest, "discovery_object_sha256": object_sha256,
                "page_start": page_start, "poll_id": poll_id, "attempts": 0,
                "queued_at_utc": self.timebase.now_iso(), "last_error_class": None})
            self.state.active_poll["task_ids"].append(identity_digest[7:23])
            enqueued += 1
        if enqueued:
            # Persist the queue, but do not mint a second immediate scheduler
            # obligation here. _close_poll() declares exactly one next action
            # after the poll is committed.  Two "due now" obligations cannot be
            # prospectively superseded and would manufacture an audit hole.
            self.save()
        return enqueued

    def _summarize(self, valid_discovery: bool, coverage_state: str,
                   new_identities: int) -> str:
        if not valid_discovery:
            return DISCOVERY_INVALID
        if coverage_state != COMPLETE:
            return COVERAGE_UNKNOWN
        if new_identities:
            return NEW_ITEMS
        assert_no_new_data_earned(valid_discovery, coverage_state, new_identities)
        return NO_NEW_DATA

    def _close_poll(self, poll_id: str, result_state: str, valid_discovery: bool,
                    pages_walked: int, first_object: str | None, gap_ids: list[str],
                    error_class: str | None,
                    new_identities: list[Any], *, enqueued: int = 0,
                    continuity: bool = False) -> PollOutcome:
        active = self.state.active_poll or {}
        active.update({"closed": True, "continuity": continuity,
                      "closed_at_utc": self.timebase.now_iso(),
                      "result_state": result_state})
        self.state.last_poll_completed_at_utc = active["closed_at_utc"]
        self.state.last_result_state = result_state
        # The cursor advances only once continuity is proved and every task this
        # poll discovered is acknowledged. Until then the anchor stays put, which
        # is what makes a crash rediscover rather than skip.
        if continuity and active.get("newest_identity_digest"):
            self.state.pending_cursor_identity_digest = active["newest_identity_digest"]
            self.state.pending_cursor_feed_updated_at_utc = active.get("newest_feed_updated")
        self.state.active_poll = None
        self._maybe_advance_cursor()
        self.save()
        self.record_current_state(
            POLL_COMPLETED if valid_discovery else POLL_FAILED,
            detail=f"{result_state}/{self.state.coverage_state}")
        self._emit("sec_discovery_poll", poll_id=poll_id, result_state=result_state,
                   valid_discovery=valid_discovery, coverage_state=self.state.coverage_state,
                   pages_walked=pages_walked, error_class=error_class,
                   discovery_object_sha256=first_object)
        return PollOutcome(poll_id=poll_id, result_state=result_state,
                           valid_discovery=valid_discovery,
                           coverage_state=self.state.coverage_state,
                           heartbeat_durable=True, pages_walked=pages_walked,
                           discovery_object_sha256=first_object, error_class=error_class,
                           gap_ids=gap_ids, new_identities=len(new_identities),
                           enqueued=enqueued)

    def _close_interrupted_poll(self) -> list[str]:
        """A poll cut short by a restart cannot claim the range it never walked.

        Offsets into a live feed are not stable across a restart, so the partial
        walk is not resumed in place: the range is recorded as unknown and the
        next poll re-establishes continuity from the unadvanced anchor, which
        resolves the gap when it succeeds.
        """
        active = self.state.active_poll
        if not active or active.get("closed"):
            self.state.active_poll = None
            return []
        pages = active.get("pages") or []
        walked_to = pages[-1].get("next_start") if pages else 0
        gap_id = self._open_gap(PAGINATION_INTERRUPTED, {
            "poll_id": active.get("poll_id"), "page_start": walked_to or 0,
            "page_range_end": None, "pages_walked": len(pages)})
        self.state.active_poll = None
        self.save()
        return [gap_id]

    # --- filing acquisition ------------------------------------------------
    def drain(self, max_items: int | None = None) -> list[dict[str, Any]]:
        """Acquire queued filings under the same limiter. Backlog never rushes."""
        self._guard_public_mutation("drain")
        if not self.configured:
            return []
        limit = self.policy.filings_per_drain if max_items is None else max_items
        outcomes: list[dict[str, Any]] = []
        for task in list(self.state.pending_tasks)[:limit]:
            if self.cooldown_remaining() > 0:
                break
            outcomes.append(self._acquire(task))
        if outcomes:
            self.record_current_state(DRAIN_COMPLETED,
                                      detail=outcomes[-1].get("result_state"))
        return outcomes

    def _acquire(self, task: dict[str, Any]) -> dict[str, Any]:
        resolved = self.store.resolve_locator(task["locator_digest"])
        if resolved is None:
            # The restricted journal is written before the task, so this cannot
            # happen from a crash; if it does, the task is unresolvable evidence.
            self._drop_task(task)
            gap = self._open_gap(FILING_ACQUISITION_FAILED, {
                "task_id": task["task_id"], "error_class": "locator_unresolvable"})
            return {"task_id": task["task_id"], "result_state": STORAGE_FAILED, "gap_id": gap}
        identity = resolved["source_identity"]
        committed = self.committed_identities()
        if identity in committed:
            # Already acknowledged: zero network requests, exactly as intended.
            # This is also the path a replay takes after a crash, so it must
            # advance the cursor like any other acknowledgement - otherwise the
            # anchor could stay stuck behind work that is provably complete.
            self._drop_task(task)
            self.state.deduplications += 1
            self._maybe_advance_cursor()
            self.save()
            return {"task_id": task["task_id"], "result_state": DEDUPLICATED,
                    "raw_object_sha256": committed[identity], "requests_spent": 0}

        locator = resolved["source_locator"]
        path = locator.replace("https://www.sec.gov", "", 1)
        attempt = self._request("FILING", path, locator,
                                poll_id=task.get("poll_id"), source_identity=identity,
                                source_published_at_utc=resolved.get("source_published_at_utc"))
        if not attempt.ok:
            task["attempts"] = int(task.get("attempts", 0)) + 1
            task["last_error_class"] = attempt.error_class or attempt.result_state
            gap_id = None
            if task["attempts"] >= MAX_FILING_ATTEMPTS:
                # Quarantine instead of hot-looping forever.  The open gap keeps
                # coverage non-COMPLETE and prevents cursor advancement.
                gap_id = self._open_gap(FILING_ACQUISITION_FAILED, {
                    "task_id": task["task_id"], "attempts": task["attempts"],
                    "error_class": task["last_error_class"]})
                append_jsonl(self.paths.sec_restricted / "failed_tasks.jsonl", dict(task))
                self._drop_task(task)
            self.save()
            return {"task_id": task["task_id"], "result_state": attempt.result_state,
                    "error_class": attempt.error_class, "gap_id": gap_id}

        # A transport-level 200 is not proof the filing locator returned a
        # Form-4 submission.  A WAF/error HTML page under 200 must never be
        # acknowledged as the filing and advance the cursor.
        try:
            filing_body = self._decoded(attempt)
        except SecTransportError as invalid:
            filing_body = b""
        form4_header = re.search(
            rb"CONFORMED SUBMISSION TYPE:\s*4(?:/A)?(?:\s|$)", filing_body,
            re.IGNORECASE)
        form4_document = re.search(
            rb"<TYPE>\s*4(?:/A)?(?:\s|<)", filing_body, re.IGNORECASE)
        if (b"<SEC-DOCUMENT>" not in filing_body.upper()
                or b"</SEC-DOCUMENT>" not in filing_body.upper()
                or not (form4_header or form4_document)):
            task["attempts"] = int(task.get("attempts", 0)) + 1
            task["last_error_class"] = "FILING_PACKAGE_INVALID"
            gap_id = self._open_gap(FILING_ACQUISITION_FAILED, {
                "task_id": task["task_id"],
                "error_class": "FILING_PACKAGE_INVALID"})
            self._enter_transient_cooldown("FILING_PACKAGE_INVALID")
            self.save()
            return {"task_id": task["task_id"],
                    "result_state": DISCOVERY_INVALID,
                    "error_class": "FILING_PACKAGE_INVALID",
                    "gap_id": gap_id}

        # Raw bytes are durable at this point. The envelope is the acknowledgement.
        version = self.store.record_source_version(
            source_identity=identity, raw_object_sha256=attempt.raw_object_sha256,
            observed_at_utc=attempt.response_received_at_utc or self.timebase.now_iso(),
            attempt_id=attempt.attempt_id)
        if version.conflict:
            self.state.conflicts += 1
            self._emit("sec_source_version_conflict", severity="WARN",
                       raw_object_sha256=attempt.raw_object_sha256,
                       prior_raw_object_sha256=version.prior_sha256, version=version.version)
        self.store.record_envelope(SecAcquisitionEnvelope(
            envelope_id=uuid.uuid4().hex[:16], attempt_id=attempt.attempt_id,
            source_identity=identity, source_locator=locator,
            endpoint_class=FILING_ENDPOINT_CLASS,
            request_attempted_at_utc=attempt.request_attempted_at_utc,
            response_received_at_utc=attempt.response_received_at_utc or "",
            http_status=200, raw_object_sha256=attempt.raw_object_sha256,
            byte_length=attempt.byte_length or 0,
            collector_version=self.store.collector_version, git_commit=self.store.git_commit,
            content_encoding=attempt.response.content_encoding if attempt.response else None,
            declared_content_length=(attempt.response.declared_content_length
                                     if attempt.response else None),
            media_type=attempt.response.media_type if attempt.response else None,
            source_published_at_utc=resolved.get("source_published_at_utc"),
            discovery_object_sha256=task.get("discovery_object_sha256"),
            poll_id=task.get("poll_id"), deduplicated=attempt.deduplicated))
        self.committed_identities()[identity] = attempt.raw_object_sha256
        # Envelope durable, so the task may now be acknowledged.
        self._drop_task(task)
        self.state.captures += 1
        self.state.last_capture_at_utc = attempt.response_received_at_utc
        self._maybe_advance_cursor()
        self.save()
        self._emit("sec_raw_capture", raw_object_sha256=attempt.raw_object_sha256,
                   byte_length=attempt.byte_length,
                   received_at_utc=attempt.response_received_at_utc)
        return {"task_id": task["task_id"], "result_state": CAPTURED_OK,
                "raw_object_sha256": attempt.raw_object_sha256,
                "byte_length": attempt.byte_length, "conflict": version.conflict}

    def _drop_task(self, task: dict[str, Any]) -> None:
        """Acknowledge exactly one full filing identity.

        task_id is intentionally short for operator diagnostics and can collide.
        identity_digest is the durable authority for queue membership.
        """
        identity = task.get("identity_digest")
        self.state.pending_tasks = [
            item for item in self.state.pending_tasks
            if item.get("identity_digest") != identity
        ]

    def _maybe_advance_cursor(self) -> None:
        """Acknowledgement precedes cursor advance, never the other way round."""
        newest = self.state.pending_cursor_identity_digest
        if newest is None or self.state.pending_tasks:
            return
        if self.state.coverage_state != COMPLETE:
            return
        self.state.cursor_identity_digest = newest
        self.state.cursor_feed_updated_at_utc = self.state.pending_cursor_feed_updated_at_utc
        self.state.cursor_advanced_at_utc = self.timebase.now_iso()
        self.state.pending_cursor_identity_digest = None
        self.state.pending_cursor_feed_updated_at_utc = None

    # --- reconciliation (detection only; backfill is later work) -----------
    def reconcile_due(self, day: date) -> dict[str, Any]:
        """Compatibility entry point; the raw primitive enforces the same gate."""
        return self.reconcile(day)

    def reconcile(self, day: date) -> dict[str, Any]:
        """Compare one due closed day against captured evidence.

        Scheduling authority is enforced at this lowest public mutation
        boundary, so a wrapper cannot make an early direct call safe.
        """
        if not self.configured:
            return {"day": day.isoformat(), "result_state": COOLDOWN_SUPPRESSED,
                    "reconciled": False}
        due_day = self.reconciliation_due()
        if due_day != day:
            return {"day": day.isoformat(), "result_state": "RECONCILIATION_NOT_DUE",
                    "reconciled": False}
        self._guard_public_mutation("reconcile")
        obligation_id = self._ensure_reconciliation_obligation()
        attempt = self._request(
            "RECONCILE", daily_index_path(day), daily_index_url(day),
            obligation_id=obligation_id)
        key = day.isoformat()
        if not attempt.ok:
            gap = self._open_gap(DAILY_INDEX_UNAVAILABLE, {
                "day": key, "result_state": attempt.result_state,
                "error_class": attempt.error_class})
            if key not in self.state.unreconciled_days:
                self.state.unreconciled_days.append(key)
            self.save()
            return {"day": key, "result_state": attempt.result_state, "reconciled": False,
                    "gap_id": gap}
        try:
            index = parse_daily_index(self._decoded(attempt), day)
        except (DiscoveryInvalid, SecTransportError) as invalid:
            invalid = (invalid if isinstance(invalid, DiscoveryInvalid)
                       else DiscoveryInvalid(invalid.error_class))
            gap = self._open_gap(DAILY_INDEX_UNAVAILABLE, {
                "day": key, "result_state": DISCOVERY_INVALID,
                "error_class": invalid.reason})
            if key not in self.state.unreconciled_days:
                self.state.unreconciled_days.append(key)
            self.save()
            return {"day": key, "result_state": DISCOVERY_INVALID, "reconciled": False,
                    "gap_id": gap, "error_class": invalid.reason}

        committed = self.committed_identities()
        queued = {task["identity_digest"] for task in self.state.pending_tasks}
        missing = [accession for accession in index.accessions
                   if accession not in committed and digest_text(accession) not in queued]
        gap_id = None
        if missing:
            # Identities stay in the restricted tier; the gap record carries the
            # interval only, because a filing count is not firewall-safe.
            append_jsonl(self.paths.sec_restricted / "reconciliation.jsonl",
                         {"day": key, "observed_at_utc": self.timebase.now_iso(),
                          "expected_not_captured": missing,
                          "daily_index_object_sha256": attempt.raw_object_sha256})
            gap_id = self._open_gap(DAILY_INDEX_GAP, {
                "day": key, "interval_start": key, "interval_end": key,
                "daily_index_object_sha256": attempt.raw_object_sha256})
        else:
            if key not in self.state.reconciled_days:
                self.state.reconciled_days.append(key)
            self.state.unreconciled_days = [value for value in self.state.unreconciled_days
                                            if value != key]
            self._recompute_coverage(self.state.coverage_state == COMPLETE,
                                     f"daily index confirmed coverage through {key}")
        self.save()
        self.record_current_state(RECONCILE_COMPLETED,
                                  detail=f"{key}:{'confirmed' if not missing else 'gap'}")
        return {"day": key, "result_state": CAPTURED_OK, "reconciled": not missing,
                "gap_id": gap_id, "daily_index_object_sha256": attempt.raw_object_sha256}

    # --- telemetry ---------------------------------------------------------
    def _emit(self, kind: str, severity: str = "INFO", **detail: Any) -> None:
        # Detailed acquisition evidence already lives under var/sec. Mirroring
        # one row per poll/capture into the shared EventLog leaks volume, timing,
        # object hashes and discovery outcomes to protocol-mutating actors.
        return

    def component_state(self) -> tuple[str, str]:
        """Protocol-facing service health, deliberately independent of filing volume."""
        if not self.configured:
            return "BLOCKED", "SEC identity/contact not configured"
        if not self.state.enabled:
            return "IDLE", self.state.blocked_reason or "capture lane disabled"
        if self.cooldown_remaining() > 0:
            return "BLOCKED", "SEC cooldown active"
        if self.liveness() == STALE:
            return "FAULT", "acquisition heartbeat stale"
        return "RUN", "acquisition service active"

    def telemetry(self) -> dict[str, Any]:
        """Strict public projection: health and integrity, never activity volume."""
        state, detail = self.component_state()
        storage = self.store.storage_health()
        materialized, materialized_error = self._validated_materialization()
        return {
            "collector_version": self.store.collector_version,
            "git_commit": self.store.git_commit,
            "configured": self.configured,
            "enabled": self.state.enabled,
            "state": state,
            "detail": detail,
            "liveness": self.liveness(),
            "coverage_state": self.state.coverage_state,
            "open_gap_kinds": sorted({gap["kind"] for gap in self.state.open_gaps}),
            "storage": firewall_safe_storage(storage),
            "rate_limit": self.budget.telemetry() if self.budget else None,
            "policy": self.policy.to_dict() if self.policy else None,
            "acquisition_critical_fingerprint": self.fingerprint,
            "materialized_fingerprint": materialized,
            "materialization_error": materialized_error,
            "fingerprint_matches_materialized": (
                materialized_error is None and materialized == self.fingerprint),
            "lifecycle_cause": self.lifecycle.get("lifecycle_cause"),
            "lifecycle_externally_attested": self.lifecycle.get("externally_attested"),
            "launch_service_managed": self.lifecycle.get("service_managed"),
            "qualifying_service_mode": self.lifecycle.get("qualifying_service_mode"),
            "capture_state": storage["capture_state"],
            "visibility_state": storage["visibility_state"],
            "admissibility_state": storage["admissibility_state"],
        }

    def _outage_seconds(self) -> float | None:
        last = self.state.last_validated_discovery_at_utc
        if last is None:
            return None
        return round((self.timebase.now() - parse_ts(last)).total_seconds(), 1)
