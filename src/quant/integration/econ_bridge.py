"""The Research -> Economic admission boundary, executable.

The chain, in order, with nothing skipped and nothing collapsed:

    ScientificEffectArtifact (scientific effect authority)
    -> forward evidence identity (scoped to exactly the evidence consumed)
    -> economic_gate(...)                       (scientific effect -> verdict)
    -> compute_input_fingerprint(...) -> AssessmentRecord
    -> EconomicAssessmentJournal.record(...)     (durable, idempotent, conflict-fails-closed)
    -> VALIDATED -> SHADOW  iff CONTINUE and capital-order-eligible; otherwise
       no promotion, no fill, no Book mutation, and the exact refusal reason
       is durably recorded.

This module is the only place allowed to transition a strategy
``VALIDATED -> SHADOW``. It does not construct a second scheduler, sizing
authority, execution authority or ticket family, and it does not touch
Desk/Risk/Execution/Book/Learning state beyond that one lifecycle read+write
on ``quant.factory.strategies.StrategyRegistry``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..economics.capacity import CapacityOutcome
from ..economics.consistency import ResearchExecutionConsistency
from ..economics.decision import EconomicVerdict, PortfolioInteraction, economic_gate
from ..economics.journal import (AssessmentRecord, EconomicAssessmentJournal,
                                 compute_input_fingerprint)
from ..economics.recipe import MEUEResult
from ..economics.states import (CONTINUE, KILL, NO_TRADE,
                                ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE)
from ..economics.theta import ThetaState
from ..factory.strategies import StrategyRegistry
from ..learning.durable import DurableOutcomeStore
from ..learning.durable import ECONOMIC_ASSESSMENT as LEARNING_ECONOMIC_ASSESSMENT
from ..learning.durable import INSUFFICIENT as LEARNING_INSUFFICIENT
from ..learning.durable import KILL as LEARNING_KILL
from ..learning.durable import NO_TRADE as LEARNING_NO_TRADE
from ..science.effect import (STRUCTURAL_INSUFFICIENT, ForwardConfirmationReceipt,
                              ScientificEffectArtifact)
from . import forward_adapter

ADMITTED = "ADMITTED"
REFUSED = "REFUSED"


@dataclass(frozen=True)
class AdmissionOutcome:
    """The boundary's result for one strategy, complete enough to audit."""

    status: str
    reason: str
    assessment_id: str
    strategy_id: str
    ticket_id: str
    promoted_to_shadow: bool
    verdict: EconomicVerdict | None = None
    capital_order_eligibility: str = ""

    def to_dict(self) -> dict[str, Any]:
        document = {
            "status": self.status, "reason": self.reason, "assessment_id": self.assessment_id,
            "strategy_id": self.strategy_id, "ticket_id": self.ticket_id,
            "promoted_to_shadow": self.promoted_to_shadow,
            "capital_order_eligibility": self.capital_order_eligibility,
        }
        if self.verdict is not None:
            document["verdict"] = self.verdict.to_dict()
        return document


def _record_admission_outcome(learning: DurableOutcomeStore | None, *, assessment_id: str,
                              strategy_id: str, ticket_id: str, kind: str,
                              status: str, reason: str,
                              reason_codes: tuple[str, ...]) -> None:
    """Durably record exactly one Learning outcome for one admission call.

    ``processed_id`` is the assessment/refusal identity the boundary already
    computed (``assessment_id``, for a resolved evaluation, or the refusal
    identity seed for one that never resolved) -- the same identity
    ``journal.record`` just durably accepted or NOOP'd, so a replay of the
    same evidence lands an identical Learning NOOP rather than a duplicate.
    A no-op when ``learning`` is not supplied.
    """
    if learning is None:
        return
    payload = {
        "assessment_id": assessment_id, "strategy_id": strategy_id, "ticket_id": ticket_id,
        "status": status, "reason": reason, "reason_codes": list(reason_codes),
    }
    learning.record(assessment_id, kind, payload)


