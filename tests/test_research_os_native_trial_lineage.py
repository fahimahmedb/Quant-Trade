"""Native challenge/export cannot borrow an unrelated generation trial."""
from copy import deepcopy
import unittest
from unittest.mock import patch

from research.research_os.expansion.v2_core import build_candidate, build_epoch_manifest, build_research_trial, canonical_hash
from research.research_os.expansion.v2_stage_executor import (
    ACTIVE_EPOCH_PATH, V2StageExecutor, _active_epoch, _assert_native_trial_lineage, v2_artifact_path,
)
from research.research_os.worker_stages import CanonicalStageExecutor, StageBlocked
from tests import test_research_os_v2_worker_integration as fixtures


CANDIDATE = 'research/research_os/artifacts/PRODUCER/oracle-v2/candidate_frozen.json'
TRIAL = 'research/research_os/artifacts/PRODUCER/oracle-v2/research_trial.json'


def fixture():
    case = fixtures.V2WorkerIntegrationTests()
    candidate = case.v2_candidate()
    epoch = case.epoch()
    task = {'task_id': 'VALIDATE-LINEAGE', 'task_type': 'VALIDATION', 'inputs': {
        'v2_candidate': CANDIDATE, 'v2_trial': TRIAL,
        'epoch_manifest_hash': build_epoch_manifest(epoch)['epoch_manifest_hash']}}
    snapshot = fixtures.FakeSnapshot({ACTIVE_EPOCH_PATH: epoch, CANDIDATE: candidate, TRIAL: case.v2_trial(candidate)})
    return snapshot, task


def rehash(trial):
    trial['trial_hash'] = canonical_hash({k: v for k, v in trial.items() if k != 'trial_hash'})


