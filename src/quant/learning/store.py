"""The learning loop.

``QUANT_NORTH_STAR.md`` lists what the system must learn from, and the hardest
item on that list is false rejects. A rejection that is never revisited is an
unmeasured decision, so rejected strategies are carried on the evaluation track
and rescored whenever genuinely new forward evidence arrives.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ..state import read_json, utc_now, write_json


MATERIAL_COUNTERFACTUAL = 0.01


@dataclass
class BuildTask:
    task_id: str
    capability: str
    reason: str
    affected_subsystems: list[str]
    acceptance: str
    priority: float
    evidence: dict[str, Any] = field(default_factory=dict)
    status: str = "OPEN"
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LearningStore:
    def __init__(self, path: Path):
        self.path = path
        payload = read_json(path, {}) or {}
        self.lessons: list[dict[str, Any]] = payload.get("lessons", [])
        self.lane_priorities: dict[str, float] = payload.get("lane_priorities", {})
        self.decision_quality: dict[str, Any] = payload.get("decision_quality", {
            "strategies_evaluated": 0, "true_rejects": 0, "false_rejects": 0,
            "undetermined": 0, "counterfactual_pnl": 0.0, "assessments": []})
        self.build_tasks: dict[str, dict[str, Any]] = payload.get("build_tasks", {})

    def save(self) -> None:
        write_json(self.path, {"version": 1, "updated_at": utc_now(),
                               "lessons": self.lessons[-200:],
                               "lane_priorities": self.lane_priorities,
                               "decision_quality": self.decision_quality,
                               "build_tasks": self.build_tasks})

    # --- research ----------------------------------------------------------
    def record_research(self, lane_name: str, lane: str, result: dict[str, Any]) -> bool:
        """Record one scientific ticket once, even if its worker is replayed."""
        if not result.get("lesson"):
            return False
        ticket_id = result.get("ticket_id")
        if ticket_id and any(item.get("source") == "RESEARCH"
                             and item.get("ticket_id") == ticket_id
                             for item in self.lessons):
            return False
        self.lessons.append({"at": utc_now(), "source": "RESEARCH", "lane": lane,
                             "lane_name": lane_name, "outcome": result.get("outcome"),
                             "ticket_id": ticket_id,
                             "lesson": result["lesson"],
                             "next_action": result.get("next_action_hint")})
        current = self.lane_priorities.get(lane_name, 30.0)
        delta = 4.0 if result.get("outcome") == "VALIDATED" else -6.0
        self.lane_priorities[lane_name] = round(current + delta, 2)
        self.save()
        return True

    def latest_lesson(self) -> str | None:
        return self.lessons[-1]["lesson"] if self.lessons else None

    # --- decision quality --------------------------------------------------
    @staticmethod
    def _assessment_core(item: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in item.items() if key != "assessed_at"}

    def assess_rejections(self, strategies: Any, evaluation_ledger: Any,
                          desk_stats: Any = None) -> list[dict[str, Any]]:
        """Refresh rejected-strategy quality only when its evidence changed.

        Returns the assessments that changed. Repeating the exact same ledger
        and desk evidence is therefore a no-op, while a new mark/fill updates
        false-reject quality instead of freezing the first verdict forever.
        """
        previous = {item["strategy_id"]: item
                    for item in self.decision_quality.get("assessments", [])}
        current_assessments: list[dict[str, Any]] = []
        changed: list[dict[str, Any]] = []
        for definition in strategies.strategies.values():
            if not definition.evaluation_track:
                continue
            attributed = evaluation_ledger.state.attribution.get(definition.strategy_id)
            stats = desk_stats(definition.strategy_id) if desk_stats else {}
            if not attributed or stats.get("booked", 0) == 0:
                continue
            positions = evaluation_ledger.sleeve_positions(definition.strategy_id)
            unrealized = sum(position["unrealized_pnl"] for position in positions)
            pnl = attributed["realized_pnl"] + unrealized - attributed["costs"]
            base = evaluation_ledger.state.initial_capital or 1.0
            ratio = pnl / base
            if abs(ratio) < MATERIAL_COUNTERFACTUAL:
                verdict = "UNDETERMINED"
            elif ratio > 0:
                verdict = "FALSE_REJECT"
            else:
                verdict = "TRUE_REJECT"
            core = {
                "strategy_id": definition.strategy_id, "verdict": verdict,
                "counterfactual_pnl": pnl, "counterfactual_return": ratio,
                "sessions": stats.get("sessions", 0),
                "rebalances": stats.get("booked", 0),
                "costs": attributed["costs"],
                "ledger_last_session": evaluation_ledger.state.last_session_date}
            old = previous.get(definition.strategy_id)
            if old is not None and self._assessment_core(old) == core:
                assessment = old
            else:
                assessment = {**core, "assessed_at": utc_now()}
                changed.append(assessment)
            current_assessments.append(assessment)

        if not current_assessments:
            return []
        summary = {
            "strategies_evaluated": len(current_assessments),
            "true_rejects": sum(1 for item in current_assessments
                                if item["verdict"] == "TRUE_REJECT"),
            "false_rejects": sum(1 for item in current_assessments
                                 if item["verdict"] == "FALSE_REJECT"),
            "undetermined": sum(1 for item in current_assessments
                                if item["verdict"] == "UNDETERMINED"),
            "counterfactual_pnl": sum(item["counterfactual_pnl"]
                                      for item in current_assessments),
            "assessments": current_assessments}
        if changed or summary != self.decision_quality:
            self.decision_quality = summary
            self.save()
        return changed

    # --- build plane -------------------------------------------------------
    def raise_build_task(self, task: BuildTask) -> BuildTask:
        if task.task_id not in self.build_tasks:
            self.build_tasks[task.task_id] = task.to_dict()
            self.lessons.append({"at": utc_now(), "source": "BUILD", "lane": None,
                                 "lesson": f"capability gap: {task.capability}",
                                 "next_action": task.acceptance})
            self.save()
        return task

    def open_build_tasks(self) -> list[dict[str, Any]]:
        return sorted((task for task in self.build_tasks.values() if task["status"] == "OPEN"),
                      key=lambda item: -item["priority"])

    def summary(self) -> dict[str, Any]:
        return {"lessons": len(self.lessons), "latest_lesson": self.latest_lesson(),
                "lane_priorities": dict(sorted(self.lane_priorities.items(),
                                               key=lambda item: -item[1])),
                "decision_quality": {key: value for key, value
                                     in self.decision_quality.items() if key != "assessments"},
                "open_build_tasks": len(self.open_build_tasks())}
