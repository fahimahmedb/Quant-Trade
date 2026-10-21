"""Fresh source reconstruction must qualify the exact V2 projection it receives."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext
from research.research_os.expansion.v2_bridge import adapt_engine_output_to_v2_candidate
from research.research_os.expansion.v2_core import build_candidate, build_epoch_manifest, canonical_hash
from research.research_os.expansion.v2_independence import AXES, independent_context
from research.research_os.expansion.v2_stage_executor import ACTIVE_EPOCH_PATH, V2StageExecutor, v2_artifact_path
from research.research_os.worker_stages import CanonicalStageExecutor, StageBlocked
from tests import test_research_os_v2_worker_integration as worker_fixtures


SOURCES = {'fundamental': 'apple_fy2025_statement_cells.json',
           'event_document': 'apple_dividend_announcements.json',
           'institutional_flow': 'sec_t1_operative_rule.json'}
BASE = Path(__file__).resolve().parents[1] / 'research/research_os'
PRODUCER = {'task_id': 'RECONSTRUCTION-FIXTURE', 'process': {'pid': 1}}
VALIDATOR_PROCESS = {'pid': 2}


def fixture(engine_key):
    path = 'research/research_os/sources/' + SOURCES[engine_key]
    source = json.loads((BASE / 'sources' / SOURCES[engine_key]).read_text())
    output = ENGINE_REGISTRY[engine_key].run(source, EngineContext(PRODUCER['task_id'], synthetic_only=False))
    snapshot = worker_fixtures.FakeSnapshot({path: source})
    candidate = adapt_engine_output_to_v2_candidate(
        output, research_trial_id='T1', research_epoch_id='E1', producer_identity=PRODUCER,
        disconfirmation_manifest={'attempted': True, 'artifact_hash': 'd' * 64},
        source_binding={'source_path': path, 'source_blob': snapshot.blobs[path],
                        'source_candidate_hash': canonical_hash(output['candidate'])})
    return snapshot, candidate


class IndependentCandidateReconstructionTests(unittest.TestCase):
    def test_declared_documentary_families_reconstruct_without_filling_unknowns(self):
        for key in SOURCES:
            snapshot, candidate = fixture(key)
            # Envelope coordinates belong to other canonical gates, not the parser.
            candidate.update(research_trial_id='ANOTHER-TRIAL', research_epoch_id='ANOTHER-EPOCH',
                             disconfirmation_manifest={'attempted': True, 'artifact': 'another-declared-artifact'})
            candidate = build_candidate(candidate)
            before = deepcopy(candidate)
            with patch('research.research_os.expansion.v2_independence.process_identity', return_value=VALIDATOR_PROCESS):
                proof = independent_context(snapshot, candidate)
            self.assertTrue(all(proof[axis] is True for axis in AXES))
            self.assertEqual(proof['cognitive_scope'], 'R0_DETERMINISTIC_STRUCTURAL_CHECKS_ONLY')
            self.assertEqual(proof['semantic_diverse_review'], 'NOT_PROVEN_NO_SEMANTIC_PASS_GRANTED')
            self.assertEqual(proof['retrieval']['reconstructed_v2_candidate_hash'], candidate['candidate_hash'])
            self.assertEqual(candidate['economic_expression']['direction'], 'NOT_YET_MEASURABLE')
            self.assertFalse(proof['outcome_accessed'])
            self.assertEqual(candidate, before)
        # Quant has no declared documentary source here; a synthetic bridge cannot
        # be promoted into primary retrieval by running the new projection check.
        source_path = 'research/research_os/sources/quant-synthetic-fixture.json'
        source = {'source_ref': 'synthetic://quant-reconstruction-fixture'}
        output = ENGINE_REGISTRY['quant'].run(source, EngineContext(PRODUCER['task_id'], synthetic_only=True))
        snapshot = worker_fixtures.FakeSnapshot({source_path: source})
        candidate = adapt_engine_output_to_v2_candidate(
            output, research_trial_id='T1', research_epoch_id='E1', producer_identity=PRODUCER,
            disconfirmation_manifest={'attempted': True},
            source_binding={'source_path': source_path, 'source_blob': snapshot.blobs[source_path],
                            'source_candidate_hash': canonical_hash(output['candidate'])})
        with patch('research.research_os.expansion.v2_independence.process_identity', return_value=VALIDATOR_PROCESS):
            with self.assertRaisesRegex(StageBlocked, 'PRIMARY_SOURCE_NOT_QUALIFIED'):
                independent_context(snapshot, candidate)

    def test_correctly_rehashed_changes_cannot_borrow_the_original_source_proof(self):
        for key in SOURCES:
            snapshot, candidate = fixture(key)
            changes = {'hypothesis_id': 'DIFFERENT', 'generation_id': 'G-OTHER',
                       'claim': 'unsupported new claim', 'mechanism_statement': 'different mechanism',
                       'universe': ['OTHER'], 'clock': 'OTHER', 'horizon': 'OTHER',
                       'economic_expression': {'instrument': 'OTHER', 'direction': 'short'},
                       'falsification_scope': 'OTHER', 'decision_map': {'yes': 'PARK', 'no': 'KILL'},
                       'known_confounders': ['invented source assertion']}
            for field, value in changes.items():
                altered = deepcopy(candidate)
                altered[field] = value
                altered = build_candidate(altered)
                self.assert_candidate_block(snapshot, altered, (key, field))
            altered = deepcopy(candidate)
            extension_field = next(k for k in altered['extension'] if k != 'type')
            altered['extension'][extension_field] = 'different source fact'
            self.assert_candidate_block(snapshot, build_candidate(altered), (key, 'extension'))
            for field, value in (('source_refs', ['different://source']), ('evidence_class', 'SYNTHETIC'),
                                 ('synthetic_only', True), ('documentary_packet_hash', '0' * 64),
                                 ('engine_family', 'QUANT_MECHANISM'), ('opaque_extra', 'unverified')):
                altered = deepcopy(candidate)
                altered['evidence_manifest'][field] = value
                self.assert_candidate_block(snapshot, build_candidate(altered), (key, field))
            altered = deepcopy(candidate)
            altered['claim'] = 'changed without updating the digest'
            self.assert_candidate_block(snapshot, altered, (key, 'stale_digest'))
            altered = deepcopy(candidate)
            altered['candidate_hash'] = '0' * 64
            self.assert_candidate_block(snapshot, altered, (key, 'false_digest'))

    def assert_candidate_block(self, snapshot, candidate, label):
        before = deepcopy(candidate)
        with self.subTest(case=label), patch('research.research_os.expansion.v2_independence.process_identity',
                                           return_value=VALIDATOR_PROCESS):
            with self.assertRaisesRegex(StageBlocked, 'CANDIDATE_RECONSTRUCTION_MISMATCH'):
                independent_context(snapshot, candidate)
            self.assertEqual(candidate, before)

    def test_native_validation_refuses_before_base_reasoning_or_writes(self):
        snapshot, candidate = fixture('fundamental')
        candidate['claim'] = 'claim not present in the bound primary reconstruction'
        candidate = build_candidate(candidate)
        path = 'research/research_os/artifacts/PRODUCER/oracle-v2/candidate_frozen.json'
        harness = worker_fixtures.V2WorkerIntegrationTests()
        epoch = harness.epoch()
        trial_path = 'research/research_os/artifacts/PRODUCER/oracle-v2/research_trial.json'
        snapshot.values.update({ACTIVE_EPOCH_PATH: epoch, path: candidate, trial_path: harness.v2_trial(candidate)})
        task = {'task_id': 'VALIDATE-RECONSTRUCTION', 'task_type': 'VALIDATION', 'inputs': {'v2_candidate': path}}
        task['inputs'].update(v2_trial=trial_path, epoch_manifest_hash=build_epoch_manifest(epoch)['epoch_manifest_hash'])
        before = deepcopy(snapshot.values)
        with patch('research.research_os.expansion.v2_independence.process_identity', return_value=VALIDATOR_PROCESS), \
                patch.object(CanonicalStageExecutor, 'execute') as base:
            with self.assertRaisesRegex(StageBlocked, 'CANDIDATE_RECONSTRUCTION_MISMATCH'):
                V2StageExecutor().execute(snapshot, task, 'independent_challenge', 'independent_validation',
                                          '2026-10-20T02:20:00Z', 'validator')
            base.assert_not_called()
        self.assertEqual(snapshot.values, before)

    def test_actual_git_and_separate_interpreter_refuse_rehashed_projection_changes(self):
        case = worker_fixtures.V2WorkerIntegrationTests()
        self.addCleanup(case.doCleanups)
        harness, worker = case.real_worker()
        worker.wake(); worker.wake()
        task = harness.read('tasks/PRODUCER-TEST.json')
        code = '''
import json,sys
from copy import deepcopy
from pathlib import Path
from research.research_os.github_state import GitHubStateStore
from research.research_os.expansion.v2_core import build_candidate
from research.research_os.expansion.v2_independence import independent_context, AXES
from research.research_os.worker_stages import StageBlocked
store=GitHubStateStore(cache=Path(sys.argv[1]),repository='fixture/repo',branch='recovery')
store.remote=sys.argv[2]
with store.snapshot() as snapshot:
    candidate=snapshot.read(sys.argv[3])
    baseline=independent_context(snapshot,candidate)
    assert baseline['process'] != candidate['producer_identity']['process']
    assert all(baseline[axis] is True for axis in AXES)
    fields={'claim':'OTHER','mechanism_statement':'OTHER','universe':['OTHER'],
            'clock':'OTHER','economic_expression':{'instrument':'OTHER','direction':'short'}}
    for field,value in fields.items():
        changed=deepcopy(candidate); changed[field]=value; changed=build_candidate(changed)
        try: independent_context(snapshot,changed)
        except StageBlocked as error:
            assert str(error)=='V2_VALIDATOR_CANDIDATE_RECONSTRUCTION_MISMATCH'
        else: raise AssertionError('altered candidate accepted: '+field)
    assert independent_context(snapshot,candidate)==baseline
    print(json.dumps({'distinct_process':True,'blocked_fields':list(fields),'source_blob':baseline['retrieval']['source_blob']}))
'''
        completed = subprocess.run([sys.executable, '-c', code, str(harness.root / 'candidate-validator-cache'),
                                    str(harness.remote), v2_artifact_path(task, 'candidate_draft.json')],
                                   capture_output=True, text=True, check=True, timeout=45)
        result = json.loads(completed.stdout)
        self.assertTrue(result['distinct_process'])
        self.assertEqual(len(result['blocked_fields']), 5)
        self.assertEqual(len(result['source_blob']), 40)
