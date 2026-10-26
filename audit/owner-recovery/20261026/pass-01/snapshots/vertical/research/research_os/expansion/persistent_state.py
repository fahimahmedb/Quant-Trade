from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import os
import tempfile
from threading import RLock

from research.research_os.legacy import LegacyKnowledgeBase
from research.research_os.scientific_store import build_scientific_ledgers, sha256_json
from .live_receipts import run_with_live_receipts


def _json_object(payload: Any) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("immutable payload must be an object")

    def check(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if not isinstance(key, str):
                    raise ValueError("immutable object keys must be strings")
                check(item)
        elif isinstance(value, (list, tuple)):
            for item in value:
                check(item)

    check(payload)
    return json.loads(json.dumps(payload, allow_nan=False, ensure_ascii=False))


def _unique_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate immutable JSON field")
        result[key] = value
    return result


def write_immutable_json(path: Path, payload: Dict[str, Any]) -> None:
    """Publish complete content once; replay requires the same canonical hash.

    A hard link exposes only a fully fsynced file and refuses replacement. The
    caller must use a filesystem supporting atomic hard links within a directory.
    """
    frozen = _json_object(payload)
    record = {"payload_hash": sha256_json(frozen), "payload": frozen}
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".immutable-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(record, stream, sort_keys=True, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            if sha256_json(read_immutable_json(path)) != record["payload_hash"]:
                raise ValueError("immutable checkpoint mutation rejected")
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        os.unlink(temporary)


def read_immutable_json(path: Path) -> Dict[str, Any]:
    record = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_fields)
    if not isinstance(record, dict) or set(record) != {"payload_hash", "payload"}:
        raise ValueError("checkpoint envelope invalid")
    frozen = _json_object(record["payload"])
    if record["payload_hash"] != sha256_json(frozen):
        raise ValueError("checkpoint hash mismatch")
    return frozen


class ImmutableArtifactRegistry:
    """Content-addressed registry: an identifier may be written once or replayed byte-equivalently."""

    def __init__(self, registry_id: str) -> None:
        self.registry_id = registry_id
        self._entries: Dict[str, Dict[str, Any]] = {}
        self._lock = RLock()

    def register(self, artifact_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            if not isinstance(artifact_id, str) or not artifact_id:
                raise ValueError("artifact identity must be a nonempty string")
            frozen = _json_object(payload)
            artifact_hash = sha256_json(frozen)
            current = self._entries.get(artifact_id)
            if current is not None:
                if current["artifact_hash"] != artifact_hash:
                    raise ValueError(f"immutable artifact mutation rejected: {artifact_id}")
                return deepcopy(current)
            record = {
                "artifact_id": artifact_id,
                "artifact_hash": artifact_hash,
                "payload": frozen,
            }
            self._entries[artifact_id] = record
            return deepcopy(record)

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            entries = [deepcopy(self._entries[key]) for key in sorted(self._entries)]
            return {
                "registry_id": self.registry_id,
                "entry_count": len(entries),
                "entries": entries,
                "immutable": True,
            }


class ForwardGenerationRegistry(ImmutableArtifactRegistry):
    def register_generation(self, registration: Dict[str, Any]) -> Dict[str, Any]:
        if registration["material_change_requires_new_generation"] is not True:
            raise ValueError("forward generation must require a new generation for material change")
        return self.register(registration["prospective_contract_id"], registration)

    def consume_future_observation(self, contract_id: str, observation: Dict[str, Any]) -> None:
        record = self._entries.get(contract_id)
        if record is None:
            raise KeyError(contract_id)
        payload = record["payload"]
        if payload["observation_authorization"] != "AUTHORIZED_FOR_EXACT_SCOPE":
            raise PermissionError("prospective observation is not authorized")
        raise NotImplementedError("observation ingestion is intentionally outside this build authority")


def build_persistent_final_shape(
    fixture: Dict[str, Any],
    *,
    legacy_ledger_path: Optional[Path] = None,
) -> Dict[str, Any]:
    result = run_with_live_receipts(fixture)
    base = Path(__file__).resolve().parents[1]
    legacy = LegacyKnowledgeBase.load(base, legacy_ledger_path)

    legacy_screen: List[Dict[str, Any]] = [
        legacy.screen_candidate(output["candidate"])
        for output in result["engine_outputs"]
    ]
    exact_duplicates = [
        screen for screen in legacy_screen
        if screen["status"] == "BLOCK_EXACT_LEGACY_DUPLICATE"
    ]

    bundle = build_scientific_ledgers(
        run_id=result["run_id"],
        outputs=result["engine_outputs"],
        timestamp="2026-10-15T13:00:00Z",
    )
    ledger = bundle["scientific_ledger"]
    ledger.append("LEGACY_REFERENCE", legacy.summary())
    for screen in legacy_screen:
        ledger.append("LEGACY_SCREEN", screen)
    for item in result["implementability"]:
        ledger.append("IMPLEMENTABILITY_ASSESSMENT", item)
    for item in result["experiment_envelopes"]:
        ledger.append("EXPERIMENT_ENVELOPE", item)
    for item in result["validations"]:
        ledger.append("INDEPENDENT_VALIDATION", item)
    for item in result["red_teams"]:
        ledger.append("RED_TEAM_ASSESSMENT", item)
    for item in result["portfolio"]["identities"]:
        ledger.append("ECONOMIC_IDENTITY", item)
    ledger.append("PORTFOLIO_MAP", result["portfolio"])
    for item in result["forward_farm"]:
        ledger.append("FORWARD_REGISTRATION", item)
    ledger.append("DECAY_GUARD", result["decay"])
    ledger.append("LEARNING_TELEMETRY", result["learning_telemetry"])
    for receipt in result["worker_receipts"]:
        ledger.append("WORKER_RECEIPT", receipt)

    experiments = ImmutableArtifactRegistry("experiment-registry.v1")
    for envelope in result["experiment_envelopes"]:
        experiments.register(envelope["experiment_id"], envelope)

    forward = ForwardGenerationRegistry("forward-generation-registry.v1")
    for registration in result["forward_farm"]:
        forward.register_generation(registration)

    persistent = dict(result)
    persistent["legacy"] = {
        "summary": legacy.summary(),
        "screen": legacy_screen,
        "gate_status": "BLOCKED_EXACT_DUPLICATE" if exact_duplicates else "PASS",
        "exact_duplicate_count": len(exact_duplicates),
        "historical_truth_mutated": False,
    }
    persistent["scientific_ledger"] = {
        "verified": ledger.verify(),
        "entry_count": len(ledger.entries),
        "entries": deepcopy(ledger.entries),
    }
    persistent["trial_ledger"] = bundle["trial_records"]
    persistent["experiment_registry"] = experiments.snapshot()
    persistent["forward_registry"] = forward.snapshot()
    persistent["persistent_state_status"] = (
        "PASS"
        if result["status"] == "PASS" and ledger.verify() and not exact_duplicates
        else "BLOCKED_OR_FAILED"
    )
    persistent["admission_rule"] = (
        "A candidate with BLOCK_EXACT_LEGACY_DUPLICATE is not admissible for downstream economic evidence. "
        "This deterministic fixture contains no exact duplicate."
    )
    return persistent
