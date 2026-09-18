"""Control Plane: the Clock.

This is the object that makes Quant one system rather than several subsystems
in one repository. It owns system lifetime, chooses what is due, routes work to
the plane that can do it, keeps component state honest and survives restarts.

``IDLE`` means alive with nothing due. It never means finished.
"""

from __future__ import annotations

import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from autonomous_research.runtime import PersistentQueue, ResearchTask  # noqa: E402
from autonomous_research.watchdog import is_lease_stale  # noqa: E402

from .dataplane.ingest import SECTOR_DATASET, SECTOR_UNIVERSE  # noqa: E402
from .dataplane.panel import PricePanel, Window  # noqa: E402
from .dataplane.registry import DatasetRegistry  # noqa: E402
from .dataplane.sec.collector import SecForm4Collector  # noqa: E402
from .dataplane.sec.timebase import Timebase  # noqa: E402
from .desk.desk import CapitalDesk  # noqa: E402
from .events import EventLog  # noqa: E402
from .factory.lanes import FOLLOWUP, WINDOWS, lane_definitions  # noqa: E402
from .factory.strategies import StrategyRegistry  # noqa: E402
from .factory.workers import ResearchContext, run_lane  # noqa: E402
from .learning.store import BuildTask, LearningStore  # noqa: E402
from .paths import QuantPaths  # noqa: E402
from .state import (ComponentRegistry, parse_ts, read_json, read_jsonl,  # noqa: E402
                     utc_now, write_json)


HEARTBEAT_TIMEOUT_SECONDS = 900
MAX_TASK_ATTEMPTS = 3
#: How long a worker may hold a task before its lease is considered stale.
TASK_LEASE_SECONDS = 600
#: Default wait between wake-ups when the system is IDLE.
IDLE_POLL_SECONDS = 60.0


