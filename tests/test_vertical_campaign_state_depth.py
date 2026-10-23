"""CP042: a stale campaign heartbeat must not erase pause or completed research truth."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
import json
import subprocess
import sys
import threading
from unittest.mock import patch

import pytest

from autonomous_research import runtime
from quant.state import write_json


def loaded(tmp_path):
    path = tmp_path / 'campaign.json'
    state = runtime.CampaignState.load_or_create(path, 'SYN-CAMPAIGN')
    return path, state


@pytest.mark.parametrize('terminal', ['PAUSED', 'STOPPED'])
def test_stale_heartbeat_cannot_undo_acknowledged_owner_state(tmp_path, terminal):
    path, owner = loaded(tmp_path)
    stale = runtime.CampaignState.load_or_create(path, 'ignored-existing-identity')
    owner.status = terminal
    owner.pause_reason = 'owner diagnostic hold'
    owner.save(path)
    durable = path.read_bytes()
    with pytest.raises(RuntimeError, match='CAMPAIGN_CHANGED_SINCE_READ'):
        stale.heartbeat(path)
    assert path.read_bytes() == durable
    assert asdict(stale) == asdict(owner)
    stale.heartbeat(path)
    assert runtime.CampaignState.load_or_create(path, 'ignored').status == terminal


def test_stale_save_cannot_erase_completed_fingerprint_or_budget(tmp_path):
    path, first = loaded(tmp_path)
    stale = runtime.CampaignState.load_or_create(path, 'ignored')
    first.cycles_completed = 7
    first.processed_data_fingerprints.append('ticket@data-v1')
    first.budget_consumed['cycles'] = 7
    first.save(path)
    stale.latest_lesson = 'uncommitted stale view'
    with pytest.raises(RuntimeError, match='CAMPAIGN_CHANGED_SINCE_READ'):
        stale.save(path)
    recovered = runtime.CampaignState.load_or_create(path, 'ignored')
    assert asdict(stale) == asdict(recovered) == asdict(first)
    assert recovered.processed_data_fingerprints == ['ticket@data-v1']


@pytest.mark.parametrize('after_commit', [False, True])
def test_failed_save_recovers_actual_durable_truth_and_retry_does_not_invent_completion(tmp_path, after_commit):
    path, state = loaded(tmp_path)
    original = asdict(state)
    state.cycles_completed = 3
    state.budget_consumed['cycles'] = 3
    attempted = asdict(state)

    def fail(target, document):
        if after_commit:
            write_json(target, document)
        raise OSError('injected persistence failure or lost ACK')

    with patch.object(runtime, '_write_json', side_effect=fail):
        with pytest.raises(OSError):
            state.save(path)
    expected = attempted if after_commit else original
    assert asdict(state) == expected
    assert asdict(runtime.CampaignState.load_or_create(path, 'ignored')) == expected
    # Exact retry acknowledges the observed body without an unnecessary rewrite.
    before = path.read_bytes()
    with patch.object(runtime, '_write_json', side_effect=AssertionError('idempotent retry must not rewrite')):
        state.save(path)
    assert path.read_bytes() == before
    if not after_commit:
        state.cycles_completed = state.budget_consumed['cycles'] = 3
        state.save(path)
        assert asdict(runtime.CampaignState.load_or_create(path, 'ignored')) == attempted


@pytest.mark.parametrize('target', ['os.open', 'fcntl.flock', 'pathlib.Path.mkdir'])
def test_lock_setup_failure_restores_checked_state_before_retry(tmp_path, target):
    path, state = loaded(tmp_path)
    before = asdict(state)
    state.latest_lesson = 'must not pretend to be saved'
    with patch(target, side_effect=OSError('injected lock setup failure')):
        with pytest.raises(OSError):
            state.save(path)
    assert asdict(state) == before
    state.latest_lesson = 'real retry'
    state.save(path)
    assert runtime.CampaignState.load_or_create(path, 'ignored').latest_lesson == 'real retry'


def test_unserializable_pending_state_does_not_poison_recovery(tmp_path):
    path, state = loaded(tmp_path)
    before = asdict(state)
    state.research_budget['max_cycles'] = float('nan')
    with pytest.raises(ValueError):
        state.save(path)
    assert asdict(state) == before
    assert json.loads(path.read_text()) == before


def test_independent_processes_cannot_both_acknowledge_conflicting_stale_campaigns(tmp_path):
    path, _ = loaded(tmp_path)
    code = '''
import sys
from pathlib import Path
from autonomous_research.runtime import CampaignState
state = CampaignState.load_or_create(Path(sys.argv[1]), 'ignored')
print('READY', flush=True)
sys.stdin.readline()
state.latest_lesson = sys.argv[2]
try:
    state.save(Path(sys.argv[1]))
except RuntimeError:
    print('CONFLICT', flush=True)
else:
    print('ACKNOWLEDGED', flush=True)
'''
    procs = [subprocess.Popen([sys.executable, '-c', code, str(path), str(i)],
                              text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
             for i in range(2)]
    try:
        for proc in procs:
            assert proc.stdout.readline().strip() == 'READY'
        results = []
        for proc in procs:
            out, err = proc.communicate('go\n', timeout=10)
            assert proc.returncode == 0, err
            results.append(out.strip())
        assert sorted(results) == ['ACKNOWLEDGED', 'CONFLICT']
        assert runtime.CampaignState.load_or_create(path, 'ignored').latest_lesson in {'0', '1'}
    finally:
        for proc in procs:
            if proc.poll() is None:
                proc.kill()
                proc.communicate(timeout=5)


@pytest.mark.parametrize('after_commit', [None, False, True])
@pytest.mark.parametrize('first_method', ['heartbeat', 'save'])
def test_shared_heartbeat_is_serialized_through_persist_and_failure_recovery(tmp_path, after_commit, first_method):
    path, state = loaded(tmp_path)
    state.latest_lesson = 'pending-first-writer'
    entered, release, second_started, second_done = (threading.Event() for _ in range(4))

    def publication(target, document):
        if threading.current_thread().name == 'first-heartbeat':
            entered.set()
            assert release.wait(5)
            if after_commit is False:
                raise OSError('before publication')
            write_json(target, document)
            if after_commit is True:
                raise OSError('after publication before ACK')
        else:
            write_json(target, document)

    def first():
        threading.current_thread().name = 'first-heartbeat'
        try:
            getattr(state, first_method)(path)
        except OSError:
            return 'error'
        return 'ok'

    def second():
        second_started.set()
        try:
            state.heartbeat(path)
        finally:
            second_done.set()

    with patch.object(runtime, '_write_json', side_effect=publication), \
         patch.object(runtime, 'utc_now', side_effect=(['2026-10-23T00:00:01+00:00', '2026-10-23T00:00:02+00:00'] if first_method == 'heartbeat' else ['2026-10-23T00:00:02+00:00'])):
        with ThreadPoolExecutor(max_workers=2) as pool:
            a = pool.submit(first)
            try:
                assert entered.wait(5)
                b = pool.submit(second)
                assert second_started.wait(5)
                assert not second_done.wait(.15)
            finally:
                release.set()
            assert a.result(timeout=5) == ('ok' if after_commit is None else 'error')
            b.result(timeout=5)
    assert asdict(state) == asdict(runtime.CampaignState.load_or_create(path, 'ignored'))
    assert state.last_heartbeat == '2026-10-23T00:00:02+00:00'


def test_valid_wire_shape_and_new_snapshot_path_keep_legacy_fields_only(tmp_path):
    path, state = loaded(tmp_path)
    expected = asdict(state)
    snapshot = tmp_path / 'snapshot.json'
    state.save(snapshot)
    assert json.loads(path.read_text()) == json.loads(snapshot.read_text()) == expected
    assert not any(k.startswith('_') for k in expected)
    assert runtime.CampaignState.load_or_create(path, 'different-requested-id').campaign_id == 'SYN-CAMPAIGN'


@pytest.mark.parametrize('alias', [True, 1.0])
def test_snapshot_fence_distinguishes_serialized_numeric_policy_identity(tmp_path, alias):
    path, state = loaded(tmp_path)
    state.research_budget['max_cycles'] = 1
    state.save(path)
    foreign = json.loads(path.read_text())
    foreign['research_budget']['max_cycles'] = alias
    write_json(path, foreign)
    before = path.read_bytes()
    state.latest_lesson = 'stale despite Python numeric equality'
    with pytest.raises(RuntimeError, match='CAMPAIGN_CHANGED_SINCE_READ'):
        state.save(path)
    assert path.read_bytes() == before


@pytest.mark.parametrize('raw', ['null', '[]', '{"campaign_id":', '{"campaign_id":"other","unsupported_field":true}'])
def test_corrupt_existing_state_is_not_silently_repaired_by_save(tmp_path, raw):
    path, state = loaded(tmp_path)
    remembered = asdict(state)
    path.write_text(raw)
    state.latest_lesson = 'must not overwrite broken evidence'
    with pytest.raises((ValueError, TypeError)):
        state.save(path)
    assert path.read_text() == raw
    assert asdict(state) == remembered


@pytest.mark.parametrize('after_write', [False, True])
def test_actual_process_death_and_fresh_load_preserve_only_committed_pause(tmp_path, after_write):
    path, stale = loaded(tmp_path)
    initial = asdict(stale)
    code = '''
import os, sys
from pathlib import Path
from autonomous_research import runtime
from quant.state import write_json
path = Path(sys.argv[1])
state = runtime.CampaignState.load_or_create(path, 'ignored')
state.status = 'PAUSED'
state.pause_reason = 'synthetic owner pause'
def die(target, payload):
    if sys.argv[2] == 'after':
        write_json(target, payload)
    os._exit(73)
runtime._write_json = die
state.save(path)
raise AssertionError('dead writer cannot return ACK')
'''
    dead = subprocess.run([sys.executable, '-c', code, str(path), 'after' if after_write else 'before'],
                          text=True, capture_output=True, timeout=10)
    assert dead.returncode == 73, dead.stderr
    assert dead.stdout == ''
    restarted = runtime.CampaignState.load_or_create(path, 'ignored')
    assert restarted.status == ('PAUSED' if after_write else initial['status'])
    if after_write:
        with pytest.raises(RuntimeError, match='CAMPAIGN_CHANGED_SINCE_READ'):
            stale.heartbeat(path)
    restarted.heartbeat(path)
    assert runtime.CampaignState.load_or_create(path, 'ignored').status == restarted.status


@pytest.mark.parametrize('same_payload', [False, True])
def test_unbound_competing_initial_publications_either_replay_or_conflict(tmp_path, same_payload):
    path = tmp_path / 'new-campaign.json'
    first = runtime.CampaignState('new')
    other = runtime.CampaignState(**asdict(first))
    if not same_payload:
        other.status = 'PAUSED'
    barrier = threading.Barrier(2)
    calls = []

    def publication(target, document):
        calls.append(deepcopy_document(document))
        write_json(target, document)

    def publish(state):
        barrier.wait(5)
        try:
            state.save(path)
            return 'ACKNOWLEDGED'
        except RuntimeError:
            return 'CONFLICT'

    with patch.object(runtime, '_write_json', side_effect=publication):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(publish, [first, other]))
    assert results.count('ACKNOWLEDGED') == (2 if same_payload else 1)
    assert len(calls) == 1
    assert asdict(first) == asdict(other) == json.loads(path.read_text())


def deepcopy_document(document):
    return json.loads(json.dumps(document))


def test_other_process_cannot_publish_while_first_persistence_is_unacknowledged(tmp_path):
    path, _ = loaded(tmp_path)
    done = tmp_path / 'second-done'
    code = '''
import sys
from pathlib import Path
from autonomous_research import runtime
from quant.state import write_json
path, mode, done = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
state = runtime.CampaignState.load_or_create(path, 'ignored')
state.latest_lesson = mode
if mode == 'first':
    def paused(target, payload):
        print('IN_PERSISTENCE', flush=True)
        sys.stdin.readline()
        write_json(target, payload)
    runtime._write_json = paused
else:
    print('STARTING', flush=True)
try:
    state.save(path)
except RuntimeError:
    result = 'CONFLICT'
else:
    result = 'ACKNOWLEDGED'
if mode == 'second':
    done.write_text(result)
print(result, flush=True)
'''
    first = subprocess.Popen([sys.executable, '-c', code, str(path), 'first', str(done)],
                             text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    second = None
    try:
        assert first.stdout.readline().strip() == 'IN_PERSISTENCE'
        second = subprocess.Popen([sys.executable, '-c', code, str(path), 'second', str(done)],
                                  text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert second.stdout.readline().strip() == 'STARTING'
        threading.Event().wait(.15)  # allow the already-started competing call to advance
        assert not done.exists(), 'second process bypassed the publication lock'
        out, err = first.communicate('release\n', timeout=10)
        assert first.returncode == 0, err
        assert out.strip() == 'ACKNOWLEDGED'
        out, err = second.communicate(timeout=10)
        assert second.returncode == 0, err
        assert out.strip() == 'CONFLICT'
        assert runtime.CampaignState.load_or_create(path, 'ignored').latest_lesson == 'first'
    finally:
        for proc in [first, second]:
            if proc is not None and proc.poll() is None:
                proc.kill()
                proc.communicate(timeout=5)


@pytest.mark.parametrize('raw', [
    '{"campaign_id":"SYN-CAMPAIGN","status":"PAUSED","status":"IDLE"}',
    '{"campaign_id":"SYN-CAMPAIGN","campaign_id":"FOREIGN"}',
    '{"campaign_id":"SYN-CAMPAIGN","budget_consumed":{"cycles":7,"cycles":0}}',
    '{"campaign_id":"SYN-CAMPAIGN","research_budget":{"max_cycles":NaN}}',
    '{"campaign_id":"SYN-CAMPAIGN","research_budget":{"max_cycles":Infinity}}',
    '{"campaign_id":"SYN-CAMPAIGN","research_budget":{"max_cycles":1e309}}',
])
def test_restart_and_save_both_reject_ambiguous_or_nonfinite_durable_campaign(tmp_path, raw):
    path, state = loaded(tmp_path)
    remembered = asdict(state)
    path.write_text(raw)
    with pytest.raises(ValueError):
        runtime.CampaignState.load_or_create(path, 'ignored')
    state.latest_lesson = 'must not normalize invalid serialized truth'
    with pytest.raises(ValueError):
        state.save(path)
    assert path.read_text() == raw
    assert asdict(state) == remembered
