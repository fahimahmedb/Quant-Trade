"""CP044: a durable pause is control state, including during worker settlement."""
from concurrent.futures import ThreadPoolExecutor
import json
import threading
from unittest.mock import patch

import pytest

from autonomous_research import runtime
from autonomous_research.orchestrator import ResearchCampaign
from autonomous_research.runtime import ResearchTask
from quant.state import write_json


def task(name, priority=1):
    return ResearchTask(name, 'synthetic', priority, 'local control fixture', 'fake', data_fingerprint='v1')


def result(t):
    return {'ticket_id': t.task_id, 'lesson': 'synthetic control only', 'outcome': 'SYNTHETIC_ONLY'}


@pytest.mark.parametrize('reason', ['', None, 'maintenance'])
@pytest.mark.parametrize('restart', [False, True])
def test_pause_without_explanation_stays_closed_until_explicit_resume(tmp_path, reason, restart):
    calls = []
    worker = lambda t: (calls.append(t.task_id), result(t))[1]
    campaign = ResearchCampaign(tmp_path, workers={'fake': worker})
    campaign.enqueue(task('one'))
    campaign.pause('maintenance' if reason is None else reason)
    if reason is None:
        campaign.state.pause_reason = None  # the existing wire field is optional
        campaign.state.save(campaign.state_path)
    if restart:
        campaign = ResearchCampaign(tmp_path, workers={'fake': worker})
    before_queue = campaign.queue.path.read_bytes()
    for _ in range(2):
        assert campaign.run_once() == 'PAUSED'
    assert calls == []
    assert campaign.queue.path.read_bytes() == before_queue
    assert campaign.queue.tasks['one'].attempts == campaign.state.cycles_completed == 0
    assert json.loads(campaign.state_path.read_text())['status'] == 'PAUSED'
    campaign.resume()
    assert campaign.run_once() == 'COMPLETED'
    assert campaign.run_once() == 'IDLE'
    assert calls == ['one']


@pytest.mark.parametrize('reason', ['', 'maintenance'])
@pytest.mark.parametrize('worker_fails', [False, True])
@pytest.mark.parametrize('next_task', [False, True])
@pytest.mark.parametrize('pause_fault', ['none', 'before_write', 'after_write'])
def test_acknowledged_or_proven_durable_pause_survives_inflight_settlement(tmp_path, reason, worker_fails, next_task, pause_fault):
    entered, release = threading.Event(), threading.Event()
    calls = []

    def worker(t):
        calls.append(t.task_id)
        if t.task_id == 'one':
            entered.set()
            assert release.wait(5)
            if worker_fails:
                raise RuntimeError('synthetic worker failure')
        return result(t)

    campaign = ResearchCampaign(tmp_path, workers={'fake': worker})
    campaign.enqueue(task('one', 2))
    if next_task:
        campaign.enqueue(task('two'))
    injected = []

    def publication(path, document):
        if document.get('status') == 'PAUSED' and not injected and pause_fault != 'none':
            injected.append(pause_fault)
            if pause_fault == 'after_write':
                write_json(path, document)
            raise OSError('injected pause persistence/ACK failure')
        write_json(path, document)

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(campaign.run_once)
        try:
            assert entered.wait(5)
            with patch.object(runtime, '_write_json', side_effect=publication):
                if pause_fault == 'none':
                    campaign.pause(reason)
                else:
                    with pytest.raises(OSError):
                        campaign.pause(reason)
                    if pause_fault == 'before_write':
                        assert json.loads(campaign.state_path.read_text())['status'] == 'RUNNING'
                        campaign.pause(reason)  # a real retry is necessary before claiming pause
                assert json.loads(campaign.state_path.read_text())['status'] == 'PAUSED'
        finally:
            release.set()
        assert future.result(timeout=5) in {'COMPLETED', 'FAILED', 'PAUSED'}
    assert calls == ['one']
    assert campaign.state.status == 'PAUSED'
    assert json.loads(campaign.state_path.read_text())['status'] == 'PAUSED'
    assert campaign.state.cycles_completed == (0 if worker_fails else 1)
    assert campaign.queue.tasks['one'].status == ('FAILED' if worker_fails else 'COMPLETED')
    assert campaign.run_once() == 'PAUSED'
    if next_task:
        assert campaign.queue.tasks['two'].status == 'PENDING'
        campaign.resume()
        assert campaign.run_once() == 'COMPLETED'
        assert calls == ['one', 'two']


