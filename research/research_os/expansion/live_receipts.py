from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List

from research.research_os.engines.live_bridge import worker_events
from .final_shape import run_aggressive_pipeline


ENGINE_ACTIVITY = {
    "QUANT_MECHANISM": "data-qualification",
    "FUNDAMENTAL": "document-reading",
    "EVENT_DOCUMENT": "document-reading",
    "INSTITUTIONAL_FLOW": "source-research",
    "EDGE_ARCHAEOLOGY": "document-reading",
}


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _receipt(run_id: str, worker_id: str, action_id: str, artifact: Any, status: str) -> Dict[str, Any]:
    payload = {
        "run_id": run_id,
        "worker_id": worker_id,
        "action_id": action_id,
        "status": status,
        "artifact_hash": _hash(artifact),
        "economic_experiment_authorized": False,
        "prospective_observation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
    }
    return {**payload, "receipt_id": f"RCP-{_hash(payload)[:20]}"}


def run_with_live_receipts(fixture: Dict[str, Any]) -> Dict[str, Any]:
    result = run_aggressive_pipeline(fixture)
    run_id = result["run_id"]
    stages: List[Dict[str, str]] = []
    receipts: List[Dict[str, Any]] = []

    for output in result["engine_outputs"]:
        hid = output["candidate"]["hypothesis_id"]
        action_id = f"discover:{hid}"
        stages.append({
            "worker_id": output["engine_id"],
            "action_id": action_id,
            "label": f"{output['engine_family']} candidate",
            "detail": output["candidate"]["claim"],
            "ui_activity": ENGINE_ACTIVITY[output["engine_family"]],
        })
        receipts.append(_receipt(run_id, output["engine_id"], action_id, output, "COMPLETE"))

    for impl in result["implementability"]:
        hid = impl["hypothesis_id"]
        action_id = f"implementability:{hid}"
        activity = "blocker" if impl["status"] != "PASS" else "data-qualification"
        stages.append({
            "worker_id": "implementability.v1",
            "action_id": action_id,
            "label": "Early implementability",
            "detail": impl["status"],
            "ui_activity": activity,
        })
        receipts.append(_receipt(run_id, "implementability.v1", action_id, impl, impl["status"]))

    for envelope in result["experiment_envelopes"]:
        hid = envelope["hypothesis_generation"].split(":", 1)[0]
        action_id = f"experiment-freeze:{hid}"
        stages.append({
            "worker_id": "experiment-infra.v1",
            "action_id": action_id,
            "label": "Experiment envelope",
            "detail": envelope["status"],
            "ui_activity": "coding-testing" if envelope["protocol_hash"] else "blocker",
        })
        receipts.append(_receipt(run_id, "experiment-infra.v1", action_id, envelope, envelope["status"]))

    for validation in result["validations"]:
        hid = validation["hypothesis_id"]
        action_id = f"validate:{hid}"
        stages.append({
            "worker_id": validation["validator"],
            "action_id": action_id,
            "label": "Independent validation",
            "detail": validation["status"],
            "ui_activity": "audit-red-team",
        })
        receipts.append(_receipt(run_id, validation["validator"], action_id, validation, validation["status"]))

    for red in result["red_teams"]:
        hid = red["hypothesis_id"]
        action_id = f"red-team:{hid}"
        stages.append({
            "worker_id": red["red_team"],
            "action_id": action_id,
            "label": "Red Team",
            "detail": red["status"],
            "ui_activity": "audit-red-team",
        })
        receipts.append(_receipt(run_id, red["red_team"], action_id, red, red["status"]))

    aggregate = [
        ("portfolio-map.v1", "portfolio:map", "Portfolio map", result["portfolio"], "data-qualification"),
        ("forward-farm.v1", "forward:readiness", "Forward farm readiness", result["forward_farm"], "commit-persistence"),
        ("decay-monitor.v1", "decay:guard", "Decay authority guard", result["decay"], "audit-red-team"),
        ("meta-research-telemetry.v1", "learning:telemetry", "Learning telemetry", result["learning_telemetry"], "commit-persistence"),
    ]
    for worker_id, action_id, label, artifact, activity in aggregate:
        stages.append({
            "worker_id": worker_id,
            "action_id": action_id,
            "label": label,
            "detail": "deterministic architecture stage",
            "ui_activity": activity,
        })
        receipts.append(_receipt(run_id, worker_id, action_id, artifact, "COMPLETE"))

    events = worker_events(run_id, stages, base_time="2026-10-15T13:00:00Z")
    result = dict(result)
    result["worker_events"] = events
    result["worker_receipts"] = receipts
    result["live_lab_bridge"] = {
        "status": "PASS",
        "event_count": len(events),
        "receipt_count": len(receipts),
        "native_event_types": sorted({e["event_type"] for e in events}),
        "economic_semantics_fabricated": False,
    }
    result["integration_fingerprint"] = _hash({
        "scientific_fingerprint": result["deterministic_fingerprint"],
        "events": events,
        "receipts": receipts,
    })
    return result
