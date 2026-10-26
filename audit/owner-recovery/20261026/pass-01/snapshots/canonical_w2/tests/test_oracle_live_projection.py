"""Native observation tests. No Site secret or production network required."""
from copy import deepcopy
from datetime import timedelta
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import urllib.error
from unittest.mock import patch

from deploy.oracle_live_projection import LiveProjection, ProjectionStore, SiteTransport, SITE


class NativeSite:
    def __init__(self):
        self.requests, self.events = [], {}
        self.generation = 0
        self.failure = False

    def post(self, route, packet):
        self.requests.append((route, deepcopy(packet)))
        if self.failure: raise RuntimeError("sensitive-error-must-not-be-recorded")
        if route == "session":
            self.generation += 1
            return dict(status="SESSION_ACCEPTED", principal="oracle-research-live", worker_id=packet["worker_id"],
                        session_id="site-" + str(self.generation), generation=self.generation, lease_id="lease", heartbeat_interval_ms=10000)
        existing = self.events.get(packet["event_id"])
        if existing:
            assert existing[0] == packet
            return dict(status="DUPLICATE_IGNORED", event_id=packet["event_id"], cursor=existing[1])
        cursor = len(self.events) + 1
        self.events[packet["event_id"]] = (deepcopy(packet), cursor)
        return dict(status="APPLIED", event_id=packet["event_id"], cursor=cursor)


