"""Mission-selected V3 admission semantics over the existing Proposal Ledger.

This module does not create a second ledger, scheduler, Candidate system, Discovery,
Factory, Scientific Memory, or authority surface. It turns bounded pre-outcome
proposal material into passive admission records and explicit continuity sidecars.

Storage authority remains ``DurableProposalLedger`` from
``multi_source_ideation_hardening``. F-derived root/variant/exposure semantics are
pure identity helpers only; the operational F feeder remains disabled/unimported.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Mapping

from .expansion.v2_core import canonical_hash
from .idea_feed.primitives import bind_identity, exposure_id
from .multi_source_ideation import _reject_outcome_fields
from .multi_source_ideation_hardening import DurableProposalLedger
from .research_intelligence import UNKNOWN, semantic_identity as research_semantic_identity

AUTHORITY_STATE = {
    "economic_experiment_authorized": False,
    "prospective_observation_authorized": False,
    "real_capital_authorized": False,
    "live_trading_authorized": False,
    "outcome_accessed": False,
}

_FORBIDDEN_DOWNSTREAM_KEYS = {
    "candidate", "candidate_id", "candidate_spec", "canonical_candidate",
    "experiment", "experiment_id", "experiment_spec", "scientific_verdict",
    "economic_identity", "portfolio_readiness", "shadow_book", "capital_allocation",
    "expected_return", "expected_pnl", "task_id", "lease", "scheduler", "oracle",
    "control_plane", "ready_task",
}
_AUTHORITY_KEYS = {
    "economic_experiment_authorized", "prospective_observation_authorized",
    "real_capital_authorized", "live_trading_authorized", "outcome_accessed",
}
_CRITICAL_ROOT_FIELDS = ("mechanism", "actor", "universe", "clock", "horizon")
_UNKNOWN = {"", "UNKNOWN", "NONE", "N/A", "NA", "UNSPECIFIED", "TBD", "UNRESOLVED"}


class AdmissionError(ValueError):
    pass


def _known(value: Any) -> bool:
    if isinstance(value, bool) or value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().upper() not in _UNKNOWN
    return isinstance(value, (int, float))


def _norm(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _norm(value[k]) for k in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [_norm(v) for v in value]
    if not _known(value):
        return UNKNOWN
    if isinstance(value, str):
        return " ".join(value.strip().lower().split())
    return value


def _find_forbidden(value: Any, path: str = "$") -> str | None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            name = str(key).strip().lower()
            current = f"{path}.{key}"
            if name in _FORBIDDEN_DOWNSTREAM_KEYS:
                return current
            if name in _AUTHORITY_KEYS and child is not False:
                return current
            found = _find_forbidden(child, current)
            if found:
                return found
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            found = _find_forbidden(child, f"{path}[{index}]")
            if found:
                return found
    return None


def _timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise AdmissionError("SOURCE_CLOCK_REQUIRED")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AdmissionError("SOURCE_CLOCK_INVALID") from exc
    if parsed.tzinfo is None:
        raise AdmissionError("SOURCE_CLOCK_TIMEZONE_REQUIRED")
    return parsed


def _sha256(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AdmissionError("SOURCE_SNAPSHOT_HASH_REQUIRED")
    raw = value.strip().lower()
    if raw.startswith("sha256:"):
        raw = raw[7:]
    if len(raw) != 64 or any(c not in "0123456789abcdef" for c in raw):
        raise AdmissionError("SOURCE_SNAPSHOT_HASH_INVALID")
    return raw


def _source_binding(raw: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise AdmissionError("SOURCE_BINDING_MAPPING_REQUIRED")
    source_identity = raw.get("source_identity") or raw.get("source_ref") or raw.get("path")
    provenance_ref = raw.get("provenance_ref") or raw.get("path") or raw.get("source_ref")
    if not _known(source_identity) or not _known(provenance_ref):
        raise AdmissionError("SOURCE_PROVENANCE_REQUIRED")
    if raw.get("qualified") is not True:
        raise AdmissionError("SOURCE_NOT_QUALIFIED")
    snapshot = _sha256(raw.get("source_snapshot_identity") or raw.get("packet_hash") or raw.get("record_hash"))
    clocks = deepcopy(dict(raw.get("clocks") or {})) if isinstance(raw.get("clocks") or {}, Mapping) else None
    if clocks is None:
        raise AdmissionError("SOURCE_CLOCKS_INVALID")
    available = clocks.get("available_time") or clocks.get("available_at") or raw.get("available_at")
    public = clocks.get("public_time") or clocks.get("published_at") or raw.get("published_at")
    effective = clocks.get("effective_time") or clocks.get("effective_at") or raw.get("effective_at")
    observed = clocks.get("capture_time") or clocks.get("ingestion_time") or raw.get("captured_at")
    if available is not None:
        a = _timestamp(available)
        if public is not None and a < _timestamp(public):
            raise AdmissionError("SOURCE_AVAILABLE_BEFORE_PUBLIC")
        if effective is not None:
            _timestamp(effective)
        if observed is not None and _timestamp(observed) < a:
            raise AdmissionError("SOURCE_CAPTURE_BEFORE_AVAILABLE")
    return {
        "source_identity": str(source_identity),
        "source_snapshot_identity": snapshot,
        "provenance_ref": str(provenance_ref),
        "qualified": True,
        "clocks": clocks,
    }


def _semantic(raw: Mapping[str, Any]) -> dict[str, Any]:
    clock_value = raw.get("clock_identity")
    clock_name = clock_value.get("name") if isinstance(clock_value, Mapping) else clock_value
    probe = {
        "identity": {
            "mechanism": raw.get("mechanism_identity", raw.get("mechanism_claim")),
            "constrained_actor": raw.get("actor_identity"),
            "timing_clock": clock_name,
            "universe": raw.get("universe_identity"),
            "payer": raw.get("payer_identity"),
            "economic_exposure": raw.get("economic_exposure"),
            "instrument": raw.get("instrument_identity"),
            "source_family": raw.get("source_family"),
            "evidence_identity": raw.get("evidence_identity"),
        }
    }
    identity = research_semantic_identity(probe)
    return {
        "mechanism": identity["mechanism"],
        "actor": identity["constrained_actor"],
        "universe": identity["universe"],
        "clock": identity["timing_clock"],
        "horizon": _norm(raw.get("horizon_identity")),
        "payer": identity["payer"],
        "economic_exposure": identity["economic_exposure"],
        "instrument": identity["instrument"],
        "source_family": identity["source_family"],
        "evidence_identity": identity["evidence_identity"],
        "parameters": _norm(raw.get("parameters") or {}),
    }


def _prior_for_root(ledger: DurableProposalLedger, root_id: str) -> list[dict[str, Any]]:
    return [row for row in ledger.snapshot() if row.get("root_hypothesis_id") == root_id]


def admit_proposal(raw_proposal: Mapping[str, Any], *, ledger: DurableProposalLedger) -> dict[str, Any]:
    """Admit into the existing passive ledger, never materializing runtime work."""
    if not isinstance(raw_proposal, Mapping):
        raise AdmissionError("PROPOSAL_MAPPING_REQUIRED")
    if not isinstance(ledger, DurableProposalLedger):
        raise AdmissionError("CANONICAL_DURABLE_PROPOSAL_LEDGER_REQUIRED")
    raw = deepcopy(dict(raw_proposal))
    forbidden = _find_forbidden(raw)
    if forbidden:
        raise AdmissionError("DOWNSTREAM_OR_AUTHORITY_FIELD_FORBIDDEN:" + forbidden)
    try:
        _reject_outcome_fields(raw, "verified_continuity_admission")
    except ValueError as exc:
        raise AdmissionError(str(exc)) from exc

    sources_raw = raw.get("sources")
    if not isinstance(sources_raw, (list, tuple)) or not sources_raw:
        raise AdmissionError("QUALIFIED_SOURCE_REQUIRED")
    sources = [_source_binding(item) for item in sources_raw]
    identity = _semantic(raw)
    critical_missing = [field for field in _CRITICAL_ROOT_FIELDS if identity.get(field) == UNKNOWN]

    cohort_id = raw.get("cohort_id") if _known(raw.get("cohort_id")) else UNKNOWN
    policy_id = raw.get("policy_id") if _known(raw.get("policy_id")) else UNKNOWN

    if critical_missing:
        subject_id = "proposal-subject:UNKNOWN"
        root_id = UNKNOWN
        variant = UNKNOWN
        novelty = "UNKNOWN"
        rejection = ["UNKNOWN_CRITICAL_FIELD:" + field for field in critical_missing]
        prior_root: list[dict[str, Any]] = []
        cumulative_exposures: list[str] = []
    else:
        bound = bind_identity(identity, parameters=identity["parameters"])
        root_id = bound["root_hypothesis_id"]
        variant = bound["variant_id"]
        subject_id = "proposal-subject:" + canonical_hash({"root": root_id, "variant": variant})
        prior_root = _prior_for_root(ledger, root_id)
        same_variant = [row for row in prior_root if row.get("variant_id") == variant]
        novelty = "DUPLICATE_OR_KNOWN" if same_variant else ("PARAMETER_VARIANT" if prior_root else "ROOT_NEW_IN_LEDGER_SCOPE")
        rejection = ["PRIOR_SCIENTIFIC_EXPOSURE_SAME_VARIANT"] if same_variant else []
        current_exposures = [
            exposure_id(root_id, kind="SOURCE_SEEN", reference=item["source_snapshot_identity"])
            for item in sources
        ]
        prior_exposures = {
            eid
            for row in prior_root
            for eid in row.get("cumulative_exposure_ids", [])
            if isinstance(eid, str)
        }
        cumulative_exposures = sorted(prior_exposures.union(current_exposures))

    source_snapshots = sorted({item["source_snapshot_identity"] for item in sources})
    attempt_payload = {
        "subject_id": subject_id,
        "source_snapshots": source_snapshots,
        "cohort_id": cohort_id,
        "policy_id": policy_id,
        "falsifiable_claim": _norm(raw.get("falsifiable_claim") or {}),
    }
    proposal_id = "proposal:" + canonical_hash(attempt_payload)
    for prior in ledger.snapshot():
        if prior.get("proposal_id") == proposal_id:
            return deepcopy(prior)

    eligible = not critical_missing and not rejection
    record = {
        "schema_version": "verified-v3-admission-v1",
        "proposal_id": proposal_id,
        "proposal_subject_id": subject_id,
        "status": "ELIGIBLE_FOR_DISCOVERY" if eligible else ("DUPLICATE_OR_KNOWN" if rejection else "NOT_ELIGIBLE"),
        "admission_disposition": "ELIGIBLE_FOR_DISCOVERY" if eligible else "REJECTED",
        "rejection_reasons": rejection,
        "novelty_disposition": novelty,
        "root_hypothesis_id": root_id,
        "variant_id": variant,
        "cohort_id": cohort_id,
        "policy_id": policy_id,
        "semantic_identity": identity,
        "source_bindings": sources,
        "source_snapshot_identities": source_snapshots,
        "provenance_refs": sorted({item["provenance_ref"] for item in sources}),
        "cumulative_exposure_ids": cumulative_exposures,
        "prior_same_root_count": len(prior_root),
        "prior_same_variant_count": sum(row.get("variant_id") == variant for row in prior_root),
        "authority": deepcopy(AUTHORITY_STATE),
        "outcome_accessed": False,
        "scientific_verdict": "NOT_PERFORMED",
        "economic_result": "NOT_OBSERVED",
        "candidate_created": False,
        "discovery_boundary": "ELIGIBLE_FOR_DISCOVERY" if eligible else "TERMINAL_ADMISSION_REJECTION",
    }
    ledger.persist(record)
    return deepcopy(record)


def discovery_handoff(record: Mapping[str, Any]) -> dict[str, Any]:
    if record.get("admission_disposition") != "ELIGIBLE_FOR_DISCOVERY":
        raise AdmissionError("ONLY_ELIGIBLE_PROPOSAL_MAY_HANDOFF")
    return {
        "schema_version": "verified-v3-discovery-handoff-v1",
        "proposal_id": record["proposal_id"],
        "proposal_subject_id": record["proposal_subject_id"],
        "root_hypothesis_id": record["root_hypothesis_id"],
        "variant_id": record["variant_id"],
        "cohort_id": record["cohort_id"],
        "semantic_identity": deepcopy(record["semantic_identity"]),
        "source_bindings": deepcopy(record["source_bindings"]),
        "cumulative_exposure_ids": deepcopy(record["cumulative_exposure_ids"]),
        "candidate_created": False,
        "scheduler_mutation": False,
        "authority": deepcopy(AUTHORITY_STATE),
        "outcome_accessed": False,
    }


def research_intelligence_input(record: Mapping[str, Any], *, required_capability: str | None = None,
                                target_lane: str | None = None) -> dict[str, Any]:
    """Project admission identity into RI without constructing a Candidate."""
    handoff = discovery_handoff(record)
    identity = handoff["semantic_identity"]
    return {
        "candidate_id": handoff["proposal_subject_id"],
        "identity": {
            "mechanism": identity["mechanism"],
            "constrained_actor": identity["actor"],
            "timing_clock": identity["clock"],
            "universe": identity["universe"],
            "payer": identity["payer"],
            "economic_exposure": identity["economic_exposure"],
            "instrument": identity["instrument"],
            "source_family": identity["source_family"],
            "evidence_identity": identity["evidence_identity"],
        },
        "required_capability": required_capability,
        "target_lane": target_lane,
        "continuity_ref": {
            "proposal_id": handoff["proposal_id"],
            "root_hypothesis_id": handoff["root_hypothesis_id"],
            "variant_id": handoff["variant_id"],
            "cohort_id": handoff["cohort_id"],
            "cumulative_exposure_ids": handoff["cumulative_exposure_ids"],
        },
    }


def bind_ri_decision(record: Mapping[str, Any], decision: Mapping[str, Any]) -> dict[str, Any]:
    expected = record.get("proposal_subject_id")
    actual = decision.get("candidate_id")
    if actual not in (None, expected):
        raise AdmissionError("RI_DECISION_SUBJECT_MISMATCH")
    body = {
        "proposal_id": record["proposal_id"],
        "proposal_subject_id": expected,
        "root_hypothesis_id": record["root_hypothesis_id"],
        "variant_id": record["variant_id"],
        "cohort_id": record["cohort_id"],
        "cumulative_exposure_ids": deepcopy(record["cumulative_exposure_ids"]),
        "ri_decision": deepcopy(dict(decision)),
    }
    return {**body, "binding_hash": canonical_hash(body)}


def bind_candidate_continuity(ri_binding: Mapping[str, Any], candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Downstream-only sidecar: Candidate identity is never injected into V3 input."""
    if not isinstance(candidate, Mapping) or not _known(candidate.get("hypothesis_id")) or not _known(candidate.get("generation_id")):
        raise AdmissionError("DOWNSTREAM_CANDIDATE_IDENTITY_REQUIRED")
    return {
        "proposal_id": ri_binding["proposal_id"],
        "proposal_subject_id": ri_binding["proposal_subject_id"],
        "root_hypothesis_id": ri_binding["root_hypothesis_id"],
        "variant_id": ri_binding["variant_id"],
        "cohort_id": ri_binding["cohort_id"],
        "cumulative_exposure_ids": deepcopy(ri_binding["cumulative_exposure_ids"]),
        "candidate_hypothesis_id": candidate["hypothesis_id"],
        "candidate_generation_id": candidate["generation_id"],
        "candidate_hash": canonical_hash(dict(candidate)),
        "ri_action": (ri_binding.get("ri_decision") or {}).get("action", UNKNOWN),
        "authority": deepcopy(AUTHORITY_STATE),
        "outcome_accessed": False,
    }
