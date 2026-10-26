"""Read-only Scientific Memory feedback for candidate screening.

This adapter intentionally creates no store and no scheduler authority. It derives
qualified memory views from the immutable imported legacy ledger, then applies
semantic-family rules to a generated candidate. Lexical overlap remains review
metadata only; it is never treated as empirical similarity or scientific identity.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping, Optional

from .research_intelligence import (
    UNKNOWN,
    identity_complete,
    identity_explanation,
    memory_relation,
    semantic_identity,
)
from .scientific_memory import normalize_legacy_record, validate_memory_record
from .scientific_store import sha256_json


def qualified_legacy_memory_view(
    records: Iterable[Mapping[str, Any]],
    source_manifest: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Normalize the immutable legacy ledger into a read-only qualified view.

    Canonical records are not copied into another persistent truth store. Records
    that fail canonical qualification remain visible in review metadata but cannot
    influence semantic suppression.
    """
    canonical: List[Dict[str, Any]] = []
    review: List[Dict[str, Any]] = []
    for raw in records:
        normalized = normalize_legacy_record(raw, source_manifest)
        if normalized.get("canonical") is True:
            validate_memory_record(normalized, require_canonical=True)
            canonical.append(normalized)
        else:
            review.append({
                "memory_id": normalized.get("memory_id"),
                "scientific_disposition": normalized.get("scientific_disposition"),
                "record_status": normalized.get("record_status"),
                "reason_codes": list(normalized.get("reason_codes") or []),
                "source_identity": deepcopy(normalized.get("source_identity") or {}),
            })
    canonical.sort(key=lambda item: item["memory_id"])
    review.sort(key=lambda item: str(item.get("memory_id")))
    return {
        "schema_version": "qualified-legacy-memory-view-v1",
        "canonical_records": canonical,
        "canonical_count": len(canonical),
        "review_records": review,
        "review_count": len(review),
        "persistent_store_created": False,
        "view_hash": sha256_json({
            "canonical": [item["memory_id"] for item in canonical],
            "review": review,
        }),
    }


def candidate_memory_contract(candidate: Mapping[str, Any]) -> Dict[str, Any]:
    """Expose only known semantic dimensions; never infer missing economics."""
    explicit = candidate.get("identity") if isinstance(candidate.get("identity"), Mapping) else {}
    evidence = candidate.get("documentary_evidence") if isinstance(candidate.get("documentary_evidence"), Mapping) else {}
    packet = evidence.get("packet") if isinstance(evidence.get("packet"), Mapping) else {}

    def value(field: str, *, candidate_field: Optional[str] = None, packet_field: Optional[str] = None) -> Any:
        if explicit.get(field) not in (None, ""):
            return explicit.get(field)
        key = candidate_field or field
        if candidate.get(key) not in (None, ""):
            return candidate.get(key)
        if packet_field and packet.get(packet_field) not in (None, ""):
            return packet.get(packet_field)
        return UNKNOWN

    identity = {
        "mechanism": value("mechanism", candidate_field="mechanism"),
        "payer": value("payer"),
        "constrained_actor": value("constrained_actor", packet_field="actor"),
        "timing_clock": value("timing_clock"),
        "universe": value("universe"),
        "economic_exposure": value("economic_exposure"),
        "instrument": value("instrument", packet_field="instrument"),
        "source_family": value("source_family"),
        "evidence_identity": value("evidence_identity", packet_field="content_hash"),
    }
    contract = deepcopy(dict(candidate))
    contract["identity"] = identity
    if not contract.get("candidate_id"):
        contract["candidate_id"] = contract.get("hypothesis_id")
    if not contract.get("protocol_id"):
        hid, gid = contract.get("hypothesis_id"), contract.get("generation_id")
        if hid and gid:
            contract["protocol_id"] = f"{hid}:{gid}"
    return contract


def _protocol_key(value: Any) -> str:
    if value is None:
        return UNKNOWN
    text = str(value).strip().lower()
    return text if text and text.upper() != UNKNOWN else UNKNOWN


