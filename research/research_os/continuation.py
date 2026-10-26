"""Thin durable-continuation contract for already-decided Research OS obligations.

The module has no scheduling or scientific-decision power.  It only proves that
an explicitly declared continuation obligation has exactly one durable closure:
child task, existing child reference, BLOCK, PARK, or terminal disposition.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

from .expansion.v2_core import canonical_hash

CLOSURE_TYPES = {"CHILD_TASK", "EXISTING_CHILD_REF", "BLOCK", "PARK", "TERMINAL"}
_REQUIRED_STOP_FIELDS = {
    "OBLIGATION_ID", "PARENT_OBJECT_ID", "OWNER", "REASON_CODE", "CLAIM_SCOPE",
    "MISSING_CONDITION", "OBSERVABLE_REOPEN_PREDICATE", "AUTHORITY_SCOPE",
    "DATA_SCOPE", "SOURCE_SCOPE", "CREATED_AT", "IDEMPOTENCY_KEY",
}


class ContinuationContractError(ValueError):
    pass


def _known(value: Any) -> bool:
    return value is not None and not isinstance(value, bool) and bool(str(value).strip())


def _validate_identity(closure: Mapping[str, Any]) -> None:
    if not _known(closure.get("OBLIGATION_ID")) or not _known(closure.get("PARENT_OBJECT_ID")):
        raise ContinuationContractError("CONTINUATION_IDENTITY_REQUIRED")
    if not _known(closure.get("IDEMPOTENCY_KEY")):
        raise ContinuationContractError("CONTINUATION_IDEMPOTENCY_KEY_REQUIRED")


def validate_closure(closure: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(closure, Mapping):
        raise ContinuationContractError("CONTINUATION_CLOSURE_MAPPING_REQUIRED")
    row = deepcopy(dict(closure))
    kind = row.get("CLOSURE_TYPE")
    if kind not in CLOSURE_TYPES:
        raise ContinuationContractError("CONTINUATION_CLOSURE_TYPE_INVALID")
    _validate_identity(row)

    if kind in {"BLOCK", "PARK"}:
        missing = sorted(field for field in _REQUIRED_STOP_FIELDS if not _known(row.get(field)))
        if missing:
            raise ContinuationContractError("STOP_CLOSURE_FIELDS_MISSING:" + ",".join(missing))
        if row.get("HISTORICAL_DISPOSITION_MUTATED") not in (None, False):
            raise ContinuationContractError("HISTORICAL_STOP_MUTATION_FORBIDDEN")
    elif kind == "CHILD_TASK":
        if not _known(row.get("CHILD_TASK_ID")):
            raise ContinuationContractError("CHILD_TASK_ID_REQUIRED")
    elif kind == "EXISTING_CHILD_REF":
        if not _known(row.get("EXISTING_CHILD_REF")):
            raise ContinuationContractError("EXISTING_CHILD_REF_REQUIRED")
    elif kind == "TERMINAL":
        if not _known(row.get("TERMINAL_DISPOSITION")) or not _known(row.get("REASON_CODE")):
            raise ContinuationContractError("TERMINAL_DISPOSITION_AND_REASON_REQUIRED")

    body = {key: value for key, value in row.items() if key != "CLOSURE_HASH"}
    expected = canonical_hash(body)
    if row.get("CLOSURE_HASH") not in (None, expected):
        raise ContinuationContractError("CONTINUATION_CLOSURE_HASH_MISMATCH")
    row["CLOSURE_HASH"] = expected
    return row


def validate_obligations(obligations: Sequence[Mapping[str, Any]],
                         closures: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    declared: dict[str, dict[str, Any]] = {}
    for obligation in obligations:
        if not isinstance(obligation, Mapping) or not _known(obligation.get("OBLIGATION_ID")):
            raise ContinuationContractError("DECLARED_OBLIGATION_ID_REQUIRED")
        oid = str(obligation["OBLIGATION_ID"])
        if oid in declared:
            raise ContinuationContractError("DUPLICATE_DECLARED_OBLIGATION:" + oid)
        declared[oid] = deepcopy(dict(obligation))

    indexed: dict[str, list[dict[str, Any]]] = {oid: [] for oid in declared}
    for closure in closures:
        row = validate_closure(closure)
        oid = str(row["OBLIGATION_ID"])
        if oid not in declared:
            raise ContinuationContractError("UNDECLARED_OBLIGATION_CLOSURE:" + oid)
        indexed[oid].append(row)

    missing = sorted(oid for oid, rows in indexed.items() if len(rows) == 0)
    multiple = sorted(oid for oid, rows in indexed.items() if len(rows) > 1)
    if missing:
        raise ContinuationContractError("ORPHANED_CONTINUATION_OBLIGATION:" + ",".join(missing))
    if multiple:
        raise ContinuationContractError("MULTIPLE_DURABLE_CLOSURES:" + ",".join(multiple))

    normalized = [indexed[oid][0] for oid in sorted(indexed)]
    proof = {
        "declared_obligation_count": len(declared),
        "durably_closed_obligation_count": len(normalized),
        "closures": normalized,
        "silent_obligation_loss": False,
        "scheduler_mutation": False,
        "scientific_decision_made": False,
        "authority_expanded": False,
    }
    proof["proof_hash"] = canonical_hash(proof)
    return proof


def reopen_event(stop_closure: Mapping[str, Any], *, reopened_at: str,
                 predicate_evidence_ref: str, event_id: str) -> dict[str, Any]:
    """Append-only reopen event.  The original BLOCK/PARK remains immutable."""
    stop = validate_closure(stop_closure)
    if stop["CLOSURE_TYPE"] not in {"BLOCK", "PARK"}:
        raise ContinuationContractError("ONLY_BLOCK_OR_PARK_MAY_REOPEN")
    if not all(_known(v) for v in (reopened_at, predicate_evidence_ref, event_id)):
        raise ContinuationContractError("REOPEN_EVENT_EVIDENCE_REQUIRED")
    body = {
        "EVENT_TYPE": "CONTINUATION_REOPENED",
        "EVENT_ID": event_id,
        "OBLIGATION_ID": stop["OBLIGATION_ID"],
        "ORIGINAL_CLOSURE_HASH": stop["CLOSURE_HASH"],
        "ORIGINAL_CLOSURE_TYPE": stop["CLOSURE_TYPE"],
        "REOPENED_AT": reopened_at,
        "PREDICATE_EVIDENCE_REF": predicate_evidence_ref,
        "HISTORICAL_DISPOSITION_MUTATED": False,
    }
    return {**body, "EVENT_HASH": canonical_hash(body)}
