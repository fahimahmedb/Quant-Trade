import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from research.research_os.live_lab_bridge import (
    LiveLabProjectionStore,
    LiveLabProjectionError,
    LocalLiveLabOutbox,
    project_live_event,
)
from research.research_os.live_lab_emitter import (
    LiveLabDeliveryError,
    SiteClient,
    SiteConfig,
    deliver_pending,
)


class DummyStore:
    def __init__(self):
        self.repository = "owner/repo"
        self.branch = "branch"
        self.commits = []
        self.last_preflight = {"status": "PASS"}

    def commit(self, snapshot, writes, **kwargs):
        self.commits.append((writes, kwargs))
        return "c" * 40


class FakeResponse:
    def __init__(self, body=b'{"status":"ACCEPTED"}', status=200):
        self.body = body
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit):
        return self.body[:limit]

    def getcode(self):
        return self.status


def event(kind="ACTION_COMPLETED", stage="mechanism_research"):
    payload = {"stage": stage, "result": "READY", "queue_state": "QUEUED"} if stage else {}
    return {
        "event_id": "SESSION-1-2",
        "session_id": "SESSION-1",
        "worker_id": "oracle-research-v2.market_discovery",
        "action_id": "TASK-1",
        "event_type": kind,
        "event_seq": 2,
        "generation": 1,
        "emitted_at": "2026-10-20T11:40:10Z",
        "payload": payload,
    }


class LiveLabBridgeTests(unittest.TestCase):
    def test_projection_preserves_source_identity_and_adds_allowlisted_ui_metadata(self):
        source = event()
        projected = project_live_event(source, {})
        self.assertEqual(projected["worker_id"], source["worker_id"])
        self.assertEqual(projected["event_id"], source["event_id"])
        self.assertEqual(projected["payload"]["ui_activity"], "hypothesis-generation")
        self.assertEqual(projected["payload"]["ui_role"], "researcher")
        self.assertEqual(projected["payload"]["ui_label"], "Oracle · Discovery")
        self.assertNotIn("ui_activity", source["payload"])

    def test_heartbeat_without_stage_never_invents_business_motion(self):
        source = event(kind="HEARTBEAT", stage=None)
        projected = project_live_event(source, {})
        self.assertEqual(projected["payload"]["ui_activity"], "none")
        self.assertNotIn("ui_role", projected["payload"])

    def test_action_started_uses_claimed_task_context(self):
        source = event(kind="ACTION_STARTED", stage=None)
        source["event_seq"] = 1
        task = {
            "task_id": "TASK-1",
            "task_type": "QUANT_RESEARCH",
            "lease": {"generation": 1},
            "execution": {"completed_stages": {}},
        }
        writes = {"research/research_os/tasks/TASK-1.json": task}
        with patch("research.research_os.live_lab_bridge.next_stage", return_value="mechanism_research"):
            projected = project_live_event(source, writes)
        self.assertEqual(projected["payload"]["ui_activity"], "hypothesis-generation")

    def test_outbox_is_idempotent_and_collision_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            outbox = LocalLiveLabOutbox(Path(tmp))
            projected = project_live_event(event(), {})
            first = outbox.enqueue(projected)
            second = outbox.enqueue(projected)
            self.assertEqual(first, second)
            altered = dict(projected)
            altered["payload"] = dict(projected["payload"], queue_state="IDLE")
            with self.assertRaisesRegex(LiveLabProjectionError, "EVENT_ID_COLLISION"):
                outbox.enqueue(altered)

    def test_projection_store_only_enqueues_after_authoritative_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            inner = DummyStore()
            outbox = LocalLiveLabOutbox(Path(tmp))
            store = LiveLabProjectionStore(inner, outbox)
            path = "research/research_os/events/TASK-1/SESSION-1-002.json"
            store.commit(object(), {path: event()})
            self.assertEqual(len(inner.commits), 1)
            self.assertEqual(len(outbox.pending()), 1)

    def test_site_config_is_pinned_and_secret_repr_is_redacted(self):
        env = {
            "QT_ORACLE_SITE_BASE_URL": "https://quant-trade-lab.sassylime.chatgpt.site",
            "QT_ORACLE_INGRESS_KEY": "top-secret",
            "QT_ORACLE_PRINCIPAL": "oracle-research-live",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = SiteConfig.from_env()
        self.assertEqual(cfg.principal, "oracle-research-live")
        self.assertNotIn("top-secret", repr(cfg))
        bad = dict(env, QT_ORACLE_SITE_BASE_URL="https://example.com")
        with patch.dict(os.environ, bad, clear=True):
            with self.assertRaisesRegex(LiveLabDeliveryError, "ORIGIN_NOT_PINNED"):
                SiteConfig.from_env()

    def test_existing_site_prefix_rejects_current_v2_worker_identity_without_rewrite(self):
        cfg = SiteConfig(
            "https://quant-trade-lab.sassylime.chatgpt.site",
            "secret-value",
            "oracle-research-live",
        )
        client = SiteClient(cfg, opener=lambda *args, **kwargs: FakeResponse())
        with self.assertRaisesRegex(LiveLabDeliveryError, "WORKER_PREFIX_MISMATCH"):
            client.deliver_event(event())

    def test_emitter_sends_bearer_without_rewriting_worker_identity_when_prefix_matches(self):
        requests = []

        def opener(request, timeout):
            requests.append(request)
            return FakeResponse()

        cfg = SiteConfig(
            "https://quant-trade-lab.sassylime.chatgpt.site",
            "secret-value",
            "oracle-research-live",
            "oracle-research-v2.",
        )
        client = SiteClient(cfg, opener=opener)
        client.ensure_session(event())
        client.deliver_event(event())
        self.assertEqual(len(requests), 2)
        self.assertTrue(requests[0].full_url.endswith("/api/oracle/session"))
        self.assertTrue(requests[1].full_url.endswith("/api/oracle/event"))
        self.assertEqual(requests[0].headers["Authorization"], "Bearer secret-value")
        posted = json.loads(requests[1].data)
        self.assertEqual(posted["worker_id"], "oracle-research-v2.market_discovery")

    def test_delivery_keeps_session_marker_and_moves_event_to_sent(self):
        calls = []

        def opener(request, timeout):
            calls.append(request.full_url)
            return FakeResponse()

        cfg = SiteConfig(
            "https://quant-trade-lab.sassylime.chatgpt.site",
            "secret-value",
            "oracle-research-live",
            "oracle-research-v2.",
        )
        with tempfile.TemporaryDirectory() as tmp:
            outbox = LocalLiveLabOutbox(Path(tmp))
            outbox.enqueue(project_live_event(event(), {}))
            result = deliver_pending(outbox, SiteClient(cfg, opener=opener))
            self.assertEqual(result["delivered"], 1)
            self.assertEqual(result["pending"], 0)
            self.assertEqual(len(calls), 2)
            self.assertEqual(len(list(outbox.sent_dir.glob("*.json"))), 1)


if __name__ == "__main__":
    unittest.main()
