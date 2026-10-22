import json

import pytest

from quant.edge_lab.engine import initialize
from quant.edge_lab.store import Store,Refused,digest,event,verify,strict_json


@pytest.mark.parametrize('budget',['tokens_total','cpu_seconds_total','metadata_bytes_per_tick'])
def test_overflow_json_cannot_disable_control_budget(tmp_path,budget):
    initialize(tmp_path);store=Store(tmp_path)
    control=store.control();control['limits'][budget]='OVERFLOW_TOKEN'
    store.control_path.write_text(json.dumps(control).replace('"OVERFLOW_TOKEN"','1e999'))
    with pytest.raises(Refused):store.control()


@pytest.mark.parametrize('schema',[True,1.0])
def test_control_schema_requires_exact_integer_version(tmp_path,schema):
    initialize(tmp_path);store=Store(tmp_path)
    control=store.control();control['schema']=schema
    store.control_path.write_text(json.dumps(control))
    with pytest.raises(Refused):store.control()


@pytest.mark.parametrize('schema',[True,1.0])
def test_state_schema_cannot_be_rehashed_as_boolean_or_float(tmp_path,schema):
    initialize(tmp_path);store=Store(tmp_path);state=store.read();state['schema']=schema
    state['integrity']=digest({k:v for k,v in state.items() if k!='integrity'})
    with pytest.raises(Refused):verify(state)


@pytest.mark.parametrize('sequence',[True,1.0])
def test_event_sequence_requires_exact_integer_even_with_matching_hash(tmp_path,sequence):
    initialize(tmp_path);state=Store(tmp_path).read()
    state['events']=[]
    event(state,'SYNTHETIC',{'source':'software-only'})
    state['events'][0]['sequence']=sequence
    state['events'][0]['hash']=digest({k:v for k,v in state['events'][0].items() if k!='hash'})
    state['integrity']=digest({k:v for k,v in state.items() if k!='integrity'})
    with pytest.raises(Refused):verify(state)


@pytest.mark.parametrize('raw',['{"x":NaN}','{"x":Infinity}','{"x":1,"x":2}','{"x":1e999}'])
def test_strict_json_rejects_ambiguous_and_nonfinite_numbers(tmp_path,raw):
    path=tmp_path/'input.json';path.write_text(raw)
    with pytest.raises(Refused):strict_json(path)


def test_exact_schema_and_finite_budget_survive_restart(tmp_path):
    initialize(tmp_path);store=Store(tmp_path);control=store.control()
    control['limits']['cpu_seconds_total']=0.125
    store.control_path.write_text(json.dumps(control))
    assert Store(tmp_path).control()['limits']['cpu_seconds_total']==0.125
    assert Store(tmp_path).read()['schema']==1
