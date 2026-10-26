from __future__ import annotations

from itertools import combinations
from typing import Any, Dict, Iterable, List


def _jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)


def economic_identity(engine_output: Dict[str, Any]) -> Dict[str, Any]:
    c = engine_output["candidate"]
    tags = set(c["economic_tags"])
    payer = "UNKNOWN"
    if "forced_flow" in tags:
        payer = "FORCED_REBALANCER"
    elif "earnings_revision" in tags or "information_processing" in tags:
        payer = "SLOW_INFORMATION_PROCESSOR"
    elif "reversal" in tags:
        payer = "TEMPORARY_LIQUIDITY_DEMAND"
    elif "valuation" in tags:
        payer = "CONSENSUS_MISPRICING"
    return {
        "hypothesis_id": c["hypothesis_id"],
        "mechanism": c["mechanism"],
        "payer": payer,
        "asset_class": "SYNTHETIC_EQUITY",
        "horizon": c["horizon"],
        "factors": sorted(tags),
        "capacity": "LOW_OR_UNKNOWN" if "low_capacity" in tags else "UNKNOWN",
        "liquidity_exposure": "HIGH" if "liquidity" in tags else "UNKNOWN",
        "crowding": "UNKNOWN",
        "tail_exposure": "UNKNOWN",
        "capital_authority": "NOT_AUTHORIZED",
    }


def build_portfolio_map(identities: List[Dict[str, Any]]) -> Dict[str, Any]:
    pairwise = []
    for left, right in combinations(identities, 2):
        overlap = round(_jaccard(left["factors"], right["factors"]), 4)
        if overlap >= 0.67:
            classification = "HIGH_OVERLAP"
        elif overlap >= 0.34:
            classification = "PARTIAL_OVERLAP"
        else:
            classification = "DIVERSIFYING_ON_TAGS"
        pairwise.append({
            "left": left["hypothesis_id"],
            "right": right["hypothesis_id"],
            "factor_overlap": overlap,
            "classification": classification,
        })
    return {
        "portfolio_engine": "portfolio-map.v0",
        "capital_allocation_authorized": False,
        "identities": identities,
        "pairwise": pairwise,
        "marginal_portfolio_value": "NOT_ESTIMATED_WITHOUT_EMPIRICAL_RETURN_DATA",
    }