@pytest.mark.parametrize('has_task', [False, True])
def test_pause_after_initial_entry_check_cannot_be_lost_before_dispatch_or_idle(tmp_path, has_task):
    calls = []
    campaign = ResearchCampaign(tmp_path, workers={'fake': lambda t: (calls.append(t.task_id), result(t))[1]})
    if has_task:
        campaign.enqueue(task('one'))
    selected, release = threading.Event(), threading.Event()
    due = campaign.queue.next_due
    visits = []

    def pause_selection(*args, **kwargs):
        answer = due(*args, **kwargs)
        visits.append(True)
        if len(visits) == 1:
            selected.set()
            assert release.wait(5)
        return answer

    with patch.object(campaign.queue, 'next_due', side_effect=pause_selection):
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(campaign.run_once)
            try:
                assert selected.wait(5)
                campaign.pause('')
                assert json.loads(campaign.state_path.read_text())['status'] == 'PAUSED'
            finally:
                release.set()
            assert future.result(timeout=5) == 'PAUSED'
    assert calls == []
    assert campaign.state.status == 'PAUSED'
    if has_task:
        assert campaign.queue.tasks['one'].status == 'PENDING'


def test_worker_can_pause_its_own_campaign_without_completion_reopening_it(tmp_path):
    calls = []

    def worker(t):
        calls.append(t.task_id)
        campaign.pause('local boundary found')
        return result(t)

    campaign = ResearchCampaign(tmp_path, workers={'fake': worker})
    campaign.enqueue(task('one', 2))
    campaign.enqueue(task('two'))
    assert campaign.run_once() == 'COMPLETED'
    assert campaign.run_once() == 'PAUSED'
    assert calls == ['one']
    assert campaign.queue.tasks['two'].status == 'PENDING'


def test_resume_is_not_permission_to_bypass_completed_cycle_budget(tmp_path):
    calls = []
    campaign = ResearchCampaign(tmp_path, max_cycles=1,
                                workers={'fake': lambda t: (calls.append(t.task_id), result(t))[1]})
    campaign.enqueue(task('one', 2))
    campaign.enqueue(task('two'))
    assert campaign.run_once() == 'COMPLETED'
    campaign.pause('')
    campaign.resume()
    assert campaign.run_once() == 'PAUSED'
    assert calls == ['one']
    assert campaign.queue.tasks['two'].status == 'PENDING'
    campaign.state.research_budget['max_cycles'] = 2
    campaign.state.save(campaign.state_path)
    campaign.resume()
    assert campaign.run_once() == 'COMPLETED'
    assert calls == ['one', 'two']
    assert campaign.state.cycles_completed == campaign.state.budget_consumed['cycles'] == 2


@pytest.mark.parametrize('publication_outcome', ['success', 'before_write', 'after_write'])
def test_pause_publication_and_worker_settlement_do_not_erase_each_other(tmp_path, publication_outcome):
    entered, release_worker = threading.Event(), threading.Event()
    worker_returned, settlement_write = threading.Event(), threading.Event()
    pause_publishing, release_pause = threading.Event(), threading.Event()

    def worker(t):
        entered.set()
        assert release_worker.wait(5)
        worker_returned.set()
        return result(t)

    campaign = ResearchCampaign(tmp_path, workers={'fake': worker})
    campaign.enqueue(task('one'))
    original_queue_save = campaign.queue.save

    def save_queue():
        if campaign.queue.tasks['one'].status == 'COMPLETED':
            settlement_write.set()
        return original_queue_save()

    injected = []

    def publication(path, document):
        if document.get('status') == 'PAUSED' and not injected:
            injected.append(True)
            pause_publishing.set()
            assert release_pause.wait(5)
            if publication_outcome != 'before_write':
                write_json(path, document)
            if publication_outcome != 'success':
                raise OSError('pause publication fault')
        else:
            write_json(path, document)

    with patch.object(campaign.queue, 'save', side_effect=save_queue):
        with ThreadPoolExecutor(max_workers=2) as pool:
            attempt = pool.submit(campaign.run_once)
            assert entered.wait(5)
            with patch.object(runtime, '_write_json', side_effect=publication):
                pause = pool.submit(campaign.pause, 'maintenance')
                try:
                    assert pause_publishing.wait(5)
                    release_worker.set()
                    assert worker_returned.wait(5)
                    # Give the returning worker a turn while pause publication is
                    # held. This probes overlapping settlement, not a timed expiry.
                    settlement_write.wait(0.2)
                finally:
                    release_pause.set()
                if publication_outcome == 'success':
                    pause.result(timeout=5)
                else:
                    with pytest.raises(OSError):
                        pause.result(timeout=5)
                assert attempt.result(timeout=5) == 'COMPLETED'
    persisted = json.loads(campaign.state_path.read_text())
    assert campaign.queue.tasks['one'].status == 'COMPLETED'
    assert persisted['cycles_completed'] == campaign.state.cycles_completed == 1
    assert persisted['budget_consumed']['cycles'] == 1
    assert persisted['processed_data_fingerprints'] == [task('one').execution_key]
    assert persisted['last_completed_ticket_id'] == 'one'
    assert persisted['status'] == ('RUNNING' if publication_outcome == 'before_write' else 'PAUSED')
