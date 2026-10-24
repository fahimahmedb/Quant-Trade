"""Existing watchdog cannot infer liveness from ambiguous time or duration proof."""
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
import json
from types import SimpleNamespace
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

from autonomous_research.runtime import CampaignState, PersistentQueue, ResearchTask
from autonomous_research.watchdog import inspect_health, is_lease_stale

NOW = datetime(2026, 10, 24, 12, tzinfo=timezone.utc)


def running(start, lease=600):
    return ResearchTask('running', 'synthetic', 1, 'clock proof only', 'fake',
                        status='RUNNING', started_at=start, lease_seconds=lease)


@pytest.mark.parametrize('age,stale', [(599.999999, False), (600, True), (600.000001, True), (0, False), (-0.000001, True)])
def test_lease_expiry_has_an_exact_boundary_and_no_future_start(age, stale):
    assert is_lease_stale(running((NOW - timedelta(seconds=age)).isoformat()), NOW) is stale


@pytest.mark.parametrize('start', [None, '', 'not-a-clock', '2026-10-24',
                                   '2026-10-24T11:59:59', 123, {}, [], True,
                                   '2026-10-24T11:59:60+00:00'])
def test_missing_malformed_or_timezone_ambiguous_start_is_conservatively_stale(start):
    assert is_lease_stale(running(start), NOW) is True


@pytest.mark.parametrize('lease', [float('nan'), float('inf'), float('-inf'),
                                  10**400, None, '600', {}, [], True, False, 0, -1])
def test_unqualified_lease_duration_cannot_prove_worker_health(lease):
    assert is_lease_stale(running(NOW.isoformat(), lease), NOW) is True


@pytest.mark.parametrize('start', ['2026-10-24T12:00:00Z', '2026-10-24T14:00:00+02:00',
                                   '2026-10-24T05:00:00-07:00'])
def test_valid_offset_spellings_are_the_same_instant(start):
    assert is_lease_stale(running(start, 0.25), NOW) is False
    assert is_lease_stale(running(start, 0.25), NOW + timedelta(seconds=0.25)) is True


def test_missing_duration_retains_existing_default():
    task = SimpleNamespace(started_at=(NOW - timedelta(seconds=599)).isoformat())
    assert is_lease_stale(task, NOW) is False
    assert is_lease_stale(task, NOW + timedelta(seconds=1)) is True


@pytest.mark.parametrize('now', [datetime(2026, 10, 24, 12), None, '2026-10-24T12:00:00Z'])
def test_unqualified_observer_clock_cannot_prove_lease_health(now):
    assert is_lease_stale(running(NOW.isoformat()), now) is True


def test_clock_fold_is_measured_as_elapsed_utc_time():
    zone = ZoneInfo('America/New_York')
    first = datetime(2026, 11, 1, 1, 30, fold=0, tzinfo=zone)
    second = datetime(2026, 11, 1, 1, 30, fold=1, tzinfo=zone)
    assert is_lease_stale(running(first.isoformat(), 3599), second) is True
    assert is_lease_stale(running(first.isoformat(), 3601), second) is False


class FixedClock(datetime):
    @classmethod
    def now(cls, tz=None):
        assert tz == timezone.utc
        return cls.fromtimestamp(NOW.timestamp(), timezone.utc)


def health(state, queue, **kwargs):
    with patch('autonomous_research.watchdog.datetime', FixedClock):
        return inspect_health(state, queue, **kwargs)


@pytest.mark.parametrize('heartbeat', [None, '', 'broken', '2026-10-24T12:00:00',
                                       '2026-10-24', {}, [], 42,
                                       '2026-10-24T12:00:00.000001+00:00'])
def test_invalid_or_future_heartbeat_alert_does_not_hide_other_faults(tmp_path, heartbeat):
    queue = PersistentQueue(tmp_path / 'queue.json')
    queue.add(running('broken'))
    queue.add(ResearchTask('failed', 'synthetic', 1, 'repeat', 'fake', status='FAILED', attempts=3))
    queue.add(ResearchTask('ready', 'synthetic', 1, 'due', 'fake'))
    state = CampaignState('local', last_heartbeat=heartbeat)
    state_before, queue_before = asdict(state), queue.path.read_bytes()
    alerts = health(state, queue)
    codes = {a['code'] for a in alerts}
    assert {'HEARTBEAT_MISSING', 'WORKER_STUCK', 'REPEATED_CRASH', 'QUEUE_STARVATION'} <= codes
    assert all(isinstance(a['detail'], str) for a in alerts)
    assert asdict(state) == state_before
    assert queue.path.read_bytes() == queue_before
    assert not (tmp_path / 'campaign.json').exists()


@pytest.mark.parametrize('age,missing', [(299.999999, False), (300, True), (300.000001, True), (0, False)])
def test_heartbeat_timeout_boundary_is_exact(tmp_path, age, missing):
    queue = PersistentQueue(tmp_path / 'queue.json')
    state = CampaignState('local', last_heartbeat=(NOW - timedelta(seconds=age)).isoformat())
    assert ('HEARTBEAT_MISSING' in {a['code'] for a in health(state, queue)}) is missing


@pytest.mark.parametrize('timeout', [float('nan'), float('inf'), True, -1, '300', None])
def test_invalid_timeout_configuration_is_explicit_not_a_healthy_inspection(tmp_path, timeout):
    state = CampaignState('local', last_heartbeat=NOW.isoformat())
    queue = PersistentQueue(tmp_path / 'queue.json')
    with pytest.raises(ValueError, match='heartbeat timeout'):
        health(state, queue, heartbeat_timeout_seconds=timeout)


def test_one_malformed_running_task_does_not_suppress_other_worker_alerts(tmp_path):
    queue = PersistentQueue(tmp_path / 'queue.json')
    malformed = running('broken')
    valid = running((NOW - timedelta(seconds=601)).isoformat())
    valid.task_id = 'expired'
    healthy = running(NOW.isoformat())
    healthy.task_id = 'healthy'
    for t in [malformed, valid, healthy]:
        queue.add(t)
    state = CampaignState('local', status='RUNNING', last_heartbeat=NOW.isoformat())
    before = queue.path.read_bytes()
    for _ in range(2):
        alerts = health(state, queue)
        assert {a['detail'] for a in alerts if a['code'] == 'WORKER_STUCK'} == {'running', 'expired'}
    assert queue.path.read_bytes() == before
    reloaded = PersistentQueue(queue.path)
    assert health(state, reloaded) == alerts
    assert json.loads(before)['version'] == 1


def test_zero_timeout_explicitly_expires_current_heartbeat(tmp_path):
    state = CampaignState('local', last_heartbeat=NOW.isoformat())
    queue = PersistentQueue(tmp_path / 'queue.json')
    assert health(state, queue, heartbeat_timeout_seconds=0) == [
        {'code': 'HEARTBEAT_MISSING', 'detail': NOW.isoformat()}]
