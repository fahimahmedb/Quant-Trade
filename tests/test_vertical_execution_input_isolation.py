from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import threading

import pytest

from research.research_os.expansion import persistent_state as persistence
from research.research_os.expansion.experiment_runner import DryRunExperimentRunner
from research.research_os.scientific_store import sha256_json
from research.research_os.tests.test_work_build_depth import sources,execution_plan


def fixture():
    inputs=[{'engine_key':'fundamental','source':sources()['fundamental']}]
    runner,plan=execution_plan(inputs)
    return runner,plan,inputs


@pytest.mark.parametrize('mutation',['append_input','clear_inputs','experiment_identity'])
@pytest.mark.parametrize('lost_completion_ack',[False,True])
def test_prepared_binding_is_the_exact_body_executed_after_caller_mutation(tmp_path,monkeypatch,mutation,lost_completion_ack):
    runner,plan,inputs=fixture();original_plan,original_inputs=deepcopy((plan,inputs))
    entered,release=threading.Event(),threading.Event();write=persistence.write_immutable_json
    def paused(path,payload):
        write(path,payload)
        if str(path).endswith('.prepared.json'):
            entered.set();assert release.wait(5)
        elif lost_completion_ack and str(path).endswith('.completed.json'):
            raise OSError('injected loss of completed receipt ACK')
    with monkeypatch.context() as patch:
        patch.setattr(persistence,'write_immutable_json',paused)
        with ThreadPoolExecutor(max_workers=1) as pool:
            future=pool.submit(runner.execute,plan,inputs,tmp_path)
            try:
                assert entered.wait(5)
                if mutation=='append_input':inputs.append(deepcopy(inputs[0]))
                elif mutation=='clear_inputs':inputs.clear()
                else:plan['experiment_id']='FOREIGN'
            finally:release.set()
            if lost_completion_ack:
                with pytest.raises(OSError):future.result()
            else:future.result()
    completed=next(tmp_path.glob('*.completed.json'))
    committed=persistence.read_immutable_json(completed)
    assert committed['experiment_id']==original_plan['experiment_id']
    assert committed['input_hash']==sha256_json(original_inputs)
    assert len(committed['records'])==len(original_inputs)==1
    assert committed['outcome_accessed'] is False
    assert committed['economic_result']=='NOT_OBSERVED'
    replay=DryRunExperimentRunner().execute(original_plan,original_inputs,tmp_path)
    assert replay==committed
    assert len(list(tmp_path.glob('*.prepared.json')))==len(list(tmp_path.glob('*.completed.json')))==1


def test_two_consumers_publish_one_identical_documentary_receipt(tmp_path):
    runner,plan,inputs=fixture();barrier=threading.Barrier(2)
    def execute(_):
        barrier.wait(5)
        return runner.execute(deepcopy(plan),deepcopy(inputs),Path(tmp_path))
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(execute,[1,2]))
    assert results[0]==results[1]
    assert len(list(tmp_path.glob('*.completed.json')))==1
    assert persistence.read_immutable_json(next(tmp_path.glob('*.completed.json')))==results[0]
