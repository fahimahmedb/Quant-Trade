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


def assess(evidence: dict[str, Any]) -> dict[str, Any]:
    declared = (evidence or {}).get("compliance") or {}
    tags = set(declared.get("practices", []))
    problems = sorted(tags & PROHIBITED)
    reasons = [f"declares prohibited practice: {tag}" for tag in problems]
    if declared.get("cross_venue_hedge") and not declared.get("settlement_rules_matched"):
        reasons.append("cross-venue hedge without a clause-by-clause settlement-rule match")
    return {"approved": not reasons, "reasons": reasons, "declared": declared}
