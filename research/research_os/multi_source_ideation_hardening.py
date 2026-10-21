"""Adversarial hardening for Multi-Source Ideation Intake V2.

This stays passive: no queue, lease, scheduler, Candidate, experiment, producer,
Control Plane, Oracle, Economic Identity, or runtime activation semantics.
"""
from __future__ import annotations

import hashlib
import json
import threading
from copy import deepcopy
from typing import Any, Mapping, Sequence

from .multi_source_ideation import POLICIES, _reject_outcome_fields


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def proposal_identity(*, policy_kind: str, context_snapshot_hash: str, payload: Mapping[str, Any], provenance: Mapping[str, Any]) -> dict:
    if policy_kind not in POLICIES:
        raise ValueError("unknown ideation policy")
    if not context_snapshot_hash or not provenance:
        raise ValueError("proposal identity requires frozen context and provenance")
    bounded_payload = deepcopy(dict(payload))
    bounded_provenance = deepcopy(dict(provenance))
    _reject_outcome_fields(bounded_payload, "proposal_identity.payload")
    _reject_outcome_fields(bounded_provenance, "proposal_identity.provenance")
    body = {
        "policy_kind": policy_kind,
        "context_snapshot_hash": context_snapshot_hash,
        "payload_hash": _hash(bounded_payload),
        "provenance_hash": _hash(bounded_provenance),
    }
    return {**body, "proposal_id": _hash(body)}


def ancestry_check(proposal: Mapping[str, Any], ancestry: Sequence[Mapping[str, Any]]) -> dict:
    """Exact ancestry is dispositive; labels alone never are."""
    parents = {str(x) for x in proposal.get("ancestor_ids", []) if x}
    if not parents:
        return {"classification": "UNKNOWN", "matches": []}
    matches = []
    for row in ancestry:
        rid = str(row.get("proposal_id") or row.get("candidate_id") or row.get("memory_id") or "")
        lineage = {str(x) for x in row.get("ancestor_ids", []) if x}
        if rid in parents or parents.intersection(lineage):
            matches.append(rid)
    return {"classification": "ANCESTRY_MATCH" if matches else "DISTINCT", "matches": sorted(x for x in matches if x)}


def combine_duplicate_evidence(*, semantic: Mapping[str, Any], ancestry: Mapping[str, Any]) -> dict:
    if ancestry.get("classification") == "ANCESTRY_MATCH":
        return {"classification": "ANCESTRY_MATCH", "basis": "EXPLICIT_LINEAGE"}
    classification = str(semantic.get("classification") or "UNKNOWN")
    if classification in {"EXACT_DUPLICATE", "POSSIBLE_EXPRESSION_EQUIVALENCE", "DISTINCT", "UNKNOWN", "REVIEW_REQUIRED"}:
        return {"classification": classification, "basis": "SEMANTIC_IDENTITY"}
    return {"classification": "REVIEW_REQUIRED", "basis": "UNRECOGNIZED_DUPLICATE_EVIDENCE"}


class SourceClaimLedger:
    """Atomic passive claim registry. A claim is not a lease and has no expiry/heartbeat."""
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._claims: dict[tuple[str, str], dict] = {}

    def claim(self, *, source_identity: str, context_snapshot_hash: str, policy_kind: str) -> dict:
        if policy_kind not in POLICIES or not source_identity or not context_snapshot_hash:
            raise ValueError("invalid source claim")
        key = (context_snapshot_hash, source_identity)
        with self._lock:
            prior = self._claims.get(key)
            if prior and prior["state"] in {"HELD", "TRANSFERRED"}:
                if prior["policy_kind"] == policy_kind:
                    return deepcopy(prior)
                raise ValueError("SOURCE_ALREADY_CLAIMED_IN_CONTEXT")
            row = {
                "claim_id": _hash({"context": context_snapshot_hash, "source": source_identity, "policy": policy_kind}),
                "context_snapshot_hash": context_snapshot_hash,
                "source_identity": source_identity,
                "policy_kind": policy_kind,
                "state": "HELD",
                "scientifically_consumed": False,
            }
            self._claims[key] = row
            return deepcopy(row)

    def transition(self, claim_id: str, target: str) -> dict:
        if target not in {"RELEASED", "TRANSFERRED"}:
            raise ValueError("invalid passive claim transition")
        with self._lock:
            for key, row in self._claims.items():
                if row["claim_id"] != claim_id:
                    continue
                if row["state"] == target:
                    return deepcopy(row)
                if row["state"] != "HELD":
                    raise ValueError("claim terminal state cannot be rewritten")
                row = {**row, "state": target, "scientifically_consumed": False}
                self._claims[key] = row
                return deepcopy(row)
        raise KeyError(claim_id)

    def snapshot(self) -> list[dict]:
        with self._lock:
            return [deepcopy(v) for _, v in sorted(self._claims.items())]


