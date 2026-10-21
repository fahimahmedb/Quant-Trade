from __future__ import annotations

from copy import deepcopy
from itertools import combinations
from math import isfinite
import re
from typing import Any, Dict, Iterable, List, Tuple

from research.research_os.scientific_store import sha256_json
from .v2_core import SEMANTIC_NULLS


_UNKNOWN = (SEMANTIC_NULLS - {"NOT_APPLICABLE"}) | {"", "UNQUALIFIED", "NOT_QUALIFIED", "UNAVAILABLE"}
_FIELD_STATES = {"KNOWN", "UNKNOWN", "NOT_APPLICABLE", "CONFLICTED"}
_CORE_FIELDS = ("payer", "mechanism", "timing_clock")
_STRICT_COMPLETE_FIELDS = {
    "payer", "forced_constrained_actor", "mechanism", "instrument", "universe",
    "timing_clock", "horizon", "capacity_bottleneck", "cost_structure",
    "economic_exposure", "event_rule_dependency", "source_identity",
}

# Diagnostics only: never statistical correlation and never outcome-derived.
_STRUCTURAL_WEIGHTS = {
    "payer": 0.16,
    "forced_constrained_actor": 0.12,
    "mechanism": 0.18,
    "instrument": 0.10,
    "universe": 0.08,
    "timing_clock": 0.16,
    "horizon": 0.06,
    "capacity_bottleneck": 0.04,
    "cost_structure": 0.04,
    "economic_exposure": 0.03,
    "event_rule_dependency": 0.02,
    "source_identity": 0.01,
}


def _semantic_state(value: Any) -> str:
    if isinstance(value, dict) and "status" in value:
        status = str(value.get("status", "")).strip().upper()
        return status if status in _FIELD_STATES else "UNKNOWN"
    if isinstance(value, str):
        normalized = value.strip().upper()
        if normalized == "NOT_APPLICABLE":
            return "NOT_APPLICABLE"
        if normalized in _UNKNOWN:
            return "UNKNOWN"
    return "KNOWN" if _is_known(value) else "UNKNOWN"


