"""Retrospective observation-window audit.

``BLUE_P0_RAW_CAPTURE_CHECKPOINT_ADDENDUM_2026-09-18.md §5.2`` closure condition
2: "every expected acquisition action is derivable from scheduler-state
transitions and is accounted for by an attempt, an authorized backoff/cooldown
transition, or an explicit failure state", and the rule right after it - the
audit "must never infer that an attempt was not due merely because no attempt was
recorded."

The first version of this module reconciled times against times, and Blue found
three ways that let a missed deadline still report ``accountable=true``:

1. the attempt window was ``abs(attempt - due) <= tolerance``, whose second half
   subsumes the forward-only condition, so a request made *before* a deadline
   could be offered as proof that the deadline was later met;
2. attempts were matched with ``any(...)`` and never consumed, so one request
   could silently answer several distinct obligations;
3. an obligation counted as "superseded" by *any* later transition, including one
   recorded after the deadline had already been missed.

All three had the same root cause: obligations had no identity, so nothing could
be reconciled one-to-one. This version gives them one.

An **obligation** is a named commitment created by a transition that declared a
``next_due_at_utc``. Exactly one resolution may retire it:

* **SUPERSEDED** - a transition that explicitly names this obligation in
  ``supersedes_obligation_id``, was recorded strictly *before* its due time, and
  carries an authorized cause. Supersession is prospective by construction: a
  transition recorded after the deadline cannot erase the hole.
* **ATTEMPT** - a durable attempt whose request time falls in ``[due, due +
  tolerance]``. Forward only, and consumed: an attempt retires at most one
  obligation.
* **PENDING** - the due time (plus grace) has not passed yet at audit time. Not
  an answer, and not a hole either; reported separately so the last obligation of
  a live service is not mistaken for a miss.

Anything else is an unexplained hole and the window is not accountable.

Supersessions are resolved before attempts. A supersession is the stronger claim
- explicit, named, and necessarily recorded before the deadline - so letting it
retire its obligation first keeps the scarce attempts available for the
obligations that actually needed a request. The reverse order would produce
spurious failures, and either order is safe against a false pass.

This module reports. It never closes ``P0_CONTINUOUS_SERVICE_STATE`` and never
records ``t0``: both belong to Blue.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import math
from typing import Any

from ...state import parse_ts, read_jsonl
from .scheduler import AUTHORIZED_SUPERSESSION_CAUSES
from .supervisor import INVALIDATING_CAUSES, LIFECYCLE_CAUSES, UNATTESTED


#: Grace after a due time within which an attempt still answers the obligation.
#: One poll interval: a tick that lands a little late is service, not a hole.
DUE_TOLERANCE_MULTIPLIER = 3.0

#: Resolution kinds.
RESOLVED_BY_ATTEMPT = "ATTEMPT"
RESOLVED_BY_SUPERSESSION = "SUPERSEDED"
PENDING = "PENDING"
UNEXPLAINED = "UNEXPLAINED"

#: Attempt result states that do not count as answering an obligation. An
#: attempt suppressed by cooldown *is* an answer: the lane tried at the due time
#: and the frozen policy stopped it, which is an accounted-for action.
NON_ANSWERING_ATTEMPT_STATES: frozenset[str] = frozenset()


@dataclass
class Obligation:
    """One named commitment and its single resolution, if it has one."""

    obligation_id: str
    created_at_utc: str
    due_at_utc: str
    state: str
    cause: str
    acquisition_critical_fingerprint: str
    transition_id: str
    supersedes_obligation_id: str | None = None
    status: str = UNEXPLAINED
    resolution_kind: str | None = None
    #: attempt_id, or the transition_id of the superseding transition.
    resolution_ref: str | None = None
    resolution_at_utc: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _obligations_from(transitions: list[dict[str, Any]]) -> tuple[list[Obligation], list[str]]:
    """Read the obligation ledger out of the scheduler journal.

    A transition that declared a due time without an ``obligation_id`` cannot be
    reconciled by name. Rather than fall back to matching by time - which is the
    defect this module was rebuilt to remove - those are reported so the window
    fails loudly instead of being audited under weaker rules.
    """
    obligations: list[Obligation] = []
    unidentified: list[str] = []
    for record in transitions:
        due = record.get("next_due_at_utc")
        if not due:
            continue
        obligation_id = record.get("obligation_id")
        if not obligation_id:
            unidentified.append(record.get("transition_id") or "unknown")
            continue
        obligations.append(Obligation(
            obligation_id=obligation_id,
            created_at_utc=record.get("recorded_at_utc") or "",
            due_at_utc=due,
            state=record.get("state") or "",
            cause=record.get("cause") or "",
            acquisition_critical_fingerprint=record.get(
                "acquisition_critical_fingerprint") or "UNAVAILABLE",
            transition_id=record.get("transition_id") or "",
            supersedes_obligation_id=record.get("supersedes_obligation_id")))
    return obligations, unidentified


def _resolve_supersessions(obligations: list[Obligation],
                           transitions: list[dict[str, Any]]) -> None:
    """Retire obligations explicitly replaced before they came due.

    Three conditions, all required: the transition names this obligation, it was
    recorded strictly before the due time, and its cause is authorized. A
    superseding transition is consumed, so one re-plan cannot retire two
    obligations.
    """
    consumed: set[str] = set()
    by_target: dict[str, list[dict[str, Any]]] = {}
    for record in transitions:
        target = record.get("supersedes_obligation_id")
        if target:
            by_target.setdefault(target, []).append(record)
    for obligation in obligations:
        candidates = by_target.get(obligation.obligation_id, [])
        due = parse_ts(obligation.due_at_utc)
        for record in sorted(candidates, key=lambda item: item.get("recorded_at_utc") or ""):
            transition_id = record.get("transition_id") or ""
            if transition_id in consumed:
                continue
            recorded_raw = record.get("recorded_at_utc")
            if not recorded_raw:
                continue
            if parse_ts(recorded_raw) >= due:
                # Recorded at or after the deadline: this is a post-hoc note, and
                # a post-hoc note never erases a missed deadline.
                continue
            if (record.get("cause") or "") not in AUTHORIZED_SUPERSESSION_CAUSES:
                continue
            obligation.status = RESOLVED_BY_SUPERSESSION
            obligation.resolution_kind = RESOLVED_BY_SUPERSESSION
            obligation.resolution_ref = transition_id
            obligation.resolution_at_utc = recorded_raw
            consumed.add(transition_id)
            break


def _resolve_attempts(obligations: list[Obligation], attempts: list[dict[str, Any]],
                      tolerance: float) -> None:
    """Resolve by explicit obligation identity, then check the due window.

    Time proximity alone is not authority: two obligations may overlap.  A
    request answers only the obligation captured durably at request creation.
    """
    by_id = {item.obligation_id: item for item in obligations}
    for record in attempts:
        obligation_id = record.get("obligation_id")
        if not obligation_id or obligation_id not in by_id:
            continue
        obligation = by_id[obligation_id]
        if obligation.status != UNEXPLAINED:
            continue
        attempted_raw = record.get("request_attempted_at_utc")
        if not attempted_raw:
            continue
        stamp = parse_ts(attempted_raw)
        due = parse_ts(obligation.due_at_utc)
        offset = (stamp - due).total_seconds()
        if offset < 0 or offset > tolerance:
            continue
        obligation.status = RESOLVED_BY_ATTEMPT
        obligation.resolution_kind = RESOLVED_BY_ATTEMPT
        obligation.resolution_ref = record.get("attempt_id")
        obligation.resolution_at_utc = stamp.isoformat()


def _mark_pending(obligations: list[Obligation], now: datetime, tolerance: float) -> None:
    """An obligation whose grace period has not elapsed is not yet a hole."""
    for obligation in obligations:
        if obligation.status != UNEXPLAINED:
            continue
        due = parse_ts(obligation.due_at_utc)
        if (now - due).total_seconds() <= tolerance:
            obligation.status = PENDING


def _validate_structure(transitions: list[dict[str, Any]],
                        attempts: list[dict[str, Any]],
                        lifecycle: list[dict[str, Any]],
                        now: datetime) -> list[str]:
    """Find malformed evidence that could otherwise manufacture a false pass."""
    findings: list[str] = []

    def aware(raw: str | None, *, future_allowed: bool = False,
              required: bool = True) -> datetime | None:
        if not raw:
            if required:
                findings.append("EVIDENCE_TIMESTAMP_MISSING")
            return None
        value = parse_ts(raw)
        if value.tzinfo is None:
            findings.append("NAIVE_TIMESTAMP")
            return None
        if value > now and not future_allowed:
            findings.append("FUTURE_EVIDENCE_TIMESTAMP")
        return value

    transition_ids: set[str] = set()
    obligation_ids: set[str] = set()
    transition_by_obligation: dict[str, dict[str, Any]] = {}
    previous_transition_time: datetime | None = None
    for record in transitions:
        transition_id = record.get("transition_id")
        if not transition_id or transition_id in transition_ids:
            findings.append("DUPLICATE_OR_MISSING_TRANSITION_ID")
        if transition_id:
            transition_ids.add(transition_id)
        stamp = aware(record.get("recorded_at_utc"))
        if stamp and previous_transition_time and stamp < previous_transition_time:
            findings.append("SCHEDULER_TIME_REVERSED")
        if stamp:
            previous_transition_time = stamp
        obligation_id = record.get("obligation_id")
        due = record.get("next_due_at_utc")
        if bool(obligation_id) != bool(due):
            findings.append("OBLIGATION_ID_DUE_MISMATCH")
        if not due and record.get("state") not in ("DISABLED", "BLOCKED_NOT_CONFIGURED"):
            findings.append("EXPECTED_ACTION_DUE_MISSING")
        if record.get("state") in ("DISABLED", "BLOCKED_NOT_CONFIGURED"):
            findings.append("ACQUISITION_DISABLED_DURING_WINDOW")
        if obligation_id:
            if obligation_id in obligation_ids:
                findings.append("DUPLICATE_OBLIGATION_ID")
            obligation_ids.add(obligation_id)
            transition_by_obligation[obligation_id] = record
            aware(due, future_allowed=True)

    superseded_targets: set[str] = set()
    prior_obligations: set[str] = set()
    for record in transitions:
        target = record.get("supersedes_obligation_id")
        if target and target not in prior_obligations:
            findings.append("NONPROSPECTIVE_SUPERSESSION")
        if record.get("obligation_id"):
            prior_obligations.add(record["obligation_id"])
        if not target:
            continue
        if target in superseded_targets:
            findings.append("OBLIGATION_SUPERSEDED_MORE_THAN_ONCE")
        superseded_targets.add(target)
        original = transition_by_obligation.get(target)
        if original is None:
            findings.append("SUPERSESSION_TARGET_UNKNOWN")
            continue
        replacement_time = aware(record.get("recorded_at_utc"))
        created_time = aware(original.get("recorded_at_utc"))
        if replacement_time and created_time and replacement_time < created_time:
            findings.append("NONPROSPECTIVE_SUPERSESSION")
        if record.get("obligation_id") == target:
            findings.append("CIRCULAR_SUPERSESSION")

    attempt_ids: set[str] = set()
    previous_attempt_time: datetime | None = None
    for record in attempts:
        attempt_id = record.get("attempt_id")
        if not attempt_id or attempt_id in attempt_ids:
            findings.append("DUPLICATE_OR_MISSING_ATTEMPT_ID")
        if attempt_id:
            attempt_ids.add(attempt_id)
        attempted = aware(record.get("request_attempted_at_utc"))
        received = aware(record.get("response_received_at_utc"), required=False)
        if attempted and previous_attempt_time and attempted < previous_attempt_time:
            findings.append("ATTEMPT_TIME_REVERSED")
        if attempted:
            previous_attempt_time = attempted
        if attempted and received and received < attempted:
            findings.append("RECEIPT_PRECEDES_ATTEMPT")
        if not record.get("obligation_id"):
            findings.append("ATTEMPT_OBLIGATION_ID_MISSING")
        elif record.get("obligation_id") not in obligation_ids:
            findings.append("ATTEMPT_OBLIGATION_UNKNOWN")

    if not lifecycle:
        findings.append("LIFECYCLE_PROVENANCE_MISSING")
    for record in lifecycle:
        aware(record.get("recorded_at_utc"))
        if record.get("lifecycle_cause") not in LIFECYCLE_CAUSES:
            findings.append("LIFECYCLE_CAUSE_UNATTESTED")
        if not record.get("boot_id") or not record.get("supervisor_id"):
            findings.append("LIFECYCLE_IDENTITY_INCOMPLETE")

    return sorted(set(findings))


def _validate_request_intents(collector: Any,
                              attempts: list[dict[str, Any]]) -> list[str]:
    """Validate request accounting as an ordered state machine, not a tally."""
    path = collector.paths.sec / "request_intents.jsonl"
    if not path.exists():
        return ["REQUEST_INTENT_JOURNAL_MISSING"] if attempts else []
    intents = list(read_jsonl(path))
    by_attempt: dict[str, list[dict[str, Any]]] = {}
    for record in intents:
        attempt_id = record.get("attempt_id")
        if not attempt_id:
            return ["REQUEST_INTENT_ID_MISSING"]
        by_attempt.setdefault(attempt_id, []).append(record)

    findings: list[str] = []
    attempt_by_id = {record.get("attempt_id"): record for record in attempts}
    allowed = {"INTENT", "RESERVED", "RECEIVED", "FINISHED"}
    for attempt_id, records in by_attempt.items():
        events = [record.get("event") for record in records]
        attempt = attempt_by_id.get(attempt_id)
        if attempt is None:
            findings.append("REQUEST_INTENT_WITHOUT_ATTEMPT")
            continue
        if any(event not in allowed for event in events):
            findings.append("REQUEST_EVENT_ORDER_INVALID")
        if not events or events[0] != "INTENT" or events[-1] != "FINISHED":
            findings.append("REQUEST_EVENT_ORDER_INVALID")
        if events.count("INTENT") != 1 or events.count("FINISHED") != 1:
            findings.append("REQUEST_ACCOUNTING_INCOMPLETE")

        suppressed = attempt.get("result_state") == "COOLDOWN_SUPPRESSED"
        expected_reserved = 0 if suppressed else 1
        if events.count("RESERVED") != expected_reserved:
            findings.append("BUDGET_RESERVATION_ACCOUNTING_INCOMPLETE")
        if events.count("RECEIVED") > 1 or (suppressed and events.count("RECEIVED")):
            findings.append("REQUEST_EVENT_ORDER_INVALID")

        positions = {event: [index for index, value in enumerate(events)
                             if value == event] for event in allowed}
        if positions["RESERVED"]:
            if (positions["RESERVED"][0] <= positions["INTENT"][0]
                    or positions["RESERVED"][0] >= positions["FINISHED"][0]):
                findings.append("REQUEST_EVENT_ORDER_INVALID")
        if positions["RECEIVED"]:
            if (not positions["RESERVED"]
                    or positions["RECEIVED"][0] <= positions["RESERVED"][0]
                    or positions["RECEIVED"][0] >= positions["FINISHED"][0]):
                findings.append("REQUEST_EVENT_ORDER_INVALID")

        prior: datetime | None = None
        for record in records:
            raw = record.get("recorded_at_utc") or record.get("reserved_at_utc")
            if not raw:
                findings.append("REQUEST_EVENT_TIMESTAMP_MISSING")
                continue
            try:
                stamp = parse_ts(raw)
            except (TypeError, ValueError):
                findings.append("REQUEST_EVENT_TIMESTAMP_INVALID")
                continue
            if prior is not None and stamp < prior:
                findings.append("REQUEST_EVENT_TIME_REVERSED")
            prior = stamp

    for record in attempts:
        if record.get("attempt_id") not in by_attempt:
            findings.append("REQUEST_ACCOUNTING_INCOMPLETE")
    return sorted(set(findings))

def _audit_observation_window(collector: Any, *, tolerance_seconds: float | None = None,
                             now: datetime | None = None) -> dict[str, Any]:
    """Reconcile the obligation ledger against the durable attempt record."""
    transitions = collector.scheduler.all()
    attempts = collector.store.attempts()
    lifecycle = list(read_jsonl(collector.paths.sec_lifecycle))
    policy = getattr(collector, "policy", None)
    tolerance = (tolerance_seconds if tolerance_seconds is not None
                 else (policy.discovery_poll_seconds * DUE_TOLERANCE_MULTIPLIER
                       if policy else 180.0))
    moment = now or collector.timebase.now()
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("INVALID_AUDIT_TOLERANCE")

    findings: list[str] = _validate_structure(transitions, attempts, lifecycle, moment)
    findings.extend(_validate_request_intents(collector, attempts))
    obligations, unidentified = _obligations_from(transitions)
    _resolve_supersessions(obligations, transitions)
    _resolve_attempts(obligations, attempts, tolerance)
    _mark_pending(obligations, moment, tolerance)

    # Every live service must retain a prospective next obligation. If the
    # currently named obligation has already been answered, a crash between the
    # response and successor scheduling must not look accountable.
    if getattr(collector.state, "enabled", False):
        open_id = getattr(collector.state, "open_obligation_id", None)
        if not open_id:
            findings.append("OPEN_OBLIGATION_MISSING")
        else:
            open_obligation = next(
                (item for item in obligations if item.obligation_id == open_id), None)
            if open_obligation is None:
                findings.append("OPEN_OBLIGATION_UNKNOWN")
            elif open_obligation.status != PENDING:
                findings.append("SUCCESSOR_OBLIGATION_MISSING")

    unexplained = [obligation.to_dict() for obligation in obligations
                   if obligation.status == UNEXPLAINED]
    pending = [obligation.obligation_id for obligation in obligations
               if obligation.status == PENDING]
    by_attempt = sum(1 for item in obligations
                     if item.status == RESOLVED_BY_ATTEMPT)
    by_supersession = sum(1 for item in obligations
                          if item.status == RESOLVED_BY_SUPERSESSION)

    fingerprints = collector.scheduler.fingerprints_seen()
    unattested = [record for record in lifecycle
                  if record.get("lifecycle_cause") == UNATTESTED]
    invalidating = [record for record in lifecycle
                    if record.get("lifecycle_cause") in INVALIDATING_CAUSES]

    if unexplained:
        findings.append("UNEXPLAINED_EXPECTED_ACTION")
    if unidentified:
        findings.append("OBLIGATION_IDENTITY_MISSING")
    if len(fingerprints) > 1:
        findings.append("ACQUISITION_FINGERPRINT_CHANGED")
    active = getattr(collector, "fingerprint", None)
    if active and any(value != active for value in fingerprints):
        findings.append("ACTIVE_FINGERPRINT_DIFFERS_FROM_JOURNAL")
    if any(record.get("acquisition_critical_fingerprint") != active
           for record in lifecycle) and active:
        findings.append("LIFECYCLE_FINGERPRINT_MISMATCH")
    if (collector.paths.sec / "integrity_fault.json").exists():
        findings.append("DURABLE_INTEGRITY_FAULT")
    if unattested:
        findings.append("LIFECYCLE_CAUSE_UNATTESTED")
    if invalidating:
        findings.append("INVALIDATING_INTERVENTION")
    if not transitions:
        findings.append("NO_SCHEDULER_PROVENANCE")
    if collector.state.coverage_state != "COMPLETE":
        findings.append("COVERAGE_NOT_COMPLETE")
    if collector.state.open_gaps:
        findings.append("OPEN_COVERAGE_GAPS")
    if not fingerprints or "UNAVAILABLE" in fingerprints:
        findings.append("ACQUISITION_FINGERPRINT_UNAVAILABLE")
    findings = sorted(set(findings))

    window = _window_bounds(transitions)
    return {
        "accountable": not findings,
        "findings": findings,
        # Obligation accounting. Every obligation has exactly one status.
        "obligations": len(obligations),
        "obligations_resolved_by_attempt": by_attempt,
        "obligations_resolved_by_supersession": by_supersession,
        "obligations_pending": len(pending),
        "obligations_pending_ids": pending,
        "obligations_unexplained": len(unexplained),
        "unexplained_obligations": unexplained,
        "obligations_without_identity": unidentified,
        "reconciliation": "one_obligation_to_one_resolution",
        "attempt_matching": "forward_only_within_tolerance_consumed",
        "supersession_rule": "explicit_named_before_due_with_authorized_cause",
        "due_tolerance_seconds": tolerance,
        # Kept for continuity with the earlier report shape.
        "expected_actions": len(obligations),
        "unexplained_expected_actions": unexplained,
        "attempts_recorded": len(attempts),
        "scheduler_transitions": len(transitions),
        "service_starts": len(lifecycle),
        "lifecycle_causes": sorted({record.get("lifecycle_cause") for record in lifecycle}
                                   - {None}),
        "lifecycle_cause_vocabulary": list(LIFECYCLE_CAUSES),
        "fingerprints_observed": fingerprints,
        "fingerprint_stable": len(fingerprints) <= 1,
        "window_start_utc": window[0],
        "window_end_utc": window[1],
        "window_duration_seconds": window[2],
        "coverage_state": collector.state.coverage_state,
        "open_gap_kinds": sorted({gap["kind"] for gap in collector.state.open_gaps}),
        # Deliberately not decided here.
        "t0_authority": "BLUE_TEAM",
        "p0_continuous_service_state": "OPEN / NOT_YET_PROVEN_CONTINUOUS",
    }


def audit_observation_window(collector: Any, *, tolerance_seconds: float | None = None,
                             now: datetime | None = None) -> dict[str, Any]:
    """Malformed evidence is an explicit failed verdict, never a missing report."""
    try:
        return _audit_observation_window(collector, tolerance_seconds=tolerance_seconds, now=now)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError):
        return {"accountable": False, "findings": ["ACQUISITION_EVIDENCE_INVALID"],
                "t0_authority": "BLUE_TEAM",
                "p0_continuous_service_state": "OPEN / NOT_YET_PROVEN_CONTINUOUS"}


def _window_bounds(transitions: list[dict[str, Any]]
                   ) -> tuple[str | None, str | None, float | None]:
    stamps = sorted(parse_ts(record["recorded_at_utc"]) for record in transitions
                    if record.get("recorded_at_utc"))
    if not stamps:
        return None, None, None
    return stamps[0].isoformat(), stamps[-1].isoformat(), round(
        (stamps[-1] - stamps[0]).total_seconds(), 1)
