"""Git anchoring for fast-lane commitments (seal, holdout request, vendor manifests).

A file under ``var/`` or an uncommitted file can be deleted and rewritten, so
it cannot prove "sealed before the look". A commitment is accepted only if:

(0) the clone is complete (``git rev-parse --is-shallow-repository`` is false;
    a shallow clone can hide an earlier commit that added the same path);
(a) ``git log --diff-filter=A`` finds exactly one commit C that added it
    (and, for write-once files, C is the only commit that ever touched it);
(b) C is an ancestor of HEAD;
(c) C is an ancestor of a branch tip that the real remote advertises
    (``git ls-remote --heads <remote>``); tips missing locally are fetched first.
    Local refs under ``refs/remotes/`` never count;
(d) ``git show C:<path>`` equals the bytes on disk.

Residual risk: a force-push (or branch deletion) on the remote can rewrite
history so that a different commit satisfies (a)-(d). Code cannot prevent
that; the protocol therefore requires branch protection (no force-push, no
deletion) and an external record of the seal and request commit hashes, and
the holdout request pins the seal commit so that rewriting the seal commit is
detected at the next grant.
"""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

DEFAULT_REMOTE = "origin"
_TIPS_CACHE: dict[tuple[str, str], tuple[float, tuple[tuple[str, str], ...]]] = {}


class GitCheckFailed(PermissionError):
    pass


@dataclass(frozen=True)
class CommittedFile:
    path: str
    commit: str
    remote_tip: str


def _git(root: Path, *args: str, timeout: float = 120) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                              timeout=timeout, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        raise GitCheckFailed(f"git unavailable: {exc}") from exc


def _out(root: Path, *args: str) -> str:
    proc = _git(root, *args)
    if proc.returncode != 0:
        raise GitCheckFailed(f"git {' '.join(args)} failed: "
                             f"{proc.stderr.decode('utf-8', 'replace').strip()}")
    return proc.stdout.decode("utf-8", "replace")


def assert_complete_clone(root: Path) -> None:
    if _out(root, "rev-parse", "--is-shallow-repository").strip() == "true":
        raise GitCheckFailed("(0) this clone is shallow, so an earlier commit touching the "
                             "path could be hidden; run `git fetch --unshallow` and retry")


def remote_tips(root: Path, remote: str = DEFAULT_REMOTE, *,
                max_age_s: float = 0.0) -> tuple[tuple[str, str], ...]:
    """(sha, ref) of every branch the real remote advertises (optionally cached)."""
    key = (str(Path(root).resolve()), remote)
    cached = _TIPS_CACHE.get(key)
    if max_age_s > 0 and cached and time.monotonic() - cached[0] <= max_age_s:
        return cached[1]
    lines = _out(root, "ls-remote", "--heads", remote).splitlines()
    tips = tuple((parts[0], parts[1]) for parts in (l.split() for l in lines) if len(parts) == 2)
    if not tips:
        raise GitCheckFailed(f"(c) remote {remote!r} advertises no branch")
    _TIPS_CACHE[key] = (time.monotonic(), tips)
    return tips


def _ensure_local(root: Path, remote: str, sha: str, ref: str) -> bool:
    if _git(root, "cat-file", "-e", f"{sha}^{{commit}}").returncode == 0:
        return True
    _git(root, "fetch", "--no-tags", "--quiet", remote, ref)
    return _git(root, "cat-file", "-e", f"{sha}^{{commit}}").returncode == 0


def published_tip(root: Path, commit: str, remote: str = DEFAULT_REMOTE, *,
                  max_age_s: float = 0.0) -> str:
    """Return an advertised remote tip that contains ``commit``, else raise."""
    for sha, ref in remote_tips(root, remote, max_age_s=max_age_s):
        if not _ensure_local(root, remote, sha, ref):
            continue
        if _git(root, "merge-base", "--is-ancestor", commit, sha).returncode == 0:
            return sha
    raise GitCheckFailed(f"(c) commit {commit[:12]} is not contained in any branch the remote "
                         f"{remote!r} advertises (not published, or history was rewritten)")


def verify_committed(repo_root: Path, path: Path, *, write_once: bool = True,
                     remote: str = DEFAULT_REMOTE, max_age_s: float = 0.0) -> CommittedFile:
    """Raise GitCheckFailed unless ``path`` satisfies checks (0) and (a)-(d)."""
    root = Path(repo_root).resolve()
    target = Path(path).resolve()
    toplevel = Path(_out(root, "rev-parse", "--show-toplevel").strip()).resolve()
    if toplevel != root:
        raise GitCheckFailed(f"{root} is not the top of a git work tree (top is {toplevel})")
    assert_complete_clone(root)
    try:
        rel = target.relative_to(root).as_posix()
    except ValueError as exc:
        raise GitCheckFailed(f"{target} is outside the repository") from exc
    if not target.is_file():
        raise GitCheckFailed(f"{rel} does not exist")
    adds = _out(root, "log", "--full-history", "--no-renames", "--diff-filter=A",
                "--format=%H", "--", rel).split()
    if len(adds) != 1:
        raise GitCheckFailed(f"(a) {rel} must be added by exactly one commit, found {len(adds)}")
    commit = adds[0]
    if write_once:
        touches = _out(root, "log", "--full-history", "--no-renames", "--format=%H",
                       "--", rel).split()
        if touches != [commit]:
            raise GitCheckFailed(f"(a) {rel} is write-once but {len(touches)} commits touch it")
    if _git(root, "merge-base", "--is-ancestor", commit, "HEAD").returncode != 0:
        raise GitCheckFailed(f"(b) commit {commit[:12]} adding {rel} is not an ancestor of HEAD")
    tip = published_tip(root, commit, remote, max_age_s=max_age_s)
    committed = _git(root, "show", f"{commit}:{rel}")
    if committed.returncode != 0:
        raise GitCheckFailed(f"(d) git show {commit[:12]}:{rel} failed")
    if committed.stdout != target.read_bytes():
        raise GitCheckFailed(f"(d) on-disk {rel} differs from its committed bytes")
    return CommittedFile(rel, commit, tip)
