"""Owner resumption is distinct from metadata and execution; no external worker."""
import copy
import tempfile
import unittest

from quant.edge_lab.engine import Lab, initialize
from quant.edge_lab.store import Refused


class SchedulerResumptionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        initialize(self.temp.name)
        self.lab = Lab(self.temp.name)
        self.worker_id = self.lab.snapshot()[0]["scheduler"]["id"]
        common = {"kind": "METHOD", "url": "https://example.invalid/synthetic",
                  "version": "synthetic", "passage": "Synthetic fixture",
                  "fact": "Fixture only", "limit": "No backend or economic worker executed"}
        self.lab.evidence({**common, "id": "off"})
        self.lab.scheduler_disabled({"id": self.worker_id, "enabled": False,
            "observed_at": "2026-10-11T00:11:00Z", "evidence_id": "off"})
        self.lab.evidence({**common, "id": "owner", "owner_request": {
            "autonomous_research_worker": True, "no_reminder_messages": True}})
        self.backend = {**common, "id": "backend", "scheduler_receipt": {
            "id": self.worker_id, "is_enabled": True, "updated_at": "2026-10-11T16:00:00Z",
            "last_run_time": "2026-10-10T23:15:00Z", "next_run_time": None}}
        self.lab.evidence(self.backend)
        self.packet = {"id": self.worker_id, "enabled": True,
            "observed_at": "2026-10-11T16:00:00Z",
            "owner_evidence_id": "owner", "backend_evidence_id": "backend"}

    def test_fresh_exact_receipt_configures_one_worker_without_spending_looks(self):
        before = self.lab.snapshot()[0]
        self.lab.scheduler_configured(self.packet)
        after = self.lab.snapshot()[0]
        scheduler = after["scheduler"]
        self.assertTrue(scheduler["enabled"])
        self.assertEqual(scheduler["id"], before["scheduler"]["id"])
        self.assertEqual(scheduler["mode"], "existing_autonomous_research_worker")
        self.assertFalse(scheduler["external_run"]["current_prompt_run_observed"])
        self.assertIsNone(scheduler["external_run"]["next_backend_run_time_observed"])
        self.assertEqual(after["events"][:-1], before["events"])
        for key in ("looks", "jobs", "trial_charges", "baseline", "imported"):
            self.assertEqual(before[key], after[key])
        self.lab.scheduler_configured(self.packet)
        self.assertEqual(self.lab.snapshot()[0], after)

    def test_metadata_tick_still_cannot_reactivate_owner_disabled_worker(self):
        before = self.lab.snapshot()[0]
        with self.assertRaises(Refused):
            self.lab.tick(actor="synthetic-metadata", enabled_confirmed=True)
        self.assertEqual(self.lab.snapshot()[0], before)

    def test_other_worker_missing_owner_or_mismatched_receipt_refused(self):
        before = self.lab.snapshot()[0]
        for update in ({"id": "other-worker"}, {"owner_evidence_id": "off"},
                       {"backend_evidence_id": "off"}, {"enabled": False},
                       {"observed_at": "2026-10-11T16:01:00Z"}):
            with self.assertRaises(Refused):
                self.lab.scheduler_configured({**self.packet, **update})
            self.assertEqual(self.lab.snapshot()[0], before)

    def test_historical_receipt_cannot_override_newer_pause(self):
        old = copy.deepcopy(self.backend)
        old["id"] = "historical-backend"
        old["scheduler_receipt"]["updated_at"] = "2026-10-10T16:00:00Z"
        self.lab.evidence(old)
        before = self.lab.snapshot()[0]
        with self.assertRaises(Refused):
            self.lab.scheduler_configured({**self.packet, "backend_evidence_id": old["id"],
                "observed_at": old["scheduler_receipt"]["updated_at"]})
        self.assertEqual(self.lab.snapshot()[0], before)

    def test_paused_control_refuses_receipt_without_mutation(self):
        self.lab.store.pause(True, "Synthetic pause")
        before = self.lab.snapshot()[0]
        with self.assertRaises(Refused):
            self.lab.scheduler_configured(self.packet)
        self.assertEqual(self.lab.snapshot()[0], before)


if __name__ == "__main__":
    unittest.main()
