from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

from research.research_os.scientific_store import sha256_json


ALLOWED_SOURCE_CLASSES = {
    "PRIMARY_PUBLIC",
    "OFFICIAL_API",
    "EXCHANGE_PUBLIC",
    "REGULATORY_FILING",
    "AUTHORIZED_INTERNAL",
    "SYNTHETIC_FIXTURE",
}
ALLOWED_PIT_MODES = {"EVENT_TIME", "PUBLICATION_TIME", "VERSIONED_SNAPSHOT"}
ALLOWED_PERMISSION_STATES = {"PUBLIC", "AUTHORIZED_INTERNAL", "FIXTURE_ONLY"}


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def qualify_source_route(route: Dict[str, Any], *, freeze_time: str) -> Dict[str, Any]:
    blockers: List[str] = []
    required = {
        "route_id",
        "source_class",
        "transport",
        "locator",
        "permission_state",
        "pit_mode",
        "revision_policy",
        "survivorship_policy",
        "timezone",
        "availability_start",
        "contains_outcome",
    }
    missing = sorted(required - route.keys())
    blockers.extend(f"MISSING_{field.upper()}" for field in missing)

    if route.get("source_class") not in ALLOWED_SOURCE_CLASSES:
        blockers.append("SOURCE_CLASS_NOT_ALLOWED")
    if route.get("pit_mode") not in ALLOWED_PIT_MODES:
        blockers.append("PIT_MODE_NOT_ALLOWED")
    if route.get("permission_state") not in ALLOWED_PERMISSION_STATES:
        blockers.append("PERMISSION_NOT_QUALIFIED")
    if not route.get("locator"):
        blockers.append("LOCATOR_MISSING")
    if route.get("contains_outcome") is not False:
        blockers.append("UNAUTHORIZED_OUTCOME_BEARING_ROUTE")
    if route.get("revision_policy") in (None, "", "UNKNOWN"):
        blockers.append("REVISION_POLICY_UNKNOWN")
    if route.get("survivorship_policy") in (None, "", "UNKNOWN"):
        blockers.append("SURVIVORSHIP_POLICY_UNKNOWN")
    if route.get("timezone") in (None, "", "UNKNOWN"):
        blockers.append("TIMEZONE_UNKNOWN")

    availability_start = route.get("availability_start")
    if availability_start:
        try:
            if _parse_utc(availability_start) > _parse_utc(freeze_time):
                blockers.append("ROUTE_NOT_AVAILABLE_AT_FREEZE")
        except ValueError:
            blockers.append("AVAILABILITY_CLOCK_INVALID")

    canonical = {
        "route_id": route.get("route_id"),
        "source_class": route.get("source_class"),
        "transport": route.get("transport"),
        "locator": route.get("locator"),
        "permission_state": route.get("permission_state"),
        "pit_mode": route.get("pit_mode"),
        "event_time_field": route.get("event_time_field"),
        "publication_time_field": route.get("publication_time_field"),
        "revision_policy": route.get("revision_policy"),
        "survivorship_policy": route.get("survivorship_policy"),
        "timezone": route.get("timezone"),
        "availability_start": route.get("availability_start"),
        "contains_outcome": route.get("contains_outcome"),
        "content_scope": route.get("content_scope", "DESIGN_METADATA_ONLY"),
    }
    return {
        "route_id": route.get("route_id"),
        "status": "PASS" if not blockers else "BLOCK",
        "blockers": sorted(set(blockers)),
        "route_hash": sha256_json(canonical),
        "freeze_time": freeze_time,
        "point_in_time_qualified": not any(
            blocker in blockers
            for blocker in (
                "PIT_MODE_NOT_ALLOWED",
                "REVISION_POLICY_UNKNOWN",
                "SURVIVORSHIP_POLICY_UNKNOWN",
                "TIMEZONE_UNKNOWN",
                "ROUTE_NOT_AVAILABLE_AT_FREEZE",
                "AVAILABILITY_CLOCK_INVALID",
            )
        ),
        "outcome_accessed": False,
        "canonical_route": canonical,
    }


class ImmutableSourceRouteRegistry:
    def __init__(self) -> None:
        self._entries: Dict[str, Dict[str, Any]] = {}

    def register(self, qualification: Dict[str, Any]) -> Dict[str, Any]:
        route_id = qualification["route_id"]
        if not route_id:
            raise ValueError("route_id required")
        current = self._entries.get(route_id)
        if current is not None:
            if current["route_hash"] != qualification["route_hash"]:
                raise ValueError(f"immutable source route mutation rejected: {route_id}")
            return deepcopy(current)
        self._entries[route_id] = deepcopy(qualification)
        return deepcopy(qualification)

    def register_many(self, qualifications: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.register(item) for item in qualifications]

    def snapshot(self) -> Dict[str, Any]:
        entries = [deepcopy(self._entries[key]) for key in sorted(self._entries)]
        return {
            "registry_id": "source-route-registry.v1",
            "entry_count": len(entries),
            "entries": entries,
            "immutable": True,
            "outcome_routes_authorized": False,
        }
