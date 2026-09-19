"""The economic gate: scientific effect in, ``CONTINUE`` / ``NO_TRADE`` / ``KILL`` out.

The chain this implements, in order, with nothing skipped:

    scientific effect -> expected gross economic effect -> executable exposure
    -> frictions -> capacity -> uncertainty -> sizing -> portfolio interaction
    -> net expected value -> continue / no-trade / kill

``NO_TRADE`` is a first-class result, not a failure of the gate. And a lane can
die on economics alone: if the whole plausible effect range sits below the
economic threshold, the verdict is ``KILL`` regardless of how small the p-value
is. A statistically real effect that cannot pay for its own frictions is not an
edge, and the gate says so rather than passing the decision upward with a
favourable-sounding significance number attached.

Nothing here authorises real capital. Every verdict carries
``PAPER_SHADOW_ONLY``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .capacity import CapacityOutcome, NEW_POLICY_VERSION
from .coordinate import ALLOCATION_WEIGHTED_RATIO
from .recipe import MEUEResult
from .states import CONTINUE, KILL, NO_TRADE, RECIPE_CONSUMABLE, RECIPE_PROVISIONAL
from .theta import ThetaState


#: Nothing in this package can authorise real capital.
PAPER_SHADOW_ONLY = "PAPER_SHADOW_ONLY"

#: Evidence labels. Historical research is development evidence; it is never
#: independent confirmation, however good the numbers look.
EVIDENCE_EXPLORATION = "EXPLORATION"
EVIDENCE_TRAINING = "TRAINING"
EVIDENCE_DEVELOPMENT = "DEVELOPMENT"
EVIDENCE_FORWARD_CONFIRMATION = "FORWARD_CONFIRMATION"

DEVELOPMENT_LABELS = (EVIDENCE_EXPLORATION, EVIDENCE_TRAINING, EVIDENCE_DEVELOPMENT)
EVIDENCE_LABELS = DEVELOPMENT_LABELS + (EVIDENCE_FORWARD_CONFIRMATION,)

#: What authority a verdict carries. Development evidence can justify continuing
#: to build; it cannot justify claiming a confirmed edge.
AUTHORITY_DEVELOPMENT_ONLY = "DEVELOPMENT_EVIDENCE_ONLY"
AUTHORITY_FORWARD_CONFIRMED = "FORWARD_CONFIRMED_SUBJECT_TO_PROTOCOL"


@dataclass(frozen=True)
class EffectEstimate:
    """An estimate of the frozen effect coordinate ``delta``, with its label."""

    #: Point estimate of ``delta``, on the frozen coordinate.
    delta_hat: float
    #: Interval on ``delta`` at ``confidence_level``. Both bounds required: a
    #: point estimate with no interval cannot be compared to a threshold.
    lower: float
    upper: float
    confidence_level: float
    evidence_label: str
    #: Which dataset/epoch produced it, for the causal timeline.
    sample_provenance: str
    #: The aggregation actually computed. Must be the frozen one.
    estimator_form: str = ALLOCATION_WEIGHTED_RATIO
    #: Number of contributing events. Not a substitute for the interval.
    event_count: int | None = None
    p_value: float | None = None

    def violations(self) -> list[str]:
        problems: list[str] = []
        if self.evidence_label not in EVIDENCE_LABELS:
            problems.append("EVIDENCE_LABEL_NOT_RECOGNISED")
        if self.estimator_form != ALLOCATION_WEIGHTED_RATIO:
            problems.append("ESTIMATOR_NOT_ON_FROZEN_EFFECT_COORDINATE")
        if not self.lower <= self.delta_hat <= self.upper:
            problems.append("POINT_ESTIMATE_OUTSIDE_ITS_OWN_INTERVAL")
        if not 0 < self.confidence_level < 1:
            problems.append("CONFIDENCE_LEVEL_OUT_OF_RANGE")
        if not self.sample_provenance:
            problems.append("SAMPLE_PROVENANCE_UNDECLARED")
        return problems

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PortfolioInteraction:
    """What the rest of the Book does to this lane's incremental value.

    A standalone expected value is the wrong number whenever the lane overlaps
    exposure the Book already carries: the capital is contended, the risk is
    correlated, and the marginal contribution is smaller than the standalone one.
    ``residual_beta`` must be declared even when it is zero, because an
    undeclared market exposure is exactly how an index return gets reported as
    an edge.
    """

    #: Share of this lane's exposure already carried by other sleeves, in [0, 1].
    overlap_fraction: float
    #: Residual market beta of the lane's exposure after the SPY-excess
    #: construction. ``None`` means nobody measured it.
    residual_beta: float | None
    #: Correlation of the lane's P&L to the existing Book, in [-1, 1].
    correlation_to_book: float | None = None
    #: Capital this lane must take from other sleeves, in account currency.
    capital_contention: float = 0.0
    notes: str = ""

    def violations(self) -> list[str]:
        problems: list[str] = []
        if not 0.0 <= self.overlap_fraction <= 1.0:
            problems.append("OVERLAP_FRACTION_OUT_OF_RANGE")
        if self.residual_beta is None:
            problems.append("RESIDUAL_BETA_UNDECLARED_HIDDEN_MARKET_EXPOSURE")
        if self.correlation_to_book is not None and not -1.0 <= self.correlation_to_book <= 1.0:
            problems.append("CORRELATION_OUT_OF_RANGE")
        if self.capital_contention < 0:
            problems.append("CAPITAL_CONTENTION_NEGATIVE")
        return problems

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EconomicVerdict:
    """The gate's output, with every step of the chain recorded."""

    verdict: str
    reason: str
    #: Threshold the effect had to clear.
    meue: float | None
    #: Effect after portfolio overlap, on the frozen coordinate.
    delta_incremental: float | None
    lower_incremental: float | None
    upper_incremental: float | None
    #: ``Q * delta_incremental - K_forward`` at the central scenario, in currency.
    net_expected_value: float | None
    margin_of_safety: float | None
    authority: str
    capital_authority: str = PAPER_SHADOW_ONLY
    chain: tuple[dict[str, Any], ...] = ()
    violations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        document = asdict(self)
        document["chain"] = [dict(step) for step in self.chain]
        document["violations"] = list(self.violations)
        return document


