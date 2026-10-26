"""Pure pre-outcome research-intelligence decision layer.

This module ranks *research actions*, not trades, returns, or portfolio choices.  It
does not mutate tasks, acquire sources, run producers, access outcomes, or schedule
work.  The Research Control Plane remains the sole orchestration authority.

Key safety properties:
* unknown semantic identity never becomes novelty;
* labels/paths/prompts do not define economic identity;
* canonical Scientific Memory can constrain search without becoming a second store;
* BLOCKED / UNEXECUTED / INVALIDATED_PROTOCOL remain distinct from NEGATIVE;
* evidence reuse is keyed by evidence identity, not file path;
* capability availability requires both an enabled capability and an active route;
* cheapest admissible falsifier wins before deeper work;
* queue-empty alone never means scientifically exhausted.
"""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .scientific_memory import (
    SCHEMA_VERSION as MEMORY_SCHEMA_VERSION,
    SCIENTIFIC_DISPOSITIONS,
    validate_memory_record,
)

UNKNOWN = "UNKNOWN"

ACTION_CLASSES = {
    "ARCHAEOLOGY_LOOKUP",
    "REUSE_EXISTING_EVIDENCE",
    "ACQUIRE_EVIDENCE_INTENT",
    "GENERATE_MECHANISM",
    "RUN_PRODUCER",
    "REPAIR_PROTOCOL",
    "ESCALATE_VALIDATION",
    "PARK",
    "NO_BUILD",
    "NO_ACTION",
}

FRONTIER_STATES = {
    "ACTIVE_ACTIONABLE",
    "ACTIVE_QUEUE",
    "DUPLICATE_ONLY",
    "SOURCE_MISSING",
    "CAPABILITY_MISSING",
    "BUDGET_BLOCKED",
    "EXTERNAL_ACCESS_BLOCKED",
    "AUTHORITY_SEALED",
    "TEMPORARILY_PARKED",
    "SCIENTIFICALLY_EXHAUSTED",
    "SEARCH_SPACE_INCOMPLETE",
}

CORE_IDENTITY_FIELDS = (
    "mechanism",
    "payer",
    "constrained_actor",
    "timing_clock",
    "universe",
    "economic_exposure",
)
AUX_IDENTITY_FIELDS = ("instrument", "source_family", "evidence_identity")
ALL_IDENTITY_FIELDS = CORE_IDENTITY_FIELDS + AUX_IDENTITY_FIELDS

_UNKNOWN_TOKENS = {"", "UNKNOWN", "NONE", "N/A", "NA", "UNSPECIFIED", "TBD"}


def _known(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool)) and str(value).strip().upper() not in _UNKNOWN_TOKENS


def _norm(value: Any) -> str:
    if not _known(value):
        return UNKNOWN
    text = str(value).strip().lower()
    text = re.sub(r"[\s_\-]+", " ", text)
    text = re.sub(r"[^\w\s:/+.]", "", text)
    return re.sub(r"\s+", " ", text).strip() or UNKNOWN


