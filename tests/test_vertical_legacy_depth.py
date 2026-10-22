from copy import deepcopy
import json
from pathlib import Path

import pytest

from research.research_os.legacy import LegacyKnowledgeBase


MANIFEST = Path('research/research_os/legacy/source_manifest.json')


def test_caller_cannot_rewrite_historical_decision_or_summary():
    manifest = json.loads(MANIFEST.read_text())
    record = {'HYPOTHESIS_ID': 'A', 'RESEARCH_DECISION': 'KILL', 'RESULT': 'NEGATIVE'}
    data = {'records': [record]}
    kb = LegacyKnowledgeBase(manifest, data)
    expected = kb.summary()
    record.update(RESEARCH_DECISION='PROMOTE', RESULT='POSITIVE')
    manifest['global_effective_trials'] = 42
    assert kb.screen_candidate({'hypothesis_id': 'A'})['historical_decision'] == 'KILL'
    assert kb.summary() == expected


@pytest.mark.parametrize('reverse', [False, True])
@pytest.mark.parametrize('primary_collision', [False, True])
def test_conflicting_identity_is_reviewed_without_arbitrary_winner(reverse, primary_collision):
    records = [
        {'HYPOTHESIS_ID': 'A', 'LEGACY_ID_IF_ANY': 'shared', 'RESULT': 'NEGATIVE', 'RESEARCH_DECISION': 'KILL'},
        {'HYPOTHESIS_ID': 'A' if primary_collision else 'B', 'LEGACY_ID_IF_ANY': 'shared', 'RESULT': 'BLOCKED', 'RESEARCH_DECISION': 'WAIT'},
    ]
    if reverse:
        records.reverse()
    kb = LegacyKnowledgeBase({}, {'records': records})
    candidate_id = 'A' if primary_collision else 'shared'
    result = kb.screen_candidate({'hypothesis_id': candidate_id})
    assert result['status'] == 'REVIEW_LEGACY_OVERLAP'
    assert len(result['matches']) == 2
    assert {m['historical_result'] for m in result['matches']} == {'NEGATIVE', 'BLOCKED'}
    other = LegacyKnowledgeBase({}, {'records': list(reversed(records))})
    assert other.screen_candidate({'hypothesis_id': candidate_id}) == result


def test_identical_record_replay_is_not_a_conflict():
    record = {'HYPOTHESIS_ID': 'A', 'LEGACY_ID_IF_ANY': 'A', 'RESEARCH_DECISION': 'KILL'}
    kb = LegacyKnowledgeBase({}, {'records': [record, deepcopy(record)]})
    assert kb.screen_candidate({'hypothesis_id': 'A'})['status'] == 'BLOCK_EXACT_LEGACY_DUPLICATE'


@pytest.mark.parametrize('records', [None, {}, '', [None], [1], ['A']])
def test_malformed_corpus_is_rejected(records):
    with pytest.raises(ValueError):
        LegacyKnowledgeBase({}, {'records': records})


def test_exact_match_result_does_not_export_mutable_ledger_fields():
    kb = LegacyKnowledgeBase({}, {'records': [{'HYPOTHESIS_ID': 'A',
        'NEXT_LEGITIMATE_STEP': {'limitations': ['original']}}]})
    result = kb.screen_candidate({'hypothesis_id': 'A'})
    result['next_legitimate_step']['limitations'].clear()
    assert kb.screen_candidate({'hypothesis_id': 'A'})['next_legitimate_step'] == {'limitations': ['original']}
