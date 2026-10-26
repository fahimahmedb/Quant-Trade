from __future__ import annotations

from copy import deepcopy
from math import isfinite
from typing import Any, Dict, List

_UNKNOWN = "UNKNOWN"
_UNQUALIFIED = {_UNKNOWN, "UNAVAILABLE", "UNSPECIFIED", "NOT_ESTIMATED",
                "CONFLICTED", "BLOCKED", "UNEXECUTED", "INVALIDATED_PROTOCOL"}
_REQUIRED_EXPRESSION_FIELDS = (
    "direction_exposure_semantics",
    "eligibility",
    "position_expression",
    "cost_model_requirements",
    "capacity_requirements",
    "data_requirements",
    "execution_assumptions",
    "falsification_relevant_implementation_conditions",
)


def _tri_state(value: Any) -> bool | str:
    if value is True:
        return True
    if value is False:
        return False
    return _UNKNOWN


def _known(value: Any) -> bool:
    if value is None or isinstance(value, bool):
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().upper() not in _UNQUALIFIED
    if isinstance(value, float):
        return isfinite(value)
    if isinstance(value, dict):
        return bool(value) and all(_known(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return bool(value) and all(_known(item) for item in value)
    return True


def _complexity(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return _UNKNOWN
    normalized = value.strip().upper()
    return normalized if normalized not in _UNQUALIFIED else _UNKNOWN


def _expression_diagnostics(meta: Dict[str, Any]) -> Dict[str, Any]:
    raw = meta.get("economic_expression")
    if not isinstance(raw, dict):
        return {
            "contract": None,
            "exact_expression_status": _UNKNOWN,
            "exact_clock_status": _UNKNOWN,
            "exact_universe_status": _UNKNOWN,
            "blocking_reasons": ["EXACT_EXPRESSION_CONTRACT_MISSING"],
        }

    contract = deepcopy(raw)
    reasons: List[str] = []

    has_universe = _known(contract.get("instrument")) or _known(contract.get("universe"))
    exact_universe_status = "PASS" if has_universe else "BLOCK"
    if not has_universe:
        reasons.append("EXACT_INSTRUMENT_OR_UNIVERSE_MISSING")

    has_entry = _known(contract.get("entry_clock"))
    has_exit = _known(contract.get("exit_clock")) or _known(contract.get("horizon"))
    exact_clock_status = "PASS" if has_entry and has_exit else "BLOCK"
    if not has_entry:
        reasons.append("EXACT_ENTRY_CLOCK_MISSING")
    if not has_exit:
        reasons.append("EXACT_EXIT_CLOCK_OR_HORIZON_MISSING")

    for field in _REQUIRED_EXPRESSION_FIELDS:
        if not _known(contract.get(field)):
            reasons.append(f"EXACT_{field.upper()}_MISSING")

    exact_expression_status = "PASS" if not reasons else "BLOCK"
    return {
        "contract": contract,
        "exact_expression_status": exact_expression_status,
        "exact_clock_status": exact_clock_status,
        "exact_universe_status": exact_universe_status,
        "blocking_reasons": reasons,
    }


def assess_implementability_depth(engine_output: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
    """Conservative implementability depth behind the existing interface.

    This function never opens economic outcomes or mutates CandidateHypothesis.
    ``implementability_status`` is the authoritative readiness decision. ``status``
    mirrors it onto the existing PASS/PARK/BLOCK surface used by downstream code.
    """

    candidate = engine_output["candidate"]
    candidate_before = deepcopy(candidate)

    source_available = _tri_state(meta.get("source_available"))
    pit_feasible = _tri_state(meta.get("pit_feasible"))
    expression_feasible = _tri_state(meta.get("expression_feasible"))
    cost_model_feasible = _tri_state(meta.get("cost_model_feasible"))
    capacity_observable = _tri_state(meta.get("capacity_observable"))
    operational_complexity = _complexity(meta.get("operational_complexity"))

    base_blockers: List[str] = []
    if source_available is False:
        base_blockers.append("SOURCE_UNAVAILABLE")
    elif source_available == _UNKNOWN:
        base_blockers.append("SOURCE_AVAILABILITY_UNKNOWN")
    if pit_feasible is False:
        base_blockers.append("PIT_NOT_QUALIFIED")
    elif pit_feasible == _UNKNOWN:
        base_blockers.append("PIT_FEASIBILITY_UNKNOWN")
    if expression_feasible is False:
        base_blockers.append("EXPRESSION_NOT_QUALIFIED")
    elif expression_feasible == _UNKNOWN:
        base_blockers.append("EXPRESSION_FEASIBILITY_UNKNOWN")
    if cost_model_feasible is False:
        base_blockers.append("COST_MODEL_NOT_QUALIFIED")
    elif cost_model_feasible == _UNKNOWN:
        base_blockers.append("COST_MODEL_FEASIBILITY_UNKNOWN")
    if capacity_observable is False:
        base_blockers.append("CAPACITY_NOT_OBSERVABLE")
    elif capacity_observable == _UNKNOWN:
        base_blockers.append("CAPACITY_OBSERVABILITY_UNKNOWN")

    expression = _expression_diagnostics(meta)
    blocking_reasons = list(base_blockers) + list(expression["blocking_reasons"])
    if operational_complexity == _UNKNOWN:
        blocking_reasons.append("OPERATIONAL_COMPLEXITY_UNKNOWN")
    blocking_reasons = sorted(set(blocking_reasons))

    structural_block = any(reason != "SOURCE_UNAVAILABLE" for reason in blocking_reasons)
    if not blocking_reasons:
        implementability_status = "IMPLEMENTABLE"
    elif source_available is False and not structural_block:
        implementability_status = "PARK_IMPLEMENTABILITY"
    else:
        implementability_status = "BLOCK_IMPLEMENTABILITY"

    status = {
        "IMPLEMENTABLE": "PASS",
        "PARK_IMPLEMENTABILITY": "PARK_IMPLEMENTABILITY",
        "BLOCK_IMPLEMENTABILITY": "BLOCK_IMPLEMENTABILITY",
    }[implementability_status]

    if candidate != candidate_before:
        raise AssertionError("implementability assessment mutated CandidateHypothesis")

    authority = {
        "economic_experiment_authorized": False,
        "prospective_observation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
    }

    return {
        "hypothesis_id": candidate["hypothesis_id"],
        "status": status,
        "implementability_status": implementability_status,
        "source_available": source_available,
        "pit_feasible": pit_feasible,
        "expression_feasible": expression_feasible,
        "cost_model_feasible": cost_model_feasible,
        "capacity_observable": capacity_observable,
        "operational_complexity": operational_complexity,
        "exact_expression_status": expression["exact_expression_status"],
        "exact_clock_status": expression["exact_clock_status"],
        "exact_universe_status": expression["exact_universe_status"],
        "exact_expression_contract": expression["contract"],
        "blocking_reasons": blocking_reasons,
        "blockers": blocking_reasons,
        "candidate_mutated": False,
        "mechanism_rewritten": False,
        "research_decision_rewritten": False,
        "authority": authority,
        **authority,
    }
