from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

from research.research_os.scientific_store import sha256_json


FORBIDDEN_CONTENT_CLASSES = {
    "returns",
    "payoffs",
    "future_outcomes",
    "market_reaction",
    "execution_prices",
    "post_event_price_response",
    "implementation_price_response",
    "post_release_price_response",
}


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def build_acquisition_plan(
    validated_adapter: Dict[str, Any],
    request: Dict[str, Any],
) -> Dict[str, Any]:
    blockers: List[str] = []
    adapter_spec = validated_adapter.get("canonical_spec") or {}
    if validated_adapter.get("status") != "PASS":
        blockers.append("ADAPTER_NOT_QUALIFIED")
    if validated_adapter.get("activated") is not False:
        blockers.append("ADAPTER_UNEXPECTEDLY_ACTIVE")
    if validated_adapter.get("network_access") is not False:
        blockers.append("NETWORK_ALREADY_ENABLED")
    if validated_adapter.get("outcome_access_authorized") is not False:
        blockers.append("OUTCOME_ACCESS_ALREADY_AUTHORIZED")

    requested_content = set(request.get("content_classes") or [])
    allowed_content = set(adapter_spec.get("allowed_content") or [])
    forbidden = set(adapter_spec.get("forbidden_content") or []) | FORBIDDEN_CONTENT_CLASSES
    disallowed_requested = sorted(requested_content - allowed_content)
    forbidden_requested = sorted(requested_content & forbidden)
    if not requested_content:
        blockers.append("NO_CONTENT_CLASS_REQUESTED")
    blockers.extend(f"CONTENT_NOT_ALLOWED:{item}" for item in disallowed_requested)
    blockers.extend(f"FORBIDDEN_CONTENT_REQUESTED:{item}" for item in forbidden_requested)

    for field in ("request_id", "entity_scope", "clock_cutoff", "version_policy"):
        if request.get(field) in (None, "", [], {}):
            blockers.append(f"MISSING_{field.upper()}")

    payload = {
        "request_id": request.get("request_id"),
        "adapter_id": validated_adapter.get("adapter_id"),
        "adapter_hash": validated_adapter.get("adapter_hash"),
        "entity_scope": deepcopy(request.get("entity_scope")),
        "content_classes": sorted(requested_content),
        "clock_cutoff": request.get("clock_cutoff"),
        "version_policy": request.get("version_policy"),
        "locator_parameters": deepcopy(request.get("locator_parameters") or {}),
        "execution_mode": "PLAN_ONLY_NO_NETWORK",
    }
    return {
        "request_id": request.get("request_id"),
        "adapter_id": validated_adapter.get("adapter_id"),
        "status": "READY_AWAITING_SOURCE_ACTIVATION_AUTHORITY" if not blockers else "BLOCK",
        "blockers": sorted(set(blockers)),
        "plan": payload,
        "plan_hash": sha256_json(payload),
        "network_execution_authorized": False,
        "network_call_performed": False,
        "outcome_access_authorized": False,
        "outcome_accessed": False,
    }


def content_firewall(plan: Dict[str, Any], raw_record: Dict[str, Any]) -> Dict[str, Any]:
    blockers: List[str] = []
    if plan.get("status") != "READY_AWAITING_SOURCE_ACTIVATION_AUTHORITY":
        blockers.append("ACQUISITION_PLAN_NOT_READY")
    if plan.get("network_call_performed") is not False:
        blockers.append("NETWORK_CALL_DETECTED")
    if raw_record.get("fixture_only") is not True:
        blockers.append("NON_FIXTURE_RECORD_FORBIDDEN_IN_WAVE4")
    if raw_record.get("contains_outcome") is not False:
        blockers.append("OUTCOME_BEARING_RECORD_FORBIDDEN")

    content_classes = set(raw_record.get("content_classes") or [])
    requested = set((plan.get("plan") or {}).get("content_classes") or [])
    forbidden_seen = sorted(content_classes & FORBIDDEN_CONTENT_CLASSES)
    undeclared = sorted(content_classes - requested)
    blockers.extend(f"FORBIDDEN_CONTENT_PRESENT:{item}" for item in forbidden_seen)
    blockers.extend(f"UNDECLARED_CONTENT_PRESENT:{item}" for item in undeclared)

    required = {
        "record_id",
        "source_version_id",
        "effective_at",
        "published_at",
        "captured_at",
        "content_classes",
        "payload",
        "fixture_only",
        "contains_outcome",
    }
    blockers.extend(f"MISSING_{field.upper()}" for field in sorted(required - raw_record.keys()))

    cutoff = (plan.get("plan") or {}).get("clock_cutoff")
    try:
        if cutoff and raw_record.get("published_at") and _parse_utc(raw_record["published_at"]) > _parse_utc(cutoff):
            blockers.append("RECORD_PUBLISHED_AFTER_CLOCK_CUTOFF")
        if raw_record.get("captured_at") and raw_record.get("published_at") and _parse_utc(raw_record["captured_at"]) < _parse_utc(raw_record["published_at"]):
            blockers.append("CAPTURE_PRECEDES_PUBLICATION")
    except ValueError:
        blockers.append("INVALID_RECORD_CLOCK")

    payload = deepcopy(raw_record.get("payload") or {})
    forbidden_keys = FORBIDDEN_CONTENT_CLASSES & set(payload.keys())
    blockers.extend(f"FORBIDDEN_PAYLOAD_KEY:{item}" for item in sorted(forbidden_keys))

    return {
        "record_id": raw_record.get("record_id"),
        "status": "PASS" if not blockers else "BLOCK",
        "blockers": sorted(set(blockers)),
        "content_classes": sorted(content_classes),
        "raw_record_hash": sha256_json(raw_record),
        "outcome_accessed": False,
        "network_origin": False,
    }


