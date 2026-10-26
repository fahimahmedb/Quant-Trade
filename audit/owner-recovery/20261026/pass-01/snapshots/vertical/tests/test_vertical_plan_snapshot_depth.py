from copy import deepcopy

import pytest

from research.research_os.expansion.experiment_runner import DryRunExperimentRunner
from research.research_os.scientific_store import sha256_json
from research.research_os.tests.test_experiment_runner_frozen_protocol import fixture


def inputs():
    envelope,qualifications,meta=fixture()
    meta['environment']={'runtime':{'python':'synthetic-version'},'dependencies':['synthetic-v1']}
    metrics=[{'name':'gross_return','rule':{'geometry':'predeclared'}},
             {'name':'net_return','rule':{'geometry':'predeclared'}}]
    meta['declared_metrics']=deepcopy(metrics)
    envelope['protocol_payload']['declared_metrics']=deepcopy(metrics)
    envelope['protocol_hash']=sha256_json(envelope['protocol_payload'])
    return envelope,qualifications,meta


@pytest.mark.parametrize('field',['environment','declared_metrics'])
@pytest.mark.parametrize('direction',['caller','receipt'])
def test_planning_freezes_nested_environment_and_metric_identity(field,direction):
    envelope,qualifications,meta=inputs();original=deepcopy((envelope,qualifications,meta))
    runner=DryRunExperimentRunner();plan=runner.plan(envelope,qualifications,meta)
    assert plan['status']=='READY_FOR_REPRODUCIBLE_DRY_RUN'
    before=deepcopy(plan)
    if direction=='caller':target=meta[field]
    elif field=='environment':target=plan['frozen_protocol']['environment']
    else:target=plan['plan']['declared_metrics']
    if field=='environment':target['runtime']['python']='changed'
    else:target[0]['rule']['geometry']='changed'
    if direction=='caller':
        assert plan==before
        assert runner.replay(plan)['status']=='REPLAY_MATCH'
    else:assert (envelope,qualifications,meta)==original


def test_valid_nested_plan_roundtrip_replay_keeps_all_authorities_closed():
    envelope,qualifications,meta=inputs();runner=DryRunExperimentRunner()
    plan=runner.plan(envelope,qualifications,meta)
    assert runner.plan(envelope,qualifications,meta)==plan
    assert runner.replay(plan)['status']=='REPLAY_MATCH'
    receipt=plan['pre_outcome_receipt']
    for key in ('economic_experiment_authorized','prospective_observation_authorized','real_capital_authorized','live_trading_authorized'):
        assert receipt[key] is False
