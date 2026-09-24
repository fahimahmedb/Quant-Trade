"""The Capital Desk.

One session runs the whole North-Star chain for every strategy the system is
entitled to act on:

``SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK``

The stages are separate functions with their own verdicts because the
architecture requires each decision to be traceable, not because six models are
needed. Most of them are deterministic.

The session obeys one causal timeline:

``information through close(t) -> decision after close(t) -> fill at open(t+1)
-> mark at close(t+1)``

The Book is therefore marked on the execution date, never on the decision date:
marking at close(t) after applying a fill priced at open(t+1) would move the
Book backward in time and value positions before they existed.

A strategy reaches the capital ledger only from a tradable lifecycle state.
Strategies on the evaluation track run the identical chain into a zero-authority
ledger so the system can measure the cost of its own rejections.
"""

from __future__ import annotations

from typing import Any

from ..book.ledger import Ledger
from ..dataplane.panel import PricePanel
from ..dataplane.registry import DatasetRegistry
from ..events import EventLog
from ..factory.signals import should_rebalance, weights_for
from ..factory.strategies import StrategyDefinition, StrategyRegistry
from ..paths import QuantPaths
from ..state import ComponentRegistry, append_jsonl, read_jsonl
from .execution import ExecutionModel
from .journal import DeskJournal
from .opportunity import OpportunityTicket
from .risk import RiskLimits, evaluate as evaluate_risk, verify_final


MIN_ORDER_NOTIONAL = 500.0