def normalize_typed_pit_record(
    plan: Dict[str, Any],
    raw_record: Dict[str, Any],
    firewall_result: Dict[str, Any],
) -> Dict[str, Any]:
    if firewall_result.get("status") != "PASS":
        return {
            "record_id": raw_record.get("record_id"),
            "status": "BLOCK",
            "blockers": ["CONTENT_FIREWALL_BLOCK"],
            "outcome_accessed": False,
        }

    typed_payload = {
        "record_id": raw_record["record_id"],
        "adapter_id": plan["adapter_id"],
        "plan_hash": plan["plan_hash"],
        "source_version_id": raw_record["source_version_id"],
        "effective_at": raw_record["effective_at"],
        "published_at": raw_record["published_at"],
        "captured_at": raw_record["captured_at"],
        "content_classes": sorted(raw_record["content_classes"]),
        "payload": deepcopy(raw_record["payload"]),
        "record_origin": "SYNTHETIC_FIXTURE_ONLY",
    }
    return {
        **typed_payload,
        "status": "PASS",
        "typed_record_hash": sha256_json(typed_payload),
        "outcome_accessed": False,
        "network_origin": False,
        "point_in_time_record": True,
    }


def build_provenance_manifest(
    plan: Dict[str, Any],
    firewall_result: Dict[str, Any],
    typed_record: Dict[str, Any],
) -> Dict[str, Any]:
    blockers: List[str] = []
    if firewall_result.get("status") != "PASS":
        blockers.append("FIREWALL_NOT_PASS")
    if typed_record.get("status") != "PASS":
        blockers.append("TYPED_RECORD_NOT_PASS")
    if plan.get("network_call_performed") is not False:
        blockers.append("NETWORK_SIDE_EFFECT_DETECTED")
    payload = {
        "request_id": plan.get("request_id"),
        "adapter_id": plan.get("adapter_id"),
        "adapter_plan_hash": plan.get("plan_hash"),
        "raw_record_hash": firewall_result.get("raw_record_hash"),
        "typed_record_hash": typed_record.get("typed_record_hash"),
        "record_id": typed_record.get("record_id"),
        "source_version_id": typed_record.get("source_version_id"),
        "published_at": typed_record.get("published_at"),
        "captured_at": typed_record.get("captured_at"),
        "origin": "SYNTHETIC_FIXTURE_ONLY",
    }
    return {
        "record_id": typed_record.get("record_id"),
        "status": "PASS" if not blockers else "BLOCK",
        "blockers": blockers,
        "manifest": payload,
        "manifest_hash": sha256_json(payload),
        "network_accessed": False,
        "outcome_accessed": False,
    }


def firewall_summary(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    items = list(records)
    return {
        "firewall_version": "acquisition-firewall.v1",
        "record_count": len(items),
        "pass_count": sum(item.get("status") == "PASS" for item in items),
        "block_count": sum(item.get("status") != "PASS" for item in items),
        "network_records": sum(bool(item.get("network_origin")) for item in items),
        "outcomes_accessed": sum(bool(item.get("outcome_accessed")) for item in items),
    }