def _step(name: str, **detail: Any) -> dict[str, Any]:
    return {"step": name, **detail}


def economic_gate(estimate: EffectEstimate, meue_result: MEUEResult, theta: ThetaState,
                  interaction: PortfolioInteraction,
                  capacity: CapacityOutcome | None = None) -> EconomicVerdict:
    """Run the chain once and return one verdict.

    Every blocking condition returns ``NO_TRADE`` rather than raising: a decision
    system that crashes instead of recording a refusal loses the refusal, and
    ``OPERATING_MODEL.md`` needs the refusals to learn from false rejects.
    """
    chain: list[dict[str, Any]] = []
    problems = list(estimate.violations()) + list(interaction.violations())
    problems.extend(theta.violations())
    chain.append(_step("SCIENTIFIC_EFFECT", delta_hat=estimate.delta_hat,
                       interval=[estimate.lower, estimate.upper],
                       evidence_label=estimate.evidence_label,
                       provenance=estimate.sample_provenance))

    authority = (AUTHORITY_FORWARD_CONFIRMED
                 if estimate.evidence_label == EVIDENCE_FORWARD_CONFIRMATION
                 else AUTHORITY_DEVELOPMENT_ONLY)

    if meue_result.recipe_state not in (RECIPE_CONSUMABLE, RECIPE_PROVISIONAL) \
            or meue_result.meue is None:
        problems.extend(meue_result.violations)
        chain.append(_step("ECONOMIC_THRESHOLD", state=meue_result.recipe_state))
        return EconomicVerdict(NO_TRADE, "ECONOMIC_RECIPE_NOT_EVALUABLE", None, None, None,
                              None, None, None, authority, chain=tuple(chain),
                              violations=tuple(sorted(set(problems))))

    meue = meue_result.meue
    chain.append(_step("ECONOMIC_THRESHOLD", meue=meue,
                       beee=meue_result.beee.value if meue_result.beee else None,
                       m_economic=meue_result.margin.value if meue_result.margin else None,
                       recipe_state=meue_result.recipe_state,
                       recipe_hash=meue_result.recipe_hash))

    q = theta.expected_deployed_exposure
    chain.append(_step("EXECUTABLE_EXPOSURE", q=q, q_provenance=theta.q_provenance,
                       capital=theta.capital))
    if q <= 0:
        return EconomicVerdict(NO_TRADE, "NO_DEPLOYABLE_EXPOSURE", meue, None, None, None,
                               None, None, authority, chain=tuple(chain),
                               violations=tuple(sorted(set(problems))))

    if capacity is not None:
        chain.append(_step("CAPACITY", **capacity.to_dict()))
        problems.extend(capacity.violations)
        if capacity.policy_consequence == NEW_POLICY_VERSION:
            return EconomicVerdict(
                NO_TRADE, NEW_POLICY_VERSION, meue, None, None, None, None, None,
                authority, chain=tuple(chain), violations=tuple(sorted(set(problems))))

    scale = 1.0 - interaction.overlap_fraction
    delta_incremental = estimate.delta_hat * scale
    lower_incremental = estimate.lower * scale
    upper_incremental = estimate.upper * scale
    chain.append(_step("PORTFOLIO_INTERACTION", overlap_fraction=interaction.overlap_fraction,
                       residual_beta=interaction.residual_beta,
                       correlation_to_book=interaction.correlation_to_book,
                       delta_incremental=delta_incremental))

    gross = q * delta_incremental
    cost = None
    if meue_result.beee is not None and meue_result.beee.value is not None:
        # At BEEE the frozen Phi is zero, so K_forward(BEEE) = Q * BEEE. That is
        # the expected forward cost on the same coordinate, without re-running
        # the cost recipe outside its frozen inputs.
        cost = q * meue_result.beee.value
    net = gross - cost if cost is not None else None
    chain.append(_step("NET_EXPECTED_VALUE", gross_value=gross, expected_forward_cost=cost,
                       net_expected_value=net))

    margin_of_safety = delta_incremental - meue

    if problems:
        return EconomicVerdict(NO_TRADE, "BLOCKING_INPUT_DEFECT", meue, delta_incremental,
                               lower_incremental, upper_incremental, net, margin_of_safety,
                               authority, chain=tuple(chain),
                               violations=tuple(sorted(set(problems))))

    if upper_incremental < meue:
        # The entire plausible effect range is below the economic threshold. A
        # small p-value cannot rescue this: the lane is economically dominated.
        return EconomicVerdict(KILL, "ECONOMICALLY_DOMINATED_ACROSS_WHOLE_INTERVAL", meue,
                               delta_incremental, lower_incremental, upper_incremental, net,
                               margin_of_safety, authority, chain=tuple(chain))
    if lower_incremental > meue:
        return EconomicVerdict(CONTINUE, "EFFECT_INTERVAL_ABOVE_ECONOMIC_THRESHOLD", meue,
                               delta_incremental, lower_incremental, upper_incremental, net,
                               margin_of_safety, authority, chain=tuple(chain))
    return EconomicVerdict(NO_TRADE, "UNCERTAINTY_STRADDLES_ECONOMIC_THRESHOLD", meue,
                           delta_incremental, lower_incremental, upper_incremental, net,
                           margin_of_safety, authority, chain=tuple(chain))
