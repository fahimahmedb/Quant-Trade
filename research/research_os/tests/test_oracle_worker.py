"""Real local Git remote tests: crashes, fencing, atomic publication and restart.

The remote is a disposable bare repository. No synthetic proof is labeled OCI
or GPT-OSS live evidence; actual scientific ASML/readiness suites run separately.
"""
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest

from research.research_os.github_state import GitHubStateStore, PREFIX, StateConflict, json_bytes
from research.research_os.model_backend import BackendUnavailable
from research.research_os.oracle_worker import ResearchOSWorker
from research.research_os.worker_preflight import AUTHORITY_KEYS, canonical_hash, git_blob_sha
from research.research_os.worker_stages import CanonicalStageExecutor, artifact_path

BASE = Path(__file__).resolve().parents[1]
AUTH = {k: False for k in AUTHORITY_KEYS}
RELEASE = 'a' * 40


def git(directory, *args):
    result = subprocess.run(['git', '-C', str(directory), *args], check=True, capture_output=True)
    return result.stdout.decode().strip()


class LocalStore(GitHubStateStore):
    def __init__(self, cache, remote):
        super().__init__(cache=cache, repository='test/research', branch='recovery')
        self.remote = str(remote)


class LocalModel:
    def __init__(self):
        self.calls = 0

    def healthcheck(self):
        return {'status': 'PASS', 'model': 'test-double', 'runtime': 'test'}

    def generate_structured(self, prompt, schema):
        self.calls += 1
        return {'summary': 'Documentary premise only.', 'disconfirmations': ['Missing economic evidence.']}


def recovery_task(task_id='RECOVER-TEST-001'):
    return {'task_id': task_id, 'task_type': 'LEGACY_RECOVERY', 'required_capability': 'legacy_recovery',
            'status': 'READY', 'priority': 80, 'inputs': {},
            'allowed_actions': ['recover and verify Legacy provenance'],
            'forbidden_actions': ['economic outcomes', 'capital allocation', 'orders', 'live trading'],
            'success_condition': 'Verify pinned Legacy without modifying history.',
            'authority': dict(AUTH, scope='LEGACY_READ_ONLY'),
            'lease': {'generation': 0, 'owner': None, 'claimed_at': None, 'expires_at': None},
            'created_at': '2026-10-19T00:00:00Z'}


