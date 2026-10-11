"""Agent queue/session safety on synthetic state; no models, network or prices."""
import copy
import tempfile
import unittest
from datetime import datetime, timezone

from quant.edge_lab.engine import Lab, initialize
from quant.edge_lab.store import Refused
from quant.edge_lab.worker import queue, start, finish


class Authority:
    def __init__(self, lab, reject=False):
        self.lab, self.reject, self.claims = lab, reject, 0
        self.remote, self.control = lab.snapshot()

    def snapshot(self):
        return {"sha": "a" * 40, "state": copy.deepcopy(self.remote), "control": copy.deepcopy(self.control)}

    def claim(self, state, parent):
        self.claims += 1
        if self.reject:
            raise Refused("Synthetic losing CAS")
        self.remote = copy.deepcopy(state)
        return "b" * 40


class WorkerTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        initialize(temp.name)
        self.lab = Lab(temp.name)
        self.evidence = {"id": "fixture", "kind": "METHOD", "url": "https://example.invalid/fixture",
            "version": "synthetic", "passage": "Fixture", "fact": "Only synthetic work",
            "limit": "No source access, market outcomes or scheduler delivery"}
        self.lab.evidence(self.evidence)

    def test_start_publishes_question_before_returning_work_without_economic_charge(self):
        before = self.lab.snapshot()[0]
        authority = Authority(self.lab)
        receipt = start(self.lab, authority, "synthetic-interactive", invocation_id="once")
        self.assertEqual(authority.claims, 1)
        self.assertEqual(receipt["published_commit"], "b" * 40)
        self.assertEqual(authority.remote["decisions"][receipt["next"]["id"]]["claim_id"], receipt["claim_id"])
        self.assertFalse(receipt["outcome_access_authorized"])
        self.assertFalse(authority.remote["worker_sessions"]["once"]["delivery_verified"])
        for key in ("looks", "jobs", "trial_charges", "baseline", "imported", "protocols"):
            self.assertEqual(before[key], authority.remote[key])

    def test_cas_loser_receives_no_work_and_preserves_original_remote_state(self):
        authority = Authority(self.lab, reject=True)
        before = copy.deepcopy(authority.remote)
        with self.assertRaisesRegex(Refused, "losing CAS"):
            start(self.lab, authority, "synthetic-loser")
        self.assertEqual(authority.remote, before)
        self.assertEqual(authority.claims, 1)

    def test_pause_is_checked_before_state_or_local_session_access(self):
        authority = Authority(self.lab)
        authority.control["paused"] = True
        authority.remote = None
        before = self.lab.snapshot()[0]
        with self.assertRaisesRegex(Refused, "PAUSED"):
            start(self.lab, authority, "synthetic")
        self.assertEqual(self.lab.snapshot()[0], before)
        self.assertEqual(authority.claims, 0)

    def test_stale_local_state_cannot_claim(self):
        authority = Authority(self.lab)
        self.lab.evidence({**self.evidence, "id": "later"})
        with self.assertRaisesRegex(Refused, "exact remote"):
            start(self.lab, authority, "synthetic")
        self.assertEqual(authority.claims, 0)

    def test_owner_disabled_scheduler_is_not_reenabled_by_agent_start(self):
        with self.lab.store.lock():
            state = self.lab.store.read()
            state["scheduler"]["enabled"] = False
            self.lab.store.save(state)
        authority = Authority(self.lab)
        with self.assertRaisesRegex(Refused, "disabled"):
            start(self.lab, authority, "scheduled-automation", "scheduled-automation")
        self.assertEqual(authority.claims, 0)

    def test_parallel_session_or_reused_invocation_cannot_start(self):
        authority = Authority(self.lab)
        start(self.lab, authority, "synthetic", invocation_id="once")
        with self.assertRaisesRegex(Refused, "Existing agent"):
            start(self.lab, authority, "second", invocation_id="other")
        self.assertEqual(authority.claims, 1)

    def test_finish_requires_original_resolved_claim_and_preserves_finished_receipt(self):
        authority = Authority(self.lab)
        receipt = start(self.lab, authority, "synthetic", invocation_id="once")
        with self.assertRaisesRegex(Refused, "Resolve"):
            finish(self.lab, authority, "once", ["fixture"], "Premature")
        self.lab.decide(receipt["next"]["id"], "WAIT", ["fixture"], "Synthetic inaccessible gate", receipt["claim_id"])
        authority.remote = self.lab.snapshot()[0]  # synthetic prior decision publication
        final = finish(self.lab, authority, "once", ["fixture"], "Gate saved; no new outcomes")
        self.assertEqual(final["status"], "COMPLETED")
        self.assertFalse(final["delivery_verified"])
        with self.assertRaisesRegex(Refused, "unfinished"):
            finish(self.lab, authority, "once", ["fixture"], "Duplicate")
        with self.lab.store.lock():
            state = self.lab.store.read()
            state["worker_sessions"]["once"]["status"] = "STARTED"
            with self.assertRaisesRegex(Refused, "replayed"):
                self.lab.store.save(state)

    def test_due_boundary_waits_and_expired_claim_requires_recovery(self):
        state, control = self.lab.snapshot()
        state["decisions"] = {"future": {"status": "OPEN", "family": "synthetic", "priority": 1,
            "not_before": "2026-10-13T12:45:00Z"}, "old": {"status": "RESEARCHING", "family": "synthetic",
            "claimed_at": "2026-10-13T10:00:00Z", "lease_seconds": 600}}
        before = queue(state, control, datetime(2026, 10, 13, 12, 44, tzinfo=timezone.utc))
        self.assertEqual(before["counts"]["scheduled"], 1)
        self.assertEqual(before["counts"]["recovery"], 1)
        self.assertEqual(before["next"]["id"], "old")
        due = queue(state, control, datetime(2026, 10, 13, 12, 45, tzinfo=timezone.utc))
        self.assertEqual(due["counts"]["ready"], 1)
        control["paused"] = True
        self.assertIsNone(queue(state, control)["next"])


if __name__ == "__main__":
    unittest.main()
