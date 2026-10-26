"""CP040 rebuilt: the export must hash exactly the body that its own guard checked."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import threading
from unittest.mock import patch

import pytest

from research.research_os.expansion import v2_core as core


def payload():
    value = json.loads((Path(__file__).parent / 'fixtures/oracle_v2_core_fixture.json').read_text())['export']
    value.update(candidate_hash='a'*64, research_trial_history_hash='b'*64,
                 research_epoch_id='E-SYNTHETIC', epoch_manifest_hash='c'*64,
                 validator_artifact_hash='f'*64)
    value['documentary_notes'] = {'limitations': ['pre-outcome only']}
    return value


@pytest.mark.parametrize('mutation', ['outcome_dict', 'outcome_tuple', 'identity', 'required_reference'])
def test_concurrent_caller_change_after_scan_cannot_enter_export(mutation):
    value = payload()
    expected = core.build_frozen_export_intent(deepcopy(value))
    scanned, release = threading.Event(), threading.Event()
    scan = core._scan_forbidden_outcome_keys

    def pause_after_scan(body, path='$'):
        hits = scan(body, path)
        if path == '$':
            scanned.set()
            assert release.wait(5)
        return hits

    with patch.object(core, '_scan_forbidden_outcome_keys', side_effect=pause_after_scan):
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(core.build_frozen_export_intent, value)
            try:
                assert scanned.wait(5)
                if mutation == 'outcome_dict':
                    value['documentary_notes']['returns'] = [1.0]
                elif mutation == 'outcome_tuple':
                    value['documentary_notes']['limitations'] = ({'pnl': 1.0},)
                elif mutation == 'identity':
                    value['research_head'] = '9'*40
                else:
                    del value['validator_artifact_hash']
            finally:
                release.set()
            result = future.result(timeout=5)
    assert result == expected
    assert core._scan_forbidden_outcome_keys(result) == []
    assert result['export_bundle_hash'] == core.canonical_hash({k:v for k,v in result.items() if k != 'export_bundle_hash'})


@pytest.mark.parametrize('reference', ['candidate_hash', 'source_snapshot_hashes'])
def test_required_schema_check_and_export_use_same_captured_body(reference):
    value = payload()
    expected = core.build_frozen_export_intent(deepcopy(value))
    require = core._require

    def remove_after_require(body, keys, label):
        require(body, keys, label)
        if label == 'EXPORT':
            del value[reference]

    with patch.object(core, '_require', side_effect=remove_after_require):
        actual = core.build_frozen_export_intent(value)
    assert actual == expected
    assert reference in actual


def test_unchanged_export_is_deterministic_across_reordered_json_and_detached_returns():
    value = payload()
    before = deepcopy(value)
    first = core.build_frozen_export_intent(value)
    reordered = json.loads(json.dumps(value, sort_keys=True))
    second = core.build_frozen_export_intent(reordered)
    assert first == second
    first['economic_expression']['direction'] = 'caller mutation'
    assert value == before
    assert second == core.build_frozen_export_intent(value)


@pytest.mark.parametrize('hidden', [{'returns': [1]}, ({'pnl': 1},), [{'outcome': 'POSITIVE'}]])
def test_existing_forbidden_content_never_receives_an_export_hash(hidden):
    value = payload()
    value['documentary_notes']['nested'] = hidden
    with pytest.raises(core.V2ContractError, match='OUTCOME_DATA_IN_RESEARCH_EXPORT'):
        core.build_frozen_export_intent(value)