class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.seed = self.root / 'seed'
        self.seed.mkdir()
        git(self.seed, 'init', '-b', 'recovery')
        git(self.seed, 'config', 'user.name', 'Test')
        git(self.seed, 'config', 'user.email', 'test@localhost')
        self.base = self.seed / 'research/research_os'
        for folder in ('runtime', 'hypotheses', 'sources', 'legacy'):
            shutil.copytree(BASE / folder, self.base / folder)
        (self.base / 'tasks').mkdir()
        manifest = json.loads((self.base / 'legacy/source_manifest.json').read_text())
        ledger = {'schema_version': manifest['schema_version'], 'governance': manifest['governance'],
                  'records': [{'HYPOTHESIS_ID': 'HISTORICAL-TEST', 'MECHANISM': 'test historical memory only'}]}
        raw = json_bytes(ledger)
        (self.seed / 'historical.json').write_bytes(raw)
        git(self.seed, 'add', '.')
        git(self.seed, 'commit', '-m', 'pinned test historical source')
        manifest.update(source_commit=git(self.seed, 'rev-parse', 'HEAD'), ledger_path='historical.json', ledger_blob_sha=git_blob_sha(raw))
        (self.base / 'legacy/source_manifest.json').write_bytes(json_bytes(manifest))
        self.task = recovery_task()
        self.write_seed_task(self.task)
        git(self.seed, 'add', '.')
        git(self.seed, 'commit', '-m', 'canonical test queue')
        self.remote = self.root / 'remote.git'
        subprocess.run(['git', 'clone', '--bare', str(self.seed), str(self.remote)], check=True, capture_output=True)
        self.store = LocalStore(self.root / 'cache', self.remote)
        self.now = datetime(2026, 10, 19, 10, tzinfo=timezone.utc)
        self.model = LocalModel()

    def tearDown(self):
        self.tmp.cleanup()

    def write_seed_task(self, task):
        (self.base / f'tasks/{task["task_id"]}.json').write_bytes(json_bytes(task))

    def worker(self, **kwargs):
        return ResearchOSWorker(self.store, release_sha=RELEASE, now=lambda: self.now,
                                executor=CanonicalStageExecutor(self.model), **kwargs)

    def read(self, path):
        with self.store.snapshot() as snapshot:
            return snapshot.read(PREFIX + path)

    def remote_change(self, fn):
        with self.store.snapshot() as snapshot:
            writes = fn(snapshot)
            return self.store.commit(snapshot, writes, message='independent concurrent mutation')

    def count_paths(self, prefix):
        with self.store.snapshot() as snapshot:
            return len([p for p in snapshot.blobs if p.startswith(PREFIX + prefix)])

    def test_two_wakes_continue_same_task_then_completed_restart_is_noop(self):
        first = self.worker(lane='evidence_data').wake()
        self.assertEqual(first['stage'], 'recover_or_qualify')
        self.assertEqual(first['status'], 'READY')
        second = self.worker(lane='evidence_data').wake()
        self.assertEqual(second['stage'], 'provenance_check')
        self.assertEqual(second['status'], 'COMPLETE')
        task = self.read('tasks/RECOVER-TEST-001.json')
        self.assertEqual(task['lease']['generation'], 2)
        self.assertEqual(self.count_paths('receipts/RECOVER-TEST-001/'), 2)
        receipt_count = self.count_paths('receipts/RECOVER-TEST-001/')
        self.worker(lane='evidence_data').wake()
        self.assertEqual(self.count_paths('receipts/RECOVER-TEST-001/'), receipt_count)
        self.assertEqual(len(task['execution']['completed_stages']), 2)

    def test_crash_boundaries_cannot_publish_partial_event_receipt_or_task(self):
        for point in ('before_claim', 'after_claim', 'after_execution',
                      'after_event_before_receipt', 'after_receipt_before_task_transition'):
            with self.subTest(point=point):
                # Separate task per crash prevents tests from sharing its progress.
                task = recovery_task('CRASH-' + point.replace('_', '-'))
                self.remote_change(lambda s: {PREFIX + f'tasks/{task["task_id"]}.json': task})
                def fail(actual):
                    if actual == point:
                        raise RuntimeError('simulated abrupt process death')
                # Make the test task the sole READY task in the selected lane.
                def restrict(s):
                    writes = {}
                    for other in s.tasks():
                        if other['task_id'] != task['task_id'] and other['status'] == 'READY':
                            other['status'] = 'COMPLETE'
                            writes[PREFIX + f'tasks/{other["task_id"]}.json'] = other
                    return writes
                with self.store.snapshot() as s:
                    writes = restrict(s)
                    if writes:
                        self.store.commit(s, writes, message='test isolate crash task')
                with self.assertRaises(RuntimeError):
                    self.worker(lane='evidence_data', fault=fail).wake()
                self.assertEqual(self.count_paths(f'receipts/{task["task_id"]}/'), 0)
                self.assertEqual(self.count_paths(f'artifacts/{task["task_id"]}/'), 0)
                self.now += timedelta(seconds=601)
                # New object/cache models a VM restart with zero local state.
                self.store = LocalStore(self.root / ('restarted-' + point), self.remote)
                resumed = self.worker(lane='evidence_data').wake()
                self.assertEqual(resumed['stage'], 'recover_or_qualify')
                self.assertEqual(self.count_paths(f'receipts/{task["task_id"]}/'), 1)
                self.assertEqual(self.count_paths(f'artifacts/{task["task_id"]}/'), 1)

    def test_double_trigger_during_valid_claim_is_busy_and_stale_generation_is_fenced(self):
        def crash(point):
            if point == 'after_claim':
                raise RuntimeError('power off')
        with self.assertRaises(RuntimeError):
            self.worker(lane='evidence_data', fault=crash).wake()
        claimed = self.read('tasks/RECOVER-TEST-001.json')
        duplicate = self.worker(lane='evidence_data').wake()
        self.assertEqual(duplicate['status'], 'NO_ADMISSIBLE_LANE_TASK')
        self.assertEqual(self.count_paths('receipts/RECOVER-TEST-001/'), 0)
        self.now += timedelta(seconds=601)
        self.worker(lane='evidence_data').wake()
        with self.store.snapshot() as s, self.assertRaises(StateConflict):
            self.worker()._verify_lease(s, claimed['task_id'], 1, claimed['execution']['session_id'], 'evidence_data')

    def test_two_workers_race_same_head_only_one_commit_can_win(self):
        other = LocalStore(self.root / 'competing-cache', self.remote)
        with self.store.snapshot() as a, other.snapshot() as b:
            path = PREFIX + 'tasks/RECOVER-TEST-001.json'
            task = a.read(path)
            task['status'] = 'CLAIMED'
            self.store.commit(a, {path: task}, expected_blobs={path: a.blobs[path]}, message='worker A wins')
            with self.assertRaises(StateConflict):
                other.commit(b, {path: task}, expected_blobs={path: b.blobs[path]}, message='worker B stale')
        self.assertEqual(self.read('tasks/RECOVER-TEST-001.json')['status'], 'CLAIMED')

    def test_actual_competing_workers_publish_only_one_stage(self):
        barrier = threading.Barrier(2)
        def run(index):
            store = LocalStore(self.root / f'racer-{index}', self.remote)
            def before_claim(point):
                if point == 'before_claim':
                    barrier.wait(timeout=30)
            worker = ResearchOSWorker(store, lane='evidence_data', worker_id=f'racer-{index}',
                                      release_sha=RELEASE, now=lambda: self.now, fault=before_claim)
            try:
                return worker.wake()['status']
            except StateConflict:
                return 'CONFLICT'
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(run, (1, 2)))
        self.assertEqual(sorted(results), ['CONFLICT', 'READY'])
        self.assertEqual(self.count_paths('receipts/RECOVER-TEST-001/'), 1)
        self.assertEqual(self.count_paths('artifacts/RECOVER-TEST-001/'), 1)
        self.assertTrue(git(self.remote, 'log', '-1', '--format=%s', 'recovery').endswith('[skip ci]'))

    def test_empty_queue_derives_once_without_executing_producer(self):
        def finish(s):
            task = s.read(PREFIX + 'tasks/RECOVER-TEST-001.json')
            task['status'] = 'COMPLETE'
            return {PREFIX + 'tasks/RECOVER-TEST-001.json': task}
        self.remote_change(finish)
        first = self.worker(lane='integrator_portfolio').wake()
        self.assertEqual(first['status'], 'DERIVED_ONE_READY_TASK')
        second = self.worker(lane='integrator_portfolio').wake()
        self.assertEqual(second['status'], 'NOOP_QUEUE_NOT_EMPTY')
        self.assertEqual(self.count_paths('receipts/queue-refill/'), 1)
        self.assertEqual(self.count_paths('artifacts/'), 0)
        self.assertEqual(self.model.calls, 0)

    def test_pinned_blob_integrity_is_checked_again_on_every_snapshot(self):
        with self.store.snapshot() as s:
            head = s.head
            # Changing the local archive cannot alter GitHub's next fresh state.
            (s.base / 'runtime/CONTROL_PLANE.json').write_text('{}')
        with self.store.snapshot() as s:
            self.assertEqual(s.head, head)
            self.assertEqual(s.read(PREFIX + 'runtime/CONTROL_PLANE.json')['source_of_truth'], 'GITHUB_DURABLE_STATE')

    def test_fresh_authority_change_during_execution_prevents_publication(self):
        outer = self
        class Mutator(CanonicalStageExecutor):
            def execute(self, snapshot, task, lane, stage, now, worker_id):
                result = super().execute(snapshot, task, lane, stage, now, worker_id)
                def mutate(s):
                    control = s.read(PREFIX + 'runtime/CONTROL_PLANE.json')
                    control['global_authority']['live_trading_authorized'] = True
                    return {PREFIX + 'runtime/worker_wakes/authority-mutation.json': {'simulation': True}}
                # Mutate the task authority (allowed path) as a competing owner.
                def task_mutation(s):
                    t = s.read(PREFIX + 'tasks/RECOVER-TEST-001.json')
                    t['authority']['live_trading_authorized'] = True
                    return {PREFIX + 'tasks/RECOVER-TEST-001.json': t}
                outer.remote_change(task_mutation)
                return result
        worker = self.worker(lane='evidence_data')
        worker.executor = Mutator()
        from research.research_os.worker_preflight import WorkerPreflightBlock
        with self.assertRaises(WorkerPreflightBlock):
            worker.wake()
        self.assertEqual(self.count_paths('receipts/RECOVER-TEST-001/'), 0)

    def test_one_lineage_per_wake_priority_order(self):
        other = recovery_task('RECOVER-TEST-002')
        other['priority'] = 100
        self.remote_change(lambda s: {PREFIX + 'tasks/RECOVER-TEST-002.json': other})
        wake = self.worker(lane='evidence_data').wake()
        self.assertEqual(wake['task_id'], other['task_id'])
        self.assertEqual(self.read('tasks/RECOVER-TEST-001.json')['lease']['generation'], 0)

    def producer(self):
        task = recovery_task('PRODUCER-TEST')
        task.update(task_type='FUNDAMENTAL_RESEARCH', required_capability='fundamental',
                    allowed_actions=['read Legacy', 'research one fundamental candidate', 'seek disconfirmation',
                                     'freeze hypothesis and create validation handoff'])
        def change(s):
            old = s.read(PREFIX + 'tasks/RECOVER-TEST-001.json')
            old['status'] = 'COMPLETE'
            return {PREFIX + 'tasks/RECOVER-TEST-001.json': old, PREFIX + 'tasks/PRODUCER-TEST.json': task}
        self.remote_change(change)
        return task

    def test_backend_failure_remains_retryable_with_receipt_then_bounds_retries(self):
        self.producer()
        self.worker(lane='fundamental_events').wake()  # Legacy stage
        class Failing(LocalModel):
            def healthcheck(self):
                raise BackendUnavailable('LOCAL_GPT_OSS_OFFLINE')
        for attempt in range(1, 4):
            worker = self.worker(lane='fundamental_events')
            worker.executor = CanonicalStageExecutor(Failing())
            result = worker.wake()
            self.assertEqual(result['status'], 'READY' if attempt < 3 else 'BLOCKED')
            self.now += timedelta(minutes=6)
        task = self.read('tasks/PRODUCER-TEST.json')
        self.assertEqual(task['execution']['attempts']['document_or_fundamental_research'], 3)
        self.assertEqual(self.count_paths('receipts/PRODUCER-TEST/'), 4)
        self.assertEqual(self.model.calls, 0)

    def test_producer_freeze_and_handoff_are_restart_safe_and_challenge_is_separate(self):
        self.producer()
        for expected in ('legacy_duplicate_check', 'document_or_fundamental_research', 'disconfirmation', 'freeze_hypothesis'):
            wake = self.worker(lane='fundamental_events').wake()
            self.assertEqual(wake['stage'], expected)
            self.assertEqual(wake['status'], 'READY', wake)
        hypotheses = self.count_paths('hypotheses/')
        self.store = LocalStore(self.root / 'vm-restarted-after-freeze', self.remote)
        wake = self.worker(lane='fundamental_events').wake()
        self.assertEqual(wake['status'], 'COMPLETE')
        self.assertEqual(self.count_paths('hypotheses/'), hypotheses)
        task = self.read('tasks/PRODUCER-TEST.json')
        self.assertEqual(len(task['execution']['completed_stages']), 5)
        with self.store.snapshot() as s:
            validators = [t for t in s.tasks() if t['task_type'] == 'VALIDATION']
        self.assertEqual(len(validators), 1)
        self.assertEqual(validators[0]['status'], 'READY')
        wake = self.worker(lane='independent_challenge').wake()
        self.assertEqual(wake['stage'], 'independent_validation')
        for stage in ('cross_examination', 'red_team', 'claim_restriction', 'integration_handoff'):
            wake = self.worker(lane='independent_challenge').wake()
            self.assertEqual(wake['stage'], stage)
        self.assertEqual(wake['status'], 'COMPLETE')
        self.assertEqual(self.count_paths('tasks/INTEGRATE-'), 0)
        self.assertEqual(self.count_paths('hypotheses/'), hypotheses)
        self.assertEqual(self.read('tasks/' + validators[0]['task_id'] + '.json')['lease']['owner'], 'oracle-research.independent_challenge')

    def test_lost_publication_acknowledgement_does_not_repeat_stage(self):
        def die(point):
            if point == 'after_publish':
                raise RuntimeError('lost response after commit')
        with self.assertRaises(RuntimeError):
            self.worker(lane='evidence_data', fault=die).wake()
        self.assertEqual(self.count_paths('receipts/RECOVER-TEST-001/'), 1)
        result = self.worker(lane='evidence_data').wake()
        self.assertEqual(result['stage'], 'provenance_check')

    def test_dry_run_and_noop_never_claim_or_call_model(self):
        before = git(self.remote, 'rev-parse', 'recovery')
        for mode in ('dry-run', 'noop'):
            self.worker().wake(mode=mode)
        self.assertEqual(git(self.remote, 'rev-parse', 'recovery'), before)
        self.assertEqual(self.model.calls, 0)

    def test_expired_lease_cannot_publish_even_if_task_was_not_reclaimed(self):
        def expire(point):
            if point == 'after_execution':
                self.now += timedelta(seconds=601)
        with self.assertRaises(StateConflict):
            self.worker(lane='evidence_data', fault=expire).wake()
        self.assertEqual(self.count_paths('artifacts/RECOVER-TEST-001/'), 0)
        self.assertEqual(self.count_paths('receipts/RECOVER-TEST-001/'), 0)


if __name__ == '__main__':
    unittest.main()
