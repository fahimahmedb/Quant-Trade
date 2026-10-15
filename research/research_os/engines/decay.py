from __future__ import annotations

from typing import Any, Dict


def decay_monitor(shadow: Dict[str, Any]) -> Dict[str, Any]:
    authorized = shadow.get("prospective_observation_authorized") is True
    any_started = any(r.get("observation_started") is True for r in shadow.get("registrations", []))
    if not authorized or not any_started:
        return {
            "decay_monitor": "decay-monitor.v0",
            "status": "INACTIVE_BY_AUTHORITY",
            "observations_consumed": 0,
            "decay_assessment": "NOT_APPLICABLE",
        }
    raise RuntimeError("development build must not consume prospective observations")