def assess_and_admit(
    *, journal: EconomicAssessmentJournal, strategies: StrategyRegistry, ticket_id: str,
    strategy_id: str, effect_artifact: ScientificEffectArtifact | None,
    meue_result: MEUEResult, theta: ThetaState, interaction: PortfolioInteraction,
    capacity: CapacityOutcome | None = None,
    consistency: ResearchExecutionConsistency | None = None,
    forward_receipt: ForwardConfirmationReceipt | None = None, code_sha: str = "",
    learning: DurableOutcomeStore | None = None,
) -> AdmissionOutcome:
    """Run the boundary once for one strategy and record the outcome durably.

    Idempotent: calling this again with the same ``effect_artifact``/
    ``meue_result``/``theta``/``interaction``/``capacity``/``consistency`` for
    the same strategy replays the same durable record and performs no second
    lifecycle mutation (the strategy is already ``SHADOW`` or beyond, so the
    lifecycle transition is skipped rather than reattempted).

    Fails closed: if the same assessment identity is presented with different
    inputs, ``journal.record`` raises
    ``quant.economics.journal.AssessmentConflict`` before any lifecycle
    mutation happens, and that exception propagates rather than being
    swallowed or silently overwriting the prior durable decision.
    """
    identity = forward_adapter.derive_forward_evidence_identity(
        artifact=effect_artifact, ticket_id=ticket_id, strategy_id=strategy_id,
        forward_receipt=forward_receipt)

    if identity is None:
        reason = forward_adapter.classify_effect_refusal(effect_artifact)
        assessment_id = forward_adapter.refusal_identity_seed(ticket_id, strategy_id,
                                                               effect_artifact)
        reason_codes = (reason,) + (tuple(effect_artifact.reason_codes)
                                    if effect_artifact is not None else ())
        record = AssessmentRecord(
            assessment_id=assessment_id, input_fingerprint=assessment_id,
            decision="ADMISSION_REFUSED", capital_order_eligibility="",
            reason_codes=reason_codes, code_sha=code_sha, strategy_id=strategy_id)
        journal.record(record)  # AssessmentConflict propagates: fail closed.
        # The upstream science outcome -- STRUCTURAL_INSUFFICIENT
        # ("INSUFFICIENT_CLUSTER_INFORMATION" in ``quant.science.effect``) --
        # is recorded distinctly (LEARNING_INSUFFICIENT) rather than folded
        # into the generic refusal kind: it is a different failure mode
        # (evidence never existed) from a resolvable coordinate mismatch or
        # an as-yet-unresolved coordinate.
        kind = (LEARNING_INSUFFICIENT if STRUCTURAL_INSUFFICIENT in reason_codes
               else LEARNING_ECONOMIC_ASSESSMENT)
        _record_admission_outcome(learning, assessment_id=assessment_id, strategy_id=strategy_id,
                                  ticket_id=ticket_id, kind=kind, status=REFUSED, reason=reason,
                                  reason_codes=reason_codes)
        return AdmissionOutcome(status=REFUSED, reason=reason, assessment_id=assessment_id,
                                strategy_id=strategy_id, ticket_id=ticket_id,
                                promoted_to_shadow=False)

    assessment_id = forward_adapter.assessment_id_for(identity)
    verdict = economic_gate(effect_artifact.effect_estimate, meue_result, theta, interaction,
                            capacity=capacity, consistency=consistency)
    fingerprint = compute_input_fingerprint(effect_artifact.effect_estimate, meue_result, theta,
                                            interaction, capacity=capacity,
                                            consistency=consistency)
    record = AssessmentRecord.from_verdict(
        assessment_id, fingerprint, verdict, meue_result,
        effect_version=effect_artifact.sample_id, protocol_hash=effect_artifact.protocol_hash,
        code_sha=code_sha, strategy_id=strategy_id)
    journal.record(record)  # AssessmentConflict propagates: fail closed.

    eligible = (verdict.verdict == CONTINUE
               and verdict.capital_order_eligibility
               == ORDER_ELIGIBILITY_PORTFOLIO_CONSIDERATION_ELIGIBLE)
    promoted = False
    if eligible:
        definition = strategies.get(strategy_id)
        if definition is not None and definition.lifecycle == "VALIDATED":
            definition.transition(
                "SHADOW", f"Economic admission {assessment_id}: CONTINUE, "
                          "capital-order-eligible")
            strategies.upsert(definition)
            promoted = True

    if verdict.verdict == KILL:
        outcome_kind = LEARNING_KILL
    elif verdict.verdict == NO_TRADE:
        outcome_kind = LEARNING_NO_TRADE
    else:
        # CONTINUE, whether or not it cleared capital-order eligibility: a
        # development-signal-only CONTINUE is still a distinct, durable
        # economic-assessment fact, never silently indistinguishable from a
        # NO_TRADE.
        outcome_kind = LEARNING_ECONOMIC_ASSESSMENT
    _record_admission_outcome(
        learning, assessment_id=assessment_id, strategy_id=strategy_id, ticket_id=ticket_id,
        kind=outcome_kind, status=ADMITTED if eligible else REFUSED, reason=verdict.reason,
        reason_codes=(verdict.verdict, verdict.capital_order_eligibility))

    return AdmissionOutcome(
        status=ADMITTED if eligible else REFUSED, reason=verdict.reason,
        assessment_id=assessment_id, strategy_id=strategy_id, ticket_id=ticket_id,
        promoted_to_shadow=promoted, verdict=verdict,
        capital_order_eligibility=verdict.capital_order_eligibility)
