from copy import deepcopy
import json
from pathlib import Path

import pytest

from research.research_os.expansion.v2_core import build_negative_memory


def payload():
    return json.loads(Path('tests/fixtures/oracle_v2_core_fixture.json').read_text())['negative_memory']


@pytest.mark.parametrize('field',['negative_knowledge_id','failure_scope','failure_reason','revisit_policy'])
@pytest.mark.parametrize('value',['', '  ', 'UNKNOWN', None, True])
def test_scoped_negative_requires_identity_scope_and_reason(field,value):
    item=payload();item[field]=value
    with pytest.raises(ValueError):build_negative_memory(item)


@pytest.mark.parametrize('field,value',[('assumptions',None),('assumptions','implicit'),
    ('regime_context',[]),('source_context','unbound'),('revisit_conditions','new evidence')])
def test_scope_context_shape_is_explicit(field,value):
    item=payload();item[field]=value
    with pytest.raises(ValueError):build_negative_memory(item)


def test_negative_memory_roundtrip_is_detached_and_hash_stable():
    item=payload();item.update(failure_scope='synthetic regime only',failure_reason='fixture limitation')
    item['assumptions']=['synthetic inputs']
    before=deepcopy(item)
    result=build_negative_memory(item)
    assert build_negative_memory(json.loads(json.dumps(result)))==result
    item['assumptions'].append('changed')
    assert result['assumptions']==before['assumptions']


def test_explicit_unknown_context_is_retained_without_unscoping_negative():
    item=payload();item.update(failure_scope='software fixture scope',failure_reason='fixture limitation')
    item['regime_context']={'external_validity':'UNKNOWN'}
    assert build_negative_memory(item)['regime_context']==item['regime_context']
