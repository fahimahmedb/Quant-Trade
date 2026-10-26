"""Canonical scientific memory over the existing Research OS scientific ledger.

This module is deliberately *not* a second truth store. It normalizes historical
facts into records that can be appended to ``AppendOnlyHashLedger`` and queried by
future research. The contracts are fail-closed: blocked/unexecuted/protocol-invalid
work cannot silently become a negative economic result, and structural overlap is
never reported as empirical similarity or correlation.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from .scientific_store import AppendOnlyHashLedger, sha256_json


SCHEMA_VERSION = "scientific-memory-v1"
LEDGER_KIND = "SCIENTIFIC_MEMORY_RECORD"
UNKNOWN = "UNKNOWN"

SCIENTIFIC_DISPOSITIONS = {
    "NEGATIVE",
    "BLOCKED",
    "UNEXECUTED",
    "POSITIVE_BUT_INSUFFICIENT",
    "INVALIDATED_PROTOCOL",
    "SCIENTIFIC_MEMORY_ONLY",
    "REVIEW_STILL_REQUIRED",
}
RECORD_STATUSES = {
    "ACTIVE",
    "SUPERSEDED_WITH_PROOF",
    "OWNER_GOVERNANCE_NORMALIZED",
    "REVIEW_STILL_REQUIRED",
}
EPISTEMIC_STATUSES = {
    "KNOWN_NEGATIVE",
    "KNOWN_POSITIVE_INSUFFICIENT",
    "UNKNOWN",
    "PROTOCOL_INVALID",
    "STRUCTURAL_ONLY",
    "MEMORY_ONLY",
    "REVIEW_REQUIRED",
}
CLAIM_CEILINGS = {
    "NEGATIVE_SCOPE_ONLY",
    "UNKNOWN_ONLY",
    "SIGNAL_NOT_PROOF",
    "PROTOCOL_WEAKNESS_ONLY",
    "STRUCTURAL_MECHANISM_ONLY",
    "MEMORY_ONLY",
    "REVIEW_ONLY",
}

SESSION_AUTHORITY = {
    "economic_experiment_authorized": False,
    "prospective_observation_authorized": False,
    "real_capital_authorized": False,
    "live_trading_authorized": False,
    "outcome_accessed": False,
}

# Branch names and paths are provenance. They are intentionally absent from this
# list so a move/rename cannot manufacture a new scientific identity.
IDENTITY_FIELDS = (
    "research_family_id",
    "mechanism",
    "protocol_id",
    "universe",
    "instrument",
    "timing_clock",
    "horizon",
    "evidence_identity",
    "evidence_time_boundary",
)
QUERY_FACETS = (
    "mechanism",
    "payer",
    "constrained_actor",
    "timing_clock",
    "universe",
    "instrument",
    "evidence_identity",
    "failure_reason",
    "protocol_weakness",
    "source_family",
    "economic_exposure",
)


def _clean(value: Any) -> Any:
    if value is None:
        return UNKNOWN
    if isinstance(value, str):
        value = value.strip()
        return value if value and value.upper() != UNKNOWN else UNKNOWN
    return value


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return " ".join(_text(v) for v in value)
    return str(value)


def _upper(*values: Any) -> str:
    return " ".join(_text(v).upper() for v in values if v is not None)


def _known(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().upper() not in {UNKNOWN, "NONE", "N/A"}
    return True


def _list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    if isinstance(value, (tuple, set)):
        return list(value)
    return [value]


def _protocol_id(record: Mapping[str, Any]) -> str:
    hypothesis = _clean(record.get("HYPOTHESIS_ID"))
    generation = _clean(record.get("GENERATION_ID"))
    frozen = _clean(record.get("FROZEN_AT"))
    if _known(hypothesis) and _known(generation):
        return f"{hypothesis}:{generation}"
    if _known(hypothesis) and _known(frozen):
        return f"{hypothesis}:frozen:{frozen}"
    return UNKNOWN


def _evidence_identity(record: Mapping[str, Any]) -> str:
    artifact = _clean(record.get("RESULT_ARTIFACT"))
    commit = _clean(record.get("RESULT_COMMIT"))
    source = _clean(record.get("RESULT_SOURCE"))
    if _known(artifact) and _known(commit):
        return f"{commit}:{artifact}"
    if _known(artifact):
        return str(artifact)
    if _known(commit):
        return str(commit)
    if _known(source) and str(source).lower() not in {"owner mission input", "mission-known assertion"}:
        return str(source)
    return UNKNOWN


def _provenance(record: Mapping[str, Any], source_manifest: Optional[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    refs: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for raw in _list(record.get("PROVENANCE")):
        ref = _clean(raw)
        if not _known(ref):
            continue
        ref_s = str(ref)
        kind = "OWNER_ASSERTION" if "owner mission input" in ref_s.lower() else "HISTORICAL_REFERENCE"
        key = f"{kind}:{ref_s}"
        if key not in seen:
            refs.append({"kind": kind, "ref": ref_s})
            seen.add(key)

    artifact = _clean(record.get("RESULT_ARTIFACT"))
    if _known(artifact):
        key = f"RESULT_ARTIFACT:{artifact}"
        if key not in seen:
            refs.append({"kind": "RESULT_ARTIFACT", "ref": str(artifact)})
            seen.add(key)

    commit = _clean(record.get("RESULT_COMMIT"))
    if _known(commit):
        key = f"RESULT_COMMIT:{commit}"
        if key not in seen:
            refs.append({"kind": "RESULT_COMMIT", "ref": str(commit)})
            seen.add(key)

    if source_manifest:
        source_commit = _clean(source_manifest.get("source_commit"))
        ledger_blob = _clean(source_manifest.get("ledger_blob_sha"))
        if _known(source_commit):
            refs.append({"kind": "PINNED_LEDGER_COMMIT", "ref": str(source_commit)})
        if _known(ledger_blob):
            refs.append({"kind": "PINNED_LEDGER_BLOB", "ref": str(ledger_blob)})
    return refs


def _non_owner_provenance(provenance: Sequence[Mapping[str, Any]]) -> bool:
    return any(item.get("kind") != "OWNER_ASSERTION" for item in provenance)


def _classify(record: Mapping[str, Any]) -> tuple[str, str, str, List[str]]:
    result = _upper(record.get("RESULT"))
    economic = _upper(record.get("ECONOMIC_EVIDENCE"))
    statistical = _upper(record.get("STATISTICAL_EVIDENCE"))
    data_integrity = _upper(record.get("DATA_INTEGRITY"))
    operational = _upper(record.get("OPERATIONAL_READINESS"))
    reuse = _upper(record.get("CURRENT_REUSABILITY"))
    point_in_time = _upper(record.get("POINT_IN_TIME_STATUS"))
    falsification_scope = _upper(record.get("FALSIFICATION_SCOPE"))
    blockers = _upper(record.get("OPEN_BLOCKERS"))
    mechanism_evidence = _upper(record.get("MECHANISM_EVIDENCE"))
    limitations = _upper(record.get("KNOWN_LIMITATIONS"))
    combined = " ".join((result, economic, statistical, data_integrity, operational, reuse, point_in_time))

    reason_codes: List[str] = []

    # Protocol/data-capture invalidation is not economic failure. Evaluate this
    # before generic BLOCKED/PARK markers because invalid capture records often
    # contain both.
    invalid_protocol = (
        "PROTOCOL_INVALID" in combined
        or "CAPTURE_INVALID" in combined
        or "INVALID_CAPTURE" in combined
        or "FAILED_IMPLEMENTATION" in combined
        or data_integrity == "FAILED"
        or "NONE; FAILED IMPLEMENTATION DOES NOT KILL MECHANISM" in falsification_scope
    )
    if invalid_protocol:
        reason_codes.append("PROTOCOL_OR_CAPTURE_INVALID")
        return "INVALIDATED_PROTOCOL", "PROTOCOL_INVALID", "PROTOCOL_WEAKNESS_ONLY", reason_codes

    # Explicit pre-look / permission / source blocks remain epistemically unknown.
    blocked_markers = (
        "BLOCKED_DATA_PERMISSION",
        "BLOCKED_BY_PERMISSION",
        "BLOCKED_BY_DATA",
        "PARK_DATA",
        "DATA_RECOVERY_ONLY",
        "GAP_COMPLETION_ONLY",
    )
    if any(marker in combined for marker in blocked_markers):
        reason_codes.append("BLOCKED_BEFORE_ADMISSIBLE_ECONOMIC_CONCLUSION")
        if blockers:
            reason_codes.append("OPEN_BLOCKER_PRESENT")
        return "BLOCKED", "UNKNOWN", "UNKNOWN_ONLY", reason_codes

    known_attempts = record.get("KNOWN_ATTEMPTS")
    no_attempts = known_attempts == 0 or str(known_attempts).strip() == "0"
    no_economic = economic in {"", "NONE", "NONE NEW", "NONE_NEW", UNKNOWN}
    explicit_unexecuted = any(
        marker in combined
        for marker in ("UNEXECUTED", "NOT_EXECUTED", "NOT MEASURED ECONOMICALLY", "ECONOMIC_TEST_COUNT=0")
    )
    if explicit_unexecuted or (no_attempts and no_economic and not blockers):
        reason_codes.append("ECONOMIC_TEST_UNEXECUTED")
        return "UNEXECUTED", "UNKNOWN", "UNKNOWN_ONLY", reason_codes

    negative_economic = (
        "NEGATIVE" in economic
        or "NEGATIVE_REPLICATION_CONFIRMED" in result
        or "FAMILY_REJECTED" in result
        or "ECONOMIC_THRESHOLD_NOT_MET" in result
        or "NEGATIVE_AFTER_COSTS" in economic
    )
    if negative_economic:
        reason_codes.append("ADMISSIBLE_HISTORICAL_NEGATIVE_SCOPE")
        return "NEGATIVE", "KNOWN_NEGATIVE", "NEGATIVE_SCOPE_ONLY", reason_codes

    positive_insufficient = any(
        marker in combined
        for marker in (
            "PROMISING_BUT_UNDERPROVED",
            "RETROSPECTIVE_POSITIVE",
            "RETROSPECTIVE_INDICATIVE",
            "POSITIVE_BUT_INSUFFICIENT",
            "INDICATIVE_AFTER_CAMPAIGN_MULTIPLICITY",
        )
    )
    if positive_insufficient:
        reason_codes.append("POSITIVE_SIGNAL_WITHOUT_PROOF")
        return "POSITIVE_BUT_INSUFFICIENT", "KNOWN_POSITIVE_INSUFFICIENT", "SIGNAL_NOT_PROOF", reason_codes

    # Qualification/promotion without new economic evidence is reusable memory,
    # not evidence of an edge.
    if any(marker in combined for marker in ("PROMOTE_EXPRESSION_NOT_EDGE_VALIDATED", "NOT_EDGE", "NOT NEW")):
        reason_codes.append("NO_NEW_ECONOMIC_EVIDENCE")
        return "SCIENTIFIC_MEMORY_ONLY", "MEMORY_ONLY", "MEMORY_ONLY", reason_codes

    if mechanism_evidence in {"STRONG", "MODERATE"} and no_economic:
        reason_codes.append("STRUCTURAL_MECHANISM_WITHOUT_ECONOMIC_PROOF")
        return "SCIENTIFIC_MEMORY_ONLY", "STRUCTURAL_ONLY", "STRUCTURAL_MECHANISM_ONLY", reason_codes

    unrecovered = any(
        marker in combined + " " + limitations
        for marker in ("UNRECOVERED", "PROVENANCE_GAP", "PRIMARY ARTIFACT NOT RECOVERED", "PROVENANCE MISSING")
    )
    if unrecovered or result in {"", UNKNOWN}:
        reason_codes.append("PRIMARY_EVIDENCE_OR_INTERPRETATION_REQUIRES_REVIEW")
        return "REVIEW_STILL_REQUIRED", "REVIEW_REQUIRED", "REVIEW_ONLY", reason_codes

    reason_codes.append("HISTORICAL_FACT_PRESERVED_WITHOUT_ECONOMIC_RECLASSIFICATION")
    return "SCIENTIFIC_MEMORY_ONLY", "MEMORY_ONLY", "MEMORY_ONLY", reason_codes


def semantic_identity(record: Mapping[str, Any]) -> Dict[str, Any]:
    return {key: _clean(record.get(key)) for key in IDENTITY_FIELDS}


def semantic_key(identity: Mapping[str, Any]) -> str:
    return sha256_json({key: identity.get(key, UNKNOWN) for key in IDENTITY_FIELDS})


def _identity_complete(identity: Mapping[str, Any]) -> bool:
    # Instrument/clock may legitimately be unknown in older history, but family,
    # mechanism, protocol, universe/horizon and evidence boundary must be known.
    required = (
        "research_family_id",
        "mechanism",
        "protocol_id",
        "universe",
        "horizon",
        "evidence_identity",
    )
    return all(_known(identity.get(field)) for field in required)


def _query_facets(record: Mapping[str, Any], identity: Mapping[str, Any]) -> Dict[str, Any]:
    failure_reasons = _list(record.get("OPEN_BLOCKERS")) + _list(record.get("KNOWN_LIMITATIONS"))
    protocol_weaknesses = _list(record.get("KNOWN_LIMITATIONS"))
    return {
        "mechanism": identity.get("mechanism", UNKNOWN),
        "payer": _clean(record.get("PAYER")),
        "constrained_actor": _clean(record.get("CONSTRAINED_ACTOR")),
        "timing_clock": identity.get("timing_clock", UNKNOWN),
        "universe": identity.get("universe", UNKNOWN),
        "instrument": identity.get("instrument", UNKNOWN),
        "evidence_identity": identity.get("evidence_identity", UNKNOWN),
        "failure_reason": [str(v) for v in failure_reasons if _known(v)],
        "protocol_weakness": [str(v) for v in protocol_weaknesses if _known(v)],
        "source_family": _clean(record.get("DATA_PROVENANCE")),
        "economic_exposure": _clean(record.get("ECONOMIC_EXPOSURE")),
    }


def normalize_legacy_record(
    record: Mapping[str, Any],
    source_manifest: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Normalize one immutable legacy record without inventing missing evidence."""
    disposition, epistemic, ceiling, reasons = _classify(record)
    provenance = _provenance(record, source_manifest)
    identity = {
        "research_family_id": _clean(record.get("RESEARCH_FAMILY_ID")),
        "mechanism": _clean(record.get("MECHANISM")),
        "protocol_id": _protocol_id(record),
        "universe": _clean(record.get("UNIVERSE")),
        "instrument": _clean(record.get("INSTRUMENT")),
        "timing_clock": _clean(record.get("TIMING_CLOCK")),
        "horizon": _clean(record.get("HORIZON")),
        "evidence_identity": _evidence_identity(record),
        "evidence_time_boundary": _clean(record.get("RESULT_OBSERVED_AT")),
    }
    key = semantic_key(identity)

    canonical = _identity_complete(identity) and _non_owner_provenance(provenance)
    if disposition == "REVIEW_STILL_REQUIRED":
        canonical = False
    status = "ACTIVE" if canonical else "REVIEW_STILL_REQUIRED"
    if not _identity_complete(identity):
        reasons = [*reasons, "INCOMPLETE_SEMANTIC_IDENTITY"]
    if not _non_owner_provenance(provenance):
        reasons = [*reasons, "INSUFFICIENT_NON_OWNER_PROVENANCE"]

    return {
        "schema_version": SCHEMA_VERSION,
        "memory_id": f"smem:{key[:24]}",
        "semantic_key": key,
        "canonical": canonical,
        "scientific_disposition": disposition,
        "epistemic_status": epistemic,
        "claim_ceiling": ceiling,
        "record_status": status,
        "identity": identity,
        "evidence": {
            "historical_result": _clean(record.get("RESULT")),
            "economic_evidence": _clean(record.get("ECONOMIC_EVIDENCE")),
            "statistical_evidence": _clean(record.get("STATISTICAL_EVIDENCE")),
            "falsification_scope": _clean(record.get("FALSIFICATION_SCOPE")),
            "research_decision": _clean(record.get("RESEARCH_DECISION")),
            "known_attempts": _clean(record.get("KNOWN_ATTEMPTS")),
            "effective_trials": _clean(record.get("EFFECTIVE_TRIALS")),
            "effective_trials_status": _clean(record.get("EFFECTIVE_TRIALS_STATUS")),
        },
        "provenance": provenance,
        "reason_codes": list(dict.fromkeys(reasons)),
        "protocol_weaknesses": [str(v) for v in _list(record.get("KNOWN_LIMITATIONS")) if _known(v)],
        "query_facets": _query_facets(record, identity),
        "supersession": None,
        "governance_refs": [],
        "source_identity": {
            "hypothesis_id": _clean(record.get("HYPOTHESIS_ID")),
            "legacy_id": _clean(record.get("LEGACY_ID_IF_ANY")),
            "generation_id": _clean(record.get("GENERATION_ID")),
        },
        "session_authority": dict(SESSION_AUTHORITY),
    }


