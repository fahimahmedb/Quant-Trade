"""Compliance gate for VET: prohibited practices are refused by construction.

Quant's objective is long-run real wealth; gains from manipulation, privileged
information or venue-rule circumvention are neither repeatable nor keepable
(confiscation, bans, prosecution) and would poison the evidence base. A lane
declares what it does in ``compliance`` (copied into the strategy's evidence
at registration); VET refuses any strategy that declares a prohibited practice
or a cross-venue hedge whose settlement rules were not matched clause by clause.
"""

from __future__ import annotations

from typing import Any

#: Practices that are illegal or break venue terms (see research/structural_edges_2026-09-25).
PROHIBITED = frozenset({
    "self_trading", "wash_trading", "reward_farming_with_self_fills", "spoofing",
    "layering", "marking_the_close", "oracle_or_resolution_influence",
    "insider_information", "event_participant", "front_running_client_orders",
    "multi_accounting", "geo_restriction_circumvention", "smart_contract_exploit",
    "user_harming_mev", "sybil_farming", "bonus_abuse",
})


#: Practices a lane may declare. Anything else (including a misspelling of a
#: prohibited tag) is refused rather than silently passed.
KNOWN_PRACTICES = frozenset({
    "public_market_data", "exchange_execution", "passive_liquidity_provision",
    "cross_venue_hedge", "event_study", "calendar_flow", "sharp_reference_pricing",
})


def assess(evidence: dict[str, Any]) -> dict[str, Any]:
    declared = (evidence or {}).get("compliance") or {}
    tags = {str(tag) for tag in declared.get("practices", [])}
    normalised = {tag.lower().replace("-", "_").replace(" ", "_") for tag in tags}
    reasons = [f"declares prohibited practice: {tag}" for tag in sorted(normalised & PROHIBITED)]
    unknown = sorted(tag for tag in tags if tag not in KNOWN_PRACTICES
                     and tag.lower().replace("-", "_").replace(" ", "_") not in PROHIBITED)
    reasons += [f"undeclared practice vocabulary: {tag}" for tag in unknown]
    if declared.get("cross_venue_hedge") and not (declared.get("settlement_rules_matched")
                                                  and declared.get("settlement_evidence")):
        reasons.append("cross-venue hedge without an evidenced clause-by-clause "
                       "settlement-rule match")
    return {"approved": not reasons, "reasons": reasons, "declared": declared}


def internal_crosses(fills_by_strategy: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Opposite fills on one symbol in one session from different sleeves.

    On a real venue these two orders could match each other (a self-trade); a
    live executor must net them into one portfolio order first.
    """
    sides: dict[tuple[str, str], dict[str, float]] = {}
    for strategy, fills in fills_by_strategy.items():
        for fill in fills:
            key = (fill["symbol"], fill["execution_date"])
            sides.setdefault(key, {})[strategy] = sides.get(key, {}).get(strategy, 0.0) + fill["quantity"]
    crosses = []
    for (symbol, day), by_strategy in sorted(sides.items()):
        if any(q > 0 for q in by_strategy.values()) and any(q < 0 for q in by_strategy.values()):
            crosses.append({"symbol": symbol, "execution_date": day, "sleeves": by_strategy})
    return crosses
