from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

from research.research_os.control_plane import load_control_plane
from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.live_bridge import worker_events
from research.research_os.engines.protocol import EngineContext
from research.research_os.legacy import LegacyKnowledgeBase
from research.research_os.scientific_store import (
    AppendOnlyHashLedger,
    scientific_snapshot,
    sha256_json,
    trial_record,
)

from .archaeology import EdgeArchaeologyEngine
from .final_shape import (
    assess_implementability,
    decay_guard,
    economic_identity_v1,
    forward_register,
    freeze_experiment_envelope,
    independent_validate,
    learning_telemetry,
    portfolio_map_v1,
    red_team,
)


ENGINE_CAPABILITIES = {
    "quant": "quant_mechanisms",
    "fundamental": "fundamental",
    "event_document": "event_document",
    "institutional_flow": "institutional_flows",
    "archaeology": "legacy_recovery",
}

ENGINE_ACTIVITY = {
    "QUANT_MECHANISM": "data-qualification",
    "FUNDAMENTAL": "document-reading",
    "EVENT_DOCUMENT": "document-reading",
    "INSTITUTIONAL_FLOW": "source-research",
    "EDGE_ARCHAEOLOGY": "document-reading",
}

CANONICAL_DOWNSTREAM_STAGE_KINDS = [
    "IMPLEMENTABILITY_ASSESSMENT",
    "EXPERIMENT_ENVELOPE",
    "INDEPENDENT_VALIDATION",
    "RED_TEAM_ASSESSMENT",
    "ECONOMIC_IDENTITY",
    "PORTFOLIO_MAP",
    "FORWARD_REGISTRATION",
    "DECAY_GUARD",
    "LEARNING_TELEMETRY",
]


def _validate_task(task: Dict[str, Any], control: Dict[str, Any], run_time: str) -> Dict[str, Any]:
    required = {
        "task_id",
        "task_type",
        "required_capability",
        "status",
        "priority",
        "inputs",
        "allowed_actions",
        "forbidden_actions",
        "success_condition",
        "authority",
        "lease",
        "created_at",
    }
    errors: List[str] = []
    missing = sorted(required - set(task))
    if missing:
        errors.append(f"missing_fields:{','.join(missing)}")
    if task.get("status") != "CLAIMED":
        errors.append("task_not_claimed")
    lease = task.get("lease") or {}
    if not isinstance(lease.get("generation"), int) or lease.get("generation", 0) < 1:
        errors.append("invalid_lease_generation")
    if not lease.get("owner"):
        errors.append("missing_lease_owner")
    from .engine_dossiers_v1 import _clock
    try:
        if not _clock(lease['claimed_at']) <= _clock(run_time) < _clock(lease['expires_at']):
            errors.append('lease_not_valid_at_run_time')
    except (KeyError, ValueError, TypeError, AttributeError):
        errors.append('lease_clock_invalid')
    if task.get("required_capability") not in set(control.get("capabilities") or []):
        errors.append("capability_not_registered")
    authority = task.get("authority") or {}
    for key in (
        "economic_experiment_authorized",
        "prospective_observation_authorized",
        "real_capital_authorized",
        "live_trading_authorized",
    ):
        if authority.get(key) is not False:
            errors.append(f"task_authority_must_be_false:{key}")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "task_id": task.get("task_id"),
        "required_capability": task.get("required_capability"),
        "lease_generation": lease.get("generation"),
        "lease_owner": lease.get("owner"),
    }


def _receipt(
    *,
    run_id: str,
    task_id: str,
    worker_id: str,
    action_id: str,
    artifact: Dict[str, Any],
    status: str,
) -> Dict[str, Any]:
    payload = {
        "run_id": run_id,
        "task_id": task_id,
        "worker_id": worker_id,
        "action_id": action_id,
        "status": status,
        "artifact_hash": sha256_json(artifact),
        "economic_experiment_authorized": False,
        "prospective_observation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
    }
    return {**payload, "receipt_id": f"RCP-{sha256_json(payload)[:20]}"}


def _stage(
    stages: List[Dict[str, Any]],
    receipts: List[Dict[str, Any]],
    *,
    run_id: str,
    task_id: str,
    stage_kind: str,
    worker_id: str,
    artifact: Dict[str, Any],
    status: str,
    activity: str,
) -> None:
    action_id = stage_kind.lower().replace("_", ":")
    stages.append({
        "worker_id": worker_id,
        "action_id": action_id,
        "label": stage_kind,
        "detail": status,
        "ui_activity": activity,
    })
    receipts.append(_receipt(
        run_id=run_id,
        task_id=task_id,
        worker_id=worker_id,
        action_id=action_id,
        artifact=artifact,
        status=status,
    ))