def validate_memory_record(record: Mapping[str, Any], *, require_canonical: bool = True) -> None:
    required = {
        "schema_version", "memory_id", "semantic_key", "canonical",
        "scientific_disposition", "epistemic_status", "claim_ceiling", "record_status",
        "identity", "evidence", "provenance", "reason_codes", "query_facets", "session_authority",
    }
    missing = sorted(required - set(record))
    if missing:
        raise ValueError(f"scientific memory record missing fields: {', '.join(missing)}")
    if record.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported scientific memory schema version")
    if record.get("scientific_disposition") not in SCIENTIFIC_DISPOSITIONS:
        raise ValueError("invalid scientific disposition")
    if record.get("epistemic_status") not in EPISTEMIC_STATUSES:
        raise ValueError("invalid epistemic status")
    if record.get("claim_ceiling") not in CLAIM_CEILINGS:
        raise ValueError("invalid claim ceiling")
    if record.get("record_status") not in RECORD_STATUSES:
        raise ValueError("invalid record status")
    if require_canonical and record.get("canonical") is not True:
        raise ValueError("non-canonical/review memory cannot enter canonical scientific ledger")
    identity = record.get("identity") or {}
    if require_canonical and not _identity_complete(identity):
        raise ValueError("canonical scientific memory requires complete semantic identity")
    if require_canonical and not _non_owner_provenance(record.get("provenance") or []):
        raise ValueError("canonical scientific memory requires non-owner historical provenance")
    authority = record.get("session_authority") or {}
    for key, required_value in SESSION_AUTHORITY.items():
        if authority.get(key) is not required_value:
            raise ValueError(f"scientific memory authority invariant violated: {key}")
    if record.get("scientific_disposition") in {"BLOCKED", "UNEXECUTED"}:
        if record.get("epistemic_status") != "UNKNOWN" or record.get("claim_ceiling") != "UNKNOWN_ONLY":
            raise ValueError("blocked/unexecuted memory must remain UNKNOWN")
    if record.get("scientific_disposition") == "POSITIVE_BUT_INSUFFICIENT" and record.get("claim_ceiling") != "SIGNAL_NOT_PROOF":
        raise ValueError("positive-but-insufficient memory cannot exceed SIGNAL_NOT_PROOF")
    if record.get("scientific_disposition") == "INVALIDATED_PROTOCOL" and record.get("claim_ceiling") != "PROTOCOL_WEAKNESS_ONLY":
        raise ValueError("protocol invalidation cannot become economic failure")


