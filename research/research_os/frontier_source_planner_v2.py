from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Callable, Dict, Iterable, Mapping, Optional


TASK_FAMILY = {
    "FUNDAMENTAL_RESEARCH": "FUNDAMENTAL",
    "EVENT_DOCUMENT": "EVENT_DOCUMENT",
    "INSTITUTIONAL_FLOW": "INSTITUTIONAL_FLOW",
    "QUANT_MECHANISM": "QUANT_MECHANISM",
}

# Historical frontier tasks predate explicit source binding. These are the exact
# worker fallbacks they consumed/attempted, so they are conservatively treated
# as consumed for the same frontier rather than replayed under a new sequence.
LEGACY_DEFAULT_SOURCE = {
    "FUNDAMENTAL_RESEARCH": "research/research_os/sources/apple_fy2025_statement_cells.json",
    "EVENT_DOCUMENT": "research/research_os/sources/apple_dividend_announcements.json",
    "INSTITUTIONAL_FLOW": "research/research_os/sources/sec_t1_operative_rule.json",
}


def _canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def _default_qualifier(packet: Dict[str, Any], family: str, freeze_time: str) -> Dict[str, Any]:
    # Lazy import keeps the planner pure/lightweight for callers and avoids
    # creating an import cycle with worker orchestration.
    from .expansion.engine_dossiers_v1 import qualify_document_packet

    return qualify_document_packet(packet, family, freeze_time)


def _catalog_entry(path: str, value: Any) -> Dict[str, Any]:
    if isinstance(value, Mapping) and "record" in value:
        record = deepcopy(value["record"])
        blob_sha = value.get("blob_sha")
    else:
        record = deepcopy(value)
        blob_sha = None
    return {"path": str(path), "record": record, "blob_sha": blob_sha}


def _qualified_source(
    entry: Dict[str, Any],
    *,
    family: str,
    qualifier: Callable[[Dict[str, Any], str, str], Dict[str, Any]],
) -> Dict[str, Any]:
    record = entry["record"]
    if not isinstance(record, Mapping):
        return {"status": "REJECT", "reason": "SOURCE_RECORD_NOT_OBJECT"}
    # This mirrors documentary_candidate's wrapper contract before delegating
    # packet semantics to the authoritative existing qualifier.
    if set(record) != {"source_ref", "freeze_time", "documentary_packet"}:
        return {"status": "REJECT", "reason": "SOURCE_WRAPPER_FIELDS_INVALID"}
    packet = record.get("documentary_packet")
    if not isinstance(packet, Mapping):
        return {"status": "REJECT", "reason": "DOCUMENTARY_PACKET_MISSING"}
    if packet.get("evidence_class") != "DOCUMENTARY":
        return {"status": "REJECT", "reason": "NON_DOCUMENTARY_SOURCE"}
    if record.get("source_ref") != packet.get("source_ref"):
        return {"status": "REJECT", "reason": "SOURCE_REF_BINDING_MISMATCH"}
    try:
        result = qualifier(dict(packet), family, str(record["freeze_time"]))
    except Exception as exc:  # fail closed: source qualification is not best-effort
        return {"status": "REJECT", "reason": f"QUALIFIER_EXCEPTION:{type(exc).__name__}"}
    if result.get("status") != "PASS":
        return {
            "status": "REJECT",
            "reason": "QUALIFICATION_BLOCK:" + ",".join(result.get("blockers") or []),
        }
    packet_hash = packet.get("content_hash")
    if not isinstance(packet_hash, str) or not packet_hash:
        return {"status": "REJECT", "reason": "PACKET_HASH_MISSING"}
    return {
        "status": "PASS",
        "path": entry["path"],
        "blob_sha": entry.get("blob_sha"),
        "packet_hash": packet_hash,
        "record_hash": _canonical_hash(record),
        "source_ref": packet.get("source_ref"),
        "available_at": packet.get("available_at"),
        "family": family,
    }


