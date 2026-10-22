"""Fresh GitHub snapshots and atomic multi-file commits on the canonical ref.

Git is the transport, not a second queue. CURRENT_BLOB_SHA checks guard tasks;
an exact ref lease guards the entire observed HEAD (including authority,
corpus, handoffs and queue refill). Every published commit is a direct child
of that HEAD; history is never rewritten and there is no blind retry.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import fcntl
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile
import tempfile
import time

from .worker_preflight import git_blob_sha, verify_materialized_legacy

PREFIX = 'research/research_os/'
SHA = re.compile(r'^[a-f0-9]{40}$')


class StateConflict(RuntimeError):
    pass


class StateUnavailable(RuntimeError):
    pass


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode()


@dataclass
class Snapshot:
    head: str
    root: Path
    blobs: dict

    @property
    def base(self):
        return self.root / 'research/research_os'

    def read(self, path):
        if path not in self.blobs:
            raise StateUnavailable('STATE_PATH_NOT_PRESENT:' + path)
        raw = (self.root / path).read_bytes()
        if git_blob_sha(raw) != self.blobs[path]:
            raise StateUnavailable('STATE_BLOB_MISMATCH:' + path)
        return json.loads(raw)

    def tasks(self):
        return [self.read(p) for p in sorted(self.blobs)
                if p.startswith(PREFIX + 'tasks/') and p.endswith('.json') and p.count('/') == 3]


class GitHubStateStore:
    def __init__(self, *, cache: Path, repository: str, branch: str):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
            raise ValueError('INVALID_REPOSITORY')
        self.cache, self.repository, self.branch = Path(cache), repository, branch
        self.ref = 'refs/heads/' + branch
        self.remote = 'https://github.com/' + repository + '.git'
        check = subprocess.run(['git', 'check-ref-format', self.ref], capture_output=True)
        if check.returncode or branch.startswith('-'):
            raise ValueError('INVALID_STATE_BRANCH')
        self.cache.mkdir(parents=True, exist_ok=True, mode=0o700)
        if not (self.cache / 'HEAD').exists():
            self._git('init', '--bare', str(self.cache), outside=True)

    def _git(self, *args, data=None, env=None, outside=False):
        cmd = ['git', '-c', 'maintenance.auto=false', '-c', 'gc.auto=0'] + ([] if outside else ['--git-dir=' + str(self.cache)]) + list(args)
        try:
            result = subprocess.run(cmd, input=data, capture_output=True, timeout=90,
                                    env=dict(os.environ, GIT_TERMINAL_PROMPT='0', **(env or {})))
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise StateUnavailable('GIT_TRANSPORT_' + type(exc).__name__) from None
        if result.returncode:
            # Do not emit credential-bearing URLs, headers or helper output.
            if args and args[0] == 'push':
                raise StateConflict('GITHUB_HEAD_CHANGED_OR_PUSH_REJECTED')
            raise StateUnavailable('GIT_OPERATION_FAILED:' + (args[0] if args else 'unknown'))
        return result.stdout

    @contextmanager
    def _locked(self):
        # Cache directory is private to the service user, never a disposable lock.
        fd = os.open(self.cache, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            os.close(fd)

    @contextmanager
    def snapshot(self):
        with self._locked():
            if shutil.disk_usage(self.cache).free < 256 * 1024 ** 2:
                raise StateUnavailable('GIT_CACHE_DISK_HEADROOM_BELOW_256_MIB')
            self._git('fetch', '--no-tags', self.remote, self.ref)
            head = self._git('rev-parse', 'FETCH_HEAD').decode().strip()
            if not SHA.fullmatch(head):
                raise StateUnavailable('INVALID_REMOTE_HEAD')
            self._git('update-ref', 'refs/quant/observed', head)
            entries = self._git('ls-tree', '-rz', head, '--', PREFIX).split(b'\0')
            blobs = {}
            for entry in filter(None, entries):
                info, name = entry.split(b'\t', 1)
                mode, kind, sha = info.decode().split()
                if kind != 'blob' or mode not in ('100644', '100755'):
                    raise StateUnavailable('NON_REGULAR_STATE_FILE')
                blobs[name.decode()] = sha
            archive = self._git('archive', head, PREFIX)
        with tempfile.TemporaryDirectory(prefix='quant-fresh-') as tmp:
            root = Path(tmp)
            with tarfile.open(fileobj=io.BytesIO(archive), mode='r:') as tar:
                for member in tar.getmembers():
                    parts = PurePosixPath(member.name).parts
                    if member.name.startswith('/') or '..' in parts or not (member.isfile() or member.isdir()):
                        raise StateUnavailable('UNSAFE_STATE_ARCHIVE')
                tar.extractall(root, filter='data')
            snapshot = Snapshot(head, root, blobs)
            manifest = snapshot.read(PREFIX + 'legacy/source_manifest.json')
            commit, path = manifest.get('source_commit', ''), manifest.get('ledger_path', '')
            if not SHA.fullmatch(commit) or not path or path.startswith('/') or '..' in PurePosixPath(path).parts:
                raise StateUnavailable('INVALID_PINNED_LEGACY_SOURCE')
            with self._locked():
                # Always request the exact fresh manifest pin, never a mutable ref.
                self._git('fetch', '--no-tags', self.remote, commit)
                ledger = self._git('show', commit + ':' + path)
            (snapshot.base / 'legacy/LEGACY_RESEARCH_LEDGER.imported.json').write_bytes(ledger)
            verify_materialized_legacy(snapshot.base)
            yield snapshot

    def commit(self, snapshot, writes, *, expected_blobs=None, create_only=(), message):
        if not writes:
            raise ValueError('EMPTY_STATE_TRANSACTION')
        for path, blob in (expected_blobs or {}).items():
            if snapshot.blobs.get(path) != blob:
                raise StateConflict('TASK_CURRENT_BLOB_SHA_MISMATCH')
        for path in create_only:
            if path in snapshot.blobs:
                raise StateConflict('IMMUTABLE_ARTIFACT_ALREADY_EXISTS:' + path)
        allowed = ('tasks/', 'events/', 'receipts/', 'artifacts/', 'hypotheses/', 'assessments/', 'runtime/worker_wakes/')
        for path in writes:
            tail = path.removeprefix(PREFIX)
            if (not path.startswith(PREFIX) or not tail.startswith(allowed)
                    or PurePosixPath(path).as_posix() != path or '..' in PurePosixPath(path).parts
                    or '\n' in path or '\t' in path):
                raise ValueError('STATE_WRITE_OUTSIDE_CANONICAL_WORKER_PATHS')
        with self._locked(), tempfile.TemporaryDirectory(prefix='quant-index-') as tmp:
            env = {'GIT_INDEX_FILE': str(Path(tmp) / 'index'),
                   'GIT_AUTHOR_NAME': 'Quant Research OS', 'GIT_AUTHOR_EMAIL': 'research-os@localhost',
                   'GIT_COMMITTER_NAME': 'Quant Research OS', 'GIT_COMMITTER_EMAIL': 'research-os@localhost'}
            self._git('read-tree', snapshot.head, env=env)
            rows = []
            for path, value in sorted(writes.items()):
                sha = self._git('hash-object', '-w', '--stdin', data=json_bytes(value)).decode().strip()
                rows.append(f'100644 {sha}\t{path}\n')
            self._git('update-index', '--index-info', data=''.join(rows).encode(), env=env)
            tree = self._git('write-tree', env=env).decode().strip()
            # Durable runtime DATA must not launch full hosted build workflows
            # at every ten-minute wake. Executable release commits still run CI.
            commit = self._git('commit-tree', tree, '-p', snapshot.head,
                               data=(message + ' [skip ci]\n').encode(), env=env).decode().strip()
            # commit-tree above proves this is a direct child of snapshot.head.
            # The explicit ref lease is compare-and-swap, including if an owner
            # rewound the ref. It never authorizes replacing another HEAD.
            # Lost responses recover from durable state on the next wake.
            self._git('push', '--porcelain', '--force-with-lease=' + self.ref + ':' + snapshot.head,
                      self.remote, commit + ':' + self.ref)
            self._git('update-ref', 'refs/quant/observed', commit)
            return commit

    def compact_if_due(self):
        """Bound local object accumulation; local timestamps grant no task authority."""
        marker = self.cache / 'last-worker-gc'
        with self._locked():
            if marker.exists() and time.time() - marker.stat().st_mtime < 86400:
                return
            if (self.cache / 'refs/quant/observed').exists():
                # Explicit gc is foreground without --auto. Ubuntu 24.04's
                # Git 2.43 does not yet accept the newer --no-detach option.
                self._git('gc', '--prune=2.weeks.ago')
            marker.touch()
