from copy import deepcopy

import pytest

from research.research_os.expansion.portfolio_v2 import portfolio_diagnostics_v2,structural_pair,structural_identity
from research.research_os.tests.test_economic_identity_portfolio_readiness import identity


@pytest.mark.parametrize('field',['payer','mechanism','timing_clock'])
@pytest.mark.parametrize('state',['CONFLICTED','BLOCKED','UNEXECUTED','INVALIDATED_PROTOCOL'])
def test_unqualified_core_axis_is_unknown(field,state):
    left=identity('L',**{field:state})
    right=identity('R')
    result=structural_pair(left,right)
    assert result['dimensions'][field] is None
    assert field in result['unknown_dimensions']
    assert structural_identity(left)['fields'][field]['status']=='UNKNOWN'


@pytest.mark.parametrize('value',[{'status':'UNKNOWN','value':'dealer'},['dealer','UNKNOWN'],
    {'known':'dealer','missing':'UNKNOWN'},('dealer','UNKNOWN')])
def test_partially_unknown_object_cannot_make_complete_core_axis(value):
    left=identity('L',payer=value);right=identity('R',payer=deepcopy(value))
    result=structural_pair(left,right)
    assert result['dimensions']['payer'] is None
    assert result['score_status']=='PARTIAL'
    assert result['classification']=='UNKNOWN'


def test_tuple_universe_matches_equivalent_list_membership():
    result=structural_pair(identity('L',universe=('B','A')),identity('R',universe=['A','B']))
    assert result['dimensions']['universe']==1.0


@pytest.mark.parametrize('tags',['payer','UNKNOWN','balance-sheet'])
def test_scalar_tag_text_is_not_compared_as_character_sets(tags):
    with pytest.raises(ValueError):structural_pair(identity('L',economic_tags=tags),identity('R'))


@pytest.mark.parametrize('value',[None,True,False,float('nan'),float('inf'),[]])
def test_existing_unknown_inputs_do_not_promote_empirical_truth(value):
    result=portfolio_diagnostics_v2([identity('L',payer=value),identity('R')])
    assert result['structural_novelty']['L']=='UNKNOWN'
    assert result['empirical_correlation']=='UNAVAILABLE'
    assert result['marginal_portfolio_contribution']=='NOT_ESTIMATED'
    for key in ('capital_allocation_authorized','position_sizing_authorized','orders_authorized',
                'real_capital_authorized','live_trading_authorized','portfolio_optimization_authorized'):
        assert result[key] is False


def test_core_overlap_and_field_ordering_remain_read_only():
    left,right=identity('L'),identity('R')
    before=deepcopy((left,right))
    result=structural_pair(left,dict(reversed(list(right.items()))))
    assert result['same_exposure_review_required'] is True
    assert (left,right)==before
    result['structural_identity']['left']['fields']['economic_exposure']['value']='changed'
    assert (left,right)==before
