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


# --- post-size / pre-fill check (M3) ----------------------------------------
#
# The pre-size check above binds Research's declared participation envelope to
# the executable ExecutionModel. It says nothing about what a *particular*
# sized order will actually do once FINAL_SIZE, rounding and ADV-based
# capacity transforms are applied to it. This second, mandatory check derives
# the *actual* implied participation from the final sized notional and the
# ADV/capacity input authorized for this fill, and re-runs the same cost
# envelope against it. A violation here fails closed before
# ``ExecutionModel.fill`` is ever called — no Book-feeding fill call is
# permitted past this point once it has failed.

ADV_AVAILABLE = "AVAILABLE"
ADV_STALE = "STALE"
ADV_MISSING = "MISSING"
ADV_INVALID = "INVALID"
ADV_STATES = (ADV_AVAILABLE, ADV_STALE, ADV_MISSING, ADV_INVALID)


@dataclass(frozen=True)
class AdvReference:
    """One symbol's authorized ADV/capacity input for the post-size check.

    Missing, stale or invalid ADV must fail closed rather than be treated as
    unlimited capacity or silently skipped — the same rule
    ``economics.capacity`` already applies to the SIZE-time liquidity
    schedule. This is the same discipline applied a second time, downstream,
    at the exact notional that will actually be sent to
    ``ExecutionModel.fill``.
    """

    symbol: str
    value: float
    state: str
    as_of: str | None = None
    #: How many sessions old the reference is, when known.
    staleness_sessions: int | None = None
    max_staleness_sessions: int | None = None

    def violations(self) -> list[str]:
        problems: list[str] = []
        if self.state not in ADV_STATES:
            problems.append(f"{self.symbol}: ADV_STATE_NOT_RECOGNISED")
            return problems
        if self.state != ADV_AVAILABLE:
            problems.append(f"{self.symbol}: ADV_{self.state}")
            return problems
        if self.value <= 0:
            problems.append(f"{self.symbol}: ADV_NONPOSITIVE_DESPITE_AVAILABLE_STATE")
        if (self.max_staleness_sessions is not None and self.staleness_sessions is not None
                and self.staleness_sessions > self.max_staleness_sessions):
            problems.append(f"{self.symbol}: ADV_STALE_BEYOND_MAX_STALENESS")
        return problems

    @property
    def valid(self) -> bool:
        return not self.violations()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PostSizeParticipationConsistency:
    """§2.6 second (post-size/pre-fill) execution-cost consistency check."""

    research_one_way_cost_bps: float
    model: ExecutionCostModel
    #: The final sized notional this specific order is about to request,
    #: already reflecting rounding/minimum-order transforms if any were
    #: applied before this check runs.
    final_notional: float
    adv: AdvReference
    subject: str = ""

    @property
    def adv_valid(self) -> bool:
        return self.adv.valid

    @property
    def implied_participation(self) -> float:
        """Actual participation the final sized order implies.

        An unusable ADV reference cannot certify *any* participation as safe,
        so it reports ``inf`` rather than ``0`` — the fail-closed direction —
        and :meth:`violations` reports the ADV defect directly rather than
        relying on the participation ceiling comparison to catch it.
        """
        if not self.adv_valid or self.adv.value <= 0:
            return float("inf")
        return abs(self.final_notional) / self.adv.value

    @property
    def ceiling(self) -> float:
        return implied_participation_ceiling(self.research_one_way_cost_bps, self.model)

    def violations(self) -> list[str]:
        label = self.subject or "POST_SIZE_EVIDENCE"
        problems = list(self.adv.violations())
        if not self.adv_valid:
            problems.append(
                f"{label}: EXECUTION_COST_CONSISTENCY_EXCEEDED_AFTER_SIZING_ADV_UNUSABLE")
            return problems
        if self.implied_participation > self.ceiling + 1e-15:
            problems.append(f"{label}: EXECUTION_COST_CONSISTENCY_EXCEEDED_AFTER_SIZING")
        if self.implied_participation > self.model.max_participation + 1e-15:
            problems.append(
                f"{label}: EXECUTION_COST_CONSISTENCY_PARTICIPATION_EXCEEDS_MODEL_MAX")
        return problems

    @property
    def consistent(self) -> bool:
        return not self.violations()

    def to_dict(self) -> dict[str, Any]:
        return {"subject": self.subject,
                "research_one_way_cost_bps": self.research_one_way_cost_bps,
                "final_notional": self.final_notional,
                "adv": self.adv.to_dict(),
                "implied_participation": self.implied_participation,
                "implied_participation_ceiling": self.ceiling,
                "execution_model": self.model.to_dict(),
                "violations": self.violations()}


def verify_post_size_participation_consistency(
        research_one_way_cost_bps: float, model: ExecutionCostModel,
        final_notional: float, adv: AdvReference,
        subject: str = "") -> PostSizeParticipationConsistency:
    return PostSizeParticipationConsistency(research_one_way_cost_bps, model, final_notional,
                                            adv, subject)
