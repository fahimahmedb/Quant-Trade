"""Bounded pre-discovery idea admission membrane.

This module is intentionally *not* a producer, Candidate factory, scheduler, or
scientific verdict engine.  It consumes qualified pre-outcome source bindings,
turns untrusted raw proposals into durable admission decisions, and stops at
``ELIGIBLE_FOR_DISCOVERY``.

The implementation reuses existing Research OS laws:
* the canonical pre-outcome outcome firewall;
* Research Intelligence semantic normalization and Scientific Memory relation;
* PIT/content-address validation from the Data Plane;
* durable JSONL primitives from ``quant.state``;
* the Scientific Store canonical hash function.

It never mutates the Control Plane, queue replenisher, Scientific Memory, or
downstream Candidate/experiment state.
"""
from __future__ import annotations

import fcntl
import os
import re
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from itertools import islice
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from quant.dataplane.identity import parse_pit_instant, validate_evidence_hash
from quant.state import append_jsonl, read_jsonl, utc_now

from .expansion.experiment_outcome_firewall import OutcomeFirewallError, assert_pre_outcome_payload
from .research_intelligence import (
    UNKNOWN,
    memory_relation,
    semantic_identity as research_semantic_identity,
)
from .scientific_store import sha256_json


SCHEMA_VERSION = "idea-proposal-v3"
LEDGER_SCHEMA_VERSION = "proposal-ledger-v1"
LEDGER_KIND = "IDEA_PROPOSAL_DECISION"
HANDOFF_SCHEMA_VERSION = "eligible-discovery-handoff-v1"

POLICY_FAMILIES = {
    "SYSTEMATIC_COVERAGE",
    "INFORMATION_VALUE",
    "DIVERGENT_EXPLORATION",
}

NOVELTY_DISPOSITIONS = {
    "LEXICALLY_DIFFERENT",
    "SEMANTICALLY_EQUIVALENT",
    "PARAMETER_VARIANT",
    "MECHANISM_VARIANT",
    "UNIVERSE_VARIANT",
    "HORIZON_VARIANT",
    "GENUINELY_NOVEL",
    "UNKNOWN",
}

ADMISSION_DISPOSITIONS = {"ELIGIBLE_FOR_DISCOVERY", "REJECTED"}

REJECTION_REASONS = {
    "DUPLICATE",
    "NEAR_DUPLICATE",
    "NO_MECHANISM",
    "UNIDENTIFIED_ACTOR",
    "UNIDENTIFIED_UNIVERSE",
    "UNIDENTIFIED_CLOCK",
    "UNIDENTIFIED_HORIZON",
    "NON_FALSIFIABLE",
    "OUTCOME_CONTAMINATED",
    "SOURCE_UNQUALIFIED",
    "UNTRACEABLE_PROVENANCE",
    "ALREADY_EXPLORED",
    "MALFORMED",
    "CONTRADICTORY_IDENTITY",
    "OUTSIDE_AUTHORITY",
    "INSUFFICIENT_INFORMATION",
    "UNKNOWN_CRITICAL_FIELD",
}

AUTHORITY_STATE = {
    "economic_experiment_authorized": False,
    "prospective_observation_authorized": False,
    "real_capital_authorized": False,
    "live_trading_authorized": False,
    "outcome_accessed": False,
}

CLOCK_FIELDS = (
    "event_time",
    "publication_time",
    "public_time",
    "available_time",
    "effective_time",
    "revision_time",
    "ingestion_time",
)

CRITICAL_IDENTITY_FIELDS = ("mechanism", "actor", "universe", "clock", "horizon")

_FORBIDDEN_DOWNSTREAM_KEYS = {
    "candidate",
    "candidate_id",
    "candidate_spec",
    "canonical_candidate",
    "experiment",
    "experiment_spec",
    "scientific_verdict",
    "economic_identity",
    "portfolio_readiness",
    "shadow_book",
    "capital_allocation",
    "expected_return",
    "expected_pnl",
}
_RESERVED_SELF_CERTIFICATION_KEYS = {
    "proposal_id",
    "proposal_fingerprint",
    "semantic_identity",
    "novelty_disposition",
    "admission_disposition",
    "prior_proposal_matches",
    "rejection_reasons",
}
_AUTHORITY_FIELDS = {
    "economic_experiment_authorized",
    "prospective_observation_authorized",
    "real_capital_authorized",
    "live_trading_authorized",
}
_UNKNOWN_TOKENS = {"", "UNKNOWN", "NONE", "N/A", "NA", "UNSPECIFIED", "TBD", "UNRESOLVED"}


class ProposalLedgerCorruption(RuntimeError):
    """A committed Proposal Ledger record cannot be trusted."""


class IdeaAdmissionError(RuntimeError):
    """The intake contract itself cannot be evaluated safely."""


def _known(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool)) and str(value).strip().upper() not in _UNKNOWN_TOKENS


def _norm(value: Any) -> str:
    if not _known(value):
        return UNKNOWN
    text = str(value).strip().lower()
    text = re.sub(r"[\s_\-]+", " ", text)
    text = re.sub(r"[^\w\s:/+.]", "", text)
    return re.sub(r"\s+", " ", text).strip() or UNKNOWN


