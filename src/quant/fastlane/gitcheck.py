"""Git anchoring for fast-lane commitments (seal, holdout request, vendor manifests).

A file under ``var/`` or an uncommitted file can be deleted and rewritten, so
it cannot prove "sealed before the look". A commitment is accepted only if:

(a) ``git log --diff-filter=A`` finds exactly one commit C that added it
    (and, for write-once files, C is the only commit that ever touched it);
(b) C is an ancestor of HEAD;
(c) C is contained in at least one remote-tracking branch (it was published);
(d) ``git show C:<path>`` equals the bytes on disk.

Only read-only git commands are run.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


class GitCheckFailed(PermissionError):
    pass


@dataclass(frozen=True)
class CommittedFile:
    path: str
    commit: str


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                              timeout=60, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        raise GitCheckFailed(f"git unavailable: {exc}") from exc


def _out(root: Path, *args: str) -> str:
    proc = _git(root, *args)
    if proc.returncode != 0:
        raise GitCheckFailed(f"git {' '.join(args)} failed: "
                             f"{proc.stderr.decode('utf-8', 'replace').strip()}")
    return proc.stdout.decode("utf-8", "replace")


def verify_committed(repo_root: Path, path: Path, *, write_once: bool = True) -> CommittedFile:
    """Raise GitCheckFailed unless ``path`` satisfies checks (a)-(d)."""
    root = Path(repo_root).resolve()
    target = Path(path).resolve()
    toplevel = Path(_out(root, "rev-parse", "--show-toplevel").strip()).resolve()
    if toplevel != root:
        raise GitCheckFailed(f"{root} is not the top of a git work tree (top is {toplevel})")
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
    remotes = _out(root, "branch", "-r", "--contains", commit).split()
    if not remotes:
        raise GitCheckFailed(f"(c) commit {commit[:12]} adding {rel} is on no remote-tracking "
                             "branch (not published)")
    committed = _git(root, "show", f"{commit}:{rel}")
    if committed.returncode != 0:
        raise GitCheckFailed(f"(d) git show {commit[:12]}:{rel} failed")
    if committed.stdout != target.read_bytes():
        raise GitCheckFailed(f"(d) on-disk {rel} differs from its committed bytes")
    return CommittedFile(rel, commit)
