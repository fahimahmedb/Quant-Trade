#!/usr/bin/env python3
"""Prepare an unprivileged host; activate only with matching live canary proof.

Separate from the scheduler-free CP1 installer. Never installs model runtimes,
downloads models, obtains credentials, grants IAM or changes scientific flags.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import pwd
import subprocess
import tempfile

from deploy.oracle_h24_canary import GATES, instance_identity
from deploy.oracle_release_install import _validate_release_receipt, validate_sha
from research.research_os.oracle_worker import backend_from_config
from research.research_os.worker_preflight import AUTHORITY_KEYS, canonical_hash

UNITS = ('quant-research-worker.service', 'quant-research-worker.timer')


def verify_qualification(report, config, *, now=None):
    if report.get('status') != 'PASS_PRE_ACTIVATION' or report.get('evidence_scope') != 'LIVE_ORACLE_VM':
        raise ValueError('LIVE_ORACLE_QUALIFICATION_REQUIRED')
    if report.get('release_sha') != config['release_sha'] or report.get('config_hash') != canonical_hash(config):
        raise ValueError('QUALIFICATION_RELEASE_OR_CONFIG_MISMATCH')
    if (report.get('instance') or {}).get('id') != config.get('vm_ocid'):
        raise ValueError('QUALIFICATION_VM_MISMATCH')
    if set(report.get('gates', {})) != set(GATES) or any(report['gates'][gate] is not True for gate in GATES):
        raise ValueError('QUALIFICATION_GATE_NOT_PASSED')
    if any((report.get('authority') or {}).get(k) is not False for k in AUTHORITY_KEYS):
        raise ValueError('QUALIFICATION_AUTHORITY_UNSAFE')
    if report.get('hosted_model_calls') != 0 or report.get('scheduler_enabled') is not False:
        raise ValueError('QUALIFICATION_EXECUTION_PATH_UNSAFE')
    completed = datetime.fromisoformat(report['completed_at'].replace('Z', '+00:00'))
    now = now or datetime.now(timezone.utc)
    if completed.tzinfo is None or not timedelta(0) <= now - completed <= timedelta(hours=6):
        raise ValueError('QUALIFICATION_EXPIRED_OR_FUTURE')
    return report


def validate_host_config(config, release):
    sha = validate_sha(config['release_sha'])
    if release.name != sha or not release.is_relative_to(Path('/opt/quant-research/releases')):
        raise ValueError('EXACT_RELEASE_REQUIRED_UNDER_OPT_QUANT_RESEARCH_RELEASES')
    receipt = _validate_release_receipt(json.loads((release / '.quant_release_receipt.json').read_text()), sha)
    if Path(receipt['path']).resolve() != release:
        raise ValueError('QUALIFIED_RELEASE_PATH_MISMATCH')
    if config.get('cache') != '/var/lib/quant-research/github.git' or config.get('lane') != 'auto':
        raise ValueError('CANONICAL_SERVICE_CACHE_AND_AUTO_LANE_REQUIRED')
    if config['repository'] != 'fahimahmedb/Quant-Trade' or config['branch'] != 'builder/oracle-economic-loop-recovery-20261019':
        raise ValueError('OWNER_AUTHORIZED_REPOSITORY_AND_BRANCH_REQUIRED')
    if not config.get('vm_ocid', '').startswith('ocid1.instance.'):
        raise ValueError('EXPLICIT_VM_OCID_REQUIRED')
    backend = backend_from_config(config)
    if backend is None or config['model_backend']['implementation'] != 'gpt_oss':
        raise ValueError('CONFIGURED_LOCAL_GPT_OSS_REQUIRED')
    return receipt


def checked(args):
    p = subprocess.run(args, capture_output=True, text=True, timeout=60)
    if p.returncode:
        raise RuntimeError('HOST_COMMAND_FAILED:' + args[0])
    return p.stdout.strip()


def atomic_write(path, data, mode=0o644):
    fd, pending = tempfile.mkstemp(prefix='.quant-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(pending, mode)
        os.replace(pending, path)
    finally:
        if os.path.exists(pending):
            os.unlink(pending)


def prepare(release, config):
    validate_host_config(config, release)
    # A repair must not point a running timer at an uncanaried release.
    for unit in ('quant-research-worker.timer', 'quant-research-worker.service'):
        state = subprocess.run(['systemctl', 'is-active', unit], capture_output=True, text=True, timeout=15)
        if state.stdout.strip() in ('active', 'activating'):
            checked(['systemctl', 'stop', unit])
    try:
        account = pwd.getpwnam('quant-research')
    except KeyError:
        checked(['useradd', '--system', '--user-group', '--home-dir', '/var/lib/quant-research',
                 '--shell', '/usr/sbin/nologin', 'quant-research'])
        account = pwd.getpwnam('quant-research')
    if account.pw_uid == 0 or account.pw_dir != '/var/lib/quant-research':
        raise ValueError('EXISTING_SERVICE_ACCOUNT_NOT_COMPATIBLE')
    state = Path('/var/lib/quant-research')
    state.mkdir(exist_ok=True, mode=0o700)
    os.chown(state, account.pw_uid, account.pw_gid)
    for root, directories, files in os.walk(release):
        os.chown(root, 0, 0)
        os.chmod(root, 0o755)
        for name in files:
            file = Path(root) / name
            if file.is_symlink():
                raise ValueError('RELEASE_SYMLINK_UNEXPECTED')
            os.chown(file, 0, 0)
            os.chmod(file, 0o644)
    for parent in (release.parent, release.parent.parent):
        os.chmod(parent, 0o755)
    config_root = Path('/etc/quant-research')
    config_root.mkdir(mode=0o750, exist_ok=True)
    os.chown(config_root, 0, account.pw_gid)
    atomic_write(config_root / 'worker.json', (json.dumps(config, indent=2) + '\n').encode(), 0o640)
    os.chown(config_root / 'worker.json', 0, account.pw_gid)
    link = Path('/opt/quant-research/current')
    pending = link.with_name('.current-pending')
    if pending.is_symlink():
        pending.unlink()
    pending.symlink_to(release, target_is_directory=True)
    pending.replace(link)
    return {'status': 'PREPARED_TIMER_NOT_INSTALLED_OR_ACTIVATED', 'sha': config['release_sha']}


def activate(release, config, qualification):
    verify_qualification(qualification, config)
    instance_identity(config['vm_ocid'])
    # Verify the prepared service-user config is the exact canaried one.
    installed_config = json.loads(Path('/etc/quant-research/worker.json').read_text())
    if installed_config != config or Path('/opt/quant-research/current').resolve() != release:
        raise ValueError('PREPARED_SERVICE_CONFIGURATION_CHANGED')
    source = release / 'deploy/systemd'
    for name in UNITS:
        atomic_write(Path('/etc/systemd/system') / name, (source / name).read_bytes())
    checked(['systemd-analyze', 'verify', *[str(Path('/etc/systemd/system') / n) for n in UNITS]])
    checked(['systemctl', 'daemon-reload'])
    checked(['systemctl', 'enable', 'quant-research-worker.timer'])
    checked(['systemctl', 'start', 'quant-research-worker.timer'])
    enabled = checked(['systemctl', 'is-enabled', 'quant-research-worker.timer'])
    active = checked(['systemctl', 'is-active', 'quant-research-worker.timer'])
    if enabled != 'enabled' or active != 'active':
        raise RuntimeError('TIMER_ENABLEMENT_NOT_CONFIRMED')
    result = {'status': 'TIMER_ENABLED_PENDING_SCHEDULED_WAKE_PROOF', 'release_sha': config['release_sha'],
              'timer_enabled': enabled, 'timer_active': active, 'authority': {k: False for k in AUTHORITY_KEYS},
              'qualified_config_hash': canonical_hash(config), 'live_evidence': True,
              'required_next': 'Observe automatic wake, journald, GitHub receipt and then final H24 receipt.'}
    atomic_write(Path('/var/lib/quant-research/activation.json'), (json.dumps(result, indent=2) + '\n').encode(), 0o600)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', required=True, type=Path)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--qualification', type=Path)
    parser.add_argument('--activate', action='store_true')
    args = parser.parse_args(argv)
    if os.geteuid() != 0:
        raise SystemExit('ROOT_REQUIRED_FOR_SYSTEMD_PACKAGING')
    release = args.release.resolve()
    config = json.loads(args.config.read_text())
    if args.activate:
        validate_host_config(config, release)
        if not args.qualification:
            parser.error('--activate requires --qualification')
        result = activate(release, config, json.loads(args.qualification.read_text()))
    else:
        result = prepare(release, config)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