def _canonical_parameters(value: Any) -> Any:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return {str(key): _canonical_parameters(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [_canonical_parameters(item) for item in value]
    if isinstance(value, str):
        return _norm(value)
    if isinstance(value, (int, float, bool)):
        return value
    return str(value)


def _sha256_address(value: Any) -> str:
    """Normalize an existing 64-hex SHA-256 identity without inventing content."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("missing source snapshot identity")
    candidate = value.strip().lower()
    if not candidate.startswith("sha256:"):
        candidate = "sha256:" + candidate
    validate_evidence_hash(candidate)
    return candidate


def _timestamp(value: str) -> datetime:
    return parse_pit_instant(value)


def _clock_contradictions(clocks: Mapping[str, Any]) -> list[str]:
    parsed: dict[str, datetime] = {}
    for field_name in CLOCK_FIELDS:
        value = clocks.get(field_name)
        if value in (None, "", UNKNOWN):
            continue
        if not isinstance(value, str):
            return [f"{field_name}:NON_STRING"]
        try:
            parsed[field_name] = _timestamp(value)
        except (TypeError, ValueError):
            return [f"{field_name}:INVALID_TIMESTAMP"]

    contradictions: list[str] = []
    if "publication_time" in parsed and "public_time" in parsed:
        if parsed["public_time"] < parsed["publication_time"]:
            contradictions.append("PUBLIC_BEFORE_PUBLICATION")
    if "public_time" in parsed and "available_time" in parsed:
        if parsed["available_time"] < parsed["public_time"]:
            contradictions.append("AVAILABLE_BEFORE_PUBLIC")
    if "available_time" in parsed and "ingestion_time" in parsed:
        if parsed["ingestion_time"] < parsed["available_time"]:
            contradictions.append("INGESTED_BEFORE_AVAILABLE")
    return contradictions


@dataclass(frozen=True)
class SourceBinding:
    """Immutable qualified source state used by one raw proposal."""

    source_identity: str
    source_snapshot_identity: str
    provenance_ref: str
    qualified: bool
    clocks: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> list[str]:
        reasons: list[str] = []
        if not _known(self.source_identity):
            reasons.append("SOURCE_UNQUALIFIED")
        try:
            _sha256_address(self.source_snapshot_identity)
        except (TypeError, ValueError):
            reasons.append("MALFORMED")
        if not _known(self.provenance_ref):
            reasons.append("UNTRACEABLE_PROVENANCE")
        if self.qualified is not True:
            reasons.append("SOURCE_UNQUALIFIED")
        if not isinstance(self.clocks, Mapping):
            reasons.append("MALFORMED")
        else:
            contradictions = _clock_contradictions(self.clocks)
            if contradictions:
                reasons.append("CONTRADICTORY_IDENTITY")
        return sorted(set(reasons))

    def normalized(self) -> dict[str, Any]:
        return {
            "source_identity": self.source_identity,
            "source_snapshot_identity": _sha256_address(self.source_snapshot_identity),
            "provenance_ref": self.provenance_ref,
            "qualified": self.qualified is True,
            "clocks": {key: self.clocks.get(key) for key in CLOCK_FIELDS if self.clocks.get(key) is not None},
        }


def source_binding_from_planner(source: Mapping[str, Any], *, qualified: bool) -> SourceBinding:
    """Adapt the existing frontier source planner output without re-qualifying it.

    The planner's ``packet_hash`` is already a content hash. Paths remain
    provenance, never semantic novelty.
    """
    if not isinstance(source, Mapping):
        raise ValueError("planner source must be a mapping")
    snapshot = source.get("packet_hash") or source.get("record_hash")
    source_identity = source.get("source_ref") or source.get("path")
    provenance = source.get("path") or source.get("source_ref")
    clocks = {}
    if source.get("available_at") is not None:
        clocks["available_time"] = source.get("available_at")
    return SourceBinding(
        source_identity=str(source_identity or UNKNOWN),
        source_snapshot_identity=_sha256_address(snapshot),
        provenance_ref=str(provenance or UNKNOWN),
        qualified=qualified,
        clocks=clocks,
    )


@dataclass(frozen=True)
class IdeationPolicy:
    """One bounded proposal policy. Its generator has no admission authority."""

    policy_id: str
    family: str
    generator: Callable[[Mapping[str, Any]], Iterable[Mapping[str, Any]]]

    def __post_init__(self) -> None:
        if not _known(self.policy_id):
            raise ValueError("policy_id is required")
        if self.family not in POLICY_FAMILIES:
            raise ValueError(f"unsupported policy family: {self.family}")
        if not callable(self.generator):
            raise TypeError("policy generator must be callable")

    def propose(self, context: Mapping[str, Any], limit: int) -> list[dict[str, Any]]:
        if limit <= 0:
            return []
        generated = self.generator(context)
        if generated is None:
            return []
        proposals: list[dict[str, Any]] = []
        for raw in islice(iter(generated), limit):
            if not isinstance(raw, Mapping):
                proposals.append({
                    "policy_id": self.policy_id,
                    "policy_family": self.family,
                    "_malformed_raw": repr(raw),
                })
                continue
            item = deepcopy(dict(raw))
            # Policy identity is owned by the intake wrapper, not trusted from a backend.
            item["policy_id"] = self.policy_id
            item["policy_family"] = self.family
            proposals.append(item)
        return proposals


@dataclass(frozen=True)
class AdmissionResult:
    proposal: dict[str, Any]
    admission_evidence: dict[str, Any]
    replayed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal": deepcopy(self.proposal),
            "admission_evidence": deepcopy(self.admission_evidence),
            "replayed": self.replayed,
        }


def _sanitize_untrusted_claims(raw: Mapping[str, Any]) -> dict[str, Any]:
    value = deepcopy(dict(raw))
    unsupported = value.pop("unsupported_claims", [])
    existing = value.get("assumptions")
    malformed_assumptions = existing is not None and not isinstance(existing, (list, tuple))
    assumptions = list(existing or []) if not malformed_assumptions else [existing]
    if unsupported is not None:
        values = unsupported if isinstance(unsupported, (list, tuple, set)) else [unsupported]
        for claim in values:
            assumptions.append(f"UNSUPPORTED_GENERATOR_CLAIM:{claim}")
    value["assumptions"] = assumptions
    if malformed_assumptions:
        value["_malformed_assumptions"] = True
    return value


def _find_forbidden_downstream_key(value: Any, path: str = "$") -> str | None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            name = str(key).lower()
            current = f"{path}.{key}"
            if name in _FORBIDDEN_DOWNSTREAM_KEYS:
                return current
            found = _find_forbidden_downstream_key(child, current)
            if found:
                return found
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            found = _find_forbidden_downstream_key(child, f"{path}[{index}]")
            if found:
                return found
    return None


def _authority_escalation(value: Any, path: str = "$") -> str | None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            name = str(key).lower()
            current = f"{path}.{key}"
            if name in _AUTHORITY_FIELDS and child is not False:
                return current
            found = _authority_escalation(child, current)
            if found:
                return found
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            found = _authority_escalation(child, f"{path}[{index}]")
            if found:
                return found
    return None


def _self_certification_key(raw: Mapping[str, Any]) -> str | None:
    for key in raw:
        if str(key).lower() in _RESERVED_SELF_CERTIFICATION_KEYS:
            return str(key)
    return None


def _parse_source_bindings(raw: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    values = raw.get("sources")
    if not isinstance(values, (list, tuple)) or not values:
        return [], ["SOURCE_UNQUALIFIED"]
    normalized: list[dict[str, Any]] = []
    reasons: list[str] = []
    for value in values:
        if not isinstance(value, Mapping):
            reasons.append("MALFORMED")
            continue
        try:
            binding = SourceBinding(
                source_identity=value.get("source_identity", UNKNOWN),
                source_snapshot_identity=value.get("source_snapshot_identity", UNKNOWN),
                provenance_ref=value.get("provenance_ref", UNKNOWN),
                qualified=value.get("qualified") is True,
                clocks=dict(value.get("clocks") or {}) if isinstance(value.get("clocks") or {}, Mapping) else value.get("clocks"),
            )
        except Exception:
            reasons.append("MALFORMED")
            continue
        binding_reasons = binding.validate()
        reasons.extend(binding_reasons)
        if not binding_reasons:
            normalized.append(binding.normalized())
    if not normalized and "SOURCE_UNQUALIFIED" not in reasons:
        reasons.append("SOURCE_UNQUALIFIED")
    return normalized, sorted(set(reasons))


def _source_bundle_identity(bindings: Sequence[Mapping[str, Any]]) -> str:
    snapshots = sorted(str(item["source_snapshot_identity"]) for item in bindings)
    if not snapshots:
        return UNKNOWN
    if len(snapshots) == 1:
        return snapshots[0]
    return "sha256:" + sha256_json({"source_snapshots": snapshots})


def _proposal_identity(raw: Mapping[str, Any]) -> dict[str, Any]:
    mechanism_claim = raw.get("mechanism_claim")
    mechanism_identity = raw.get("mechanism_identity", mechanism_claim)
    clock_value = raw.get("clock_identity")
    if isinstance(clock_value, Mapping):
        clock_name = clock_value.get("name")
    else:
        clock_name = clock_value

    adapter = {
        "identity": {
            "mechanism": mechanism_identity,
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
    normalized = research_semantic_identity(adapter)
    return {
        "mechanism": normalized["mechanism"],
        "actor": normalized["constrained_actor"],
        "universe": normalized["universe"],
        "clock": normalized["timing_clock"],
        "horizon": _norm(raw.get("horizon_identity")),
        "payer": normalized["payer"],
        "economic_exposure": normalized["economic_exposure"],
        "instrument": normalized["instrument"],
        "parameters": _canonical_parameters(raw.get("parameters")),
    }


def _semantic_key(identity: Mapping[str, Any]) -> str:
    return sha256_json({
        "mechanism": identity.get("mechanism", UNKNOWN),
        "actor": identity.get("actor", UNKNOWN),
        "universe": identity.get("universe", UNKNOWN),
        "clock": identity.get("clock", UNKNOWN),
        "horizon": identity.get("horizon", UNKNOWN),
        "parameters": identity.get("parameters", {}),
    })


def _critical_identity_reasons(identity: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    if identity.get("mechanism") == UNKNOWN:
        reasons.extend(["NO_MECHANISM", "UNKNOWN_CRITICAL_FIELD"])
    if identity.get("actor") == UNKNOWN:
        reasons.extend(["UNIDENTIFIED_ACTOR", "UNKNOWN_CRITICAL_FIELD"])
    if identity.get("universe") == UNKNOWN:
        reasons.extend(["UNIDENTIFIED_UNIVERSE", "UNKNOWN_CRITICAL_FIELD"])
    if identity.get("clock") == UNKNOWN:
        reasons.extend(["UNIDENTIFIED_CLOCK", "UNKNOWN_CRITICAL_FIELD"])
    if identity.get("horizon") == UNKNOWN:
        reasons.extend(["UNIDENTIFIED_HORIZON", "UNKNOWN_CRITICAL_FIELD"])
    return sorted(set(reasons))


def _clock_identity_reasons(raw: Mapping[str, Any]) -> list[str]:
    value = raw.get("clock_identity")
    if value in (None, "", UNKNOWN):
        return ["UNIDENTIFIED_CLOCK", "UNKNOWN_CRITICAL_FIELD"]
    if isinstance(value, Mapping):
        if _norm(value.get("name")) == UNKNOWN:
            return ["UNIDENTIFIED_CLOCK", "UNKNOWN_CRITICAL_FIELD"]
        contradictions = _clock_contradictions(value)
        if contradictions:
            return ["CONTRADICTORY_IDENTITY"]
        return []
    if not _known(value):
        return ["UNIDENTIFIED_CLOCK", "UNKNOWN_CRITICAL_FIELD"]
    return []


def _falsifiability_reasons(raw: Mapping[str, Any]) -> list[str]:
    value = raw.get("falsifiable_claim")
    if not isinstance(value, Mapping):
        return ["NON_FALSIFIABLE"]
    statement = value.get("statement")
    falsifier = value.get("falsifier")
    if not _known(statement) or not _known(falsifier):
        return ["NON_FALSIFIABLE"]
    return []


def _proposal_fingerprint(raw: Mapping[str, Any], identity: Mapping[str, Any]) -> str:
    claim = raw.get("falsifiable_claim") if isinstance(raw.get("falsifiable_claim"), Mapping) else {}
    lexical = {
        "mechanism_claim": _norm(raw.get("mechanism_claim")),
        "mechanism_identity": identity.get("mechanism"),
        "actor_identity": identity.get("actor"),
        "universe_identity": identity.get("universe"),
        "clock_identity": identity.get("clock"),
        "horizon_identity": identity.get("horizon"),
        "falsifiable_statement": _norm(claim.get("statement")),
        "falsifier": _norm(claim.get("falsifier")),
        "assumptions": [_norm(item) for item in (raw.get("assumptions") or [])],
        "parameters": identity.get("parameters", {}),
    }
    return "sha256:" + sha256_json(lexical)


def _proposal_relation(
    identity: Mapping[str, Any],
    fingerprint: str,
    prior: Mapping[str, Any],
) -> str | None:
    other_identity = prior.get("semantic_identity") or {}
    if any(identity.get(field) == UNKNOWN for field in CRITICAL_IDENTITY_FIELDS):
        return "UNKNOWN"
    if any(other_identity.get(field) == UNKNOWN for field in CRITICAL_IDENTITY_FIELDS):
        return None

    same_core = all(identity.get(field) == other_identity.get(field) for field in CRITICAL_IDENTITY_FIELDS)
    if same_core and identity.get("parameters", {}) == other_identity.get("parameters", {}):
        if fingerprint == prior.get("proposal_fingerprint"):
            return "SEMANTICALLY_EQUIVALENT"
        return "LEXICALLY_DIFFERENT"

    if same_core and identity.get("parameters", {}) != other_identity.get("parameters", {}):
        return "PARAMETER_VARIANT"

    if all(identity.get(field) == other_identity.get(field) for field in ("actor", "universe", "clock", "horizon")):
        if identity.get("mechanism") != other_identity.get("mechanism"):
            return "MECHANISM_VARIANT"

    if all(identity.get(field) == other_identity.get(field) for field in ("mechanism", "actor", "clock", "horizon")):
        if identity.get("universe") != other_identity.get("universe"):
            return "UNIVERSE_VARIANT"

    if all(identity.get(field) == other_identity.get(field) for field in ("mechanism", "actor", "universe", "clock")):
        if identity.get("horizon") != other_identity.get("horizon"):
            return "HORIZON_VARIANT"
    return None


_RELATION_PRIORITY = {
    "UNKNOWN": 0,
    "SEMANTICALLY_EQUIVALENT": 1,
    "LEXICALLY_DIFFERENT": 2,
    "PARAMETER_VARIANT": 3,
    "MECHANISM_VARIANT": 4,
    "UNIVERSE_VARIANT": 5,
    "HORIZON_VARIANT": 6,
}


def _memory_probe(raw: Mapping[str, Any], identity: Mapping[str, Any], snapshot: str) -> dict[str, Any]:
    # ``memory_relation`` accepts any mapping with an ``identity`` member; no
    # downstream Candidate object or identifier is constructed here.
    return {
        "identity": {
            "mechanism": identity.get("mechanism"),
            "payer": identity.get("payer"),
            "constrained_actor": identity.get("actor"),
            "timing_clock": identity.get("clock"),
            "universe": identity.get("universe"),
            "economic_exposure": identity.get("economic_exposure"),
            "instrument": identity.get("instrument"),
            "source_family": raw.get("source_family"),
            "evidence_identity": snapshot,
        },
    }


def _classify_novelty(
    *,
    raw: Mapping[str, Any],
    identity: Mapping[str, Any],
    fingerprint: str,
    snapshot: str,
    prior_proposals: Sequence[Mapping[str, Any]],
    scientific_memory: Sequence[Mapping[str, Any]],
) -> tuple[str, list[dict[str, Any]], bool]:
    if any(identity.get(field) == UNKNOWN for field in CRITICAL_IDENTITY_FIELDS):
        return "UNKNOWN", [], False

    matches: list[dict[str, Any]] = []
    relations: list[str] = []
    prior_rejected = False
    for prior in prior_proposals:
        relation = _proposal_relation(identity, fingerprint, prior)
        if relation is None:
            continue
        relations.append(relation)
        prior_rejected = prior_rejected or (
            relation in {"SEMANTICALLY_EQUIVALENT", "LEXICALLY_DIFFERENT", "PARAMETER_VARIANT"}
            and prior.get("admission_disposition") == "REJECTED"
        )
        matches.append({
            "kind": "PROPOSAL_LEDGER",
            "proposal_id": prior.get("proposal_id"),
            "relation": relation,
            "prior_admission_disposition": prior.get("admission_disposition"),
        })

    memory_probe = _memory_probe(raw, identity, snapshot)
    for record in scientific_memory:
        if not isinstance(record, Mapping):
            continue
        try:
            relation = memory_relation(memory_probe, record)
        except (TypeError, ValueError):
            continue
        if relation.get("qualified") is not True:
            continue
        if relation.get("same_semantic_family") is True:
            relations.append("SEMANTICALLY_EQUIVALENT")
            matches.append({
                "kind": "SCIENTIFIC_MEMORY",
                "memory_id": relation.get("memory_id"),
                "relation": "SEMANTICALLY_EQUIVALENT",
                "scientific_disposition": relation.get("scientific_disposition"),
                "claim_ceiling": relation.get("claim_ceiling"),
            })
            continue
        # Qualified memory that matches all known core dimensions but still has
        # unresolved dimensions is a real ambiguity.  It must not be converted
        # into a favorable novelty claim merely because the old record is sparse.
        if not relation.get("mismatched_core_dimensions") and relation.get("unknown_core_dimensions"):
            relations.append("UNKNOWN")
            matches.append({
                "kind": "SCIENTIFIC_MEMORY",
                "memory_id": relation.get("memory_id"),
                "relation": "UNKNOWN",
                "unknown_core_dimensions": list(relation.get("unknown_core_dimensions") or []),
            })

    if not relations:
        return "GENUINELY_NOVEL", matches, prior_rejected
    chosen = sorted(relations, key=lambda item: _RELATION_PRIORITY[item])[0]
    return chosen, matches, prior_rejected


def _novelty_rejections(novelty: str, prior_rejected: bool, memory_match: bool) -> list[str]:
    reasons: list[str] = []
    if novelty == "SEMANTICALLY_EQUIVALENT":
        reasons.append("DUPLICATE")
    elif novelty in {"LEXICALLY_DIFFERENT", "PARAMETER_VARIANT"}:
        reasons.append("NEAR_DUPLICATE")
    elif novelty == "UNKNOWN":
        reasons.extend(["UNKNOWN_CRITICAL_FIELD", "INSUFFICIENT_INFORMATION"])
    if prior_rejected or memory_match:
        reasons.append("ALREADY_EXPLORED")
    return sorted(set(reasons))


def _validate_parent_ids(value: Any) -> tuple[list[str], list[str]]:
    if value is None:
        return [], []
    if not isinstance(value, (list, tuple)):
        return [], ["MALFORMED"]
    parents: list[str] = []
    reasons: list[str] = []
    for parent in value:
        if not isinstance(parent, str) or not parent.startswith("idea:") or len(parent) <= len("idea:"):
            reasons.append("MALFORMED")
        else:
            parents.append(parent)
    return sorted(set(parents)), sorted(set(reasons))


def _minimal_raw_reasons(raw: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    if not _known(raw.get("policy_id")):
        reasons.append("MALFORMED")
    if raw.get("policy_family") not in POLICY_FAMILIES:
        reasons.append("MALFORMED")
    if not _known(raw.get("mechanism_claim")):
        reasons.append("NO_MECHANISM")
    if raw.get("assumptions") is not None and not isinstance(raw.get("assumptions"), (list, tuple)):
        reasons.append("MALFORMED")
    if raw.get("parameters") is not None and not isinstance(raw.get("parameters"), Mapping):
        reasons.append("MALFORMED")
    if "_malformed_raw" in raw or raw.get("_malformed_assumptions") is True:
        reasons.append("MALFORMED")
    return reasons


class ProposalLedger:
    """Durable, hash-chained, idempotent pre-discovery proposal history."""

    def __init__(
        self,
        path: Path,
        *,
        scientific_memory: Sequence[Mapping[str, Any]] = (),
        fault_hook: Callable[[str, Mapping[str, Any]], None] | None = None,
    ) -> None:
        self.path = Path(path)
        self.scientific_memory = tuple(deepcopy(list(scientific_memory)))
        self._fault_hook = fault_hook

    @property
    def _transaction_lock_path(self) -> Path:
        return self.path.with_name(self.path.name + ".admission.lock")

    @contextmanager
    def _transaction(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self._transaction_lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            os.close(fd)

    def _fault(self, stage: str, **context: Any) -> None:
        if self._fault_hook is not None:
            self._fault_hook(stage, context)

    def _validate_entry(self, entry: Mapping[str, Any], *, expected_seq: int, previous_hash: str | None) -> None:
        if set(entry) != {
            "schema_version", "seq", "kind", "previous_hash",
            "payload_hash", "payload", "entry_hash",
        }:
            raise ProposalLedgerCorruption("PROPOSAL_LEDGER_FIELDS_INVALID")
        if entry.get("schema_version") != LEDGER_SCHEMA_VERSION:
            raise ProposalLedgerCorruption("PROPOSAL_LEDGER_SCHEMA_INVALID")
        if entry.get("seq") != expected_seq or entry.get("kind") != LEDGER_KIND:
            raise ProposalLedgerCorruption("PROPOSAL_LEDGER_SEQUENCE_OR_KIND_INVALID")
        if entry.get("previous_hash") != previous_hash:
            raise ProposalLedgerCorruption("PROPOSAL_LEDGER_CHAIN_INVALID")
        payload = entry.get("payload")
        if not isinstance(payload, Mapping):
            raise ProposalLedgerCorruption("PROPOSAL_LEDGER_PAYLOAD_INVALID")
        if entry.get("payload_hash") != sha256_json(payload):
            raise ProposalLedgerCorruption("PROPOSAL_LEDGER_PAYLOAD_HASH_INVALID")
        expected_hash = sha256_json({
            "seq": expected_seq,
            "kind": LEDGER_KIND,
            "previous_hash": previous_hash,
            "payload_hash": entry.get("payload_hash"),
        })
        if entry.get("entry_hash") != expected_hash:
            raise ProposalLedgerCorruption("PROPOSAL_LEDGER_ENTRY_HASH_INVALID")
        self._validate_payload(payload)

    def _validate_payload(self, payload: Mapping[str, Any]) -> None:
        if not _known(payload.get("attempt_id")):
            raise ProposalLedgerCorruption("PROPOSAL_ATTEMPT_ID_INVALID")
        proposal = payload.get("proposal")
        evidence = payload.get("admission_evidence")
        if not isinstance(proposal, Mapping) or not isinstance(evidence, Mapping):
            raise ProposalLedgerCorruption("PROPOSAL_PAYLOAD_SHAPE_INVALID")
        if proposal.get("schema_version") != SCHEMA_VERSION:
            raise ProposalLedgerCorruption("PROPOSAL_SCHEMA_INVALID")
        if not isinstance(proposal.get("proposal_id"), str) or not proposal["proposal_id"].startswith("idea:"):
            raise ProposalLedgerCorruption("PROPOSAL_ID_INVALID")
        if proposal.get("novelty_disposition") not in NOVELTY_DISPOSITIONS:
            raise ProposalLedgerCorruption("PROPOSAL_NOVELTY_INVALID")
        if proposal.get("admission_disposition") not in ADMISSION_DISPOSITIONS:
            raise ProposalLedgerCorruption("PROPOSAL_ADMISSION_INVALID")
        reasons = proposal.get("rejection_reasons")
        if not isinstance(reasons, list) or any(reason not in REJECTION_REASONS for reason in reasons):
            raise ProposalLedgerCorruption("PROPOSAL_REJECTION_REASON_INVALID")
        if proposal.get("admission_disposition") == "ELIGIBLE_FOR_DISCOVERY" and reasons:
            raise ProposalLedgerCorruption("ELIGIBLE_PROPOSAL_HAS_REJECTION")
        if proposal.get("admission_disposition") == "ELIGIBLE_FOR_DISCOVERY":
            try:
                validate_evidence_hash(proposal.get("source_snapshot_identity"))
            except (AttributeError, TypeError, ValueError) as exc:
                raise ProposalLedgerCorruption("ELIGIBLE_PROPOSAL_SNAPSHOT_INVALID") from exc
        try:
            _timestamp(str(proposal.get("created_at")))
        except (TypeError, ValueError) as exc:
            raise ProposalLedgerCorruption("PROPOSAL_CREATED_AT_INVALID") from exc
        if evidence.get("authority_state") != AUTHORITY_STATE:
            raise ProposalLedgerCorruption("PROPOSAL_AUTHORITY_STATE_INVALID")
        if evidence.get("scheduler_mutation") is not False:
            raise ProposalLedgerCorruption("PROPOSAL_SCHEDULER_MUTATION_INVALID")
        if evidence.get("candidate_created") is not False:
            raise ProposalLedgerCorruption("PROPOSAL_CANDIDATE_BOUNDARY_INVALID")

    def _entries_unlocked(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        data = self.path.read_bytes()
        if data and not data.endswith(b"\n"):
            raise ProposalLedgerCorruption("PROPOSAL_LEDGER_TORN_TAIL")
        try:
            entries = list(read_jsonl(self.path))
        except Exception as exc:
            raise ProposalLedgerCorruption("PROPOSAL_LEDGER_MALFORMED_RECORD") from exc
        previous_hash = None
        for seq, entry in enumerate(entries, 1):
            self._validate_entry(entry, expected_seq=seq, previous_hash=previous_hash)
            previous_hash = entry["entry_hash"]
        return entries

    def entries(self) -> list[dict[str, Any]]:
        with self._transaction():
            return deepcopy(self._entries_unlocked())

    def proposals(self) -> list[dict[str, Any]]:
        return [entry["payload"]["proposal"] for entry in self.entries()]

    def verify(self) -> bool:
        self.entries()
        return True

    def _append_unlocked(self, payload: dict[str, Any], entries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        seq = len(entries) + 1
        previous_hash = entries[-1]["entry_hash"] if entries else None
        payload_hash = sha256_json(payload)
        entry = {
            "schema_version": LEDGER_SCHEMA_VERSION,
            "seq": seq,
            "kind": LEDGER_KIND,
            "previous_hash": previous_hash,
            "payload_hash": payload_hash,
            "payload": payload,
            "entry_hash": sha256_json({
                "seq": seq,
                "kind": LEDGER_KIND,
                "previous_hash": previous_hash,
                "payload_hash": payload_hash,
            }),
        }
        self._validate_entry(entry, expected_seq=seq, previous_hash=previous_hash)
        self._fault("before_ledger_append", seq=seq, attempt_id=payload["attempt_id"])
        append_jsonl(self.path, entry)
        self._fault("after_ledger_append", seq=seq, attempt_id=payload["attempt_id"])
        return entry

    def admit(self, raw_proposal: Mapping[str, Any]) -> AdmissionResult:
        if not isinstance(raw_proposal, Mapping):
            raise IdeaAdmissionError("raw proposal must be a mapping")
        raw = _sanitize_untrusted_claims(raw_proposal)
        try:
            raw_digest = sha256_json(raw)
        except (TypeError, ValueError) as exc:
            raise IdeaAdmissionError("raw proposal is not canonical-json serializable") from exc
        attempt_id = "idea-attempt:" + raw_digest

        with self._transaction():
            entries = self._entries_unlocked()
            for entry in entries:
                payload = entry["payload"]
                if payload.get("attempt_id") == attempt_id:
                    return AdmissionResult(
                        proposal=deepcopy(payload["proposal"]),
                        admission_evidence=deepcopy(payload["admission_evidence"]),
                        replayed=True,
                    )

            reasons = _minimal_raw_reasons(raw)
            forbidden = _find_forbidden_downstream_key(raw)
            self_certification = _self_certification_key(raw)
            authority_escalation = _authority_escalation(raw)
            if forbidden or self_certification or authority_escalation:
                reasons.append("OUTSIDE_AUTHORITY")

            if "OUTSIDE_AUTHORITY" not in reasons:
                try:
                    assert_pre_outcome_payload(raw)
                except OutcomeFirewallError:
                    reasons.append("OUTCOME_CONTAMINATED")

            bindings, source_reasons = _parse_source_bindings(raw)
            reasons.extend(source_reasons)

            identity = _proposal_identity(raw)
            reasons.extend(_critical_identity_reasons(identity))
            reasons.extend(_clock_identity_reasons(raw))
            reasons.extend(_falsifiability_reasons(raw))
            parents, parent_reasons = _validate_parent_ids(raw.get("parent_proposal_ids"))
            reasons.extend(parent_reasons)

            snapshot = _source_bundle_identity(bindings)
            fingerprint = _proposal_fingerprint(raw, identity)
            prior_proposals = [entry["payload"]["proposal"] for entry in entries]
            novelty, matches, prior_rejected = _classify_novelty(
                raw=raw,
                identity=identity,
                fingerprint=fingerprint,
                snapshot=snapshot,
                prior_proposals=prior_proposals,
                scientific_memory=self.scientific_memory,
            )
            memory_match = any(match.get("kind") == "SCIENTIFIC_MEMORY" for match in matches)
            reasons.extend(_novelty_rejections(novelty, prior_rejected, memory_match))

            reasons = sorted(set(reason for reason in reasons if reason in REJECTION_REASONS))
            admission = "REJECTED" if reasons else "ELIGIBLE_FOR_DISCOVERY"
            semantic_key = _semantic_key(identity)
            proposal_id = "idea:" + semantic_key
            source_identities = sorted({binding["source_identity"] for binding in bindings})
            provenance_refs = sorted({binding["provenance_ref"] for binding in bindings})
            created_at = utc_now()
            proposal = {
                "schema_version": SCHEMA_VERSION,
                "proposal_id": proposal_id,
                "policy_id": str(raw.get("policy_id") or UNKNOWN),
                "policy_family": str(raw.get("policy_family") or UNKNOWN),
                "created_at": created_at,
                "source_identities": source_identities,
                "source_snapshot_identity": snapshot,
                "provenance_ref": provenance_refs,
                "proposal_fingerprint": fingerprint,
                "semantic_identity": {**identity, "semantic_key": semantic_key},
                "parent_proposal_ids": parents,
                "mechanism_claim": raw.get("mechanism_claim", UNKNOWN),
                "actor_identity": raw.get("actor_identity", UNKNOWN),
                "universe_identity": raw.get("universe_identity", UNKNOWN),
                "clock_identity": deepcopy(raw.get("clock_identity", UNKNOWN)),
                "horizon_identity": raw.get("horizon_identity", UNKNOWN),
                "falsifiable_claim": deepcopy(raw.get("falsifiable_claim", {})),
                "assumptions": deepcopy(list(raw.get("assumptions") or [])),
                "prior_proposal_matches": matches,
                "novelty_disposition": novelty,
                "admission_disposition": admission,
                "rejection_reasons": reasons,
                "lineage_version": 1,
                "generator_trust": "UNTRUSTED",
            }
            evidence = {
                "source_bindings": deepcopy(bindings),
                "authority_state": deepcopy(AUTHORITY_STATE),
                "pre_outcome_firewall": "PASS" if "OUTCOME_CONTAMINATED" not in reasons else "REJECT",
                "semantic_identity_complete": not any(
                    identity.get(field) == UNKNOWN for field in CRITICAL_IDENTITY_FIELDS
                ),
                "falsifiability": "PASS" if "NON_FALSIFIABLE" not in reasons else "REJECT",
                "novelty_disposition": novelty,
                "rejection_reasons": deepcopy(reasons),
                "scheduler_mutation": False,
                "candidate_created": False,
                "discovery_boundary": "STOP_AT_ELIGIBLE_FOR_DISCOVERY",
            }
            payload = {
                "attempt_id": attempt_id,
                "proposal": proposal,
                "admission_evidence": evidence,
            }
            self._append_unlocked(payload, entries)
            return AdmissionResult(proposal=proposal, admission_evidence=evidence, replayed=False)


def discovery_handoff(result: AdmissionResult | Mapping[str, Any]) -> dict[str, Any]:
    """Return the narrow downstream handoff; never construct a Candidate."""
    if isinstance(result, AdmissionResult):
        proposal = result.proposal
        evidence = result.admission_evidence
    else:
        proposal = result.get("proposal") if isinstance(result, Mapping) else None
        evidence = result.get("admission_evidence") if isinstance(result, Mapping) else None
    if not isinstance(proposal, Mapping) or not isinstance(evidence, Mapping):
        raise IdeaAdmissionError("invalid admission result")
    if proposal.get("admission_disposition") != "ELIGIBLE_FOR_DISCOVERY":
        raise IdeaAdmissionError("only ELIGIBLE_FOR_DISCOVERY proposals may be handed off")
    return {
        "schema_version": HANDOFF_SCHEMA_VERSION,
        "proposal_id": proposal["proposal_id"],
        "semantic_identity": deepcopy(proposal["semantic_identity"]),
        "provenance_ref": deepcopy(proposal["provenance_ref"]),
        "source_snapshot_identity": proposal["source_snapshot_identity"],
        "parent_proposal_ids": deepcopy(proposal["parent_proposal_ids"]),
        "mechanism_claim": proposal["mechanism_claim"],
        "universe_identity": proposal["universe_identity"],
        "clock_identity": deepcopy(proposal["clock_identity"]),
        "horizon_identity": proposal["horizon_identity"],
        "falsifiable_claim": deepcopy(proposal["falsifiable_claim"]),
        "assumptions": deepcopy(proposal["assumptions"]),
        "novelty_disposition": proposal["novelty_disposition"],
        "admission_evidence": deepcopy(evidence),
        "terminal_state": "ELIGIBLE_FOR_DISCOVERY",
        "candidate_created": False,
    }


def run_intake_cycle(
    policies: Sequence[IdeationPolicy],
    *,
    context: Mapping[str, Any],
    ledger: ProposalLedger,
    max_new_proposals_per_cycle: int = 8,
) -> dict[str, Any]:
    """Run bounded *proposal generation only*; no task, queue, or runtime mutation."""
    if (
        isinstance(max_new_proposals_per_cycle, bool)
        or not isinstance(max_new_proposals_per_cycle, int)
        or max_new_proposals_per_cycle < 0
    ):
        raise ValueError("max_new_proposals_per_cycle must be a non-negative integer")
    if context.get("frontier_state") == "SCIENTIFICALLY_EXHAUSTED":
        return {
            "status": "NOOP_FRONTIER_SCIENTIFICALLY_EXHAUSTED",
            "generated_count": 0,
            "new_eligible_count": 0,
            "decisions": [],
            "policy_errors": [],
            "scheduler_mutation": False,
            "candidate_objects_created": False,
        }

    remaining = int(max_new_proposals_per_cycle)
    decisions: list[dict[str, Any]] = []
    policy_errors: list[dict[str, str]] = []
    generated_count = 0
    new_eligible_count = 0

    for policy in policies:
        if remaining <= 0:
            break
        try:
            proposals = policy.propose(context, remaining)
        except Exception as exc:
            policy_errors.append({"policy_id": policy.policy_id, "error": type(exc).__name__})
            continue
        for raw in proposals:
            if remaining <= 0:
                break
            remaining -= 1
            generated_count += 1
            result = ledger.admit(raw)
            decisions.append(result.to_dict())
            if (
                not result.replayed
                and result.proposal.get("admission_disposition") == "ELIGIBLE_FOR_DISCOVERY"
            ):
                new_eligible_count += 1

    if new_eligible_count:
        status = "ELIGIBLE_FOR_DISCOVERY"
    elif generated_count == 0 and context.get("qualified_sources_available") is False:
        status = "NOOP_NO_QUALIFIED_SOURCE"
    elif generated_count == 0:
        status = "NOOP_NO_ADMISSIBLE_PROPOSAL"
    else:
        duplicate_like = all(
            decision["replayed"]
            or any(reason in {"DUPLICATE", "NEAR_DUPLICATE", "ALREADY_EXPLORED"}
                   for reason in decision["proposal"]["rejection_reasons"])
            for decision in decisions
        )
        status = "NOOP_NO_NOVEL_PROPOSAL" if duplicate_like else "NOOP_NO_ADMISSIBLE_PROPOSAL"

    return {
        "status": status,
        "generated_count": generated_count,
        "new_eligible_count": new_eligible_count,
        "decisions": decisions,
        "policy_errors": policy_errors,
        "scheduler_mutation": False,
        "candidate_objects_created": False,
    }
