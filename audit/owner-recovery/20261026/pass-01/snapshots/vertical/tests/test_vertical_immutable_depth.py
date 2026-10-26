import json
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from research.research_os.expansion import persistent_state as state
from research.research_os.scientific_store import sha256_json


@pytest.mark.parametrize('first,second', [({'x': True}, {'x': 1}), ({'x': 1}, {'x': 1.0}), ({'x': 0.0}, {'x': -0.0})])
def test_checkpoint_replay_uses_hash_identity(tmp_path, first, second):
    path = tmp_path / 'checkpoint.json'
    state.write_immutable_json(path, first)
    original = path.read_bytes()
    with pytest.raises(ValueError, match='mutation'):
        state.write_immutable_json(path, second)
    assert path.read_bytes() == original


def test_checkpoint_tuple_replay_uses_wire_identity(tmp_path):
    path = tmp_path / 'checkpoint.json'
    state.write_immutable_json(path, {'x': (1, 2)})
    state.write_immutable_json(path, {'x': (1, 2)})
    assert state.read_immutable_json(path) == {'x': [1, 2]}


@pytest.mark.parametrize('payload', [[], None, {'x': float('nan')}, {'x': float('inf')}, {'nested': {1: 'bad'}}])
def test_checkpoint_and_registry_reject_noncanonical_objects(tmp_path, payload):
    path = tmp_path / 'checkpoint.json'
    with pytest.raises((ValueError, TypeError)):
        state.write_immutable_json(path, payload)
    assert not path.exists()
    registry = state.ImmutableArtifactRegistry('r')
    with pytest.raises((ValueError, TypeError)):
        registry.register('id', payload)
    assert registry.snapshot()['entry_count'] == 0


@pytest.mark.parametrize('raw', ['null', '[]', '1', '{"payload_hash":"x","payload":{}}',
    '{"payload_hash":"' + sha256_json({'x': 1}) + '","payload":{"x":0,"x":1}}',
    json.dumps({'payload_hash':sha256_json({'x': float('nan')}), 'payload':{'x': float('nan')}})])
def test_checkpoint_malformed_read_fails_closed(tmp_path, raw):
    path = tmp_path / 'checkpoint.json'
    path.write_text(raw)
    with pytest.raises(ValueError):
        state.read_immutable_json(path)


@pytest.mark.parametrize('artifact_id', ['', None, 1, True])
def test_registry_requires_exact_nonempty_identity(artifact_id):
    registry = state.ImmutableArtifactRegistry('r')
    with pytest.raises(ValueError):
        registry.register(artifact_id, {})
    assert registry.snapshot()['entry_count'] == 0


def test_registry_deterministic_competing_payloads(monkeypatch):
    registry = state.ImmutableArtifactRegistry('r')
    entered, release, second_started = threading.Event(), threading.Event(), threading.Event()
    original = state.sha256_json
    def held(payload):
        if payload == {'x': 1}:
            entered.set()
            assert release.wait(5)
        return original(payload)
    monkeypatch.setattr(state, 'sha256_json', held)
    def second():
        second_started.set()
        return registry.register('same', {'x': 2})
    with ThreadPoolExecutor(max_workers=2) as pool:
        one = pool.submit(registry.register, 'same', {'x': 1})
        try:
            assert entered.wait(5)
            two = pool.submit(second)
            assert second_started.wait(5)
            assert not two.done()
        finally:
            release.set()
        assert one.result()['payload'] == {'x': 1}
        with pytest.raises(ValueError, match='mutation'):
            two.result()
    assert registry.snapshot()['entries'][0]['payload'] == {'x': 1}


def test_registry_normalizes_and_detaches_wire_payload():
    registry = state.ImmutableArtifactRegistry('r')
    payload = {'nested': ([1],)}
    result = registry.register('id', payload)
    payload['nested'][0].append(2)
    assert result['payload'] == {'nested': [[1]]}
    result['payload']['nested'][0].append(3)
    snapshot = registry.snapshot()
    assert snapshot['entries'][0]['artifact_hash'] == sha256_json(snapshot['entries'][0]['payload'])
    assert snapshot['entries'][0]['payload'] == {'nested': [[1]]}


@pytest.mark.parametrize('different', [False, True])
def test_checkpoint_concurrent_publish_once(tmp_path, different):
    path = tmp_path / 'checkpoint.json'
    barrier = threading.Barrier(2)
    def publish(i):
        barrier.wait(5)
        try:
            state.write_immutable_json(path, {'x': i if different else 1})
            return 'OK'
        except ValueError:
            return 'CONFLICT'
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(publish, [1, 2]))
    assert outcomes.count('OK') == (1 if different else 2)
    assert state.read_immutable_json(path)['x'] in [1, 2]
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize('point', ['before_link', 'after_link'])
def test_checkpoint_publish_failure_retry(tmp_path, monkeypatch, point):
    import os
    path = tmp_path / 'checkpoint.json'
    original = os.link
    def fail(src, dst):
        if point == 'after_link':
            original(src, dst)
        raise OSError('injected ACK loss')
    with monkeypatch.context() as patch:
        patch.setattr(os, 'link', fail)
        with pytest.raises(OSError):
            state.write_immutable_json(path, {'x': [1]})
    assert path.exists() is (point == 'after_link')
    state.write_immutable_json(path, {'x': [1]})
    assert state.read_immutable_json(path) == {'x': [1]}
    assert list(tmp_path.iterdir()) == [path]
