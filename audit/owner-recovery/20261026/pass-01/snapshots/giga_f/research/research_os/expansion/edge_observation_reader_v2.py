"""Task-scoped observation over caller-supplied verified snapshots, never a writer."""
from copy import deepcopy

from research.research_os.github_state import PREFIX, SHA
from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.oracle_worker import ASSERTION, ID
from research.research_os.worker_stages import PRODUCERS, artifact_path
from .edge_observability_v2 import _assert_pre_outcome, build_edge_observability_projection
from .source_qualification import build_producer_test_readiness
from .v2_core import assert_authority_closed, canonical_hash
from .v2_state import POLICY_PATH, V2StateStore
from .v2_stage_executor import ACTIVE_EPOCH_PATH


class EdgeObservationReadError(ValueError):
    pass


def task_observation_paths(task_id):
    if not isinstance(task_id, str) or not ID.fullmatch(task_id):
        raise EdgeObservationReadError("INVALID_OBSERVATION_TASK_ID")
    return (POLICY_PATH, ACTIVE_EPOCH_PATH, PREFIX + f"tasks/{task_id}.json",
            artifact_path({"task_id": task_id}, "mechanism_research"),
            artifact_path({"task_id": task_id}, "document_or_fundamental_research"))


class _BoundedReads:
    def __init__(self, snapshot, task_id):
        if not isinstance(snapshot.head, str) or not SHA.fullmatch(snapshot.head):
            raise EdgeObservationReadError("EXACT_SNAPSHOT_HEAD_REQUIRED")
        self.snapshot, self.head, self.blobs = snapshot, snapshot.head, snapshot.blobs
        self.allowed, self.read_blobs = set(task_observation_paths(task_id)), {}

    def read(self, path):
        if path not in self.allowed:
            raise EdgeObservationReadError("OBSERVATION_PATH_NOT_ALLOWLISTED")
        blob = self.blobs.get(path)
        if not isinstance(blob, str) or not SHA.fullmatch(blob):
            raise EdgeObservationReadError("OBSERVATION_BLOB_REQUIRED:" + path)
        value = self.snapshot.read(path)  # existing Snapshot verifies the bytes
        if not isinstance(value, dict):
            raise EdgeObservationReadError("OBSERVATION_OBJECT_REQUIRED:" + path)
        _assert_pre_outcome(value)
        self.read_blobs[path] = blob
        return value


def _receipt_bound(reader, task, path, research):
    execution = task.get("execution") or {}
    session = execution.get("session_id")
    if not isinstance(session, str) or not ID.fullmatch(session):
        raise EdgeObservationReadError("OBSERVATION_RECEIPT_SESSION_REQUIRED")
    expected = PREFIX + f"receipts/{task['task_id']}/{session}.json"
    if execution.get("last_receipt") != expected:
        raise EdgeObservationReadError("OBSERVATION_RECEIPT_PATH_MISMATCH")
    reader.allowed.add(expected)
    receipt = reader.read(expected)
    if (receipt.get("task_id") != task["task_id"]
            or receipt.get("session_id") != session or receipt.get("receipt_id") != session
            or type(receipt.get("lease_generation")) is not int
            or receipt["lease_generation"] != (task.get("lease") or {}).get("generation")
            or path not in receipt.get("artifacts", [])
            or not SHA.fullmatch(str(receipt.get("input_head", "")))
            or receipt.get("input_head") != research.get("input_head")
            or any((receipt.get("authority_assertion") or {}).get(k) is not False for k in ASSERTION)
            or receipt.get("status") != "BLOCKED"):
        raise EdgeObservationReadError("OBSERVATION_RECEIPT_BINDING_MISMATCH")


