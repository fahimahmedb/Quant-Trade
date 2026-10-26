from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

from .frontier_source_planner_v2 import plan_frontier_source


ACTIVE_STATUSES = {"READY", "CLAIMED"}
TERMINAL_STATUSES = {"COMPLETE", "BLOCKED", "FAILED", "CANCELLED", "KILLED"}
SOURCE_PREFIX = "research/research_os/sources/"


def _canonical_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_frontier(base: Path) -> Dict[str, Any]:
    return json.loads((base / "runtime" / "RESEARCH_FRONTIER.json").read_text())


def load_tasks(base: Path) -> List[Dict[str, Any]]:
    tasks: List[Dict[str, Any]] = []
    for path in sorted((base / "tasks").glob("*.json")):
        tasks.append(json.loads(path.read_text()))
    return tasks


def load_source_catalog(base: Path) -> Dict[str, Any]:
    """Load only root source JSON records; qualification decides admissibility.

    Capture-support JSON may be present in the same directory. It is deliberately
    not pre-classified here: the source planner rejects anything that does not
    satisfy the authoritative documentary wrapper + family contract.
    """
    catalog: Dict[str, Any] = {}
    for path in sorted((base / "sources").glob("*.json")):
        try:
            record = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        catalog[SOURCE_PREFIX + path.name] = {"record": record}
    return catalog


