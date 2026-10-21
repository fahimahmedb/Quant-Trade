import copy
import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from research.research_os.scientific_store import AppendOnlyHashLedger, build_scientific_ledgers


def ledger():
    result = AppendOnlyHashLedger()
    result.append('TEST', {'nested': {'values': [1]}})
    return result


def test_input_alias_is_detached():
    payload = {'nested': [1]}
    result = AppendOnlyHashLedger()
    result.append('TEST', payload)
    payload['nested'].append(2)
    assert result.verify()
    assert result.entries[0]['payload'] == {'nested': [1]}


def test_return_alias_is_detached():
    result = AppendOnlyHashLedger()
    entry = result.append('TEST', {'nested': [1]})
    entry['payload']['nested'].append(2)
    entry['entry_hash'] = 'changed'
    assert result.verify()


def test_trial_export_does_not_mutate_ledger():
    result = build_scientific_ledgers(run_id='r', outputs=[{'candidate': {
        'hypothesis_id': 'h', 'generation_id': 'g'}}], timestamp='synthetic')
    result['trial_records'][0]['limitations'].clear()
    assert result['scientific_ledger'].verify()


@pytest.mark.parametrize('payload', [{'x': float('nan')}, {'x': float('inf')},
                                     {'x': {1: 'ambiguous'}}, [], {'x': object()}])
def test_bad_payload_cannot_append(payload):
    result = ledger()
    before = copy.deepcopy(result.entries)
    with pytest.raises((TypeError, ValueError)):
        result.append('TEST', payload)
    assert result.entries == before


@pytest.mark.parametrize('kind', ['', None, 1, True])
def test_bad_kind_cannot_append(kind):
    result = ledger()
    with pytest.raises((TypeError, ValueError)):
        result.append(kind, {})
    assert len(result.entries) == 1


@pytest.mark.parametrize('mutation', ['nonobject', 'bool_seq', 'extra', 'missing', 'nan'])
def test_malformed_chain_fails_closed(mutation, tmp_path):
    result = ledger()
    if mutation == 'nonobject':
        result.entries[0] = None
    elif mutation == 'bool_seq':
        result.entries[0]['seq'] = True
    elif mutation == 'extra':
        result.entries[0]['unhashed'] = 'injected'
    elif mutation == 'missing':
        del result.entries[0]['payload']
    else:
        result.entries[0]['payload']['bad'] = float('nan')
    assert result.verify() is False
    path = tmp_path / 'ledger.jsonl'
    path.write_text('previous\n')
    with pytest.raises(ValueError):
        result.write_jsonl(path)
    assert path.read_text() == 'previous\n'
    with pytest.raises(ValueError):
        result.append('NEXT', {})


def test_atomic_publication_failure_and_retry(tmp_path, monkeypatch):
    import os
    result = ledger()
    path = tmp_path / 'ledger.jsonl'
    result.write_jsonl(path)
    previous = path.read_bytes()
    result.append('NEXT', {})
    replace = os.replace
    def fail(*args, **kwargs):
        raise OSError('injected before publication')
    with monkeypatch.context() as patch:
        patch.setattr(os, 'replace', fail)
        with pytest.raises(OSError):
            result.write_jsonl(path)
    assert path.read_bytes() == previous
    assert sorted(p.name for p in tmp_path.iterdir()) == ['ledger.jsonl']
    assert os.replace is replace
    result.write_jsonl(path)
    recovered = AppendOnlyHashLedger()
    recovered.entries = [json.loads(line) for line in path.read_text().splitlines()]
    assert recovered.verify()
    assert recovered.entries == result.entries
    committed = path.read_bytes()
    result.write_jsonl(path)
    assert path.read_bytes() == committed


def test_concurrent_append_keeps_one_chain():
    result = AppendOnlyHashLedger()
    with ThreadPoolExecutor(max_workers=8) as pool:
        receipts = list(pool.map(lambda i: result.append('TEST', {'id': i}), range(100)))
    assert result.verify()
    assert sorted(r['seq'] for r in receipts) == list(range(1, 101))
    assert len({r['payload']['id'] for r in receipts}) == 100


def test_append_serializes_hash_and_sequence(monkeypatch):
    import threading
    from research.research_os import scientific_store
    result = AppendOnlyHashLedger()
    entered, release, second_started = threading.Event(), threading.Event(), threading.Event()
    original = scientific_store.sha256_json
    def held_hash(value):
        if value == {'id': 1}:
            entered.set()
            assert release.wait(5)
        return original(value)
    monkeypatch.setattr(scientific_store, 'sha256_json', held_hash)
    def second():
        second_started.set()
        return result.append('TEST', {'id': 2})
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(result.append, 'TEST', {'id': 1})
        try:
            assert entered.wait(5)
            other = pool.submit(second)
            assert second_started.wait(5)
            assert not other.done()
        finally:
            release.set()
        assert first.result()['seq'] == 1
        assert other.result()['seq'] == 2
    assert result.verify()


@pytest.mark.parametrize('failed_fsync', [1, 2])
def test_fsync_failure_leaves_complete_old_or_new_document(tmp_path, monkeypatch, failed_fsync):
    import os
    result = ledger()
    path = tmp_path / 'ledger.jsonl'
    result.write_jsonl(path)
    result.append('NEXT', {'unicode': 'é'})
    original = os.fsync
    calls = 0
    def failing(fd):
        nonlocal calls
        calls += 1
        if calls == failed_fsync:
            raise OSError('injected fsync failure')
        return original(fd)
    with monkeypatch.context() as patch:
        patch.setattr(os, 'fsync', failing)
        with pytest.raises(OSError):
            result.write_jsonl(path)
    recovered = AppendOnlyHashLedger()
    recovered.entries = [json.loads(line) for line in path.read_text().splitlines()]
    assert recovered.verify()
    assert len(recovered.entries) == (1 if failed_fsync == 1 else 2)
    result.write_jsonl(path)
    recovered.entries = [json.loads(line) for line in path.read_text().splitlines()]
    assert recovered.entries == result.entries
    assert list(tmp_path.iterdir()) == [path]
