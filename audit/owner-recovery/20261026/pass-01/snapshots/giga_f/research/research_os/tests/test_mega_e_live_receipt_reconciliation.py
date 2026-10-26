"""MEGA E adversarial tests for observation-only Live Lab receipt recovery."""
from contextlib import contextmanager
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from deploy.oracle_live_projection import durable_observation_path, reconcile_local_observation_receipts


class FakeSnapshot:
    def __init__(self, values):
        self.values = deepcopy(values)
        self.blobs = {path: "b" * 40 for path in values}

    def read(self, path):
        return deepcopy(self.values[path])


class FakeStore:
    def __init__(self, values=None):
        self.values = deepcopy(values or {})
        self.commits = []

    @contextmanager
    def snapshot(self):
        yield FakeSnapshot(self.values)

    def commit(self, snapshot, writes, *, create_only=(), message, **kwargs):
        for path in create_only:
            if path in self.values:
                raise RuntimeError("UNEXPECTED_TEST_OVERWRITE")
        self.commits.append(dict(writes=deepcopy(writes), create_only=list(create_only), message=message))
        self.values.update(deepcopy(writes))
        return "c" * 40


def valid_receipt():
    source = {
        "event_id": "task-g2-001",
        "session_id": "task-g2",
        "worker_id": "oracle-research.fundamental_events",
        "action_id": "task",
        "generation": 2,
        "event_seq": 1,
        "input_commit": "a" * 40,
        "lane": "fundamental_events",
        "stage": "document_or_fundamental_research",
    }
    session = {"session_id": "site-1", "generation": 1, "lease_id": "lease", "heartbeat_interval_ms": 10000}
    packet = {
        "principal": "oracle-research-live",
        "event_id": source["event_id"],
        "trace_id": source["session_id"],
        "worker_id": source["worker_id"],
        "session_id": session["session_id"],
        "generation": session["generation"],
        "lease_id": session["lease_id"],
        "event_seq": 1,
        "event_type": "ACTION_STARTED",
        "action_id": source["action_id"],
        "emitted_at": "2026-10-21T16:00:00Z",
        "payload": {"ui_activity": "document-reading"},
    }
    return {
        "schema_version": "oracle-live-projection-v1",
        "source": source,
        "site_session": session,
        "records": [
            {"state": "PENDING", "packet": packet},
            {"state": "ACKNOWLEDGED", "event_id": packet["event_id"], "cursor": 7,
             "status": "APPLIED", "accepted_at": None},
        ],
        "authority": "OBSERVATIONAL_ONLY",
        "canonical_terminal": None,
        "source_events_mutated": False,
        "stale_starts_replayed": False,
        "credentials_included": False,
    }


class MegaELiveReceiptReconciliationTests(unittest.TestCase):
    def state_dir(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        return Path(temporary.name)

    def write_local(self, state, receipt, name="receipt.json"):
        path = state / name
        path.write_text(json.dumps(receipt))
        return path

    def test_acknowledged_receipt_reconciles_once_then_exact_duplicate_is_noop(self):
        state = self.state_dir()
        receipt = valid_receipt()
        store = FakeStore()
        local = self.write_local(state, receipt)

        first = reconcile_local_observation_receipts(store, state)
        canonical = durable_observation_path(receipt)
        self.assertEqual(first, {"reconciled": 1, "already_durable": 0, "pending_or_invalid": 0,
                                 "conflicts": 0, "unavailable": 0})
        self.assertEqual(len(store.commits), 1)
        self.assertEqual(store.commits[0]["create_only"], [canonical])
        self.assertEqual(store.values[canonical], receipt)
        self.assertFalse(local.exists())

        local = self.write_local(state, receipt)
        second = reconcile_local_observation_receipts(store, state)
        self.assertEqual(second["already_durable"], 1)
        self.assertEqual(second["reconciled"], 0)
        self.assertEqual(len(store.commits), 1)
        self.assertFalse(local.exists())

    def test_pending_start_without_ack_is_never_promoted_to_durable_receipt(self):
        state = self.state_dir()
        receipt = valid_receipt()
        receipt["records"] = receipt["records"][:1]
        local = self.write_local(state, receipt)
        store = FakeStore()

        summary = reconcile_local_observation_receipts(store, state)
        self.assertEqual(summary["pending_or_invalid"], 1)
        self.assertEqual(store.commits, [])
        self.assertTrue(local.exists())
        self.assertNotIn(durable_observation_path(receipt), store.values)

    def test_conflicting_existing_canonical_receipt_is_never_overwritten(self):
        state = self.state_dir()
        receipt = valid_receipt()
        canonical = durable_observation_path(receipt)
        conflicting = deepcopy(receipt)
        conflicting["records"][1]["cursor"] = 99
        store = FakeStore({canonical: conflicting})
        local = self.write_local(state, receipt)

        summary = reconcile_local_observation_receipts(store, state)
        self.assertEqual(summary["conflicts"], 1)
        self.assertEqual(store.commits, [])
        self.assertEqual(store.values[canonical], conflicting)
        self.assertTrue(local.exists())

    def test_malformed_local_state_cannot_mutate_github(self):
        state = self.state_dir()
        receipt = valid_receipt()
        receipt["credentials_included"] = True
        local = self.write_local(state, receipt, "unsafe.json")
        store = FakeStore()

        summary = reconcile_local_observation_receipts(store, state)
        self.assertEqual(summary["pending_or_invalid"], 1)
        self.assertEqual(store.commits, [])
        self.assertEqual(store.values, {})
        self.assertTrue(local.exists())


if __name__ == "__main__":
    unittest.main()
