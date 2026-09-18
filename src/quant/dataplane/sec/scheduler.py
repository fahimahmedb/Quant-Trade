"""Durable scheduler-state provenance.

``BLUE_P0_RAW_CAPTURE_CHECKPOINT_ADDENDUM_2026-09-18.md §5.2``: the retrospective
audit "derives the expected attempt sequence from these transitions. It must
never infer that an attempt was not due merely because no attempt was recorded."

That sentence is the whole design. A journal of attempts can only show what
happened; it cannot distinguish "nothing was due" from "something was due and
the service was dead". So every transition that can change the next expected
acquisition action is written here *prospectively*, with the time it will next
be due, so a hole in the attempt journal can be checked against what the
scheduler said it intended to do.

Every record carries the active acquisition fingerprint, so a transition can be
attributed to the exact frozen semantics that produced it.

Firewall-safe by construction: states, causes, times, digests and cooldown
figures only. No accession, locator, filing content or count.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from ...state import append_jsonl, read_jsonl
from pathlib import Path


#: Scheduler states. Each says what the lane is waiting for.
AWAITING_POLL = "AWAITING_POLL"
POLL_DUE = "POLL_DUE"
DRAINING = "DRAINING"
RECONCILING = "RECONCILING"
BACKOFF = "BACKOFF"
COOLDOWN = "COOLDOWN"
BLOCKED_NOT_CONFIGURED = "BLOCKED_NOT_CONFIGURED"
DISABLED = "DISABLED"

SCHEDULER_STATES = (AWAITING_POLL, POLL_DUE, DRAINING, RECONCILING, BACKOFF, COOLDOWN,
                    BLOCKED_NOT_CONFIGURED, DISABLED)

#: Causes. Why the next expected action changed.
SERVICE_START = "SERVICE_START"
POLL_COMPLETED = "POLL_COMPLETED"
POLL_FAILED = "POLL_FAILED"
WORK_ENQUEUED = "WORK_ENQUEUED"
DRAIN_COMPLETED = "DRAIN_COMPLETED"
RECONCILE_COMPLETED = "RECONCILE_COMPLETED"
BACKOFF_ENTERED = "BACKOFF_ENTERED"
COOLDOWN_OBSERVED = "COOLDOWN_OBSERVED"
COOLDOWN_EXPIRED = "COOLDOWN_EXPIRED"
CONFIG_FAIL_CLOSED = "CONFIG_FAIL_CLOSED"
LANE_DISABLED = "LANE_DISABLED"
LANE_ENABLED = "LANE_ENABLED"


@dataclass
class SchedulerTransition:
    """One prospective statement about what the lane will do next."""

    transition_id: str
    recorded_at_utc: str
    state: str
    cause: str
    #: When the next acquisition action becomes due. None means "nothing is due
    #: and nothing will become due without an external change", which is itself
    #: a claim the audit can check.
    next_due_at_utc: str | None
    acquisition_critical_fingerprint: str
    boot_id: str | None = None
    lifecycle_cause: str | None = None
    cooldown_until_utc: str | None = None
    cooldown_reason: str | None = None
    backoff_step: int | None = None
    coverage_state: str | None = None
    work_in_flight: bool = False
    detail: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SchedulerJournal:
    """Append-only scheduler provenance."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def record(self, transition: SchedulerTransition) -> SchedulerTransition:
        if transition.state not in SCHEDULER_STATES:
            raise ValueError(f"unknown scheduler state: {transition.state}")
        append_jsonl(self.path, transition.to_dict())
        return transition

    def all(self) -> list[dict[str, Any]]:
        return list(read_jsonl(self.path))

    def latest(self) -> dict[str, Any] | None:
        records = self.all()
        return records[-1] if records else None

    def expected_actions(self) -> list[dict[str, Any]]:
        """Every moment the scheduler prospectively said an action would be due.

        This is what the retrospective audit reconciles against the attempt
        journal. A due time with no corresponding attempt and no later
        transition explaining it is an unexplained hole.
        """
        return [record for record in self.all() if record.get("next_due_at_utc")]

    def fingerprints_seen(self) -> list[str]:
        seen: list[str] = []
        for record in self.all():
            value = record.get("acquisition_critical_fingerprint")
            if value and value not in seen:
                seen.append(value)
        return seen