def _consumed_bindings(
    tasks: Iterable[Dict[str, Any]], *, frontier_id: str, task_type: str
) -> Dict[str, set]:
    legacy_paths: set[str] = set()
    packet_bindings: set[tuple[str, str]] = set()
    blob_bindings: set[tuple[str, str]] = set()
    record_bindings: set[tuple[str, str]] = set()

    for task in tasks:
        derivation = task.get("derivation") or {}
        if derivation.get("frontier_id") != frontier_id:
            continue
        inputs = task.get("inputs") or {}
        path = inputs.get("documentary_source")
        if path:
            packet_hash = inputs.get("documentary_source_packet_hash")
            blob_sha = inputs.get("documentary_source_blob")
            record_hash = inputs.get("documentary_source_record_hash")
            if packet_hash:
                packet_bindings.add((path, str(packet_hash)))
            if blob_sha:
                blob_bindings.add((path, str(blob_sha)))
            if record_hash:
                record_bindings.add((path, str(record_hash)))
            if not any((packet_hash, blob_sha, record_hash)):
                legacy_paths.add(path)
            continue

        # Pre-planner frontier tasks used the worker's single hard-coded fallback.
        default = LEGACY_DEFAULT_SOURCE.get(task_type)
        if default:
            legacy_paths.add(default)

    return {
        "legacy_paths": legacy_paths,
        "packet_bindings": packet_bindings,
        "blob_bindings": blob_bindings,
        "record_bindings": record_bindings,
    }


def _is_consumed(source: Dict[str, Any], consumed: Dict[str, set]) -> bool:
    path = source["path"]
    if path in consumed["legacy_paths"]:
        return True
    if (path, source["packet_hash"]) in consumed["packet_bindings"]:
        return True
    if source.get("blob_sha") and (path, source["blob_sha"]) in consumed["blob_bindings"]:
        return True
    if (path, source["record_hash"]) in consumed["record_bindings"]:
        return True
    return False


def plan_frontier_source(
    *,
    frontier_entry: Mapping[str, Any],
    tasks: Iterable[Dict[str, Any]],
    source_catalog: Mapping[str, Any],
    qualifier: Optional[Callable[[Dict[str, Any], str, str], Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Select one unused engine-qualified documentary packet for a frontier.

    This function performs pre-outcome planning only. It executes no engine,
    acquires no data, reads no outcome, and mutates no state. Old pre-planner
    tasks are treated conservatively: their historical hard-coded fallback path
    is considered consumed because no durable source hash existed at that time.
    """

    task_type = str(frontier_entry.get("task_type") or "")
    frontier_id = str(frontier_entry.get("frontier_id") or "")
    family = TASK_FAMILY.get(task_type)
    if not frontier_id or not family:
        return {
            "status": "NO_ADMISSIBLE_DOCUMENTARY_SOURCE",
            "frontier_id": frontier_id or "UNKNOWN",
            "task_type": task_type or "UNKNOWN",
            "family": family,
            "qualified_count": 0,
            "unused_count": 0,
            "source": None,
            "rejections": [],
        }

    qualifier = qualifier or _default_qualifier
    consumed = _consumed_bindings(tasks, frontier_id=frontier_id, task_type=task_type)
    qualified = []
    rejections = []
    for path, raw in sorted(source_catalog.items()):
        entry = _catalog_entry(path, raw)
        decision = _qualified_source(entry, family=family, qualifier=qualifier)
        if decision["status"] == "PASS":
            qualified.append(decision)
        else:
            rejections.append({"path": path, "reason": decision["reason"]})

    unused = [source for source in qualified if not _is_consumed(source, consumed)]
    unused.sort(
        key=lambda source: (
            str(source.get("available_at") or ""),
            source["path"],
            source["packet_hash"],
        )
    )
    if not qualified:
        status = "NO_ADMISSIBLE_DOCUMENTARY_SOURCE"
        selected = None
    elif not unused:
        status = "NO_UNUSED_ADMISSIBLE_SOURCE"
        selected = None
    else:
        status = "SOURCE_SELECTED"
        selected = unused[0]

    return {
        "status": status,
        "frontier_id": frontier_id,
        "task_type": task_type,
        "family": family,
        "qualified_count": len(qualified),
        "unused_count": len(unused),
        "source": selected,
        "rejections": rejections,
    }
