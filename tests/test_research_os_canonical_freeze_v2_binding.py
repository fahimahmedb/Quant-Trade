"""Canonical V1 decisions must describe the V2 candidate receiving the verdict."""
from copy import deepcopy
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

from research.research_os.expansion.v2_core import build_candidate, build_epoch_manifest, canonical_hash
from research.research_os.expansion.v2_stage_executor import ACTIVE_EPOCH_PATH, V2StageExecutor
from research.research_os.github_state import PREFIX
from research.research_os.worker_stages import CanonicalStageExecutor, StageBlocked
from tests import test_research_os_v2_worker_integration as fixtures


def fixture():
    case = fixtures.V2WorkerIntegrationTests()
    candidate = case.v2_candidate()
    frozen_path, values = case.canonical_freeze_values(candidate)
    candidate_path = PREFIX + 'artifacts/PRODUCER/oracle-v2/candidate_frozen.json'
    trial_path = PREFIX + 'artifacts/PRODUCER/oracle-v2/research_trial.json'
    epoch = case.epoch()
    values.update({ACTIVE_EPOCH_PATH: epoch, candidate_path: candidate, trial_path: case.v2_trial(candidate)})
    task = {'task_id': 'VALIDATE-FREEZE', 'task_type': 'VALIDATION', 'inputs': {
        'v2_candidate': candidate_path, 'v2_trial': trial_path, 'frozen_hypothesis': frozen_path,
        'epoch_manifest_hash': build_epoch_manifest(epoch)['epoch_manifest_hash']}}
    return case, fixtures.FakeSnapshot(values), task


