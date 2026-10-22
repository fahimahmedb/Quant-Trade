from copy import deepcopy
import json
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from research.research_os.expansion import source_qualification as source


def route():
    fixture=json.loads(Path('research/research_os/simulations/wave2_hardening_fixture.json').read_text())
    return deepcopy(fixture['source_routes']['SYN-QUANT-001']),fixture['freeze_time']


@pytest.mark.parametrize('field', ['route_id','transport','locator','revision_policy','survivorship_policy','timezone'])
@pytest.mark.parametrize('value', ['', '   ', 'UNKNOWN', 'CONFLICTED'])
def test_route_required_identity_and_policy_values_are_qualified(field,value):
    item,freeze=route();item[field]=value
    assert source.qualify_source_route(item,freeze_time=freeze)['status']=='BLOCK'


@pytest.mark.parametrize('field', ['status','point_in_time_qualified','outcome_accessed'])
def test_registry_cannot_trust_altered_qualification(field):
    item,freeze=route();qualification=source.qualify_source_route(item,freeze_time=freeze)
    qualification[field]={'status':'BLOCK','point_in_time_qualified':False,'outcome_accessed':True}[field]
    with pytest.raises(ValueError):source.ImmutableSourceRouteRegistry().register(qualification)


def test_registry_requalifies_body_not_just_supplied_route_hash():
    item,freeze=route();qualification=source.qualify_source_route(item,freeze_time=freeze)
    qualification['canonical_route']['contains_outcome']=True
    with pytest.raises(ValueError):source.ImmutableSourceRouteRegistry().register(qualification)


def test_registry_does_not_replay_a_different_freeze_context():
    item,freeze=route();registry=source.ImmutableSourceRouteRegistry()
    qualification=source.qualify_source_route(item,freeze_time=freeze)
    registry.register(qualification)
    later=source.qualify_source_route(item,freeze_time='2026-10-16T15:00:00Z')
    assert qualification['route_hash']==later['route_hash']
    with pytest.raises(ValueError):registry.register(later)


def test_registry_competing_contexts_do_not_both_succeed(monkeypatch):
    item,freeze=route();first=source.qualify_source_route(item,freeze_time=freeze)
    later=source.qualify_source_route(item,freeze_time='2026-10-16T15:00:00Z')
    registry=source.ImmutableSourceRouteRegistry()
    entered,release,started=threading.Event(),threading.Event(),threading.Event()
    original=source.deepcopy
    def held(value):
        if isinstance(value,dict) and value.get('freeze_time')==freeze:
            entered.set();assert release.wait(5)
        return original(value)
    monkeypatch.setattr(source,'deepcopy',held)
    def second():started.set();return registry.register(later)
    with ThreadPoolExecutor(max_workers=2) as pool:
        one=pool.submit(registry.register,first)
        try:
            assert entered.wait(5);two=pool.submit(second);assert started.wait(5)
            assert not two.done()
        finally:release.set()
        assert one.result()==first
        with pytest.raises(ValueError):two.result()
    assert registry.snapshot()['entries']==[first]


@pytest.mark.parametrize('available,expected', [('2026-10-15T13:00:00Z','PASS'),
    ('2026-10-15T15:00:00+02:00','PASS'),('2026-10-15T13:00:00.000001Z','BLOCK'),
    ('2026-10-15T13:00:00','BLOCK')])
def test_source_clock_boundary_is_inclusive_and_timezone_explicit(available,expected):
    item,_=route();item['availability_start']=available
    assert source.qualify_source_route(item,freeze_time='2026-10-15T13:00:00Z')['status']==expected


def test_valid_blocked_qualification_can_be_recorded_without_promotion():
    item,freeze=route();item['contains_outcome']=True
    qualified=source.qualify_source_route(item,freeze_time=freeze)
    assert qualified['status']=='BLOCK'
    registry=source.ImmutableSourceRouteRegistry()
    assert registry.register(qualified)==qualified
    assert registry.snapshot()['entries'][0]['status']=='BLOCK'
    assert registry.snapshot()['outcome_routes_authorized'] is False