class OracleLiveProjectionTests(unittest.TestCase):
    def fixture(self):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        site = NativeSite(); projection = LiveProjection(site, Path(temporary.name))
        self.addCleanup(projection.stop.set)
        event = dict(event_id="task-g2-001", session_id="task-g2", worker_id="oracle-research.fundamental_events",
                     action_id="task", generation=2, event_seq=1, emitted_at="2026-10-20T11:00:00Z", event_type="ACTION_STARTED")
        return site, projection, event

    def test_explicit_lane_activity_session_mapping_heartbeat_and_real_stdout_proof(self):
        site, projection, event = self.fixture()
        projection.started(event, "fundamental_events", "document_or_fundamental_research", "a" * 40)
        projection._post_event("WORKER_HEARTBEAT", "hb-1", {}, event["emitted_at"])
        projection.terminal = dict(event, event_id="task-g2-002", event_type="ACTION_COMPLETED", event_seq=2, source_commit="b" * 40)
        stdout = b'{"status":"READY","hosted_model_calls":0}\n'
        projection.finished(stdout, 0); count = len(site.requests); projection.finished(stdout, 0)
        self.assertEqual(len(site.requests), count)
        packets = [p for route, p in site.requests if route == "event"]
        self.assertEqual(packets[0]["payload"]["ui_activity"], "document-reading")
        self.assertEqual(packets[0]["payload"]["ui_role"], "researcher")
        self.assertEqual(packets[1]["payload"], {})
        self.assertEqual(packets[2]["effect_proof"]["stdout_sha256"], hashlib.sha256(stdout).hexdigest())
        self.assertEqual(packets[2]["event_seq"], 3)
        self.assertEqual(projection.receipt()["canonical_terminal"]["event_seq"], 2)
        self.assertEqual(projection.receipt()["site_session"]["generation"], 1)
        self.assertEqual(projection.receipt()["source"]["generation"], 2)
        self.assertEqual(packets[-1]["event_type"], "SESSION_ENDED")

    def test_site_failure_cannot_roll_back_science_and_stale_start_is_not_replayed(self):
        site, projection, event = self.fixture(); site.failure = True
        class Store:
            committed = False
            def commit(self, snapshot, writes, **kwargs): self.committed = True; return "a" * 40
        store = Store()
        observer = ProjectionStore(store, projection, lambda s, t: "fundamental_events", lambda t, l: "legacy_duplicate_check")
        writes = {"research/research_os/events/task/e.json": event,
                  "research/research_os/tasks/task.json": {"task_id": "task"}}
        before = deepcopy(writes)
        self.assertEqual(observer.commit(object(), writes), "a" * 40)
        self.assertTrue(store.committed); self.assertEqual(writes, before)
        self.assertNotIn("sensitive-error", json.dumps(projection.receipt()))
        restarted = LiveProjection(site, projection.state)
        self.assertIsNone(restarted.source)
        self.assertEqual(len(site.requests), 1)

    def test_failed_canonical_cas_never_opens_a_site_session(self):
        site, projection, event = self.fixture()
        class Store:
            def commit(self, *args, **kwargs): raise RuntimeError("HEAD_CHANGED")
        observer = ProjectionStore(Store(), projection, lambda s, t: "fundamental_events", lambda t, l: "legacy_duplicate_check")
        with self.assertRaises(RuntimeError):
            observer.commit(object(), {"research/research_os/events/task/e.json": event})
        self.assertEqual(site.requests, [])

    def test_http_uncertain_event_retry_preserves_identity_and_never_logs_authorization(self):
        site, projection, event = self.fixture()
        class Opener:
            requests = []
            def open(self, request, timeout):
                self.requests.append(request)
                self.authorization = request.get_header("Authorization")
                if len(self.requests) == 1: raise TimeoutError()
                class Response:
                    def __enter__(self): return self
                    def __exit__(self, *args): pass
                    def read(self, limit): return b'{"status":"DUPLICATE_IGNORED","event_id":"e","cursor":1}'
                return Response()
        opener = Opener()
        transport = SiteTransport("fixture-key-not-a-secret", opener=opener)
        ack = transport.post("event", {"event_id": "e"})
        self.assertEqual(ack["status"], "DUPLICATE_IGNORED")
        self.assertEqual(opener.requests[0].data, opener.requests[1].data)
        self.assertEqual(opener.authorization, "Bearer fixture-key-not-a-secret")
        with self.assertRaises(ValueError): SiteTransport("fixture-key", "http://other.invalid")
        with self.assertRaises(ValueError): transport.post("other", {})

    def test_unknown_activity_has_no_business_motion_and_economic_animation_is_absent(self):
        site, projection, event = self.fixture()
        projection.started(event, "fundamental_events", "unknown_stage", "a" * 40)
        projection.finished(b"interrupted\n", 1)
        packet = next(p for route, p in site.requests if route == "event")
        self.assertEqual(packet["payload"]["ui_activity"], "none")
        self.assertNotIn("calculation-economic-look", json.dumps(site.requests))
        self.assertNotIn('"owner"', json.dumps(site.requests))

    def test_local_receipt_retention_is_bounded_and_never_replays_starts(self):
        site, projection, event = self.fixture()
        for i in range(260): (projection.state / (str(i) + '.json')).write_text('{}')
        resumed = LiveProjection(site, projection.state)
        self.assertEqual(len(list(projection.state.glob('*.json'))), 255)
        self.assertIsNone(resumed.source)
        self.assertEqual(site.requests, [])

    def test_real_git_claim_observed_only_after_cas_and_restart_uses_new_generation(self):
        from research.research_os.tests import test_oracle_worker as fixture
        from research.research_os.oracle_worker import routing, next_stage
        from research.research_os.oracle_worker_v2 import build_v2_worker
        harness = fixture.WorkerTests(); harness.setUp(); self.addCleanup(harness.tearDown)
        harness.producer()
        from datetime import datetime, timezone
        harness.now = datetime(2026, 10, 20, 11, tzinfo=timezone.utc)
        site, projection, _ = self.fixture()
        config = dict(research_contract_version="v2-core", worker_id="oracle-research", release_sha="f" * 40)
        observer = ProjectionStore(harness.store, projection, routing, next_stage)
        worker = build_v2_worker(config, store=observer, backend=harness.model); worker.now = lambda: harness.now
        def crash(point):
            if point == "after_claim": raise RuntimeError("ACTUAL_CLAIM_INTERRUPT_FIXTURE")
        worker.fault = crash
        with self.assertRaises(RuntimeError): worker.wake()
        first = harness.read("tasks/PRODUCER-TEST.json")
        self.assertEqual(first["status"], "CLAIMED")
        self.assertEqual(projection.source["session_id"], first["execution"]["session_id"])
        projection.stop.set(); projection.thread.join(timeout=1)
        harness.now += timedelta(seconds=601)
        recovered = LiveProjection(site, projection.state)
        self.addCleanup(recovered.stop.set)
        resumed = build_v2_worker(config, store=ProjectionStore(harness.store, recovered, routing, next_stage), backend=harness.model)
        resumed.now = lambda: harness.now
        result = resumed.wake(); recovered.finished((json.dumps(result) + "\n").encode(), 0)
        second = harness.read("tasks/PRODUCER-TEST.json")
        self.assertEqual(second["lease"]["generation"], 2)
        self.assertNotEqual(projection.source["event_id"], recovered.source["event_id"])
        self.assertEqual(site.generation, 2)
        with harness.store.snapshot() as snapshot:
            self.assertEqual(len([p for p in snapshot.blobs if p.startswith("research/research_os/receipts/PRODUCER-TEST/")]), 1)


if __name__ == "__main__": unittest.main()
