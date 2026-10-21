"""Identity-safe bridge from qualified archaeology provenance to scientific memory."""
from __future__ import annotations
from copy import deepcopy
from typing import Any, Dict, Mapping, List

from .archaeology import finding_provenance_refs, validate_finding
from .scientific_memory import validate_memory_record


def _known(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value.strip().upper() != "UNKNOWN"


def bind_qualified_provenance(memory_record: Mapping[str, Any], finding: Mapping[str, Any]) -> Dict[str, Any]:
    validate_finding(finding)
    if finding["terminal_state"] != "QUALIFIED_CURRENT":
        raise ValueError("only QUALIFIED_CURRENT archaeology may bind canonical provenance")
    if finding["memory_action"] in {"KEEP_REVIEW_ONLY", "NO_MEMORY_MUTATION"}:
        raise ValueError("review/no-mutation archaeology cannot bind canonical memory")

    updated = deepcopy(dict(memory_record))
    validate_memory_record(updated, require_canonical=True)
    source_identity = updated.get("source_identity") or {}
    identity = updated.get("identity") or {}
    admissible = {
        str(v) for v in (
            source_identity.get("hypothesis_id"), source_identity.get("legacy_id"),
            source_identity.get("generation_id"), source_identity.get("archaeology_subject_id"),
            identity.get("research_family_id"), identity.get("protocol_id"),
        ) if _known(v)
    }
    if finding["subject_id"] not in admissible:
        raise ValueError("archaeology subject does not match canonical memory identity")

    protected = {k: deepcopy(updated.get(k)) for k in (
        "scientific_disposition", "epistemic_status", "claim_ceiling", "evidence", "identity"
    )}
    existing = {(x.get("kind"), x.get("ref")) for x in updated.get("provenance") or []}
    for item in finding_provenance_refs(finding):
        key = (item["kind"], item["ref"])
        if key not in existing:
            updated.setdefault("provenance", []).append(item)
            existing.add(key)
    for key, before in protected.items():
        if updated.get(key) != before:
            raise AssertionError(f"archaeology binding mutated protected scientific field: {key}")
    validate_memory_record(updated, require_canonical=True)
    return updated


def supersession_proof_refs(finding: Mapping[str, Any]) -> List[str]:
    validate_finding(finding)
    if finding["history_disposition"] != "SUPERSEDED_WITH_PROOF":
        raise ValueError("finding is not an explicit SUPERSEDED_WITH_PROOF decision")
    refs = [x["ref"] for x in finding_provenance_refs(finding)]
    if not refs:
        raise ValueError("supersession requires immutable proof refs")
    return refs
