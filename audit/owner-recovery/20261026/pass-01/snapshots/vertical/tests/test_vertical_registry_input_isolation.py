"""Caller-owned objects cannot change a proof after admission checks."""
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import threading

import pytest

from research.research_os.expansion import forward_v2 as forward
from research.research_os.expansion import typed_pit_registry_v1 as typed_module
from research.research_os.expansion import source_qualification as source
from research.research_os.expansion.acquisition_firewall_v1 import content_firewall,normalize_typed_pit_record,build_provenance_manifest
from test_vertical_forward_registry_depth import contract
from test_vertical_typed_registry_depth import pair
from test_vertical_source_route_depth import route
from test_vertical_firewall_depth import fixture


def paused_call(call,entered,release,mutate):
    with ThreadPoolExecutor(max_workers=1) as pool:
        future=pool.submit(call)
        try:
            assert entered.wait(5),'publication checkpoint not reached'
            mutate()
        finally:
            release.set()
        return future.result()


def forward_pause(monkeypatch):
    entered,release=threading.Event(),threading.Event()
    clock_seen=False
    original_clock,original_copy=forward._parse_utc,forward.deepcopy
    def clock(value):
        nonlocal clock_seen
        result=original_clock(value);clock_seen=True
        return result
    def copy(value):
        if clock_seen and isinstance(value,dict) and 'contract_id' in value:
            entered.set();assert release.wait(5)
        return original_copy(value)
    monkeypatch.setattr(forward,'_parse_utc',clock)
    monkeypatch.setattr(forward,'deepcopy',copy)
    return entered,release


@pytest.mark.parametrize('field',['contract_id','observation_scope','observation_count'])
def test_forward_keeps_the_exact_validated_input(monkeypatch,field):
    supplied=contract();expected=deepcopy(supplied);registry=forward.ForwardRegistryV2()
    entered,release=forward_pause(monkeypatch)
    def mutate():
        if field=='observation_scope':supplied[field]['instrument']='changed after checks'
        elif field=='observation_count':supplied[field]=1
        else:supplied[field]='FOREIGN'
    returned=paused_call(lambda:registry.register(supplied),entered,release,mutate)
    assert returned==expected
    assert registry.snapshot()['entries']==[expected]


def test_forward_caller_cannot_import_authority_after_admission(monkeypatch,tmp_path):
    supplied=contract();expected=deepcopy(supplied);registry=forward.ForwardRegistryV2()
    entered,release=forward_pause(monkeypatch)
    def mutate():
        from research.research_os.scientific_store import sha256_json
        supplied.update(state='AUTHORIZED_FOR_EXACT_SCOPE',owner_authorization='AUTHORIZED_FOR_EXACT_SCOPE',
                        authorization_scope_hash=sha256_json(supplied['observation_scope']))
    paused_call(lambda:registry.register(supplied),entered,release,mutate)
    with pytest.raises(PermissionError):
        registry.validate_observation_candidate('C',{'observed_at':'2026-10-16T00:00:00Z','scope':expected['observation_scope']})
    assert registry.snapshot()['authorized_count']==0
    path=tmp_path/'forward.json';registry.save(path)
    assert forward.ForwardRegistryV2.load(path).snapshot()==registry.snapshot()


@pytest.mark.parametrize('field',['source_version_id','published_at','record_id'])
def test_typed_registry_metadata_cannot_change_after_proof_validation(monkeypatch,field):
    supplied,manifest=pair();expected=deepcopy(supplied);registry=typed_module.TypedPITRegistry()
    entered,release=threading.Event(),threading.Event()
    plan_hash=supplied['plan_hash'];original=typed_module.re.fullmatch
    def match(pattern,value,*args,**kwargs):
        result=original(pattern,value,*args,**kwargs)
        if pattern==r'[0-9a-f]{64}' and value==plan_hash:
            entered.set();assert release.wait(5)
        return result
    monkeypatch.setattr(typed_module.re,'fullmatch',match)
    returned=paused_call(lambda:registry.register(supplied,manifest),entered,release,
                         lambda:supplied.update({field:'changed after checks'}))
    assert returned[field]==expected[field]
    assert registry.snapshot()['entries'][0][field]==expected[field]


@pytest.mark.parametrize('field',['status','freeze_time','canonical_route','route_id'])
def test_source_registry_copies_the_proof_it_validated(monkeypatch,field):
    item,freeze=route();supplied=source.qualify_source_route(item,freeze_time=freeze)
    expected=deepcopy(supplied);registry=source.ImmutableSourceRouteRegistry()
    entered,release=threading.Event(),threading.Event();checked=False
    original_check,original_copy=source._qualified_route_text,source.deepcopy
    def check(value):
        nonlocal checked
        result=original_check(value);checked=True
        return result
    def copy(value):
        if checked and isinstance(value,dict) and 'route_hash' in value:
            entered.set();assert release.wait(5)
        return original_copy(value)
    monkeypatch.setattr(source,'_qualified_route_text',check)
    monkeypatch.setattr(source,'deepcopy',copy)
    def mutate():
        if field=='canonical_route':supplied[field]['contains_outcome']=True
        elif field=='status':supplied[field]='BLOCK'
        elif field=='route_id':supplied[field]='FOREIGN'
        else:supplied[field]='2026-10-20T00:00:00Z'
    returned=paused_call(lambda:registry.register(supplied),entered,release,mutate)
    assert returned==expected
    assert registry.snapshot()['entries']==[expected]
    assert registry.register(expected)==expected


def second_pair():
    plan,raw=fixture();raw['record_id']='PIT-SECOND'
    proof=content_firewall(plan,raw)
    record=normalize_typed_pit_record(plan,raw,proof)
    return record,build_provenance_manifest(plan,proof,record)


@pytest.mark.parametrize('iterator_failure',[False,True])
def test_typed_batch_partial_prefix_has_exact_replay_and_recovery(iterator_failure):
    first=pair();second=second_pair();registry=typed_module.TypedPITRegistry()
    bad=deepcopy(second);bad[1]['manifest_hash']='invalid'
    def inputs():
        yield first
        if iterator_failure:raise RuntimeError('injected iterator failure')
        yield bad
    with pytest.raises((ValueError,RuntimeError)):registry.register_many(inputs())
    assert registry.snapshot()['entry_count']==1
    recovered=registry.register_many([first,second])
    assert registry.snapshot()['entry_count']==2
    assert registry.register_many([first,second])==recovered


@pytest.mark.parametrize('iterator_failure',[False,True])
def test_source_batch_partial_prefix_has_exact_replay_and_recovery(iterator_failure):
    item,freeze=route();first=source.qualify_source_route(item,freeze_time=freeze)
    item['route_id']='SECOND';second=source.qualify_source_route(item,freeze_time=freeze)
    registry=source.ImmutableSourceRouteRegistry();bad=deepcopy(second);bad['status']='INVALID'
    def inputs():
        yield first
        if iterator_failure:raise RuntimeError('injected iterator failure')
        yield bad
    with pytest.raises((ValueError,RuntimeError)):registry.register_many(inputs())
    assert registry.snapshot()['entry_count']==1
    recovered=registry.register_many([first,second])
    assert registry.snapshot()['entry_count']==2
    assert registry.register_many([first,second])==recovered
