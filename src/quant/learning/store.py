"""The learning loop.

``QUANT_NORTH_STAR.md`` lists what the system must learn from, and the hardest
item on that list is the one most systems skip: false rejects. A rejection that
is never revisited is an unmeasured decision, so every rejected strategy is
carried on the evaluation track and scored against what it would have done.

This store also holds ``BuildTask`` records: capability gaps the system noticed
about itself, which is how the Build Plane receives work.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ..state import read_json, utc_now, write_json


#: A counterfactual result inside this band is noise, not a decision error.
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
    def record_research(self, lane_name: str, lane: str, result: dict[str, Any]) -> None:
        if not result.get("lesson"):
            return
        self.lessons.append({"at": utc_now(), "source": "RESEARCH", "lane": lane,
                             "lane_name": lane_name, "outcome": result.get("outcome"),
                             "ticket_id": result.get("ticket_id"),
                             "lesson": result["lesson"],
                             "next_action": result.get("next_action_hint")})
        current = self.lane_priorities.get(lane_name, 30.0)
        # A rejection lowers the lane's priority; a validated result raises it.
        delta = 4.0 if result.get("outcome") == "VALIDATED" else -6.0
        self.lane_priorities[lane_name] = round(current + delta, 2)
        self.save()

    def latest_lesson(self) -> str | None:
        return self.lessons[-1]["lesson"] if self.lessons else None

    # --- decision quality --------------------------------------------------
    def assess_rejections(self, strategies: Any, evaluation_ledger: Any,
                          desk_stats: Any = None) -> list[dict[str, Any]]:
        """Score every rejected strategy against what it would actually have done."""
        assessments = []
        for definition in strategies.strategies.values():
            if not definition.evaluation_track:
                continue
            attributed = evaluation_ledger.state.attribution.get(definition.strategy_id)
            stats = desk_stats(definition.strategy_id) if desk_stats else {}
            if not attributed or stats.get("booked", 0) == 0:
                continue
            # The strategy's own sleeve, not the aggregate book: another strategy's
            # position in the same symbol is not this one's counterfactual.
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
            assessments.append({
                "strategy_id": definition.strategy_id, "verdict": verdict,
                "counterfactual_pnl": pnl, "counterfactual_return": ratio,
                "sessions": stats.get("sessions", 0),
                "rebalances": stats.get("booked", 0),
                "costs": attributed["costs"], "assessed_at": utc_now()})
        if assessments:
            self.decision_quality = {
                "strategies_evaluated": len(assessments),
                "true_rejects": sum(1 for item in assessments if item["verdict"] == "TRUE_REJECT"),
                "false_rejects": sum(1 for item in assessments
                                     if item["verdict"] == "FALSE_REJECT"),
                "undetermined": sum(1 for item in assessments
                                    if item["verdict"] == "UNDETERMINED"),
                "counterfactual_pnl": sum(item["counterfactual_pnl"] for item in assessments),
                "assessments": assessments}
            self.save()
        return assessments

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