def observe_edge_task(snapshot, task_id, *, declared_routes=None, validated_adapters=None):
    """Project one producer task at one immutable Git HEAD.

    The snapshot's read method must verify Git blobs (github_state.Snapshot or
    the offline CLI adapter). No network, source-content reads, handoff traversal,
    validator inference, task creation, adapter activation or repository writes.
    """
    reader = _BoundedReads(snapshot, task_id)
    _assert_pre_outcome({"declared_routes": declared_routes, "validated_adapters": validated_adapters})
    # Reuse the existing exact epoch/policy/membrane preflight without a store,
    # snapshot acquisition, commit or model. Only its two bounded reads run.
    context = V2StateStore(None)
    context._preflight(reader)
    binding = {key: context.last_preflight[key] for key in
               ("research_epoch_id", "epoch_manifest_hash", "policy_hash")}
    task_path = PREFIX + f"tasks/{task_id}.json"
    task = reader.read(task_path)
    if task.get("task_id") != task_id:
        raise EdgeObservationReadError("OBSERVATION_TASK_ID_MISMATCH")
    if task.get("task_type") not in PRODUCERS or task.get("research_contract_version") != "v2-core":
        raise EdgeObservationReadError("V2_PRODUCER_TASK_REQUIRED")
    assert_authority_closed(task.get("authority") or {})
    execution = task.get("execution") or {}
    task_binding = execution.get("v2_epoch_binding")
    if task_binding is not None and task_binding != binding:
        raise EdgeObservationReadError("OBSERVATION_TASK_EPOCH_BINDING_MISMATCH")
    stage = ("document_or_fundamental_research" if task["task_type"] in
             ("FUNDAMENTAL_RESEARCH", "EVENT_DOCUMENT") else "mechanism_research")
    path = artifact_path(task, stage)
    completion = (execution.get("completed_stages") or {}).get(stage)
    research, producer = None, None
    acquisition_state = "NOT_PROJECTED_NO_RESEARCH_ARTIFACT"
    if completion and (completion.get("artifact") != path or path not in reader.blobs):
        raise EdgeObservationReadError("OBSERVATION_COMPLETED_STAGE_REFERENCE_MISMATCH")
    if path in reader.blobs:
        if task_binding != binding:
            raise EdgeObservationReadError("OBSERVATION_RESEARCH_EPOCH_BINDING_REQUIRED")
        research = reader.read(path)
        assert_authority_closed(research.get("authority") or {})
        if research.get("outcome_accessed") is not False or research.get("economic_result") != "NOT_OBSERVED":
            raise EdgeObservationReadError("OBSERVATION_PRE_OUTCOME_MARKERS_REQUIRED")
        if research.get("stage") != stage:
            raise EdgeObservationReadError("OBSERVATION_RESEARCH_STAGE_MISMATCH")
        if completion:
            if completion.get("artifact_hash") != canonical_hash(research):
                raise EdgeObservationReadError("OBSERVATION_ARTIFACT_CONTENT_HASH_MISMATCH")
        else:
            _receipt_bound(reader, task, path, research)
        has_output = bool(research.get("engine_output") or research.get("candidate"))
        if has_output or "research_epoch_id" in research or "epoch_manifest_hash" in research:
            if (research.get("research_contract_version") != "v2-core"
                    or research.get("research_epoch_id") != binding["research_epoch_id"]
                    or research.get("epoch_manifest_hash") != binding["epoch_manifest_hash"]):
                raise EdgeObservationReadError("OBSERVATION_ARTIFACT_EPOCH_MISMATCH")
        elif not research.get("blocker") or completion:
            raise EdgeObservationReadError("OBSERVATION_UNBOUND_RESEARCH_ARTIFACT")
        source = research.get("source_path")
        if has_output and source is None:
            raise EdgeObservationReadError("OBSERVATION_SOURCE_BINDING_REQUIRED")
        if source is not None:
            if (not isinstance(source, str) or not source.startswith(PREFIX + "sources/")
                    or "/../" in source or "/./" in source
                    or not SHA.fullmatch(str(research.get("source_blob", "")))
                    or reader.blobs.get(source) != research["source_blob"]):
                raise EdgeObservationReadError("OBSERVATION_SOURCE_BLOB_BINDING_MISMATCH")
        output = research.get("engine_output") or {}
        candidate = output.get("candidate") or {}
        if candidate:
            if (output.get("engine_family") != ENGINE_REGISTRY[PRODUCERS[task["task_type"]]].family
                    or any((research.get("candidate") or {}).get(k) != v for k, v in candidate.items())):
                raise EdgeObservationReadError("OBSERVATION_CANDIDATE_BINDING_MISMATCH")
            lineage = task.get("lineage") or {}
            if (lineage.get("hypothesis_id") and lineage["hypothesis_id"] != candidate.get("hypothesis_id")):
                raise EdgeObservationReadError("OBSERVATION_LINEAGE_BINDING_MISMATCH")
            if (lineage.get("generation_id") and lineage["generation_id"] != candidate.get("generation_id")):
                raise EdgeObservationReadError("OBSERVATION_LINEAGE_GENERATION_MISMATCH")
            if "generation" in lineage and "G" + str(lineage["generation"]).removeprefix("G") != candidate.get("generation_id"):
                raise EdgeObservationReadError("OBSERVATION_LINEAGE_GENERATION_MISMATCH")
        if research.get("blocker") or (research.get("screen") or {}).get("status") == "BLOCK":
            acquisition_state = "NOT_PROJECTED_UPSTREAM_BLOCKED"
        elif not candidate or not (research.get("dossier") or {}).get("dossier"):
            acquisition_state = "NOT_PROJECTED_NO_DOSSIER"
        else:
            producer = build_producer_test_readiness(output, research["dossier"]["dossier"])
            acquisition_state = "PROJECTED_FROM_BOUND_RESEARCH_DOSSIER"
    elif task_binding is None and (execution.get("completed_stages") or execution.get("session_id")):
        raise EdgeObservationReadError("OBSERVATION_EXECUTED_TASK_EPOCH_BINDING_REQUIRED")

    arguments = {"task": task, "research": research}
    if producer is not None:
        arguments.update(producer_readiness=producer, declared_routes=declared_routes,
                         validated_adapters=validated_adapters)
    edge = build_edge_observability_projection(**arguments)
    observation = {
        "schema_version": "oracle-v2-task-observation-v1",
        "snapshot_head": reader.head,
        "research_epoch_binding": binding,
        "task_id": task_id,
        "task_status": task.get("status", "UNKNOWN"),
        "research_stage": stage,
        "research_artifact_status": "PRESENT_AND_BOUND" if research is not None else "ABSENT",
        "scope": "PRODUCER_TASK_ONLY_NOT_VALIDATOR_OR_SITE",
        "task_epoch_binding": "VERIFIED" if task_binding is not None else "NOT_BOUND_UNEXECUTED",
        "source_artifacts": dict(sorted(reader.read_blobs.items())),
        "source_packet_binding": ({"path": research["source_path"], "blob": research["source_blob"]}
                                  if research and research.get("source_path") else None),
        "acquisition_projection_state": acquisition_state,
        "acquisition_catalog_applied": producer is not None,
        "edge_projection": edge,
        "network_execution_authorized": False,
        "network_call_performed": False,
        "outcome_accessed": False,
        "economic_result": "NOT_OBSERVED",
        "authority": deepcopy(edge["authority"]),
        "projection_only": True,
    }
    observation["observation_hash"] = canonical_hash(observation)
    return observation
