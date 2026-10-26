from __future__ import annotations

from copy import deepcopy
from itertools import combinations
from math import isfinite
from typing import Any, Dict, Iterable, List, Tuple

from research.research_os.scientific_store import sha256_json
from .v2_core import SEMANTIC_NULLS


_UNKNOWN = SEMANTIC_NULLS | {"", "UNQUALIFIED", "NOT_QUALIFIED", "UNAVAILABLE"}

# Structural weights are diagnostics only. They are deliberately not statistical
# correlations and never consume returns. The three core economic-identity axes
# (payer, mechanism, clock) are sufficient to force a same-exposure review when
# all three are known and equal.
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


def _is_known(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().upper() not in _UNKNOWN
    if isinstance(value, bool):
        return False
    if isinstance(value, float):
        return isfinite(value)
    if isinstance(value, dict):
        return any(_is_known(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_is_known(item) for item in value)
    return value is not None


def _stable_value(value: Any) -> Any:
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, list):
        return sorted(value) if all(isinstance(v, str) for v in value) else value
    return value


def _eq_known(left: Any, right: Any) -> Any:
    left = _stable_value(left)
    right = _stable_value(right)
    if not _is_known(left) or not _is_known(right):
        return None
    return 1.0 if left == right else 0.0


def _jaccard(left: Iterable[str], right: Iterable[str]) -> Any:
    a = {value for value in left or [] if _is_known(value)}
    b = {value for value in right or [] if _is_known(value)}
    if not a or not b:
        return None
    return round(len(a & b) / len(a | b), 4)


def _candidate_from_identity(identity: Dict[str, Any]) -> Dict[str, Any]:
    basis = identity.get("documentary_basis")
    if isinstance(basis, dict) and isinstance(basis.get("candidate"), dict):
        return basis["candidate"]
    return {}


def _first_known(*choices: Tuple[Any, str]) -> Tuple[Any, str]:
    for value, path in choices:
        if _is_known(value):
            return deepcopy(_stable_value(value)), path
    return "UNKNOWN", "UNKNOWN"


def structural_identity(identity: Dict[str, Any]) -> Dict[str, Any]:
    """Project an identity into economic structure without inventing evidence.

    Every field carries a trace back to the hypothesis/generation and, when
    available, the candidate/source/dossier hashes that support the identity.
    Missing support remains UNKNOWN. This function is read-only with respect to
    the producer identity and candidate.
    """
    _verify_documentary_identity(identity)
    declaration = identity.get("frozen_declaration")
    if declaration is not None:
        from .final_shape import _frozen_identity_declaration
        envelope = declaration["envelope"]
        frozen_candidate = envelope["protocol_payload"]["candidate"]
        if (declaration != _frozen_identity_declaration({"candidate": frozen_candidate}, envelope)
                or any(identity.get(key) != frozen_candidate.get(key)
                       for key in ("hypothesis_id", "generation_id", "mechanism"))):
            raise ValueError("FROZEN_IDENTITY_DECLARATION_BINDING_MISMATCH")
    candidate = _candidate_from_identity(identity)
    provenance = identity.get("identity_provenance", {})
    if not isinstance(provenance, dict):
        provenance = {}

    candidate_hash = provenance.get("candidate_hash")
    if declaration is not None:
        if _is_known(candidate_hash) and candidate_hash != declaration["candidate_hash"]:
            raise ValueError("FROZEN_IDENTITY_CANDIDATE_BINDING_MISMATCH")
        candidate_hash = declaration["candidate_hash"]
    if not _is_known(candidate_hash) and candidate:
        candidate_hash = sha256_json(candidate)
    if not _is_known(candidate_hash):
        candidate_hash = "UNKNOWN"

    source_hash = provenance.get("source_hash", "UNKNOWN")
    dossier_hash = provenance.get("dossier_hash", "UNKNOWN")
    source_refs = provenance.get("source_refs", [])

    field_choices = {
        "payer": (
            (identity.get("payer"), "identity.payer"),
            (candidate.get("payer"), "candidate.payer"),
        ),
        "forced_constrained_actor": (
            (identity.get("forced_constrained_actor"), "identity.forced_constrained_actor"),
            (identity.get("forced_actor"), "identity.forced_actor"),
            (identity.get("constrained_actor"), "identity.constrained_actor"),
            (candidate.get("forced_constrained_actor"), "candidate.forced_constrained_actor"),
            (candidate.get("forced_actor"), "candidate.forced_actor"),
            (candidate.get("constrained_actor"), "candidate.constrained_actor"),
        ),
        "mechanism": (
            (identity.get("mechanism"), "identity.mechanism"),
            (candidate.get("mechanism"), "candidate.mechanism"),
        ),
        "instrument": (
            (identity.get("instrument"), "identity.instrument"),
            (candidate.get("instrument"), "candidate.instrument"),
            (identity.get("asset"), "identity.asset"),
        ),
        "universe": (
            (identity.get("universe"), "identity.universe"),
            (candidate.get("universe"), "candidate.universe"),
        ),
        "timing_clock": (
            (identity.get("timing_clock"), "identity.timing_clock"),
            (identity.get("clock"), "identity.clock"),
            (candidate.get("timing_clock"), "candidate.timing_clock"),
            (candidate.get("clock"), "candidate.clock"),
        ),
        "horizon": (
            (identity.get("horizon"), "identity.horizon"),
            (candidate.get("horizon"), "candidate.horizon"),
        ),
        "capacity_bottleneck": (
            (identity.get("capacity_bottleneck"), "identity.capacity_bottleneck"),
            (candidate.get("capacity_bottleneck"), "candidate.capacity_bottleneck"),
            (identity.get("capacity"), "identity.capacity"),
        ),
        "cost_structure": (
            (identity.get("cost_structure"), "identity.cost_structure"),
            (candidate.get("cost_structure"), "candidate.cost_structure"),
        ),
        "economic_exposure": (
            (identity.get("economic_exposure"), "identity.economic_exposure"),
            (candidate.get("economic_exposure"), "candidate.economic_exposure"),
            (identity.get("economic_tags"), "identity.economic_tags"),
        ),
        "event_rule_dependency": (
            (identity.get("event_rule_dependency"), "identity.event_rule_dependency"),
            (candidate.get("event_rule_dependency"), "candidate.event_rule_dependency"),
        ),
        "source_identity": (
            (identity.get("source_identity"), "identity.source_identity"),
            (source_hash, "identity_provenance.source_hash"),
        ),
    }

    documentary = identity.get("evidence_class") == "DOCUMENTARY"
    if documentary:
        # These native identity fields intentionally retain UNKNOWN when their
        # economic meaning is not supported. Issuer facts, thesis tags and a
        # proposed candidate horizon cannot qualify different structural fields.
        for name in ("instrument", "horizon", "economic_exposure"):
            field_choices[name] = ((identity.get(name), "identity." + name),)

    declared_fields = {"instrument": "instrument", "universe": "universe",
                       "timing_clock": "entry_clock", "horizon": "horizon"} if declaration is not None else {}
    if declaration is not None:
        expression = envelope["protocol_payload"]["dataset_provenance"]["protocol"]["economic_expression"]
        for name, key in declared_fields.items():
            field_choices[name] = ((expression.get(key), "frozen_protocol.economic_expression." + key),)

    fields: Dict[str, Any] = {}
    unknown_fields: List[str] = []
    for name, choices in field_choices.items():
        value, path = _first_known(*choices)
        if not _is_known(value):
            unknown_fields.append(name)
        fields[name] = {
            "value": value,
            "status": "KNOWN" if _is_known(value) else "UNKNOWN",
            "provenance": {
                "hypothesis_id": identity.get("hypothesis_id", "UNKNOWN"),
                "generation_id": identity.get("generation_id", "UNKNOWN"),
                "candidate_hash": candidate_hash,
                "source_hash": source_hash if _is_known(source_hash) else "UNKNOWN",
                "dossier_hash": dossier_hash if _is_known(dossier_hash) else "UNKNOWN",
                "identity_hash": sha256_json(identity),
                "source_path": path,
                "source_refs": deepcopy(source_refs) if isinstance(source_refs, list) else [],
            },
        }
        if documentary:
            support_name = {"instrument": "asset", "economic_exposure": "economic_tags",
                            "capacity_bottleneck": "capacity"}.get(name, name)
            record = deepcopy(provenance.get("field_support", {}).get(
                support_name, {"status": "UNKNOWN", "support": None}))
            declared_value = identity.get(support_name, "UNKNOWN")
            if name == "source_identity":
                support_name, declared_value = "identity_provenance.source_hash", source_hash
                record = {"status": "CONTENT_IDENTITY_ONLY", "support": {"source_hash": source_hash}}
            fields[name]["documentary_evidence"] = dict(
                record, identity_field=support_name, declared_value=deepcopy(declared_value))
        if declaration is not None:
            fields[name]["provenance"]["protocol_hash"] = envelope["protocol_hash"]
        if name in declared_fields:
            fields[name]["status"] = "DECLARED" if _is_known(value) else "UNKNOWN"
            fields[name]["declaration_evidence"] = {
                "status": "DECLARED_ONLY" if _is_known(value) else "UNKNOWN",
                "protocol_hash": envelope["protocol_hash"], "candidate_hash": candidate_hash,
                "source_path": path, "source_factual_qualification": False,
            }

    return {
        "hypothesis_id": identity.get("hypothesis_id", "UNKNOWN"),
        "generation_id": identity.get("generation_id", "UNKNOWN"),
        "fields": fields,
        "unknown_fields": sorted(unknown_fields),
        "identity_hash": sha256_json(identity),
        "candidate_immutable": True,
        "empirical_return_data_consumed": False,
    }


def structural_pair(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    _verify_documentary_identity(left)
    _verify_documentary_identity(right)
    left_struct = structural_identity(left)
    right_struct = structural_identity(right)

    structural_dimensions = {
        key: _eq_known(
            left_struct["fields"][key]["value"],
            right_struct["fields"][key]["value"],
        )
        for key in _STRUCTURAL_WEIGHTS
    }
    # Preserve the pre-existing v2 diagnostic keys for downstream consumers while
    # moving economic identity decisions to the richer structural field set.
    legacy_dimensions = {
        "asset": _eq_known(left.get("asset"), right.get("asset")),
        "liquidity": _eq_known(left.get("liquidity"), right.get("liquidity")),
        "tail_exposure": _eq_known(left.get("tail_exposure"), right.get("tail_exposure")),
        "economic_tags": _jaccard(left.get("economic_tags", []), right.get("economic_tags", [])),
    }
    dimensions = {**structural_dimensions, **legacy_dimensions}
    unknown = sorted(key for key, value in dimensions.items() if value is None)
    structural_unknown = [key for key, value in structural_dimensions.items() if value is None]
    score = round(
        sum((structural_dimensions[key] or 0.0) * _STRUCTURAL_WEIGHTS[key] for key in structural_dimensions),
        4,
    )
    max_score = round(score + sum(_STRUCTURAL_WEIGHTS[key] for key in structural_unknown), 4)

    core = ("payer", "mechanism", "timing_clock")
    core_known = all(structural_dimensions[key] is not None for key in core)
    core_same = core_known and all(structural_dimensions[key] == 1.0 for key in core)
    payer_and_mechanism_different = (
        structural_dimensions["payer"] == 0.0 and structural_dimensions["mechanism"] == 0.0
    )

    if core_same:
        classification = "HIGH_STRUCTURAL_OVERLAP_REVIEW"
        review_required = True
    elif payer_and_mechanism_different:
        classification = "STRUCTURALLY_DISTINGUISHABLE"
        review_required = False
    elif not core_known:
        classification = "UNKNOWN"
        review_required = False
    elif score >= 0.50:
        classification = "HIGH_STRUCTURAL_OVERLAP_REVIEW"
        review_required = True
    elif score >= 0.25:
        classification = "PARTIAL_STRUCTURAL_OVERLAP"
        review_required = False
    else:
        classification = "STRUCTURALLY_DISTINGUISHABLE"
        review_required = False

    return {
        "left": left["hypothesis_id"],
        "right": right["hypothesis_id"],
        "structural_overlap_score": score,
        "dimensions": dimensions,
        "unknown_dimensions": unknown,
        "score_status": "PARTIAL" if structural_unknown else "COMPLETE",
        "overlap_score_interval": [score, max_score],
        "identity_hashes": [sha256_json(left), sha256_json(right)],
        "candidate_hashes": [
            left_struct["fields"]["mechanism"]["provenance"]["candidate_hash"],
            right_struct["fields"]["mechanism"]["provenance"]["candidate_hash"],
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
        "review_basis": list(core) if core_same else [],
        "empirical_correlation": "UNAVAILABLE",
        "empirical_correlation_reason": "NO_ADMISSIBLE_RETURN_DATA_CONSUMED",
        # Compatibility with the previous v2 output. This remains explicitly
        # non-empirical and must never be interpreted as a numeric correlation.
        "statistical_correlation": "UNAVAILABLE_BY_DESIGN",
        "return_series_consumed": False,
        "structural_identity": {"left": left_struct, "right": right_struct},
    }


def _portfolio_pair(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """Preserve the canonical v2 summary while retaining B4's richer analysis.

    Existing portfolio consumers use the seven-axis summary contract. New
    economic-identity consumers use structural_pair or economic_structure.
    Neither interpretation is an empirical correlation.
    """
    pair = structural_pair(left, right)
    pair["economic_structure"] = {key: deepcopy(pair[key]) for key in (
        "classification", "structural_overlap_score", "dimensions", "unknown_dimensions",
        "score_status", "overlap_score_interval",
    )}
    weights = {"mechanism": .15, "payer": .20, "asset": .15, "horizon": .10,
               "liquidity": .05, "tail_exposure": .10, "economic_tags": .25}
    dimensions = {key: (_jaccard(left.get(key, []), right.get(key, [])) if key == "economic_tags"
                        else _eq_known(left.get(key), right.get(key))) for key in weights}
    unknown = sorted(key for key, value in dimensions.items() if value is None)
    score = round(sum((dimensions[key] or 0) * weights[key] for key in dimensions), 4)
    pair.update(
        dimensions=dimensions, unknown_dimensions=unknown, structural_overlap_score=score,
        score_status="PARTIAL" if unknown else "COMPLETE",
        overlap_score_interval=[score, round(score + sum(weights[k] for k in unknown), 4)],
        classification=("INSUFFICIENT_EVIDENCE" if unknown else "HIGH_STRUCTURAL_OVERLAP"
                        if score >= .65 else "PARTIAL_STRUCTURAL_OVERLAP" if score >= .30
                        else "STRUCTURALLY_DISTINCT_OR_UNKNOWN"),
    )
    return pair


def portfolio_diagnostics_v2(identities: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    items = list(identities)
    for item in items:
        _verify_documentary_identity(item)
    keys = [item["hypothesis_id"] for item in items]
    if len(set(keys)) != len(keys):
        raise ValueError("portfolio requires one selected generation per hypothesis")

    pairwise: List[Dict[str, Any]] = [_portfolio_pair(a, b) for a, b in combinations(items, 2)]
    novelty: Dict[str, Any] = {}
    for item in items:
        related = [p for p in pairwise if item["hypothesis_id"] in {p["left"], p["right"]}]
        if not related or any(p["economic_structure"]["classification"] == "UNKNOWN" for p in related):
            novelty[item["hypothesis_id"]] = "UNKNOWN"
        elif all(p["economic_structure"]["score_status"] == "COMPLETE" for p in related):
            novelty[item["hypothesis_id"]] = round(
                1.0 - max(p["economic_structure"]["structural_overlap_score"] for p in related), 4
            )
        else:
            novelty[item["hypothesis_id"]] = "UNKNOWN"

    return {
        "portfolio_engine": "portfolio-diagnostics.v2",
        "candidate_count": len(items),
        "structural_identities": [structural_identity(item) for item in items],
        "pairwise": pairwise,
        "same_exposure_review_pairs": [
            {"left": p["left"], "right": p["right"], "basis": p["review_basis"]}
            for p in pairwise
            if p["same_exposure_review_required"]
        ],
        "structural_novelty": novelty,
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
        "claim": "Structural economic-identity diagnostics only; no empirical portfolio value is estimated.",
        "future_question": "Does this edge add economically distinct value?",
    }


def _verify_documentary_identity(identity: Dict[str, Any]) -> None:
    if identity.get("evidence_class") == "DOCUMENTARY" or "documentary_basis" in identity:
        from .final_shape import economic_identity_v1

        basis = identity.get("documentary_basis")
        if not isinstance(basis, dict) or basis.get("synthetic_only") is not False:
            raise ValueError("documentary identity lacks its producer basis")
        declaration = identity.get("frozen_declaration")
        envelope = declaration["envelope"] if declaration is not None else None
        if identity != economic_identity_v1(basis, {}, frozen_envelope=envelope):
            raise ValueError("documentary identity differs from reconstructed dossier support")
