"""Additional falsification controls across existing North Star nodes.

These controls do not give whole-module D3/D4 qualification.
"""
from copy import deepcopy
from itertools import permutations
import json
from pathlib import Path

import pytest

from research.research_os.expansion.v2_core import (
    CLOSED_AUTHORITY,assert_authority_closed,classify_model_pit,release_feedback)
from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext,validate_engine_output
from research.research_os.engines.cross_exam import cross_examine
from research.research_os.engines.shadow import shadow_register
from research.research_os.engines.decay import decay_monitor
from research.research_os.expansion.portfolio_v2 import portfolio_diagnostics_v2
from research.research_os.tests.test_economic_identity_portfolio_readiness import identity


@pytest.mark.parametrize('key',list(CLOSED_AUTHORITY))
@pytest.mark.parametrize('value',[True,0,None])
def test_all_owner_authority_flags_require_exact_false(key,value):
    authority=dict(CLOSED_AUTHORITY);authority[key]=value
    with pytest.raises(ValueError):assert_authority_closed(authority)


@pytest.mark.parametrize('field',['source_epoch_closed','policy_allows_release'])
@pytest.mark.parametrize('value',[False,1,None])
def test_feedback_requires_explicit_close_and_release(field,value):
    args=dict(source_epoch_id='source',successor_epoch_id='successor',source_epoch_closed=True,
              policy_allows_release=True,feedback_hash='a'*64)
    args[field]=value
    with pytest.raises(ValueError):release_feedback(**args)


@pytest.mark.parametrize('authorized,started',[(False,False),(False,True),(True,False),(1,True),(None,True)])
def test_legacy_shadow_decay_cannot_consume_without_both_explicit_states(authorized,started):
    result=decay_monitor({'prospective_observation_authorized':authorized,'registrations':[{'observation_started':started}]})
    assert result['status']=='INACTIVE_BY_AUTHORITY'
    assert result['observations_consumed']==0


def test_legacy_decay_alternate_authorized_path_still_denies_execution():
    with pytest.raises(RuntimeError):
        decay_monitor({'prospective_observation_authorized':True,'registrations':[{'observation_started':True}]})


@pytest.mark.parametrize('source_pit',[False,True])
@pytest.mark.parametrize('cutoff',['PROVABLY_BEFORE_CUTOFF','NOT_PROVABLE','AFTER_CUTOFF'])
def test_model_pit_never_promotes_source_only_truth(source_pit,cutoff):
    result=classify_model_pit(source_pit=source_pit,model_knowledge_cutoff_status=cutoff)
    assert result['historical_generation_status']==(
        'SOURCE_NOT_PIT' if not source_pit else 'SOURCE_AND_MODEL_PIT' if cutoff=='PROVABLY_BEFORE_CUTOFF'
        else 'HISTORICAL_IDEA_GENERATION_NOT_PROVABLY_PIT' if cutoff=='NOT_PROVABLE' else 'MODEL_KNOWLEDGE_AFTER_CUTOFF')


@pytest.mark.parametrize('key',list(ENGINE_REGISTRY))
def test_existing_producer_families_replay_without_input_mutation(key):
    fixture=json.loads(Path('research/research_os/simulations/aggressive_architecture_fixture.json').read_text())
    source=fixture['sources'][key];before=deepcopy(source)
    context=EngineContext('VERTICAL-SYNTHETIC-SURVEY')
    one=ENGINE_REGISTRY[key].run(source,context)
    validate_engine_output(one)
    assert one==ENGINE_REGISTRY[key].run(source,context)
    assert source==before
    assert one['synthetic_only'] is True
    assert one['candidate']['observation_authorization']=='NOT_AUTHORIZED'


@pytest.mark.parametrize('key',list(ENGINE_REGISTRY))
def test_producer_mode_cannot_be_relabeled_documentary_without_evidence(key):
    fixture=json.loads(Path('research/research_os/simulations/aggressive_architecture_fixture.json').read_text())
    with pytest.raises(ValueError):ENGINE_REGISTRY[key].run(fixture['sources'][key],EngineContext('SURVEY',synthetic_only=False))


def test_cross_exam_and_shadow_registration_keep_producer_truth_unchanged():
    fixture=json.loads(Path('research/research_os/simulations/aggressive_architecture_fixture.json').read_text())
    outputs=[engine.run(fixture['sources'][key],EngineContext('SURVEY')) for key,engine in ENGINE_REGISTRY.items()]
    before=deepcopy(outputs)
    challenge=cross_examine(outputs)
    shadow=shadow_register(outputs)
    assert challenge['status']=='COMPLETE'
    assert challenge['mutated_hypotheses'] is False
    assert shadow['prospective_observation_authorized'] is False
    assert all(r['observation_started'] is False for r in shadow['registrations'])
    assert outputs==before


@pytest.mark.parametrize('order',list(permutations(['A','B','C'])))
def test_portfolio_order_does_not_change_pairwise_semantics(order):
    values={'A':identity('A'),'B':identity('B',payer='another'),'C':identity('C',timing_clock='UNKNOWN')}
    result=portfolio_diagnostics_v2([values[k] for k in order])
    baseline=portfolio_diagnostics_v2([values[k] for k in sorted(values)])
    normalize=lambda r:{frozenset((p['left'],p['right'])):(p['dimensions'],p['economic_structure']) for p in r['pairwise']}
    assert normalize(result)==normalize(baseline)
    assert result['structural_novelty']==baseline['structural_novelty']
    assert result['return_series_consumed'] is False
