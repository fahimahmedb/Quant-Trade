"""Persistent scheduler, dispatcher, reprioritizer, and boundary detector."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

from .pipeline import run_discovery_cycle
from .runtime import CampaignState, PersistentQueue, ResearchTask, utc_now

Worker = Callable[[ResearchTask], dict[str, Any]]


class ResearchCampaign:
    def __init__(self, root: Path, campaign_id: str = "quant-research-v1",
                 max_cycles: int | None = None, workers: dict[str, Worker] | None = None):
        self.root = root
        self.runtime_dir = root / "runtime"
        self.state_path = self.runtime_dir / "campaign_state.json"
        self.queue = PersistentQueue(self.runtime_dir / "research_queue.json")
        self.state = CampaignState.load_or_create(self.state_path, campaign_id, max_cycles)
        self.workers = {"vertical_slice": self._vertical_slice_worker}
        self.workers.update(workers or {})
        self._recover_interrupted_work()
        self._sync_state()

    def _recover_interrupted_work(self) -> None:
        for task in self.queue.tasks.values():
            if task.status == "RUNNING":
                task.status = "PENDING"
                task.last_error = "process stopped while worker was running; recovered for retry"
                task.updated_at = utc_now()
        self.queue.save()

    def _vertical_slice_worker(self, task: ResearchTask) -> dict[str, Any]:
        ticket = run_discovery_cycle(
            self.root / "data/nasdaq_composite_daily.txt",
            self.runtime_dir / "tickets", self.runtime_dir / "memory.jsonl")
        return {"ticket_id": ticket.ticket_id, "lesson": ticket.lesson,
                "next_action_hint": ticket.next_action_hint,
                "outcome": ticket.validation_result.get("decision", ticket.status)}

    def enqueue(self, task: ResearchTask) -> bool:
        if task.execution_key in self.state.processed_data_fingerprints:
            return False
        added = self.queue.add(task)
        self._sync_state()
        return added

    def seed_from_opportunity_map(self) -> None:
        """Turn ranked lanes into durable work, blocking absent datasets explicitly."""
        opportunity_path = self.root / "research" / "opportunity_map.json"
        opportunities = json.loads(opportunity_path.read_text(encoding="utf-8"))["lanes"]
        data_path = self.root / "data" / "nasdaq_composite_daily.txt"
        fingerprint = hashlib.sha256(data_path.read_bytes()).hexdigest()
        legacy_key = f"TSR-NDX-001@sha256:{fingerprint}"
        memory_lines = (self.root / "research" / "memory.jsonl").read_text(encoding="utf-8").splitlines()
        memory_records = [json.loads(line) for line in memory_lines if line.strip()]
        legacy_record = next((record for record in reversed(memory_records)
                              if record.get("ticket_id") == "TSR-NDX-001"), None)
        if legacy_record is None:
            self.enqueue(ResearchTask("TSR-NDX-001", "time_series_relative_value", 30,
                                      "exercise the existing bounded worker once", "vertical_slice",
                                      data_fingerprint=f"sha256:{fingerprint}"))
        else:
            self.queue.add(ResearchTask(
                "TSR-NDX-001", "time_series_relative_value", 30,
                "historical PR #7 vertical slice", "vertical_slice", status="COMPLETED", attempts=1,
                data_fingerprint=f"sha256:{fingerprint}",
                metadata={"result": {"ticket_id": "TSR-NDX-001",
                                     "outcome": legacy_record.get("validation_result", {}).get("decision"),
                                     "lesson": legacy_record.get("lesson"),
                                     "next_action_hint": legacy_record.get("next_action_hint")}}))
            if legacy_key not in self.state.processed_data_fingerprints:
                self.state.processed_data_fingerprints.append(legacy_key)
            self.state.last_completed_ticket_id = "TSR-NDX-001"
            self.state.latest_lesson = legacy_record.get("lesson")
            self.state.next_action = legacy_record.get("next_action_hint")
        for lane in opportunities:
            if lane["lane"] == "time_series_relative_value":
                continue
            task = ResearchTask(
                task_id=f"SCAN-{lane['lane'].upper().replace('_', '-')}-001",
                lane=lane["lane"], priority=lane["total"], worker="unavailable_data",
                parent="opportunity_map", reason=f"ranked research lane: {lane['decision']}",
                required_resources=[lane["constraint"]], status="BLOCKED",
                blocked_reason=lane["constraint"])
            self.enqueue(task)
        self._sync_state()

    def _budget_exhausted(self) -> bool:
        maximum = self.state.research_budget.get("max_cycles")
        return maximum is not None and self.state.budget_consumed.get("cycles", 0) >= maximum

    def run_once(self) -> str:
        if self.state.status == "STOPPED":
            self.state.heartbeat(self.state_path)
            return "STOPPED"
        if self.state.status == "PAUSED" and self.state.pause_reason:
            self.state.heartbeat(self.state_path)
            return "PAUSED"
        self.state.pause_reason = None
        self.state.stop_reason = None
        if self._budget_exhausted():
            self.state.status = "PAUSED"
            self.state.pause_reason = "configured cycle budget exhausted"
            self.state.heartbeat(self.state_path)
            return "PAUSED"
        task = self.queue.next_due()
        if task is None:
            self.state.status = "IDLE"
            self.state.next_action = self._next_action_description()
            self._sync_state()
            self.state.heartbeat(self.state_path)
            return "IDLE"
        worker = self.workers.get(task.worker)
        if worker is None:
            task.status = "BLOCKED"
            task.blocked_reason = f"worker unavailable: {task.worker}"
            task.updated_at = utc_now()
            self.queue.save()
            self._sync_state()
            return self.run_once()
        self.state.status = "RUNNING"
        task.status = "RUNNING"
        task.attempts += 1
        task.updated_at = utc_now()
        self.queue.save()
        self._sync_state()
        try:
            result = worker(task)
        except Exception as exc:
            task.status = "FAILED"
            task.last_error = f"{type(exc).__name__}: {exc}"
            task.updated_at = utc_now()
            self.queue.save()
            self._sync_state()
            if self.queue.next_due() is not None:
                return self.run_once()
            self.state.status = "IDLE"
            self.state.next_action = self._next_action_description()
            self.state.heartbeat(self.state_path)
            return "FAILED"
        task.status = "COMPLETED"
        task.updated_at = utc_now()
        task.metadata["result"] = result
        self.state.cycles_completed += 1
        self.state.budget_consumed["cycles"] = self.state.cycles_completed
        self.state.last_completed_ticket_id = result.get("ticket_id", task.task_id)
        self.state.latest_lesson = result.get("lesson")
        if task.execution_key not in self.state.processed_data_fingerprints:
            self.state.processed_data_fingerprints.append(task.execution_key)
        self._promote_followup(task, result)
        self.queue.save()
        self.state.status = "RUNNING"
        self._sync_state()
        self.state.heartbeat(self.state_path)
        return "COMPLETED"

    def _promote_followup(self, task: ResearchTask, result: dict[str, Any]) -> None:
        followup = task.metadata.get("followup")
        if followup:
            candidate = ResearchTask(parent=task.task_id, **followup)
            self.enqueue(candidate)
        self.state.next_action = result.get("next_action_hint") or self._next_action_description()

    def _next_action_description(self) -> str:
        due = self.queue.next_due()
        if due:
            return f"execute {due.task_id}: {due.reason}"
        blocked = sorted((task for task in self.queue.tasks.values() if task.status == "BLOCKED"),
                         key=lambda task: -task.priority)
        if blocked:
            return f"waiting for resource: {blocked[0].blocked_reason}"
        return "waiting for the next scheduled scan or new data"

    def _sync_state(self) -> None:
        self.state.active_ticket_ids = sorted(
            task.task_id for task in self.queue.tasks.values() if task.status == "RUNNING")
        self.state.queued_ticket_ids = [task.task_id for task in sorted(
            self.queue.tasks.values(), key=lambda item: (-item.priority, item.created_at))
            if task.status == "PENDING"]
        self.state.blocked_tasks = [
            {"task_id": task.task_id, "lane": task.lane, "reason": task.blocked_reason}
            for task in self.queue.tasks.values() if task.status == "BLOCKED"]
        if self.state.active_ticket_ids or self.state.queued_ticket_ids or self.state.status == "IDLE":
            self.state.next_action = self._next_action_description()
        self.state.save(self.state_path)

    def pause(self, reason: str) -> None:
        self.state.status = "PAUSED"
        self.state.pause_reason = reason
        self.state.heartbeat(self.state_path)

    def resume(self) -> None:
        self.state.status = "IDLE"
        self.state.pause_reason = None
        self.state.stop_reason = None
        self.state.heartbeat(self.state_path)

    def inspect(self) -> dict[str, Any]:
        return {"campaign": asdict(self.state), "queue_counts": self.queue.counts()}