class CapitalDesk:
    def __init__(self, paths: QuantPaths, strategies: StrategyRegistry,
                 datasets: DatasetRegistry, log: EventLog, components: ComponentRegistry,
                 execution: ExecutionModel | None = None, limits: RiskLimits | None = None,
                 initial_capital: float = 1_000_000.0, strategy_allocation: float = 0.5):
        self.paths = paths
        self.strategies = strategies
        self.datasets = datasets
        self.log = log
        self.components = components
        self.execution = execution or ExecutionModel()
        self.limits = limits or RiskLimits()
        self.strategy_allocation = strategy_allocation
        self.journal = DeskJournal(paths.desk_journal)
        self.capital = Ledger(paths.book, "quant-shadow-book", "CAPITAL", initial_capital)
        self.evaluation = Ledger(paths.evaluation_ledger, "quant-evaluation-track",
                                 "EVALUATION", initial_capital)
        self._opportunity_ids: set[str] | None = None

    # --- helpers -----------------------------------------------------------
    def ledger_for(self, definition: StrategyDefinition) -> Ledger:
        if definition.tradable:
            return self.capital
        # A strategy that lost its entitlement still owns its capital sleeve
        # until that sleeve is flat; its exit must be booked where it lives.
        if self._holds(self.capital, definition.strategy_id):
            return self.capital
        return self.evaluation

    @staticmethod
    def _holds(ledger: Ledger, strategy_id: str) -> bool:
        return any(abs(position.quantity) > 1e-9
                   for position in ledger.sleeves.get(strategy_id, {}).values())

    def liquidating(self, definition: StrategyDefinition) -> bool:
        """No entitlement left, but a sleeve still open: it must be flattened."""
        return (not definition.tradable and not definition.evaluation_track
                and self._holds(self.capital, definition.strategy_id))

    def actionable(self) -> list[StrategyDefinition]:
        return sorted((definition for definition in self.strategies.strategies.values()
                       if definition.tradable or definition.evaluation_track
                       or self.liquidating(definition)),
                      key=lambda item: item.strategy_id)

    # --- the chain ---------------------------------------------------------
    def run_session(self, panel: PricePanel, date: str, next_date: str | None) -> dict[str, Any]:
        """Run one dated session. ``next_date`` is when orders can actually execute."""
        tickets: list[OpportunityTicket] = []
        replayed: list[str] = []
        actionable = self.actionable()
        decision = self.journal.decision_snapshot(date)
        if decision is None:
            decision = self.journal.begin_session(
                date, self.capital.state.to_dict(), self.evaluation.state.to_dict())
        decision_ledgers = {authority: Ledger.from_document(document)
                            for authority, document in decision.items()}

        self.components.set("SCAN", "RUN", f"session {date}")
        if not actionable:
            self.components.set("SCAN", "IDLE", "no strategy is tradable or on evaluation")
            for name in ("VET", "SIZE", "RISK", "FILLS"):
                self.components.set(name, "IDLE", "no opportunity reached this stage")
            self.log.emit("DESK", "SCAN", "session_no_candidates", date,
                          reason="no strategy holds a tradable lifecycle state")
        for definition in actionable:
            opportunity_id = f"OPP-{definition.strategy_id}-{date}"
            if self.journal.is_processed(opportunity_id):
                outcome = self.journal.outcomes.get(opportunity_id)
                if outcome:
                    tickets.append(OpportunityTicket(**outcome))
                replayed.append(opportunity_id)
                continue
            plan = self.journal.pending_plan(opportunity_id)
            if plan is not None:
                tickets.append(self._resume(definition, plan))
                replayed.append(opportunity_id)
                continue
            try:
                tickets.append(self._run_strategy(
                    panel, date, next_date, definition, opportunity_id,
                    decision_ledgers[self.ledger_for(definition).state.authority]))
            except Exception as exc:
                # Once intent is durable this is a transaction interruption,
                # not a strategy fault.  Let the process boundary propagate so
                # restart recovery resumes the recorded plan.
                if self.journal.pending_plan(opportunity_id) is not None:
                    raise
                ticket = OpportunityTicket(opportunity_id, date, definition.strategy_id,
                                           definition.lifecycle,
                                           self.ledger_for(definition).state.authority,
                                           execution_date=next_date)
                ticket.stop("SCAN", "FAULT", f"{type(exc).__name__}: {exc}")
                self.components.set("SCAN", "FAULT", ticket.reason)
                self.log.emit("DESK", "SCAN", "strategy_fault", opportunity_id,
                              severity="FAULT", strategy=definition.strategy_id,
                              session=date, error=ticket.reason)
                tickets.append(self._finish(definition, ticket))

        if next_date:
            self._charge_rolls(panel, date, next_date, decision_ledgers)
        # The mark belongs to the session where the orders executed.
        marks = self._mark(panel, next_date or date)
        # Re-reading the whole append-only file every session was O(history)
        # (red-team finding); the id set is loaded once and kept in step.
        if self._opportunity_ids is None:
            self._opportunity_ids = {row.get("opportunity_id")
                                     for row in read_jsonl(self.paths.opportunities)}
        for ticket in tickets:
            if ticket.opportunity_id not in self._opportunity_ids:
                append_jsonl(self.paths.opportunities, ticket.to_dict())
                self._opportunity_ids.add(ticket.opportunity_id)
        self.journal.close_session(date)
        return {"date": date, "execution_date": next_date,
                "tickets": [ticket.to_dict() for ticket in tickets], "replayed": replayed,
                "capital": self.capital.summary(), "evaluation": self.evaluation.summary(),
                "marks": marks}

    def _run_strategy(self, panel: PricePanel, date: str, next_date: str | None,
                      definition: StrategyDefinition, opportunity_id: str,
                      decision_ledger: Ledger) -> OpportunityTicket:
        spec = definition.to_spec()
        ledger = self.ledger_for(definition)
        decision_prices = {symbol: panel.adjusted(date, symbol, "close")
                           for symbol in panel.symbols if panel.has(date, symbol)}
        execution_prices = ({symbol: panel.adjusted(next_date, symbol, "open")
                             for symbol in panel.symbols if next_date and panel.has(next_date, symbol)})
        ticket = OpportunityTicket(
            opportunity_id=opportunity_id, session_date=date,
            strategy_id=definition.strategy_id, lifecycle=definition.lifecycle,
            ledger=ledger.state.authority, execution_date=next_date)

        # --- SCAN ----------------------------------------------------------
        missing = self.datasets.missing_for([spec.dataset_id] if spec.dataset_id else [])
        if missing:
            self.components.set("SCAN", "BLOCKED", f"dataset unavailable: {missing}")
            return self._finish(definition, ticket.stop(
                "SCAN", "BLOCKED", f"required dataset unavailable: {missing}", missing=missing))
        liquidating = self.liquidating(definition)
        weights = {} if liquidating else weights_for(panel, spec, date)
        ticket.target_weights = weights
        if liquidating:
            ticket.record("SCAN", "LIQUIDATE",
                          f"{definition.lifecycle}: no capital entitlement remains; the open "
                          f"sleeve is flattened through the normal chain")
        elif not weights:
            self.components.set("SCAN", "IDLE", "no qualifying cross-sectional signal")
            return self._finish(definition, ticket.stop(
                "SCAN", "NO_TRADE", "no symbol cleared the signal threshold at this session"))
        ticket.record("SCAN", "CANDIDATE", f"{len(weights)} legs proposed by "
                      f"{spec.label}", gross=sum(abs(value) for value in weights.values()))

        # --- VET -----------------------------------------------------------
        self.components.set("VET", "RUN", definition.strategy_id)
        if next_date is None:
            self.components.set("VET", "BLOCKED", "no execution session follows this one")
            return self._finish(definition, ticket.stop(
                "VET", "BLOCKED", "no later session exists in which orders could execute"))
        sessions_held = self._sessions_since_rebalance(definition, panel, date)
        current_weights = self._current_weights(decision_ledger, definition, decision_prices)
        drift = sum(abs(weights.get(symbol, 0.0) - current_weights.get(symbol, 0.0))
                    for symbol in set(weights) | set(current_weights))
        if not liquidating and not should_rebalance(sessions_held, drift, spec):
            self.components.set("VET", "IDLE", "holding period or no-trade band")
            return self._finish(definition, ticket.stop(
                "VET", "NO_TRADE", f"{sessions_held} sessions into a "
                f"{spec.holding_days}-session hold with drift {drift:.3f} against a "
                f"{spec.no_trade_band:.2f} band", sessions_held=sessions_held, drift=drift))
        ticket.record("VET", "ACCEPTED", f"rebalance due, drift {drift:.3f}", drift=drift,
                      lifecycle=definition.lifecycle)

        # --- SIZE ----------------------------------------------------------
        self.components.set("SIZE", "RUN", definition.strategy_id)
        capital = decision_ledger.nav_at(decision_prices) * definition.capital_fraction * self.strategy_allocation
        target_notional = {symbol: capital * weight for symbol, weight in weights.items()}
        # Legs the sleeve holds but no longer wants are targeted at zero, so RISK
        # scores the portfolio the fills will actually produce.
        for symbol in decision_ledger.sleeve_exposures_at(definition.strategy_id, decision_prices):
            target_notional.setdefault(symbol, 0.0)
        ticket.sized_notional = sum(abs(value) for value in target_notional.values())
        entitlement = ("counterfactual size on the evaluation ledger"
                       if not definition.tradable else
                       f"{definition.lifecycle} capital entitlement")
        ticket.record("SIZE", "SIZED",
                      f"{entitlement}: {definition.capital_fraction:.0%} of a "
                      f"{self.strategy_allocation:.0%} allocation",
                      capital_fraction=definition.capital_fraction, allocation=capital,
                      gross_notional=ticket.sized_notional)

        # --- RISK ----------------------------------------------------------
        self.components.set("RISK", "RUN", definition.strategy_id)
        verdict = evaluate_risk(decision_ledger, definition.strategy_id, target_notional,
                                self.limits, decision_prices)
        if liquidating:
            # Flattening only removes exposure. A throttle or a breached floor
            # must never trap a sleeve that has lost its entitlement.
            verdict = {**verdict, "approved": True, "scale": 1.0,
                       "scaled_target": dict(target_notional),
                       "liquidation_override": verdict["vetoes"]}
        if not verdict["approved"]:
            self.components.set("RISK", "IDLE", "proposal vetoed")
            self.log.emit("DESK", "RISK", "opportunity_vetoed", ticket.opportunity_id,
                          severity="WARN", vetoes=verdict["vetoes"])
            return self._finish(definition, ticket.stop(
                "RISK", "VETOED", "; ".join(verdict["vetoes"]), **verdict))
        approved = verdict["scaled_target"]
        ticket.record("RISK", "APPROVED",
                      f"final portfolio gross {verdict['gross_ratio']:.2f}x, net "
                      f"{verdict['net_ratio']:+.3f}x, scale {verdict['scale']:.2f}", **verdict)

        # --- FILLS ---------------------------------------------------------
        self.components.set("FILLS", "RUN", definition.strategy_id)
        legs, fills = self._execute(panel, ledger, definition, date, next_date, approved,
                                    minimum=0.0 if liquidating else MIN_ORDER_NOTIONAL)
        ticket.legs = legs
        ticket.fills = fills
        if not fills:
            self.components.set("FILLS", "IDLE", "no order cleared the minimum size")
            return self._finish(definition, ticket.stop(
                "FILLS", "NO_TRADE", "every implied order was below the minimum order size"))

        # Capacity truncation can move the executed portfolio away from the approved
        # one, so the limits are checked once more on what will actually be applied.
        final_prices = dict(execution_prices)
        final_prices.update({fill["symbol"]: fill["fill_price"] for fill in fills})
        quantities = {symbol: position.quantity
                      for symbol, position in ledger.sleeves.get(definition.strategy_id, {}).items()
                      if abs(position.quantity) > 1e-9}
        for fill in fills:
            quantities[fill["symbol"]] = quantities.get(fill["symbol"], 0.0) + fill["quantity"]
        executed = {symbol: quantity * final_prices[symbol]
                    for symbol, quantity in quantities.items() if abs(quantity) > 1e-9}
        commission = sum(fill["commission"] for fill in fills)
        final = verify_final(ledger, definition.strategy_id, executed, self.limits,
                             final_prices, nav_adjustment=-commission)
        if liquidating and not final["approved"]:
            final = {**final, "approved": True, "liquidation_override": final["vetoes"]}
        if not final["approved"]:
            self.components.set("RISK", "IDLE", "executed portfolio vetoed")
            self.log.emit("DESK", "RISK", "execution_vetoed", ticket.opportunity_id,
                          severity="WARN", vetoes=final["vetoes"])
            return self._finish(definition, ticket.stop(
                "RISK", "VETOED",
                "executed portfolio breaches a hard limit: " + "; ".join(final["vetoes"]),
                **final))
        ticket.record("FILLS", "FILLED", f"{len(fills)} orders executed at the "
                      f"{next_date} open",
                      shortfall=sum(fill["implementation_shortfall"] for fill in fills),
                      commission=sum(fill["commission"] for fill in fills),
                      final_gross_ratio=final["gross_ratio"],
                      final_net_ratio=final["net_ratio"])

        # --- BOOK ----------------------------------------------------------
        self.components.set("BOOK", "RUN", definition.strategy_id)
        # Intent is durable before money moves, so a crash here resumes rather
        # than re-deciding against a Book that already carries these fills.
        self.journal.begin(opportunity_id, definition.strategy_id, date,
                           ticket.to_dict(), fills)
        return self._apply(definition, ticket, fills, next_date)

    def _apply(self, definition: StrategyDefinition, ticket: OpportunityTicket,
               fills: list[dict[str, Any]], execution_date: str) -> OpportunityTicket:
        """Apply a recorded plan. Safe to call again after a crash."""
        ledger = self.ledger_for(definition)
        effects = [ledger.apply_fill(fill["symbol"], fill["quantity"], fill["fill_price"],
                                     fill["commission"], execution_date,
                                     definition.strategy_id,
                                     operation_id=f"{ticket.opportunity_id}:{fill['symbol']}")
                   for fill in fills]
        ticket.book_effect = {"ledger": ledger.state.authority, "nav_after": ledger.nav,
                              "cash_after": ledger.state.cash,
                              "realized_pnl": sum(effect["realized_pnl"] for effect in effects),
                              "costs": sum(fill["commission"] for fill in fills),
                              "replayed_operations": sum(1 for effect in effects
                                                         if effect["replayed"])}
        self.log.emit("DESK", "BOOK", "opportunity_booked", ticket.opportunity_id,
                      ledger=ledger.state.authority, strategy=definition.strategy_id,
                      orders=len(fills), notional=sum(fill["notional"] for fill in fills))
        if ticket.status != "BOOKED":
            ticket.complete(f"{len(fills)} fills applied to the "
                            f"{ledger.state.authority} ledger", **ticket.book_effect)
        return self._finish(definition, ticket, rebalanced=True)

    def _resume(self, definition: StrategyDefinition,
                plan: dict[str, Any]) -> OpportunityTicket:
        """Re-apply an interrupted session's recorded intent, unchanged."""
        ticket = OpportunityTicket(**plan["ticket"])
        self.log.emit("DESK", "BOOK", "session_resumed", ticket.opportunity_id,
                      severity="WARN", strategy=definition.strategy_id,
                      fills=len(plan["fills"]))
        return self._apply(definition, ticket, plan["fills"],
                           ticket.execution_date or plan["session_date"])

    # --- stage helpers -----------------------------------------------------
    def _finish(self, definition: StrategyDefinition, ticket: OpportunityTicket,
                rebalanced: bool = False) -> OpportunityTicket:
        self.journal.commit(ticket.opportunity_id, definition.strategy_id, ticket.status,
                            ticket.session_date, rebalanced, ticket.to_dict())
        return ticket

    def _sessions_since_rebalance(self, definition: StrategyDefinition, panel: PricePanel,
                                  date: str) -> int | None:
        last = self.journal.stats_for(definition.strategy_id).get("last_rebalance_date")
        if not last:
            return None
        spec = definition.to_spec()
        universe = [spec.calendar_symbol] if spec.calendar_symbol else spec.universe
        previous = panel.aligned_index(universe, last)
        current = panel.aligned_index(universe, date)
        if previous is None or current is None:
            return None
        return current - previous

    def _current_weights(self, ledger: Ledger, definition: StrategyDefinition,
                         prices: dict[str, float]) -> dict[str, float]:
        held = ledger.sleeve_exposures_at(definition.strategy_id, prices)
        base = ledger.nav_at(prices) * definition.capital_fraction * self.strategy_allocation
        if base <= 0:
            return {}
        return {symbol: value / base for symbol, value in held.items()}

    def _execute(self, panel: PricePanel, ledger: Ledger, definition: StrategyDefinition,
                 date: str, next_date: str, target_notional: dict[str, float],
                 minimum: float = MIN_ORDER_NOTIONAL
                 ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        prices = {symbol: panel.adjusted(next_date, symbol, "open") for symbol in panel.symbols
                  if panel.has(next_date, symbol)}
        held = ledger.sleeve_exposures_at(definition.strategy_id, prices)
        legs: list[dict[str, Any]] = []
        fills: list[dict[str, Any]] = []
        for symbol in sorted(set(target_notional) | set(held)):
            if not panel.has(next_date, symbol):
                continue
            price = panel.adjusted(next_date, symbol, "open")
            if price <= 0:
                continue
            target = target_notional.get(symbol, 0.0)
            current = held.get(symbol, 0.0)
            delta_notional = target - current
            leg = {"symbol": symbol, "target_notional": target, "current_notional": current,
                   "delta_notional": delta_notional}
            legs.append(leg)
            if abs(delta_notional) < minimum or abs(delta_notional) <= 1e-9:
                leg["skipped"] = "below minimum order size"
                continue
            quantity = delta_notional / price
            if target == 0.0:
                # close exactly: price drift must not leave a residual sliver
                position = ledger.sleeves.get(definition.strategy_id, {}).get(symbol)
                if position is not None:
                    quantity = -position.quantity
            fill = self.execution.fill(panel, symbol, quantity, date, next_date)
            if abs(fill["quantity"]) * fill["fill_price"] < minimum:
                leg["skipped"] = "capacity truncation left the order below minimum size"
                continue
            fills.append(fill)
        return legs, fills

    def _charge_rolls(self, panel: PricePanel, date: str, next_date: str,
                      decision_ledgers: dict[str, Ledger]) -> float:
        """Charge contract rolls to the positions that were held across them.

        Positions entering the session (the durable decision snapshot, so a
        replay sees the same holdings) are held through ``next_date``'s move
        until that session's fills, so they pay any roll recorded on
        ``next_date``. The charge is on absolute notional: longs and shorts
        both pay to roll. Research charges the identical amount.
        """
        total = 0.0
        for authority, snapshot in decision_ledgers.items():
            ledger = self.capital if authority == self.capital.state.authority else self.evaluation
            for strategy_id, holdings in sorted(snapshot.sleeves.items()):
                for symbol, position in sorted(holdings.items()):
                    if abs(position.quantity) <= 1e-9 or not panel.has(date, symbol):
                        continue
                    rate = (panel.feature(next_date, symbol, "roll_cost")
                            if panel.has(next_date, symbol) else None)
                    if not rate:
                        continue
                    amount = abs(position.quantity) * panel.price(date, symbol) * rate
                    effect = ledger.apply_charge(
                        strategy_id, amount, next_date,
                        operation_id=f"ROLL-{strategy_id}-{symbol}-{next_date}", kind="roll")
                    total += effect["amount"]
        return total

    def _mark(self, panel: PricePanel, mark_date: str) -> dict[str, Any]:
        prices = {symbol: panel.price(mark_date, symbol) for symbol in panel.symbols
                  if panel.has(mark_date, symbol)}
        capital_point = self.capital.mark_to_market(mark_date, prices)
        evaluation_point = self.evaluation.mark_to_market(mark_date, prices)
        self.components.set("BOOK", "RUN" if self.capital.open_positions() else "IDLE",
                            f"marked {mark_date}")
        return {"capital": capital_point, "evaluation": evaluation_point}
