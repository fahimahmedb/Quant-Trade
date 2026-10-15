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

PRODUCER_TEST_READINESS_FIELDS = {
    "mechanism",
    "universe",
    "clock",
    "expression_requirements",
    "data_requirements",
    "cost_capacity_requirements",
    "falsification",
}
PRODUCER_READINESS_STATES = {"SUPPORTED", "PARTIAL", "REQUIRED", "UNKNOWN"}
UNKNOWN_ONLY_CLAIMS = {
    "payer",
    "quantity_mechanism",
    "directional_mechanism",
    "novelty",
    "consensus",
    "surprise",
    "market_response",
    "empirical_return",
    "capacity_estimate",
}
UNKNOWN_VALUES = {"UNKNOWN", "UNAVAILABLE", "NOT_OBSERVED", "NOT_ESTIMATED"}


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _walk_mapping(value: Any):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key, item
            yield from _walk_mapping(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk_mapping(item)


def qualify_producer_test_readiness(readiness: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a producer-side pre-outcome economic-test specification.

    The contract deliberately accepts UNKNOWN/REQUIRED fields. It qualifies whether
    the producer has stated the exact remaining work without promoting documentary
    facts into an economic result. New producer claims must carry an explicit legacy
    screen; existing bound candidates may declare that the gate applies only to any
    future claim extension.
    """
    blockers: List[str] = []
    required = PRODUCER_TEST_READINESS_FIELDS | {
        "engine_family",
        "legacy_screen",
        "unsupported_economic_claims",
        "outcome_accessed",
        "economic_result",
    }
    missing = sorted(required - readiness.keys())
    blockers.extend(f"MISSING_{field.upper()}" for field in missing)

    if readiness.get("outcome_accessed") is not False:
        blockers.append("OUTCOME_ACCESS_NOT_ALLOWED")
    if readiness.get("economic_result") != "NOT_OBSERVED":
        blockers.append("ECONOMIC_RESULT_NOT_ALLOWED")

    legacy = readiness.get("legacy_screen")
    if not isinstance(legacy, dict):
        blockers.append("LEGACY_SCREEN_MISSING")
    else:
        state = legacy.get("status")
        if state not in {"PASS", "REQUIRED_BEFORE_NEW_CLAIM", "NOT_APPLICABLE_EXISTING_BOUND_CANDIDATE"}:
            blockers.append("LEGACY_SCREEN_STATE_INVALID")
        if legacy.get("new_claim") is True and state != "PASS":
            blockers.append("LEGACY_SCREEN_REQUIRED_BEFORE_NEW_PRODUCER_CLAIM")

    for field in sorted(PRODUCER_TEST_READINESS_FIELDS):
        record = readiness.get(field)
        if not isinstance(record, dict):
            blockers.append(f"{field.upper()}_RECORD_INVALID")
            continue
        status = record.get("status")
        if status not in PRODUCER_READINESS_STATES:
            blockers.append(f"{field.upper()}_STATUS_INVALID")
        if status in {"SUPPORTED", "PARTIAL"} and not record.get("support"):
            blockers.append(f"{field.upper()}_SUPPORT_MISSING")
        if status == "UNKNOWN" and record.get("support"):
            blockers.append(f"{field.upper()}_UNKNOWN_WITH_SUPPORT")
        if "value" not in record:
            blockers.append(f"{field.upper()}_VALUE_MISSING")

    unsupported = readiness.get("unsupported_economic_claims")
    if not isinstance(unsupported, dict):
        blockers.append("UNSUPPORTED_ECONOMIC_CLAIMS_INVALID")
    else:
        for field in UNKNOWN_ONLY_CLAIMS:
            if field in unsupported and unsupported[field] not in UNKNOWN_VALUES:
                blockers.append(f"UNSUPPORTED_{field.upper()}_PROMOTED")

    # Defense in depth: these keys may appear nested in readiness records, but they
    # still cannot be populated from an announcement or rule packet alone.
    for key, value in _walk_mapping(readiness):
        if key in UNKNOWN_ONLY_CLAIMS and value not in UNKNOWN_VALUES:
            blockers.append(f"UNSUPPORTED_{key.upper()}_PROMOTED")

    canonical = deepcopy(readiness)
    canonical.pop("readiness_hash", None)
    return {
        "status": "PASS" if not blockers else "BLOCK",
        "blockers": sorted(set(blockers)),
        "readiness_hash": sha256_json(canonical),
        "field_statuses": {
            field: readiness.get(field, {}).get("status", "MISSING")
            if isinstance(readiness.get(field), dict) else "MISSING"
            for field in sorted(PRODUCER_TEST_READINESS_FIELDS)
        },
        "outcome_accessed": False,
        "economic_result": "NOT_OBSERVED",
    }


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