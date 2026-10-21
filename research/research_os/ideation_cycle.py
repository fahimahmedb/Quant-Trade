"""Cycle-level coordinator for passive Multi-Source Ideation Intake V2.

The coordinator provides the missing durable cycle/receipt/disposition contracts while
preserving the hard boundary: it cannot create operational work or scientific truth.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping, Sequence

from .multi_source_ideation import POLICIES, TERMINAL_STATES, barrier


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def raw_proposal_receipt(*, cycle_id: str, artifact: Mapping[str, Any], provenance: Mapping[str, Any]) -> dict:
    if artifact.get("policy_kind") not in POLICIES or artifact.get("status") not in TERMINAL_STATES:
        raise ValueError("receipt requires a terminal bounded policy artifact")
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


def ideation_cycle(*, cycle_id: str, context_snapshot: Mapping[str, Any], artifacts: Sequence[Mapping[str, Any]], receipts: Sequence[Mapping[str, Any]]) -> dict:
    h = context_snapshot.get("context_snapshot_hash")
    state = barrier(artifacts, str(h))
    receipt_by_policy = {r.get("policy_kind"): r for r in receipts if r.get("cycle_id") == cycle_id}
    if state.get("intake_allowed"):
        missing = set(POLICIES) - set(receipt_by_policy)
        if missing:
            return {
                "schema_version": "ideation-cycle-v2", "cycle_id": cycle_id,
                "context_snapshot_hash": h, "status": "WAITING_FOR_RECEIPTS",
                "missing_receipts": sorted(missing), "intake_allowed": False,
                "outcome_accessed": False,
            }
    return {
        "schema_version": "ideation-cycle-v2", "cycle_id": cycle_id,
        "context_snapshot_hash": h, "status": state["status"],
        "terminal_statuses": {a["policy_kind"]: a["status"] for a in artifacts},
        "receipt_ids": {k: v.get("receipt_id") for k, v in receipt_by_policy.items()},
        "intake_allowed": bool(state.get("intake_allowed")),
        "outcome_accessed": False,
        "ready_tasks_created": 0, "candidates_created": 0,
    }


def proposal_disposition(*, proposal_id: str, intake_decision: Mapping[str, Any], lineage: Mapping[str, Any], duplicate: Mapping[str, Any], implementability: Mapping[str, Any]) -> dict:
    decision = str(intake_decision.get("decision") or "INVALID_INPUT")
    allowed = {"ELIGIBLE_FOR_DISCOVERY", "NEEDS_DISCOVERY_SYNTHESIS", "NOT_ELIGIBLE", "REVIEW_REQUIRED", "STALE_REQUALIFICATION_REQUIRED"}
    if decision not in allowed:
        raise ValueError("unrecognized passive intake disposition")
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