class NativeTrialLineageTests(unittest.TestCase):
    def assert_native_block(self, snapshot, task, reason, stage='independent_validation'):
        before = deepcopy(snapshot.values)
        with patch.object(CanonicalStageExecutor, 'execute') as base, \
                patch('research.research_os.expansion.v2_stage_executor.independent_context') as retrieval:
            with self.assertRaisesRegex(StageBlocked, reason):
                V2StageExecutor().execute(snapshot, task, 'independent_challenge', stage,
                                          '2026-10-20T02:20:00Z', 'validator')
            base.assert_not_called()
            retrieval.assert_not_called()
        self.assertEqual(snapshot.values, before)

    def test_rehashed_foreign_lineage_is_refused_at_each_native_challenge_stage(self):
        changes = (
            ('trial_id', 'V2_CANDIDATE_TRIAL_BINDING_MISMATCH'),
            ('trial_epoch', 'V2_RESEARCH_LINEAGE_EPOCH_MISMATCH'),
            ('candidate_epoch', 'V2_RESEARCH_LINEAGE_EPOCH_MISMATCH'),
            ('packet', 'V2_TRIAL_SOURCE_PROPOSAL_BINDING_MISMATCH'),
            ('hypothesis_id', 'V2_TRIAL_SOURCE_PROPOSAL_BINDING_MISMATCH'),
            ('generation_id', 'V2_TRIAL_SOURCE_PROPOSAL_BINDING_MISMATCH'),
            ('candidate_hash', 'V2_TRIAL_SOURCE_PROPOSAL_BINDING_MISMATCH'),
            ('missing_source_hash', 'V2_TRIAL_SOURCE_PROPOSAL_BINDING_MISMATCH'),
            ('invalid_manifest', 'V2_TRIAL_SOURCE_PROPOSAL_BINDING_MISMATCH'),
        )
        for changed, reason in changes:
            for stage in ('independent_validation', 'cross_examination', 'red_team', 'claim_restriction', 'integration_handoff'):
                with self.subTest(changed=changed, stage=stage):
                    snapshot, task = fixture()
                    trial = snapshot.values[TRIAL]
                    if changed == 'trial_id':
                        trial['research_trial_id'] = 'OTHER'
                    elif changed == 'trial_epoch':
                        trial['research_epoch_id'] = 'OTHER'
                    elif changed == 'candidate_epoch':
                        snapshot.values[CANDIDATE]['research_epoch_id'] = 'OTHER'
                        snapshot.values[CANDIDATE] = build_candidate(snapshot.values[CANDIDATE])
                    elif changed == 'packet':
                        trial['source_packet_hash'] = '0' * 64
                    elif changed in ('missing_source_hash', 'invalid_manifest'):
                        candidate = snapshot.values[CANDIDATE]
                        if changed == 'missing_source_hash':
                            candidate['evidence_manifest']['source_candidate_hash'] = None
                            trial['generated_proposals'][0]['candidate_hash'] = None
                        else:
                            candidate['evidence_manifest'] = 'invalid'
                        snapshot.values[CANDIDATE] = build_candidate(candidate)
                    else:
                        trial['generated_proposals'][0][changed] = 'OTHER'
                    rehash(trial)
                    # Integrity alone remains valid; the semantic join must fail.
                    self.assertEqual(trial['trial_hash'], canonical_hash({k: v for k, v in trial.items() if k != 'trial_hash'}))
                    self.assert_native_block(snapshot, task, reason, stage)

    def test_trial_hash_and_derived_counts_are_verified_before_trust(self):
        for changed in ('hash', 'body', 'proposal_count', 'discard_count', 'missing_id', 'empty_proposals'):
            with self.subTest(changed=changed):
                snapshot, task = fixture()
                trial = snapshot.values[TRIAL]
                if changed == 'hash':
                    trial['trial_hash'] = '0' * 64
                elif changed == 'body':
                    trial['retry_count'] += 1
                else:
                    if changed in ('proposal_count', 'discard_count'):
                        trial[changed] = 999
                    elif changed == 'missing_id':
                        del trial['research_trial_id']
                    else:
                        trial['generated_proposals'] = []
                    rehash(trial)
                self.assert_native_block(snapshot, task, 'V2_RESEARCH_TRIAL_INTEGRITY_MISMATCH')

    def test_manifest_and_trial_reference_scope_fail_before_outside_reads(self):
        snapshot, task = fixture()
        task['inputs']['epoch_manifest_hash'] = '0' * 64
        self.assert_native_block(snapshot, task, 'V2_EPOCH_BINDING_CHANGED_BEFORE_VALIDATION')
        for path in ('research/research_os/evaluation/closed.json', '/tmp/trial.json',
                     'research/research_os/artifacts/../evaluation/closed.json', 42):
            snapshot, task = fixture()
            task['inputs']['v2_trial'] = path
            with patch.object(snapshot, 'read', wraps=snapshot.read) as read:
                self.assert_native_block(snapshot, task, 'V2_TRIAL_REFERENCE_REQUIRED')
                self.assertNotIn((path,), [call.args for call in read.call_args_list])

    def test_actual_git_generated_trial_replays_and_foreign_reference_stops_before_model(self):
        case = fixtures.V2WorkerIntegrationTests()
        self.addCleanup(case.doCleanups)
        harness, worker = case.real_worker()
        worker.wake(); worker.wake()
        producer = harness.read('tasks/PRODUCER-TEST.json')
        candidate_path = v2_artifact_path(producer, 'candidate_draft.json')
        trial_path = v2_artifact_path(producer, 'research_trial.json')
        foreign_path = 'research/research_os/artifacts/OTHER/oracle-v2/research_trial.json'
        with harness.store.snapshot() as snapshot:
            trial = snapshot.read(trial_path)
            foreign_body = {k: v for k, v in trial.items() if k != 'trial_hash'}
            foreign_body['research_trial_id'] = 'OTHER'
            harness.store.commit(snapshot, {foreign_path: build_research_trial(foreign_body)},
                                 create_only=[foreign_path], message='Test-only unrelated trial fixture')
        with harness.store.snapshot() as snapshot:
            epoch = _active_epoch(snapshot)
            task = {'task_id': 'VALIDATE-LINEAGE', 'task_type': 'VALIDATION', 'inputs': {
                'v2_candidate': candidate_path, 'v2_trial': trial_path, 'epoch_manifest_hash': epoch['epoch_manifest_hash']}}
            candidate = snapshot.read(candidate_path)
            _assert_native_trial_lineage(snapshot, task, epoch, candidate)
            task['inputs']['v2_trial'] = foreign_path
            with patch.object(CanonicalStageExecutor, 'execute') as base:
                with self.assertRaisesRegex(StageBlocked, 'V2_CANDIDATE_TRIAL_BINDING_MISMATCH'):
                    V2StageExecutor().execute(snapshot, task, 'independent_challenge', 'independent_validation',
                                              '2026-10-20T02:20:00Z', 'validator')
                base.assert_not_called()
            task['inputs']['v2_trial'] = trial_path
            _assert_native_trial_lineage(snapshot, task, epoch, candidate)
            self.assertEqual(snapshot.read(trial_path), trial)
