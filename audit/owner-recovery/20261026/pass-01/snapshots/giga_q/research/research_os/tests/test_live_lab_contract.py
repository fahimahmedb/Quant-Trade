import unittest
from datetime import datetime, timezone

from research.research_os.live_lab_contract import (
    FORBIDDEN_UI_ACTIVITIES,
    assert_live_ui_contract,
    live_ui_metadata,
)
from research.research_os.oracle_live_worker import LiveLabResearchOSWorker


class DummyStore:
    pass


class DummyExecutor:
    pass


class LiveLabContractTests(unittest.TestCase):
    def test_explicit_stage_mapping_is_truth_preserving(self):
        docs = live_ui_metadata('fundamental_events', 'document_or_fundamental_research')
        self.assertEqual(docs, {
            'ui_role': 'researcher',
            'ui_label': 'Oracle · Documents',
            'ui_activity': 'document-reading',
        })
        discovery = live_ui_metadata('market_discovery', 'mechanism_research')
        self.assertEqual(discovery['ui_activity'], 'hypothesis-generation')
        self.assertNotIn(discovery['ui_activity'], FORBIDDEN_UI_ACTIVITIES)
        self.assertEqual(live_ui_metadata('fundamental_events', 'future_unknown_stage')['ui_activity'], 'none')
        with self.assertRaisesRegex(ValueError, 'LIVE_LAB_UNKNOWN_CANONICAL_LANE'):
            live_ui_metadata('invented_lane', 'mechanism_research')
        assert_live_ui_contract()

    def test_wrapper_enriches_existing_events_only(self):
        worker = LiveLabResearchOSWorker(
            DummyStore(),
            lane='auto',
            worker_id='oracle-research',
            release_sha='a' * 40,
            executor=DummyExecutor(),
            now=lambda: datetime(2026, 10, 20, 2, 10, tzinfo=timezone.utc),
        )
        task = {
            'task_id': 'FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-TEST',
            'task_type': 'FUNDAMENTAL_RESEARCH',
            'lease': {'generation': 4},
            'execution': {'completed_stages': {'legacy_duplicate_check': {}}},
        }
        started = worker._event(task, 'session-g4', 'fundamental_events', 1, 'ACTION_STARTED', {'queue_state': 'WORKING'})
        self.assertEqual(started['payload']['ui_role'], 'researcher')
        self.assertEqual(started['payload']['ui_label'], 'Oracle · Documents')
        self.assertEqual(started['payload']['ui_activity'], 'document-reading')
        self.assertNotIn('progress', started['payload'])
        self.assertNotIn('economic_result', started['payload'])
        self.assertNotIn('authority', started['payload'])

        completed = worker._event(task, 'session-g4', 'fundamental_events', 2, 'ACTION_COMPLETED', {
            'stage': 'document_or_fundamental_research',
            'result': 'READY',
        })
        self.assertEqual(completed['payload']['ui_activity'], 'document-reading')

        heartbeat = worker._event(task, 'session-g4', 'fundamental_events', 3, 'WORKER_HEARTBEAT', {})
        self.assertFalse(any(key.startswith('ui_') for key in heartbeat['payload']))


if __name__ == '__main__':
    unittest.main()
