"""CP041 rebuilt: one checked identity/body through each existing Core builder."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import threading
from unittest.mock import patch

import pytest

from research.research_os.expansion import v2_core as core


CASES = [
    ('epoch', core.build_epoch_manifest, 'research_epoch_id', 'research_policy_hash'),
    ('trial', core.build_research_trial, 'research_trial_id', 'model_identity'),
    ('candidate', core.build_candidate, 'hypothesis_id', 'claim'),
    ('validator', core.build_validator_result, 'validator_identity', 'validator_context_hash'),
    ('negative_memory', core.build_negative_memory, 'negative_knowledge_id', 'revisit_policy'),
]


def bundle():
    return json.loads((Path(__file__).parent / 'fixtures/oracle_v2_core_fixture.json').read_text())


@pytest.mark.parametrize('key,builder,identity,required', CASES, ids=[c[0] for c in CASES])
@pytest.mark.parametrize('mutation', ['null_checked_identity', 'delete_required_field'])
def test_concurrent_mutation_after_checks_cannot_enter_hashed_core_artifact(key,builder,identity,required,mutation):
    supplied = bundle()[key]
    expected = builder(deepcopy(supplied))
    checked, release = threading.Event(), threading.Event()
    check = core._require_identifiers

    def pause_after_identifier_check(body, fields, label):
        check(body, fields, label)
        checked.set()
        assert release.wait(5)

    with patch.object(core, '_require_identifiers', side_effect=pause_after_identifier_check):
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(builder, supplied)
            try:
                assert checked.wait(5)
                if mutation == 'null_checked_identity':
                    supplied[identity] = None
                else:
                    del supplied[required]
            finally:
                release.set()
            actual = future.result(timeout=5)
    assert actual == expected
    # Re-admission of the returned artifact must enforce the same contract.
    assert builder(actual) == expected


@pytest.mark.parametrize('key,builder,identity,required', CASES, ids=[c[0] for c in CASES])
def test_valid_reconstruction_and_detached_returns_are_unchanged(key,builder,identity,required):
    supplied = bundle()[key]
    before = deepcopy(supplied)
    expected = builder(supplied)
    assert builder(json.loads(json.dumps(expected, sort_keys=True))) == expected
    expected[identity] = 'caller-output-change'
    assert supplied == before
    assert builder(supplied)[identity] == before[identity]


def test_epoch_policy_hash_and_fields_cannot_mix_snapshots_after_clock_validation():
    supplied = bundle()['epoch']
    expected = core.build_epoch_manifest(deepcopy(supplied))
    parse = core._parse_time
    calls = []

    def change_after_last_checked_clock(value):
        result = parse(value)
        calls.append(value)
        if len(calls) == 4:
            supplied['max_candidate_exports'] = 0
            supplied['allowed_model_set'].clear()
        return result

    with patch.object(core, '_parse_time', side_effect=change_after_last_checked_clock):
        actual = core.build_epoch_manifest(supplied)
    assert len(calls) == 4
    assert actual == expected
    assert core.build_epoch_manifest(actual) == expected
