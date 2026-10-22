from copy import deepcopy

import pytest

from research.research_os.expansion.final_shape import freeze_experiment_envelope,_hash
from research.research_os.tests.test_implementability_depth import _engine_output


def fixture():
    return _engine_output(),{'status':'PASS'}, {
        'dataset_provenance':{'sources':[{'version':'synthetic-v1'}]},
        'declared_metrics':[{'name':'synthetic geometry','threshold':1}],
        'cost_model_version':'fixture-cost','code_version':'fixture-code',
        'implementability_declaration':{'scope':['software-only']}}


@pytest.mark.parametrize('field',['mechanism','decision_map','dataset_provenance','declared_metrics'])
@pytest.mark.parametrize('direction',['caller','receipt'])
def test_freeze_detaches_all_admitted_mutable_identity(field,direction):
    output,impl,meta=fixture()
    frozen=freeze_experiment_envelope(output,impl,meta)
    original=deepcopy((output,meta,frozen))
    if field=='mechanism':
        target=output['candidate'] if direction=='caller' else frozen['protocol_payload']['candidate']
        target['mechanism']='rewritten'
    elif field=='decision_map':
        target=output['candidate']['decision_map'] if direction=='caller' else frozen['protocol_payload']['candidate']['decision_map']
        target.clear()
    elif field=='dataset_provenance':
        target=meta['dataset_provenance'] if direction=='caller' else frozen['dataset_provenance']
        target['sources'][0]['version']='rewritten'
    else:
        target=meta['declared_metrics'] if direction=='caller' else frozen['protocol_payload']['declared_metrics']
        target[0]['threshold']=2
    if direction=='caller':
        assert frozen==original[2]
        assert frozen['protocol_hash']==_hash(frozen['protocol_payload'])
    else:
        assert (output,meta)==original[:2]


@pytest.mark.parametrize('value',[float('nan'),float('inf')])
def test_nonfinite_protocol_cannot_receive_frozen_hash(value):
    output,impl,meta=fixture();meta['declared_metrics'][0]['threshold']=value
    frozen=freeze_experiment_envelope(output,impl,meta)
    assert frozen['status']=='NOT_FROZEN_INVALID_PROTOCOL'
    assert frozen['protocol_hash'] is None
    assert frozen['protocol_payload'] is None
    assert frozen['outcome_opened'] is False


def test_exact_double_freeze_is_deterministic_and_detached():
    output,impl,meta=fixture()
    first=freeze_experiment_envelope(output,impl,meta)
    second=freeze_experiment_envelope(output,impl,meta)
    assert first==second
    first['protocol_payload']['candidate']['decision_map'].clear()
    assert second['protocol_hash']==_hash(second['protocol_payload'])
    assert second['outcome_opened'] is False
    assert second['result']=='NOT_OBSERVED'


def test_existing_implementation_declaration_stays_detached():
    output,impl,meta=fixture()
    frozen=freeze_experiment_envelope(output,impl,meta)
    meta['implementability_declaration']['scope'].clear()
    assert frozen['protocol_payload']['implementability_declaration']['scope']==['software-only']
