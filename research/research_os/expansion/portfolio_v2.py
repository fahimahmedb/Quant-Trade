from __future__ import annotations

from itertools import combinations
from typing import Any, Dict, Iterable, List


def _eq_known(left: Any, right: Any) -> float:
    if left in (None, "UNKNOWN") or right in (None, "UNKNOWN"):
        return 0.0
    return 1.0 if left == right else 0.0


def _jaccard(left: Iterable[str], right: Iterable[str]) -> float:
    a, b = set(left or []), set(right or [])
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def structural_pair(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    tag_overlap = _jaccard(left.get("economic_tags", []), right.get("economic_tags", []))
    dimensions = {
        "payer": _eq_known(left.get("payer"), right.get("payer")),
        "asset": _eq_known(left.get("asset"), right.get("asset")),
        "horizon": _eq_known(left.get("horizon"), right.get("horizon")),
        "liquidity": _eq_known(left.get("liquidity"), right.get("liquidity")),
        "tail_exposure": _eq_known(left.get("tail_exposure"), right.get("tail_exposure")),
        "economic_tags": round(tag_overlap, 4),
    }
    weights = {
        "payer": 0.25,
        "asset": 0.15,
        "horizon": 0.10,
        "liquidity": 0.10,
        "tail_exposure": 0.15,
        "economic_tags": 0.25,
    }
    score = round(sum(dimensions[key] * weights[key] for key in dimensions), 4)
    return {
        "left": left["hypothesis_id"],
        "right": right["hypothesis_id"],
        "structural_overlap_score": score,
        "dimensions": dimensions,
        "classification": (
            "HIGH_STRUCTURAL_OVERLAP"
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
    pairwise: List[Dict[str, Any]] = [structural_pair(a, b) for a, b in combinations(items, 2)]
    novelty: Dict[str, float] = {}
    for item in items:
        overlaps = [
            pair["structural_overlap_score"]
            for pair in pairwise
            if item["hypothesis_id"] in {pair["left"], pair["right"]}
        ]
        novelty[item["hypothesis_id"]] = round(1.0 - max(overlaps, default=0.0), 4)

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
