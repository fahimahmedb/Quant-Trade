from copy import deepcopy

import pytest

from research.research_os.expansion.red_team_v2 import red_team_negative_rights_v2
from research.research_os.expansion.validation_readiness import CHECK_ORDER, validate_economic_test_readiness
from research.research_os.tests.test_economic_readiness_validation import _fixture


def receipt():
    result = validate_economic_test_readiness(_fixture())
    assert red_team_negative_rights_v2(result)['status'] == 'PASS'
    return result


@pytest.mark.parametrize('field,value,blocker', [
    ('status','BLOCK','BLOCK_CLAIM_LEVEL'),
    ('block_reasons',['frozen input conflict'],'BLOCK_CLAIM_LEVEL'),
    ('ready_for_authorized_economic_test',False,'BLOCK_CLAIM_LEVEL'),
    ('economic_test_authorized',True,'BLOCK_CLAIM_LEVEL'),
    ('outcome_access_authorized',True,'BLOCK_LEAKAGE'),
])
def test_contradictory_validator_summary_cannot_pass(field,value,blocker):
    record = receipt()
    record[field] = value
    before = deepcopy(record)
    result = red_team_negative_rights_v2(record)
    assert result['status'] == 'BLOCK'
    assert blocker in result['negative_rights']
    assert record == before
    assert result['economic_test_authorized'] is False
    assert result['capital_authorized'] is False


def test_frozen_input_check_is_not_omitted():
    record = receipt()
    record['checks']['frozen_input_binding']['status'] = 'FAIL'
    assert 'BLOCK_REPRODUCIBILITY' in red_team_negative_rights_v2(record)['negative_rights']


@pytest.mark.parametrize('state', ['UNKNOWN','CONFLICTED','BLOCKED','UNEXECUTED','INVALIDATED_PROTOCOL',None,True])
@pytest.mark.parametrize('field,blocker', [('data_integrity_status','BLOCK_DATA'), ('leakage_status','BLOCK_LEAKAGE'),
    ('clock_status','BLOCK_CLOCK'), ('pit_status','BLOCK_PIT'), ('economic_identity_status','BLOCK_ECONOMIC_IDENTITY'),
    ('portfolio_duplication_status','BLOCK_PORTFOLIO_DUPLICATION')])
def test_explicit_unqualified_context_is_not_ignored(state, field, blocker):
    result = red_team_negative_rights_v2(receipt(), context={field:state})
    assert result['status'] == 'BLOCK'
    assert blocker in result['negative_rights']


@pytest.mark.parametrize('field', list(CHECK_ORDER))
def test_each_known_check_missing_blocks(field):
    record = receipt()
    del record['checks'][field]
    assert red_team_negative_rights_v2(record)['status'] == 'BLOCK'


def test_unknown_failed_validator_check_preserves_denial():
    record = receipt()
    record['checks']['future_additional_invariant'] = {'status': 'FAIL'}
    assert red_team_negative_rights_v2(record)['status'] == 'BLOCK'


def test_positive_optional_context_and_default_stay_equivalent():
    record = receipt()
    assert red_team_negative_rights_v2(record, context={'pit_status':'PASS'}) == red_team_negative_rights_v2(record)
