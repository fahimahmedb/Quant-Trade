"""The Capital Desk.

One session runs the whole North-Star chain for every strategy the system is
entitled to act on:

``SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK``

The stages are separate functions with their own verdicts because the
architecture requires each decision to be traceable, not because six models are
needed. Most of them are deterministic.

A strategy reaches the capital ledger only from a tradable lifecycle state.
Strategies on the evaluation track run the identical chain into a zero-authority
ledger so the system can measure the cost of its own rejections.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..book.ledger import Ledger
from ..dataplane.panel import PricePanel
from ..dataplane.registry import DatasetRegistry
from ..events import EventLog
from ..factory.signals import should_rebalance, weights_for
from ..factory.strategies import StrategyDefinition, StrategyRegistry
from ..paths import QuantPaths
from ..state import ComponentRegistry, append_jsonl
from .execution import ExecutionModel
from .opportunity import OpportunityTicket
from .risk import RiskLimits, evaluate as evaluate_risk


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
        self.capital = Ledger(paths.book, "quant-shadow-book", "CAPITAL", initial_capital)
        self.evaluation = Ledger(Path(str(paths.var / "evaluation_ledger.json")),
                                 "quant-evaluation-track", "EVALUATION", initial_capital)

    # --- helpers -----------------------------------------------------------
    def ledger_for(self, definition: StrategyDefinition) -> Ledger:
        return self.capital if definition.tradable else self.evaluation

    def actionable(self) -> list[StrategyDefinition]:
        return sorted((definition for definition in self.strategies.strategies.values()
                       if definition.tradable or definition.desk.get("evaluation_track")),
                      key=lambda item: item.strategy_id)

    def _positions_of(self, ledger: Ledger, strategy_id: str) -> dict[str, float]:
        return {position["symbol"]: position["market_value"]
                for position in ledger.open_positions()
                if position.get("strategy_id") == strategy_id}

    # --- the chain ---------------------------------------------------------
    def run_session(self, panel: PricePanel, date: str, next_date: str | None) -> dict[str, Any]:
        """Run one dated session. ``next_date`` is when orders can actually execute."""
        tickets: list[OpportunityTicket] = []
        actionable = self.actionable()

        self.components.set("SCAN", "RUN", f"session {date}")
        if not actionable:
            self.components.set("SCAN", "IDLE", "no strategy is tradable or on evaluation")
            for name in ("VET", "SIZE", "RISK", "FILLS"):
                self.components.set(name, "IDLE", "no opportunity reached this stage")
            self.log.emit("DESK", "SCAN", "session_no_candidates", date,
                          reason="no strategy holds a tradable lifecycle state")
        for definition in actionable:
            tickets.append(self._run_strategy(panel, date, next_date, definition))

        marks = self._mark(panel, date)
        summary = {"date": date, "tickets": [ticket.to_dict() for ticket in tickets],
                   "capital": self.capital.summary(), "evaluation": self.evaluation.summary(),
                   "marks": marks}
        for ticket in tickets:
            append_jsonl(self.paths.opportunities, ticket.to_dict())
        self.strategies.save()
        return summary

    def _run_strategy(self, panel: PricePanel, date: str, next_date: str | None,
                      definition: StrategyDefinition) -> OpportunityTicket:
        spec = definition.to_spec()
        ledger = self.ledger_for(definition)
        ticket = OpportunityTicket(
            opportunity_id=f"OPP-{definition.strategy_id}-{date}",
            session_date=date, strategy_id=definition.strategy_id,
            lifecycle=definition.lifecycle, ledger=ledger.state.authority)
        definition.desk["sessions"] = definition.desk.get("sessions", 0) + 1
        definition.desk["tickets"] = definition.desk.get("tickets", 0) + 1

        # --- SCAN ----------------------------------------------------------
        missing = self.datasets.missing_for([spec.dataset_id] if spec.dataset_id else [])
        if missing:
            self.components.set("SCAN", "BLOCKED", f"dataset unavailable: {missing}")
            return self._finish(definition, ticket.stop(
                "SCAN", "BLOCKED", f"required dataset unavailable: {missing}", missing=missing))
        weights = weights_for(panel, spec, date)
        ticket.target_weights = weights
        if not weights:
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
        current_weights = self._current_weights(ledger, definition)
        drift = sum(abs(weights.get(symbol, 0.0) - current_weights.get(symbol, 0.0))
                    for symbol in set(weights) | set(current_weights))
        if not should_rebalance(sessions_held, drift, spec):
            self.components.set("VET", "IDLE", "holding period or no-trade band")
            return self._finish(definition, ticket.stop(
                "VET", "NO_TRADE", f"{sessions_held} sessions into a "
                f"{spec.holding_days}-session hold with drift {drift:.3f} against a "
                f"{spec.no_trade_band:.2f} band", sessions_held=sessions_held, drift=drift))
        ticket.record("VET", "ACCEPTED", f"rebalance due, drift {drift:.3f}", drift=drift,
                      lifecycle=definition.lifecycle)

        # --- SIZE ----------------------------------------------------------
        self.components.set("SIZE", "RUN", definition.strategy_id)
        capital = ledger.nav * definition.capital_fraction * self.strategy_allocation
        target_notional = {symbol: capital * weight for symbol, weight in weights.items()}
        # Legs the strategy holds but no longer wants are targeted at zero. Without
        # them RISK would score a portfolio that keeps positions the FILLS stage is
        # about to close, and would veto an exactly neutral rebalance for breaching
        # neutrality -- leaving the book further from the limit than accepting it.
        for symbol in self._positions_of(ledger, definition.strategy_id):
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
        verdict = evaluate_risk(ledger, target_notional, self.limits)
        if not verdict["approved"]:
            self.components.set("RISK", "IDLE", "proposal vetoed")
            definition.desk["vetoed"] = definition.desk.get("vetoed", 0) + 1
            self.log.emit("DESK", "RISK", "opportunity_vetoed", ticket.opportunity_id,
                          severity="WARN", vetoes=verdict["vetoes"])
            return self._finish(definition, ticket.stop(
                "RISK", "VETOED", "; ".join(verdict["vetoes"]), **verdict))
        if verdict["throttled"]:
            target_notional = {symbol: value * verdict["scale"]
                               for symbol, value in target_notional.items()}
        ticket.record("RISK", "APPROVED",
                      f"gross {verdict['gross_ratio']:.2f}x, net {verdict['net_ratio']:+.3f}x, "
                      f"scale {verdict['scale']:.2f}", **verdict)

        # --- FILLS ---------------------------------------------------------
        self.components.set("FILLS", "RUN", definition.strategy_id)
        legs, fills = self._execute(panel, ledger, definition, date, next_date, target_notional)
        ticket.legs = legs
        ticket.fills = fills
        if not fills:
            self.components.set("FILLS", "IDLE", "no order cleared the minimum size")
            return self._finish(definition, ticket.stop(
                "FILLS", "NO_TRADE", "every implied order was below the minimum order size"))
        ticket.record("FILLS", "FILLED", f"{len(fills)} orders executed at the "
                      f"{next_date} open",
                      shortfall=sum(fill["implementation_shortfall"] for fill in fills),
                      commission=sum(fill["commission"] for fill in fills))

        # --- BOOK ----------------------------------------------------------
        self.components.set("BOOK", "RUN", definition.strategy_id)
        effects = [ledger.apply_fill(fill["symbol"], fill["quantity"], fill["fill_price"],
                                     fill["commission"], next_date, definition.strategy_id)
                   for fill in fills]
        ticket.book_effect = {"ledger": ledger.state.authority, "nav_after": ledger.nav,
                              "cash_after": ledger.state.cash,
                              "realized_pnl": sum(effect["realized_pnl"] for effect in effects),
                              "costs": sum(fill["commission"] for fill in fills)}
        definition.desk["last_rebalance_date"] = date
        definition.desk["booked"] = definition.desk.get("booked", 0) + 1
        self.log.emit("DESK", "BOOK", "opportunity_booked", ticket.opportunity_id,
                      ledger=ledger.state.authority, strategy=definition.strategy_id,
                      orders=len(fills), notional=sum(fill["notional"] for fill in fills))
        return self._finish(definition, ticket.complete(
            f"{len(fills)} fills applied to the {ledger.state.authority} ledger",
            **ticket.book_effect))

    # --- stage helpers -----------------------------------------------------
    def _finish(self, definition: StrategyDefinition,
                ticket: OpportunityTicket) -> OpportunityTicket:
        if ticket.status == "NO_TRADE":
            definition.desk["no_trade"] = definition.desk.get("no_trade", 0) + 1
        self.strategies.upsert(definition)
        return ticket

    def _sessions_since_rebalance(self, definition: StrategyDefinition, panel: PricePanel,
                                  date: str) -> int | None:
        last = definition.desk.get("last_rebalance_date")
        if not last:
            return None
        universe = definition.to_spec().universe
        previous = panel.aligned_index(universe, last)
        current = panel.aligned_index(universe, date)
        if previous is None or current is None:
            return None
        return current - previous

    def _current_weights(self, ledger: Ledger, definition: StrategyDefinition) -> dict[str, float]:
        held = self._positions_of(ledger, definition.strategy_id)
        base = ledger.nav * definition.capital_fraction * self.strategy_allocation
        if base <= 0:
            return {}
        return {symbol: value / base for symbol, value in held.items()}

    def _execute(self, panel: PricePanel, ledger: Ledger, definition: StrategyDefinition,
                 date: str, next_date: str, target_notional: dict[str, float]
                 ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        held = self._positions_of(ledger, definition.strategy_id)
        legs: list[dict[str, Any]] = []
        fills: list[dict[str, Any]] = []
        for symbol in sorted(set(target_notional) | set(held)):
            if not panel.has(next_date, symbol):
                continue
            price = self.execution.adjusted(panel, next_date, symbol, "open")
            if price <= 0:
                continue
            target = target_notional.get(symbol, 0.0)
            current = held.get(symbol, 0.0)
            delta_notional = target - current
            leg = {"symbol": symbol, "target_notional": target, "current_notional": current,
                   "delta_notional": delta_notional}
            legs.append(leg)
            if abs(delta_notional) < MIN_ORDER_NOTIONAL:
                leg["skipped"] = "below minimum order size"
                continue
            fill = self.execution.fill(panel, symbol, delta_notional / price, date, next_date)
            if abs(fill["quantity"]) * fill["fill_price"] < MIN_ORDER_NOTIONAL:
                leg["skipped"] = "capacity truncation left the order below minimum size"
                continue
            fills.append(fill)
        return legs, fills

    def _mark(self, panel: PricePanel, date: str) -> dict[str, Any]:
        prices = {symbol: panel.price(date, symbol) for symbol in panel.symbols
                  if panel.has(date, symbol)}
        capital_point = self.capital.mark_to_market(date, prices)
        evaluation_point = self.evaluation.mark_to_market(date, prices)
        self.components.set("BOOK", "RUN" if self.capital.open_positions() else "IDLE",
                            f"marked {date}")
        return {"capital": capital_point, "evaluation": evaluation_point}
