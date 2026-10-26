#!/usr/bin/env python3
"""Install an optional exact-SHA Site observer around the unchanged qualified V2 core.

Owner/root boundary only. The rotated credential arrives encrypted for this VM;
it never enters command history, stdout, Git, the scientific config or receipts.
"""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import pwd
import re
import stat
import subprocess
import time
import urllib.request

CORE_SHA = 'a67ffec48fff895d5edc42171855e2213e49cf0d'
SITE = 'https://quant-trade-lab.sassylime.chatgpt.site'
SERVICE = 'quant-research-worker-v2.service'
TIMER = 'quant-research-worker-v2.timer'
PROJECTION_HASH = '431fa165c6dd17e7aa4b042ac58a73467d3cde36a4ff387bc09f764262d66596'


@contextmanager
def worker_lock():
    fd = os.open('/var/lib/quant-research', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        os.close(fd)


def checked(args, timeout=30):
    result = subprocess.run(args, capture_output=True, timeout=timeout)
    if result.returncode: raise RuntimeError('CONTROL_FAILED:' + Path(args[0]).name)
    return result.stdout


def fetch(url, limit=262144):
    request = urllib.request.Request(url, headers={'User-Agent': 'Quant-Trade-native-observer'})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read(limit + 1)
    if len(raw) > limit: raise ValueError('DOWNLOAD_SIZE_EXCEEDED')
    return raw


def atomic(path, data, mode=0o644, gid=0):
    path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    if path.is_symlink(): raise ValueError('ROOT_DESTINATION_SYMLINK')
    pending = path.with_name('.' + path.name + '.pending')
    fd = os.open(pending, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, 'wb') as stream:
        os.fchown(stream.fileno(), 0, gid); os.fchmod(stream.fileno(), mode)
        stream.write(data); stream.flush(); os.fsync(stream.fileno())
    pending.replace(path)


def parse_secret(raw):
    # The sealed payload contains only a newly generated 256-bit hex credential.
    value = raw.decode('ascii').strip()
    if not re.fullmatch('[a-f0-9]{64}', value): raise ValueError('SEALED_CREDENTIAL_FORMAT_INVALID')
    return value


def environment(existing, key):
    # Preserve unrelated settings without printing any existing value.
    lines = [s for s in existing.splitlines() if not re.match(r'^\s*QT_ORACLE_(INGRESS_KEY|PRINCIPAL|SITE_BASE_URL)=', s)]
    lines += ['QT_ORACLE_INGRESS_KEY=' + key, 'QT_ORACLE_PRINCIPAL=oracle-research-live',
              'QT_ORACLE_SITE_BASE_URL=' + SITE]
    return ('\n'.join(lines) + '\n').encode()


def override(release):
    return ('[Service]\nEnvironmentFile=/etc/quant-research/worker.env\nExecStart=\n'
            'ExecStart=/usr/bin/flock --nonblock --conflict-exit-code=0 /var/lib/quant-research '
            '/usr/bin/python3.12 -I -B ' + str(release / 'oracle_live_projection.py') +
            ' --core-release /opt/quant-research/releases/' + CORE_SHA +
            ' --config /etc/quant-research-v2/worker.json'
            ' --state-dir /var/lib/quant-research-v2/live-observer\n').encode()


def install(args):
    if os.geteuid() != 0: raise ValueError('ROOT_REQUIRED_FOR_SYSTEMD_AND_SECRET_FILE')
    if not re.fullmatch('[a-f0-9]{40}', args.sha) or not re.fullmatch('[a-f0-9]{64}', args.cipher_sha256):
        raise ValueError('EXACT_SOURCE_AND_SEALED_PAYLOAD_HASH_REQUIRED')
    for run_id, name in ((args.ci_run, 'Oracle V2 Core'), (args.sec_ci_run, 'SEC P0 pre-t0 gate')):
        run = json.loads(fetch('https://api.github.com/repos/fahimahmedb/Quant-Trade/actions/runs/' + str(run_id)))
        if (run.get('head_sha') != args.sha or run.get('head_branch') != 'builder/oracle-v2-core-20261020'
                or run.get('name') != name or run.get('status') != 'completed' or run.get('conclusion') != 'success'):
            raise ValueError('EXACT_OBSERVER_CI_REQUIRED')
    core = Path('/opt/quant-research/releases') / CORE_SHA
    import sys
    sys.path.insert(0, str(core))
    from deploy.oracle_v2_deploy import validate_config
    config = json.loads(Path('/etc/quant-research-v2/worker.json').read_text())
    if validate_config(config) != core or Path('/opt/quant-research-v2/current').resolve() != core:
        raise ValueError('QUALIFIED_SCIENTIFIC_CORE_CHANGED')
    if checked(['systemctl', 'is-enabled', TIMER]).strip() != b'enabled':
        raise ValueError('EXISTING_V2_TIMER_MUST_BE_ENABLED')
    health = json.loads(fetch('http://127.0.0.1:8080/health', 4096))
    if health.get('status') != 'ok': raise ValueError('LOCAL_MODEL_NOT_HEALTHY')
    worker, transport = pwd.getpwnam('quant-research'), pwd.getpwnam('ocarun')
    stage = Path(transport.pw_dir) / '.cache/quant-live-link'
    for path in (stage, stage / 'transport.pem', stage / 'sealed.bin'):
        mode = path.lstat()
        if path.is_symlink() or mode.st_uid != transport.pw_uid or stat.S_IMODE(mode.st_mode) & 0o077:
            raise ValueError('PRIVATE_VM_TRANSPORT_PERMISSIONS_REQUIRED')
    cipher = (stage / 'sealed.bin').read_bytes()
    if len(cipher) != 384 or hashlib.sha256(cipher).hexdigest() != args.cipher_sha256:
        raise ValueError('SEALED_PAYLOAD_HASH_MISMATCH')
    raw = checked(['openssl', 'pkeyutl', '-decrypt', '-inkey', str(stage / 'transport.pem'),
                   '-in', str(stage / 'sealed.bin'), '-pkeyopt', 'rsa_padding_mode:oaep',
                   '-pkeyopt', 'rsa_oaep_md:sha256'])
    key = parse_secret(raw)
    source = fetch('https://raw.githubusercontent.com/fahimahmedb/Quant-Trade/' + args.sha + '/deploy/oracle_live_projection.py')
    if hashlib.sha256(source).hexdigest() != PROJECTION_HASH: raise ValueError('OBSERVER_SOURCE_HASH_MISMATCH')
    compile(source, 'oracle_live_projection.py', 'exec')
    release = Path('/opt/quant-research/live-projections') / args.sha
    env = Path('/etc/quant-research/worker.env')
    if env.is_symlink(): raise ValueError('ENVIRONMENT_SYMLINK_REFUSED')
    if env.exists() and (env.stat().st_uid != 0 or stat.S_IMODE(env.stat().st_mode) & 0o007):
        raise ValueError('EXISTING_ENVIRONMENT_PERMISSIONS_UNSAFE')
    env_data = environment(env.read_text() if env.exists() else '', key)
    dropin = Path('/etc/systemd/system') / (SERVICE + '.d/50-native-live.conf')
    previous = dropin.read_bytes() if dropin.exists() else None
    checked(['systemctl', 'stop', TIMER])
    try:
        # Drain the existing bounded wake. Never kill a scientific stage to add UI.
        deadline = time.monotonic() + 500
        while checked(['systemctl', 'show', SERVICE, '--property=ActiveState', '--value']).strip() in (b'active', b'activating', b'deactivating'):
            if time.monotonic() >= deadline: raise ValueError('EXISTING_WAKE_STILL_RUNNING_RETRY_INSTALL_LATER')
            time.sleep(2)
        with worker_lock():
            atomic(release / 'oracle_live_projection.py', source)
            atomic(env, env_data, 0o640, worker.pw_gid)
            atomic(dropin, override(release))
            checked(['systemctl', 'daemon-reload'])
            checked(['systemd-analyze', 'verify', SERVICE])
            receipt = dict(status='NATIVE_SITE_OBSERVER_INSTALLED_LIVE_PROOF_PENDING', observer_sha=args.sha,
                           observer_sha256=PROJECTION_HASH, scientific_core_sha=CORE_SHA,
                           scientific_config_modified=False, secret_exported=False,
                           secret_file_mode='0640', principal='oracle-research-live',
                           worker_prefix='oracle-research.', site=SITE,
                           authority={k:config[k] for k in ('economic_experiment_authorized','prospective_observation_authorized','real_capital_authorized','live_trading_authorized')})
            atomic(Path('/etc/quant-research-v2/live-projection-receipt.json'), (json.dumps(receipt, sort_keys=True) + '\n').encode())
    except Exception:
        if previous is None:
            dropin.unlink(missing_ok=True)
        else: atomic(dropin, previous)
        checked(['systemctl', 'daemon-reload'])
        raise
    finally:
        checked(['systemctl', 'start', TIMER])
    checked(['systemctl', 'start', '--no-block', SERVICE])
    # Ciphertext and ephemeral transport key have no further use.
    (stage / 'transport.pem').unlink(); (stage / 'sealed.bin').unlink()
    print(json.dumps(receipt, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sha', required=True)
    parser.add_argument('--ci-run', required=True, type=int)
    parser.add_argument('--sec-ci-run', required=True, type=int)
    parser.add_argument('--cipher-sha256', required=True)
    install(parser.parse_args())


if __name__ == '__main__': main()