def _is_known(value: Any) -> bool:
    if isinstance(value, dict) and "status" in value:
        if _semantic_state(value) != "KNOWN":
            return False
        return _is_known(value.get("value"))
    if isinstance(value, str):
        normalized = value.strip().upper()
        return bool(value.strip()) and normalized not in _UNKNOWN and normalized != "NOT_APPLICABLE"
    if isinstance(value, bool):
        return False
    if isinstance(value, float):
        return isfinite(value)
    if isinstance(value, dict):
        return any(_is_known(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_is_known(item) for item in value)
    return value is not None


def _fully_known_assumption_value(value: Any) -> bool:
    """A structured economic fact is known only when every declared atom is usable."""
    if isinstance(value, dict) and "status" in value:
        if _semantic_state(value) != "KNOWN":
            return False
        return _fully_known_assumption_value(value.get("value"))
    if value is None or isinstance(value, bool):
        return False
    if isinstance(value, str):
        return _is_known(value)
    if isinstance(value, float):
        return isfinite(value)
    if isinstance(value, dict):
        return bool(value) and all(_fully_known_assumption_value(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return bool(value) and all(_fully_known_assumption_value(item) for item in value)
    return True


def _validated_memory_refs(value: Any) -> List[str]:
    """Memory is opaque structural context; malformed refs never become silent evidence."""
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("economic identity memory refs must be a list")
    refs: List[str] = []
    for ref in value:
        if not isinstance(ref, str) or not _is_known(ref):
            raise ValueError("economic identity memory ref must be a known string")
        refs.append(ref.strip())
    return sorted(set(refs))


def _stable_value(value: Any) -> Any:
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, list):
        return sorted(value) if all(isinstance(v, str) for v in value) else value
    return value


def _canonical_text(value: str) -> str:
    # Only syntactic normalization. Semantic aliases require an explicit canonical_id.
    value = value.strip().casefold()
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value


def _canonical_value(value: Any, *, canonical_id: Any = None) -> Any:
    if _is_known(canonical_id):
        return _canonical_text(str(canonical_id))
    value = _stable_value(value)
    if isinstance(value, str):
        return _canonical_text(value)
    if isinstance(value, list):
        return sorted(_canonical_value(item) for item in value)
    if isinstance(value, dict):
        return sha256_json(value)
    return value


def _field_input(value: Any, path: str, *, strict_complete: bool = False) -> Dict[str, Any]:
    if isinstance(value, dict) and "status" in value:
        status = _semantic_state(value)
        raw_value = deepcopy(_stable_value(value.get("value", status)))
        canonical_id = value.get("canonical_id")
        evidence_refs = value.get("evidence_refs", [])
        if not isinstance(evidence_refs, list):
            evidence_refs = []
        known_check = _fully_known_assumption_value if strict_complete else _is_known
        if status == "KNOWN" and not known_check(raw_value):
            status = "UNKNOWN"
            raw_value = "UNKNOWN"
        return {
            "status": status,
            "value": raw_value,
            "canonical_value": _canonical_value(raw_value, canonical_id=canonical_id) if status == "KNOWN" else None,
            "canonical_id": deepcopy(canonical_id) if _is_known(canonical_id) else None,
            "evidence_refs": deepcopy(evidence_refs),
            "assumption": deepcopy(value.get("assumption")) if "assumption" in value else None,
            "source_path": path,
        }
    status = _semantic_state(value)
    if strict_complete and status == "KNOWN" and not _fully_known_assumption_value(value):
        status = "UNKNOWN"
    raw_value = deepcopy(_stable_value(value)) if status == "KNOWN" else status
    return {
        "status": status,
        "value": raw_value,
        "canonical_value": _canonical_value(raw_value) if status == "KNOWN" else None,
        "canonical_id": None,
        "evidence_refs": [],
        "assumption": None,
        "source_path": path,
    }


def _select_field(
    name: str,
    primary: Iterable[Tuple[Any, str]],
    fallback: Iterable[Tuple[Any, str]] = (),
) -> Dict[str, Any]:
    """Choose one field without silently normalizing contradictory known inputs."""
    strict_complete = name in _STRICT_COMPLETE_FIELDS
    for group in (tuple(primary), tuple(fallback)):
        records = [
            _field_input(value, path, strict_complete=strict_complete)
            for value, path in group if value is not None
        ]
        if not records:
            continue
        explicit_conflict = [record for record in records if record["status"] == "CONFLICTED"]
        known = [record for record in records if record["status"] == "KNOWN"]
        if explicit_conflict:
            return {
                "status": "CONFLICTED", "value": "CONFLICTED", "canonical_value": None,
                "canonical_id": None, "evidence_refs": [], "assumption": None,
                "source_path": "+".join(record["source_path"] for record in explicit_conflict),
                "conflict_values": [record["value"] for record in explicit_conflict],
            }
        if known:
            distinct = {repr(record["canonical_value"]) for record in known}
            if len(distinct) > 1:
                return {
                    "status": "CONFLICTED", "value": "CONFLICTED", "canonical_value": None,
                    "canonical_id": None,
                    "evidence_refs": sorted({ref for record in known for ref in record["evidence_refs"]}),
                    "assumption": None,
                    "source_path": "+".join(record["source_path"] for record in known),
                    "conflict_values": [record["value"] for record in known],
                }
            selected = known[0]
            selected["conflict_values"] = []
            return selected
        not_applicable = [record for record in records if record["status"] == "NOT_APPLICABLE"]
        if not_applicable and len(not_applicable) == len(records):
            selected = not_applicable[0]
            selected["conflict_values"] = []
            return selected
    return {
        "status": "UNKNOWN", "value": "UNKNOWN", "canonical_value": None,
        "canonical_id": None, "evidence_refs": [], "assumption": None,
        "source_path": "UNKNOWN", "conflict_values": [],
    }


def _candidate_from_identity(identity: Dict[str, Any]) -> Dict[str, Any]:
    basis = identity.get("documentary_basis")
    if isinstance(basis, dict) and isinstance(basis.get("candidate"), dict):
        return basis["candidate"]
    snapshot = identity.get("candidate_snapshot")
    if isinstance(snapshot, dict):
        return snapshot
    return {}


def _verify_identity_binding(identity: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
    provenance = identity.get("identity_provenance")
    provenance = provenance if isinstance(provenance, dict) else {}
    binding = identity.get("candidate_binding", provenance.get("candidate_binding"))
    if binding is None:
        if candidate:
            binding = {
                "hypothesis_id": candidate.get("hypothesis_id"),
                "generation_id": candidate.get("generation_id"),
                "candidate_hash": provenance.get("candidate_hash", sha256_json(candidate)),
            }
        else:
            return {"status": "UNBOUND", "candidate_hash": provenance.get("candidate_hash", "UNKNOWN")}
    if not isinstance(binding, dict):
        raise ValueError("economic identity candidate binding must be a mapping")
    if binding.get("hypothesis_id") not in (None, identity.get("hypothesis_id")):
        raise ValueError("economic identity hypothesis binding mismatch")
    if binding.get("generation_id") not in (None, identity.get("generation_id")):
        raise ValueError("economic identity generation binding mismatch")
    if candidate:
        expected = sha256_json(candidate)
        declared = binding.get("candidate_hash", provenance.get("candidate_hash"))
        if _is_known(declared) and declared != expected:
            raise ValueError("economic identity candidate hash binding mismatch")
        if candidate.get("hypothesis_id") != identity.get("hypothesis_id"):
            raise ValueError("economic identity candidate hypothesis mismatch")
        if candidate.get("generation_id") != identity.get("generation_id"):
            raise ValueError("economic identity candidate generation mismatch")
        return {"status": "BOUND", "candidate_hash": expected}
    return {
        "status": "DECLARED",
        "candidate_hash": binding.get("candidate_hash", provenance.get("candidate_hash", "UNKNOWN")),
    }


def structural_identity(identity: Dict[str, Any]) -> Dict[str, Any]:
    """Canonical pre-outcome economic fingerprint with explicit uncertainty."""
    _verify_documentary_identity(identity)
    candidate = _candidate_from_identity(identity)
    binding = _verify_identity_binding(identity, candidate)
    provenance = identity.get("identity_provenance", {})
    if not isinstance(provenance, dict):
        provenance = {}

    candidate_hash = binding.get("candidate_hash", "UNKNOWN")
    if not _is_known(candidate_hash) and candidate:
        candidate_hash = sha256_json(candidate)
    if not _is_known(candidate_hash):
        candidate_hash = "UNKNOWN"
    source_hash = provenance.get("source_hash", "UNKNOWN")
    dossier_hash = provenance.get("dossier_hash", "UNKNOWN")
    source_refs = provenance.get("source_refs", [])
    memory_refs = _validated_memory_refs(provenance.get("memory_refs", identity.get("memory_refs", [])))

    specs = {
        "payer": (((identity.get("payer"), "identity.payer"), (candidate.get("payer"), "candidate.payer")), ()),
        "forced_constrained_actor": (((identity.get("forced_constrained_actor"), "identity.forced_constrained_actor"),
            (identity.get("forced_actor"), "identity.forced_actor"), (identity.get("constrained_actor"), "identity.constrained_actor"),
            (candidate.get("forced_constrained_actor"), "candidate.forced_constrained_actor"),
            (candidate.get("forced_actor"), "candidate.forced_actor"), (candidate.get("constrained_actor"), "candidate.constrained_actor")), ()),
        "mechanism": (((identity.get("mechanism"), "identity.mechanism"), (candidate.get("mechanism"), "candidate.mechanism")), ()),
        "instrument": (((identity.get("instrument"), "identity.instrument"), (candidate.get("instrument"), "candidate.instrument")),
            ((identity.get("asset"), "identity.asset"),)),
        "universe": (((identity.get("universe"), "identity.universe"), (candidate.get("universe"), "candidate.universe")), ()),
        "timing_clock": (((identity.get("timing_clock"), "identity.timing_clock"), (identity.get("clock"), "identity.clock"),
            (candidate.get("timing_clock"), "candidate.timing_clock"), (candidate.get("clock"), "candidate.clock")), ()),
        "horizon": (((identity.get("horizon"), "identity.horizon"), (candidate.get("horizon"), "candidate.horizon")), ()),
        "capacity_bottleneck": (((identity.get("capacity_bottleneck"), "identity.capacity_bottleneck"),
            (candidate.get("capacity_bottleneck"), "candidate.capacity_bottleneck")), ((identity.get("capacity"), "identity.capacity"),)),
        "cost_structure": (((identity.get("cost_structure"), "identity.cost_structure"), (candidate.get("cost_structure"), "candidate.cost_structure")), ()),
        "economic_exposure": (((identity.get("economic_exposure"), "identity.economic_exposure"),
            (candidate.get("economic_exposure"), "candidate.economic_exposure")), ()),
        "event_rule_dependency": (((identity.get("event_rule_dependency"), "identity.event_rule_dependency"),
            (candidate.get("event_rule_dependency"), "candidate.event_rule_dependency")), ()),
        "source_identity": (((identity.get("source_identity"), "identity.source_identity"),),
            ((source_hash, "identity_provenance.source_hash"),)),
    }

    fields: Dict[str, Any] = {}
    by_state = {state: [] for state in _FIELD_STATES}
    identity_hash_payload = deepcopy(identity)
    identity_hash_payload.pop("memory_refs", None)
    identity_hash = sha256_json(identity_hash_payload)
    for name, (primary, fallback) in specs.items():
        record = _select_field(name, primary, fallback)
        by_state[record["status"]].append(name)
        fields[name] = {
            "value": record["value"],
            "status": record["status"],
            "canonical_value": record["canonical_value"],
            "canonical_id": record["canonical_id"],
            "evidence_refs": deepcopy(record["evidence_refs"]),
            "assumption": deepcopy(record["assumption"]),
            "conflict_values": deepcopy(record["conflict_values"]),
            "provenance": {
                "hypothesis_id": identity.get("hypothesis_id", "UNKNOWN"),
                "generation_id": identity.get("generation_id", "UNKNOWN"),
                "candidate_hash": candidate_hash,
                "source_hash": source_hash if _is_known(source_hash) else "UNKNOWN",
                "dossier_hash": dossier_hash if _is_known(dossier_hash) else "UNKNOWN",
                "identity_hash": identity_hash,
                "source_path": record["source_path"],
                "source_refs": deepcopy(source_refs) if isinstance(source_refs, list) else [],
            },
        }

    blockers = []
    for field in _CORE_FIELDS:
        state = fields[field]["status"]
        if state != "KNOWN":
            blockers.append(f"CORE_{field.upper()}_{state}")
    blockers.extend(f"FIELD_{field.upper()}_CONFLICTED" for field in by_state["CONFLICTED"] if field not in _CORE_FIELDS)
    readiness = "QUALIFIED_CURRENT" if not blockers else "PARTIAL_WITH_EXPLICIT_BLOCKER"
    applicable = len(fields) - len(by_state["NOT_APPLICABLE"])
    known_fraction = round(len(by_state["KNOWN"]) / applicable, 4) if applicable else 0.0

    return {
        "hypothesis_id": identity.get("hypothesis_id", "UNKNOWN"),
        "generation_id": identity.get("generation_id", "UNKNOWN"),
        "fields": fields,
        "known_fields": sorted(by_state["KNOWN"]),
        "unknown_fields": sorted(by_state["UNKNOWN"]),
        "not_applicable_fields": sorted(by_state["NOT_APPLICABLE"]),
        "conflicted_fields": sorted(by_state["CONFLICTED"]),
        "identity_completeness": {"known_fraction": known_fraction, "applicable_field_count": applicable},
        "identity_readiness": {"status": readiness, "blockers": sorted(blockers), "required_core_fields": list(_CORE_FIELDS)},
        "candidate_binding": binding,
        "identity_hash": identity_hash,
        "candidate_immutable": True,
        "empirical_return_data_consumed": False,
        "memory_context": {
            "refs": deepcopy(memory_refs),
            "structural_context_only": True,
            "empirical_correlation_inferred": False,
            "expected_alpha_inferred": False,
        },
    }


def _field_relation(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    ls, rs = left["status"], right["status"]
    if "CONFLICTED" in {ls, rs}:
        relation, overlap = "CONFLICTED", None
    elif "UNKNOWN" in {ls, rs}:
        relation, overlap = "UNKNOWN", None
    elif ls == rs == "NOT_APPLICABLE":
        relation, overlap = "NOT_APPLICABLE", None
    elif "NOT_APPLICABLE" in {ls, rs}:
        relation, overlap = "INCOMPARABLE", None
    elif left["canonical_value"] == right["canonical_value"]:
        relation, overlap = "SAME", 1.0
    else:
        relation, overlap = "DIFFERENT", 0.0
    return {
        "relation": relation,
        "overlap": overlap,
        "left_status": ls,
        "right_status": rs,
        "left_value": deepcopy(left["value"]),
        "right_value": deepcopy(right["value"]),
        "left_canonical_id": deepcopy(left.get("canonical_id")),
        "right_canonical_id": deepcopy(right.get("canonical_id")),
    }


def _jaccard(left: Iterable[str], right: Iterable[str]) -> Any:
    a = {_canonical_text(value) for value in left or [] if isinstance(value, str) and _is_known(value)}
    b = {_canonical_text(value) for value in right or [] if isinstance(value, str) and _is_known(value)}
    if not a or not b:
        return None
    return round(len(a & b) / len(a | b), 4)


def _eq_known(left: Any, right: Any) -> Any:
    l = _field_input(left, "left")
    r = _field_input(right, "right")
    return _field_relation(l, r)["overlap"]


def _relationship_signals(rel: Dict[str, str]) -> List[str]:
    """Named structural motifs. They are review diagnostics, never empirical evidence."""
    signals: List[str] = []
    if rel["mechanism"] == "SAME" and rel["instrument"] == "DIFFERENT":
        signals.append("SAME_MECHANISM_DIFFERENT_INSTRUMENT")
    if rel["payer"] == "SAME" and rel["timing_clock"] == "DIFFERENT":
        signals.append("SAME_PAYER_DIFFERENT_CLOCK")
    if rel["event_rule_dependency"] == "SAME" and rel["horizon"] == "DIFFERENT":
        signals.append("SAME_EVENT_DEPENDENCY_DIFFERENT_HORIZON")
    if rel["economic_exposure"] == "SAME" and rel["instrument"] == "DIFFERENT":
        signals.append("SAME_EXPOSURE_DIFFERENT_WRAPPER")
    if (
        rel["payer"] == "SAME"
        and rel["forced_constrained_actor"] == "SAME"
        and rel["mechanism"] == "UNKNOWN"
    ):
        signals.append("SAME_PAYER_ACTOR_MECHANISM_UNRESOLVED")
    if (
        rel["mechanism"] == "SAME"
        and rel["source_identity"] == "DIFFERENT"
    ):
        signals.append("SAME_MECHANISM_DIFFERENT_SOURCE_IDENTITY")
    return sorted(signals)


def structural_pair(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    left_struct = structural_identity(left)
    right_struct = structural_identity(right)
    relationships = {
        key: _field_relation(left_struct["fields"][key], right_struct["fields"][key])
        for key in _STRUCTURAL_WEIGHTS
    }
    structural_dimensions = {key: record["overlap"] for key, record in relationships.items()}
    legacy_dimensions = {
        "asset": _eq_known(left.get("asset"), right.get("asset")),
        "liquidity": _eq_known(left.get("liquidity"), right.get("liquidity")),
        "tail_exposure": _eq_known(left.get("tail_exposure"), right.get("tail_exposure")),
        "economic_tags": _jaccard(left.get("economic_tags", []), right.get("economic_tags", [])),
    }
    dimensions = {**structural_dimensions, **legacy_dimensions}
    unresolved = sorted(key for key, value in structural_dimensions.items() if value is None)
    score = round(
        sum((structural_dimensions[key] or 0.0) * _STRUCTURAL_WEIGHTS[key] for key in structural_dimensions),
        4,
    )
    potentially_same = [key for key in unresolved if relationships[key]["relation"] in {"UNKNOWN", "INCOMPARABLE"}]
    max_score = round(score + sum(_STRUCTURAL_WEIGHTS[key] for key in potentially_same), 4)

    rel = {key: relationships[key]["relation"] for key in relationships}
    signals = _relationship_signals(rel)
    core_known = all(rel[key] in {"SAME", "DIFFERENT"} for key in _CORE_FIELDS)
    core_same = core_known and all(rel[key] == "SAME" for key in _CORE_FIELDS)
    conflicts = sorted(key for key, value in rel.items() if value == "CONFLICTED")
    payer_mechanism_same = rel["payer"] == "SAME" and rel["mechanism"] == "SAME"
    payer_and_mechanism_different = rel["payer"] == "DIFFERENT" and rel["mechanism"] == "DIFFERENT"
    explicit_same_exposure = rel["economic_exposure"] == "SAME"
    payer_actor_mechanism_unresolved = "SAME_PAYER_ACTOR_MECHANISM_UNRESOLVED" in signals

    review_basis: List[str] = []
    if conflicts:
        classification = "CONFLICTED_IDENTITY_REVIEW"
        review_required = True
        review_basis = conflicts
    elif core_same:
        classification = "HIGH_STRUCTURAL_OVERLAP_REVIEW"
        review_required = True
        review_basis = list(_CORE_FIELDS)
    elif payer_mechanism_same:
        classification = "RELATED_EXPOSURE_REVIEW"
        review_required = True
        review_basis = ["payer", "mechanism"]
    elif explicit_same_exposure:
        classification = "RELATED_EXPOSURE_REVIEW"
        review_required = True
        review_basis = ["economic_exposure"]
    elif payer_actor_mechanism_unresolved:
        classification = "RELATED_EXPOSURE_REVIEW"
        review_required = True
        review_basis = ["payer", "forced_constrained_actor", "mechanism:UNKNOWN"]
    elif payer_and_mechanism_different:
        classification = "STRUCTURALLY_DISTINGUISHABLE"
        review_required = False
    elif not core_known:
        classification = "UNKNOWN"
        review_required = False
    elif score >= 0.50:
        classification = "HIGH_STRUCTURAL_OVERLAP_REVIEW"
        review_required = True
        review_basis = sorted(key for key, value in rel.items() if value == "SAME")
    elif score >= 0.25:
        classification = "PARTIAL_STRUCTURAL_OVERLAP"
        review_required = False
    else:
        classification = "STRUCTURALLY_DISTINGUISHABLE"
        review_required = False

    same_fields = sorted(key for key, value in rel.items() if value == "SAME")
    different_fields = sorted(key for key, value in rel.items() if value == "DIFFERENT")
    unknown_fields = sorted(key for key, value in rel.items() if value == "UNKNOWN")
    return {
        "left": left["hypothesis_id"],
        "right": right["hypothesis_id"],
        "structural_overlap_score": score,
        "dimensions": dimensions,
        "field_relationships": relationships,
        "relationship_signals": signals,
        "same_fields": same_fields,
        "different_fields": different_fields,
        "unknown_dimensions": sorted(set(unresolved) | {key for key, value in legacy_dimensions.items() if value is None}),
        "conflicted_dimensions": conflicts,
        "score_status": "PARTIAL" if unresolved else "COMPLETE",
        "overlap_score_interval": [score, max_score],
        "identity_hashes": [left_struct["identity_hash"], right_struct["identity_hash"]],
        "candidate_hashes": [
            left_struct["candidate_binding"].get("candidate_hash", "UNKNOWN"),
            right_struct["candidate_binding"].get("candidate_hash", "UNKNOWN"),
        ],
        "source_hashes": [
            left_struct["fields"]["source_identity"]["provenance"]["source_hash"],
            right_struct["fields"]["source_identity"]["provenance"]["source_hash"],
        ],
        "dossier_hashes": [
            left_struct["fields"]["source_identity"]["provenance"]["dossier_hash"],
            right_struct["fields"]["source_identity"]["provenance"]["dossier_hash"],
        ],
        "generations": [left.get("generation_id", "UNKNOWN"), right.get("generation_id", "UNKNOWN")],
        "classification": classification,
        "same_exposure_review_required": review_required,
        "review_basis": review_basis,
        "explanation": {
            "decisive_same_fields": review_basis if review_required else same_fields,
            "different_fields": different_fields,
            "unknown_fields": unknown_fields,
            "conflicted_fields": conflicts,
            "relationship_signals": signals,
            "source_identity_difference_is_not_independence_evidence": rel["source_identity"] == "DIFFERENT",
        },
        "empirical_correlation": "UNAVAILABLE",
        "empirical_correlation_reason": "NO_ADMISSIBLE_RETURN_DATA_CONSUMED",
        "statistical_correlation": "UNAVAILABLE_BY_DESIGN",
        "return_series_consumed": False,
        "structural_identity": {"left": left_struct, "right": right_struct},
    }


def _portfolio_pair(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """Preserve legacy seven-axis summary while retaining canonical economic structure."""
    pair = structural_pair(left, right)
    pair["economic_structure"] = {key: deepcopy(pair[key]) for key in (
        "classification", "structural_overlap_score", "dimensions", "field_relationships", "relationship_signals",
        "same_fields", "different_fields", "unknown_dimensions", "conflicted_dimensions",
        "score_status", "overlap_score_interval", "same_exposure_review_required", "review_basis", "explanation",
    )}
    weights = {
        "mechanism": .15, "payer": .20, "asset": .15, "horizon": .10,
        "liquidity": .05, "tail_exposure": .10, "economic_tags": .25,
    }
    dimensions = {
        key: (_jaccard(left.get(key, []), right.get(key, [])) if key == "economic_tags"
              else _eq_known(left.get(key), right.get(key)))
        for key in weights
    }
    unknown = sorted(key for key, value in dimensions.items() if value is None)
    score = round(sum((dimensions[key] or 0) * weights[key] for key in dimensions), 4)
    pair["legacy_v2_summary"] = {
        "dimensions": dimensions,
        "unknown_dimensions": unknown,
        "structural_overlap_score": score,
        "score_status": "PARTIAL" if unknown else "COMPLETE",
        "overlap_score_interval": [score, round(score + sum(weights[k] for k in unknown), 4)],
        "classification": (
            "INSUFFICIENT_EVIDENCE" if unknown else
            "HIGH_STRUCTURAL_OVERLAP" if score >= .65 else
            "PARTIAL_STRUCTURAL_OVERLAP" if score >= .30 else
            "STRUCTURALLY_DISTINCT_OR_UNKNOWN"
        ),
    }
    # Compatibility keys remain legacy while economic_structure is canonical.
    pair.update(pair["legacy_v2_summary"])
    return pair


def portfolio_diagnostics_v2(identities: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    items = list(identities)
    projections = [structural_identity(item) for item in items]
    keys = [item["hypothesis_id"] for item in items]
    if len(set(keys)) != len(keys):
        raise ValueError("portfolio requires one selected generation per hypothesis")

    pairwise = [_portfolio_pair(a, b) for a, b in combinations(items, 2)]
    novelty: Dict[str, Any] = {}
    for item in items:
        related = [p for p in pairwise if item["hypothesis_id"] in {p["left"], p["right"]}]
        if not related or any(
            p["economic_structure"]["classification"] in {"UNKNOWN", "CONFLICTED_IDENTITY_REVIEW"}
            for p in related
        ):
            novelty[item["hypothesis_id"]] = "UNKNOWN"
        elif all(p["economic_structure"]["score_status"] == "COMPLETE" for p in related):
            novelty[item["hypothesis_id"]] = round(
                1.0 - max(p["economic_structure"]["structural_overlap_score"] for p in related), 4
            )
        else:
            novelty[item["hypothesis_id"]] = "UNKNOWN"

    structural_blockers = []
    for projection in projections:
        structural_blockers.extend(
            f"{projection['hypothesis_id']}:{code}"
            for code in projection["identity_readiness"]["blockers"]
        )
    for pair in pairwise:
        if pair["economic_structure"]["classification"] == "CONFLICTED_IDENTITY_REVIEW":
            structural_blockers.append(f"{pair['left']}:{pair['right']}:IDENTITY_CONFLICT")
    structural_status = "QUALIFIED_CURRENT" if not structural_blockers else "PARTIAL_WITH_EXPLICIT_BLOCKER"

    decision_blockers: List[str] = []
    if len(items) < 2:
        decision_blockers.append("INSUFFICIENT_CANDIDATES_FOR_RELATIONSHIP_MAP")
    for projection in projections:
        if not _is_known(projection["hypothesis_id"]):
            decision_blockers.append("IDENTITY_HYPOTHESIS_ID_UNKNOWN")
        if not _is_known(projection["generation_id"]):
            decision_blockers.append(f"{projection['hypothesis_id']}:GENERATION_ID_UNKNOWN")
        binding = projection["candidate_binding"]
        if binding.get("status") != "BOUND" or not _is_known(binding.get("candidate_hash")):
            decision_blockers.append(f"{projection['hypothesis_id']}:CANDIDATE_BINDING_NOT_VERIFIED")
    for pair in pairwise:
        economic = pair["economic_structure"]
        pair_id = f"{pair['left']}:{pair['right']}"
        if economic["classification"] == "CONFLICTED_IDENTITY_REVIEW":
            decision_blockers.append(f"{pair_id}:IDENTITY_CONFLICT")
        elif economic["classification"] == "UNKNOWN":
            decision_blockers.append(f"{pair_id}:RELATIONSHIP_UNKNOWN")
        if economic["same_exposure_review_required"]:
            decision_blockers.append(f"{pair_id}:SAME_EXPOSURE_REVIEW_REQUIRED")
        if economic["score_status"] != "COMPLETE":
            decision_blockers.append(f"{pair_id}:RELATIONSHIP_INCOMPLETE")
    decision_status = "QUALIFIED_CURRENT" if not decision_blockers else "PARTIAL_WITH_EXPLICIT_BLOCKER"

    return {
        "portfolio_engine": "portfolio-diagnostics.v2",
        "candidate_count": len(items),
        "structural_identities": projections,
        "pairwise": pairwise,
        "same_exposure_review_pairs": [
            {"left": p["left"], "right": p["right"], "basis": p["economic_structure"]["review_basis"]}
            for p in pairwise if p["economic_structure"]["same_exposure_review_required"]
        ],
        "structural_novelty": novelty,
        "portfolio_readiness": {
            "structural_mapping": {
                "status": structural_status,
                "blockers": sorted(set(structural_blockers)),
            },
            "pre_outcome_decision": {
                "status": decision_status,
                "blockers": sorted(set(decision_blockers)),
                "relationship_count": len(pairwise),
                "requires_verified_candidate_binding": True,
                "unknown_is_not_diversification": True,
                "same_exposure_review_is_not_portfolio_clearance": True,
            },
            "empirical_layer": {
                "status": "SEALED_BY_AUTHORITY",
                "blockers": [
                    "NO_ADMISSIBLE_RETURN_SERIES_CONSUMED",
                    "ECONOMIC_EXPERIMENT_AUTHORITY_CLOSED",
                    "PROSPECTIVE_OBSERVATION_AUTHORITY_CLOSED",
                ],
                "facts_required_before_empirical_analysis": [
                    "ADMISSIBLE_RETURN_SERIES_WITH_PROVENANCE",
                    "FROZEN_EMPIRICAL_PORTFOLIO_PROTOCOL",
                    "AUTHORIZED_OUTCOME_ACCESS",
                    "OBSERVED_COST_AND_CAPACITY_INPUTS_WHERE_REQUIRED",
                ],
                "requirements_do_not_grant_authority": True,
            },
        },
        "empirical_correlation": "UNAVAILABLE",
        "empirical_correlation_reason": "NO_ADMISSIBLE_RETURN_DATA_CONSUMED",
        "marginal_portfolio_contribution": "NOT_ESTIMATED",
        "marginal_portfolio_contribution_reason": "NO_ADMISSIBLE_RETURN_DATA_CONSUMED",
        "statistical_correlation_matrix": "UNAVAILABLE_BY_DESIGN",
        "covariance_matrix": "UNAVAILABLE_BY_DESIGN",
        "marginal_alpha_estimate": "NOT_ESTIMATED",
        "return_series_consumed": False,
        "capital_allocation_authorized": False,
        "position_sizing_authorized": False,
        "orders_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
        "portfolio_optimization_authorized": False,
        "economic_experiment_authorized": False,
        "prospective_observation_authorized": False,
        "claim": "Structural economic-identity diagnostics only; no empirical portfolio value is estimated.",
        "future_question": "Does this edge add economically distinct value?",
    }


def _verify_documentary_identity(identity: Dict[str, Any]) -> None:
    if identity.get("evidence_class") == "DOCUMENTARY" or "documentary_basis" in identity:
        from .final_shape import economic_identity_v1

        basis = identity.get("documentary_basis")
        if not isinstance(basis, dict) or basis.get("synthetic_only") is not False:
            raise ValueError("documentary identity lacks its producer basis")
        replay_candidate = deepcopy(identity)
        memory_refs = replay_candidate.pop("memory_refs", None)
        if memory_refs is not None:
            _validated_memory_refs(memory_refs)
        if replay_candidate != economic_identity_v1(basis, {}):
            raise ValueError("documentary identity differs from reconstructed dossier support")
