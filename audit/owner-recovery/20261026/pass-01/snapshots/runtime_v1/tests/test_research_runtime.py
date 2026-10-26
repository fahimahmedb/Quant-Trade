import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from autonomous_research.orchestrator import ResearchCampaign
from autonomous_research.runtime import CampaignState, PersistentQueue, ResearchTask
from autonomous_research.watchdog import inspect_health


def successful_worker(task):
    return {"ticket_id": task.task_id, "outcome": "REJECT_RESEARCH",
            "lesson": "candidate rejected after adversarial validation",
            "next_action_hint": "scan the next independent lane"}


class StateAndQueueTests(unittest.TestCase):
    def test_campaign_state_persists(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            state = CampaignState.load_or_create(path, "campaign")
            state.cycles_completed = 7
            state.latest_lesson = "durable"
            state.save(path)
            recovered = CampaignState.load_or_create(path, "ignored")
            self.assertEqual((recovered.campaign_id, recovered.cycles_completed,
                              recovered.latest_lesson), ("campaign", 7, "durable"))

    def test_queue_persists_priority_and_blocked_work(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.json"
            queue = PersistentQueue(path)
            queue.add(ResearchTask("low", "a", 1, "low value", "fake"))
            queue.add(ResearchTask("blocked", "b", 99, "needs data", "fake",
                                   status="BLOCKED", blocked_reason="missing panel"))
            queue.add(ResearchTask("high", "c", 5, "high value", "fake"))
            recovered = PersistentQueue(path)
            self.assertEqual(recovered.next_due().task_id, "high")
            self.assertEqual(recovered.tasks["blocked"].blocked_reason, "missing panel")


class CampaignLifecycleTests(unittest.TestCase):
    def make_campaign(self, root, max_cycles=None):
        return ResearchCampaign(Path(root), "test", max_cycles=max_cycles,
                                workers={"fake": successful_worker})

    def test_restart_recovers_exact_state_without_duplicate_rerun(self):
        with tempfile.TemporaryDirectory() as directory:
            first = self.make_campaign(directory)
            first.enqueue(ResearchTask("one", "lane", 1, "test", "fake", data_fingerprint="v1"))
            self.assertEqual(first.run_once(), "COMPLETED")
            restarted = self.make_campaign(directory)
            self.assertEqual(restarted.state.cycles_completed, 1)
            self.assertEqual(restarted.run_once(), "IDLE")
            self.assertFalse(restarted.enqueue(
                ResearchTask("one", "lane", 1, "duplicate", "fake", data_fingerprint="v1")))
            self.assertEqual(restarted.state.cycles_completed, 1)

    def test_same_task_new_fingerprint_can_run(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign = self.make_campaign(directory)
            campaign.enqueue(ResearchTask("one", "lane", 1, "test", "fake", data_fingerprint="v1"))
            campaign.run_once()
            self.assertTrue(campaign.enqueue(
                ResearchTask("one", "lane", 1, "new evidence", "fake", data_fingerprint="v2")))

    def test_rejected_ticket_promotes_followup_and_continues(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign = self.make_campaign(directory)
            campaign.enqueue(ResearchTask(
                "first", "lane-a", 2, "falsify", "fake",
                metadata={"followup": {"task_id": "second", "lane": "lane-b", "priority": 3,
                                       "reason": "independent next lane", "worker": "fake"}}))
            self.assertEqual(campaign.run_once(), "COMPLETED")
            self.assertEqual(campaign.queue.next_due().task_id, "second")
            self.assertEqual(campaign.run_once(), "COMPLETED")
            self.assertEqual(campaign.state.cycles_completed, 2)

    def test_idle_is_not_stopped_and_heartbeat_persists(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign = self.make_campaign(directory)
            before = campaign.state.last_heartbeat
            self.assertEqual(campaign.run_once(), "IDLE")
            recovered = self.make_campaign(directory)
            self.assertEqual(recovered.state.status, "IDLE")
            self.assertNotEqual(recovered.state.status, "STOPPED")
            self.assertGreaterEqual(recovered.state.last_heartbeat, before)

    def test_blocked_task_does_not_prevent_executable_task(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign = self.make_campaign(directory)
            campaign.enqueue(ResearchTask("blocked", "a", 100, "missing", "fake",
                                          status="BLOCKED", blocked_reason="missing data"))
            campaign.enqueue(ResearchTask("ready", "b", 1, "available", "fake"))
            self.assertEqual(campaign.run_once(), "COMPLETED")
            self.assertEqual(campaign.queue.tasks["ready"].status, "COMPLETED")
            self.assertEqual(campaign.queue.tasks["blocked"].status, "BLOCKED")

    def test_budget_exhaustion_pauses_with_explicit_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign = self.make_campaign(directory, max_cycles=1)
            campaign.enqueue(ResearchTask("one", "a", 2, "one", "fake"))
            campaign.enqueue(ResearchTask("two", "b", 1, "two", "fake"))
            campaign.run_once()
            self.assertEqual(campaign.run_once(), "PAUSED")
            self.assertEqual(campaign.state.status, "PAUSED")
            self.assertIn("budget", campaign.state.pause_reason)
            self.assertEqual(campaign.queue.tasks["two"].status, "PENDING")

    def test_operator_pause_survives_restart_until_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign = self.make_campaign(directory)
            campaign.enqueue(ResearchTask("ready", "a", 1, "ready", "fake"))
            campaign.pause("maintenance")
            restarted = self.make_campaign(directory)
            self.assertEqual(restarted.run_once(), "PAUSED")
            self.assertEqual(restarted.queue.tasks["ready"].status, "PENDING")
            restarted.resume()
            self.assertEqual(restarted.run_once(), "COMPLETED")

    def test_restart_recovers_interrupted_worker(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign = self.make_campaign(directory)
            campaign.enqueue(ResearchTask("one", "a", 1, "one", "fake", status="RUNNING"))
            restarted = self.make_campaign(directory)
            self.assertEqual(restarted.queue.tasks["one"].status, "PENDING")
            self.assertIn("recovered", restarted.queue.tasks["one"].last_error)


class WatchdogTests(unittest.TestCase):
    def test_detects_required_fault_classes(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = PersistentQueue(Path(directory) / "queue.json")
            queue.add(ResearchTask("stuck", "a", 1, "stuck", "fake", status="RUNNING"))
            queue.add(ResearchTask("crash", "b", 1, "crash", "fake", attempts=3, status="FAILED"))
            queue.add(ResearchTask("ready", "c", 2, "ready", "fake"))
            state = CampaignState("test", status="IDLE")
            state.last_heartbeat = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            codes = {alert["code"] for alert in inspect_health(state, queue, 10)}
            self.assertTrue({"HEARTBEAT_MISSING", "WORKER_STUCK", "REPEATED_CRASH",
                             "QUEUE_STARVATION"}.issubset(codes))


if __name__ == "__main__":
    unittest.main()
