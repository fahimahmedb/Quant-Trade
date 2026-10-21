"""Pure Mega-A Research Intelligence chain orchestration.

No task creation, scheduler mutation, outcome access, or persistent-memory write occurs
here. Candidate admission remains owned by research_intelligence; this layer adds the
missing cross-candidate order: explicit hypothesis priority, explicit information value,
then admitted cost.
"""
from __future__ import annotations

from copy import deepcopy
import math
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .research_intelligence import classify_frontier, evaluate_search_space

UNKNOWN = "UNKNOWN"
CHAIN_VERSION = "MEGA_A_RESEARCH_CHAIN_V1"
FIXED_CHAIN = (
    "SCIENTIFIC_MEMORY", "ARCHAEOLOGY", "CURRENT_FRONTIER", "EVIDENCE_GAPS",
    "AVAILABLE_CAPABILITIES", "SEARCH_SPACE", "NOVELTY_DUP_CONTROL",
    "HYPOTHESIS_PRIORITY", "INFORMATION_VALUE", "COST_BUDGET_BLOCKER",
    "NEXT_ACTION", "FRONTIER_EXHAUSTION_NOOP", "FEEDBACK",
)
_ACTION_ORDER = {
    "ARCHAEOLOGY_LOOKUP": 0, "REUSE_EXISTING_EVIDENCE": 1, "REPAIR_PROTOCOL": 2,
    "ACQUIRE_EVIDENCE_INTENT": 3, "GENERATE_MECHANISM": 4, "RUN_PRODUCER": 5,
    "ESCALATE_VALIDATION": 6, "PARK": 7, "NO_BUILD": 8, "NO_ACTION": 9,
}
_OUTCOME_FIELDS = frozenset({
    "alpha", "pnl", "profit", "profitability", "return", "returns",
    "observed_return", "realized_return", "sharpe", "performance", "outcome",
})


def _number(value: Any) -> Optional[float]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    value = float(value)
    return value if math.isfinite(value) else None


def _count(value: Any) -> Any:
    if value is None:
        return UNKNOWN
    if isinstance(value, (Mapping, list, tuple, set, frozenset)):
        return len(value)
    return 1


def _ignored_outcome_fields(candidate: Mapping[str, Any]) -> List[str]:
    found = {str(k) for k in candidate if str(k).lower() in _OUTCOME_FIELDS}
    for action in candidate.get("actions") or []:
        if isinstance(action, Mapping):
            found.update(f"actions.{k}" for k in action if str(k).lower() in _OUTCOME_FIELDS)
    return sorted(found)


def _ranking(candidate: Mapping[str, Any], decision: Mapping[str, Any]) -> Dict[str, Any]:
    selected = decision.get("selected_action") or {}
    priority = _number(candidate.get("hypothesis_priority"))
    info = _number(candidate.get("information_value"))
    if info is None and isinstance(selected, Mapping):
        info = _number(selected.get("information_value"))
    cost = _number(selected.get("cost_units")) if isinstance(selected, Mapping) else None
    return {
        "hypothesis_priority": priority if priority is not None else UNKNOWN,
        "hypothesis_priority_source": "EXPLICIT_CANDIDATE_METADATA" if priority is not None else "UNKNOWN_NOT_INFERRED",
        "information_value": info if info is not None else UNKNOWN,
        "information_value_source": "EXPLICIT_RESEARCH_DESIGN_METADATA" if info is not None else "UNKNOWN_NOT_INFERRED",
        "cost_units": cost if cost is not None else UNKNOWN,
        "cost_source": "SELECTED_ADMITTED_ACTION" if cost is not None else "UNKNOWN_NOT_INFERRED",
        "outcome_fields_present_but_ignored": _ignored_outcome_fields(candidate),
    }


def _rank_key(item: Mapping[str, Any]) -> Tuple[Any, ...]:
    rank = item["research_ranking"]
    p, i, c = rank["hypothesis_priority"], rank["information_value"], rank["cost_units"]
    return (
        p == UNKNOWN, -float(p) if p != UNKNOWN else 0.0,
        i == UNKNOWN, -float(i) if i != UNKNOWN else 0.0,
        c == UNKNOWN, float(c) if c != UNKNOWN else 0.0,
        _ACTION_ORDER.get(str(item.get("action")), 99),
        str(item.get("candidate_id") or ""),
    )


