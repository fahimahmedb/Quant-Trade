from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Iterable, List

from research.research_os.scientific_store import sha256_json
from .acquisition_firewall_v1 import FORBIDDEN_CONTENT_CLASSES, build_acquisition_plan
from .source_qualification import qualify_producer_test_readiness


CLOSED_AUTHORITY = {
    "economic_experiment_authorized": False,
    "prospective_observation_authorized": False,
    "real_capital_authorized": False,
    "live_trading_authorized": False,
}

FORBIDDEN_REQUIREMENT_MARKERS = (
    " return",
    "returns",
    "pnl",
    "profit",
    "loss",
    "payoff",
    "outcome",
    "market response",
    "market reaction",
    "price response",
    "execution price",
    "future price",
    "future observation",
    "post-event",
    "post event",
    "post-release",
    "post release",
)


def _parse_bound_clock(value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("CLOCK_CUTOFF_REQUIRED")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("CLOCK_CUTOFF_MUST_BE_TIMEZONE_AWARE")


def _forbidden_requirement(requirement: str) -> bool:
    text = " " + " ".join(requirement.lower().replace("_", " ").split())
    return any(marker in text for marker in FORBIDDEN_REQUIREMENT_MARKERS)


def _validate_readiness(readiness: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
    if not isinstance(readiness, dict):
        raise ValueError("READINESS_PROJECTION_REQUIRED")
    if readiness.get("outcome_accessed") is not False:
        raise ValueError("OUTCOME_BEARING_READINESS_FORBIDDEN")
    if readiness.get("economic_result") != "NOT_OBSERVED":
        raise ValueError("ECONOMIC_RESULT_BEARING_READINESS_FORBIDDEN")
    specification = readiness.get("specification")
    if not isinstance(specification, dict):
        raise ValueError("READINESS_SPECIFICATION_REQUIRED")
    qualification = qualify_producer_test_readiness(specification)
    if qualification["status"] != "PASS":
        raise ValueError("READINESS_SPECIFICATION_NOT_QUALIFIED:" + ",".join(qualification["blockers"]))
    supplied = readiness.get("qualification")
    if supplied is not None and supplied.get("readiness_hash") != qualification["readiness_hash"]:
        raise ValueError("READINESS_QUALIFICATION_BINDING_MISMATCH")
    if not readiness.get("hypothesis_id"):
        raise ValueError("HYPOTHESIS_ID_REQUIRED")
    return specification, qualification


def _explicit_requirements(specification: Dict[str, Any]) -> List[str]:
    record = specification.get("data_requirements") or {}
    if record.get("status") not in {"REQUIRED", "PARTIAL"}:
        return []
    values = record.get("value")
    if not isinstance(values, list) or not values or any(not isinstance(item, str) or not item.strip() for item in values):
        raise ValueError("EXPLICIT_DATA_REQUIREMENT_LIST_REQUIRED")
    return sorted(set(item.strip() for item in values))


def _catalog_matches(requirement: str, catalog: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [deepcopy(item) for item in catalog if isinstance(item, dict) and item.get("requirement") == requirement]


def _validate_declared_route(entry: Dict[str, Any]) -> List[str]:
    blockers: List[str] = []
    required = ("requirement", "adapter_id", "content_classes", "entity_scope", "clock_cutoff", "version_policy")
    for field in required:
        if entry.get(field) in (None, "", [], {}):
            blockers.append("MISSING_" + field.upper())
    classes = entry.get("content_classes")
    if classes not in (None, []) and (
        not isinstance(classes, list)
        or any(not isinstance(item, str) or not item.strip() for item in classes)
    ):
        blockers.append("CONTENT_CLASSES_INVALID")
    try:
        _parse_bound_clock(entry.get("clock_cutoff"))
    except (TypeError, ValueError):
        blockers.append("CLOCK_CUTOFF_NOT_PIT_BOUND")
    if entry.get("version_policy") in (None, "", "UNKNOWN"):
        blockers.append("VERSION_POLICY_NOT_DECLARED")
    return sorted(set(blockers))


def _request_id(hypothesis_id: str, requirement: str, entry: Dict[str, Any], adapter: Dict[str, Any]) -> str:
    identity = {
        "hypothesis_id": hypothesis_id,
        "requirement": requirement,
        "adapter_id": entry.get("adapter_id"),
        "adapter_hash": adapter.get("adapter_hash"),
        "content_classes": sorted(entry.get("content_classes") or []),
        "entity_scope": entry.get("entity_scope"),
        "clock_cutoff": entry.get("clock_cutoff"),
        "version_policy": entry.get("version_policy"),
        "locator_parameters": entry.get("locator_parameters") or {},
    }
    return "ACQ-" + sha256_json(identity)[:24]


def build_evidence_acquisition_intents(
    readiness: Dict[str, Any],
    *,
    declared_routes: Iterable[Dict[str, Any]],
    validated_adapters: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Project explicit producer data gaps into bounded no-network acquisition intents.

    Matching is exact by requirement text and adapter id. This function never
    discovers providers, activates adapters, fetches data, opens outcomes, or
    mutates the producer candidate. The existing acquisition firewall remains
    authoritative for whether a declared request is plan-ready.
    """

    specification, qualification = _validate_readiness(readiness)
    requirements = _explicit_requirements(specification)
    routes = list(declared_routes)
    hypothesis_id = str(readiness["hypothesis_id"])
    intents: List[Dict[str, Any]] = []

    for requirement in requirements:
        base = {
            "hypothesis_id": hypothesis_id,
            "requirement": requirement,
            "outcome_accessed": False,
            "economic_result": "NOT_OBSERVED",
            "network_execution_authorized": False,
        }
        if _forbidden_requirement(requirement):
            intents.append({**base, "status": "BLOCK_FORBIDDEN_REQUIREMENT", "blockers": ["FORBIDDEN_OUTCOME_LIKE_REQUIREMENT"], "request": None, "acquisition_plan": None})
            continue

        matches = _catalog_matches(requirement, routes)
        if not matches:
            intents.append({**base, "status": "UNRESOLVED_NO_DECLARED_ROUTE", "blockers": ["NO_EXACT_DECLARED_ROUTE"], "request": None, "acquisition_plan": None})
            continue
        if len(matches) != 1:
            intents.append({**base, "status": "BLOCK_AMBIGUOUS_DECLARED_ROUTE", "blockers": ["MULTIPLE_EXACT_DECLARED_ROUTES"], "request": None, "acquisition_plan": None})
            continue

        entry = matches[0]
        route_blockers = _validate_declared_route(entry)
        if route_blockers:
            intents.append({**base, "status": "BLOCK_INVALID_DECLARED_ROUTE", "blockers": route_blockers, "request": None, "acquisition_plan": None})
            continue

        adapter_id = entry["adapter_id"]
        adapter = validated_adapters.get(adapter_id)
        if adapter is None:
            intents.append({**base, "status": "UNRESOLVED_ADAPTER_NOT_DECLARED", "blockers": ["VALIDATED_ADAPTER_NOT_PRESENT:" + str(adapter_id)], "request": None, "acquisition_plan": None})
            continue

        requested_content = set(entry["content_classes"])
        if requested_content & FORBIDDEN_CONTENT_CLASSES:
            intents.append({**base, "status": "BLOCK_FORBIDDEN_CONTENT_CLASS", "blockers": ["FORBIDDEN_CONTENT_REQUESTED:" + item for item in sorted(requested_content & FORBIDDEN_CONTENT_CLASSES)], "request": None, "acquisition_plan": None})
            continue

        request = {
            "request_id": _request_id(hypothesis_id, requirement, entry, adapter),
            "entity_scope": deepcopy(entry["entity_scope"]),
            "content_classes": sorted(requested_content),
            "clock_cutoff": entry["clock_cutoff"],
            "version_policy": entry["version_policy"],
            "locator_parameters": deepcopy(entry.get("locator_parameters") or {}),
        }
        plan = build_acquisition_plan(adapter, request)
        status = "READY_PLAN_ONLY" if plan["status"] == "READY_AWAITING_SOURCE_ACTIVATION_AUTHORITY" else "BLOCK_FIREWALL"
        intents.append({
            **base,
            "status": status,
            "blockers": list(plan["blockers"]),
            "adapter_id": adapter_id,
            "adapter_hash": adapter.get("adapter_hash"),
            "declared_route_hash": sha256_json(entry),
            "request": request,
            "acquisition_plan": plan,
        })

    ready_count = sum(item["status"] == "READY_PLAN_ONLY" for item in intents)
    blocked_count = sum(item["status"].startswith("BLOCK") for item in intents)
    unresolved_count = sum(item["status"].startswith("UNRESOLVED") for item in intents)
    if not requirements:
        overall = "NO_EXPLICIT_DATA_REQUIREMENTS"
    elif blocked_count:
        overall = "BLOCK"
    elif ready_count == len(requirements):
        overall = "READY_PLAN_ONLY"
    else:
        overall = "INCOMPLETE_UNRESOLVED"

    payload = {
        "schema_version": "evidence-acquisition-intents.v2",
        "hypothesis_id": hypothesis_id,
        "readiness_hash": qualification["readiness_hash"],
        "requirements": requirements,
        "intents": intents,
        "summary": {
            "requirement_count": len(requirements),
            "ready_count": ready_count,
            "blocked_count": blocked_count,
            "unresolved_count": unresolved_count,
        },
        "status": overall,
        "projection_only": True,
        "network_execution_authorized": False,
        "network_call_performed": False,
        "outcome_accessed": False,
        "economic_result": "NOT_OBSERVED",
        "authority": dict(CLOSED_AUTHORITY),
    }
    return {**payload, "projection_hash": sha256_json(payload)}
