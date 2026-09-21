"""The anti-double-counting map between ``K_forward`` and ``M_economic``.

``ONE_RISK_CLASS_ONE_PRIMARY_ECONOMIC_HOME``: every named uncertainty or risk
class has exactly one primary home. Charging the same risk as an expected cost
*and* as a margin makes the threshold wrong in a direction that flatters nothing
and nobody — it simply rejects viable deployment on double protection — and the
friction partition section 7 gives it a state:

    FRICTION_MARGIN_DOUBLE_COUNT -> INVALID_MEUE_RECIPE

A deliberate split of one risk across both objects is allowed, but only with a
documented non-overlap decomposition, so the exception cannot be taken silently.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from .fingerprint import recipe_hash
from .states import (ECONOMIC_HOMES, FRICTION_MARGIN_DOUBLE_COUNT, HOME_K_FORWARD,
                     HOME_M_ECONOMIC)


#: Risk classes that may never enter market/deployment MEUE at all
#: (``PROGRAM_COST_DOES_NOT_ENTER_MARKET_DEPLOYMENT_MEUE``).
EXCLUDED_RISK_CLASSES = {
    "PROGRAM_TCO": "PROGRAM_COST_DOES_NOT_ENTER_MARKET_DEPLOYMENT_MEUE",
    "BUILDER_COST": "PROGRAM_COST_DOES_NOT_ENTER_MARKET_DEPLOYMENT_MEUE",
    "RESEARCH_SUNK_COST": "PROGRAM_COST_DOES_NOT_ENTER_MARKET_DEPLOYMENT_MEUE",
    "RESEARCH_OPPORTUNITY_COST": "PROGRAM_COST_DOES_NOT_ENTER_MARKET_DEPLOYMENT_MEUE",
    "STATISTICAL_STANDARD_ERROR": "MARGIN_IS_NOT_STATISTICAL_UNCERTAINTY",
    "ALPHA_LEVEL": "MARGIN_IS_NOT_STATISTICAL_UNCERTAINTY",
    "MINIMUM_DETECTABLE_EFFECT": "MARGIN_IS_NOT_STATISTICAL_UNCERTAINTY",
}


@dataclass(frozen=True)
class RiskClaim:
    """One named risk class claimed by one economic object."""

    risk_class: str
    home: str
    description: str = ""
    #: Required only when the same class is deliberately claimed by both homes.
    non_overlap_proof: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RiskPartition:
    claims: tuple[RiskClaim, ...]

    def violations(self) -> list[str]:
        problems: list[str] = []
        by_class: dict[str, list[RiskClaim]] = {}
        for claim in self.claims:
            if claim.home not in ECONOMIC_HOMES:
                problems.append(f"{claim.risk_class}: ECONOMIC_HOME_NOT_RECOGNISED")
            if claim.risk_class in EXCLUDED_RISK_CLASSES:
                problems.append(f"{claim.risk_class}: "
                                f"{EXCLUDED_RISK_CLASSES[claim.risk_class]}")
            if not claim.description:
                problems.append(f"{claim.risk_class}: RISK_CLASS_DESCRIPTION_UNDECLARED")
            by_class.setdefault(claim.risk_class, []).append(claim)
        for risk_class, claims in sorted(by_class.items()):
            homes = {claim.home for claim in claims}
            if len(claims) > 1 and len(homes) == 1:
                problems.append(f"{risk_class}: DUPLICATE_CLAIM_IN_SAME_HOME")
            if homes == {HOME_K_FORWARD, HOME_M_ECONOMIC}:
                proofs = [claim.non_overlap_proof for claim in claims]
                if not all(proofs):
                    problems.append(f"{FRICTION_MARGIN_DOUBLE_COUNT}:{risk_class}")
        return problems

    def home_of(self, risk_class: str) -> tuple[str, ...]:
        return tuple(sorted({claim.home for claim in self.claims
                             if claim.risk_class == risk_class}))

    def rule_document(self) -> dict[str, Any]:
        return {"claims": sorted((claim.to_dict() for claim in self.claims),
                                 key=lambda row: (row["risk_class"], row["home"]))}

    def fingerprint(self) -> str:
        return recipe_hash(self.rule_document())


def partition_from(claims: Iterable[RiskClaim]) -> RiskPartition:
    return RiskPartition(tuple(claims))