def _hash(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def semantic_identity(candidate: Mapping[str, Any]) -> Dict[str, str]:
    """Extract structured identity without using labels, paths, or prompts."""
    identity = candidate.get("identity") or {}
    aliases = {
        "actor": "constrained_actor",
        "clock": "timing_clock",
        "source": "source_family",
        "evidence": "evidence_identity",
        "exposure": "economic_exposure",
    }
    out: Dict[str, str] = {}
    for field in ALL_IDENTITY_FIELDS:
        raw = identity.get(field)
        if raw is None:
            for alias, canonical in aliases.items():
                if canonical == field and identity.get(alias) is not None:
                    raw = identity.get(alias)
                    break
        out[field] = _norm(raw)
    return out


def identity_complete(identity: Mapping[str, Any]) -> bool:
    return all(_norm(identity.get(field)) != UNKNOWN for field in CORE_IDENTITY_FIELDS)


def mechanism_key(identity: Mapping[str, Any]) -> Optional[str]:
    normalized = {field: _norm(identity.get(field)) for field in CORE_IDENTITY_FIELDS}
    if not identity_complete(normalized):
        return None
    return _hash(normalized)


def evidence_key(identity: Mapping[str, Any]) -> Optional[str]:
    evidence = _norm(identity.get("evidence_identity"))
    if evidence == UNKNOWN:
        return None
    return _hash({"evidence_identity": evidence})


def identity_explanation(identity: Mapping[str, Any]) -> Dict[str, Any]:
    missing = [field for field in CORE_IDENTITY_FIELDS if _norm(identity.get(field)) == UNKNOWN]
    return {
        "resolved": not missing,
        "missing_core_dimensions": missing,
        "mechanism_key": mechanism_key(identity),
        "evidence_key": evidence_key(identity),
        "dimensions": {field: _norm(identity.get(field)) for field in ALL_IDENTITY_FIELDS},
    }


def _memory_facets(record: Mapping[str, Any]) -> Dict[str, str]:
    facets = record.get("query_facets") or {}
    return {
        "mechanism": _norm(facets.get("mechanism")),
        "payer": _norm(facets.get("payer")),
        "constrained_actor": _norm(facets.get("constrained_actor")),
        "timing_clock": _norm(facets.get("timing_clock")),
        "universe": _norm(facets.get("universe")),
        "economic_exposure": _norm(facets.get("economic_exposure")),
        "instrument": _norm(facets.get("instrument")),
        "source_family": _norm(facets.get("source_family")),
        "evidence_identity": _norm(facets.get("evidence_identity")),
    }


def _qualified_memory(record: Mapping[str, Any]) -> Tuple[bool, str]:
    if record.get("schema_version") != MEMORY_SCHEMA_VERSION:
        return False, "MEMORY_SCHEMA_UNQUALIFIED"
    try:
        validate_memory_record(record, require_canonical=True)
    except (TypeError, ValueError) as exc:
        return False, f"MEMORY_RECORD_UNQUALIFIED:{exc}"
    if record.get("record_status") == "SUPERSEDED_WITH_PROOF":
        return False, "MEMORY_SUPERSEDED_WITH_PROOF"
    if record.get("scientific_disposition") not in SCIENTIFIC_DISPOSITIONS:
        return False, "MEMORY_DISPOSITION_UNQUALIFIED"
    return True, "MEMORY_QUALIFIED"


def memory_relation(candidate: Mapping[str, Any], record: Mapping[str, Any]) -> Dict[str, Any]:
    """Return deterministic structural relation; never empirical similarity."""
    qualified, qualification_reason = _qualified_memory(record)
    current = semantic_identity(candidate)
    observed = _memory_facets(record)
    matched: List[str] = []
    mismatched: List[str] = []
    unknown: List[str] = []

    for field in CORE_IDENTITY_FIELDS:
        a, b = current[field], observed[field]
        if UNKNOWN in {a, b}:
            unknown.append(field)
        elif a == b:
            matched.append(field)
        else:
            mismatched.append(field)

    same_family = qualified and not mismatched and not unknown
    ev_a, ev_b = current["evidence_identity"], observed["evidence_identity"]
    same_evidence = qualified and ev_a != UNKNOWN and ev_b != UNKNOWN and ev_a == ev_b

    return {
        "memory_id": record.get("memory_id"),
        "qualified": qualified,
        "qualification_reason": qualification_reason,
        "same_semantic_family": same_family,
        "same_evidence": same_evidence,
        "matched_core_dimensions": matched,
        "mismatched_core_dimensions": mismatched,
        "unknown_core_dimensions": unknown,
        "scientific_disposition": record.get("scientific_disposition") if qualified else None,
        "claim_ceiling": record.get("claim_ceiling") if qualified else None,
    }


def _lane_map(workflow_lanes: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    return {str(item.get("lane_id")): item for item in workflow_lanes.get("lanes", []) if item.get("lane_id")}


def capability_route_status(
    capability_id: Optional[str],
    target_lane: Optional[str],
    capability_registry: Mapping[str, Any],
    workflow_lanes: Mapping[str, Any],
) -> Dict[str, Any]:
    """Require enabled capability and a compatible active lane."""
    if not capability_id:
        return {"available": True, "state": "NOT_REQUIRED", "freshness": "NOT_REQUIRED"}

    caps = {
        str(item.get("capability_id")): item
        for item in capability_registry.get("capabilities", [])
        if item.get("capability_id")
    }
    cap = caps.get(str(capability_id))
    if not cap:
        return {"available": False, "state": "CAPABILITY_MISSING", "freshness": "UNKNOWN"}

    if cap.get("production_enabled") is not True or cap.get("route_active") is False:
        return {"available": False, "state": "CAPABILITY_INACTIVE", "freshness": "UNKNOWN"}

    freshness = str(cap.get("freshness", UNKNOWN)).upper()
    if cap.get("stale") is True or freshness == "STALE":
        return {"available": False, "state": "CAPABILITY_STALE", "freshness": "STALE"}

    lanes = _lane_map(workflow_lanes)
    lane = lanes.get(str(target_lane)) if target_lane else None
    if not lane:
        return {"available": False, "state": "ROUTE_MISSING", "freshness": freshness}
    if lane.get("enabled") is False or lane.get("active") is False:
        return {"available": False, "state": "ROUTE_INACTIVE", "freshness": freshness}
    if str(capability_id) not in set(lane.get("capabilities") or []):
        return {"available": False, "state": "ROUTE_CAPABILITY_MISMATCH", "freshness": freshness}
    return {"available": True, "state": "AVAILABLE", "freshness": freshness}


def _authority_status(action: Mapping[str, Any], authority: Mapping[str, Any]) -> Dict[str, Any]:
    required = list(action.get("requires_authority") or [])
    sealed = [key for key in required if authority.get(key) is not True]
    return {"admissible": not sealed, "required_authority": required, "sealed_authority": sealed}


def _budget_status(action: Mapping[str, Any], budget_context: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    cost = float(action.get("cost_units", 0) or 0)
    if cost <= 0:
        return {"admissible": True, "state": "ZERO_COST", "cost_units": cost}
    if budget_context is None:
        return {"admissible": False, "state": "BUDGET_UNKNOWN", "cost_units": cost}
    if budget_context.get("blocked") is True:
        return {"admissible": False, "state": "BUDGET_BLOCKED", "cost_units": cost}
    remaining = budget_context.get("remaining_units")
    if remaining is None:
        return {"admissible": False, "state": "BUDGET_UNKNOWN", "cost_units": cost}
    try:
        available = float(remaining)
    except (TypeError, ValueError):
        return {"admissible": False, "state": "BUDGET_UNKNOWN", "cost_units": cost}
    return {
        "admissible": cost <= available,
        "state": "WITHIN_BUDGET" if cost <= available else "BUDGET_EXCEEDED",
        "cost_units": cost,
        "remaining_units": available,
    }


def _explicit_blockers(candidate: Mapping[str, Any]) -> List[Dict[str, Any]]:
    blockers = []
    for raw in candidate.get("blockers") or []:
        item = dict(raw) if isinstance(raw, Mapping) else {"kind": str(raw)}
        status = str(item.get("status", "OPEN")).upper()
        if status not in {"RESOLVED", "CLOSED"}:
            blockers.append(item)
    return blockers


def _default_action(candidate: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "action": "RUN_PRODUCER",
        "cost_units": float(candidate.get("default_cost_units", 1) or 1),
        "depth": "WIDE",
        "is_falsifier": True,
        "falsification_power": "MEDIUM",
        "uncertainty_resolved": candidate.get("uncertainty") or "candidate mechanism admissibility",
        "required_capability": candidate.get("required_capability"),
        "target_lane": candidate.get("target_lane"),
        "requires_authority": list(candidate.get("required_authority") or []),
    }


def _candidate_actions(candidate: Mapping[str, Any]) -> List[Dict[str, Any]]:
    raw = candidate.get("actions")
    actions = [deepcopy(dict(item)) for item in raw or [] if isinstance(item, Mapping)]
    if not actions:
        actions = [_default_action(candidate)]
    for action in actions:
        if action.get("action") not in ACTION_CLASSES:
            raise ValueError(f"unsupported research action class: {action.get('action')}")
        action.setdefault("cost_units", 0)
        action.setdefault("depth", "WIDE")
        action.setdefault("is_falsifier", False)
        action.setdefault("falsification_power", "UNKNOWN")
        action.setdefault("uncertainty_resolved", candidate.get("uncertainty") or UNKNOWN)
        action.setdefault("required_capability", candidate.get("required_capability"))
        action.setdefault("target_lane", candidate.get("target_lane"))
        action.setdefault("requires_authority", list(candidate.get("required_authority") or []))
    return actions


def _admit_action(
    action: Mapping[str, Any],
    *,
    capability_registry: Mapping[str, Any],
    workflow_lanes: Mapping[str, Any],
    authority: Mapping[str, Any],
    budget_context: Optional[Mapping[str, Any]],
) -> Dict[str, Any]:
    capability = capability_route_status(
        action.get("required_capability"), action.get("target_lane"), capability_registry, workflow_lanes
    )
    authority_state = _authority_status(action, authority)
    budget = _budget_status(action, budget_context)
    depth = str(action.get("depth", "WIDE")).upper()
    deep_ok = depth != "DEEP" or bool(str(action.get("deep_justification", "")).strip())
    blockers: List[str] = []
    if not capability["available"]:
        blockers.append(capability["state"])
    if not authority_state["admissible"]:
        blockers.append("AUTHORITY_SEALED")
    if not budget["admissible"]:
        blockers.append(budget["state"])
    if not deep_ok:
        blockers.append("DEEP_ESCALATION_UNJUSTIFIED")
    return {
        "action": deepcopy(dict(action)),
        "admissible": not blockers,
        "blockers": blockers,
        "capability": capability,
        "authority": authority_state,
        "budget": budget,
        "depth_justified": deep_ok,
    }


def _action_sort_key(admitted: Mapping[str, Any]) -> Tuple[int, float, int, str]:
    action = admitted["action"]
    falsifier_rank = 0 if action.get("is_falsifier") is True else 1
    cost = float(action.get("cost_units", 0) or 0)
    depth_rank = 0 if str(action.get("depth", "WIDE")).upper() == "WIDE" else 1
    return falsifier_rank, cost, depth_rank, str(action.get("action"))


def _terminal_decision(
    action: str,
    reason: str,
    *,
    candidate: Mapping[str, Any],
    identity: Mapping[str, Any],
    memory: Sequence[Mapping[str, Any]],
    blockers: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    return {
        "candidate_id": candidate.get("candidate_id") or candidate.get("hypothesis_id"),
        "action": action,
        "executable": False,
        "reason_codes": [reason],
        "identity": identity_explanation(identity),
        "memory_influence": [deepcopy(dict(item)) for item in memory],
        "blockers": list(blockers or []),
        "uncertainty_resolved": None,
        "selection_trace": [],
        "scheduler_mutation": False,
    }


def decide_candidate(
    candidate: Mapping[str, Any],
    *,
    memory_records: Iterable[Mapping[str, Any]] = (),
    capability_registry: Optional[Mapping[str, Any]] = None,
    workflow_lanes: Optional[Mapping[str, Any]] = None,
    authority: Optional[Mapping[str, Any]] = None,
    budget_context: Optional[Mapping[str, Any]] = None,
    prior_candidates: Iterable[Mapping[str, Any]] = (),
) -> Dict[str, Any]:
    """Choose the next pre-outcome research action without creating a task."""
    registry = capability_registry or {"capabilities": []}
    lanes = workflow_lanes or {"lanes": []}
    authority_state = dict(authority or {})
    identity = semantic_identity(candidate)
    memory = list(memory_records)
    relations = [memory_relation(candidate, record) for record in memory]
    qualified = [rel for rel in relations if rel["qualified"]]
    same_family = [rel for rel in qualified if rel["same_semantic_family"]]

    if not identity_complete(identity):
        action = {
            "action": "ARCHAEOLOGY_LOOKUP",
            "cost_units": 0,
            "depth": "WIDE",
            "is_falsifier": True,
            "falsification_power": "HIGH",
            "uncertainty_resolved": "semantic identity dimensions",
        }
        return {
            "candidate_id": candidate.get("candidate_id") or candidate.get("hypothesis_id"),
            "action": "ARCHAEOLOGY_LOOKUP",
            "executable": True,
            "reason_codes": ["SEMANTIC_IDENTITY_UNRESOLVED", "UNKNOWN_IDENTITY_IS_NOT_NOVELTY"],
            "identity": identity_explanation(identity),
            "memory_influence": qualified,
            "blockers": [],
            "uncertainty_resolved": action["uncertainty_resolved"],
            "selected_action": action,
            "selection_trace": ["resolve identity before novelty classification"],
            "scheduler_mutation": False,
        }

    this_key = mechanism_key(identity)
    for prior in prior_candidates:
        prior_identity = semantic_identity(prior)
        if this_key and mechanism_key(prior_identity) == this_key:
            return _terminal_decision(
                "NO_BUILD", "DUPLICATE_CURRENT_SEARCH_SPACE", candidate=candidate, identity=identity, memory=qualified
            )

    dispositions = {str(rel.get("scientific_disposition")) for rel in same_family}
    if "NEGATIVE" in dispositions:
        return _terminal_decision(
            "NO_BUILD", "KNOWN_NEGATIVE_SAME_SEMANTIC_FAMILY", candidate=candidate, identity=identity, memory=same_family
        )

    if "INVALIDATED_PROTOCOL" in dispositions:
        record_ids = {
            _norm((record.get("identity") or {}).get("protocol_id"))
            for record in memory
            if memory_relation(candidate, record).get("same_semantic_family")
            and record.get("scientific_disposition") == "INVALIDATED_PROTOCOL"
        }
        proposed_protocol = _norm(candidate.get("protocol_id") or (candidate.get("identity") or {}).get("protocol_id"))
        if proposed_protocol == UNKNOWN or proposed_protocol in record_ids:
            return {
                **_terminal_decision(
                    "REPAIR_PROTOCOL",
                    "INVALIDATED_PROTOCOL_MUST_CHANGE_BEFORE_RERUN",
                    candidate=candidate,
                    identity=identity,
                    memory=same_family,
                ),
                "executable": True,
                "uncertainty_resolved": "protocol validity",
            }

    if "BLOCKED" in dispositions and candidate.get("memory_blockers_resolved") is not True:
        return _terminal_decision(
            "PARK",
            "HISTORICAL_BLOCKER_UNRESOLVED_NOT_NEGATIVE",
            candidate=candidate,
            identity=identity,
            memory=same_family,
            blockers=["MEMORY_BLOCKED_UNRESOLVED"],
        )

    if candidate.get("external_access_required") is True and candidate.get("external_access_available") is not True:
        return _terminal_decision(
            "PARK",
            "EXTERNAL_ACCESS_REQUIRED",
            candidate=candidate,
            identity=identity,
            memory=same_family,
            blockers=["EXTERNAL_ACCESS_BLOCKED"],
        )

    open_blockers = _explicit_blockers(candidate)
    if open_blockers:
        kinds = [str(item.get("kind", "OPEN_BLOCKER")).upper() for item in open_blockers]
        return _terminal_decision(
            "PARK", "OPEN_BLOCKER", candidate=candidate, identity=identity, memory=same_family, blockers=kinds
        )

    evidence_relations = [rel for rel in qualified if rel["same_evidence"]]
    if evidence_relations and candidate.get("evidence_reuse_admissible") is True:
        return {
            "candidate_id": candidate.get("candidate_id") or candidate.get("hypothesis_id"),
            "action": "REUSE_EXISTING_EVIDENCE",
            "executable": True,
            "reason_codes": ["QUALIFIED_EVIDENCE_ALREADY_EXISTS", "PATH_RENAME_DOES_NOT_CREATE_EVIDENCE"],
            "identity": identity_explanation(identity),
            "memory_influence": evidence_relations,
            "blockers": [],
            "uncertainty_resolved": candidate.get("uncertainty") or "existing evidence applicability",
            "selected_action": {"action": "REUSE_EXISTING_EVIDENCE", "cost_units": 0, "depth": "WIDE"},
            "selection_trace": ["reuse qualified evidence before acquisition"],
            "scheduler_mutation": False,
        }

    if "POSITIVE_BUT_INSUFFICIENT" in dispositions:
        candidate = deepcopy(dict(candidate))
        candidate["actions"] = [
            action for action in _candidate_actions(candidate)
            if action.get("action") in {"ESCALATE_VALIDATION", "ARCHAEOLOGY_LOOKUP", "REUSE_EXISTING_EVIDENCE"}
        ] or [{
            "action": "ESCALATE_VALIDATION",
            "cost_units": 0,
            "depth": "WIDE",
            "is_falsifier": True,
            "falsification_power": "HIGH",
            "uncertainty_resolved": "whether positive-but-insufficient evidence survives independent challenge",
            "required_capability": "validator",
            "target_lane": "independent_challenge",
        }]

    admitted = [
        _admit_action(
            action,
            capability_registry=registry,
            workflow_lanes=lanes,
            authority=authority_state,
            budget_context=budget_context,
        )
        for action in _candidate_actions(candidate)
    ]
    admissible = [item for item in admitted if item["admissible"]]
    if not admissible:
        all_blockers = sorted({blocker for item in admitted for blocker in item["blockers"]})
        if any(blocker == "AUTHORITY_SEALED" for blocker in all_blockers):
            reason = "AUTHORITY_SEALED"
        elif any(blocker.startswith("BUDGET_") for blocker in all_blockers):
            reason = "BUDGET_BLOCKED"
        elif any(blocker.startswith(("CAPABILITY_", "ROUTE_")) for blocker in all_blockers):
            reason = "CAPABILITY_OR_ROUTE_BLOCKED"
        else:
            reason = "NO_ADMISSIBLE_ACTION"
        return _terminal_decision(
            "PARK", reason, candidate=candidate, identity=identity, memory=same_family, blockers=all_blockers
        )

    chosen = sorted(admissible, key=_action_sort_key)[0]
    selected = chosen["action"]
    reason_codes = ["CHEAPEST_ADMISSIBLE_FALSIFIER_FIRST" if selected.get("is_falsifier") else "ADMISSIBLE_RESEARCH_ACTION"]
    if "UNEXECUTED" in dispositions:
        reason_codes.append("HISTORICAL_UNEXECUTED_IS_NOT_FAILURE")
    if "BLOCKED" in dispositions:
        reason_codes.append("HISTORICAL_BLOCKER_RESOLVED_REOPENED")
    if "POSITIVE_BUT_INSUFFICIENT" in dispositions:
        reason_codes.append("POSITIVE_BUT_INSUFFICIENT_NOT_PROMOTED")
    return {
        "candidate_id": candidate.get("candidate_id") or candidate.get("hypothesis_id"),
        "action": selected["action"],
        "executable": True,
        "reason_codes": reason_codes,
        "identity": identity_explanation(identity),
        "memory_influence": same_family,
        "blockers": [],
        "uncertainty_resolved": selected.get("uncertainty_resolved"),
        "selected_action": deepcopy(dict(selected)),
        "selection_trace": [
            {
                "action": item["action"].get("action"),
                "admissible": item["admissible"],
                "blockers": item["blockers"],
                "cost_units": item["action"].get("cost_units", 0),
                "is_falsifier": item["action"].get("is_falsifier", False),
                "depth": item["action"].get("depth", "WIDE"),
            }
            for item in sorted(admitted, key=lambda x: str(x["action"].get("action")))
        ],
        "scheduler_mutation": False,
    }


def evaluate_search_space(
    candidates: Sequence[Mapping[str, Any]],
    *,
    memory_records: Iterable[Mapping[str, Any]] = (),
    capability_registry: Optional[Mapping[str, Any]] = None,
    workflow_lanes: Optional[Mapping[str, Any]] = None,
    authority: Optional[Mapping[str, Any]] = None,
    budget_context: Optional[Mapping[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Evaluate deterministically; first semantic identity owns duplicate precedence."""
    decisions: List[Dict[str, Any]] = []
    prior: List[Mapping[str, Any]] = []
    memory = list(memory_records)
    for candidate in candidates:
        decisions.append(
            decide_candidate(
                candidate,
                memory_records=memory,
                capability_registry=capability_registry,
                workflow_lanes=workflow_lanes,
                authority=authority,
                budget_context=budget_context,
                prior_candidates=prior,
            )
        )
        prior.append(candidate)
    return decisions


def classify_frontier(
    decisions: Sequence[Mapping[str, Any]],
    *,
    queue_active_count: int,
    search_space_complete: bool = False,
    archaeology_complete: bool = False,
) -> Dict[str, Any]:
    """Classify frontier state without equating queue-empty with exhaustion."""
    if queue_active_count > 0:
        return {"state": "ACTIVE_QUEUE", "scientifically_exhausted": False}

    if any(item.get("executable") is True and item.get("action") not in {"NO_BUILD", "NO_ACTION"} for item in decisions):
        return {"state": "ACTIVE_ACTIONABLE", "scientifically_exhausted": False}

    reasons = {reason for item in decisions for reason in item.get("reason_codes", [])}
    blockers = {blocker for item in decisions for blocker in item.get("blockers", [])}

    if decisions and all(item.get("action") == "NO_BUILD" for item in decisions):
        return {"state": "DUPLICATE_ONLY", "scientifically_exhausted": False}
    if "EXTERNAL_ACCESS_BLOCKED" in blockers or "EXTERNAL_ACCESS_REQUIRED" in reasons:
        return {"state": "EXTERNAL_ACCESS_BLOCKED", "scientifically_exhausted": False}
    if "AUTHORITY_SEALED" in blockers or "AUTHORITY_SEALED" in reasons:
        return {"state": "AUTHORITY_SEALED", "scientifically_exhausted": False}
    if any(b in blockers for b in {"BUDGET_BLOCKED", "BUDGET_EXCEEDED", "BUDGET_UNKNOWN"}) or "BUDGET_BLOCKED" in reasons:
        return {"state": "BUDGET_BLOCKED", "scientifically_exhausted": False}
    if any(b.startswith(("CAPABILITY_", "ROUTE_")) for b in blockers):
        return {"state": "CAPABILITY_MISSING", "scientifically_exhausted": False}
    if any("SOURCE" in b for b in blockers):
        return {"state": "SOURCE_MISSING", "scientifically_exhausted": False}
    if decisions and any(item.get("action") == "PARK" for item in decisions):
        return {"state": "TEMPORARILY_PARKED", "scientifically_exhausted": False}

    if not decisions and search_space_complete and archaeology_complete:
        return {
            "state": "SCIENTIFICALLY_EXHAUSTED",
            "scientifically_exhausted": True,
            "basis": ["NO_CANDIDATES", "SEARCH_SPACE_COMPLETE", "ARCHAEOLOGY_COMPLETE", "NO_OPEN_DEPENDENCY"],
        }
    return {
        "state": "SEARCH_SPACE_INCOMPLETE",
        "scientifically_exhausted": False,
        "basis": ["QUEUE_EMPTY_IS_NOT_FRONTIER_EXHAUSTED"],
    }


def choose_next_action(decisions: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Choose among evaluated decisions without creating a Control Plane task."""
    executable = [
        item for item in decisions
        if item.get("executable") is True and item.get("action") not in {"NO_BUILD", "NO_ACTION"}
    ]
    if not executable:
        return {
            "action": "NO_ACTION",
            "candidate_id": None,
            "reason_codes": ["NO_EXECUTABLE_RESEARCH_ACTION"],
            "scheduler_mutation": False,
        }

    action_order = {
        "ARCHAEOLOGY_LOOKUP": 0,
        "REUSE_EXISTING_EVIDENCE": 1,
        "REPAIR_PROTOCOL": 2,
        "ACQUIRE_EVIDENCE_INTENT": 3,
        "GENERATE_MECHANISM": 4,
        "RUN_PRODUCER": 5,
        "ESCALATE_VALIDATION": 6,
    }
    ordered = sorted(
        executable,
        key=lambda item: (
            float((item.get("selected_action") or {}).get("cost_units", 0) or 0),
            action_order.get(str(item.get("action")), 99),
            str(item.get("candidate_id") or ""),
        ),
    )
    chosen = deepcopy(dict(ordered[0]))
    chosen["scheduler_mutation"] = False
    return chosen
