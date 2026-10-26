from copy import deepcopy
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from research.research_os.expansion import typed_pit_registry_v1 as module
from research.research_os.expansion.acquisition_firewall_v1 import content_firewall, normalize_typed_pit_record, build_provenance_manifest
from research.research_os.scientific_store import sha256_json
from test_vertical_firewall_depth import fixture


def pair():
    plan,raw=fixture()
    firewall=content_firewall(plan,raw)
    typed=normalize_typed_pit_record(plan,raw,firewall)
    return typed,build_provenance_manifest(plan,firewall,typed)


@pytest.mark.parametrize('field,value', [('typed_record_hash','a'*64),('source_version_id','foreign'),
    ('published_at','2026-10-16T13:00:00Z'),('point_in_time_record',False),('record_origin','NETWORK'),('record_id','')])
def test_registry_rejects_unbound_typed_fields(field,value):
    typed,manifest=pair()
    typed[field]=value
    registry=module.TypedPITRegistry()
    with pytest.raises(ValueError):registry.register(typed,manifest)
    assert registry.snapshot()['entry_count']==0


@pytest.mark.parametrize('field,value', [('typed_record_hash','a'*64),('record_id','foreign'),
    ('source_version_id','foreign'),('published_at','2026-10-16T00:00:00Z'),('raw_record_hash','b'*64),
    ('origin','NETWORK')])
def test_even_rehashed_foreign_manifest_cannot_certify_record(field,value):
    typed,manifest=pair()
    manifest['manifest'][field]=value
    manifest['manifest_hash']=sha256_json(manifest['manifest'])
    registry=module.TypedPITRegistry()
    with pytest.raises(ValueError):registry.register(typed,manifest)
    assert registry.snapshot()['entry_count']==0


@pytest.mark.parametrize('field', ['outcome_accessed','network_accessed'])
def test_manifest_authority_flags_cannot_be_laundered(field):
    typed,manifest=pair();manifest[field]=True
    with pytest.raises(ValueError):module.TypedPITRegistry().register(typed,manifest)


def test_manifest_hash_must_be_verified():
    typed,manifest=pair();manifest['manifest_hash']='a'*64
    with pytest.raises(ValueError):module.TypedPITRegistry().register(typed,manifest)


def test_replay_and_snapshot_are_detached():
    typed,manifest=pair();registry=module.TypedPITRegistry()
    one=registry.register(typed,manifest)
    two=registry.register(deepcopy(typed),deepcopy(manifest))
    assert one==two
    one['source_version_id']='changed'
    snapshot=registry.snapshot();snapshot['entries'].clear()
    assert registry.snapshot()['entry_count']==1
    assert registry.snapshot()['entries'][0]==two


def test_competing_registration_cannot_replace_different_content(monkeypatch):
    typed,manifest=pair()
    other=deepcopy(typed);other['payload']['document_excerpt']='second valid record body'
    plan,raw=fixture();raw['payload']=other['payload']
    firewall=content_firewall(plan,raw)
    other=normalize_typed_pit_record(plan,raw,firewall)
    other_manifest=build_provenance_manifest(plan,firewall,other)
    registry=module.TypedPITRegistry()
    # Hold the first copy at its pre-publication boundary. The competing writer
    # previously won publication and was then overwritten by the paused writer.
    entered,release,started=threading.Event(),threading.Event(),threading.Event()
    original=module.deepcopy
    def held(value):
        if isinstance(value,dict) and value.get('typed_record_hash')==typed['typed_record_hash'] and 'payload' not in value:
            entered.set();assert release.wait(5)
        return original(value)
    monkeypatch.setattr(module,'deepcopy',held)
    def second():
        started.set();return registry.register(other,other_manifest)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first=pool.submit(registry.register,typed,manifest)
        try:
            assert entered.wait(5)
            second_future=pool.submit(second)
            assert started.wait(5)
            assert not second_future.done()
        finally:release.set()
        assert first.result()['typed_record_hash']==typed['typed_record_hash']
        with pytest.raises(ValueError):second_future.result()
    assert registry.snapshot()['entry_count']==1


@pytest.mark.parametrize('key', ['returns','future_outcomes','execution_prices'])
def test_secondary_registry_api_does_not_admit_fully_rehashed_outcome_content(key):
    typed,manifest=pair()
    typed['payload']['nested']=[{key:[0.1]}]
    body={k:v for k,v in typed.items() if k not in {'status','typed_record_hash','outcome_accessed','network_origin','point_in_time_record'}}
    typed['typed_record_hash']=sha256_json(body)
    manifest['manifest']['typed_record_hash']=typed['typed_record_hash']
    manifest['manifest_hash']=sha256_json(manifest['manifest'])
    with pytest.raises(ValueError):module.TypedPITRegistry().register(typed,manifest)
