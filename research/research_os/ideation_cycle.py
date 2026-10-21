"""Cycle-level coordinator for passive Multi-Source Ideation Intake V2.

The coordinator provides durable cycle/receipt/disposition contracts while
preserving the hard boundary: it cannot create operational work or scientific truth.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping, Sequence

from .multi_source_ideation import (
    POLICIES,
    TERMINAL_STATES,
    _reject_outcome_fields,
    barrier,
    validate_policy_input,
)


def _hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    ).hexdigest()


def raw_proposal_receipt(
    *, cycle_id: str, artifact: Mapping[str, Any], provenance: Mapping[str, Any]
) -> dict:
    """Bind one terminal policy artifact to its passive source provenance.

    Receipts remain pre-outcome: neither the artifact nor provenance may smuggle
    empirical/economic outcomes into the ideation layer.
    """
    if artifact.get("policy_kind") not in POLICIES or artifact.get("status") not in TERMINAL_STATES:
        raise ValueError("receipt requires a terminal bounded policy artifact")
    _reject_outcome_fields(artifact, "receipt.artifact")
    _reject_outcome_fields(provenance, "receipt.provenance")
    body = {
        "schema_version": "raw-proposal-receipt-v2",
        "cycle_id": cycle_id,
        "policy_kind": artifact["policy_kind"],
        "status": artifact["status"],
        "artifact_kind": artifact.get("artifact_kind"),
        "context_snapshot_hash": artifact.get("context_snapshot_hash"),
        "artifact_hash": _hash(artifact),
        "provenance": deepcopy(dict(provenance)),
        "outcome_accessed": False,
    }
    body["receipt_id"] = _hash(body)
    return body


def validate_raw_proposal_receipt(
    receipt: Mapping[str, Any], artifact: Mapping[str, Any], *, cycle_id: str
) -> None:
    """Fail closed unless a receipt binds exactly to the supplied artifact."""
    if not isinstance(receipt, Mapping):
        raise ValueError("raw proposal receipt must be a mapping")
    if receipt.get("schema_version") != "raw-proposal-receipt-v2":
        raise ValueError("unsupported raw proposal receipt schema")
    if receipt.get("cycle_id") != cycle_id:
        raise ValueError("raw proposal receipt cycle mismatch")
    _reject_outcome_fields(artifact, "receipt.artifact")
    _reject_outcome_fields(receipt.get("provenance", {}), "receipt.provenance")
    expected_fields = {
        "policy_kind": artifact.get("policy_kind"),
        "status": artifact.get("status"),
        "artifact_kind": artifact.get("artifact_kind"),
        "context_snapshot_hash": artifact.get("context_snapshot_hash"),
        "artifact_hash": _hash(artifact),
    }
    for key, expected in expected_fields.items():
        if receipt.get(key) != expected:
            raise ValueError(f"raw proposal receipt {key} mismatch")
    if receipt.get("outcome_accessed") is not False:
        raise ValueError("raw proposal receipt outcome_accessed must remain false")
    body = deepcopy(dict(receipt))
    supplied = body.pop("receipt_id", None)
    if not supplied or _hash(body) != supplied:
        raise ValueError("raw proposal receipt id mismatch")


def ideation_cycle(
    *,
    cycle_id: str,
    context_snapshot: Mapping[str, Any],
    artifacts: Sequence[Mapping[str, Any]],
    receipts: Sequence[Mapping[str, Any]],
) -> dict:
    validate_policy_input(context_snapshot)
    h = context_snapshot.get("context_snapshot_hash")
    state = barrier(artifacts, str(h))

    receipt_by_policy: dict[str, Mapping[str, Any]] = {}
    for receipt in receipts:
        if receipt.get("cycle_id") != cycle_id:
            continue
        policy = str(receipt.get("policy_kind") or "")
        if policy not in POLICIES:
            raise ValueError("raw proposal receipt has invalid policy")
        if policy in receipt_by_policy:
            raise ValueError("duplicate raw proposal receipt for policy in cycle")
        receipt_by_policy[policy] = receipt

    artifact_by_policy = {str(a.get("policy_kind")): a for a in artifacts}
    for policy, receipt in receipt_by_policy.items():
        artifact = artifact_by_policy.get(policy)
        if artifact is None:
            raise ValueError("raw proposal receipt has no matching policy artifact")
        validate_raw_proposal_receipt(receipt, artifact, cycle_id=cycle_id)

    if state.get("intake_allowed"):
        missing = set(POLICIES) - set(receipt_by_policy)
        if missing:
            return {
                "schema_version": "ideation-cycle-v2",
                "cycle_id": cycle_id,
                "context_snapshot_hash": h,
                "status": "WAITING_FOR_RECEIPTS",
                "missing_receipts": sorted(missing),
                "intake_allowed": False,
                "outcome_accessed": False,
            }
        # All policies are terminal and all receipts are exact-bound at this point.
        for policy in POLICIES:
            validate_raw_proposal_receipt(
                receipt_by_policy[policy], artifact_by_policy[policy], cycle_id=cycle_id
            )

    return {
        "schema_version": "ideation-cycle-v2",
        "cycle_id": cycle_id,
        "context_snapshot_hash": h,
        "status": state["status"],
        "terminal_statuses": {a["policy_kind"]: a["status"] for a in artifacts},
        "receipt_ids": {k: v.get("receipt_id") for k, v in receipt_by_policy.items()},
        "intake_allowed": bool(state.get("intake_allowed")),
        "outcome_accessed": False,
        "ready_tasks_created": 0,
        "candidates_created": 0,
    }


def proposal_disposition(
    *,
    proposal_id: str,
    intake_decision: Mapping[str, Any],
    lineage: Mapping[str, Any],
    duplicate: Mapping[str, Any],
    implementability: Mapping[str, Any],
) -> dict:
    decision = str(intake_decision.get("decision") or "INVALID_INPUT")
    allowed = {
        "ELIGIBLE_FOR_DISCOVERY",
        "NEEDS_DISCOVERY_SYNTHESIS",
        "NOT_ELIGIBLE",
        "REVIEW_REQUIRED",
        "STALE_REQUALIFICATION_REQUIRED",
    }
    if decision not in allowed:
        raise ValueError("unrecognized passive intake disposition")
    _reject_outcome_fields(lineage, "disposition.memory_lineage")
    _reject_outcome_fields(duplicate, "disposition.duplicate")
    _reject_outcome_fields(implementability, "disposition.implementability")
    return {
        "schema_version": "ideation-disposition-v2",
        "proposal_id": proposal_id,
        "decision": decision,
        "eligible_for_discovery": intake_decision.get("eligible_for_discovery") is True,
        "memory_lineage": deepcopy(dict(lineage)),
        "duplicate": deepcopy(dict(duplicate)),
        "light_implementability": deepcopy(dict(implementability)),
        "operational_admission": False,
        "scientific_verdict": "NOT_PERFORMED",
        "economic_result": "NOT_OBSERVED",
        "outcome_accessed": False,
    }