def append_memory_record(ledger: AppendOnlyHashLedger, record: Mapping[str, Any]) -> Dict[str, Any]:
    validate_memory_record(record, require_canonical=True)
    return ledger.append(LEDGER_KIND, deepcopy(dict(record)))


def attach_owner_governance(
    record: Mapping[str, Any], *, decision_ref: str, action: str, reason: str
) -> Dict[str, Any]:
    """Govern interpretation without rewriting the scientific evidence."""
    if not decision_ref.strip():
        raise ValueError("owner governance requires a durable decision reference")
    updated = deepcopy(dict(record))
    original_disposition = updated.get("scientific_disposition")
    original_evidence = deepcopy(updated.get("evidence"))
    updated["record_status"] = "OWNER_GOVERNANCE_NORMALIZED"
    updated.setdefault("governance_refs", []).append({
        "decision_ref": decision_ref,
        "action": action,
        "reason": reason,
    })
    if updated.get("scientific_disposition") != original_disposition or updated.get("evidence") != original_evidence:
        raise AssertionError("governance must not overwrite scientific evidence")
    return updated


def supersede_with_proof(
    record: Mapping[str, Any], *, superseding_memory_id: str, proof_refs: Sequence[str], reason: str
) -> Dict[str, Any]:
    """Mark a memory superseded while preserving it and all original provenance."""
    clean_refs = [ref.strip() for ref in proof_refs if isinstance(ref, str) and ref.strip()]
    if not superseding_memory_id.strip() or not clean_refs:
        raise ValueError("supersession requires a superseding memory id and durable proof refs")
    updated = deepcopy(dict(record))
    original_provenance = deepcopy(updated.get("provenance"))
    updated["record_status"] = "SUPERSEDED_WITH_PROOF"
    updated["supersession"] = {
        "superseding_memory_id": superseding_memory_id,
        "proof_refs": clean_refs,
        "reason": reason,
    }
    if updated.get("provenance") != original_provenance:
        raise AssertionError("supersession must preserve original provenance")
    return updated


