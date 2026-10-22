from copy import deepcopy
import json
from pathlib import Path

import pytest

from research.research_os.expansion.acquisition_firewall_v1 import (
    build_acquisition_plan, content_firewall, normalize_typed_pit_record, build_provenance_manifest)
from research.research_os.expansion.source_adapters_v1 import validate_adapter_spec
from research.research_os.scientific_store import sha256_json


BASE = Path('research/research_os/simulations')


def fixture():
    wave3 = json.loads((BASE/'wave3_engine_depth_fixture.json').read_text())
    wave4 = json.loads((BASE/'wave4_acquisition_firewall_fixture.json').read_text())
    request = wave4['acquisition_requests'][0]
    spec = next(a for a in wave3['adapters'] if a['adapter_id'] == request['adapter_id'])
    plan = build_acquisition_plan(validate_adapter_spec(spec), request)
    raw = wave4['raw_records'][request['request_id']]
    assert content_firewall(plan, raw)['status'] == 'PASS'
    return plan,raw


@pytest.mark.parametrize('container', ['dict','list','tuple'])
@pytest.mark.parametrize('key', ['returns','future_outcomes','execution_prices'])
def test_forbidden_payload_at_any_depth_is_blocked(container, key):
    plan,raw = fixture()
    hidden = {key: [0.1]}
    raw['payload']['nested'] = hidden if container == 'dict' else [hidden] if container == 'list' else (hidden,)
    assert content_firewall(plan, raw)['status'] == 'BLOCK'


@pytest.mark.parametrize('field', ['effective_at','published_at','captured_at'])
@pytest.mark.parametrize('value', ['', None, '2026-10-15T12:00:00', 'invalid'])
def test_record_clock_requires_qualified_value(field, value):
    plan,raw = fixture()
    raw[field] = value
    assert content_firewall(plan, raw)['status'] == 'BLOCK'


@pytest.mark.parametrize('field,value', [('clock_cutoff','2026-10-16T13:00:00Z'), ('content_classes',['returns'])])
def test_plan_body_mutation_cannot_reuse_ready_hash(field,value):
    plan,raw = fixture()
    plan['plan'][field] = value
    assert content_firewall(plan, raw)['status'] == 'BLOCK'


@pytest.mark.parametrize('field', ['network_execution_authorized','outcome_access_authorized','outcome_accessed'])
def test_secondary_firewall_entry_rejects_open_authority(field):
    plan,raw = fixture()
    plan[field] = True
    assert content_firewall(plan,raw)['status'] == 'BLOCK'


@pytest.mark.parametrize('field,value', [('record_id',''),('source_version_id',None),('content_classes',[]),('payload',[])])
def test_presence_does_not_qualify_missing_required_values(field,value):
    plan,raw = fixture()
    raw[field] = value
    assert content_firewall(plan,raw)['status'] == 'BLOCK'


def test_normalizer_cannot_reuse_pass_for_changed_raw_record():
    plan,raw = fixture()
    proof = content_firewall(plan,raw)
    raw['payload']['document_excerpt'] = 'changed documentary bytes'
    assert normalize_typed_pit_record(plan,raw,proof)['status'] == 'BLOCK'


def test_normalizer_cannot_trust_forged_pass_after_contamination():
    plan,raw = fixture()
    proof = content_firewall(plan,raw)
    raw['payload']['future_outcomes'] = [1]
    assert normalize_typed_pit_record(plan,raw,proof)['status'] == 'BLOCK'


@pytest.mark.parametrize('mutation', ['typed_payload','typed_hash','manifest_plan','foreign_firewall'])
def test_provenance_manifest_reconstructs_internal_proofs(mutation):
    plan,raw = fixture()
    firewall = content_firewall(plan,raw)
    typed = normalize_typed_pit_record(plan,raw,firewall)
    if mutation == 'typed_payload':
        typed['payload']['document_excerpt'] = 'rewritten'
    elif mutation == 'typed_hash':
        typed['typed_record_hash'] = 'a'*64
    elif mutation == 'manifest_plan':
        plan['plan_hash'] = 'a'*64
    else:
        firewall['raw_record_hash'] = 'b'*64
    assert build_provenance_manifest(plan,firewall,typed)['status'] == 'BLOCK'


def test_valid_pipeline_remains_deterministic_and_detached():
    plan,raw = fixture()
    original = deepcopy(raw)
    proof = content_firewall(plan,raw)
    typed = normalize_typed_pit_record(plan,raw,proof)
    manifest = build_provenance_manifest(plan,proof,typed)
    assert manifest['status'] == 'PASS'
    assert manifest == build_provenance_manifest(plan,proof,typed)
    typed['payload']['document_excerpt'] = 'altered export'
    assert raw == original


@pytest.mark.parametrize('value', ['', 'invalid', '2026-10-15T13:00:00'])
def test_plan_rejects_ambiguous_cutoff(value):
    wave3=json.loads((BASE/'wave3_engine_depth_fixture.json').read_text())
    wave4=json.loads((BASE/'wave4_acquisition_firewall_fixture.json').read_text())
    request=wave4['acquisition_requests'][0]
    spec=next(a for a in wave3['adapters'] if a['adapter_id']==request['adapter_id'])
    request['clock_cutoff']=value
    assert build_acquisition_plan(validate_adapter_spec(spec),request)['status']=='BLOCK'


def test_clock_boundary_and_offset_equivalence_remain_admitted():
    plan,raw=fixture()
    raw['published_at']='2026-10-15T15:00:00+02:00'
    raw['captured_at']='2026-10-15T13:00:00Z'
    assert content_firewall(plan,raw)['status']=='PASS'
    assert plan['plan_hash']==sha256_json(plan['plan'])
