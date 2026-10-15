from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List


ALLOWED_EVENT_TYPES = {"ACTION_STARTED", "ACTION_COMPLETED", "WORKER_HEARTBEAT", "SESSION_ENDED"}
ALLOWED_UI_ACTIVITIES = {
    "none",
    "source-research",
    "document-reading",
    "data-qualification",
    "coding-testing",
    "calculation-economic-look",
    "audit-red-team",
    "commit-persistence",
    "handoff",
    "result",
    "blocker",
}


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def worker_events(run_id: str, stages: Iterable[Dict[str, str]], *, base_time: str) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    seq_by_worker: Dict[str, int] = {}
    clock = _parse_utc(base_time)
    absolute_seq = 0
    for stage in stages:
        worker_id = stage["worker_id"]
        action_id = stage["action_id"]
        label = stage.get("label", action_id)
        detail = stage.get("detail", "")
        activity = stage.get("ui_activity", "source-research")
        if activity not in ALLOWED_UI_ACTIVITIES:
            raise ValueError(f"invalid ui_activity: {activity}")
        for event_type in ("ACTION_STARTED", "ACTION_COMPLETED"):
            seq_by_worker[worker_id] = seq_by_worker.get(worker_id, 0) + 1
            seq = seq_by_worker[worker_id]
            absolute_seq += 1
            events.append({
                "event_id": f"{run_id}:{worker_id}:{seq}",
                "session_id": run_id,
                "worker_id": worker_id,
                "action_id": action_id,
                "event_type": event_type,
                "event_seq": seq,
                "generation": 1,
                "emitted_at": _iso(clock + timedelta(seconds=absolute_seq)),
                "payload": {
                    "label": label,
                    "detail": detail,
                    "ui_activity": activity if event_type == "ACTION_STARTED" else "none",
                },
            })
    validate_native_events(events)
    return events


def validate_native_events(events: List[Dict[str, Any]]) -> None:
    required = {"event_id", "session_id", "worker_id", "action_id", "event_type", "event_seq", "generation", "emitted_at"}
    for event in events:
        missing = required - event.keys()
        if missing:
            raise ValueError(f"worker event missing fields: {sorted(missing)}")
        if event["event_type"] not in ALLOWED_EVENT_TYPES:
            raise ValueError(f"unsupported native event type: {event['event_type']}")
        if event["event_seq"] < 1 or event["generation"] < 1:
            raise ValueError("invalid worker event ordering")
        activity = (event.get("payload") or {}).get("ui_activity")
        if activity not in ALLOWED_UI_ACTIVITIES:
            raise ValueError(f"unsupported ui activity: {activity}")
