from __future__ import annotations

from itertools import combinations
from typing import Any, Dict, Iterable, List
from research.research_os.scientific_store import sha256_json


def _eq_known(left: Any, right: Any) -> Any:
    if left in (None, "", "UNKNOWN", "UNQUALIFIED", "NOT_QUALIFIED") or right in (None, "", "UNKNOWN", "UNQUALIFIED", "NOT_QUALIFIED"):
        return None
    return 1.0 if left == right else 0.0


def _jaccard(left: Iterable[str], right: Iterable[str]) -> float:
    a, b = set(left or []), set(right or [])
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def structural_pair(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    _verify_documentary_identity(left)
    _verify_documentary_identity(right)
    tag_overlap = _jaccard(left.get("economic_tags", []), right.get("economic_tags", []))
    dimensions = {
        "mechanism": _eq_known(left.get("mechanism"), right.get("mechanism")),
        "payer": _eq_known(left.get("payer"), right.get("payer")),
        "asset": _eq_known(left.get("asset"), right.get("asset")),
        "horizon": _eq_known(left.get("horizon"), right.get("horizon")),
        "liquidity": _eq_known(left.get("liquidity"), right.get("liquidity")),
        "tail_exposure": _eq_known(left.get("tail_exposure"), right.get("tail_exposure")),
        "economic_tags": round(tag_overlap, 4) if left.get('economic_tags') and right.get('economic_tags') else None,
    }
    weights = {
        "mechanism": 0.15,
        "payer": 0.20,
        "asset": 0.15,
        "horizon": 0.10,
        "liquidity": 0.05,
        "tail_exposure": 0.10,
        "economic_tags": 0.25,
    }
    unknown = sorted(key for key, value in dimensions.items() if value is None)
    score = round(sum((dimensions[key] or 0) * weights[key] for key in dimensions), 4)
    return {
        "left": left["hypothesis_id"],
        "right": right["hypothesis_id"],
        "structural_overlap_score": score,
        "dimensions": dimensions,
        "unknown_dimensions": unknown,
        "score_status": "PARTIAL" if unknown else "COMPLETE",
        "overlap_score_interval": [score, round(score + sum(weights[k] for k in unknown), 4)],
        "identity_hashes": [sha256_json(left), sha256_json(right)],
        "dossier_hashes": [item.get('identity_provenance', {}).get('dossier_hash') for item in (left, right)],
        "classification": (
            "INSUFFICIENT_EVIDENCE" if unknown else "HIGH_STRUCTURAL_OVERLAP"
            if score >= 0.65
            else "PARTIAL_STRUCTURAL_OVERLAP"
            if score >= 0.30
            else "STRUCTURALLY_DISTINCT_OR_UNKNOWN"
        ),
        "statistical_correlation": "UNAVAILABLE_BY_DESIGN",
        "return_series_consumed": False,
    }


def portfolio_diagnostics_v2(identities: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    items = list(identities)
    for item in items:
        _verify_documentary_identity(item)
    keys = [item['hypothesis_id'] for item in items]
    if len(set(keys)) != len(keys):
        raise ValueError("portfolio requires one selected generation per hypothesis")
    pairwise: List[Dict[str, Any]] = [structural_pair(a, b) for a, b in combinations(items, 2)]
    novelty: Dict[str, Any] = {}
    for item in items:
        overlaps = [
            pair["structural_overlap_score"]
            for pair in pairwise
            if item["hypothesis_id"] in {pair["left"], pair["right"]}
        ]
        related = [p for p in pairwise if item['hypothesis_id'] in {p['left'], p['right']}]
        novelty[item["hypothesis_id"]] = (
            round(1.0 - max(overlaps), 4) if related and all(p['score_status'] == 'COMPLETE' for p in related)
            else "UNKNOWN"
        )

    return {
        "portfolio_engine": "portfolio-diagnostics.v2",
        "candidate_count": len(items),
        "pairwise": pairwise,
        "structural_novelty": novelty,
        "statistical_correlation_matrix": "UNAVAILABLE_BY_DESIGN",
        "covariance_matrix": "UNAVAILABLE_BY_DESIGN",
        "marginal_alpha_estimate": "NOT_ESTIMATED",
        "return_series_consumed": False,
        "capital_allocation_authorized": False,
        "position_sizing_authorized": False,
        "orders_authorized": False,
        "claim": "Structural diversification diagnostics only; not an empirical portfolio optimizer.",
    }


def _verify_documentary_identity(identity: Dict[str, Any]) -> None:
    if identity.get('evidence_class') == 'DOCUMENTARY' or 'documentary_basis' in identity:
        from .final_shape import economic_identity_v1
        basis = identity.get('documentary_basis')
        if not isinstance(basis, dict) or basis.get('synthetic_only') is not False:
            raise ValueError('documentary identity lacks its producer basis')
        if identity != economic_identity_v1(basis, {}):
            raise ValueError('documentary identity differs from reconstructed dossier support')
