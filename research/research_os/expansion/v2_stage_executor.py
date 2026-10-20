from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Mapping

from research.research_os.github_state import PREFIX
from research.research_os.worker_stages import (
    AUTHORITY,
    REASONING_POLICY,
    CanonicalStageExecutor,
    DEFAULT_SOURCES,
    PRODUCERS,
    StageBlocked,
    artifact_path,
)

from .economic_test_readiness_v1 import READY as V1_READY
from .v2_bridge import adapt_engine_output_to_v2_candidate, adapt_existing_validation_to_v2
from .v2_independence import AXES, independent_context, process_identity
from .v2_core import (
    V2ContractError,
    blinding_integrity,
    build_epoch_manifest,
    build_frozen_export_intent,
    build_research_trial,
    build_negative_memory,
    canonical_hash,
)

ACTIVE_EPOCH_PATH = PREFIX + "runtime/V2_ACTIVE_EPOCH.json"


def v2_artifact_path(task: Mapping[str, Any], name: str) -> str:
    return PREFIX + f"artifacts/{task['task_id']}/oracle-v2/{name}.json"


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise StageBlocked("V2_TIMESTAMP_WITHOUT_TIMEZONE")
    return parsed


def _active_epoch(snapshot) -> Dict[str, Any]:
    raw = snapshot.read(ACTIVE_EPOCH_PATH)
    if raw.get("state") != "OPEN":
        raise StageBlocked("V2_ACTIVE_EPOCH_NOT_OPEN")
    try:
        manifest = build_epoch_manifest(raw)
    except V2ContractError as exc:
        raise StageBlocked("V2_ACTIVE_EPOCH_INVALID:" + str(exc)) from None
    manifest["owner_outcome_blinding_status"] = raw.get("owner_outcome_blinding_status", "BLINDED")
    manifest["supervisor_outcome_blinding_status"] = raw.get("supervisor_outcome_blinding_status", "BLINDED")
    manifest["first_evaluation_export_accepted"] = bool(raw.get("first_evaluation_export_accepted", False))
    return manifest


def _source_pit(engine_output: Mapping[str, Any], epoch: Mapping[str, Any]) -> Dict[str, Any]:
    candidate = engine_output.get("candidate") or {}
    packet = ((candidate.get("documentary_evidence") or {}).get("packet") or {})
    available_at = packet.get("available_at")
    if not available_at:
        return {
            "source_pit": "UNRESOLVED",
            "available_at": None,
            "knowledge_cutoff": epoch["knowledge_cutoff"],
            "model_pit": "NOT_APPLICABLE_DETERMINISTIC_PRODUCER",
            "historical_generation_status": "SOURCE_PIT_UNRESOLVED",
        }
    try:
        qualified = _parse_time(available_at) <= _parse_time(epoch["knowledge_cutoff"])
    except (ValueError, TypeError):
        qualified = False
    return {
        "source_pit": "PASS" if qualified else "FAIL",
        "available_at": available_at,
        "knowledge_cutoff": epoch["knowledge_cutoff"],
        "model_pit": "NOT_APPLICABLE_DETERMINISTIC_PRODUCER",
        "historical_generation_status": (
            "DETERMINISTIC_PRODUCER_SOURCE_PIT" if qualified else "SOURCE_NOT_PIT"
        ),
    }


def _research_stage(task: Mapping[str, Any]) -> str:
    return "document_or_fundamental_research" if task["task_type"] in ("FUNDAMENTAL_RESEARCH", "EVENT_DOCUMENT") else "mechanism_research"


def _read_v2_candidate(snapshot, task: Mapping[str, Any]) -> Dict[str, Any]:
    path = (task.get("inputs") or {}).get("v2_candidate")
    if not path or not path.startswith(PREFIX + "artifacts/"):
        raise StageBlocked("V2_CANDIDATE_REFERENCE_REQUIRED")
    candidate = snapshot.read(path)
    if candidate.get("candidate_hash") != canonical_hash({k: v for k, v in candidate.items() if k != "candidate_hash"}):
        raise StageBlocked("V2_CANDIDATE_HASH_MISMATCH")
    return candidate


def _validator_sidecar(snapshot, task: Mapping[str, Any]) -> Dict[str, Any]:
    return snapshot.read(v2_artifact_path(task, "validator.json"))