def _engine_output(
    engine_key: str,
    fixture: Dict[str, Any],
    context: EngineContext,
) -> Dict[str, Any]:
    if engine_key == "archaeology":
        return EdgeArchaeologyEngine().run(fixture["sources"]["archaeology"], context)
    if engine_key not in ENGINE_REGISTRY:
        raise ValueError(f"unsupported engine key: {engine_key}")
    return ENGINE_REGISTRY[engine_key].run(fixture["sources"][engine_key], context)


def run_canonical_spine(
    base: Path,
    fixture: Dict[str, Any],
    task: Dict[str, Any],
    *,
    legacy_ledger_path: Optional[Path] = None,
    candidate_override_hypothesis_id: Optional[str] = None,
    checkpoint_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Run one deterministic final-shape lineage.

    This is an architecture proof only. It never opens economic outcomes, starts
    prospective observation, allocates capital or trades.
    """

    run_id = str(fixture["run_id"]) + ":CANONICAL-SPINE"
    base_time = fixture.get("base_time", "2026-10-15T14:00:00Z")
    task_id = task["task_id"]

    control = load_control_plane(base)
    task_validation = _validate_task(task, control, base_time)
    if control["status"] != "PASS":
        raise ValueError(f"control plane invalid: {control['errors']}")
    if task_validation["status"] != "PASS":
        raise ValueError(f"research task invalid: {task_validation['errors']}")

    engine_key = task.get("inputs", {}).get("engine_key")
    expected_capability = ENGINE_CAPABILITIES.get(engine_key)
    if expected_capability is None:
        raise ValueError(f"task engine_key is not routable: {engine_key}")
    if task["required_capability"] != expected_capability:
        raise ValueError("task capability does not match engine route")

    governance = {
        "owner_scope": task["authority"].get("scope"),
        "control_mode": control["mode"],
        "workflow_model": control["workflow_model"],
        "global_authority": deepcopy(control["global_authority"]),
        "task_authority": deepcopy(task["authority"]),
        "real_capital_authorized": False,
        "live_trading_authorized": False,
        "prospective_observation_authorized": False,
        "economic_experiment_authorized": False,
    }

    stages: List[Dict[str, Any]] = []
    receipts: List[Dict[str, Any]] = []
    stage_order: List[str] = []

    def emit(kind: str, worker: str, artifact: Dict[str, Any], status: str, activity: str) -> None:
        stage_order.append(kind)
        _stage(
            stages,
            receipts,
            run_id=run_id,
            task_id=task_id,
            stage_kind=kind,
            worker_id=worker,
            artifact=artifact,
            status=status,
            activity=activity,
        )

    emit("GOVERNANCE_SNAPSHOT", "owner-governance.v1", governance, "PASS", "commit-persistence")
    emit("CONTROL_PLANE_SNAPSHOT", "control-plane.v1", control, control["status"], "commit-persistence")
    emit("TASK_CLAIM", task["lease"]["owner"], task, task_validation["status"], "commit-persistence")

    documentary_mode = task.get('inputs', {}).get('evidence_mode') == 'DOCUMENTARY'
    if documentary_mode and 'DOCUMENTARY_RESEARCH' not in task.get('allowed_actions', []):
        raise PermissionError('documentary execution must be explicit in the task contract')
    context = EngineContext(run_id=run_id, synthetic_only=not documentary_mode)
    output = _engine_output(engine_key, fixture, context)
    if documentary_mode:
        from .engine_dossiers_v1 import _clock
        if _clock(base_time) < _clock(output['candidate']['documentary_evidence']['freeze_time']):
            raise ValueError('run clock precedes documentary source availability/freeze')
    if candidate_override_hypothesis_id is not None:
        output = deepcopy(output)
        output["candidate"]["hypothesis_id"] = candidate_override_hypothesis_id
    candidate_hash_before = sha256_json(output["candidate"])
    hid = output["candidate"]["hypothesis_id"]
    emit(
        "CANDIDATE_HYPOTHESIS",
        output["engine_id"],
        output,
        "COMPLETE",
        ENGINE_ACTIVITY[output["engine_family"]],
    )

    legacy = LegacyKnowledgeBase.load(base, legacy_ledger_path)
    legacy_screen = legacy.screen_candidate(output["candidate"])
    legacy_blocked = legacy_screen["status"] == "BLOCK_EXACT_LEGACY_DUPLICATE"
    emit(
        "LEGACY_SCREEN",
        "legacy-anti-restart.v1",
        legacy_screen,
        legacy_screen["status"],
        "blocker" if legacy_blocked else "document-reading",
    )

    ledger = AppendOnlyHashLedger()
    snapshot = scientific_snapshot(
        run_id=run_id,
        candidate=output["candidate"],
        timestamp=base_time,
    )
    trial = trial_record(
        run_id=run_id,
        candidate=output["candidate"],
        timestamp=base_time,
    )
    if documentary_mode:
        snapshot['lifecycle'] = 'IDEA'
        trial['covered_scope'] = 'Documentary candidate construction only; no economic experiment'
        trial['attempt_refs'] = list(output['source_refs'])
    ledger.append("GOVERNANCE_SNAPSHOT", governance)
    ledger.append("CONTROL_PLANE_SNAPSHOT", control)
    ledger.append("RESEARCH_TASK_CLAIM", deepcopy(task))
    ledger.append("SCIENTIFIC_SNAPSHOT", snapshot)
    ledger.append("TRIAL_RECORD", trial)
    ledger.append("LEGACY_REFERENCE", legacy.summary())
    ledger.append("LEGACY_SCREEN", legacy_screen)

    if legacy_blocked:
        persistence_artifact = {
            "status": "BLOCKED_EXACT_LEGACY_DUPLICATE",
            "ledger_verified_before_receipts": ledger.verify(),
            "downstream_stage_count": 0,
        }
        emit(
            "CANONICAL_PERSISTENCE",
            "scientific-ledger.v1",
            persistence_artifact,
            persistence_artifact["status"],
            "commit-persistence",
        )
        emit(
            "HANDOFF",
            "control-plane.v1",
            {"task_id": task_id, "terminal_state": "BLOCKED", "reason": legacy_screen["status"]},
            "BLOCKED",
            "handoff",
        )
        for receipt in receipts:
            ledger.append("WORKER_RECEIPT", receipt)
        events = worker_events(run_id, stages, base_time=base_time)
        final = {
            "run_id": run_id,
            "status": "BLOCKED_EXACT_LEGACY_DUPLICATE",
            "synthetic_only": context.synthetic_only,
            "event_provenance": "BUILD_REPLAY_NOT_LIVE",
            "governance": governance,
            "control_plane": control,
            "task_validation": task_validation,
            "task": deepcopy(task),
            "candidate": output,
            "legacy": {"summary": legacy.summary(), "screen": legacy_screen},
            "downstream_executed": False,
            "downstream_stage_kinds": [],
            "trial_ledger": [trial],
            "scientific_ledger": {
                "verified": ledger.verify(),
                "entry_count": len(ledger.entries),
                "entries": deepcopy(ledger.entries),
            },
            "stage_order": stage_order,
            "worker_events": events,
            "worker_receipts": receipts,
            "live_lab_bridge": {
                "status": "PASS",
                "native_event_types": sorted({e["event_type"] for e in events}),
                "economic_semantics_fabricated": False,
            },
            "authority": {
                "economic_experiment_authorized": False,
                "prospective_observation_authorized": False,
                "real_capital_authorized": False,
                "live_trading_authorized": False,
            },
        }
        final["canonical_fingerprint"] = sha256_json({
            "status": final["status"],
            "stage_order": final["stage_order"],
            "ledger": final["scientific_ledger"],
            "events": final["worker_events"],
            "receipts": final["worker_receipts"],
            "authority": final["authority"],
        })
        if checkpoint_dir is not None:
            from .persistent_state import write_immutable_json
            write_immutable_json(checkpoint_dir / f"{final['canonical_fingerprint']}.canonical.json", final)
        return final

    meta_hid = output["candidate"]["hypothesis_id"]
    if checkpoint_dir is not None:
        from .persistent_state import write_immutable_json
        generation_key = sha256_json([meta_hid, output['candidate']['generation_id']])
        write_immutable_json(checkpoint_dir / f'{generation_key}.generation.json', output['candidate'])
    # In the normal fixture the hypothesis id is the engine's canonical synthetic id.
    impl = assess_implementability(output, fixture["implementability"][meta_hid])
    envelope = freeze_experiment_envelope(output, impl, fixture["experiments"][meta_hid])
    validation = independent_validate(output, impl, envelope)
    documentary_depth = None
    if 'documentary_evidence' in output['candidate']:
        from .canonical_depth_v1 import execute_documentary_depth
        from .validation_v2 import validator_diagnostics_v2
        documentary_depth = execute_documentary_depth(output, envelope, checkpoint_dir)
        envelope['dry_run_execution'] = documentary_depth
        diagnostics = validator_diagnostics_v2(
            engine_output=output, validation_v1=validation,
            source_qualifications=[documentary_depth['source_qualification']],
            envelope=envelope, dry_run_plan=documentary_depth['dry_run_plan'],
            trial_record=trial, experiment_meta=fixture['experiments'][meta_hid],
            executed_dry_run=documentary_depth['executed_dry_run'],
        )
        validation = {**validation, **diagnostics}
    red = red_team(output, impl, validation, fixture["experiments"][meta_hid])
    identity = economic_identity_v1(output, fixture["economic_identity"][meta_hid])
    portfolio = portfolio_map_v1([identity])
    forward = forward_register(output, envelope, validation, red)
    decay = decay_guard([forward])
    telemetry = learning_telemetry([impl], [validation], [red])

    downstream = [
        ("IMPLEMENTABILITY_ASSESSMENT", "implementability.v1", impl, impl["status"], "data-qualification" if impl["status"] == "PASS" else "blocker"),
        ("EXPERIMENT_ENVELOPE", "experiment-infra.v1", envelope, envelope["status"], "coding-testing" if envelope["protocol_hash"] else "blocker"),
        ("INDEPENDENT_VALIDATION", validation["validator"], validation, validation["status"], "audit-red-team"),
        ("RED_TEAM_ASSESSMENT", red["red_team"], red, red["status"], "audit-red-team"),
        ("ECONOMIC_IDENTITY", "economic-identity.v1", identity, "COMPLETE", "data-qualification"),
        ("PORTFOLIO_MAP", "portfolio-map.v1", portfolio, "COMPLETE", "data-qualification"),
        ("FORWARD_REGISTRATION", "forward-farm.v1", forward, forward["readiness"], "commit-persistence"),
        ("DECAY_GUARD", "decay-monitor.v1", decay, decay["status"], "audit-red-team"),
        ("LEARNING_TELEMETRY", "meta-research-telemetry.v1", telemetry, "COMPLETE", "commit-persistence"),
    ]
    for kind, worker, artifact, status, activity in downstream:
        emit(kind, worker, artifact, status, activity)
        ledger.append(kind, artifact)

    candidate_hash_after = sha256_json(output["candidate"])
    if candidate_hash_before != candidate_hash_after:
        raise ValueError("canonical candidate mutated across downstream stages")

    persistence_artifact = {
        "status": "PASS",
        "ledger_verified_before_receipts": ledger.verify(),
        "downstream_stage_count": len(downstream),
        "candidate_hash_stable": candidate_hash_before == candidate_hash_after,
    }
    emit("CANONICAL_PERSISTENCE", "scientific-ledger.v1", persistence_artifact, "PASS", "commit-persistence")
    emit(
        "HANDOFF",
        "control-plane.v1",
        {"task_id": task_id, "terminal_state": "COMPLETE", "next": "NONE_IN_ARCHITECTURE_SIMULATION"},
        "COMPLETE",
        "handoff",
    )

    for receipt in receipts:
        ledger.append("WORKER_RECEIPT", receipt)

    events = worker_events(run_id, stages, base_time=base_time)
    authority = {
        "economic_experiment_authorized": False,
        "prospective_observation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
    }

    status = "PASS"
    if envelope["outcome_opened"] is not False:
        status = "FAIL"
    if forward["observation_started"] is not False or forward["future_outcomes_consumed"] != 0:
        status = "FAIL"
    if portfolio["capital_allocation_authorized"] or portfolio["orders_authorized"]:
        status = "FAIL"
    if validation["independent_from_producer"] is not True:
        status = "FAIL"
    if not ledger.verify():
        status = "FAIL"

    final = {
        "run_id": run_id,
        "status": status,
        "synthetic_only": context.synthetic_only,
        "event_provenance": "BUILD_REPLAY_NOT_LIVE",
        "governance": governance,
        "control_plane": control,
        "task_validation": task_validation,
        "task": deepcopy(task),
        "candidate": output,
        "legacy": {"summary": legacy.summary(), "screen": legacy_screen},
        "implementability": impl,
        "experiment_envelope": envelope,
        "validation": validation,
        "red_team": red,
        "economic_identity": identity,
        "portfolio": portfolio,
        "forward_registration": forward,
        "decay": decay,
        "learning_telemetry": telemetry,
        "downstream_executed": True,
        "downstream_stage_kinds": list(CANONICAL_DOWNSTREAM_STAGE_KINDS),
        "trial_ledger": [trial],
        "scientific_ledger": {
            "verified": ledger.verify(),
            "entry_count": len(ledger.entries),
            "entries": deepcopy(ledger.entries),
        },
        "stage_order": stage_order,
        "worker_events": events,
        "worker_receipts": receipts,
        "live_lab_bridge": {
            "status": "PASS",
            "native_event_types": sorted({e["event_type"] for e in events}),
            "event_count": len(events),
            "receipt_count": len(receipts),
            "economic_semantics_fabricated": False,
        },
        "authority": authority,
    }
    if documentary_depth is not None:
        final['documentary_depth'] = documentary_depth
    final["canonical_fingerprint"] = sha256_json({
        "status": final["status"],
        "stage_order": final["stage_order"],
        "ledger": final["scientific_ledger"],
        "events": final["worker_events"],
        "receipts": final["worker_receipts"],
        "authority": final["authority"],
    })
    if checkpoint_dir is not None:
        from .persistent_state import write_immutable_json
        write_immutable_json(checkpoint_dir / f"{final['canonical_fingerprint']}.canonical.json", final)
    return final
