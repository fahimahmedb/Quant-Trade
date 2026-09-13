from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one replacement, found {count}")
    target.write_text(text.replace(old, new), encoding="utf-8")


# Desk decisions at close(t) may not consume execution information from open(t+1).
replace_once(
    "src/quant/desk/desk.py",
    '''        execution_prices = ({symbol: panel.adjusted(next_date, symbol, "open")
                             for symbol in panel.symbols if next_date and panel.has(next_date, symbol)})
''',
    '''        decision_prices = {symbol: panel.adjusted(date, symbol, "close")
                           for symbol in panel.symbols if panel.has(date, symbol)}
        execution_prices = ({symbol: panel.adjusted(next_date, symbol, "open")
                             for symbol in panel.symbols if next_date and panel.has(next_date, symbol)})
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
    '''        executed = dict(ledger.sleeve_exposures_at(definition.strategy_id, execution_prices))
        for fill in fills:
            executed[fill["symbol"]] = (executed.get(fill["symbol"], 0.0)
                                        + fill["quantity"] * fill["fill_price"])
        final_prices = dict(execution_prices)
        final_prices.update({fill["symbol"]: fill["fill_price"] for fill in fills})
        final = verify_final(ledger, definition.strategy_id, executed, self.limits, final_prices)
''',
    '''        final_prices = dict(execution_prices)
        final_prices.update({fill["symbol"]: fill["fill_price"] for fill in fills})
        # Existing and newly executed quantity must be valued on one coherent
        # post-fill price vector. Otherwise the final RISK check subtracts the
        # old sleeve at one basis and adds it back at another.
        executed = dict(ledger.sleeve_exposures_at(definition.strategy_id, final_prices))
        for fill in fills:
            executed[fill["symbol"]] = (executed.get(fill["symbol"], 0.0)
                                        + fill["quantity"] * final_prices[fill["symbol"]])
        final = verify_final(
            ledger, definition.strategy_id, executed, self.limits, final_prices,
            nav_adjustment=-sum(fill["commission"] for fill in fills))
''')

# The Control Plane must distinguish append-only forward evidence from a rewrite
# of the frozen research cohort, keep the terminal close pending until it can
# execute, and commit research as a transaction rather than a loose sequence.
replace_once(
    "src/quant/clock.py",
    '''from .dataplane.panel import PricePanel  # noqa: E402
''',
    '''from .dataplane.panel import PricePanel, Window  # noqa: E402
''')
replace_once(
    "src/quant/clock.py",
    '''    def _unblock_dependencies(self) -> list[str]:
        """A dataset becoming available is what makes blocked work executable."""
        unblocked = []
        for task in self.queue.tasks.values():
            if task.status != "BLOCKED" or not task.required_resources:
                continue
            if not self.datasets.missing_for(task.required_resources):
                task.status = "PENDING"
                task.blocked_reason = None
                task.updated_at = utc_now()
                unblocked.append(task.task_id)
                self.log.emit("CONTROL", "CONTROL", "dependency_resolved", task.task_id,
                              resources=task.required_resources)
        if unblocked:
            self.queue.save()
        return unblocked
''',
    '''    def _unblock_dependencies(self) -> list[str]:
        """A dataset becoming available is what makes blocked work executable.

        A frozen-cohort integrity block is different: the bytes are available,
        but their history contradicts the evidence already registered. Only a
        later cohort verification may clear that review boundary.
        """
        unblocked = []
        for task in self.queue.tasks.values():
            if task.status != "BLOCKED" or not task.required_resources:
                continue
            if task.metadata.get("integrity_block"):
                continue
            if not self.datasets.missing_for(task.required_resources):
                task.status = "PENDING"
                task.blocked_reason = None
                task.updated_at = utc_now()
                unblocked.append(task.task_id)
                self.log.emit("CONTROL", "CONTROL", "dependency_resolved", task.task_id,
                              resources=task.required_resources)
        if unblocked:
            self.queue.save()
        return unblocked
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
    '''    def _reactivate_changed_research(self, changed: list[Any]) -> list[str]:
        """React to a new dataset version without recycling frozen science.

        Once Discovery/Validation are frozen, an append belongs to forward
        SHADOW evidence and must not buy another historical experiment. A change
        inside the frozen cohort is stronger: it blocks the lineage for review.
        """
        available = {record.dataset_id: record for record in changed
                     if record.availability == "AVAILABLE"}
        record = available.get(self.dataset_id)
        if record is None:
            return []

        frozen = self.strategies.research_partition(self.dataset_id)
        cohort_check: bool | None = None
        if frozen and self.strategies.research_cohorts.get(self.dataset_id):
            panel = PricePanel.load(self.paths.root / record.path)
            validation_end = frozen["VALIDATION"]["end"]
            rows = [dict(bar) for (date, symbol), bar in sorted(panel.bars.items())
                    if date <= validation_end and symbol in self.universe]
            cohort_check = self.strategies.verify_research_cohort(self.dataset_id, rows)

        if cohort_check is False:
            reason = f"historical research cohort changed for {self.dataset_id}"
            changed_state = False
            for task in self.queue.tasks.values():
                if task.worker != "research_lane" or self.dataset_id not in task.required_resources:
                    continue
                if not task.metadata.get("integrity_block"):
                    task.metadata["pre_integrity_status"] = task.status
                task.metadata["integrity_block"] = True
                task.status = "BLOCKED"
                task.blocked_reason = reason
                task.updated_at = utc_now()
                changed_state = True
            if changed_state:
                self.queue.save()
                self.log.emit("DATA", "RESEARCH", "research_lineage_blocked", self.dataset_id,
                              severity="FAULT", reason=reason,
                              fingerprint=record.fingerprint)
            return []

        if cohort_check is True:
            changed_state = False
            for task in self.queue.tasks.values():
                if task.worker != "research_lane" or self.dataset_id not in task.required_resources:
                    continue
                if task.metadata.pop("integrity_block", False):
                    task.status = task.metadata.pop("pre_integrity_status", "COMPLETED")
                    task.blocked_reason = None
                    task.updated_at = utc_now()
                    changed_state = True
                if task.status == "COMPLETED" and task.data_fingerprint != record.fingerprint:
                    task.metadata["latest_dataset_fingerprint"] = record.fingerprint
                    changed_state = True
            if changed_state:
                self.queue.save()
            return []

        # Before the first cohort is frozen, a genuinely different dataset can
        # still make a completed question worth asking again.
        reactivated: list[str] = []
        for task in self.queue.tasks.values():
            if task.status != "COMPLETED" or self.dataset_id not in task.required_resources:
                continue
            if task.data_fingerprint == record.fingerprint:
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
        if frozen:
            start = frozen["SHADOW"]["start"]
            dates = [date for date in panel.aligned_dates(self.universe) if date >= start]
            if not dates:
                return None
            return Window("SHADOW", start, dates[-1])
        return panel.split(WINDOWS, symbols=self.universe)["SHADOW"]

    def _next_desk_session(self) -> tuple[str, str | None] | None:
        panel, window = self.panel(), self.shadow_window()
        if panel is None or window is None:
            return None
        aligned = panel.aligned_dates(self.universe)
        index = {date: position for position, date in enumerate(aligned)}
        dates = [date for date in aligned if window.contains(date)]
        pending = [date for date in dates
                   if self.state.desk_cursor is None or date > self.state.desk_cursor]
        for date in pending:
            position = index[date]
            if position + 1 < len(aligned):
                return date, aligned[position + 1]
        # A close with no later execution session is not a decision yet. Keep it
        # pending so the next data arrival can execute from that information set.
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
    '''        # Scientific output may already be durable here. Keep the queue
        # transaction RUNNING until learning/follow-up side effects are durable,
        # so a process death requeues the work instead of creating a false terminal.
        task.metadata["result"] = result
        task.updated_at = utc_now()
        self.queue.save()
        self.learning.record_research(lane_name, task.lane, result)
        self._promote_followup(lane_name, result)
        if task.execution_key not in self.state.completed_work:
            self.state.completed_work.append(task.execution_key)
            self.state.research_runs += 1
        self.state.next_action = result.get("next_action_hint") or self._describe_next_action()
        # Persist the Control-side commit before marking the queue terminal. If
        # the process dies after this write, dead-work detection closes the task
        # without repeating the scientific transaction.
        self.save()
        task.status = "COMPLETED"
        task.updated_at = utc_now()
        self.queue.save()
        self.components.set("RESEARCH", "IDLE", f"{task.task_id} closed: {result['outcome']}")
        self.components.set("LEARNING", "RUN", "research lesson recorded")
        self.heartbeat()
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

# The old baseline test treated a pure append as a reason to rerun historical
# research. Frozen partitions make that expectation an integrity regression.
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
    '''    def test_append_only_data_extends_shadow_without_repeating_research(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.build(directory)
            system = self.system(root)
            system.boot()
            self.assertEqual(system.tick(), "RESEARCH")
            runs = system.state.research_runs
            task = next(task for task in system.queue.tasks.values()
                        if task.status == "COMPLETED")
            self.build(directory, sessions=430)          # deterministic append only
            resumed = self.system(root)
            resumed.boot()
            refreshed = resumed.queue.tasks[task.task_id]
            self.assertEqual(refreshed.status, "COMPLETED")
            self.assertEqual(resumed.state.research_runs, runs)
''')

# Isolate the NAV-floor assertion from the independent drawdown halt.
replace_once(
    "tests/test_v1_red_team.py",
    '''            limits = RiskLimits(min_nav_ratio=0.50, max_net_ratio=1.0,
                                max_gross_ratio=5.0, max_symbol_ratio=1.0)
''',
    '''            limits = RiskLimits(min_nav_ratio=0.50, max_net_ratio=1.0,
                                max_gross_ratio=5.0, max_symbol_ratio=1.0,
                                drawdown_halt=-0.75, drawdown_throttle=-0.70)
''')

print("integrity patches applied")
