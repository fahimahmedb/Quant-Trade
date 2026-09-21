"""M3 — Economic SIZE -> independent RISK -> FILLS -> BOOK.

Frozen topology (``governance/BLUE_FIRST_VERTICAL_ONE_BIG_BUILD_FROZEN_SPEC_2026-09-21.md``
§4-5, restated in detail in
``governance/BLUE_ONE_BIG_BUILD_PRESTAGE_2026-09-21.md`` §2.3-2.6/§8 M3)::

    Economic-admitted SHADOW opportunity
    -> Economic SIZE            (economics.sizing.compute_final_size)
    -> pre-size cost check       (economics.consistency.verify_research_cost_consistency)
    -> independent Risk          (desk.risk.evaluate)
    -> post-size/pre-fill check  (economics.consistency.verify_post_size_participation_consistency)
    -> ExecutionModel.fill       (desk.execution.ExecutionModel, sole fill authority)
    -> Ledger.apply_fill         (book.ledger.Ledger, sole Book)
    -> post-fill Risk re-check   (desk.risk.verify_final)

M2 RECONCILIATION (post-landing)
=================================

M2 (``quant.integration.econ_bridge.assess_and_admit`` +
``quant.economics.journal``) has landed on this branch. Its durable output is
an ``economics.journal.AssessmentRecord``, and the record now carries both
``strategy_id`` and ``margin_of_safety`` (added specifically so M3 SIZE never
has to invent a parallel numeric margin no one populates — see
``AssessmentRecord.margin_of_safety`` and
``EconomicAssessmentJournal.latest_for_strategy``).
:class:`LaneEconomicAdmission` is built from that real durable record via
:meth:`LaneEconomicAdmission.from_assessment_record` (``desk.desk.CapitalDesk``
is the caller); the functions below still never construct an admission
themselves and never call ``economic_gate``/the journal directly — that
boundary belongs to M2/desk.py, not here.

This module does not create a second Book, a second execution engine or a
second ticket family. It calls the existing, unmodified
``desk.risk.evaluate``/``verify_final``, ``desk.execution.ExecutionModel.fill``
and ``book.ledger.Ledger.apply_fill`` exactly as ``desk.desk.CapitalDesk``
already does, so splicing this into ``CapitalDesk._run_strategy`` in place of
its current naive ``capital = nav * capital_fraction * allocation`` SIZE line
is a small, local change once M2's admission object exists for real.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from ..book.ledger import Ledger
from ..economics.consistency import (AdvReference, ExecutionCostModel,
                                     PostSizeParticipationConsistency,
                                     ResearchExecutionConsistency,
                                     verify_post_size_participation_consistency,
                                     verify_research_cost_consistency)
from ..economics.sizing import LaneSizeResult, MarginSizingRule, compute_final_size
from ..dataplane.panel import PricePanel
from . import risk as risk_mod
from .execution import PHASE_ENTRY, PHASE_SCHEDULED_EXIT, ExecutionModel
from .risk import RiskLimits


#: Economic decisions from ``economics.decision.economic_gate`` (mirrored here
#: rather than imported, to keep this module importable without pulling in the
#: full economic-gate dependency chain for a simple string comparison).
DECISION_CONTINUE = "CONTINUE"
DECISION_NO_TRADE = "NO_TRADE"
DECISION_KILL = "KILL"

#: ``EconomicVerdict.capital_order_eligibility`` values that make a CONTINUE
#: more than a development signal. Mirrors ``economics.states``.
ELIGIBILITY_PORTFOLIO_CONSIDERATION = "PORTFOLIO_CONSIDERATION_ELIGIBLE"

MIN_ORDER_NOTIONAL = 500.0

#: Terminal M3 outcomes. Every one is a first-class durable result, never a
#: silent skip (frozen spec §5: "NO_TRADE, KILL, VETO and INSUFFICIENT are
#: first-class durable economic outcomes").
OUTCOME_NO_TRADE = "NO_TRADE"
OUTCOME_VETOED = "VETOED"
OUTCOME_BOOKED = "BOOKED"


@dataclass(frozen=True)
class LaneEconomicAdmission:
    """Exactly what M3 needs from a durable ``economics.journal.AssessmentRecord``.

    Fields map to ``AssessmentRecord`` 1:1 (``assessment_id``, ``decision``,
    ``capital_order_eligibility``, ``strategy_id``, ``margin_of_safety``,
    ``reason_codes``). ``margin_rule`` is the one field the record does not
    and should not carry: the margin-to-size mapping is a Desk/lifecycle
    sizing policy, not an economic verdict, so it is supplied by the caller
    (``desk.desk.CapitalDesk``) rather than persisted with the assessment.
    """

    assessment_id: str
    strategy_id: str
    decision: str
    capital_order_eligibility: str
    margin_of_safety: float
    margin_rule: MarginSizingRule
    reason_codes: tuple[str, ...] = ()

    @property
    def capital_order_eligible(self) -> bool:
        return (self.decision == DECISION_CONTINUE
                and self.capital_order_eligibility == ELIGIBILITY_PORTFOLIO_CONSIDERATION)

    def to_dict(self) -> dict[str, Any]:
        document = asdict(self)
        document["margin_rule"] = self.margin_rule.to_dict()
        return document

    @classmethod
    def from_assessment_record(cls, record: Mapping[str, Any],
                               margin_rule: MarginSizingRule) -> "LaneEconomicAdmission":
        """Build the admission M3 SIZE needs from a real, durable
        ``economics.journal.AssessmentRecord`` (as returned by
        ``EconomicAssessmentJournal.get``/``latest_for_strategy``, or
        ``AssessmentRecord.to_dict()`` directly).

        A record persisted before ``margin_of_safety`` existed on the schema
        carries ``None`` there; this is surfaced as ``0.0`` (the sizing
        rule's own floor: ``MarginSizingRule.fraction`` already returns zero
        at or below ``minimum_margin >= 0``), never fabricated as a positive
        margin.
        """
        margin = record.get("margin_of_safety")
        reason_codes = record.get("reason_codes") or ()
        return cls(
            assessment_id=str(record.get("assessment_id", "")),
            strategy_id=str(record.get("strategy_id", "")),
            decision=str(record.get("decision", "")),
            capital_order_eligibility=str(record.get("capital_order_eligibility", "")),
            margin_of_safety=float(margin) if margin is not None else 0.0,
            margin_rule=margin_rule, reason_codes=tuple(reason_codes))


@dataclass
class LaneDecisionCard:
    """Everything §9 of the prestage spec asks a Decision Card to preserve,
    scoped to what M3 alone produces (SIZE through BOOK). Reason codes
    accumulate across stages; the card is terminal once ``action`` is set.
    """

    opportunity_id: str
    strategy_id: str
    assessment_id: str
    economic_size: LaneSizeResult | None = None
    pre_size_cost_consistency: ResearchExecutionConsistency | None = None
    risk_verdict: dict[str, Any] | None = None
    post_size_cost_consistency: dict[str, PostSizeParticipationConsistency] = field(
        default_factory=dict)
    fills: list[dict[str, Any]] = field(default_factory=list)
    book_operation_ids: list[str] = field(default_factory=list)
    action: str | None = None
    reason_codes: tuple[str, ...] = ()

    def stop(self, action: str, *reasons: str) -> "LaneDecisionCard":
        self.action = action
        self.reason_codes = self.reason_codes + tuple(reasons)
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id, "strategy_id": self.strategy_id,
            "assessment_id": self.assessment_id,
            "economic_size": self.economic_size.to_dict() if self.economic_size else None,
            "pre_size_cost_consistency": (self.pre_size_cost_consistency.to_dict()
                                          if self.pre_size_cost_consistency else None),
            "risk_verdict": self.risk_verdict,
            "post_size_cost_consistency": {
                symbol: check.to_dict()
                for symbol, check in self.post_size_cost_consistency.items()},
            "fills": list(self.fills), "book_operation_ids": list(self.book_operation_ids),
            "action": self.action, "reason_codes": list(self.reason_codes)}


def _declared_participation_envelope(model: ExecutionModel) -> float:
    """The participation envelope Research/Economic evidence is checked
    against pre-size: the full width the desk model is authorized to use.
    """
    return model.max_participation


def pre_size_cost_check(admission: LaneEconomicAdmission, execution: ExecutionModel,
                        research_one_way_cost_bps: float) -> ResearchExecutionConsistency:
    """§2.6 first check, bound to the actual authoritative ExecutionModel."""
    model = ExecutionCostModel.from_execution_model(execution)
    return verify_research_cost_consistency(
        research_one_way_cost_bps, model, _declared_participation_envelope(execution),
        subject=admission.strategy_id)


def post_size_cost_check(strategy_id: str, symbol: str, final_notional: float,
                         execution: ExecutionModel, research_one_way_cost_bps: float,
                         adv: AdvReference) -> PostSizeParticipationConsistency:
    """§2.6 second check: actual implied participation from the final sized
    notional against the authorized ADV/capacity input for this fill.
    """
    model = ExecutionCostModel.from_execution_model(execution)
    return verify_post_size_participation_consistency(
        research_one_way_cost_bps, model, final_notional, adv, subject=f"{strategy_id}:{symbol}")


def run_lane_entry(
        *, panel: PricePanel, ledger: Ledger, admission: LaneEconomicAdmission,
        target_weights: Mapping[str, float], current_decision_nav: float,
        strategy_allocation: float, lifecycle_capital_fraction: float,
        execution: ExecutionModel, limits: RiskLimits,
        adv_by_symbol: Mapping[str, AdvReference], research_one_way_cost_bps: float,
        opportunity_id: str, signal_date: str, execution_date: str,
) -> LaneDecisionCard:
    """Run SIZE -> pre-size check -> RISK -> post-size check -> FILLS -> BOOK
    for one strategy's entry, once M2 has already produced ``admission``.

    Every early return is a first-class terminal outcome with zero Book
    mutation and a durable reason. Exactly one ``ExecutionModel.fill`` call
    and one ``Ledger.apply_fill`` call happen per symbol that actually trades,
    and never more than one of each.
    """
    card = LaneDecisionCard(opportunity_id, admission.strategy_id, admission.assessment_id)

    # Economic CONTINUE is necessary but never sufficient on its own; a
    # CONTINUE that is not capital-order-eligible (development signal only)
    # must never reach SHADOW capital deployment (mandatory acceptance case
    # #11 in the prestage spec). M2 owns the SHADOW promotion decision; M3
    # additionally refuses to size anything that is not eligible, as a second
    # independent gate rather than trusting the caller filtered already.
    if not admission.capital_order_eligible:
        return card.stop(OUTCOME_NO_TRADE, "ECONOMIC_ADMISSION_NOT_CAPITAL_ORDER_ELIGIBLE",
                         *admission.reason_codes)

    # --- SIZE ----------------------------------------------------------
    size = compute_final_size(
        admission.strategy_id, admission.margin_rule, admission.margin_of_safety,
        current_decision_nav, strategy_allocation, lifecycle_capital_fraction)
    card.economic_size = size
    if size.zero_size:
        return card.stop(OUTCOME_NO_TRADE, *size.reason_codes)

    # --- pre-size execution-cost consistency (§15A / §2.6 first check) -
    pre_check = pre_size_cost_check(admission, execution, research_one_way_cost_bps)
    card.pre_size_cost_consistency = pre_check
    if not pre_check.consistent:
        return card.stop(OUTCOME_NO_TRADE, *pre_check.violations())

    target_notional = {symbol: size.final_size_notional * weight
                       for symbol, weight in target_weights.items()}
    # Legs the sleeve holds but no longer wants are targeted at zero, exactly
    # as desk.CapitalDesk._run_strategy already does, so RISK sees the
    # portfolio the fills will actually produce.
    for symbol in ledger.sleeve_exposures_at(admission.strategy_id, {}):
        target_notional.setdefault(symbol, 0.0)

    # --- independent RISK (downstream veto/throttle; Economic CONTINUE is
    # not an approved order) ---------------------------------------------
    verdict = risk_mod.evaluate(ledger, admission.strategy_id, target_notional, limits)
    card.risk_verdict = verdict
    if not verdict["approved"]:
        return card.stop(OUTCOME_VETOED, "RISK_VETOED_AFTER_ECONOMIC_CONTINUE",
                         *verdict["vetoes"])

    approved = verdict["scaled_target"]

    # --- post-size / pre-fill execution-cost consistency (§15B), for every
    # symbol about to receive an order, before ANY ExecutionModel.fill call.
    # Risk can only throttle (scale <= 1) so it can only shrink participation
    # relative to the pre-size envelope; this re-check nonetheless runs on
    # the actual post-risk, post-size notional, never on the pre-risk one,
    # so a hypothetical future transform that increased participation would
    # still be caught here rather than upstream.
    fills: list[dict[str, Any]] = []
    for symbol, notional in sorted(approved.items()):
        if abs(notional) < MIN_ORDER_NOTIONAL:
            continue
        adv = adv_by_symbol.get(symbol)
        if adv is None:
            adv = AdvReference(symbol=symbol, value=0.0, state="MISSING")
        post_check = post_size_cost_check(
            admission.strategy_id, symbol, notional, execution, research_one_way_cost_bps, adv)
        card.post_size_cost_consistency[symbol] = post_check
        if not post_check.consistent:
            return card.stop(OUTCOME_NO_TRADE,
                             "EXECUTION_COST_CONSISTENCY_EXCEEDED_AFTER_SIZING",
                             *post_check.violations())

    # Second pass: only after every symbol's post-size check has passed does
    # any ExecutionModel.fill call happen. A partial-pass, partial-fill state
    # is exactly the "no ExecutionModel.fill call allowed after failure"
    # invariant the frozen spec requires, so all checks resolve before any
    # fill is placed.
    price_lookup: dict[str, float] = {}
    for symbol, notional in sorted(approved.items()):
        if abs(notional) < MIN_ORDER_NOTIONAL:
            continue
        if not panel.has(execution_date, symbol):
            continue
        price = panel.adjusted(execution_date, symbol, "open")
        if price <= 0:
            continue
        price_lookup[symbol] = price
        quantity = notional / price
        fill = execution.fill(panel, symbol, quantity, signal_date, execution_date,
                              phase=PHASE_ENTRY)
        if abs(fill["quantity"]) * fill["fill_price"] < MIN_ORDER_NOTIONAL:
            continue
        fills.append(fill)

    if not fills:
        return card.stop(OUTCOME_NO_TRADE, "NO_ORDER_CLEARED_MINIMUM_SIZE_AFTER_CHECKS")

    card.fills = fills
    for fill in fills:
        operation_id = f"{opportunity_id}:{fill['symbol']}:{PHASE_ENTRY}"
        ledger.apply_fill(fill["symbol"], fill["quantity"], fill["fill_price"],
                          fill["commission"], execution_date, admission.strategy_id,
                          operation_id=operation_id)
        card.book_operation_ids.append(operation_id)

    # --- post-fill RISK re-check on the exact executed portfolio -------
    final_prices = dict(price_lookup)
    final_prices.update({fill["symbol"]: fill["fill_price"] for fill in fills})
    quantities = {symbol: position.quantity
                 for symbol, position in ledger.sleeves.get(admission.strategy_id, {}).items()
                 if abs(position.quantity) > 1e-9}
    executed = {symbol: quantity * final_prices[symbol]
               for symbol, quantity in quantities.items()
               if abs(quantity) > 1e-9 and symbol in final_prices}
    commission = sum(fill["commission"] for fill in fills)
    final = risk_mod.verify_final(ledger, admission.strategy_id, executed, limits,
                                  final_prices, nav_adjustment=-commission)
    if not final["approved"]:
        # The fills already happened (Book-feeding fill/Book application is
        # the sole authoritative record); a post-fill breach is recorded as a
        # VETOED terminal outcome for Learning, exactly mirroring
        # ``desk.desk.CapitalDesk._run_strategy``'s existing post-fill check,
        # rather than attempting a nonexistent "unfill".
        return card.stop(OUTCOME_VETOED, "EXECUTED_PORTFOLIO_BREACHES_HARD_LIMIT",
                         *final["vetoes"])

    return card.stop(OUTCOME_BOOKED)


def run_lane_scheduled_exit(
        *, panel: PricePanel, ledger: Ledger, admission: LaneEconomicAdmission,
        execution: ExecutionModel, limits: RiskLimits,
        adv_by_symbol: Mapping[str, AdvReference], research_one_way_cost_bps: float,
        opportunity_id: str, signal_date: str, execution_date: str,
) -> LaneDecisionCard:
    """Close the strategy's whole sleeve at the frozen scheduled-exit session,
    through the same authoritative SIZE/RISK/FILLS/BOOK chain and the same
    ``ExecutionModel`` (``phase=SCHEDULED_EXIT``), never a second engine.

    Sizing has nothing left to decide for an exit (the target is flat, not an
    economic-margin-derived notional), so this path skips ``compute_final_size``
    but still runs both cost-consistency checks and independent Risk, because
    an exit order still consumes liquidity and still must clear the same
    executable-cost bar as an entry.
    """
    card = LaneDecisionCard(opportunity_id, admission.strategy_id, admission.assessment_id)
    held = ledger.sleeve_exposures(admission.strategy_id)
    if not held:
        return card.stop(OUTCOME_NO_TRADE, "SCHEDULED_EXIT_NO_OPEN_SLEEVE")

    target_notional = {symbol: 0.0 for symbol in held}

    pre_check = pre_size_cost_check(admission, execution, research_one_way_cost_bps)
    card.pre_size_cost_consistency = pre_check
    if not pre_check.consistent:
        return card.stop(OUTCOME_NO_TRADE, *pre_check.violations())

    verdict = risk_mod.evaluate(ledger, admission.strategy_id, target_notional, limits)
    card.risk_verdict = verdict
    if not verdict["approved"]:
        return card.stop(OUTCOME_VETOED, "RISK_VETOED_SCHEDULED_EXIT", *verdict["vetoes"])

    fills: list[dict[str, Any]] = []
    price_lookup: dict[str, float] = {}
    for symbol, exposure in sorted(held.items()):
        if not panel.has(execution_date, symbol):
            continue
        price = panel.adjusted(execution_date, symbol, "open")
        if price <= 0:
            continue
        price_lookup[symbol] = price
        adv = adv_by_symbol.get(symbol) or AdvReference(symbol=symbol, value=0.0, state="MISSING")
        post_check = post_size_cost_check(
            admission.strategy_id, symbol, exposure, execution, research_one_way_cost_bps, adv)
        card.post_size_cost_consistency[symbol] = post_check
        if not post_check.consistent:
            return card.stop(OUTCOME_NO_TRADE,
                             "EXECUTION_COST_CONSISTENCY_EXCEEDED_AFTER_SIZING",
                             *post_check.violations())

    for symbol in sorted(held):
        if symbol not in price_lookup:
            continue
        position = ledger.sleeves.get(admission.strategy_id, {}).get(symbol)
        if position is None or abs(position.quantity) <= 1e-9:
            continue
        fill = execution.fill(panel, symbol, -position.quantity, signal_date, execution_date,
                              phase=PHASE_SCHEDULED_EXIT)
        fills.append(fill)

    if not fills:
        return card.stop(OUTCOME_NO_TRADE, "SCHEDULED_EXIT_NO_ORDER_CLEARED")

    card.fills = fills
    for fill in fills:
        operation_id = f"{opportunity_id}:{fill['symbol']}:{PHASE_SCHEDULED_EXIT}"
        ledger.apply_fill(fill["symbol"], fill["quantity"], fill["fill_price"],
                          fill["commission"], execution_date, admission.strategy_id,
                          operation_id=operation_id)
        card.book_operation_ids.append(operation_id)

    return card.stop(OUTCOME_BOOKED)
