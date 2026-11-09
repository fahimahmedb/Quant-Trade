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
from .execution import ExecutionCapacityUnavailable, ExecutionModel
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

    # --- helpers -----------------------------------------------------------
    def ledger_for(self, definition: StrategyDefinition,
                   authority: str | None = None) -> Ledger:
        if authority is not None:
            if authority == "CAPITAL":
                return self.capital
            if authority == "EVALUATION":
                return self.evaluation
            raise ValueError(f"unknown recorded Book authority: {authority}")
        return self.capital if definition.tradable else self.evaluation

    def actionable(self) -> list[StrategyDefinition]:
        return sorted((definition for definition in self.strategies.strategies.values()
                       if definition.tradable or definition.evaluation_track
                       or any(book.sleeve_exposures(definition.strategy_id)
                              for book in (self.capital, self.evaluation))
                       or any(plan.get("strategy_id") == definition.strategy_id
                              for plan in self.journal.pending.values())),
                      key=lambda item: item.strategy_id)

    def _work_items(self, date: str, actionable: list[StrategyDefinition]
                    ) -> list[tuple[StrategyDefinition, str, str | None]]:
        """Retired sleeves remain tracked in their original Book, not rehomed."""
        tasks: list[tuple[StrategyDefinition, str, str | None]] = []
        for definition in actionable:
            ordinary_id = f"OPP-{definition.strategy_id}-{date}"
            if definition.lifecycle != "RETIRED":
                tasks.append((definition, ordinary_id, None))
                continue
            pending_books: set[str] = set()
            # A decision already booked under the legacy per-session identity
            # cannot be silently followed by a second retirement fill on replay.
            prior = self.journal.outcomes.get(ordinary_id)
            if ordinary_id in self.journal.processed and isinstance(prior, dict):
                prior_authority = prior.get("ledger")
                if prior_authority in {"CAPITAL", "EVALUATION"}:
                    tasks.append((definition, ordinary_id, prior_authority))
                    pending_books.add(prior_authority)
            for opportunity_id, plan in sorted(self.journal.pending.items()):
                if (plan.get("strategy_id") != definition.strategy_id
                        or plan.get("session_date") != date):
                    continue
                authority = (plan.get("ticket") or {}).get("ledger")
                if authority not in {"CAPITAL", "EVALUATION"}:
                    raise ValueError("pending retirement replay lacks original Book authority")
                tasks.append((definition, opportunity_id, authority))
                pending_books.add(authority)
            # Explicit evaluation_track preserves the zero-authority
            # counterfactual lifecycle even after retirement from CAPITAL.
            if definition.evaluation_track and "EVALUATION" not in pending_books:
                evaluation_id = (ordinary_id if not any(
                    item[1] == ordinary_id for item in tasks)
                    else f"OPP-{definition.strategy_id}-EVALUATION-{date}")
                tasks.append((definition, evaluation_id, "EVALUATION"))
                pending_books.add("EVALUATION")
            for book in (self.capital, self.evaluation):
                authority = book.state.authority
                if (authority not in pending_books
                        and book.sleeve_exposures(definition.strategy_id)):
                    tasks.append((definition,
                                  f"OPP-{definition.strategy_id}-{authority}-{date}",
                                  authority))
        return tasks

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
        for definition, opportunity_id, authority in self._work_items(date, actionable):
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
                    decision_ledgers[self.ledger_for(definition, authority).state.authority],
                    authority=authority))
            except Exception as exc:
                # Once intent is durable this is a transaction interruption,
                # not a strategy fault.  Let the process boundary propagate so
                # restart recovery resumes the recorded plan.
                if self.journal.pending_plan(opportunity_id) is not None:
                    raise
                ticket = OpportunityTicket(opportunity_id, date, definition.strategy_id,
                                           definition.lifecycle,
                                           self.ledger_for(definition, authority).state.authority,
                                           execution_date=next_date)
                ticket.stop("SCAN", "FAULT", f"{type(exc).__name__}: {exc}")
                self.components.set("SCAN", "FAULT", ticket.reason)
                self.log.emit("DESK", "SCAN", "strategy_fault", opportunity_id,
                              severity="FAULT", strategy=definition.strategy_id,
                              session=date, error=ticket.reason)
                tickets.append(self._finish(definition, ticket))

        # The mark belongs to the session where the orders executed.
        marks = self._mark(panel, next_date or date)
        existing = {row.get("opportunity_id") for row in read_jsonl(self.paths.opportunities)}
        for ticket in tickets:
            if ticket.opportunity_id not in existing:
                append_jsonl(self.paths.opportunities, ticket.to_dict())
        self.journal.close_session(date)
        return {"date": date, "execution_date": next_date,
                "tickets": [ticket.to_dict() for ticket in tickets], "replayed": replayed,
                "capital": self.capital.summary(), "evaluation": self.evaluation.summary(),
                "marks": marks}

    def _run_strategy(self, panel: PricePanel, date: str, next_date: str | None,
                      definition: StrategyDefinition, opportunity_id: str,
                      decision_ledger: Ledger, authority: str | None = None
                      ) -> OpportunityTicket:
        spec = definition.to_spec()
        ledger = self.ledger_for(definition, authority)
        decision_prices = {symbol: panel.adjusted(date, symbol, "close")
                           for symbol in panel.symbols if panel.has(date, symbol)}
        execution_prices = ({symbol: panel.adjusted(next_date, symbol, "open")
                             for symbol in panel.symbols if next_date and panel.has(next_date, symbol)})
        ticket = OpportunityTicket(
            opportunity_id=opportunity_id, session_date=date,
            strategy_id=definition.strategy_id, lifecycle=definition.lifecycle,
            ledger=ledger.state.authority, execution_date=next_date)

        if (definition.lifecycle == "RETIRED"
                and not (ledger.state.authority == "EVALUATION"
                         and definition.evaluation_track)):
            held = decision_ledger.sleeve_exposures_at(definition.strategy_id, decision_prices)
            if not held:
                return self._finish(definition, ticket.stop(
                    "SCAN", "NO_TRADE", "retired sleeve already flat in original Book"))
            ticket.record("SCAN", "CANDIDATE",
                          "retired sleeve requires tracked risk reduction",
                          residual_notional=held, source_ledger=ledger.state.authority)
            if next_date is None:
                return self._finish(definition, ticket.stop(
                    "VET", "BLOCKED", "no eligible next execution session for retired sleeve",
                    residual_notional=held))
            ticket.record("VET", "ACCEPTED", "retirement exit mandate only")
            target_notional = {symbol: 0.0 for symbol in held}
            ticket.record("SIZE", "SIZED", "reduce retired sleeve to zero where admissible",
                          gross_notional=sum(abs(value) for value in held.values()))
        else:
            # --- SCAN ----------------------------------------------------------
            missing = self.datasets.missing_for([spec.dataset_id] if spec.dataset_id else [])
            if missing:
                self.components.set("SCAN", "BLOCKED", f"dataset unavailable: {missing}")
                return self._finish(definition, ticket.stop(
                    "SCAN", "BLOCKED", f"required dataset unavailable: {missing}", missing=missing))
            weights = weights_for(panel, spec, date)
            ticket.target_weights = weights
            if not weights:
                existing = decision_ledger.sleeve_exposures_at(definition.strategy_id, decision_prices)
                aligned_index = panel.aligned_index(spec.universe, date)
                if aligned_index is None:
                    status = "BLOCKED"
                    reason = "required aligned signal data unavailable"
                elif aligned_index < spec.lookback_days:
                    status = "NO_TRADE"
                    reason = "insufficient signal history; existing sleeve remains tracked"
                else:
                    status = "NO_TRADE"
                    reason = "no qualifying signal target; existing sleeve remains tracked"
                self.components.set("SCAN", "IDLE" if status == "NO_TRADE" else "BLOCKED", reason)
                return self._finish(definition, ticket.stop(
                    "SCAN", status, reason, held_notional=existing,
                    signal_state="DATA_UNAVAILABLE" if status == "BLOCKED" else "NO_TARGET"))
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
        legs, fills = self._execute(panel, ledger, definition, date, next_date, approved)
        ticket.legs = legs
        ticket.fills = fills
        if not fills:
            reasons = [leg.get("skipped") for leg in legs if leg.get("skipped")]
            status = "BLOCKED" if reasons else "NO_TRADE"
            reason = "; ".join(sorted(set(reasons))) if reasons else "no executable orders"
            self.components.set("FILLS", "BLOCKED" if reasons else "IDLE", reason)
            return self._finish(definition, ticket.stop(
                "FILLS", status, reason, residual_legs=legs))

        # Capacity truncation can move the executed portfolio away from the approved
        # one, so the limits are checked once more on what will actually be applied.
        final = self._verify_modeled_fills(ledger, definition.strategy_id, fills,
                                          execution_prices)
        if not final["approved"]:
            self.components.set("RISK", "IDLE", "executed portfolio vetoed")
            self.log.emit("DESK", "RISK", "execution_vetoed", ticket.opportunity_id,
                          severity="WARN", vetoes=final["vetoes"])
            return self._finish(definition, ticket.stop(
                "RISK", "VETOED",
                "executed portfolio breaches a hard limit: " + "; ".join(final["vetoes"]),
                **final))
        # An overnight gap can activate the halt after the decision. Every
        # independently durable prefix must then pass at the same opening marks.
        if min(verdict["drawdown"], final["drawdown"]) <= self.limits.drawdown_halt:
            for prefix_length in range(1, len(fills)):
                prefix_verdict = self._verify_modeled_fills(
                    ledger, definition.strategy_id, fills[:prefix_length], execution_prices)
                if not prefix_verdict["approved"]:
                    return self._finish(definition, ticket.stop(
                        "RISK", "VETOED", "unsafe intermediate fill under drawdown halt",
                        prefix_length=prefix_length, vetoes=prefix_verdict["vetoes"]))
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

    def _verify_modeled_fills(self, ledger: Ledger, strategy_id: str,
                              fills: list[dict[str, Any]],
                              opening_prices: dict[str, float]) -> dict[str, Any]:
        """Compare Book risk at fixed opening marks, including execution loss."""
        exposures = ledger.sleeve_exposures_at(strategy_id, opening_prices)
        nav_adjustment = 0.0
        for fill in fills:
            symbol = fill["symbol"]
            price = opening_prices[symbol]
            quantity = fill["quantity"]
            exposures[symbol] = exposures.get(symbol, 0.0) + quantity * price
            nav_adjustment -= quantity * (fill["fill_price"] - price) + fill["commission"]
        return verify_final(ledger, strategy_id, exposures, self.limits, opening_prices,
                            nav_adjustment=nav_adjustment)

    def _apply(self, definition: StrategyDefinition, ticket: OpportunityTicket,
               fills: list[dict[str, Any]], execution_date: str) -> OpportunityTicket:
        """Apply a recorded plan. Safe to call again after a crash."""
        ledger = self.ledger_for(definition, ticket.ledger)
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
        universe = definition.to_spec().universe
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
                 date: str, next_date: str, target_notional: dict[str, float]
                 ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        prices = {symbol: panel.adjusted(next_date, symbol, "open") for symbol in panel.symbols
                  if panel.has(next_date, symbol)}
        held = ledger.sleeve_exposures_at(definition.strategy_id, prices)
        unpriced_held = {symbol for symbol in held if prices.get(symbol, 0.0) <= 0.0}
        legs: list[dict[str, Any]] = []
        fills: list[dict[str, Any]] = []
        for symbol in sorted(set(target_notional) | set(held)):
            target = target_notional.get(symbol, 0.0)
            current = held.get(symbol, 0.0)
            delta_notional = target - current
            leg = {"symbol": symbol, "target_notional": target, "current_notional": current,
                   "delta_notional": delta_notional}
            legs.append(leg)
            price = prices.get(symbol, 0.0)
            if price <= 0.0:
                leg["skipped"] = "opening price unavailable"
                continue
            if unpriced_held:
                leg["skipped"] = "existing sleeve has an unpriced opening leg"
                continue
            if abs(delta_notional) < MIN_ORDER_NOTIONAL:
                leg["skipped"] = "below minimum order size"
                continue
            try:
                fill = self.execution.fill(panel, symbol, delta_notional / price, date, next_date)
            except ExecutionCapacityUnavailable as exc:
                leg["skipped"] = str(exc)
                continue
            if abs(fill["quantity"]) * fill["fill_price"] < MIN_ORDER_NOTIONAL:
                leg["skipped"] = "capacity truncation left the order below minimum size"
                continue
            fills.append(fill)
        return legs, fills

    def _mark(self, panel: PricePanel, mark_date: str) -> dict[str, Any]:
        prices = {symbol: panel.price(mark_date, symbol) for symbol in panel.symbols
                  if panel.has(mark_date, symbol)}
        capital_point = self.capital.mark_to_market(mark_date, prices)
        evaluation_point = self.evaluation.mark_to_market(mark_date, prices)
        self.components.set("BOOK", "RUN" if self.capital.open_positions() else "IDLE",
                            f"marked {mark_date}")
        return {"capital": capital_point, "evaluation": evaluation_point}