class CanonicalFreezeV2BindingTests(unittest.TestCase):
    def assert_before_model_block(self, snapshot, task, code, stage='independent_validation'):
        before = deepcopy(snapshot.values)
        with patch.object(CanonicalStageExecutor, 'execute') as base, \
                patch('research.research_os.expansion.v2_stage_executor.independent_context') as retrieval:
            with self.assertRaisesRegex(StageBlocked, code):
                V2StageExecutor().execute(snapshot, task, 'independent_challenge', stage,
                                          '2026-10-20T02:30:00Z', 'validator')
            base.assert_not_called()
            retrieval.assert_not_called()
        self.assertEqual(snapshot.values, before)

    def test_rehashed_subjects_and_source_hashes_cannot_borrow_the_canonical_freeze(self):
        for field, value in (('hypothesis_id', 'OTHER'), ('generation_id', 'G2'),
                             ('source_candidate_hash', 'a' * 64)):
            for stage in ('independent_validation', 'cross_examination', 'red_team', 'claim_restriction', 'integration_handoff'):
                with self.subTest(field=field, stage=stage):
                    case, snapshot, task = fixture()
                    candidate_path = task['inputs']['v2_candidate']
                    candidate = snapshot.values[candidate_path]
                    if field == 'source_candidate_hash':
                        candidate['evidence_manifest'][field] = value
                    else:
                        candidate[field] = value
                    snapshot.values[candidate_path] = build_candidate(candidate)
                    snapshot.values[task['inputs']['v2_trial']] = case.v2_trial(candidate)
                    self.assert_before_model_block(snapshot, task, 'V2_CANONICAL_FREEZE_CANDIDATE_BINDING_MISMATCH', stage)

    def test_canonical_scientific_fields_cannot_drift_from_the_recorded_engine_output(self):
        changes = {'hypothesis_id': 'OTHER', 'generation_id': 'G2', 'mechanism': 'other valid mechanism',
                   'claim': 'changed claim', 'falsification_scope': 'silently changed falsification',
                   'decision_map': {'supports': 'PROMOTE', 'fails': 'EXPLORE'}}
        for field, value in changes.items():
            with self.subTest(field=field):
                _, snapshot, task = fixture()
                snapshot.values[task['inputs']['frozen_hypothesis']][field] = value
                self.assert_before_model_block(snapshot, task, 'FROZEN_ENGINE_OUTPUT_BINDING_MISMATCH')

    def test_native_requires_output_and_retains_a_hash_valid_existing_stage_binding(self):
        _, snapshot, task = fixture()
        frozen = snapshot.values[task['inputs']['frozen_hypothesis']]
        del frozen['worker_provenance']['engine_output_ref']
        self.assert_before_model_block(snapshot, task, 'V2_CANONICAL_FROZEN_ENGINE_OUTPUT_REQUIRED')
        for reference in ('research/research_os/evaluation/closed.json', '/tmp/engine.json',
                          'research/research_os/artifacts/../sources/not-an-engine.json'):
            _, snapshot, task = fixture()
            frozen = snapshot.values[task['inputs']['frozen_hypothesis']]
            frozen['worker_provenance']['engine_output_ref'] = reference
            with patch.object(snapshot, 'read', wraps=snapshot.read) as read:
                self.assert_before_model_block(snapshot, task, 'FROZEN_ENGINE_OUTPUT_REFERENCE_REQUIRED')
                self.assertNotIn((reference,), [call.args for call in read.call_args_list])
        _, snapshot, task = fixture()
        before = deepcopy(snapshot.values)
        with patch.object(CanonicalStageExecutor, 'execute', return_value=({'stage': 'cross_examination'}, {}, 'CONTINUE')):
            result, writes, status = V2StageExecutor().execute(snapshot, task, 'independent_challenge', 'cross_examination',
                                                              '2026-10-20T02:30:00Z', 'validator')
        binding = result['v2_canonical_freeze_binding']
        self.assertEqual(binding['binding_hash'], canonical_hash({k: v for k, v in binding.items() if k != 'binding_hash'}))
        self.assertEqual(binding['frozen_hypothesis_hash'], canonical_hash(snapshot.values[task['inputs']['frozen_hypothesis']]))
        self.assertEqual(binding['v2_candidate_hash'], snapshot.values[task['inputs']['v2_candidate']]['candidate_hash'])
        self.assertEqual(writes, {})
        self.assertEqual(status, 'CONTINUE')
        self.assertTrue(all(value is False for value in result['authority'].values()))
        self.assertEqual(snapshot.values, before)

    def test_actual_two_producer_handoff_in_distinct_process_cannot_misattribute_a_verdict(self):
        case = fixtures.V2WorkerIntegrationTests()
        self.addCleanup(case.doCleanups)
        harness, worker = case.real_worker()
        template = harness.read('tasks/PRODUCER-TEST.json')
        for _ in range(5):
            self.assertIn(worker.wake()['status'], ('READY', 'COMPLETE'))
        event = deepcopy(template)
        event.update(task_id='PRODUCER-EVENT-TEST', task_type='EVENT_DOCUMENT',
                     required_capability='event_document', priority=100)
        event_path = PREFIX + 'tasks/PRODUCER-EVENT-TEST.json'
        with harness.store.snapshot() as snapshot:
            harness.store.commit(snapshot, {event_path: event}, create_only=[event_path],
                                 message='Test-only second documentary producer')
        for _ in range(5):
            self.assertIn(worker.wake()['status'], ('READY', 'COMPLETE'))
        code = '''
import json,sys
from copy import deepcopy
from pathlib import Path
from research.research_os.github_state import GitHubStateStore
from research.research_os.tests.test_oracle_worker import LocalModel
from research.research_os.expansion.v2_stage_executor import V2StageExecutor
from research.research_os.worker_stages import _frozen,StageBlocked
store=GitHubStateStore(cache=Path(sys.argv[1]),repository='fixture/repo',branch='recovery');store.remote=sys.argv[2]
with store.snapshot() as snapshot:
    tasks=[t for t in snapshot.tasks() if t['task_type']=='VALIDATION']
    a=next(t for t in tasks if t['lineage']['parent_task_id']=='PRODUCER-TEST')
    b=next(t for t in tasks if t['lineage']['parent_task_id']=='PRODUCER-EVENT-TEST')
    assert len(tasks)==2
    observed=[]
    for task in (a,b):
        model=LocalModel()
        result,writes,status=V2StageExecutor(model).execute(snapshot,task,'independent_challenge','independent_validation','2026-10-20T02:30:00Z','oracle-v2.independent_challenge')
        validator=writes[result['v2_validator']]
        _,identity,output=_frozen(snapshot,task,'independent_challenge')
        assert validator['hypothesis_id']==identity['hypothesis_id']
        assert validator['scientific_decision']=='BLOCK'
        assert validator['independence_evidence']['canonical_freeze_binding']==result['v2_canonical_freeze_binding']
        assert result['v2_canonical_freeze_binding']['frozen_hypothesis_hash']==result['frozen_hash']
        assert model.calls==1 and result['outcome_accessed'] is False
        observed.append(identity['hypothesis_id'])
    assert observed[0]!=observed[1]
    task=deepcopy(a);task['inputs']['frozen_hypothesis']=b['inputs']['frozen_hypothesis'];task['lineage']=b['lineage']
    model=LocalModel()
    try: V2StageExecutor(model).execute(snapshot,task,'independent_challenge','independent_validation','2026-10-20T02:30:00Z','oracle-v2.independent_challenge')
    except StageBlocked as error: assert str(error)=='V2_CANONICAL_FREEZE_CANDIDATE_BINDING_MISMATCH'
    else: raise AssertionError('wrong-subject verdict accepted')
    assert model.calls==0
    print(json.dumps({'subjects':observed,'foreign_freeze_blocked':True,'foreign_model_calls':model.calls}))
'''
        completed = subprocess.run([sys.executable, '-c', code, str(harness.root / 'canonical-validator-cache'),
                                    str(harness.remote)], check=True, capture_output=True, text=True, timeout=45)
        result = json.loads(completed.stdout)
        self.assertTrue(result['foreign_freeze_blocked'])
        self.assertEqual(result['foreign_model_calls'], 0)
        self.assertEqual(len(set(result['subjects'])), 2)
