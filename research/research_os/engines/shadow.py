from __future__ import annotations

from typing import Any, Dict, List


def shadow_register(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    registrations = []
    for output in candidates:
        c = output["candidate"]
        registrations.append({
            "hypothesis_id": c["hypothesis_id"],
            "generation_id": c["generation_id"],
            "prospective_contract_status": "DRAFT_ONLY",
            "evidence_timing": c.get("evidence_timing", "UNDETERMINED"),
            "prospective_integrity": "NOT_ASSESSED",
            "observation_authorization": "NOT_AUTHORIZED",
            "observation_started": False,
        })
    return {
        "shadow_registry": "shadow-registry.v0",
        "prospective_observation_authorized": False,
        "registrations": registrations,
    }
