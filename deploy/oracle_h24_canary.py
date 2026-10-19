#!/usr/bin/env python3
"""Run on the actual Oracle VM as the intended unprivileged worker user.

Records live inventory, local inference, fresh no-op, a synthetic canonical
Legacy-only task, actual process death after claim, expiry/restart, two durable
stages and no duplicate artifacts. Does not install/replace any model or timer.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

from deploy.oracle_model_inventory import inventory
from deploy.oracle_release_install import _validate_release_receipt
from research.research_os.github_state import GitHubStateStore, PREFIX, json_bytes
from research.research_os.oracle_worker import ResearchOSWorker, backend_from_config
from research.research_os.worker_preflight import AUTHORITY_KEYS, canonical_hash
from research.research_os.worker_stages import CanonicalStageExecutor

AUTHORITY = {k: False for k in AUTHORITY_KEYS}
GATES = ('oracle_instance_verified', 'exact_release_ci', 'inventory_recorded', 'local_gpt_oss_health', 'local_structured_inference',
         'dry_run', 'readonly_noop', 'crash_after_claim', 'expired_claim_recovered',
         'two_successive_wakes', 'no_duplicate_artifacts', 'github_receipts_verified', 'authority_closed')


def instance_identity(expected):
    request = urllib.request.Request('http://169.254.169.254/opc/v2/instance/',
                                     headers={'Authorization': 'Bearer Oracle'})
    # Oracle link-local metadata is never routed through a general HTTP proxy.
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request, timeout=5) as r:
        metadata = json.loads(r.read(65536))
    result = {k: metadata.get(k) for k in ('id', 'shape', 'region', 'shapeConfig')}
    if result['id'] != expected:
        raise ValueError('ORACLE_INSTANCE_ID_MISMATCH')
    if result['shape'] not in ('VM.Standard.A1.Flex', 'VM.Standard.E2.1.Micro'):
        raise ValueError('SHAPE_NOT_IN_FREE_TIER_ALLOWLIST')
    if result['shape'] == 'VM.Standard.A1.Flex':
        shape = result.get('shapeConfig') or {}
        if not (0 < shape.get('memoryInGBs', 0) <= 24 and 0 < shape.get('ocpus', 0) <= 4):
            raise ValueError('A1_RESOURCES_NOT_PROVEN_WITHIN_ALWAYS_FREE_ENVELOPE')
    return result


def store_from_config(config):
    return GitHubStateStore(cache=Path(config['cache']), repository=config['repository'], branch=config['branch'])


def release_ci(config):
    run_id = int(config['qualification_ci_run_id'])
    url = f'https://api.github.com/repos/fahimahmedb/Quant-Trade/actions/runs/{run_id}'
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'Quant-Trade-Oracle-Qualification'}
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as r:
        run = json.loads(r.read(1024 * 1024))
    if (run.get('head_sha') != config['release_sha'] or run.get('status') != 'completed'
            or run.get('conclusion') != 'success' or run.get('name') != 'Oracle Economic Loop Recovery CI'):
        raise ValueError('EXACT_RELEASE_ORACLE_CI_NOT_SUCCESSFUL')
    return {k: run.get(k) for k in ('id', 'head_sha', 'status', 'conclusion', 'html_url')}


def worker_from_config(config, task_id, *, fault=None):
    return ResearchOSWorker(store_from_config(config), lane='evidence_data', worker_id=config['worker_id'],
                            release_sha=config['release_sha'], lease_seconds=90, fault=fault,
                            executor=CanonicalStageExecutor(), expected_task_id=task_id)


def synthetic_task(task_id):
    now = datetime.now(timezone.utc).isoformat()
    return {'task_id': task_id, 'task_type': 'LEGACY_RECOVERY', 'required_capability': 'legacy_recovery',
            'status': 'READY', 'priority': 2147483647, 'inputs': {'canary': True},
            'allowed_actions': ['recover and verify Legacy provenance without modifying history'],
            'forbidden_actions': ['new hypothesis', 'freeze', 'economic outcome', 'prospective observation',
                                  'capital allocation', 'position sizing', 'orders', 'live trading'],
            'success_condition': 'Two reproducible read-only Legacy provenance stages and durable GitHub receipts.',
            'authority': dict(AUTHORITY, scope='H24_SYNTHETIC_LEGACY_PROVENANCE_CANARY'),
            'lease': {'generation': 0, 'owner': None, 'claimed_at': None, 'expires_at': None},
            'created_at': now}


def qualify(config_path, output_path):
    config = json.loads(config_path.read_text())
    report = {'status': 'IN_PROGRESS', 'evidence_scope': 'LIVE_ORACLE_VM', 'release_sha': config['release_sha'],
              'config_hash': canonical_hash(config), 'authority': dict(AUTHORITY), 'gates': {g: False for g in GATES}}
    def save():
        temp = output_path.with_suffix('.tmp')
        temp.write_bytes(json_bytes(report))
        temp.replace(output_path)
    try:
        root = Path(__file__).resolve().parents[1]
        release = _validate_release_receipt(json.loads((root / '.quant_release_receipt.json').read_text()), config['release_sha'])
        if Path(release['path']).resolve() != root:
            raise ValueError('CANARY_EXECUTABLE_RELEASE_MISMATCH')
        report['instance'] = instance_identity(config['vm_ocid'])
        report['gates']['oracle_instance_verified'] = True
        report['exact_release_ci'] = release_ci(config)
        report['gates']['exact_release_ci'] = True
        report['inventory'] = inventory(['/usr/share/ollama/.ollama/models', '/var/lib/ollama', '/opt/models'])
        report['gates']['inventory_recorded'] = True
        backend = backend_from_config(config)
        if backend is None or config['model_backend']['implementation'] != 'gpt_oss':
            raise ValueError('INVENTORIED_LOCAL_GPT_OSS_REQUIRED_FOR_QUALIFICATION')
        report['model_health'] = backend.healthcheck()
        report['gates']['local_gpt_oss_health'] = True
        start = time.monotonic()
        schema = {'type': 'object', 'properties': {'outcome_authorized': {'type': 'boolean', 'enum': [False]}},
                  'required': ['outcome_authorized'], 'additionalProperties': False}
        answer = backend.generate_structured('Return JSON: outcome_authorized must be false. No tools or outcomes.', schema)
        if answer != {'outcome_authorized': False}:
            raise ValueError('LOCAL_MODEL_CANARY_INVALID')
        report['local_inference_seconds'] = round(time.monotonic() - start, 3)
        memory = dict(line.split(':', 1) for line in Path('/proc/meminfo').read_text().splitlines())
        if int(memory['MemAvailable'].split()[0]) < 512 * 1024:
            raise ValueError('MODEL_LEAVES_LESS_THAN_512_MIB_HEADROOM')
        if report['inventory']['disk']['free'] < 2 * 1024 ** 3:
            raise ValueError('LESS_THAN_2_GIB_DISK_HEADROOM')
        report['post_inference_resources'] = {'mem_available_kib': int(memory['MemAvailable'].split()[0]),
                                               'swap_free_kib': int(memory['SwapFree'].split()[0])}
        report['gates']['local_structured_inference'] = True
        task_id = 'AAA-ORACLE-H24-CANARY-' + config['release_sha'][:16]
        worker = ResearchOSWorker(store_from_config(config), lane='auto', worker_id=config['worker_id'],
                                  release_sha=config['release_sha'])
        report['dry_run'] = worker.wake(mode='dry-run')
        report['gates']['dry_run'] = True
        report['noop'] = worker.wake(mode='noop')
        report['gates']['readonly_noop'] = True
        store = store_from_config(config)
        path = PREFIX + f'tasks/{task_id}.json'
        with store.snapshot() as s:
            if path not in s.blobs:
                store.commit(s, {path: synthetic_task(task_id)}, create_only=[path], message='Research OS H24 provenance canary')
            task = s.read(path) if path in s.blobs else None
        # Repeated qualification for an already-completed release reuses its
        # durable recovery evidence instead of creating a second canary lineage.
        if not task or task['status'] != 'COMPLETE':
            if not task or task['status'] != 'CLAIMED':
                child = subprocess.run([sys.executable, '-m', 'deploy.oracle_h24_canary', '--config', str(config_path),
                                        '--crash-after-claim', task_id], timeout=120)
                if child.returncode != 75:
                    raise ValueError('CANARY_CHILD_DID_NOT_DIE_AFTER_CLAIM')
            with store.snapshot() as s:
                task = s.read(path)
                if task['status'] != 'CLAIMED':
                    raise ValueError('CLAIM_NOT_DURABLE_AFTER_PROCESS_DEATH')
                expiry = datetime.fromisoformat(task['lease']['expires_at'].replace('Z', '+00:00'))
            report['gates']['crash_after_claim'] = True
            save()
            while datetime.now(timezone.utc) <= expiry:
                time.sleep(min(2, max(0.1, (expiry - datetime.now(timezone.utc)).total_seconds())))
            # Fresh object reconstructs all context. No process-local checkpoint.
            report['wake_1'] = worker_from_config(config, task_id).wake()
            report['wake_2'] = worker_from_config(config, task_id).wake()
        with store.snapshot() as s:
            task = s.read(path)
            receipts = [p for p in s.blobs if p.startswith(PREFIX + f'receipts/{task_id}/')]
            artifacts = [p for p in s.blobs if p.startswith(PREFIX + f'artifacts/{task_id}/oracle-worker/')]
            events = [s.read(p) for p in s.blobs if p.startswith(PREFIX + f'events/{task_id}/')]
            started_generations = {e['generation'] for e in events if e['event_type'] == 'ACTION_STARTED'}
            if (task['status'] != 'COMPLETE' or len(receipts) != 2 or len(artifacts) != 2
                    or task['lease']['generation'] < 3 or len(started_generations) < 3):
                raise ValueError('CANARY_RECOVERY_OR_IDEMPOTENCE_NOT_PROVEN')
            for receipt_path in receipts:
                receipt = s.read(receipt_path)
                if receipt['status'] != 'COMPLETE' or any(receipt['authority_assertion'].values()):
                    raise ValueError('CANARY_RECEIPT_AUTHORITY_UNSAFE')
            report.update(github_head=s.head, task_id=task_id, receipts=receipts, artifacts=artifacts)
        for gate in GATES:
            report['gates'][gate] = True
        report.update(status='PASS_PRE_ACTIVATION', completed_at=datetime.now(timezone.utc).isoformat(),
                      scheduler_enabled=False, model_installations=0, hosted_model_calls=0,
                      restart_scope='REAL_CHILD_PROCESS_EXIT_AND_EXPIRED_LEASE; VM reboot not claimed')
        save()
        with store.snapshot() as s:
            evidence_path = PREFIX + f'artifacts/{task_id}/qualification-{report["config_hash"][:16]}.json'
            if evidence_path not in s.blobs:
                store.commit(s, {evidence_path: report}, create_only=[evidence_path], message='Research OS Oracle live pre-activation evidence')
        return report
    except Exception as exc:
        report.update(status='BLOCKED', blocker=type(exc).__name__ + ':' + str(exc))
        save()
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--crash-after-claim')
    args = parser.parse_args(argv)
    if args.crash_after_claim:
        def die(point):
            if point == 'after_claim':
                os._exit(75)
        worker_from_config(json.loads(args.config.read_text()), args.crash_after_claim, fault=die).wake()
        raise SystemExit('CLAIM_CRASH_NOT_TRIGGERED')
    if not args.output:
        parser.error('--output is required')
    print(json.dumps(qualify(args.config, args.output), sort_keys=True))


if __name__ == '__main__':
    main()
