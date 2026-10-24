"""Typed queue CAS and ambiguous/corrupt durable input cannot erase observed truth."""
from copy import deepcopy
from dataclasses import asdict
import json
from unittest.mock import patch

import pytest

from autonomous_research import runtime
from autonomous_research.runtime import PersistentQueue, QueueConflict, ResearchTask
from quant.state import write_json


def task(name='original'):
    return ResearchTask(name, 'synthetic', 1, 'durable proof only', 'fake', attempts=0,
                        lease_seconds=600, metadata={'identity': {'sequence': 0}}, data_fingerprint='v1')


def setup_queue(tmp_path):
    queue = PersistentQueue(tmp_path / 'queue.json')
    queue.add(task())
    return queue


def typed_change(document, field):
    if field == 'priority':
        document['tasks'][0]['priority'] = True
    elif field == 'attempts':
        document['tasks'][0]['attempts'] = False
    elif field == 'lease':
        document['tasks'][0]['lease_seconds'] = 600.0
    else:
        document['tasks'][0]['metadata']['identity']['sequence'] = False


@pytest.mark.parametrize('field', ['priority', 'attempts', 'lease', 'metadata'])
@pytest.mark.parametrize('operation', ['save', 'add'])
def test_typed_only_external_change_fences_stale_writer_and_retries_from_readback(tmp_path, field, operation):
    queue = setup_queue(tmp_path)
    observed = json.loads(queue.path.read_text())
    external = deepcopy(observed)
    typed_change(external, field)
    assert external == observed  # Python equality is precisely the unsafe comparison.
    assert json.dumps(external, sort_keys=True) != json.dumps(observed, sort_keys=True)
    write_json(queue.path, external)
    durable = queue.path.read_bytes()
    with pytest.raises(QueueConflict):
        if operation == 'save':
            queue.tasks['original'].reason = 'stale edit'
            queue.save()
        else:
            queue.add(task('next'))
    assert queue.path.read_bytes() == durable
    assert json.dumps(asdict(queue.tasks['original']), sort_keys=True) == json.dumps(external['tasks'][0], sort_keys=True)
    assert 'next' not in queue.tasks
    assert queue.add(task('next')) is True
    assert queue.add(task('next')) is False
    reloaded = PersistentQueue(queue.path)
    assert set(reloaded.tasks) == {'original', 'next'}
    assert json.dumps(asdict(reloaded.tasks['original']), sort_keys=True) == json.dumps(external['tasks'][0], sort_keys=True)


def corrupt_document(document, kind):
    encoded = json.dumps(document)
    if kind == 'duplicate_root':
        return encoded.replace('"version": 1', '"version": 2, "version": 1')
    if kind == 'duplicate_task':
        return encoded.replace('"attempts": 0', '"attempts": 2, "attempts": 0')
    if kind == 'duplicate_nested':
        return encoded.replace('"sequence": 0', '"sequence": 1, "sequence": 0')
    if kind == 'nonfinite':
        return encoded.replace('"sequence": 0', '"sequence": NaN')
    if kind == 'bool_version':
        return encoded.replace('"version": 1', '"version": true')
    if kind == 'unknown_version':
        return encoded.replace('"version": 1', '"version": 2')
    if kind == 'duplicate_identity':
        document = deepcopy(document)
        document['tasks'].append(deepcopy(document['tasks'][0]))
        return json.dumps(document)
    if kind == 'invalid_tasks_shape':
        document = deepcopy(document)
        document['tasks'] = 'original'
        return json.dumps(document)
    return encoded[:-5]


