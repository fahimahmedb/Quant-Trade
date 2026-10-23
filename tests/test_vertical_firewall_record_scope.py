from copy import deepcopy

import pytest

from research.research_os.expansion.acquisition_firewall_v1 import content_firewall,normalize_typed_pit_record,build_provenance_manifest
from research.research_os.expansion.typed_pit_registry_v1 import TypedPITRegistry
from test_vertical_firewall_depth import fixture
from test_vertical_typed_registry_depth import pair


@pytest.mark.parametrize('key',['returns','future_outcomes','execution_prices'])
@pytest.mark.parametrize('placement',['top','extension'])
def test_forbidden_record_content_cannot_hide_outside_payload(key,placement):
    plan,raw=fixture()
    if placement=='top':raw[key]='SYNTHETIC_FORBIDDEN_CONTENT'
    else:raw['untrusted_extension']=({'nested':{key:'SYNTHETIC_FORBIDDEN_CONTENT'}},)
    assert content_firewall(plan,raw)['status']=='BLOCK'


def test_alternate_normalizer_cannot_certify_top_level_forbidden_content():
    plan,raw=fixture();raw['returns']='SYNTHETIC_FORBIDDEN_CONTENT'
    supplied=content_firewall(plan,raw)
    assert normalize_typed_pit_record(plan,raw,supplied)['status']=='BLOCK'


@pytest.mark.parametrize('location',['typed_record','provenance_manifest'])
def test_registry_does_not_ignore_forbidden_content_in_unhashed_extensions(location):
    record,manifest=pair();before=deepcopy((record,manifest))
    target=record if location=='typed_record' else manifest
    target['untrusted_extension']=({'returns':'SYNTHETIC_FORBIDDEN_CONTENT'},)
    registry=TypedPITRegistry()
    with pytest.raises(ValueError):registry.register(record,manifest)
    assert registry.snapshot()['entry_count']==0
    assert before[0]['payload']==record['payload']


def test_documentary_note_extension_is_not_misclassified_as_an_outcome():
    plan,raw=fixture();raw['capture_notes']={'fixture_stage':'software-only'}
    firewall=content_firewall(plan,raw);assert firewall['status']=='PASS'
    typed=normalize_typed_pit_record(plan,raw,firewall)
    manifest=build_provenance_manifest(plan,firewall,typed)
    assert manifest['status']=='PASS'
    registry=TypedPITRegistry();registry.register(typed,manifest)
    assert registry.snapshot()['entry_count']==1
