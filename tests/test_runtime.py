import json
import tempfile
import unittest
from pathlib import Path

from autonomous_research.runtime import CampaignRuntime, ResearchTask, TaskOutcome


class FixedClock:
    def __init__(self):
        self.tick = 0

    def __call__(self):
        self.tick += 1
        return f"2026-01-01T00:00:{self.tick:02d}+00:00"


class RuntimeTests(unittest.TestCase):
    def make_runtime(self, directory, workers=None):
        return CampaignRuntime(Path(directory) / "state.json", Path(directory) / "queue.json",
                               workers or {}, FixedClock())

    def test_runs_priority_order_and_does_not_repeat_after_restart(self):
        completed = []

        def worker(payload):
            completed.append(payload["name"])
            return TaskOutcome("COMPLETED", f"learned {payload['name']}", payload["next"])

        with tempfile.TemporaryDirectory() as directory:
            runtime = self.make_runtime(directory, {"scan": worker})
            runtime.enqueue(ResearchTask("low", "scan", 1, {"name": "low", "next": "later"}))
            runtime.enqueue(ResearchTask("high", "scan", 2, {"name": "high", "next": "next"}))
            runtime.run_once()
            restarted = self.make_runtime(directory, {"scan": worker})
            restarted.run_once()
            restarted.run_once()
            self.assertEqual(completed, ["high", "low"])
            self.assertEqual(restarted.state["cycles_completed"], 2)
            self.assertEqual(restarted.state["status"], "IDLE")

    def test_blocked_task_does_not_prevent_other_work(self):
        def worker(payload):
            if payload["blocked"]:
                return TaskOutcome("BLOCKED", "data absent", blocked_reason="missing data")
            return TaskOutcome("COMPLETED", "scan rejected honestly")

        with tempfile.TemporaryDirectory() as directory:
            runtime = self.make_runtime(directory, {"scan": worker})
            runtime.enqueue(ResearchTask("blocked", "scan", 2, {"blocked": True}))
            runtime.enqueue(ResearchTask("ready", "scan", 1, {"blocked": False}))
            runtime.run_once()
            runtime.run_once()
            self.assertEqual(runtime.state["cycles_completed"], 2)
            self.assertEqual(runtime.state["status"], "IDLE")
            self.assertEqual(runtime.state["blocked_tasks"][0]["task_id"], "blocked")

    def test_recovers_active_task_after_simulated_process_death(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = self.make_runtime(directory)
            runtime.enqueue(ResearchTask("work", "scan", 1))
            queue = json.loads(runtime.queue_path.read_text())
            queue[0]["status"] = "ACTIVE"
            runtime.queue_path.write_text(json.dumps(queue))
            restarted = self.make_runtime(directory)
            self.assertEqual(restarted.tasks[0].status, "QUEUED")
            self.assertEqual(restarted.state["active_ticket_ids"], [])

    def test_budget_pauses_without_consuming_queued_task(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = self.make_runtime(directory, {"scan": lambda _: TaskOutcome("COMPLETED", "done")})
            runtime.state["research_budget"] = {"max_tasks": 0}
            runtime.enqueue(ResearchTask("work", "scan", 1))
            runtime.run_once()
            self.assertEqual(runtime.state["status"], "PAUSED")
            self.assertEqual(runtime.tasks[0].status, "QUEUED")


if __name__ == "__main__":
    unittest.main()