def _facet_values(value: Any) -> set[str]:
    if isinstance(value, (list, tuple, set)):
        return {str(v) for v in value if _known(v)}
    return {str(value)} if _known(value) else set()


class ScientificMemoryIndex:
    """Read/query view over scientific-memory entries already in the ledger."""

    def __init__(self, records: Iterable[Mapping[str, Any]]):
        current: Dict[str, Dict[str, Any]] = {}
        for raw in records:
            record = deepcopy(dict(raw))
            validate_memory_record(record, require_canonical=True)
            current[record["memory_id"]] = record
        self._records = current

    @classmethod
    def from_ledger(cls, ledger: AppendOnlyHashLedger) -> "ScientificMemoryIndex":
        records = [entry["payload"] for entry in ledger.entries if entry.get("kind") == LEDGER_KIND]
        return cls(records)

    @property
    def records(self) -> List[Dict[str, Any]]:
        return [deepcopy(self._records[key]) for key in sorted(self._records)]

    def query(
        self,
        *,
        scientific_disposition: Optional[str] = None,
        epistemic_status: Optional[str] = None,
        include_superseded: bool = False,
        **facets: Any,
    ) -> List[Dict[str, Any]]:
        unknown_facets = sorted(set(facets) - set(QUERY_FACETS))
        if unknown_facets:
            raise ValueError(f"unsupported scientific-memory facets: {', '.join(unknown_facets)}")
        results: List[Dict[str, Any]] = []
        for record in self._records.values():
            if not include_superseded and record.get("record_status") == "SUPERSEDED_WITH_PROOF":
                continue
            if scientific_disposition and record.get("scientific_disposition") != scientific_disposition:
                continue
            if epistemic_status and record.get("epistemic_status") != epistemic_status:
                continue
            record_facets = record.get("query_facets") or {}
            matched = True
            for key, expected in facets.items():
                expected_values = _facet_values(expected)
                observed_values = _facet_values(record_facets.get(key))
                if not expected_values or not expected_values.issubset(observed_values):
                    matched = False
                    break
            if matched:
                results.append(deepcopy(record))
        return sorted(results, key=lambda item: item["memory_id"])

    def structural_retrieval(self, candidate: Mapping[str, Any]) -> List[Dict[str, Any]]:
        """Return deterministic facet overlap without empirical similarity math."""
        candidate_facets = {key: candidate.get(key) for key in QUERY_FACETS if _known(candidate.get(key))}
        matches: List[Dict[str, Any]] = []
        for record in self._records.values():
            observed = record.get("query_facets") or {}
            matched_facets: List[str] = []
            for key, value in candidate_facets.items():
                if _facet_values(value) & _facet_values(observed.get(key)):
                    matched_facets.append(key)
            if matched_facets:
                matches.append({
                    "memory_id": record["memory_id"],
                    "scientific_disposition": record["scientific_disposition"],
                    "epistemic_status": record["epistemic_status"],
                    "claim_ceiling": record["claim_ceiling"],
                    "matched_facets": sorted(matched_facets),
                    "similarity_kind": "STRUCTURAL_FACET_OVERLAP_ONLY",
                    "empirical_similarity_computed": False,
                    "empirical_correlation": UNKNOWN,
                })
        return sorted(matches, key=lambda item: (item["memory_id"], item["matched_facets"]))
