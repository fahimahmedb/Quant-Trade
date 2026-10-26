from copy import deepcopy

import pytest

from research.research_os.expansion.final_shape import assess_implementability
from research.research_os.tests.test_implementability_depth import _complete_meta, _engine_output


FIELDS=['direction_exposure_semantics','eligibility','position_expression','cost_model_requirements',
        'capacity_requirements','data_requirements','execution_assumptions',
        'falsification_relevant_implementation_conditions','entry_clock']


@pytest.mark.parametrize('field',FIELDS)
@pytest.mark.parametrize('value', [['UNKNOWN'], {'value':'UNKNOWN'}, ['declared','UNKNOWN'],
                                 {'status':'UNKNOWN','value':'declared'}])
def test_nested_unknown_does_not_qualify_exact_expression(field,value):
    meta=_complete_meta();meta['economic_expression'][field]=deepcopy(value)
    result=assess_implementability(_engine_output(),meta)
    assert result['status']=='BLOCK_IMPLEMENTABILITY'
    assert result['exact_expression_status']=='BLOCK'
    assert all(v is False for v in result['authority'].values())


@pytest.mark.parametrize('value',['CONFLICTED','BLOCKED','UNEXECUTED','INVALIDATED_PROTOCOL'])
def test_unqualified_complexity_is_not_declared_known(value):
    meta=_complete_meta();meta['operational_complexity']=value
    assert assess_implementability(_engine_output(),meta)['status']=='BLOCK_IMPLEMENTABILITY'


@pytest.mark.parametrize('field',['source_available','pit_feasible','expression_feasible','cost_model_feasible','capacity_observable'])
def test_truthy_integer_cannot_promote_tri_state(field):
    meta=_complete_meta();meta[field]=1
    result=assess_implementability(_engine_output(),meta)
    assert result['status']=='BLOCK_IMPLEMENTABILITY'
    assert result[field]=='UNKNOWN'


def test_supported_nested_expression_remains_valid_and_detached():
    meta=_complete_meta();meta['economic_expression']['data_requirements']={'snapshots':['versioned','pre-decision']}
    output=_engine_output();before=deepcopy((meta,output))
    result=assess_implementability(output,meta)
    assert result['status']=='PASS'
    result['exact_expression_contract']['data_requirements']['snapshots'].clear()
    assert (meta,output)==before


def test_unavailable_source_with_other_premises_known_is_parked():
    meta=_complete_meta();meta['source_available']=False
    assert assess_implementability(_engine_output(),meta)['status']=='PARK_IMPLEMENTABILITY'
