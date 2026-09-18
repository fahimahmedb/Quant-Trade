"""Retrospective observation-window audit.

``BLUE_P0_RAW_CAPTURE_CHECKPOINT_ADDENDUM_2026-09-18.md §5.2`` closure condition
2: "every expected acquisition action is derivable from scheduler-state
transitions and is accounted for by an attempt, an authorized backoff/cooldown
transition, or an explicit failure state."

The rule that shapes this module is the one right after it: the audit "must
never infer that an attempt was not due merely because no attempt was recorded."
So the expected sequence is read forward out of the scheduler journal - each
transition prospectively declared a ``next_due_at_utc`` - and each declared due
time is then matched against what actually happened. A due time with neither an
attempt nor a later transition explaining it is an unexplained hole, and the
window is not accountable.

This module reports. It never closes ``P0_CONTINUOUS_SERVICE_STATE`` and never
records ``t0``: both belong to Blue.
"""

from __future__ import annotations

from typing import Any

from ...state import parse_ts
from .supervisor import INVALIDATING_CAUSES, LIFECYCLE_CAUSES, UNATTESTED


#: Slack allowed between a declared due time and the attempt that answers it.
#: One poll interval: a tick that lands a little late is service, not a hole.
DUE_TOLERANCE_MULTIPLIER = 3.0


def audit_observation_window(collector: Any, *, tolerance_seconds: float | None = None
                             ) -> dict[str, Any]:
    """Reconcile prospective scheduler intent against the durable attempt record."""
    transitions = collector.scheduler.all()
    attempts = collector.store.attempts()
    lifecycle = list(_read_lifecycle(collector))
    policy = collector.policy
    tolerance = (tolerance_seconds if tolerance_seconds is not None
                 else (policy.discovery_poll_seconds * DUE_TOLERANCE_MULTIPLIER
                       if policy else 180.0))

    attempt_times = sorted(parse_ts(record["request_attempted_at_utc"])
                           for record in attempts if record.get("request_attempted_at_utc"))
    # Sort on the timestamp alone: two transitions can share an instant, and
    # comparing the records themselves as a tie-break is not defined.
    transition_times = sorted(((parse_ts(record["recorded_at_utc"]), record)
                               for record in transitions if record.get("recorded_at_utc")),
                              key=lambda pair: pair[0])

    unexplained: list[dict[str, Any]] = []
    expected = 0
    for record in transitions:
        due_raw = record.get("next_due_at_utc")
        if not due_raw:
            continue
        expected += 1
        due = parse_ts(due_raw)
        # An attempt at or after the due time, within tolerance, answers it.
        answered = any(0 <= (stamp - due).total_seconds() <= tolerance
                       or abs((stamp - due).total_seconds()) <= tolerance
                       for stamp in attempt_times)
        if answered:
            continue
        # Or a later transition that moved the due time is an explanation:
        # the lane re-planned before the action came due.
        superseded = any(stamp > parse_ts(record["recorded_at_utc"])
                         and later.get("transition_id") != record.get("transition_id")
                         for stamp, later in transition_times)
        if superseded:
            continue
        unexplained.append({"transition_id": record.get("transition_id"),
                            "state": record.get("state"),
                            "cause": record.get("cause"),
                            "next_due_at_utc": due_raw})

    fingerprints = collector.scheduler.fingerprints_seen()
    unattested = [record for record in lifecycle
                  if record.get("lifecycle_cause") == UNATTESTED]
    invalidating = [record for record in lifecycle
                    if record.get("lifecycle_cause") in INVALIDATING_CAUSES]

    findings: list[str] = []
    if unexplained:
        findings.append("UNEXPLAINED_EXPECTED_ACTION")
    if len(fingerprints) > 1:
        findings.append("ACQUISITION_FINGERPRINT_CHANGED")
    if unattested:
        findings.append("LIFECYCLE_CAUSE_UNATTESTED")
    if invalidating:
        findings.append("INVALIDATING_INTERVENTION")
    if not transitions:
        findings.append("NO_SCHEDULER_PROVENANCE")

    window = _window_bounds(transition_times)
    return {
        "accountable": not findings,
        "findings": findings,
        "expected_actions": expected,
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


def _read_lifecycle(collector: Any) -> list[dict[str, Any]]:
    from ...state import read_jsonl
    return list(read_jsonl(collector.paths.sec_lifecycle))


def _window_bounds(transition_times: list[tuple[Any, dict[str, Any]]]
                   ) -> tuple[str | None, str | None, float | None]:
    if not transition_times:
        return None, None, None
    first, last = transition_times[0][0], transition_times[-1][0]
    return first.isoformat(), last.isoformat(), round((last - first).total_seconds(), 1)
