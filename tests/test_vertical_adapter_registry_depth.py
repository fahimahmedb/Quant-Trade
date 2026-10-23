from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import threading
import json
from pathlib import Path

import pytest

from research.research_os.expansion import source_adapters_v1 as adapters


def spec():
    return json.loads(Path('research/research_os/simulations/wave3_engine_depth_fixture.json').read_text())['adapters'][0]


@pytest.mark.parametrize('field',['adapter_id','provider_family','permission_model','clock_semantics','revision_policy','survivorship_policy','locator_template'])
@pytest.mark.parametrize('value',['   ','UNKNOWN',True])
def test_adapter_required_text_cannot_qualify_from_ambiguity(field,value):
    item=spec();item[field]=value
    assert adapters.validate_adapter_spec(item)['status']=='BLOCK'


@pytest.mark.parametrize('field,value',[('status','BLOCK'),('activated',True),('network_access',True),
    ('outcome_access_authorized',True),('adapter_hash','a'*64),('adapter_id','foreign')])
def test_design_registry_reconstructs_the_supplied_qualification(field,value):
    item=adapters.validate_adapter_spec(spec());item[field]=value
    registry=adapters.DesignOnlyAdapterRegistry()
    with pytest.raises(ValueError):registry.register(item)
    assert registry.snapshot()['entry_count']==0


def test_changed_canonical_body_cannot_reuse_a_validated_hash():
    item=adapters.validate_adapter_spec(spec());item['canonical_spec']['allowed_content'].append('returns')
    with pytest.raises(ValueError):adapters.DesignOnlyAdapterRegistry().register(item)


def test_competing_designs_cannot_both_publish_same_adapter_identity(monkeypatch):
    one=adapters.validate_adapter_spec(spec());changed=spec();changed['locator_template']='fixture://different'
    two=adapters.validate_adapter_spec(changed)
    registry=adapters.DesignOnlyAdapterRegistry();entered,release,started=threading.Event(),threading.Event(),threading.Event()
    original=adapters.deepcopy
    def held(value):
        if isinstance(value,dict) and value.get('adapter_hash')==one['adapter_hash']:
            entered.set();assert release.wait(5)
        return original(value)
    monkeypatch.setattr(adapters,'deepcopy',held)
    def second():started.set();return registry.register(two)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first=pool.submit(registry.register,one)
        try:
            assert entered.wait(5);other=pool.submit(second);assert started.wait(5)
            assert not other.done()
        finally:release.set()
        assert first.result()==one
        with pytest.raises(ValueError):other.result()
    assert registry.snapshot()['entries']==[one]


def test_real_blocked_design_is_retained_without_activation_and_returns_detached():
    item=spec();item['network_access']=True
    qualified=adapters.validate_adapter_spec(item);assert qualified['status']=='BLOCK'
    registry=adapters.DesignOnlyAdapterRegistry();result=registry.register(qualified)
    result['canonical_spec']['allowed_content'].clear()
    assert registry.register(qualified)==qualified
    snapshot=registry.snapshot()
    assert snapshot['activated_count']==snapshot['network_enabled_count']==snapshot['outcome_authorized_count']==0


@pytest.mark.parametrize('iterator_failure',[False,True])
def test_design_batch_retains_only_valid_prefix_and_can_resume(iterator_failure):
    one=adapters.validate_adapter_spec(spec());changed=spec();changed['adapter_id']='SECOND'
    two=adapters.validate_adapter_spec(changed);bad=deepcopy(two);bad['activated']=True
    registry=adapters.DesignOnlyAdapterRegistry()
    def inputs():
        yield one
        if iterator_failure:raise RuntimeError('injected iterator failure')
        yield bad
    with pytest.raises((ValueError,RuntimeError)):registry.register_many(inputs())
    assert registry.snapshot()['entry_count']==1
    assert registry.register_many([one,two]) is None
    assert registry.register_many([one,two]) is None
    assert registry.snapshot()['entry_count']==2
