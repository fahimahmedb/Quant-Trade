from copy import deepcopy
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from research.research_os.expansion import forward_v2 as forward
from research.research_os.scientific_store import sha256_json


def contract():
    return forward.build_forward_contract_v2({'prospective_contract_id':'C','hypothesis_id':'H',
        'generation_id':'G','protocol_hash':'a'*64,'readiness':'READY_AWAITING_OWNER_AUTHORITY'},
        t0='2026-10-15T13:00:00Z',observation_scope={'instrument':'SYNTHETIC_SOFTWARE_ONLY'})


def rehash(record):
    keys=('contract_id','hypothesis_id','generation_id','protocol_hash','t0','observation_scope','material_change_requires_new_generation')
    record['contract_hash']=sha256_json({k:record[k] for k in keys})


@pytest.mark.parametrize('field',['contract_id','hypothesis_id','generation_id'])
@pytest.mark.parametrize('value',[None,'','UNKNOWN'])
def test_forward_identity_cannot_be_partial_even_after_rehash(field,value):
    record=contract();record[field]=value;rehash(record)
    with pytest.raises(ValueError):forward.ForwardRegistryV2().register(record)


@pytest.mark.parametrize('field',['observation_count','future_outcomes_consumed'])
@pytest.mark.parametrize('value',[False,0.0])
def test_zero_consumption_requires_exact_integer_proof(field,value):
    record=contract();record[field]=value
    with pytest.raises((ValueError,PermissionError)):forward.ForwardRegistryV2().register(record)


def test_competing_contract_ids_cannot_double_register_one_generation(monkeypatch):
    one=contract();two=deepcopy(one);two['contract_id']='OTHER';rehash(two)
    registry=forward.ForwardRegistryV2()
    entered,release,started=threading.Event(),threading.Event(),threading.Event()
    original=forward.deepcopy
    def held(value):
        if isinstance(value,dict) and value.get('contract_id')=='C':
            entered.set();assert release.wait(5)
        return original(value)
    monkeypatch.setattr(forward,'deepcopy',held)
    def second():started.set();return registry.register(two)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first=pool.submit(registry.register,one)
        try:
            assert entered.wait(5);second_future=pool.submit(second);assert started.wait(5)
            assert not second_future.done()
        finally:release.set()
        assert first.result()==one
        with pytest.raises(ValueError):second_future.result()
    assert registry.snapshot()['entry_count']==1


def test_immutable_save_reload_replay_keeps_observation_denied(tmp_path):
    registry=forward.ForwardRegistryV2();one=contract();registry.register(one)
    path=tmp_path/'registry.json';registry.save(path)
    restored=forward.ForwardRegistryV2.load(path);restored.register(one);restored.save(path)
    assert restored.snapshot()==registry.snapshot()
    with pytest.raises(PermissionError):restored.validate_observation_candidate('C',{'observed_at':'2026-10-16T00:00:00Z','scope':one['observation_scope']})
