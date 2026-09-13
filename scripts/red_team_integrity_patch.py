"""One-shot patch applicator for the independent V1 red-team repair.

This file deletes itself (and its workflow) after applying the reviewed textual
changes. It exists only because the review environment exposes GitHub writes but
not an interactive checkout.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one match, found {count}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


# -------------------------------------------------------------------------
# Capital Desk: close(t) decisions cannot depend on open(t+1), and final risk
# must value all post-fill quantities on one coherent price vector.
# -------------------------------------------------------------------------
replace_once(
    "src/quant/desk/desk.py",
    '''        execution_prices = ({symbol: panel.adjusted(next_date, symbol, "open")
                             for symbol in panel.symbols if next_date and panel.has(next_date, symbol)})
        ticket = OpportunityTicket(
''',
    '''        decision_prices = {symbol: panel.adjusted(date, symbol, "close")
                           for symbol in panel.symbols if panel.has(date, symbol)}
        execution_prices = ({symbol: panel.adjusted(next_date, symbol, "open")
                             for symbol in panel.symbols if next_date and panel.has(next_date, symbol)})
        ticket = OpportunityTicket(
''')
replace_once(
    "src/quant/desk/desk.py",
    '''        current_weights = self._current_weights(ledger, definition, execution_prices)
''',
    '''        current_weights = self._current_weights(ledger, definition, decision_prices)
''')
replace_once(
    "src/quant/desk/desk.py",
    '''        capital = ledger.nav_at(execution_prices) * definition.capital_fraction * self.strategy_allocation
''',
    '''        capital = ledger.nav_at(decision_prices) * definition.capital_fraction * self.strategy_allocation
''')
replace_once(
    "src/quant/desk/desk.py",
    '''        for symbol in ledger.sleeve_exposures_at(definition.strategy_id, execution_prices):
''',
    '''        for symbol in ledger.sleeve_exposures_at(definition.strategy_id, decision_prices):
''')
replace_once(
    "src/quant/desk/desk.py",
    '''        verdict = evaluate_risk(ledger, definition.strategy_id, target_notional, self.limits,
                                execution_prices)
''',
    '''        verdict = evaluate_risk(ledger, definition.strategy_id, target_notional, self.limits,
                                decision_prices)
''')
replace_once(
    "src/quant/desk/desk.py",
    '''        # Capacity truncation can move the executed portfolio away from the approved
        # one, so the limits are checked once more on what will actually be applied.
        executed = dict(ledger.sleeve_exposures_at(definition.strategy_id, execution_prices))
        for fill in fills:
            executed[fill["symbol"]] = (executed.get(fill["symbol"], 0.0)
                                        + fill["quantity"] * fill["fill_price"])
        final_prices = dict(execution_prices)
        final_prices.update({fill["symbol"]: fill["fill_price"] for fill in fills})
        final = verify_final(ledger, definition.strategy_id, executed, self.limits, final_prices)
''',
    '''        # Capacity truncation can move the executed portfolio away from the approved
        # one. Build the exact post-fill *quantities*, then value old and new
        # quantity on one final vector. Mixing the unimpacted open for the old
        # sleeve with fill prices for the delta makes project() subtract a
        # different state from the one being added.
        final_prices = dict(execution_prices)
        final_prices.update({fill["symbol"]: fill["fill_price"] for fill in fills})
        quantities = {symbol: position.quantity
                      for symbol, position in ledger.sleeves.get(definition.strategy_id, {}).items()
                      if position.quantity}
        for fill in fills:
            quantities[fill["symbol"]] = quantities.get(fill["symbol"], 0.0) + fill["quantity"]
        executed = {symbol: quantity * final_prices[symbol]
                    for symbol, quantity in quantities.items()
                    if abs(quantity) > 1e-9 and symbol in final_prices}
        commission_total = sum(fill["commission"] for fill in fills)
        final = verify_final(ledger, definition.strategy_id, executed, self.limits, final_prices,
                             nav_adjustment=-commission_total)
''')
replace_once(
    "src/quant/desk/desk.py",
    '''                      commission=sum(fill["commission"] for fill in fills),
''',
    '''                      commission=commission_total,
''')

# -------------------------------------------------------------------------
# Book: a same-session restatement replaces economic history, so a superseded
# high mark must not survive as a phantom peak and distort future drawdown.
# -------------------------------------------------------------------------
replace_once(
    "src/quant/book/ledger.py",
    '''        self.state.last_session_date = date
        self.state.peak_nav = max(self.state.peak_nav, nav)
        point = {"date": date, "nav": nav, "cash": self.state.cash,
''',
    '''        self.state.last_session_date = date
        point = {"date": date, "nav": nav, "cash": self.state.cash,
''')
replace_once(
    "src/quant/book/ledger.py",
    '''        else:
            self.state.sessions += 1
            self.state.nav_history.append(point)
        self.save()
''',
    '''        else:
            self.state.sessions += 1
            self.state.nav_history.append(point)
        # Peak NAV is derived from the authoritative history. This is essential
        # when the current session is restated: a superseded intraday/synthetic
        # mark may not continue to throttle future risk.
        self.state.peak_nav = max(
            [self.state.initial_capital]
            + [float(item["nav"]) for item in self.state.nav_history])
        self.save()
''')

# -------------------------------------------------------------------------
# Control Plane: dataset appends extend SHADOW; they do not buy another pass
# over a frozen discovery/validation cohort. Historical rewrites become durable
# integrity blocks. The terminal close waits until an execution session exists.
# Research finalization is committed in crash-safe order.
# -------------------------------------------------------------------------
replace_once(
    "src/quant/clock.py",
    '''from .dataplane.panel import PricePanel  # noqa: E402
''',
    '''from .dataplane.panel import PricePanel, Window  # noqa: E402
''')
replace_once(
    "src/quant/clock.py",
    '''        for task in self.queue.tasks.values():
            if task.status != "BLOCKED" or not task.required_resources:
                continue
            if not self.datasets.missing_for(task.required_resources):
''',
    '''        for task in self.queue.tasks.values():
            if task.status != "BLOCKED" or not task.required_resources:
                continue
            if task.metadata.get("integrity_block"):
                continue
            if not self.datasets.missing_for(task.required_resources):
''')
replace_once(
    "src/quant/clock.py",
    '''    def _reactivate_changed_research(self, changed: list[Any]) -> list[str]:
        """Wake completed research on genuinely new available dataset versions."""
        available = {record.dataset_id: record for record in changed
                     if record.availability == "AVAILABLE"}
        reactivated: list[str] = []
        for task in self.queue.tasks.values():
            if task.status != "COMPLETED" or self.dataset_id not in task.required_resources:
                continue
            record = available.get(self.dataset_id)
            if record is None or task.data_fingerprint == record.fingerprint:
                continue
            history = task.metadata.setdefault("execution_history", [])
            if task.metadata.get("result") is not None:
                history.append({"fingerprint": task.data_fingerprint,
                                "result": task.metadata["result"],
                                "completed_at": task.updated_at})
            task.data_fingerprint = record.fingerprint
            task.status = "PENDING"
            task.updated_at = utc_now()
            reactivated.append(task.task_id)
        if reactivated:
            self.queue.save()
        return reactivated
''',
    '''    def _frozen_cohort_rows(self, panel: PricePanel) -> list[dict[str, Any]] | None:
        partition = self.strategies.research_partition(self.dataset_id)
        if not partition:
            return None
        validation_end = partition["VALIDATION"]["end"]
        visible = panel.restrict(end=validation_end)
        return [dict(bar) for (date, symbol), bar in sorted(visible.bars.items())
                if date <= validation_end and symbol in self.universe]

    def _reactivate_changed_research(self, changed: list[Any]) -> list[str]:
        """React to data versions by scientific cohort, not whole-file fingerprint.

        Appends beyond the frozen validation boundary are new forward/shadow
        evidence and must not rerun the same historical experiment. A rewrite
        *inside* the frozen cohort invalidates lineage and blocks review rather
        than silently buying a new experiment.
        """
        available = {record.dataset_id: record for record in changed
                     if record.availability == "AVAILABLE"}
        record = available.get(self.dataset_id)
        if record is None:
            return []
        panel = self.panel()
        rows = self._frozen_cohort_rows(panel) if panel is not None else None
        cohort_match = (self.strategies.verify_research_cohort(self.dataset_id, rows)
                        if rows is not None else None)
        reactivated: list[str] = []
        mutated = False
        for task in self.queue.tasks.values():
            if task.status != "COMPLETED" or self.dataset_id not in task.required_resources:
                continue
            if task.data_fingerprint == record.fingerprint:
                continue
            if cohort_match is True:
                # The science did not change. Advance only the observed data
                # fingerprint so future boots do not rediscover the same append.
                task.data_fingerprint = record.fingerprint
                task.updated_at = utc_now()
                mutated = True
                continue
            if cohort_match is False:
                task.status = "BLOCKED"
                task.blocked_reason = f"historical research cohort changed for {self.dataset_id}"
                task.metadata["integrity_block"] = True
                task.updated_at = utc_now()
                mutated = True
                self.log.emit("RESEARCH", "RESEARCH", "research_lineage_blocked", task.task_id,
                              severity="FAULT", reason=task.blocked_reason)
                continue
            # No frozen cohort exists yet: a genuinely changed dataset can make
            # the task worth executing. Completed V1 research normally has a
            # cohort, so this is a pre-freeze compatibility path.
            history = task.metadata.setdefault("execution_history", [])
            if task.metadata.get("result") is not None:
                history.append({"fingerprint": task.data_fingerprint,
                                "result": task.metadata["result"],
                                "completed_at": task.updated_at})
            task.data_fingerprint = record.fingerprint
            task.status = "PENDING"
            task.updated_at = utc_now()
            reactivated.append(task.task_id)
            mutated = True
        if mutated:
            self.queue.save()
        return reactivated
''')
replace_once(
    "src/quant/clock.py",
    '''    def shadow_window(self):
        panel = self.panel()
        if panel is None:
            return None
        return panel.split(WINDOWS, symbols=self.universe)["SHADOW"]

    def _next_desk_session(self) -> tuple[str, str | None] | None:
        panel, window = self.panel(), self.shadow_window()
        if panel is None or window is None:
            return None
        dates = [date for date in panel.aligned_dates(self.universe) if window.contains(date)]
        pending = [date for date in dates
                   if self.state.desk_cursor is None or date > self.state.desk_cursor]
        if not pending:
            return None
        date = pending[0]
        following = pending[1] if len(pending) > 1 else None
        return date, following
''',
    '''    def shadow_window(self):
        panel = self.panel()
        if panel is None:
            return None
        frozen = self.strategies.research_partition(self.dataset_id)
        if not frozen:
            return panel.split(WINDOWS, symbols=self.universe)["SHADOW"]
        dates = panel.aligned_dates(self.universe)
        if not dates:
            return None
        start = frozen["SHADOW"]["start"]
        end = dates[-1]
        if end < start:
            return None
        return Window("SHADOW", start, end)

    def _next_desk_session(self) -> tuple[str, str | None] | None:
        panel, window = self.panel(), self.shadow_window()
        if panel is None or window is None:
            return None
        all_dates = panel.aligned_dates(self.universe)
        positions = {date: index for index, date in enumerate(all_dates)}
        pending = [date for date in all_dates if window.contains(date)
                   and (self.state.desk_cursor is None or date > self.state.desk_cursor)]
        for date in pending:
            index = positions[date]
            if index + 1 < len(all_dates):
                return date, all_dates[index + 1]
        # The final close is information we have, but without a later session
        # there is no executable opportunity yet. Leave it pending for refresh.
        return None
''')
replace_once(
    "src/quant/clock.py",
    '''        task.status = "COMPLETED"
        task.metadata["result"] = result
        task.updated_at = utc_now()
        self.queue.save()
        if task.execution_key not in self.state.completed_work:
            self.state.completed_work.append(task.execution_key)
        self.state.research_runs += 1
        self.learning.record_research(lane_name, task.lane, result)
        self._promote_followup(lane_name, result)
        self.components.set("RESEARCH", "IDLE", f"{task.task_id} closed: {result['outcome']}")
        self.components.set("LEARNING", "RUN", "research lesson recorded")
        self.state.next_action = result.get("next_action_hint") or self._describe_next_action()
        self.heartbeat()
        return "RESEARCH"
''',
    '''        # Persist the worker result while the task is still RUNNING. If
        # learning/control finalization dies, boot will requeue the task and the
        # worker's scientific writes are idempotent by ticket/cohort identity.
        task.metadata["result"] = result
        task.updated_at = utc_now()
        self.queue.save()

        self.learning.record_research(lane_name, task.lane, result)
        self._promote_followup(lane_name, result)
        if task.execution_key not in self.state.completed_work:
            self.state.completed_work.append(task.execution_key)
            self.state.research_runs += 1
        self.components.set("RESEARCH", "IDLE", f"{task.task_id} closed: {result['outcome']}")
        self.components.set("LEARNING", "RUN", "research lesson recorded")
        self.state.next_action = result.get("next_action_hint") or self._describe_next_action()
        # Commit Control state before declaring the queue item terminal. A crash
        # between these writes replays a RUNNING task; completed_work then turns
        # that replay into a no-op instead of losing the control-side outcome.
        self.heartbeat()
        task.status = "COMPLETED"
        task.updated_at = utc_now()
        self.queue.save()
        return "RESEARCH"
''')
replace_once(
    "src/quant/clock.py",
    '''        if self.learning.decision_quality.get("strategies_evaluated", 0):
            return False
        assessments = self.learning.assess_rejections(
''',
    '''        assessments = self.learning.assess_rejections(
''')

# Existing regression whose old assertion encoded whole-file fingerprint replay
# is updated to the stronger frozen-cohort rule.
replace_once(
    "tests/test_quant_system.py",
    '''    def test_new_data_makes_the_same_question_worth_asking_again(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.build(directory)
            system = self.system(root)
            system.boot()
            self.assertEqual(system.tick(), "RESEARCH")
            runs = system.state.research_runs
            task = next(task for task in system.queue.tasks.values()
                        if task.status == "COMPLETED")
            prior = task.metadata["result"]
            self.build(directory, sessions=430)          # the dataset moves on
            resumed = self.system(root)
            resumed.boot()
            refreshed = resumed.queue.tasks[task.task_id]
            self.assertEqual(refreshed.status, "PENDING")
            self.assertEqual(refreshed.metadata["execution_history"][0]["result"], prior)
            resumed.tick()
            self.assertEqual(resumed.state.research_runs, runs + 1)
''',
    '''    def test_append_only_data_extends_shadow_without_repeating_frozen_research(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.build(directory)
            system = self.system(root)
            system.boot()
            self.assertEqual(system.tick(), "RESEARCH")
            runs = system.state.research_runs
            task = next(task for task in system.queue.tasks.values()
                        if task.status == "COMPLETED")
            self.build(directory, sessions=430)          # append-only forward data
            resumed = self.system(root)
            resumed.boot()
            refreshed = resumed.queue.tasks[task.task_id]
            self.assertEqual(refreshed.status, "COMPLETED")
            self.assertEqual(resumed.state.research_runs, runs)
''')

# Isolate the commission/NAV test from the independent drawdown halt.
replace_once(
    "tests/test_v1_red_team.py",
    '''            limits = RiskLimits(min_nav_ratio=0.50, max_net_ratio=1.0,
                                max_gross_ratio=5.0, max_symbol_ratio=1.0)
''',
    '''            limits = RiskLimits(min_nav_ratio=0.50, max_net_ratio=1.0,
                                max_gross_ratio=5.0, max_symbol_ratio=1.0,
                                drawdown_halt=-1.0, drawdown_throttle=-1.0)
''')

# Durable regression for the independently found stale-peak defect.
replace_once(
    "tests/test_v1_red_team.py",
    '''class LearningRefreshTests(unittest.TestCase):
''',
    '''class LedgerRestatementTests(unittest.TestCase):
    def test_same_session_restatement_cannot_leave_a_phantom_peak(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / "book.json", initial_capital=100.0)
            ledger.apply_fill("AAA", 1.0, 10.0, 0.0, "2025-01-01", "S", "fill")
            ledger.mark_to_market("2025-01-01", {"AAA": 30.0})
            self.assertEqual(ledger.state.peak_nav, 120.0)
            ledger.mark_to_market("2025-01-01", {"AAA": 10.0})
            self.assertEqual(ledger.state.nav_history[-1]["nav"], 100.0)
            self.assertEqual(ledger.state.peak_nav, 100.0)
            self.assertAlmostEqual(ledger.drawdown, 0.0)


class LearningRefreshTests(unittest.TestCase):
''')

# Remove one-shot tooling from the resulting review diff.
for relative in ("scripts/red_team_integrity_patch.py",
                 ".github/workflows/red-team-apply-integrity.yml"):
    path = ROOT / relative
    if path.exists():
        path.unlink()
