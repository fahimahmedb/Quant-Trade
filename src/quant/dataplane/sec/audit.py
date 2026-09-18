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
    """Assign at most one attempt to each still-open obligation, forward only.

    Obligations are taken in due order and each is given the earliest unconsumed
    attempt inside ``[due, due + tolerance]``. Greedy assignment over two sorted
    sequences is optimal for point-in-window matching, and consumption is what
    makes the relation one-to-one.
    """
    available = sorted(
        ((parse_ts(record["request_attempted_at_utc"]), record.get("attempt_id") or "")
         for record in attempts
         if record.get("request_attempted_at_utc")
         and record.get("result_state") not in NON_ANSWERING_ATTEMPT_STATES),
        key=lambda pair: pair[0])
    spent: set[int] = set()
    for obligation in sorted(obligations, key=lambda item: item.due_at_utc):
        if obligation.status != UNEXPLAINED:
            continue
        due = parse_ts(obligation.due_at_utc)
        for index, (stamp, attempt_id) in enumerate(available):
            if index in spent:
                continue
            offset = (stamp - due).total_seconds()
            # Forward only. An attempt made before the deadline answers whatever
            # was due then, never a commitment that had not yet come due.
            if offset < 0:
                continue
            if offset > tolerance:
                break
            obligation.status = RESOLVED_BY_ATTEMPT
            obligation.resolution_kind = RESOLVED_BY_ATTEMPT
            obligation.resolution_ref = attempt_id
            obligation.resolution_at_utc = stamp.isoformat()
            spent.add(index)
            break


def _mark_pending(obligations: list[Obligation], now: datetime, tolerance: float) -> None:
    """An obligation whose grace period has not elapsed is not yet a hole."""
    for obligation in obligations:
        if obligation.status != UNEXPLAINED:
            continue
        due = parse_ts(obligation.due_at_utc)
        if (now - due).total_seconds() <= tolerance:
            obligation.status = PENDING


def audit_observation_window(collector: Any, *, tolerance_seconds: float | None = None,
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

    obligations, unidentified = _obligations_from(transitions)
    _resolve_supersessions(obligations, transitions)
    _resolve_attempts(obligations, attempts, tolerance)
    _mark_pending(obligations, moment, tolerance)

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

    findings: list[str] = []
    if unexplained:
        findings.append("UNEXPLAINED_EXPECTED_ACTION")
    if unidentified:
        findings.append("OBLIGATION_IDENTITY_MISSING")
    if len(fingerprints) > 1:
        findings.append("ACQUISITION_FINGERPRINT_CHANGED")
    if unattested:
        findings.append("LIFECYCLE_CAUSE_UNATTESTED")
    if invalidating:
        findings.append("INVALIDATING_INTERVENTION")
    if not transitions:
        findings.append("NO_SCHEDULER_PROVENANCE")

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


def _window_bounds(transitions: list[dict[str, Any]]
                   ) -> tuple[str | None, str | None, float | None]:
    stamps = sorted(parse_ts(record["recorded_at_utc"]) for record in transitions
                    if record.get("recorded_at_utc"))
    if not stamps:
        return None, None, None
    return stamps[0].isoformat(), stamps[-1].isoformat(), round(
        (stamps[-1] - stamps[0]).total_seconds(), 1)
