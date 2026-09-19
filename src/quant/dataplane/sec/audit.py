"""Fail-closed retrospective audit for the pre-t0 SEC acquisition service.

The audit never invents a healthy interval from absence. Every scheduled action
has an obligation id and a network attempt may answer only the exact obligation
it names. Request accounting is reconciled across four independent durable
facts: scheduler obligation, traffic-budget reservation, pre-send intent and
attempt journal.

This module reports. It never declares t0 and never closes the 14-day state.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from ...state import parse_ts, read_jsonl
from .scheduler import AUTHORIZED_SUPERSESSION_CAUSES
from .supervisor import INVALIDATING_CAUSES, LIFECYCLE_CAUSES, UNATTESTED

DUE_TOLERANCE_MULTIPLIER = 3.0
RESOLVED_BY_ATTEMPT = "ATTEMPT"
RESOLVED_BY_SUPERSESSION = "SUPERSEDED"
PENDING = "PENDING"
UNEXPLAINED = "UNEXPLAINED"


@dataclass
class Obligation:
    obligation_id: str
    transition_id: str
    created_at: datetime
    due_at: datetime
    status: str = UNEXPLAINED
    resolution_ref: str | None = None


def _aware(raw: str) -> datetime:
    value = parse_ts(raw)
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp is not timezone-aware")
    return value.astimezone(timezone.utc)


def _read(path) -> list[dict[str, Any]]:
    rows = list(read_jsonl(path))
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError("journal record is not an object")
    return rows


def _unique(rows: list[dict[str, Any]], key: str, finding: str,
            findings: list[str], *, required: bool = True) -> None:
    seen: set[str] = set()
    for row in rows:
        value = row.get(key)
        if not value:
            if required:
                findings.append(finding)
            continue
        if value in seen:
            findings.append(finding)
        seen.add(value)


def _validate_timestamps(rows: list[dict[str, Any]], key: str, now: datetime,
                         findings: list[str]) -> None:
    prior: datetime | None = None
    for row in rows:
        raw = row.get(key)
        if not raw:
            findings.append("TIMESTAMP_MISSING")
            continue
        stamp = _aware(raw)
        if stamp > now:
            findings.append("FUTURE_EVIDENCE")
        if prior is not None and stamp < prior:
            findings.append("JOURNAL_CLOCK_REVERSED")
        prior = stamp


def _obligations(transitions: list[dict[str, Any]],
                 findings: list[str]) -> dict[str, Obligation]:
    out: dict[str, Obligation] = {}
    for row in transitions:
        due_raw = row.get("next_due_at_utc")
        oid = row.get("obligation_id")
        if due_raw is None:
            if oid is not None:
                findings.append("OBLIGATION_WITHOUT_DUE_TIME")
            continue
        if not oid:
            findings.append("OBLIGATION_IDENTITY_MISSING")
            continue
        if oid in out:
            findings.append("DUPLICATE_OBLIGATION_ID")
            continue
        created = _aware(row["recorded_at_utc"])
        due = _aware(due_raw)
        if due < created:
            findings.append("OBLIGATION_DUE_BEFORE_CREATION")
        out[oid] = Obligation(oid, row.get("transition_id") or "", created, due)
    return out


def _apply_supersessions(obligations: dict[str, Obligation],
                         transitions: list[dict[str, Any]],
                         findings: list[str]) -> None:
    used_transitions: set[str] = set()
    by_transition = {row.get("transition_id"): row for row in transitions
                     if row.get("transition_id")}
    for row in transitions:
        target = row.get("supersedes_obligation_id")
        if not target:
            continue
        tid = row.get("transition_id")
        target_ob = obligations.get(target)
        if target_ob is None:
            findings.append("SUPERSESSION_TARGET_UNKNOWN")
            continue
        if not tid or tid in used_transitions:
            findings.append("SUPERSESSION_TRANSITION_REUSED")
            continue
        recorded = _aware(row["recorded_at_utc"])
        if recorded < target_ob.created_at:
            findings.append("NONCAUSAL_SUPERSESSION")
            continue
        if recorded >= target_ob.due_at:
            # A re-plan at/after the deadline cannot erase the missed duty.
            continue
        if (row.get("cause") or "") not in AUTHORIZED_SUPERSESSION_CAUSES:
            findings.append("UNAUTHORIZED_SUPERSESSION")
            continue
        if tid == target_ob.transition_id:
            findings.append("SELF_SUPERSESSION")
            continue
        # The transition doing the superseding must itself exist in the ledger.
        if tid not in by_transition:
            findings.append("SUPERSESSION_TRANSITION_UNKNOWN")
            continue
        if target_ob.status != UNEXPLAINED:
            findings.append("OBLIGATION_DOUBLE_RESOLUTION")
            continue
        target_ob.status = RESOLVED_BY_SUPERSESSION
        target_ob.resolution_ref = tid
        used_transitions.add(tid)


def _apply_attempts(obligations: dict[str, Obligation],
                    attempts: list[dict[str, Any]], tolerance: float,
                    findings: list[str]) -> None:
    for row in attempts:
        oid = row.get("obligation_id")
        aid = row.get("attempt_id")
        if not oid:
            findings.append("ATTEMPT_OBLIGATION_ID_MISSING")
            continue
        obligation = obligations.get(oid)
        if obligation is None:
            findings.append("ATTEMPT_OBLIGATION_UNKNOWN")
            continue
        stamp = _aware(row["request_attempted_at_utc"])
        offset = (stamp - obligation.due_at).total_seconds()
        if offset < 0:
            findings.append("ATTEMPT_BEFORE_DUE")
            continue
        if offset > tolerance:
            findings.append("ATTEMPT_AFTER_DUE_WINDOW")
            continue
        if obligation.status == RESOLVED_BY_SUPERSESSION:
            findings.append("OBLIGATION_DOUBLE_RESOLUTION")
            continue
        if obligation.status == RESOLVED_BY_ATTEMPT:
            findings.append("OBLIGATION_MULTIPLE_ATTEMPTS")
            continue
        obligation.status = RESOLVED_BY_ATTEMPT
        obligation.resolution_ref = aid


def _mark_pending(obligations: dict[str, Obligation], now: datetime,
                  tolerance: float) -> None:
    for obligation in obligations.values():
        if obligation.status == UNEXPLAINED and \
                (now - obligation.due_at).total_seconds() <= tolerance:
            obligation.status = PENDING


def _request_accounting(attempts: list[dict[str, Any]],
                        reservations: list[dict[str, Any]],
                        intents: list[dict[str, Any]],
                        findings: list[str]) -> None:
    _unique(reservations, "attempt_id", "DUPLICATE_BUDGET_RESERVATION", findings)
    _unique(attempts, "attempt_id", "DUPLICATE_ATTEMPT_ID", findings)

    stages: dict[str, list[str]] = {}
    for row in intents:
        aid = row.get("attempt_id")
        event = row.get("event")
        if not aid or event not in {
            "INTENT", "RESERVED", "SEND_AUTHORIZED", "RECEIVED", "FINISHED", "SUPPRESSED"}:
            findings.append("REQUEST_INTENT_INVALID")
            continue
        stages.setdefault(aid, []).append(event)

    reservation_ids = {row.get("attempt_id") for row in reservations}
    attempt_ids = {row.get("attempt_id") for row in attempts}
    for aid, events in stages.items():
        for event in set(events):
            if events.count(event) > 1:
                findings.append("DUPLICATE_REQUEST_STAGE")
        if "SUPPRESSED" in events:
            if any(event in events for event in ("RESERVED", "SEND_AUTHORIZED",
                                                 "RECEIVED", "FINISHED")):
                findings.append("SUPPRESSED_REQUEST_WAS_EMITTED")
            continue
        required = {"INTENT", "RESERVED", "SEND_AUTHORIZED", "FINISHED"}
        if not required.issubset(events):
            findings.append("REQUEST_ACCOUNTING_INCOMPLETE")
        if aid not in reservation_ids:
            findings.append("ATTEMPT_WITHOUT_BUDGET_RESERVATION")
        if "SEND_AUTHORIZED" in events and aid not in attempt_ids:
            findings.append("SEND_WITHOUT_DURABLE_ATTEMPT")

    for aid in reservation_ids:
        if aid not in stages:
            findings.append("BUDGET_RESERVATION_WITHOUT_INTENT")
        if aid not in attempt_ids:
            findings.append("BUDGET_RESERVATION_WITHOUT_ATTEMPT")
    for aid in attempt_ids:
        if aid not in reservation_ids:
            findings.append("ATTEMPT_WITHOUT_BUDGET_RESERVATION")
        events = stages.get(aid, [])
        if "SEND_AUTHORIZED" not in events or "FINISHED" not in events:
            findings.append("ATTEMPT_REQUEST_CHAIN_INCOMPLETE")


def audit_observation_window(collector: Any, *, tolerance_seconds: float | None = None,
                             now: datetime | None = None) -> dict[str, Any]:
    """Return a count-free pass/fail projection suitable for a pre-t0 gate."""
    findings: list[str] = []
    try:
        moment = (now or collector.timebase.now()).astimezone(timezone.utc)
        if moment.tzinfo is None:
            raise ValueError("audit time must be aware")
        active_fingerprint = collector.fingerprint
        all_transitions = _read(collector.paths.sec_scheduler)
        all_lifecycle = _read(collector.paths.sec_lifecycle)
        all_intents = _read(collector.paths.sec_request_intents)
        all_reservations = _read(collector.paths.sec_budget_reservations)
        all_attempts = collector.store.attempts()

        # A new acquisition-critical fingerprint begins a new prospective epoch.
        # Historical bytes/journals remain immutable, but cannot certify or poison
        # the current pre-t0 window.
        transitions = [row for row in all_transitions
                       if row.get("acquisition_critical_fingerprint") == active_fingerprint]
        lifecycle = [row for row in all_lifecycle
                     if row.get("acquisition_critical_fingerprint") == active_fingerprint]
        intents = [row for row in all_intents
                   if row.get("acquisition_critical_fingerprint") == active_fingerprint]
        scoped_ids = {row.get("attempt_id") for row in intents if row.get("attempt_id")}
        attempts = [row for row in all_attempts if row.get("attempt_id") in scoped_ids]
        reservations = [row for row in all_reservations
                        if row.get("attempt_id") in scoped_ids]
        policy = getattr(collector, "policy", None)
        tolerance = (tolerance_seconds if tolerance_seconds is not None else
                     (policy.discovery_poll_seconds * DUE_TOLERANCE_MULTIPLIER
                      if policy else 180.0))
        if tolerance < 0 or tolerance == float("inf"):
            raise ValueError("invalid tolerance")

        _unique(transitions, "transition_id", "DUPLICATE_TRANSITION_ID", findings)
        _validate_timestamps(transitions, "recorded_at_utc", moment, findings)
        _validate_timestamps(attempts, "request_attempted_at_utc", moment, findings)
        if lifecycle:
            _validate_timestamps(lifecycle, "recorded_at_utc", moment, findings)
        else:
            findings.append("LIFECYCLE_PROVENANCE_MISSING")

        obligations = _obligations(transitions, findings)
        _apply_supersessions(obligations, transitions, findings)
        _apply_attempts(obligations, attempts, tolerance, findings)
        _mark_pending(obligations, moment, tolerance)

        if any(item.status == UNEXPLAINED for item in obligations.values()):
            findings.append("UNEXPLAINED_EXPECTED_ACTION")
        if not transitions:
            findings.append("NO_SCHEDULER_PROVENANCE")

        fingerprints = {row.get("acquisition_critical_fingerprint")
                        for row in transitions if row.get("acquisition_critical_fingerprint")}
        if len(fingerprints) > 1:
            findings.append("ACQUISITION_FINGERPRINT_CHANGED")
        if any(row.get("lifecycle_cause") == UNATTESTED for row in lifecycle):
            findings.append("LIFECYCLE_CAUSE_UNATTESTED")
        if any(row.get("lifecycle_cause") not in LIFECYCLE_CAUSES
               for row in lifecycle):
            findings.append("LIFECYCLE_CAUSE_INVALID")
        if any(row.get("lifecycle_cause") in INVALIDATING_CAUSES for row in lifecycle):
            findings.append("INVALIDATING_INTERVENTION")

        _request_accounting(attempts, reservations, intents, findings)
        findings.extend(collector._state_proof_findings())
        if collector.state.coverage_state != "COMPLETE" or collector.state.open_gaps:
            findings.append("COVERAGE_NOT_COMPLETE")
        if collector.liveness() != "RUNNING":
            findings.append("COLLECTOR_NOT_LIVE")
    except Exception:
        findings.append("ACQUISITION_JOURNAL_INVALID")

    findings = sorted(set(findings))
    return {
        "accountable": not findings,
        "findings": findings,
        "fingerprint_stable": "ACQUISITION_FINGERPRINT_CHANGED" not in findings,
        "coverage_complete": "COVERAGE_NOT_COMPLETE" not in findings,
        "request_accounting_complete": not any(
            marker in finding for finding in findings
            for marker in ("REQUEST_", "ATTEMPT_", "BUDGET_RESERVATION")),
        "lifecycle_attested": not any(
            finding.startswith("LIFECYCLE_") for finding in findings),
        "t0_authority": "BLUE_TEAM",
        "p0_continuous_service_state": "OPEN / NOT_YET_PROVEN_CONTINUOUS",
    }