def scientific_memory_feedback(
    candidate: Mapping[str, Any],
    memory_records: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Return a semantic screen decision without scheduling or executing work."""
    contract = candidate_memory_contract(candidate)
    identity = semantic_identity(contract)
    records = list(memory_records)
    relations = [memory_relation(contract, record) for record in records]
    qualified = [item for item in relations if item.get("qualified")]
    same_family = [item for item in qualified if item.get("same_semantic_family")]

    base = {
        "candidate_id": contract.get("candidate_id"),
        "identity": identity_explanation(identity),
        "memory_influence": same_family,
        "qualified_relation_count": len(qualified),
        "same_family_count": len(same_family),
        "scheduler_mutation": False,
        "persistent_store_created": False,
        "empirical_similarity_computed": False,
        "empirical_correlation": UNKNOWN,
        "model_commentary_used_as_evidence": False,
    }

    if not identity_complete(identity):
        return {
            **base,
            "allow_candidate_progress": False,
            "action": "ARCHAEOLOGY_LOOKUP",
            "reason_codes": ["SEMANTIC_IDENTITY_UNRESOLVED", "UNKNOWN_IDENTITY_IS_NOT_NOVELTY"],
            "scientific_equivalence": "NOT_ESTABLISHED",
        }

    dispositions = {str(item.get("scientific_disposition")) for item in same_family}
    if "NEGATIVE" in dispositions:
        return {
            **base,
            "allow_candidate_progress": False,
            "action": "NO_BUILD",
            "reason_codes": ["KNOWN_NEGATIVE_SAME_SEMANTIC_FAMILY"],
            "scientific_equivalence": "ESTABLISHED_SAME_SEMANTIC_FAMILY",
        }

    if "INVALIDATED_PROTOCOL" in dispositions:
        invalid_ids = set()
        for record in records:
            relation = memory_relation(contract, record)
            if relation.get("same_semantic_family") and record.get("scientific_disposition") == "INVALIDATED_PROTOCOL":
                invalid_ids.add(_protocol_key((record.get("identity") or {}).get("protocol_id")))
        proposed = _protocol_key(contract.get("protocol_id") or (contract.get("identity") or {}).get("protocol_id"))
        if proposed == UNKNOWN or proposed in invalid_ids:
            return {
                **base,
                "allow_candidate_progress": False,
                "action": "REPAIR_PROTOCOL",
                "reason_codes": ["INVALIDATED_PROTOCOL_MUST_CHANGE_BEFORE_RERUN"],
                "scientific_equivalence": "ESTABLISHED_SAME_SEMANTIC_FAMILY",
            }

    if "BLOCKED" in dispositions and contract.get("memory_blockers_resolved") is not True:
        return {
            **base,
            "allow_candidate_progress": False,
            "action": "PARK",
            "reason_codes": ["HISTORICAL_BLOCKER_UNRESOLVED_NOT_NEGATIVE"],
            "scientific_equivalence": "ESTABLISHED_SAME_SEMANTIC_FAMILY",
        }

    if "POSITIVE_BUT_INSUFFICIENT" in dispositions:
        return {
            **base,
            "allow_candidate_progress": False,
            "action": "ESCALATE_VALIDATION",
            "reason_codes": ["POSITIVE_BUT_INSUFFICIENT_NOT_PROMOTED"],
            "scientific_equivalence": "ESTABLISHED_SAME_SEMANTIC_FAMILY",
        }

    reasons = ["NO_QUALIFIED_MEMORY_SUPPRESSION"]
    if "UNEXECUTED" in dispositions:
        reasons.append("HISTORICAL_UNEXECUTED_IS_NOT_FAILURE")
    if "BLOCKED" in dispositions:
        reasons.append("HISTORICAL_BLOCKER_RESOLVED_REOPENED")
    return {
        **base,
        "allow_candidate_progress": True,
        "action": "NO_ACTION",
        "reason_codes": reasons,
        "scientific_equivalence": (
            "ESTABLISHED_SAME_SEMANTIC_FAMILY" if same_family else "NOT_ESTABLISHED"
        ),
    }
