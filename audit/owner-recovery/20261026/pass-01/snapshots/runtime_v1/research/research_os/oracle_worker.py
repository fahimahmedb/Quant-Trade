"""Bounded canonical Research OS wake: fresh state -> lease -> stage -> persist.

Each stage completion, event, receipt and output is ONE Git commit. Process
death cannot expose an event without its receipt/task transition. The claim is
a separate durable transaction; objectively expired claims can be reclaimed
with a new generation. There is no local authoritative queue or model fallback.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import uuid

from .github_state import GitHubStateStore, PREFIX, StateConflict, StateUnavailable
from .model_backend import BackendUnavailable, GPTOSSBackend, LocalHTTPBackend, ModelBudget
from .queue_replenisher import derive_refill_task, queue_summary
from .worker_preflight import AUTHORITY_KEYS, WorkerPreflightBlock, canonical_hash, run_worker_preflight
from .worker_stages import (CanonicalStageExecutor, StageBlocked, artifact_path,
                            lineage_key, require_stage_authorized, stage_plan)

AUTHORITY = {k: False for k in AUTHORITY_KEYS}
ASSERTION = {'economic_experiment_performed': False, 'prospective_observation_performed': False,
             'real_capital_used': False, 'live_trading_performed': False}
ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,180}$')


def timestamp(value):
    return value.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def clock(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise StageBlocked('LEASE_CLOCK_WITHOUT_TIMEZONE')
    return parsed


def routing(snapshot, task):
    control = snapshot.read(PREFIX + 'runtime/CONTROL_PLANE.json')
    matches = [r for r in control['routing'] if r['task_type'] == task['task_type']
               and r['capability'] == task.get('required_capability')]
    if len(matches) != 1:
        raise StageBlocked('TASK_ROUTE_NOT_UNAMBIGUOUS')
    return matches[0]['lane']


def next_stage(task, lane):
    done = (task.get('execution') or {}).get('completed_stages', {})
    plan = stage_plan(task, lane)
    if set(done) - set(plan):
        raise StageBlocked('UNSUPPORTED_PERSISTED_STAGE')
    # Stages form a prefix; no skipping a research/validator gate.
    prefix = [s for s in plan if s in done]
    if prefix != plan[:len(prefix)]:
        raise StageBlocked('NON_SEQUENTIAL_STAGE_HISTORY')
    return next((s for s in plan if s not in done), None)


class ResearchOSWorker:
    def __init__(self, store, *, lane='auto', worker_id='oracle-research', release_sha,
                 executor=None, lease_seconds=600, now=None, fault=None, expected_task_id=None):
        if not ID.fullmatch(worker_id) or not re.fullmatch('[a-f0-9]{40}', release_sha):
            raise ValueError('EXACT_RELEASE_SHA_AND_SAFE_WORKER_ID_REQUIRED')
        if not 30 <= lease_seconds <= 3300:
            raise ValueError('LEASE_MUST_BE_30_TO_3300_SECONDS')
        self.store, self.lane, self.worker_id, self.release_sha = store, lane, worker_id, release_sha
        self.executor, self.lease_seconds = executor or CanonicalStageExecutor(), lease_seconds
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.fault = fault or (lambda point: None)
        self.expected_task_id = expected_task_id

    def _select(self, snapshot):
        candidates = []
        tasks, now = snapshot.tasks(), self.now()
        for task in tasks:
            if task.get('status') not in ('READY', 'CLAIMED'):
                continue
            if not ID.fullmatch(task.get('task_id', '')):
                raise StageBlocked('UNSAFE_TASK_ID')
            try:
                lane = routing(snapshot, task)
            except StageBlocked:
                continue
            if self.lane != 'auto' and lane != self.lane:
                continue
            lease = task.get('lease') or {}
            if task['status'] == 'CLAIMED':
                expires = lease.get('expires_at')
                if not expires or clock(expires) > now:
                    continue
            retry_at = (task.get('execution') or {}).get('retry_after')
            if retry_at and clock(retry_at) > now:
                continue
            key = lineage_key(task)
            if any(t.get('status') == 'CLAIMED' and t['task_id'] != task['task_id']
                   and lineage_key(t) == key for t in tasks):
                continue
            run_worker_preflight(snapshot.base, task=task)
            candidates.append((task, lane))
        candidates.sort(key=lambda pair: (-int(pair[0].get('priority', 0)), pair[0]['task_id']))
        return candidates[0] if candidates else (None, None)

    def _event(self, task, session, lane, seq, kind, payload):
        generation = task['lease']['generation']
        return {'event_id': f'{session}-{seq}', 'session_id': session,
                'worker_id': self.worker_id + '.' + lane, 'action_id': task['task_id'],
                'event_type': kind, 'event_seq': seq, 'generation': generation,
                'emitted_at': timestamp(self.now()), 'payload': payload}

    def _verify_lease(self, snapshot, task_id, generation, session, lane):
        task = snapshot.read(PREFIX + f'tasks/{task_id}.json')
        lease = task.get('lease') or {}
        if (task.get('status') != 'CLAIMED' or lease.get('generation') != generation
                or lease.get('owner') != self.worker_id + '.' + lane
                or (task.get('execution') or {}).get('session_id') != session):
            raise StateConflict('STALE_CLAIM_OR_LEASE_GENERATION')
        if not lease.get('expires_at') or clock(lease['expires_at']) <= self.now():
            raise StateConflict('LEASE_EXPIRED_BEFORE_TRANSITION')
        if routing(snapshot, task) != lane:
            raise StateConflict('TASK_LANE_CHANGED')
        preflight = run_worker_preflight(snapshot.base, task=task)
        return task, preflight

    def wake(self, *, mode='run'):
        if mode not in ('run', 'dry-run', 'noop'):
            raise ValueError('INVALID_WAKE_MODE')
        with self.store.snapshot() as snapshot:
            preflight = run_worker_preflight(snapshot.base)
            task, lane = self._select(snapshot)
            if task and self.expected_task_id and task['task_id'] != self.expected_task_id:
                raise StateConflict('CANARY_SELECTED_A_DIFFERENT_TASK_ABORT')
            base_receipt = {'release_sha': self.release_sha, 'input_head': snapshot.head,
                            'state_repository': self.store.repository, 'state_branch': self.store.branch,
                            'authority': dict(AUTHORITY), 'preflight': preflight,
                            'one_lineage_per_wake': True, 'hosted_model_calls': 0}
            if mode == 'dry-run':
                return dict(base_receipt, status='DRY_RUN', writes=0,
                            selected_task=task['task_id'] if task else None, lane=lane)
            if mode == 'noop':
                return self._idle(snapshot, base_receipt, 'READ_ONLY_CANARY', persist=False)
            if task is None:
                return self._refill_or_idle(snapshot, base_receipt)
            # Installed code never supplies authority or tasks. Re-read a complete
            # fresh snapshot immediately before the optimistic claim transaction.
            observed_head, observed_blob = snapshot.head, snapshot.blobs[PREFIX + f"tasks/{task['task_id']}.json"]
        with self.store.snapshot() as snapshot:
            if snapshot.head != observed_head:
                raise StateConflict('HEAD_CHANGED_BEFORE_CLAIM')
            task, selected_lane = self._select(snapshot)
            if task and self.expected_task_id and task['task_id'] != self.expected_task_id:
                raise StateConflict('CANARY_SELECTED_A_DIFFERENT_TASK_ABORT')
            if not task or selected_lane != lane:
                raise StateConflict('TASK_NO_LONGER_ADMISSIBLE')
            task = deepcopy(task)
            task_id = task['task_id']
            task_path = PREFIX + f'tasks/{task_id}.json'
            if snapshot.blobs[task_path] != observed_blob:
                raise StateConflict('TASK_CURRENT_BLOB_SHA_CHANGED')
            lease = task['lease']
            if type(lease.get('generation')) is not int or lease['generation'] < 0:
                raise StageBlocked('INVALID_LEASE_GENERATION')
            session = f'{task_id}-g{lease["generation"] + 1}-{uuid.uuid4().hex[:12]}'
            start = self.now()
            task['lease'] = {'generation': lease['generation'] + 1, 'owner': self.worker_id + '.' + lane,
                             'claimed_at': timestamp(start), 'expires_at': timestamp(start + timedelta(seconds=self.lease_seconds))}
            task.update(status='CLAIMED', updated_at=timestamp(start))
            execution = task.setdefault('execution', {})
            execution.update(session_id=session, release_sha=self.release_sha, lineage=lineage_key(task))
            event = self._event(task, session, lane, 1, 'ACTION_STARTED', {'queue_state': 'WORKING', 'lineage': lineage_key(task)})
            event_path = PREFIX + f'events/{task_id}/{session}-001.json'
            self.fault('before_claim')
            self.store.commit(snapshot, {task_path: task, event_path: event}, expected_blobs={task_path: observed_blob},
                              create_only=[event_path], message='Research OS claim ' + session)
            generation = task['lease']['generation']
        self.fault('after_claim')
        with self.store.snapshot() as snapshot:
            task, preflight = self._verify_lease(snapshot, task_id, generation, session, lane)
            stage = next_stage(task, lane)
            stage_head, task_blob = snapshot.head, snapshot.blobs[task_path]
            status, writes = 'CONTINUE', {}
            try:
                if stage is None:
                    output, status = {'stage': 'already_completed', 'authority': AUTHORITY}, 'COMPLETE'
                else:
                    lanes = snapshot.read(PREFIX + 'runtime/WORKFLOW_LANES.json')
                    lane_config = next(l for l in lanes['lanes'] if l['lane_id'] == lane)
                    if stage not in lane_config['same_lineage_stages'] or stage in lane_config['forbidden_stages']:
                        raise StageBlocked('STAGE_OUTSIDE_LANE_CONTRACT')
                    require_stage_authorized(task, stage)
                    output, writes, status = self.executor.execute(snapshot, deepcopy(task), lane, stage,
                                                                   timestamp(self.now()), self.worker_id + '.' + lane)
            except BackendUnavailable as exc:
                output, status = {'stage': stage, 'retryable': True, 'blocker': str(exc)}, 'RETRY'
            except (StageBlocked, ValueError, KeyError, TypeError) as exc:
                output, status = {'stage': stage, 'retryable': False, 'blocker': str(exc)}, 'BLOCKED'
            output.update(input_head=stage_head, preflight=preflight, release_sha=self.release_sha,
                          state_repository=self.store.repository, state_branch=self.store.branch,
                          authority=dict(AUTHORITY), outcome_accessed=False, economic_result='NOT_OBSERVED')
        self.fault('after_execution')
        with self.store.snapshot() as snapshot:
            fresh_task, fresh_preflight = self._verify_lease(snapshot, task_id, generation, session, lane)
            if snapshot.head != stage_head or snapshot.blobs[task_path] != task_blob:
                raise StateConflict('FRESH_STATE_CHANGED_DURING_STAGE')
            task = deepcopy(fresh_task)
            execution = task.setdefault('execution', {})
            attempts = execution.setdefault('attempts', {})
            if status == 'RETRY':
                attempts[stage] = attempts.get(stage, 0) + 1
                task['status'] = 'READY' if attempts[stage] < 3 else 'BLOCKED'
                execution['retry_after'] = timestamp(self.now() + timedelta(minutes=5))
                artifact = PREFIX + f'artifacts/{task_id}/oracle-worker/retries/{session}.json'
            else:
                artifact = artifact_path(task, stage or 'already_completed')
                if stage and status != 'BLOCKED':
                    execution.setdefault('completed_stages', {})[stage] = {'artifact': artifact, 'artifact_hash': canonical_hash(output)}
                execution.pop('retry_after', None)
                task['status'] = ('BLOCKED' if status == 'BLOCKED' else
                                  'COMPLETE' if status == 'COMPLETE' or next_stage(task, lane) is None else 'READY')
            writes[artifact] = output
            execution['last_receipt'] = PREFIX + f'receipts/{task_id}/{session}.json'
            task.update(updated_at=timestamp(self.now()))
            task['lease']['expires_at'] = timestamp(self.now())
            if task['status'] in ('COMPLETE', 'BLOCKED'):
                task['completion'] = {'receipt': execution['last_receipt'], 'completed_at': timestamp(self.now()),
                                      'result': task['status'], 'artifacts': list(writes)}
            queue = [task if t['task_id'] == task_id else t for t in snapshot.tasks()]
            queue.extend(v for p, v in writes.items() if p.startswith(PREFIX + 'tasks/'))
            summary = queue_summary(queue)
            queue_state = 'QUEUED' if summary['ready_count'] else 'WAITING' if summary['claimed_count'] else 'IDLE'
            event = self._event(task, session, lane, 2, 'SESSION_ENDED' if task['status'] == 'BLOCKED' or status == 'RETRY' else 'ACTION_COMPLETED',
                                {'stage': stage, 'result': task['status'], 'queue_state': queue_state, **summary})
            if output.get('handoff'):
                event['payload'].update(next_task_id=output['handoff'], next_lane=output['next_lane'])
            event_path = PREFIX + f'events/{task_id}/{session}-002.json'
            writes[event_path] = event
            self.fault('after_event_before_receipt')
            receipt = {'receipt_id': session, 'task_id': task_id, 'worker_id': self.worker_id + '.' + lane,
                       'session_id': session, 'lease_generation': generation,
                       'started_at': timestamp(start), 'completed_at': timestamp(self.now()),
                       'input_head': stage_head, 'status': 'BLOCKED' if task['status'] == 'BLOCKED' or status == 'RETRY' else 'COMPLETE',
                       'summary': f'{stage}: {status}; task={task["status"]}; release={self.release_sha}',
                       'artifacts': [artifact], 'evidence_refs': [event_path], 'authority_assertion': dict(ASSERTION)}
            writes[execution['last_receipt']] = receipt
            self.fault('after_receipt_before_task_transition')
            immutable = list(writes)
            writes[task_path] = task
            commit = self.store.commit(snapshot, writes, expected_blobs={task_path: task_blob}, create_only=immutable,
                                       message=f'Research OS {stage} {session}')
            self.fault('after_publish')
            return dict(base_receipt, status=task['status'], task_id=task_id, lane=lane, stage=stage,
                        session_id=session, receipt=execution['last_receipt'], output_commit=commit)

    def _idle(self, snapshot, base_receipt, reason, *, persist=True):
        result = dict(base_receipt, status=reason, queue=queue_summary(snapshot.tasks()),
                      observed_at=timestamp(self.now()), writes=0)
        if persist:
            wake_id = timestamp(self.now()).replace(':', '').replace('-', '') + '-' + uuid.uuid4().hex[:10]
            path = PREFIX + 'runtime/worker_wakes/' + wake_id + '.json'
            result['output_commit'] = self.store.commit(snapshot, {path: result}, create_only=[path], message='Research OS bounded wake ' + reason)
        return result

    def _refill_or_idle(self, snapshot, base_receipt):
        if self.lane not in ('auto', 'integrator_portfolio'):
            return self._idle(snapshot, base_receipt, 'NO_ADMISSIBLE_LANE_TASK')
        derived = derive_refill_task(frontier=snapshot.read(PREFIX + 'runtime/RESEARCH_FRONTIER.json'),
                                     tasks=snapshot.tasks(), created_at=timestamp(self.now()))
        task = derived['task']
        if task is None:
            return self._idle(snapshot, base_receipt, derived['status'])
        original_head = snapshot.head
        # A second full scan and HEAD compare, followed by atomic publication.
        with self.store.snapshot() as fresh:
            if fresh.head != original_head:
                raise StateConflict('QUEUE_CHANGED_BEFORE_REFILL')
            run_worker_preflight(fresh.base)
            confirmed = derive_refill_task(frontier=fresh.read(PREFIX + 'runtime/RESEARCH_FRONTIER.json'),
                                           tasks=fresh.tasks(), created_at=task['created_at'])
            if confirmed != derived:
                raise StateConflict('FRONTIER_DERIVATION_CHANGED')
            task_path = PREFIX + f'tasks/{task["task_id"]}.json'
            key = derived['derivation_key']
            receipt_path = PREFIX + f'receipts/queue-refill/{key}.json'
            event_path = PREFIX + f'events/queue-refill/{key}.json'
            event = {'event_id': key, 'session_id': key, 'worker_id': self.worker_id + '.integrator_portfolio',
                     'action_id': task['task_id'], 'event_type': 'ACTION_COMPLETED', 'event_seq': 1,
                     'generation': 1, 'emitted_at': timestamp(self.now()),
                     'payload': {'result': 'DERIVED_ONE_READY_TASK', 'queue_state': 'QUEUED', 'ready_count': 1,
                                 'next_task_id': task['task_id'], 'next_lane': derived['task']['derivation']['target_lane']}}
            receipt = dict(base_receipt, derivation=derived, producer_execution_same_wake=False)
            writes = {task_path: task, receipt_path: receipt, event_path: event}
            commit = self.store.commit(fresh, writes, create_only=list(writes), message='Research OS canonical queue refill ' + key)
            return dict(base_receipt, status='DERIVED_ONE_READY_TASK', task_id=task['task_id'], output_commit=commit)


def backend_from_config(config):
    model = config.get('model_backend')
    if not model:
        return None
    implementation = model.get('implementation')
    if implementation not in ('gpt_oss', 'local_http'):
        raise ValueError('UNKNOWN_MODEL_BACKEND_IMPLEMENTATION')
    cls = GPTOSSBackend if implementation == 'gpt_oss' else LocalHTTPBackend
    return cls(endpoint=model['endpoint'], model=model['model'], runtime=model['runtime'],
               budget=ModelBudget(**model.get('budget', {})))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--mode', choices=['run', 'dry-run', 'noop'], default='run')
    parser.add_argument('--healthcheck', action='store_true')
    args = parser.parse_args(argv)
    config = json.loads(Path(args.config).read_text())
    backend = backend_from_config(config)
    if args.healthcheck:
        if backend is None:
            raise BackendUnavailable('LOCAL_MODEL_NOT_CONFIGURED')
        print(json.dumps(backend.healthcheck(), sort_keys=True))
        return 0
    if args.mode == 'run':
        from deploy.oracle_release_install import _validate_release_receipt
        release_root = Path(__file__).resolve().parents[2]
        receipt = json.loads((release_root / '.quant_release_receipt.json').read_text())
        _validate_release_receipt(receipt, config['release_sha'])
        if Path(receipt['path']).resolve() != release_root:
            raise ValueError('EXECUTABLE_RELEASE_PATH_MISMATCH')
    store = GitHubStateStore(cache=Path(config['cache']), repository=config['repository'], branch=config['branch'])
    worker = ResearchOSWorker(store, lane=config.get('lane', 'auto'), worker_id=config['worker_id'],
                              release_sha=config['release_sha'], executor=CanonicalStageExecutor(backend))
    print(json.dumps(worker.wake(mode=args.mode), sort_keys=True))
    if args.mode == 'run':
        store.compact_if_due()
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except StateConflict as exc:
        print(json.dumps({'status': 'RETRY_FRESH_STATE_NEXT_WAKE', 'reason': str(exc), 'authority': AUTHORITY}))
        raise SystemExit(0)
    except (RuntimeError, ValueError, KeyError, OSError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': str(exc), 'authority': AUTHORITY}))
        raise SystemExit(1)