def queue_summary(tasks: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    items = list(tasks)
    return {
        "task_count": len(items),
        "ready_count": sum(item.get("status") == "READY" for item in items),
        "claimed_count": sum(item.get("status") == "CLAIMED" for item in items),
        "active_count": sum(item.get("status") in ACTIVE_STATUSES for item in items),
        "terminal_count": sum(item.get("status") in TERMINAL_STATUSES for item in items),
        "unknown_count": sum(item.get("status") not in ACTIVE_STATUSES | TERMINAL_STATUSES for item in items),
    }


def _issued_counts(tasks: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for task in tasks:
        derivation = task.get("derivation") or {}
        frontier_id = derivation.get("frontier_id")
        if frontier_id:
            counts[frontier_id] = counts.get(frontier_id, 0) + 1
    return counts


def _existing_derivation_keys(tasks: Iterable[Dict[str, Any]]) -> set[str]:
    return {
        str((task.get("derivation") or {}).get("derivation_key"))
        for task in tasks
        if (task.get("derivation") or {}).get("derivation_key")
    }


def _safe_authority(frontier: Dict[str, Any]) -> Dict[str, Any]:
    authority = deepcopy(frontier.get("authority") or {})
    required_false = (
        "economic_experiment_authorized",
        "prospective_observation_authorized",
        "real_capital_authorized",
        "live_trading_authorized",
    )
    if any(authority.get(key) is not False for key in required_false):
        raise ValueError("frontier authority boundary is unsafe")
    return authority


def _source_plan_summary(plan: Mapping[str, Any]) -> Dict[str, Any]:
    source = plan.get("source") or {}
    return {
        "status": plan.get("status"),
        "qualified_count": plan.get("qualified_count", 0),
        "unused_count": plan.get("unused_count", 0),
        "source": ({
            "path": source.get("path"),
            "blob_sha": source.get("blob_sha"),
            "packet_hash": source.get("packet_hash"),
            "record_hash": source.get("record_hash"),
        } if source else None),
    }


def derive_refill_task(
    *,
    frontier: Dict[str, Any],
    tasks: Iterable[Dict[str, Any]],
    created_at: str,
    source_catalog: Optional[Mapping[str, Any]] = None,
    source_qualifier=None,
) -> Dict[str, Any]:
    """Derive at most one bounded producer task from Owner-governed frontier state.

    This function never executes research. When a source catalog is supplied,
    only a frontier with one unused engine-qualified documentary packet can be
    scheduled. Sequence numbers alone therefore cannot manufacture scientific
    novelty. Existing direct callers that do not supply a catalog retain legacy
    derivation behavior; production workers and derive_from_repo supply one.
    """

    items = list(tasks)
    summary = queue_summary(items)
    if frontier.get("status") != "ACTIVE":
        return {"status": "NOOP_FRONTIER_INACTIVE", "queue": summary, "task": None}
    if frontier.get("require_global_queue_empty") is not True:
        raise ValueError("research frontier must require a globally empty queue")
    if frontier.get("max_new_tasks_per_refill") != 1:
        raise ValueError("queue refill must be bounded to one task")
    if frontier.get("producer_execution_same_refill_wake") is not False:
        raise ValueError("producer work may not execute in the refill wake")
    if frontier.get("recursive_refill_same_wake") is not False:
        raise ValueError("recursive refill is forbidden")
    authority = _safe_authority(frontier)

    # An unsupported task state has no qualified scheduling meaning. Preserve
    # it for reconciliation instead of treating it as an empty queue.
    if summary["unknown_count"]:
        return {"status": "BLOCKED_UNKNOWN_TASK_STATUS", "queue": summary, "task": None}

    if summary["active_count"] > 0:
        return {"status": "NOOP_QUEUE_NOT_EMPTY", "queue": summary, "task": None}

    issued = _issued_counts(items)
    max_issued = int(frontier.get("max_issued_per_frontier", 0))
    eligible = [
        entry
        for entry in frontier.get("frontiers", [])
        if entry.get("enabled") is True and issued.get(entry["frontier_id"], 0) < max_issued
    ]
    if not eligible:
        return {"status": "NOOP_FRONTIER_EXHAUSTED", "queue": summary, "task": None}

    source_plans: Dict[str, Dict[str, Any]] = {}
    if source_catalog is not None:
        source_eligible = []
        for entry in eligible:
            plan = plan_frontier_source(
                frontier_entry=entry,
                tasks=items,
                source_catalog=source_catalog,
                qualifier=source_qualifier,
            )
            source_plans[entry["frontier_id"]] = plan
            if plan.get("status") == "SOURCE_SELECTED":
                source_eligible.append(entry)
        if not source_eligible:
            return {
                "status": "NOOP_NO_ADMISSIBLE_NOVEL_SOURCE",
                "queue": summary,
                "source_plans": {key: _source_plan_summary(value) for key, value in sorted(source_plans.items())},
                "task": None,
            }
        eligible = source_eligible

    eligible.sort(
        key=lambda entry: (
            issued.get(entry["frontier_id"], 0),
            -int(entry.get("priority", 0)),
            entry["frontier_id"],
        )
    )
    selected = eligible[0]
    selected_plan = source_plans.get(selected["frontier_id"])
    selected_source = (selected_plan or {}).get("source")
    sequence = issued.get(selected["frontier_id"], 0) + 1
    derivation_payload = {
        "schema_version": frontier.get("schema_version"),
        "frontier_id": selected["frontier_id"],
        "sequence": sequence,
        "task_type": selected["task_type"],
        "required_capability": selected["required_capability"],
        "target_lane": selected["target_lane"],
        "objective": selected["objective"],
    }
    if selected_source:
        derivation_payload["source_binding"] = {
            "path": selected_source["path"],
            "blob_sha": selected_source.get("blob_sha"),
            "packet_hash": selected_source["packet_hash"],
            "record_hash": selected_source["record_hash"],
        }
    derivation_key = _canonical_hash(derivation_payload)
    if derivation_key in _existing_derivation_keys(items):
        return {
            "status": "NOOP_DERIVATION_ALREADY_EXISTS",
            "queue": summary,
            "derivation_key": derivation_key,
            "task": None,
        }

    short = selected["frontier_id"].replace("_", "-")
    task_id = f"FRONTIER-{short}-{sequence:03d}"
    inputs = {
        "objective": selected["objective"],
        "frontier_id": selected["frontier_id"],
        "derivation_key": derivation_key,
        "legacy_gate_required": frontier.get("require_legacy_screen_before_freeze") is True,
        "causal_distinctness_required": True,
        "source_policy": "PUBLIC_OR_EXPLICITLY_AUTHORIZED_NON_OUTCOME_SOURCES_ONLY",
    }
    source_binding = None
    if selected_source:
        source_binding = {
            "path": selected_source["path"],
            "blob_sha": selected_source.get("blob_sha"),
            "packet_hash": selected_source["packet_hash"],
            "record_hash": selected_source["record_hash"],
        }
        inputs.update({
            "documentary_source": selected_source["path"],
            "documentary_source_blob": selected_source.get("blob_sha"),
            "documentary_source_packet_hash": selected_source["packet_hash"],
            "documentary_source_record_hash": selected_source["record_hash"],
        })

    task = {
        "task_id": task_id,
        "task_type": selected["task_type"],
        "required_capability": selected["required_capability"],
        "status": "READY",
        "priority": int(selected.get("priority", 70)),
        "inputs": inputs,
        "allowed_actions": list(selected.get("allowed_actions") or []),
        "forbidden_actions": list(selected.get("forbidden_actions") or []),
        "success_condition": selected["success_condition"],
        "authority": {
            "scope": "BOUNDED_FRONTIER_DISCOVERY_AND_FREEZE_ONLY",
            **authority,
        },
        "lease": {
            "generation": 0,
            "owner": None,
            "claimed_at": None,
            "expires_at": None,
        },
        "created_at": created_at,
        "updated_at": created_at,
        "derivation": {
            "type": "EMPTY_QUEUE_FRONTIER_REFILL",
            "frontier_id": selected["frontier_id"],
            "sequence": sequence,
            "derivation_key": derivation_key,
            "selection_policy": frontier.get("selection_policy"),
            "target_lane": selected["target_lane"],
            "steward_lane": "integrator_portfolio",
            **({"source_binding": source_binding} if source_binding else {}),
        },
    }

    validate_derived_task(task)
    return {
        "status": "DERIVED_ONE_READY_TASK",
        "queue": summary,
        "selected_frontier": selected["frontier_id"],
        "derivation_key": derivation_key,
        **({"source_plan": _source_plan_summary(selected_plan)} if selected_plan else {}),
        "task": task,
    }


def validate_source_binding(task: Mapping[str, Any]) -> None:
    """Verify the source selection survives in task inputs, at any lease state.

    Historical tasks without explicit source selection remain supported. A
    source-aware refill cannot silently shed its binding and use that fallback.
    This checks selection integrity; it does not qualify source contents.
    """
    inputs = task.get("inputs") or {}
    derivation = task.get("derivation") or {}
    binding = derivation.get("source_binding")
    source_fields = ("documentary_source", "documentary_source_blob",
                     "documentary_source_packet_hash", "documentary_source_record_hash")
    required = ("source_binding" in derivation or
                (derivation.get("type") == "EMPTY_QUEUE_FRONTIER_REFILL"
                 and any(key in inputs for key in source_fields)))
    if not required:
        return
    if not isinstance(binding, Mapping) or not binding:
        raise ValueError("derived source binding missing or invalid")
    path = inputs.get("documentary_source")
    if not isinstance(path, str) or not path.startswith(SOURCE_PREFIX):
        raise ValueError("derived source path is outside documentary source store")
    if path != binding.get("path"):
        raise ValueError("derived source path binding mismatch")
    for field in ("packet_hash", "record_hash"):
        if not isinstance(binding.get(field), str) or not binding[field]:
            raise ValueError("derived source " + field + " missing")
        if inputs.get("documentary_source_" + field) != binding[field]:
            raise ValueError("derived source " + field + " binding mismatch")
    if inputs.get("documentary_source_blob") != binding.get("blob_sha"):
        raise ValueError("derived source blob binding mismatch")


def validate_derived_task(task: Dict[str, Any]) -> None:
    if task.get("status") != "READY":
        raise ValueError("derived task must start READY")
    if (task.get("lease") or {}).get("generation") != 0:
        raise ValueError("derived task lease generation must start at zero")
    if (task.get("lease") or {}).get("owner") is not None:
        raise ValueError("derived task may not be pre-claimed")
    authority = task.get("authority") or {}
    for key in (
        "economic_experiment_authorized",
        "prospective_observation_authorized",
        "real_capital_authorized",
        "live_trading_authorized",
    ):
        if authority.get(key) is not False:
            raise ValueError(f"unsafe derived task authority: {key}")
    inputs = task.get("inputs", {})
    if inputs.get("legacy_gate_required") is not True:
        raise ValueError("derived discovery task must require Legacy screening")
    validate_source_binding(task)
    forbidden = " ".join(task.get("forbidden_actions") or []).lower()
    if "backtest" not in forbidden:
        raise ValueError("derived discovery task must explicitly forbid backtests")
    if "capital" not in forbidden or "live trading" not in forbidden:
        raise ValueError("derived discovery task must explicitly forbid capital and live trading")


def derive_from_repo(base: Path, *, created_at: str) -> Dict[str, Any]:
    return derive_refill_task(
        frontier=load_frontier(base),
        tasks=load_tasks(base),
        created_at=created_at,
        source_catalog=load_source_catalog(base),
    )
