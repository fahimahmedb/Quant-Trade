from __future__ import annotations

from typing import Any, Dict, List


def learning_telemetry(*, outputs: List[Dict[str, Any]], validations: List[Dict[str, Any]], red_team: Dict[str, Any]) -> Dict[str, Any]:
    resolved = sum(1 for v in validations if v["status"] in {"PASS", "BLOCK"})
    duplicate_warnings = sum(1 for p in red_team.get("pairwise", []) if p["relation"] != "INDEPENDENT")
    return {
        "telemetry_engine": "learning-telemetry.v0",
        "candidate_count": len(outputs),
        "resolved_validation_count": resolved,
        "duplicate_or_overlap_warning_count": duplicate_warnings,
        "known_attempts": len(outputs),
        "effective_trials_status": "UNKNOWN",
        "effective_trials": None,
        "time_to_falsification": "NOT_MEASURED_IN_SYNTHETIC_BUILD",
        "research_cost_per_resolved_decision": "NOT_MEASURED_IN_SYNTHETIC_BUILD",
        "prospective_survival": "NOT_APPLICABLE",
        "calibration": "NOT_MEASURED_IN_SYNTHETIC_BUILD",
    }
