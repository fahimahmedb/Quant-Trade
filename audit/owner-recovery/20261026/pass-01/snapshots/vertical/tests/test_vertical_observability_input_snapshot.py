"""CP061: the displayed body must be the body that passed the content guard."""
from copy import deepcopy
from unittest.mock import patch
import pytest
from research.research_os.expansion import edge_observability_v2 as projection


def inputs():
    return {
        'task': {'task_id': 'T-SNAPSHOT', 'task_type': 'EVENT_DOCUMENT'},
        'research': {
            'candidate': {'hypothesis_id': 'H-SNAPSHOT'},
            'dossier': {'blockers': ['MISSING_DOCUMENT'], 'claim_ceiling': 'DOCUMENTED_FACTS_ONLY',
                        'dossier': {'rule': {'status': 'UNKNOWN', 'support': None, 'limitations': ['not recovered']}}},
        },
        'validator': {'scientific_decision': 'BLOCK'},
        'readiness': {'status': 'INCOMPLETE', 'claim_ceiling': 'DOCUMENTED_FACTS_ONLY', 'outcome_accessed': False},
    }


@pytest.mark.parametrize('mutation', ['ready', 'ceiling_outcome', 'remove_blocker', 'support', 'validator'])
def test_cp061_caller_mutation_after_scan_cannot_change_projected_truth(mutation):
    supplied = inputs()
    expected = projection.build_edge_observability_projection(**deepcopy(supplied))
    original = projection._collect_blockers
    calls = []

    def mutate_then_collect(*args, **kwargs):
        calls.append(True)
        if mutation == 'ready':
            supplied['readiness']['status'] = 'READY'
        elif mutation == 'ceiling_outcome':
            supplied['readiness']['claim_ceiling'] = {'returns': [1]}
        elif mutation == 'remove_blocker':
            supplied['research']['dossier']['blockers'].clear()
        elif mutation == 'support':
            supplied['research']['dossier']['dossier']['rule'].update(status='SUPPORTED', support={'ref': 'injected'})
        else:
            supplied['validator']['scientific_decision'] = 'PASS'
        return original(*args, **kwargs)

    with patch.object(projection, '_collect_blockers', side_effect=mutate_then_collect):
        result = projection.build_edge_observability_projection(**supplied)
    assert calls == [True]
    assert result == expected
    projection._assert_pre_outcome(result)
    assert all(value is False for value in result['authority'].values())


def test_cp061_projection_is_deterministic_and_detached_from_nested_caller():
    supplied = inputs()
    before = deepcopy(supplied)
    a = projection.build_edge_observability_projection(**supplied)
    b = projection.build_edge_observability_projection(**deepcopy(supplied))
    assert a == b
    a['evidence_maturity']['fields']['rule']['limitations'].append('caller change')
    a['authority']['real_capital_authorized'] = True
    assert supplied == before
    assert b == projection.build_edge_observability_projection(**supplied)
