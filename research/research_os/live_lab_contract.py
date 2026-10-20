"""Truth-preserving UI metadata for Oracle Research OS live events.

This module does not create work, progress, decisions, economic results or authority.
It only labels an already-authorized canonical stage for the Live Lab renderer.
Unknown lanes fail closed. Unknown stages render with no business gesture.
"""
from __future__ import annotations

UI_ACTIVITY_NONE = "none"
FORBIDDEN_UI_ACTIVITIES = {"calculation-economic-look"}

LANE_UI = {
    "market_discovery": ("researcher", "Oracle · Discovery"),
    "fundamental_events": ("researcher", "Oracle · Documents"),
    "independent_challenge": ("auditor", "Oracle · Validator"),
    "evidence_data": ("data", "Oracle · Evidence"),
    "integrator_portfolio": ("manager", "Oracle · Integration"),
}

STAGE_ACTIVITY = {
    "legacy_duplicate_check": "data-qualification",
    "mechanism_research": "hypothesis-generation",
    "document_or_fundamental_research": "document-reading",
    "disconfirmation": "audit-red-team",
    "freeze_hypothesis": "commit-persistence",
    "validation_handoff": "handoff",
    "independent_validation": "audit-red-team",
    "cross_examination": "audit-red-team",
    "red_team": "audit-red-team",
    "claim_restriction": "audit-red-team",
    "integration_handoff": "handoff",
    "recover_or_qualify": "data-qualification",
    "provenance_check": "data-qualification",
    "economic_identity": "data-qualification",
    "overlap_map": "data-qualification",
    "portfolio_map": "data-qualification",
    "shadow_readiness": "audit-red-team",
    "ledger_and_telemetry_update": "commit-persistence",
}


def live_ui_metadata(lane: str, stage: str | None) -> dict[str, str]:
    """Return explicit allowlisted UI facts for one factual canonical stage."""
    if lane not in LANE_UI:
        raise ValueError("LIVE_LAB_UNKNOWN_CANONICAL_LANE")
    role, label = LANE_UI[lane]
    activity = STAGE_ACTIVITY.get(stage, UI_ACTIVITY_NONE)
    if activity in FORBIDDEN_UI_ACTIVITIES:
        raise ValueError("LIVE_LAB_ECONOMIC_LOOK_CANNOT_BE_INFERRED")
    return {"ui_role": role, "ui_label": label, "ui_activity": activity}


def assert_live_ui_contract() -> None:
    """Fail closed if a future mapping accidentally opens economic animation."""
    for lane in LANE_UI:
        for stage in STAGE_ACTIVITY:
            metadata = live_ui_metadata(lane, stage)
            if metadata["ui_activity"] in FORBIDDEN_UI_ACTIVITIES:
                raise AssertionError("FORBIDDEN_LIVE_LAB_ACTIVITY_MAPPED")
