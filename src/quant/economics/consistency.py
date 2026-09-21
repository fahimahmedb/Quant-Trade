"""Research evidence must describe the executable strategy, not a cheaper one.

``QUANT_NORTH_STAR.md`` and the project's integrity invariants require research
evidence to describe the executable paper/shadow strategy rather than a more
favourable backtest object.  The Research Factory charges a flat one-way cost per
unit of turnover; the Capital Desk charges commission plus half-spread plus a
participation-dependent impact.  Those two numbers are only consistent below a
participation rate, and above it the research object is strictly cheaper than the
strategy the desk would actually run.

This module computes that boundary instead of asserting the relationship holds:

    implied participation ceiling p* solves
        commission + half_spread + impact_at_reference * sqrt(p*/max_participation)
        = research_one_way_cost

Above ``p*``, a lane validated on the research cost assumption is not evidence
about the executable path, and :func:`verify_research_cost_consistency` says so.

Defect this closes: ECON-001. ``src/quant/desk/execution.py`` states that the
desk model "is calibrated to land at or under" ``RESEARCH_ONE_WAY_COST_BPS``.
With the shipped coefficients that holds only below roughly 0.61% of ADV, while
the desk's own ``max_participation`` is 5%. The two constants also live in
separate modules with no code path linking them, so nothing was checking the
claim. The guard here does not silently rewrite either constant: which one moves
is a research-protocol decision, because lowering the desk's participation and
raising the research cost assumption have different consequences for already
recorded lane evidence.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ExecutionCostModel:
    """The desk's one-way cost structure, read from the model rather than copied.

    Fields mirror :class:`quant.desk.execution.ExecutionModel`. Kept as a
    separate value object so the economic engine never has to import, and
    therefore never risks mutating, desk execution state.
    """

    commission_bps: float
    half_spread_bps: float
    impact_bps_at_full_participation: float
    max_participation: float

    @classmethod
    def from_execution_model(cls, model: Any) -> "ExecutionCostModel":
        return cls(commission_bps=float(model.commission_bps),
                   half_spread_bps=float(model.half_spread_bps),
                   impact_bps_at_full_participation=float(
                       model.impact_bps_at_full_participation),
                   max_participation=float(model.max_participation))

    def impact_bps(self, participation: float) -> float:
        if participation <= 0 or self.max_participation <= 0:
            return 0.0
        shape = math.sqrt(min(participation, 1.0) / self.max_participation)
        return self.impact_bps_at_full_participation * shape

    def one_way_cost_bps(self, participation: float) -> float:
        """Commission plus half-spread plus impact at this participation."""
        return self.commission_bps + self.half_spread_bps + self.impact_bps(participation)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def implied_participation_ceiling(research_one_way_cost_bps: float,
                                  model: ExecutionCostModel) -> float:
    """Largest participation at which research cost still covers modelled cost.

    Returns ``0.0`` when the fixed part of the desk's cost already exceeds the
    research assumption: then no positive participation is consistent, and the
    research object is cheaper than execution at any size.
    """
    fixed = model.commission_bps + model.half_spread_bps
    headroom = research_one_way_cost_bps - fixed
    if headroom <= 0 or model.impact_bps_at_full_participation <= 0:
        return 0.0
    shape = headroom / model.impact_bps_at_full_participation
    return model.max_participation * shape * shape


@dataclass(frozen=True)
class ResearchExecutionConsistency:
    """Whether research cost evidence covers the participation actually used."""

    research_one_way_cost_bps: float
    model: ExecutionCostModel
    #: Participation the executable path is allowed to reach.
    participation_used: float
    #: Identifier of the lane or strategy whose evidence this concerns.
    subject: str = ""

    @property
    def ceiling(self) -> float:
        return implied_participation_ceiling(self.research_one_way_cost_bps, self.model)

    @property
    def modelled_cost_bps(self) -> float:
        return self.model.one_way_cost_bps(self.participation_used)

    @property
    def understatement_bps(self) -> float:
        """How much cheaper the research object is, in bps of one-way notional."""
        return max(self.modelled_cost_bps - self.research_one_way_cost_bps, 0.0)

    def violations(self) -> list[str]:
        problems: list[str] = []
        label = self.subject or "RESEARCH_EVIDENCE"
        if self.participation_used > self.ceiling + 1e-15:
            problems.append(
                f"{label}: RESEARCH_EVIDENCE_ONLY_VALID_BELOW_IMPLIED_PARTICIPATION_CEILING")
        if self.understatement_bps > 0:
            problems.append(f"{label}: RESEARCH_EVIDENCE_CHEAPER_THAN_EXECUTION")
        return problems

    @property
    def consistent(self) -> bool:
        return not self.violations()

    def to_dict(self) -> dict[str, Any]:
        return {"subject": self.subject,
                "research_one_way_cost_bps": self.research_one_way_cost_bps,
                "participation_used": self.participation_used,
                "implied_participation_ceiling": self.ceiling,
                "modelled_one_way_cost_bps": self.modelled_cost_bps,
                "understatement_bps": self.understatement_bps,
                "execution_model": self.model.to_dict(),
                "violations": self.violations()}


def verify_research_cost_consistency(research_one_way_cost_bps: float,
                                     model: ExecutionCostModel,
                                     participation_used: float,
                                     subject: str = "") -> ResearchExecutionConsistency:
    return ResearchExecutionConsistency(research_one_way_cost_bps, model,
                                        participation_used, subject)