def rank_research_decisions(
    decisions: Sequence[Mapping[str, Any]], candidates: Sequence[Mapping[str, Any]]
) -> Dict[str, Any]:
    """Rank admitted decisions; UNKNOWN remains symbolic and outcomes never score."""
    if len(decisions) != len(candidates):
        raise ValueError("decisions and candidates must preserve one-to-one search-space order")
    decorated: List[Dict[str, Any]] = []
    for decision, candidate in zip(decisions, candidates):
        item = deepcopy(dict(decision))
        item["research_ranking"] = _ranking(candidate, decision)
        decorated.append(item)
    executable = [
        d for d in decorated
        if d.get("executable") is True and d.get("action") not in {"NO_BUILD", "NO_ACTION", "PARK"}
    ]
    complete = bool(executable) and all(
        d["research_ranking"][field] != UNKNOWN
        for d in executable
        for field in ("hypothesis_priority", "information_value", "cost_units")
    )
    if not executable:
        selected = {
            "candidate_id": None, "action": "NO_ACTION", "executable": False,
            "reason_codes": ["NO_EXECUTABLE_RESEARCH_ACTION"], "scheduler_mutation": False,
        }
    else:
        selected = deepcopy(sorted(executable, key=_rank_key)[0])
        reasons = list(selected.get("reason_codes") or [])
        reasons.append("HYPOTHESIS_PRIORITY_THEN_INFORMATION_VALUE_THEN_COST")
        if not complete:
            reasons.append("RANKING_METADATA_INCOMPLETE_UNKNOWN_NOT_INFERRED")
        selected["reason_codes"] = list(dict.fromkeys(reasons))
        selected["scheduler_mutation"] = False
    return {
        "selected": selected, "decisions": decorated, "ranking_complete": complete,
        "ranking_contract": [
            "EXPLICIT_HYPOTHESIS_PRIORITY_DESC", "EXPLICIT_INFORMATION_VALUE_DESC",
            "ADMITTED_COST_ASC", "ACTION_CLASS_THEN_CANDIDATE_ID_TIEBREAK_ONLY",
        ],
        "scheduler_mutation": False, "outcome_accessed": False,
    }


def plan_research_chain(
    candidates: Sequence[Mapping[str, Any]], *,
    memory_records: Iterable[Mapping[str, Any]] = (), archaeology: Any,
    current_frontier: Any, evidence_gaps: Any,
    capability_registry: Optional[Mapping[str, Any]], workflow_lanes: Optional[Mapping[str, Any]],
    authority: Optional[Mapping[str, Any]] = None,
    budget_context: Optional[Mapping[str, Any]] = None,
    queue_active_count: int = 0, search_space_complete: bool = False,
    archaeology_complete: bool = False,
) -> Dict[str, Any]:
    """Produce one deterministic recommendation receipt for the fixed chain."""
    memory = list(memory_records)  # materialize once: generators are safe and deterministic
    required = {
        "archaeology": archaeology, "current_frontier": current_frontier,
        "evidence_gaps": evidence_gaps, "capability_registry": capability_registry,
        "workflow_lanes": workflow_lanes,
    }
    missing = sorted(k for k, v in required.items() if v is None)
    receipt = {
        "scientific_memory_records": len(memory), "archaeology": _count(archaeology),
        "current_frontier": _count(current_frontier), "evidence_gaps": _count(evidence_gaps),
        "capability_registry": "PRESENT" if capability_registry is not None else "MISSING",
        "workflow_lanes": "PRESENT" if workflow_lanes is not None else "MISSING",
        "authority_context": "PRESENT" if authority is not None else "MISSING_FAIL_CLOSED_BY_ADMISSION",
        "budget_context": "PRESENT" if budget_context is not None else "MISSING_FAIL_CLOSED_FOR_POSITIVE_COST",
        "missing_required_context": missing,
    }
    if missing:
        return {
            "version": CHAIN_VERSION, "fixed_chain": list(FIXED_CHAIN), "input_receipt": receipt,
            "decisions": [], "next_action": {
                "candidate_id": None, "action": "NO_ACTION", "executable": False,
                "reason_codes": ["CHAIN_CONTEXT_INCOMPLETE", *[f"MISSING_{k.upper()}" for k in missing]],
                "scheduler_mutation": False,
            },
            "frontier": {"state": "SEARCH_SPACE_INCOMPLETE", "scientifically_exhausted": False,
                         "basis": ["CHAIN_CONTEXT_INCOMPLETE", "QUEUE_EMPTY_IS_NOT_FRONTIER_EXHAUSTED"]},
            "ranking_complete": False, "scheduler_mutation": False, "outcome_accessed": False,
        }
    decisions = evaluate_search_space(
        candidates, memory_records=memory, capability_registry=capability_registry,
        workflow_lanes=workflow_lanes, authority=authority, budget_context=budget_context,
    )
    ranked = rank_research_decisions(decisions, candidates)
    frontier = classify_frontier(
        decisions, queue_active_count=queue_active_count,
        search_space_complete=search_space_complete, archaeology_complete=archaeology_complete,
    )
    return {
        "version": CHAIN_VERSION, "fixed_chain": list(FIXED_CHAIN), "input_receipt": receipt,
        "decisions": ranked["decisions"], "next_action": ranked["selected"],
        "ranking_complete": ranked["ranking_complete"], "ranking_contract": ranked["ranking_contract"],
        "frontier": frontier,
        "feedback": {"next_action_candidate_id": ranked["selected"].get("candidate_id"),
                     "frontier_state": frontier.get("state"), "persistent_memory_mutation": False},
        "scheduler_mutation": False, "outcome_accessed": False,
    }