class Timer:
    """Injectable clock source. Tests substitute one that never really sleeps."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)


class _TimerTimebase(Timebase):
    """Give the capture lane the Control Plane's clock, not a second one.

    The lane declares its own time contract to avoid an import cycle; this
    adapter makes sure a test that controls the system clock also controls
    capture cadence, backoff and cooldown.
    """

    def __init__(self, timer: Timer):
        self.timer = timer

    def now(self) -> datetime:
        return self.timer.now()

    def sleep(self, seconds: float) -> None:
        self.timer.sleep(seconds)


@dataclass
class ControlState:
    system_id: str = "quant-system-v1"
    status: str = "IDLE"
    mode: str = "paper_shadow"
    created_at: str = field(default_factory=utc_now)
    last_boot_at: str | None = None
    last_heartbeat: str = field(default_factory=utc_now)
    boots: int = 0
    ticks: int = 0
    waits: int = 0
    last_wake_at: str | None = None
    research_runs: int = 0
    desk_sessions: int = 0
    desk_cursor: str | None = None
    #: Execution identities (task@dataset-fingerprint) already completed. Work is
    #: only repeated when the evidence underneath it has changed.
    completed_work: list[str] = field(default_factory=list)
    next_action: str | None = None
    pause_reason: str | None = None
    faults: list[dict[str, Any]] = field(default_factory=list)
    run_history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class QuantSystem:
    """The whole system, addressable from one object."""

    def __init__(self, root: Path, initial_capital: float = 1_000_000.0,
                 universe: list[str] | None = None, dataset_id: str = SECTOR_DATASET,
                 timer: Timer | None = None):
        self.paths = QuantPaths(Path(root)).ensure()
        self.timer = timer or Timer()
        self.universe = universe or SECTOR_UNIVERSE
        self.dataset_id = dataset_id
        self.log = EventLog(self.paths.events)
        self.components = ComponentRegistry(self.paths.components)
        self.datasets = DatasetRegistry(self.paths.dataset_registry, self.paths.root)
        self.strategies = StrategyRegistry(self.paths.strategies)
        self.learning = LearningStore(self.paths.learning)
        self.queue = PersistentQueue(self.paths.work_queue)
        self.desk = CapitalDesk(self.paths, self.strategies, self.datasets, self.log,
                                self.components, initial_capital=initial_capital)
        # The P0 SEC capture lane is owned by the Control Plane rather than by a
        # separate process, so its lifecycle, liveness and restart behaviour are
        # the ones the rest of the system already proves. It fails closed when
        # the SEC-required identity is absent: BLOCKED, never a request.
        self.sec = SecForm4Collector(self.paths, timebase=_TimerTimebase(self.timer),
                                     root=self.paths.root, emit=self.log.emit)
        payload = read_json(self.paths.control)
        self.state = ControlState(**payload) if payload else ControlState()
        self._panel: PricePanel | None = None
        self._panel_fingerprint: str | None = None

    # --- persistence -------------------------------------------------------
    def save(self) -> None:
        self.state.last_heartbeat = utc_now()
        write_json(self.paths.control, self.state.to_dict())

    def heartbeat(self) -> None:
        self.save()

    # --- lifecycle ---------------------------------------------------------
    def boot(self) -> dict[str, Any]:
        """Resume the same system. Never create a new world."""
        self.state.boots += 1
        self.state.last_boot_at = utc_now()
        self.components.set("CONTROL", "RUN", "booting")
        recovered = self._recover_interrupted()
        arrived = self.datasets.reload()
        changed = self.datasets.refresh_availability()
        # Task fingerprints are the durable comparison point.  The registry
        # may already contain the new version when this process is constructed,
        # so do not depend solely on an in-memory "changed" notification.
        refresh_records = self.datasets.available()
        refreshed = self._reactivate_changed_research(refresh_records)
        unblocked = self._unblock_dependencies()
        seeded = self._seed_work()
        self.log.emit("CONTROL", "CONTROL", "system_boot", self.state.system_id,
                      boot=self.state.boots, recovered=recovered,
                      datasets_changed=[record.dataset_id for record in changed],
                      research_reactivated=refreshed,
                      unblocked=unblocked, seeded=seeded,
                      resumed_desk_cursor=self.state.desk_cursor,
                      book_nav=self.desk.capital.nav)
        # Bind this process's externally attested lifecycle before any capture
        # work runs, so the observation audit can attribute every subsequent
        # scheduler transition to a known service instance.
        lifecycle = self.sec.record_service_start()
        self.state.next_action = self._describe_next_action()
        self.components.set("CONTROL", "IDLE", "booted")
        self.save()
        return {"boot": self.state.boots, "recovered": recovered, "seeded": seeded,
                "unblocked": unblocked, "next_action": self.state.next_action,
                "sec_lifecycle_cause": lifecycle["lifecycle_cause"],
                "sec_boot_id": lifecycle["boot_id"],
                "sec_acquisition_fingerprint": lifecycle[
                    "acquisition_critical_fingerprint"]}

    def _recover_interrupted(self) -> list[str]:
        recovered = []
        for task in self.queue.tasks.values():
            if task.status == "RUNNING":
                task.status = "PENDING"
                task.last_error = "process stopped while the worker was running; requeued"
                task.updated_at = utc_now()
                recovered.append(task.task_id)
            elif task.status == "FAILED" and task.attempts < MAX_TASK_ATTEMPTS:
                # A fault is retried on a fresh process, not in the loop that
                # produced it, and only while the attempt budget allows.
                task.status = "PENDING"
                task.updated_at = utc_now()
                recovered.append(task.task_id)
        if recovered:
            self.queue.save()
            self.log.emit("CONTROL", "CONTROL", "work_recovered", ", ".join(recovered),
                          severity="WARN", tasks=recovered)
        for name, status in self.components.statuses.items():
            if status.state == "RUN":
                self.components.set(name, "IDLE", "reset by restart recovery")
        return recovered

    def _unblock_dependencies(self) -> list[str]:
        """A dataset becoming available is what makes blocked work executable."""
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

    def _reactivate_changed_research(self, changed: list[Any]) -> list[str]:
        """Classify changed bytes against the frozen scientific cohort.

        Appends after Validation are forward evidence and must not buy another
        historical experiment. A changed value inside the frozen cohort blocks
        research and Desk progression until explicit review.
        """
        record = self.datasets.get(self.dataset_id)
        if record is None or record.availability != "AVAILABLE":
            return []
        status = self._frozen_cohort_status()
        touched: list[str] = []
        if status is False:
            reason = "historical research cohort changed; review required"
            for task in self.queue.tasks.values():
                if task.worker != "research_lane" or self.dataset_id not in task.required_resources:
                    continue
                task.status = "BLOCKED"
                task.blocked_reason = reason
                task.metadata["integrity_block"] = True
                task.updated_at = utc_now()
                touched.append(task.task_id)
            if touched:
                self.queue.save()
                self.components.set("RESEARCH", "BLOCKED", reason)
                self.log.emit("DATA", "RESEARCH", "research_cohort_changed",
                              self.dataset_id, severity="FAULT", tasks=touched)
            return touched
        if status is True:
            # Restoring the exact frozen cohort clears an integrity block, but a
            # forward append alone never reactivates completed science.
            for task in self.queue.tasks.values():
                if not task.metadata.pop("integrity_block", False):
                    continue
                task.blocked_reason = None
                task.status = "COMPLETED" if task.metadata.get("result") else "PENDING"
                task.updated_at = utc_now()
                touched.append(task.task_id)
            if touched:
                self.queue.save()
        return touched

    def _seed_work(self) -> list[str]:
        """Declare the research lanes, and preserve the lanes still genuinely blocked."""
        seeded = []
        definitions = lane_definitions(self.universe, self.dataset_id)
        for lane_name, definition in definitions.items():
            if lane_name == FOLLOWUP.get("xs_daily_relative_value") and lane_name not in (
                    task.metadata.get("lane_name") for task in self.queue.tasks.values()):
                continue  # promoted by evidence, not seeded blindly
            task_id = f"RESEARCH-{lane_name.upper().replace('_', '-')}"
            if task_id in self.queue.tasks:
                continue
            missing = self.datasets.missing_for([self.dataset_id])
            task = ResearchTask(
                task_id=task_id, lane=definition["lane"], priority=definition["priority"],
                reason=definition["question"], worker="research_lane",
                required_resources=[self.dataset_id],
                status="BLOCKED" if missing else "PENDING",
                blocked_reason=f"dataset unavailable: {missing}" if missing else None,
                data_fingerprint=(record.fingerprint
                                  if (record := self.datasets.get(self.dataset_id)) else None),
                metadata={"lane_name": lane_name})
            if self.queue.add(task):
                seeded.append(task_id)
        for entry in self._legacy_blocked_lanes():
            if entry["task_id"] not in self.queue.tasks and self.queue.add(ResearchTask(**{
                    key: value for key, value in entry.items() if key != "capability"})):
                seeded.append(entry["task_id"])
                self.learning.raise_build_task(BuildTask(
                    task_id=f"BUILD-{entry['task_id']}", capability=entry["capability"],
                    reason=entry["blocked_reason"],
                    affected_subsystems=entry.get("affected_subsystems", ["DATA", "RESEARCH"]),
                    acceptance=entry.get(
                        "acceptance",
                        f"a validated, fingerprinted dataset unblocks {entry['task_id']}"
                    ),
                    priority=entry["priority"]))
        return seeded

    def _legacy_blocked_lanes(self) -> list[dict[str, Any]]:
        """Research lanes the repository ranked but cannot execute without new data."""
        path = self.paths.root / "research" / "opportunity_map.json"
        payload = read_json(path)
        if not payload:
            return []
        entries = []
        for lane in payload["lanes"]:
            if lane["lane"] in {"statistical_arbitrage", "time_series_relative_value"}:
                continue  # now executable, or already carried by the legacy worker
            entry = {
                "task_id": f"SCAN-{lane['lane'].upper().replace('_', '-')}-001",
                "lane": lane["lane"], "priority": float(lane["total"]),
                "reason": f"ranked research lane: {lane['decision']}",
                "worker": "unavailable_data", "required_resources": [lane["lane"] + "_panel"],
                "status": "BLOCKED", "blocked_reason": lane["constraint"],
                "capability": f"point-in-time dataset for the {lane['lane']} lane",
            }
            if lane["lane"] == "insider_filings":
                entry.update({
                    "worker": "unavailable_scientific_protocol",
                    "required_resources": [],
                    "capability": (
                        "authorized parsing / qualification / scientific admissibility path "
                        "for the insider_filings lane"
                    ),
                    "acceptance": (
                        "an authorized downstream Form-4 protocol can consume captured raw "
                        "evidence without violating the P0 visibility firewall"
                    ),
                    "affected_subsystems": ["DATA", "RESEARCH"],
                })
            entries.append(entry)
        return entries

    # --- data --------------------------------------------------------------
    def panel(self) -> PricePanel | None:
        record = self.datasets.get(self.dataset_id)
        if record is None or record.availability != "AVAILABLE":
            return None
        if self._panel is None or self._panel_fingerprint != record.fingerprint:
            self._panel = PricePanel.load(self.paths.root / record.path)
            self._panel_fingerprint = record.fingerprint
        return self._panel

    def _research_cohort_rows(self) -> list[dict[str, Any]] | None:
        panel = self.panel()
        frozen = self.strategies.research_partition(self.dataset_id)
        if panel is None or frozen is None:
            return None
        end = frozen["VALIDATION"]["end"]
        visible = panel.restrict(end=end)
        return [dict(bar) for (date, symbol), bar in sorted(visible.bars.items())
                if date <= end and symbol in self.universe]

    def _frozen_cohort_status(self) -> bool | None:
        rows = self._research_cohort_rows()
        if rows is None:
            return None
        return self.strategies.verify_research_cohort(self.dataset_id, rows)

    def shadow_window(self):
        panel = self.panel()
        if panel is None:
            return None
        frozen = self.strategies.research_partition(self.dataset_id)
        if frozen is None:
            return panel.split(WINDOWS, symbols=self.universe)["SHADOW"]
        start = frozen["SHADOW"]["start"]
        dates = [date for date in panel.aligned_dates(self.universe) if date >= start]
        return Window("SHADOW", start, dates[-1]) if dates else None

    def _next_desk_session(self) -> tuple[str, str | None] | None:
        panel, window = self.panel(), self.shadow_window()
        if panel is None or window is None or self._frozen_cohort_status() is False:
            return None
        dates = [date for date in panel.aligned_dates(self.universe) if window.contains(date)]
        pending = [date for date in dates
                   if self.state.desk_cursor is None or date > self.state.desk_cursor]
        # close(t) is a decision point only once open(t+1) actually exists. Leave
        # the terminal close pending so an append can make it executable later.
        if len(pending) < 2:
            return None
        return pending[0], pending[1]

    # --- the tick ----------------------------------------------------------
    def tick(self) -> str:
        """Advance the system by one unit of due work."""
        self.state.ticks += 1
        if self.state.status == "PAUSED" and self.state.pause_reason:
            self.components.set("CONTROL", "PAUSED", self.state.pause_reason)
            self.heartbeat()
            return "PAUSED"

        # Acquisition goes first. A missed SEC discovery window is irrecoverable:
        # the feed is a rolling window and a filing that leaves it cannot be
        # re-observed at the time it was published. Research and desk work run
        # over committed, fingerprinted data and are replayable at any later
        # tick, so they must never starve the capture lane.
        capture = self._run_due_capture()
        if capture is not None:
            return capture

        task = self.queue.next_due()
        if task is not None:
            return self._run_task(task)

        session = self._next_desk_session()
        if session is not None:
            return self._run_desk_session(*session)

        if self._assess_decision_quality():
            return "LEARNED"

        return self._idle()

    def _run_due_capture(self) -> str | None:
        """Advance the SEC capture lane by one unit of work, if any is due.

        A queued filing is drained before a new poll is started, so a backlog is
        worked off at the frozen rate rather than growing behind fresh discovery.
        """
        collector = self.sec
        if not collector.configured or not collector.state.enabled:
            return None
        try:
            return self._capture_step(collector)
        except Exception as exc:
            # A capture fault must not kill the system, and must not be mistaken
            # for a quiet poll. The attempt journal already holds whatever was
            # durably recorded before the fault.
            detail = f"{type(exc).__name__}: {exc}"
            self.components.set("SEC_CAPTURE", "FAULT", detail[:200])
            self.state.faults.append({"at": utc_now(), "task": "SEC_CAPTURE",
                                      "error": detail[:200]})
            self.log.emit("DATA", "SEC_CAPTURE", "capture_fault",
                          collector.store.collector_version, severity="FAULT",
                          error_class=type(exc).__name__)
            self.heartbeat()
            return "SEC_FAULT"

    def _capture_step(self, collector: SecForm4Collector) -> str | None:
        if collector.has_pending_work():
            self.components.set("SEC_CAPTURE", "RUN", "acquiring a queued filing")
            outcomes = collector.drain()
            self.state.status = "RUN"
            state, detail = collector.component_state()
            self.components.set("SEC_CAPTURE", state, detail)
            self.heartbeat()
            return "SEC_CAPTURE" if outcomes else None
        if collector.poll_due():
            self.components.set("SEC_CAPTURE", "RUN", "polling SEC discovery")
            outcome = collector.poll()
            self.state.status = "RUN"
            state, detail = collector.component_state()
            self.components.set("SEC_CAPTURE", state, detail)
            self.heartbeat()
            return f"SEC_DISCOVERY_{outcome.result_state}"
        day = collector.reconciliation_due()
        if day is not None:
            self.components.set("SEC_CAPTURE", "RUN", "reconciling a closed day")
            result = collector.reconcile(day)
            self.state.status = "RUN"
            state, detail = collector.component_state()
            self.components.set("SEC_CAPTURE", state, detail)
            self.heartbeat()
            return f"SEC_RECONCILE_{result['result_state']}"
        return None

    def _idle(self) -> str:
        self.state.status = "IDLE"
        blocked = [task for task in self.queue.tasks.values() if task.status == "BLOCKED"]
        self.components.set("CONTROL", "IDLE", "no work due")
        self.components.set("RESEARCH", "BLOCKED" if blocked else "IDLE",
                            blocked[0].blocked_reason if blocked else "no research due")
        # The desk stages hold the state of the last session they ran. Once no
        # session is due they are idle, and saying so keeps the surface honest.
        for name in ("SCAN", "VET", "SIZE", "RISK", "FILLS"):
            self.components.set(name, "IDLE", "no session due")
        self.components.set("BOOK", "RUN" if self.desk.capital.open_positions() else "IDLE",
                            f"marked through {self.desk.capital.state.last_session_date}")
        self.components.set("DATA", "IDLE" if self.datasets.health()["healthy"] else "BLOCKED",
                            f"{len(self.datasets.available())} datasets available")
        capture_state, capture_detail = self.sec.component_state()
        self.components.set("SEC_CAPTURE", capture_state, capture_detail)
        self.components.set("LEARNING", "IDLE",
                            f"{len(self.learning.lessons)} lessons recorded")
        self.components.set("BUILD", "BLOCKED" if self.learning.open_build_tasks() else "IDLE",
                            f"{len(self.learning.open_build_tasks())} open capability gaps")
        self.state.next_action = self._describe_next_action()
        self.heartbeat()
        return "IDLE"

    def _run_task(self, task: ResearchTask) -> str:
        if task.worker != "research_lane":
            task.status = "BLOCKED"
            task.blocked_reason = task.blocked_reason or f"no worker named {task.worker}"
            task.updated_at = utc_now()
            self.queue.save()
            return self.tick()
        missing = self.datasets.missing_for(task.required_resources)
        if missing:
            task.status = "BLOCKED"
            task.blocked_reason = f"dataset unavailable: {missing}"
            self.queue.save()
            self.components.set("RESEARCH", "BLOCKED", task.blocked_reason)
            return self.tick()
        record = self.datasets.get(self.dataset_id)
        cohort_status = self._frozen_cohort_status()
        if cohort_status is False:
            task.status = "BLOCKED"
            task.blocked_reason = "historical research cohort changed; review required"
            task.metadata["integrity_block"] = True
            task.updated_at = utc_now()
            self.queue.save()
            self.components.set("RESEARCH", "BLOCKED", task.blocked_reason)
            self.heartbeat()
            return "BLOCKED"
        if record is not None and cohort_status is None and task.data_fingerprint != record.fingerprint:
            task.data_fingerprint = record.fingerprint
        if task.execution_key in self.state.completed_work:
            # Repeating an identical test on identical data buys no information and
            # would inflate the multiple-testing trial count, making the next real
            # result harder to accept for no reason.
            task.status = "COMPLETED"
            task.updated_at = utc_now()
            self.queue.save()
            self.log.emit("RESEARCH", "RESEARCH", "dead_work_skipped", task.task_id,
                          execution_key=task.execution_key)
            return self.tick()

        self.state.status = "RUN"
        task.status = "RUNNING"
        task.attempts += 1
        task.started_at = utc_now()
        task.lease_seconds = TASK_LEASE_SECONDS
        task.updated_at = utc_now()
        self.queue.save()
        self.components.set("RESEARCH", "RUN", task.task_id)
        self.save()

        lane_name = task.metadata["lane_name"]
        context = ResearchContext(self.paths, self.datasets, self.strategies, self.log)
        try:
            result = run_lane(context, lane_name, self.universe, self.dataset_id)
        except Exception as exc:  # A worker fault must not kill the system.
            integrity = isinstance(exc, ValueError) and "historical research cohort changed" in str(exc)
            task.status = "BLOCKED" if integrity else "FAILED"
            task.blocked_reason = str(exc) if integrity else None
            task.last_error = f"{type(exc).__name__}: {exc}"
            task.updated_at = utc_now()
            self.queue.save()
            fault = {"at": utc_now(), "task": task.task_id, "error": task.last_error}
            self.state.faults.append(fault)
            self.components.set("RESEARCH", "FAULT", task.last_error)
            self.log.emit("RESEARCH", "RESEARCH", "worker_fault", task.task_id,
                          severity="FAULT", error=task.last_error,
                          data_integrity=integrity)
            self.heartbeat()
            return "FAULT"

        # Persist the worker result while the task is still RUNNING. A crash
        # anywhere below is therefore recoverable rather than falsely terminal.
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
        # completed_work is the transaction commit marker and is durable before
        # the queue becomes terminal. A crash after this point is dead-work-safe.
        self.heartbeat()
        task.status = "COMPLETED"
        task.updated_at = utc_now()
        self.queue.save()
        return "RESEARCH"

    def _promote_followup(self, lane_name: str, result: dict[str, Any]) -> None:
        """Turn a diagnosed failure into the next executable action, not a question."""
        successor = FOLLOWUP.get(lane_name)
        if not successor or not result.get("cost_bound"):
            return
        task_id = f"RESEARCH-{successor.upper().replace('_', '-')}"
        if task_id in self.queue.tasks:
            return
        definition = lane_definitions(self.universe, self.dataset_id)[successor]
        record = self.datasets.get(self.dataset_id)
        added = self.queue.add(ResearchTask(
            task_id=task_id, lane=definition["lane"], priority=definition["priority"],
            reason=f"promoted by {lane_name}: {result['next_action_hint']}",
            worker="research_lane", parent=f"RESEARCH-{lane_name.upper().replace('_', '-')}",
            required_resources=[self.dataset_id],
            data_fingerprint=record.fingerprint if record else None,
            metadata={"lane_name": successor}))
        if added:
            self.log.emit("RESEARCH", "RESEARCH", "followup_promoted", task_id,
                          parent=lane_name, because=result["next_action_hint"])

    def _run_desk_session(self, date: str, next_date: str | None) -> str:
        self.state.status = "RUN"
        self.components.set("CONTROL", "RUN", f"desk session {date}")
        panel = self.panel()
        summary = self.desk.run_session(panel, date, next_date)
        self.state.desk_cursor = date
        self.state.desk_sessions += 1
        booked = [ticket for ticket in summary["tickets"] if ticket["status"] == "BOOKED"]
        if booked:
            self.log.emit("DESK", "BOOK", "session_booked", date, tickets=len(booked),
                          capital_nav=summary["capital"]["nav"],
                          evaluation_nav=summary["evaluation"]["nav"])
        self.state.next_action = self._describe_next_action()
        self.heartbeat()
        return "SESSION"

    def _assess_decision_quality(self) -> bool:
        """Once the desk has finished its window, score the system's own rejections."""
        if self._next_desk_session() is not None or self.state.desk_sessions == 0:
            return False
        assessments = self.learning.assess_rejections(
            self.strategies, self.desk.evaluation, self.desk.journal.stats_for)
        if not assessments:
            return False
        self.components.set("LEARNING", "RUN", "rejection quality assessed")
        for assessment in assessments:
            self.log.emit("LEARNING", "LEARNING", "rejection_assessed",
                          assessment["strategy_id"], verdict=assessment["verdict"],
                          counterfactual_return=assessment["counterfactual_return"])
        self.heartbeat()
        return True

    # --- operator ----------------------------------------------------------
    def run(self, max_ticks: int = 10_000) -> dict[str, Any]:
        started = utc_now()
        outcomes: dict[str, int] = {}
        for _ in range(max_ticks):
            outcome = self.tick()
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
            if outcome in {"IDLE", "PAUSED"}:
                break
        entry = {"run_id": f"run-{len(self.state.run_history) + 1}", "started_at": started,
                 "finished_at": utc_now(), "outcomes": outcomes,
                 "ticks": sum(outcomes.values()), "ended": self.state.status}
        self.state.run_history.append(entry)
        self.state.run_history = self.state.run_history[-50:]
        self.save()
        return entry

    def serve(self, poll_seconds: float = IDLE_POLL_SECONDS, max_cycles: int | None = None,
              stop_when: Callable[["QuantSystem"], bool] | None = None) -> dict[str, Any]:
        """Run indefinitely: work when work is due, wait when it is not.

        ``run`` returns at the first IDLE, which is only useful for a bounded
        batch. The system is supposed to stay alive: IDLE means nothing is due
        right now, not that the campaign is over. Each wake re-checks dataset
        availability, because new data is the event that unblocks work.

        Waiting goes through the injectable timer so liveness can be tested
        deterministically instead of by sleeping in a test suite.
        """
        started = utc_now()
        outcomes: dict[str, int] = {}
        cycles = 0
        while True:
            outcome = self.tick()
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
            if outcome not in {"IDLE", "PAUSED"}:
                continue
            if stop_when is not None and stop_when(self):
                break
            if max_cycles is not None and cycles >= max_cycles:
                break
            cycles += 1
            self.state.waits += 1
            self.components.set("CONTROL", "IDLE",
                                f"waiting {poll_seconds:.0f}s for due work or new data")
            self.log.emit("CONTROL", "CONTROL", "clock_waiting", self.state.system_id,
                          poll_seconds=poll_seconds, next_action=self.state.next_action)
            self.save()
            self.timer.sleep(poll_seconds)
            self.state.last_wake_at = self.timer.now().isoformat()
            arrived = self.datasets.reload()
            changed = self.datasets.refresh_availability()
            if arrived or changed:
                self._panel = None  # the cached panel may be stale
                self._seed_work()
                refresh_records = list(changed) + [self.datasets.get(dataset_id)
                                                   for dataset_id in arrived
                                                   if self.datasets.get(dataset_id)]
                self._reactivate_changed_research(refresh_records)
            unblocked = self._unblock_dependencies()
            if arrived or changed or unblocked:
                self.log.emit("CONTROL", "CONTROL", "clock_woken", self.state.system_id,
                              datasets_arrived=arrived,
                              datasets_changed=[record.dataset_id for record in changed],
                              unblocked=unblocked)
            self.save()
        entry = {"run_id": f"serve-{len(self.state.run_history) + 1}", "started_at": started,
                 "finished_at": utc_now(), "outcomes": outcomes, "waits": cycles,
                 "ticks": sum(outcomes.values()), "ended": self.state.status, "mode": "serve"}
        self.state.run_history.append(entry)
        self.state.run_history = self.state.run_history[-50:]
        self.save()
        return entry

    def pause(self, reason: str) -> None:
        self.state.status = "PAUSED"
        self.state.pause_reason = reason
        self.components.set("CONTROL", "PAUSED", reason)
        self.log.emit("CONTROL", "CONTROL", "system_paused", reason)
        self.save()

    def resume(self) -> None:
        self.state.status = "IDLE"
        self.state.pause_reason = None
        self.components.set("CONTROL", "IDLE", "resumed by operator")
        self.log.emit("CONTROL", "CONTROL", "system_resumed", self.state.system_id)
        self.save()

    # --- observation -------------------------------------------------------
    def _describe_next_action(self) -> str:
        due = self.queue.next_due()
        if due is not None:
            return f"run research task {due.task_id}"
        session = self._next_desk_session()
        if session is not None:
            return f"run the desk session for {session[0]}"
        if self.sec.configured and self.sec.state.enabled:
            if self.sec.has_pending_work():
                return "acquire the queued SEC filing raw bytes"
            cooldown = self.sec.cooldown_remaining()
            if cooldown > 0:
                return f"wait {cooldown:.0f}s for the SEC cooldown to expire"
            if self.sec.state.coverage_state != "COMPLETE":
                return (f"resolve SEC capture coverage: "
                        f"{self.sec.state.coverage_detail or 'unknown'}")
        blocked = sorted((task for task in self.queue.tasks.values()
                          if task.status == "BLOCKED"), key=lambda task: -task.priority)
        if blocked:
            return (f"blocked on a dependency for {blocked[0].task_id}: "
                    f"{blocked[0].blocked_reason}")
        if self.sec.configured and self.sec.state.enabled:
            return "poll SEC discovery when the next cadence window opens"
        return "idle: awaiting new data, a new session or an operator instruction"

    def health(self) -> list[dict[str, str]]:
        """Watchdog. Reports conditions, never repairs silently."""
        alerts: list[dict[str, str]] = []
        now = self.timer.now()
        age = (now - parse_ts(self.state.last_heartbeat)).total_seconds()
        if age > HEARTBEAT_TIMEOUT_SECONDS:
            alerts.append({"code": "HEARTBEAT_STALE",
                           "detail": f"{age:.0f}s since the last heartbeat"})
        for task in self.queue.tasks.values():
            # RUNNING is healthy work until the lease expires; only then is it stuck.
            if task.status == "RUNNING" and is_lease_stale(task, now):
                alerts.append({"code": "WORKER_STUCK",
                               "detail": f"{task.task_id} lease expired "
                                         f"(started {task.started_at})"})
            if task.attempts >= MAX_TASK_ATTEMPTS and task.status in {"PENDING", "FAILED"}:
                alerts.append({"code": "REPEATED_FAILURE", "detail": task.task_id})
        for name, status in self.components.statuses.items():
            if status.state == "FAULT":
                alerts.append({"code": "COMPONENT_FAULT", "detail": f"{name}: {status.detail}"})
        health = self.datasets.health()
        if not health["healthy"]:
            alerts.append({"code": "DATA_UNHEALTHY", "detail": str(health["by_availability"])})
        if self.state.status == "IDLE" and self.queue.next_due() is not None:
            alerts.append({"code": "QUEUE_STARVATION",
                           "detail": self.queue.next_due().task_id})
        exposures = self.desk.capital.exposures()
        if abs(exposures["net_ratio"]) > self.desk.limits.max_net_ratio:
            alerts.append({"code": "NET_EXPOSURE_BREACH",
                           "detail": f"{exposures['net_ratio']:+.3f}"})
        return alerts

    def _ticket_counts(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        recent: list[dict[str, Any]] = []
        for ticket in read_jsonl(self.paths.opportunities):
            counts[ticket["status"]] = counts.get(ticket["status"], 0) + 1
            recent.append(ticket)
        return {"total": sum(counts.values()), "by_status": counts,
                "recent": [{"opportunity_id": item["opportunity_id"],
                            "session_date": item["session_date"],
                            "strategy_id": item["strategy_id"], "ledger": item["ledger"],
                            "stage": item["stage"], "status": item["status"],
                            "reason": item["reason"]} for item in recent[-8:][::-1]]}

    def snapshot(self) -> dict[str, Any]:
        """Everything the status surface and the brief are rendered from."""
        return {
            "control": self.state.to_dict(),
            "components": self.components.snapshot(),
            "data": {"health": self.datasets.health(),
                     "datasets": {key: record.to_dict()
                                  for key, record in self.datasets.records.items()}},
            "research": {"queue": self.queue.counts(),
                         "tasks": [{"task_id": task.task_id, "status": task.status,
                                    "lane": task.lane, "priority": task.priority,
                                    "blocked_reason": task.blocked_reason,
                                    "result": task.metadata.get("result")}
                                   for task in sorted(self.queue.tasks.values(),
                                                      key=lambda item: -item.priority)],
                         "strategies": {key: value.to_dict()
                                        for key, value in self.strategies.strategies.items()},
                         "desk_stats": {key: self.desk.journal.stats_for(key)
                                        for key in self.strategies.strategies},
                         "lifecycle": self.strategies.by_lifecycle()},
            "book": self.desk.capital.summary(),
            "book_positions": self.desk.capital.open_positions(),
            "book_sleeves": {key: self.desk.capital.sleeve_positions(key)
                             for key in self.desk.capital.sleeves},
            "evaluation": self.desk.evaluation.summary(),
            "evaluation_positions": self.desk.evaluation.open_positions(),
            "tickets": self._ticket_counts(),
            "learning": self.learning.summary(),
            "build_tasks": self.learning.open_build_tasks(),
            "health": self.health(),
            # Opaque acquisition telemetry only. See the visibility firewall in
            # governance/P0_RAW_CAPTURE_CRITICAL_PATH_RECLASSIFICATION_2026-09-18.md.
            "sec_capture": self.sec.telemetry(),
            "events": {"total": self.log.count(), "recent": self.log.recent(15),
                       "faults": len(self.log.faults())},
        }