def _trial_sidecar(snapshot, task: Mapping[str, Any]) -> Dict[str, Any]:
    path = (task.get("inputs") or {}).get("v2_trial") or v2_artifact_path(task, "research_trial.json")
    return snapshot.read(path)


class V2StageExecutor(CanonicalStageExecutor):
    """Add V2 scientific contracts around the already-qualified V1 stages.

    The base executor remains authoritative for source handling, screening,
    freezing, independent challenge and red-team gates. V2 sidecars are added
    to the same atomic stage transaction. No outcome source is introduced.
    """

    def execute(self, snapshot, task, lane, stage, now, worker_id):
        epoch = _active_epoch(snapshot)
        window = epoch["research_window"]
        if not _parse_time(window["start"]) <= _parse_time(now) < _parse_time(window["end"]):
            raise StageBlocked("V2_RESEARCH_WINDOW_CLOSED")
        if stage == "claim_restriction":
            if _parse_time(now) >= _parse_time(epoch["export_cutoff"]):
                raise StageBlocked("V2_EXPORT_CUTOFF_REACHED")
            exports = sum(1 for p in snapshot.blobs if "/oracle-v2/frozen_export_intent" in p
                          and snapshot.read(p).get("research_epoch_id") == epoch["research_epoch_id"])
            if exports >= epoch["max_candidate_exports"]:
                raise StageBlocked("V2_EPOCH_EXPORT_BUDGET_EXHAUSTED")
        independence = None
        if lane == "independent_challenge" and stage == "independent_validation":
            independence = independent_context(snapshot, _read_v2_candidate(snapshot, task))
        if isinstance(getattr(self.backend, "calls", None), list):
            self.backend.calls.clear()
        if stage in ("mechanism_research", "document_or_fundamental_research"):
            source = (task.get("inputs") or {}).get("documentary_source")
            key = PRODUCERS[task["task_type"]]
            source = source or (PREFIX + "sources/" + DEFAULT_SOURCES[key] if key in DEFAULT_SOURCES else None)
            if source:
                if not isinstance(source, str) or not source.startswith(PREFIX + "sources/"):
                    raise StageBlocked("V2_UNSAFE_DOCUMENTARY_SOURCE_PATH")
                packet = snapshot.read(source).get("documentary_packet") or {}
                available = packet.get("available_at")
                if not available or _parse_time(available) > _parse_time(epoch["knowledge_cutoff"]):
                    raise StageBlocked("V2_SOURCE_PIT_NOT_QUALIFIED_BEFORE_IDEATION")
                intent = (task.get("execution") or {}).get("v2_trial_intent")
                if intent and snapshot.read(intent).get("source_blob") != snapshot.blobs[source]:
                    raise StageBlocked("V2_SOURCE_CHANGED_AFTER_IDEATION_INTENT")
        result, writes, status = super().execute(snapshot, task, lane, stage, now, worker_id)
        result["research_contract_version"] = "v2-core"
        result["research_epoch_id"] = epoch["research_epoch_id"]
        result["epoch_manifest_hash"] = epoch["epoch_manifest_hash"]
        result["authority"] = dict(AUTHORITY)
        result["outcome_accessed"] = False
        result["economic_result"] = "NOT_OBSERVED"

        if stage in ("mechanism_research", "document_or_fundamental_research") and result.get("engine_output"):
            engine_output = result["engine_output"]
            candidate = engine_output["candidate"]
            trial_id = f"{epoch['research_epoch_id']}::{task['task_id']}::{candidate['generation_id']}"
            source_packet = ((candidate.get("documentary_evidence") or {}).get("packet") or {})
            intents = sorted(p for p in snapshot.blobs if p.startswith(PREFIX + f"artifacts/{task['task_id']}/oracle-v2/trial_intents/")
                             and not p.endswith("-completion.json"))
            trial = build_research_trial({
                "research_trial_id": trial_id,
                "research_epoch_id": epoch["research_epoch_id"],
                "trial_type": "RESEARCH_GENERATION_TRIAL",
                "model_identity": "DETERMINISTIC_ENGINE",
                "prompt_hash": canonical_hash({"engine_id": engine_output["engine_id"], "mode": "registered-engine"}),
                "context_hash": canonical_hash({
                    "source_refs": engine_output.get("source_refs", []),
                    "source_blob": result.get("source_blob"),
                }),
                "retrieval_manifest_hash": canonical_hash({
                    "source_path": result.get("source_path"),
                    "source_refs": engine_output.get("source_refs", []),
                }),
                "source_packet_hash": source_packet.get("content_hash") or canonical_hash(source_packet),
                "generated_at": now,
                "sampling_parameters": {"mode": "DETERMINISTIC_REGISTERED_ENGINE"},
                "generated_proposals": [{
                    "hypothesis_id": candidate["hypothesis_id"],
                    "generation_id": candidate["generation_id"],
                    "candidate_hash": canonical_hash(candidate),
                }],
                "discarded_proposals": ([{"hypothesis_id": candidate["hypothesis_id"], "reason": "STRUCTURAL_SCREEN_BLOCK",
                                          "blockers": result.get("screen", {}).get("block_reasons", [])}]
                                        if status == "BLOCKED" else []),
                "retry_count": max(0, len(intents) - 1),
                "ideation_intents": intents,
                "earlier_attempt_proposals": "UNKNOWN_IF_NO_DURABLE_COMPLETION",
                "executable_release_sha": (task.get("execution") or {}).get("release_sha"),
            })
            v2_candidate = adapt_engine_output_to_v2_candidate(
                engine_output,
                research_trial_id=trial_id,
                research_epoch_id=epoch["research_epoch_id"],
                producer_identity={
                    "process": process_identity(),
                    "worker_id": worker_id,
                    "lane": lane,
                    "task_id": task["task_id"],
                    "engine_id": engine_output["engine_id"],
                    "engine_family": engine_output["engine_family"],
                },
                disconfirmation_manifest={"attempted": False, "status": "PENDING"},
                source_binding={"source_path": result.get("source_path"), "source_blob": result.get("source_blob"),
                                "source_candidate_hash": canonical_hash(candidate)},
            )
            leakage = _source_pit(engine_output, epoch)
            leakage["reasoning_output_classification"] = (result.get("reasoning") or {}).get(
                "classification", "NO_MODEL_COMMENTARY"
            )
            writes[v2_artifact_path(task, "research_trial.json")] = trial
            writes[v2_artifact_path(task, "candidate_draft.json")] = v2_candidate
            writes[v2_artifact_path(task, "leakage.json")] = leakage
            if status == "BLOCKED":
                writes[v2_artifact_path(task, "negative_memory.json")] = build_negative_memory({
                    "negative_knowledge_id": trial_id + "::screen", "failure_scope": "CURRENT_STRUCTURAL_SCREEN",
                    "assumptions": {"screen": result["screen"]}, "regime_context": "PRE_OUTCOME_DOCUMENTARY_ONLY",
                    "source_context": {"path": result.get("source_path"), "blob": result.get("source_blob")},
                    "failure_reason": "UNRESOLVED_OR_DUPLICATE_EXPOSURE",
                    "revisit_conditions": ["New evidence resolves the recorded structural blockers without rewriting frozen history"],
                    "revisit_policy": "NEW_GENERATION_WITH_EXPLICIT_DISTINCTNESS_EVIDENCE"})
            result["v2_sidecars"] = {
                "research_trial": v2_artifact_path(task, "research_trial.json"),
                "candidate_draft": v2_artifact_path(task, "candidate_draft.json"),
                "leakage": v2_artifact_path(task, "leakage.json"),
            }

        elif stage == "disconfirmation":
            research = snapshot.read(artifact_path(task, _research_stage(task)))
            record = {
                "research_epoch_id": epoch["research_epoch_id"],
                "hypothesis_id": research["engine_output"]["candidate"]["hypothesis_id"],
                "attempted": True,
                "base_stage_hash": canonical_hash(result),
                "screen_status": (result.get("screen") or {}).get("status", "UNKNOWN"),
                "falsification_scope": result.get("falsification_scope", "UNRESOLVED"),
                "model_commentary_classification": (result.get("reasoning") or {}).get(
                    "classification", "NO_MODEL_COMMENTARY"
                ),
                "outcome_accessed": False,
            }
            writes[v2_artifact_path(task, "disconfirmation.json")] = record
            result["v2_disconfirmation"] = v2_artifact_path(task, "disconfirmation.json")

        elif stage == "freeze_hypothesis" and status != "BLOCKED":
            research = snapshot.read(artifact_path(task, _research_stage(task)))
            disconfirmation_path = v2_artifact_path(task, "disconfirmation.json")
            disconfirmation = snapshot.read(disconfirmation_path)
            trial = snapshot.read(v2_artifact_path(task, "research_trial.json"))
            v2_candidate = adapt_engine_output_to_v2_candidate(
                research["engine_output"],
                research_trial_id=trial["research_trial_id"],
                research_epoch_id=epoch["research_epoch_id"],
                producer_identity=snapshot.read(v2_artifact_path(task, "candidate_draft.json"))["producer_identity"],
                source_binding={"source_path": research["source_path"], "source_blob": research["source_blob"],
                                "source_candidate_hash": canonical_hash(research["engine_output"]["candidate"])},
                disconfirmation_manifest={
                    "attempted": True,
                    "artifact": disconfirmation_path,
                    "artifact_hash": canonical_hash(disconfirmation),
                    "status": disconfirmation.get("screen_status", "UNKNOWN"),
                },
            )
            frozen_sidecar = v2_artifact_path(task, "candidate_frozen.json")
            writes[frozen_sidecar] = v2_candidate
            result["v2_candidate"] = frozen_sidecar
            result["v2_candidate_hash"] = v2_candidate["candidate_hash"]

        elif stage == "validation_handoff" and status != "BLOCKED":
            producer_candidate = v2_artifact_path(task, "candidate_frozen.json")
            producer_trial = v2_artifact_path(task, "research_trial.json")
            child_paths = [
                path for path, value in writes.items()
                if path.startswith(PREFIX + "tasks/") and isinstance(value, dict)
                and value.get("task_type") in ("VALIDATION", "RED_TEAM")
            ]
            if len(child_paths) != 1:
                raise StageBlocked("V2_VALIDATION_HANDOFF_TASK_NOT_UNAMBIGUOUS")
            child = writes[child_paths[0]]
            inputs = child.setdefault("inputs", {})
            inputs.update({
                "research_contract_version": "v2-core",
                "research_epoch_id": epoch["research_epoch_id"],
                "epoch_manifest_hash": epoch["epoch_manifest_hash"],
                "v2_candidate": producer_candidate,
                "v2_trial": producer_trial,
            })
            result["v2_validation_handoff"] = {
                "task": child["task_id"],
                "candidate": producer_candidate,
                "trial": producer_trial,
                "epoch_manifest_hash": epoch["epoch_manifest_hash"],
            }

        elif lane == "independent_challenge" and stage == "independent_validation":
            candidate = _read_v2_candidate(snapshot, task)
            if (task.get("inputs") or {}).get("epoch_manifest_hash") != epoch["epoch_manifest_hash"]:
                raise StageBlocked("V2_EPOCH_BINDING_CHANGED_BEFORE_VALIDATION")
            existing = (result.get("readiness") or {}).get("validator") or result.get("validation")
            if not isinstance(existing, dict):
                raise StageBlocked("V2_EXISTING_VALIDATOR_RESULT_REQUIRED")
            reasoning = result.get("reasoning") or {}
            model = (reasoning.get("backend_health") or {}).get("model", "DETERMINISTIC_VALIDATOR")
            validator = adapt_existing_validation_to_v2(
                v2_candidate=candidate,
                existing_validation=existing,
                validator_identity=worker_id,
                validator_version="oracle-v2-validator-bridge-v1",
                validator_model="R0_DETERMINISTIC_VALIDATOR_LOCAL_CRITIC_UNVERIFIED:" + model,
                validator_prompt_hash=canonical_hash({"policy": REASONING_POLICY, "stage": stage}),
                validator_context_hash=canonical_hash({
                    "candidate_hash": candidate["candidate_hash"],
                    "screen": result.get("screen"),
                }),
                validator_retrieval_manifest_hash=canonical_hash(independence["retrieval"]),
                independence_evidence=independence,
                producer_identity_hash=canonical_hash(candidate["producer_identity"]),
                validator_state_identity_hash=canonical_hash({
                    "worker_id": worker_id,
                    "lane": lane,
                    "task_id": task["task_id"],
                    "role": "INDEPENDENT_VALIDATOR_STATE",
                    "process": independence["process"],
                }),
            )
            path = v2_artifact_path(task, "validator.json")
            writes[path] = validator
            result["v2_validator"] = path
            result["v2_scientific_decision"] = validator["scientific_decision"]

        elif lane == "independent_challenge" and stage == "claim_restriction":
            candidate = _read_v2_candidate(snapshot, task)
            trial = _trial_sidecar(snapshot, task)
            validator = _validator_sidecar(snapshot, task)
            validation_stage = snapshot.read(artifact_path(task, "independent_validation"))
            readiness = validation_stage.get("readiness") or {}
            blockers = list(result.get("blockers") or [])
            if validator.get("scientific_decision") != "PASS":
                blockers.append("V2_VALIDATOR_BLOCK")
            if not all(validator.get("independence_evidence", {}).get(axis) is True for axis in AXES):
                blockers.append("V2_VALIDATOR_INDEPENDENCE_NOT_PROVEN")
            if readiness.get("status") != V1_READY:
                blockers.append("PRE_OUTCOME_READINESS_NOT_READY")
            blind = blinding_integrity(
                owner_status=epoch["owner_outcome_blinding_status"],
                supervisor_status=epoch["supervisor_outcome_blinding_status"],
            )
            if blind["epoch_blinding_integrity"] != "PASS":
                blockers.append("EPOCH_BLINDING_INTEGRITY_BROKEN")

            readiness_sidecar = {
                "research_epoch_id": epoch["research_epoch_id"],
                "candidate_hash": candidate["candidate_hash"],
                "validator_hash": validator["validator_hash"],
                "status": "INCOMPLETE" if blockers else "READY",
                "claim_ceiling": "DESIGN_ONLY" if blockers else "READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY",
                "blockers": sorted(set(blockers)),
                "blinding": blind,
                "authority": dict(AUTHORITY),
                "outcome_accessed": False,
            }
            writes[v2_artifact_path(task, "readiness.json")] = readiness_sidecar
            result["v2_readiness"] = v2_artifact_path(task, "readiness.json")

            if not blockers:
                plan = readiness.get("experiment_plan") or {}
                plan_payload = plan.get("plan") or {}
                protocol_hash = plan_payload.get("protocol_hash")
                source_qualifications = list(readiness.get("source_qualifications") or [])
                source_hashes = [
                    item.get("snapshot_hash") or item.get("route_hash")
                    for item in source_qualifications
                ]
                if not protocol_hash or not source_hashes or any(not value for value in source_hashes):
                    raise StageBlocked("V2_READY_PACKAGE_MISSING_EXPORT_BINDINGS")
                frozen_protocol = plan.get("frozen_protocol") or {}
                export = build_frozen_export_intent({
                    "candidate_hash": candidate["candidate_hash"],
                    "research_trial_history_hash": canonical_hash([trial["trial_hash"]]),
                    "research_epoch_id": epoch["research_epoch_id"],
                    "epoch_manifest_hash": epoch["epoch_manifest_hash"],
                    "protocol_hash": protocol_hash,
                    "source_snapshot_hashes": sorted(source_hashes),
                    "pit_manifest_hash": canonical_hash(source_qualifications),
                    "universe": candidate["universe"],
                    "clock": candidate["clock"],
                    "horizon": candidate["horizon"],
                    "economic_expression": candidate["economic_expression"],
                    "cost_model_declaration": deepcopy(frozen_protocol.get("cost_assumptions") or {"status": "DECLARED_IN_READY_PACKAGE"}),
                    "capacity_declaration": deepcopy(frozen_protocol.get("capacity_assumptions") or {"status": "DECLARED_IN_READY_PACKAGE"}),
                    "multiplicity_declaration": {
                        "trial_accounting": deepcopy(readiness.get("trial_accounting") or {}),
                        "family": frozen_protocol.get("multiplicity_family", "DECLARED_IN_READY_PACKAGE"),
                    },
                    "validator_artifact_hash": validator["validator_hash"],
                    "research_head": snapshot.head,
                })
                export["evaluation_plane_status"] = "SEALED"
                export["evaluation_ingest_status"] = "NOT_ATTEMPTED_V2_CORE"
                export["economic_experiment_authorized"] = False
                export["prospective_observation_authorized"] = False
                export_path = v2_artifact_path(task, "frozen_export_intent.json")
                writes[export_path] = export
                result["v2_frozen_export_intent"] = export_path
                result["v2_claim_ceiling"] = "READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY"

        return result, writes, status
