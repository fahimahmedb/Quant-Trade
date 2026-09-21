"""The deployment scenario ``theta`` and the one-way causal order around it.

``D09_ROUTE_B_COST_PARAMETER_SOURCE_AND_JOINT_SCENARIO_CONTRACT_2026-09-17.md``
section 5 fixes the direction:

    theta -> G, A_claim^G, C, execution policy, permitted liquidity state
          -> participation(theta) -> K_forward -> M_economic -> MEUE

and section 6 forbids the loop ``choose C -> compute MEUE -> change C because the
threshold is inconvenient -> recompute``, even when every iteration is
outcome-blind.

A direction cannot be enforced by intention, so this module seals ``theta``
before the economic evaluation runs and refuses a second evaluation in the same
session on a different capital point unless a multi-scenario authority was
declared in advance.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .fingerprint import recipe_hash
from .states import THETA_UNRESOLVED


#: Where the expected deployed exposure ``Q(theta)`` came from. EC1 section 7 is
#: explicit that Q must reflect the frozen allocation/overlap/saturation
#: semantics and is never a naive ``C * event_count`` annualisation.
Q_PROVENANCE_ALLOCATION_CONSTRUCTOR = "FROZEN_ALLOCATION_CONSTRUCTOR"
Q_PROVENANCE_NAIVE_ANNUALISATION = "NAIVE_CAPITAL_TIMES_EVENT_COUNT"
Q_PROVENANCE_UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class ThetaState:
    """One admissible deployment scenario.

    Nothing here is a Form 4 outcome. ``expected_deployed_exposure`` is an
    ex-ante property of the allocation policy, not a realised deployment.
    """

    theta_id: str
    #: Authorized capital point inside ``C_claim(G*)``, in account currency.
    capital: float
    #: Identifier of the authorized D07 geometry ``G``.
    geometry_id: str
    #: Identifier of the frozen ``A_CONSTRUCTOR`` instance.
    allocation_constructor_id: str
    #: Identifier of the permitted pre-outcome allocation state.
    allocation_state_id: str
    #: Execution policy identifier (entry regime, exit convention).
    execution_policy_id: str
    #: ``Q(theta) = E[sum_j a_j(theta)]``, total expected deployed exposure in
    #: account currency over the authority-bearing evaluation regime.
    expected_deployed_exposure: float
    q_provenance: str = Q_PROVENANCE_UNAVAILABLE
    #: Permitted liquidity reference state, e.g. reference ADV per name.
    liquidity_reference: float | None = None
    #: Participation implied by the policy at this capital and liquidity.
    participation: float | None = None
    #: The evaluation regime Q is expressed over, e.g. "ONE_CALENDAR_YEAR".
    evaluation_regime: str = "UNDECLARED"

    def violations(self) -> list[str]:
        problems: list[str] = []
        if self.capital <= 0:
            problems.append("CAPITAL_MUST_BE_POSITIVE")
        if self.expected_deployed_exposure < 0:
            problems.append("EXPECTED_DEPLOYED_EXPOSURE_NEGATIVE")
        if self.q_provenance == Q_PROVENANCE_NAIVE_ANNUALISATION:
            problems.append("Q_IS_NEVER_NAIVE_CAPITAL_TIMES_EVENT_COUNT")
        if self.q_provenance == Q_PROVENANCE_UNAVAILABLE:
            problems.append("Q_PROVENANCE_UNAVAILABLE")
        if self.evaluation_regime == "UNDECLARED":
            problems.append("EVALUATION_REGIME_UNDECLARED")
        return problems

    @property
    def resolved(self) -> bool:
        return not self.violations()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def fingerprint(self) -> str:
        return recipe_hash(self.to_dict())


@dataclass(frozen=True)
class ThetaSelectionRule:
    """Frozen rule that determines which ``theta`` may be evaluated.

    Freezing this before any MEUE number exists is what
    ``THETA_SELECTION_RULE_PRECEDES_MEUE_RESULT`` asks for.
    """

    rule_id: str
    #: Upstream objects allowed to determine theta (D02/D03/D07/A_CONSTRUCTOR...).
    upstream_authorities: tuple[str, ...]
    #: How the capital point/domain is chosen inside ``C_claim(G*)``.
    capital_selection_rule: str
    #: Which liquidity/reference inputs may be consumed.
    liquidity_inputs: tuple[str, ...]
    #: Failure state when no authorized theta can be instantiated.
    failure_state: str = THETA_UNRESOLVED
    #: Predeclared economic scenarios, when more than one theta is evaluated.
    declared_scenarios: tuple[str, ...] = ()
    #: Multiplicity semantics required when more than one scenario is declared.
    multiplicity_semantics: str | None = None

    def violations(self) -> list[str]:
        problems: list[str] = []
        if not self.upstream_authorities:
            problems.append("UPSTREAM_AUTHORITIES_UNDECLARED")
        if not self.capital_selection_rule:
            problems.append("CAPITAL_SELECTION_RULE_UNDECLARED")
        if len(self.declared_scenarios) > 1 and not self.multiplicity_semantics:
            problems.append("MULTIPLE_SCENARIOS_WITHOUT_MULTIPLICITY_SEMANTICS")
        if self.failure_state != THETA_UNRESOLVED:
            problems.append("THETA_FAILURE_STATE_NOT_RECOGNISED")
        return problems

    def admits(self, theta: ThetaState) -> bool:
        if not self.declared_scenarios:
            return True
        return theta.theta_id in self.declared_scenarios

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def fingerprint(self) -> str:
        return recipe_hash(self.to_dict())


class ThetaFeedbackViolation(RuntimeError):
    """``theta`` moved after an economic threshold had been computed."""


@dataclass
class EvaluationSession:
    """One economic evaluation, sealed against threshold shopping.

    The session records every ``theta`` it evaluated. A second theta is allowed
    only when the frozen selection rule declared it in advance; otherwise the
    session raises, because the only reason to try another capital point after
    seeing a threshold is to make the threshold attainable.
    """

    session_id: str
    rule: ThetaSelectionRule
    evaluated: list[str] = field(default_factory=list)
    thresholds_observed: int = 0

    def admit(self, theta: ThetaState) -> ThetaState:
        if not self.rule.admits(theta):
            raise ThetaFeedbackViolation(
                f"{theta.theta_id} is not a predeclared scenario of {self.rule.rule_id}")
        fingerprint = theta.fingerprint()
        if fingerprint in self.evaluated:
            return theta
        if self.thresholds_observed and not self.rule.declared_scenarios:
            raise ThetaFeedbackViolation(
                "NO_SIZE_SEARCH_TO_MAKE_MEUE_ATTAINABLE: a new theta was admitted after a "
                f"threshold was produced in session {self.session_id}")
        if (self.evaluated and self.thresholds_observed
                and len(self.evaluated) >= len(self.rule.declared_scenarios)):
            raise ThetaFeedbackViolation(
                "MEUE_DOES_NOT_FEED_BACK_TO_THETA_SAME_EVALUATION: session "
                f"{self.session_id} exhausted its predeclared scenarios")
        self.evaluated.append(fingerprint)
        return theta

    def record_threshold(self) -> None:
        self.thresholds_observed += 1

    def to_dict(self) -> dict[str, Any]:
        return {"session_id": self.session_id, "rule_id": self.rule.rule_id,
                "rule_hash": self.rule.fingerprint(),
                "theta_fingerprints": list(self.evaluated),
                "thresholds_observed": self.thresholds_observed}
