"""CP039 rebuilt: real process death around immutable publication, then reboot of writer."""
import json
import subprocess
import sys
import time

import pytest

from research.research_os.expansion.persistent_state import read_immutable_json, write_immutable_json


# The child dies without Python finally blocks. This is process-death evidence,
# not a simulation of physical power loss or a promise of orphan reclamation.
CHILD = r'''
import json, os, stat, sys
from pathlib import Path
from research.research_os.expansion.persistent_state import write_immutable_json
path, stage, payload = Path(sys.argv[1]), sys.argv[2], json.loads(sys.argv[3])
fsync, link, unlink = os.fsync, os.link, os.unlink

def die(point):
    if stage == point:
        os._exit(73)

def sync(fd):
    kind = 'directory' if stat.S_ISDIR(os.fstat(fd).st_mode) else 'staging'
    die('before_' + kind + '_fsync')
    fsync(fd)
    die('after_' + kind + '_fsync')

def publish(src, dst):
    die('before_link')
    link(src, dst)
    die('after_link')

def cleanup(src):
    die('before_unlink')
    unlink(src)
    die('after_unlink')

os.fsync, os.link, os.unlink = sync, publish, cleanup
try:
    write_immutable_json(path, payload)
except ValueError as exc:
    print(json.dumps({'status': 'CONFLICT', 'reason': str(exc)}), flush=True)
    sys.exit(3)
print(json.dumps({'status': 'ACKNOWLEDGED'}), flush=True)
'''

RACER = r'''
import json, sys, time
from pathlib import Path
from research.research_os.expansion.persistent_state import write_immutable_json
path, ready, release = map(Path, sys.argv[1:4])
payload = json.loads(sys.argv[4])
ready.write_text('ready')
limit = time.monotonic() + 10
while not release.exists():
    if time.monotonic() >= limit:
        raise RuntimeError('test release not delivered')
    time.sleep(.005)
try:
    write_immutable_json(path, payload)
    print('ACKNOWLEDGED', flush=True)
except ValueError:
    print('CONFLICT', flush=True)
'''


def child(path, stage, payload):
    return subprocess.run([sys.executable, '-c', CHILD, str(path), stage, json.dumps(payload)],
                          text=True, capture_output=True, timeout=15)


def assert_only_complete_destination(path, payload):
    assert read_immutable_json(path) == payload
    record = json.loads(path.read_text())
    assert set(record) == {'payload_hash', 'payload'}


@pytest.mark.parametrize('point,published', [
    ('before_staging_fsync', False), ('after_staging_fsync', False),
    ('before_link', False), ('after_link', True),
    ('before_directory_fsync', True), ('after_directory_fsync', True),
    ('before_unlink', True), ('after_unlink', True),
])
def test_real_process_death_never_exposes_partial_destination_and_retry_has_one_identity(tmp_path, point, published):
    path = tmp_path / 'trial.checkpoint.json'
    payload = {'trial': 'SYNTHETIC-CRASH', 'attempts': 0, 'authority': False,
               'body': {'scope': ['a', 'b'], 'declared': 'no economic results'}}
    dead = child(path, point, payload)
    assert dead.returncode == 73, (dead.returncode, dead.stderr)
    assert dead.stdout == ''  # no fabricated acknowledgement from the dead writer
    assert path.exists() is published
    before = path.read_bytes() if published else None
    inode = path.stat().st_ino if published else None
    if published:
        assert_only_complete_destination(path, payload)
    for _ in range(3):
        retry = child(path, 'no_crash', payload)
        assert retry.returncode == 0, retry.stderr
        assert json.loads(retry.stdout)['status'] == 'ACKNOWLEDGED'
        assert_only_complete_destination(path, payload)
        if before is None:
            before, inode = path.read_bytes(), path.stat().st_ino
        assert path.read_bytes() == before
        assert path.stat().st_ino == inode
    # Abrupt exit may leave a staging hardlink. It is not another destination or
    # a successful receipt and is deliberately not silently garbage-collected here.
    assert [p.name for p in tmp_path.iterdir() if not p.name.startswith('.immutable-')] == [path.name]


@pytest.mark.parametrize('point', ['before_link', 'after_link', 'after_directory_fsync'])
def test_after_lost_ack_a_conflicting_fresh_writer_cannot_overwrite_published_truth(tmp_path, point):
    path = tmp_path / 'checkpoint.json'
    original, conflict = {'x': True}, {'x': 1}
    dead = child(path, point, original)
    assert dead.returncode == 73
    published = point != 'before_link'
    competitor = child(path, 'no_crash', conflict)
    assert competitor.returncode == (3 if published else 0), competitor.stderr
    winner = original if published else conflict
    assert_only_complete_destination(path, winner)
    denied = child(path, 'no_crash', conflict if published else original)
    assert denied.returncode == 3
    assert_only_complete_destination(path, winner)


@pytest.mark.parametrize('second', [{'x': True}, {'x': 1}, {'x': 1.0}])
def test_independent_process_publishers_have_one_typed_winner_and_no_partial_read(tmp_path, second):
    path = tmp_path / 'checkpoint.json'
    release = tmp_path / 'release'
    procs = []
    try:
        for i, payload in enumerate([{'x': True}, second]):
            ready = tmp_path / f'ready-{i}'
            procs.append(subprocess.Popen([sys.executable, '-c', RACER, str(path), str(ready),
                                           str(release), json.dumps(payload)],
                                          text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
        limit = time.monotonic() + 10
        while not all((tmp_path / f'ready-{i}').exists() for i in range(2)):
            assert time.monotonic() < limit
            assert all(p.poll() is None for p in procs)
            time.sleep(.005)
        release.write_text('go')
        outputs = []
        for proc in procs:
            out, err = proc.communicate(timeout=15)
            assert proc.returncode == 0, err
            outputs.append(out.strip())
        assert outputs.count('ACKNOWLEDGED') == (2 if type(second['x']) is bool else 1)
        winner = read_immutable_json(path)
        assert json.dumps(winner, sort_keys=True) in [json.dumps({'x': True}, sort_keys=True), json.dumps(second, sort_keys=True)]
        before = path.read_bytes()
        for value in ({'x': True}, second):
            retry = child(path, 'no_crash', value)
            assert retry.returncode == (0 if json.dumps(value, sort_keys=True) == json.dumps(winner, sort_keys=True) else 3)
            assert path.read_bytes() == before
    finally:
        for proc in procs:
            if proc.poll() is None:
                proc.kill()
                proc.communicate(timeout=5)


@pytest.mark.parametrize('damage', ['torn_envelope', 'payload_edit', 'rehashed_foreign_payload'])
def test_restarted_writer_does_not_repair_or_reinterpret_damaged_durable_proof(tmp_path, damage):
    path = tmp_path / 'checkpoint.json'
    original = {'trial': 'original', 'authority': False}
    write_immutable_json(path, original)
    if damage == 'torn_envelope':
        path.write_bytes(path.read_bytes()[:-9])
    else:
        record = json.loads(path.read_text())
        record['payload']['trial'] = 'foreign'
        if damage == 'rehashed_foreign_payload':
            from research.research_os.scientific_store import sha256_json
            record['payload_hash'] = sha256_json(record['payload'])
        path.write_text(json.dumps(record))
    corrupted = path.read_bytes()
    result = child(path, 'no_crash', original)
    assert result.returncode == 3, result.stderr
    assert json.loads(result.stdout)['status'] == 'CONFLICT'
    assert path.read_bytes() == corrupted