@pytest.mark.parametrize('where', ['root', 'task', 'nested'])
@pytest.mark.parametrize('same', [False, True])
def test_duplicate_fields_are_ambiguous_even_if_the_last_value_or_both_values_match(tmp_path, where, same):
    queue = setup_queue(tmp_path)
    original = queue.path.read_text()
    old, new = {'root': ('"version": 1', '"version": 1' if same else '"version": 2'),
                'task': ('"attempts": 0', '"attempts": 0' if same else '"attempts": 1'),
                'nested': ('"sequence": 0', '"sequence": 0' if same else '"sequence": 1')}[where]
    queue.path.write_text(original.replace(old, new + ', ' + old))
    before = queue.path.read_bytes()
    with pytest.raises(ValueError, match='duplicate'):
        PersistentQueue(queue.path)
    assert queue.path.read_bytes() == before


@pytest.mark.parametrize('value', ['NaN', 'Infinity', '-Infinity', '1e309'])
@pytest.mark.parametrize('field', ['priority', 'metadata'])
def test_nonfinite_durable_json_is_denied_at_load_before_any_queue_effect(tmp_path, value, field):
    queue = setup_queue(tmp_path)
    old = '"priority": 1' if field == 'priority' else '"sequence": 0'
    key = 'priority' if field == 'priority' else 'sequence'
    queue.path.write_text(queue.path.read_text().replace(old, '"'+key+'": '+value))
    before = queue.path.read_bytes()
    with pytest.raises(ValueError):
        PersistentQueue(queue.path)
    assert queue.path.read_bytes() == before


@pytest.mark.parametrize('kind', ['duplicate_root', 'duplicate_task', 'duplicate_nested', 'nonfinite',
                                  'bool_version', 'unknown_version', 'duplicate_identity',
                                  'invalid_tasks_shape', 'truncated'])
@pytest.mark.parametrize('operation', ['save', 'add'])
def test_invalid_durable_recovery_restores_last_trusted_snapshot_without_repairing_disk(tmp_path, kind, operation):
    queue = setup_queue(tmp_path)
    original_wire = queue.path.read_bytes()
    trusted = asdict(queue.tasks['original'])
    queue.path.write_text(corrupt_document(json.loads(original_wire), kind))
    invalid_wire = queue.path.read_bytes()
    with pytest.raises((ValueError, TypeError, QueueConflict, KeyError)):
        if operation == 'save':
            queue.tasks['original'].reason = 'uncommitted edit'
            queue.save()
        else:
            queue.add(task('next'))
    assert queue.path.read_bytes() == invalid_wire
    assert set(queue.tasks) == {'original'}
    assert asdict(queue.tasks['original']) == trusted
    # Only a real external repair unblocks the queue. No inferred successful write.
    queue.path.write_bytes(original_wire)
    assert queue.add(task('next')) is True
    assert queue.add(task('next')) is False
    assert set(PersistentQueue(queue.path).tasks) == {'original', 'next'}


def test_harmless_key_order_and_whitespace_do_not_create_false_conflicts(tmp_path):
    queue = setup_queue(tmp_path)
    document = json.loads(queue.path.read_text())
    queue.path.write_text(json.dumps(dict(reversed(list(document.items()))), separators=(',', ':')))
    assert queue.add(task('next')) is True
    assert set(PersistentQueue(queue.path).tasks) == {'original', 'next'}


@pytest.mark.parametrize('ack_lost', [False, True])
def test_strict_readback_preserves_exact_typed_new_task_after_publication_error(tmp_path, ack_lost):
    queue = setup_queue(tmp_path)
    proposal = task('next')
    proposal.metadata['identity']['sequence'] = False
    before = queue.path.read_bytes()

    def publication(path, document):
        if ack_lost:
            write_json(path, document)
        raise OSError('publication/ACK error')

    with patch.object(runtime, '_write_json', side_effect=publication):
        with pytest.raises(OSError):
            queue.add(proposal)
    if ack_lost:
        assert queue.tasks['next'].metadata['identity']['sequence'] is False
        assert queue.add(proposal) is False
    else:
        assert queue.path.read_bytes() == before
        assert 'next' not in queue.tasks
        assert queue.add(proposal) is True
    restored = PersistentQueue(queue.path)
    assert set(restored.tasks) == {'original', 'next'}
    assert restored.tasks['next'].metadata['identity']['sequence'] is False