class DurableProposalLedger:
    """Thread-safe, restartable passive ledger with caller-supplied durable snapshot."""
    FORBIDDEN_KEYS = {"lease", "lease_owner", "heartbeat", "worker_owner", "retry_at", "scheduler_state"}
    FORBIDDEN_STATUS = {"READY", "LEASED", "RUNNING", "RETRY"}

    @classmethod
    def _reject_operational_keys(cls, value: Any, path: str = "record") -> None:
        if isinstance(value, Mapping):
            for key, nested in value.items():
                normalized = str(key).strip().lower()
                if normalized in cls.FORBIDDEN_KEYS:
                    raise ValueError(f"operational work semantics forbidden in Proposal Ledger: {path}.{key}")
                cls._reject_operational_keys(nested, f"{path}.{key}")
        elif isinstance(value, (list, tuple)):
            for index, nested in enumerate(value):
                cls._reject_operational_keys(nested, f"{path}[{index}]")

    def __init__(self, rows: Sequence[Mapping[str, Any]] = ()) -> None:
        self._lock = threading.Lock()
        self._rows: dict[str, dict] = {}
        for row in rows:
            self.persist(row)

    def persist(self, record: Mapping[str, Any]) -> str:
        row = deepcopy(dict(record))
        self._reject_operational_keys(row)
        if str(row.get("status", "")).upper() in self.FORBIDDEN_STATUS:
            raise ValueError("operational work semantics forbidden in Proposal Ledger")
        rid = str(row.get("proposal_id") or _hash(row))
        with self._lock:
            prior = self._rows.get(rid)
            if prior is not None and prior != row:
                raise ValueError("immutable proposal identity collision")
            self._rows[rid] = row
        return rid

    def snapshot(self) -> list[dict]:
        with self._lock:
            return [deepcopy(v) for _, v in sorted(self._rows.items())]


def qualify_for_discovery(*, proposal: Mapping[str, Any], context_snapshot_hash: str, memory: Mapping[str, Any], duplicate: Mapping[str, Any], implementability: Mapping[str, Any]) -> dict:
    if proposal.get("context_snapshot_hash") != context_snapshot_hash:
        return {"decision": "STALE_REQUALIFICATION_REQUIRED", "eligible_for_discovery": False}
    if proposal.get("artifact_kind") != "IDEA_PROPOSAL":
        return {"decision": "NEEDS_DISCOVERY_SYNTHESIS", "eligible_for_discovery": proposal.get("artifact_kind") == "IDEATION_SEED"}
    if memory.get("classification") in {"KNOWN_EXACT_NEGATIVE", "SUPERSEDED"}:
        return {"decision": "NOT_ELIGIBLE", "eligible_for_discovery": False}
    if duplicate.get("classification") in {"EXACT_DUPLICATE", "ANCESTRY_MATCH"}:
        return {"decision": "NOT_ELIGIBLE", "eligible_for_discovery": False}
    if duplicate.get("classification") in {"UNKNOWN", "REVIEW_REQUIRED"}:
        return {"decision": "REVIEW_REQUIRED", "eligible_for_discovery": False}
    if implementability.get("admissible") is not True:
        return {"decision": "NOT_ELIGIBLE", "eligible_for_discovery": False}
    return {
        "decision": "ELIGIBLE_FOR_DISCOVERY",
        "eligible_for_discovery": True,
        "boundary": "ELIGIBLE_FOR_DISCOVERY",
        "ready_task_created": False,
        "candidate_created": False,
    }
