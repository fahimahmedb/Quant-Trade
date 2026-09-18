"""Collector identity recorded on every attempt and envelope.

The mission requires "collector version / git commit" on each attempt record so
a later reviewer can tell which code produced a capture. The commit is read from
the repository rather than shelled out for, so it works in a test sandbox.
"""

from __future__ import annotations

from pathlib import Path


COLLECTOR_NAME = "sec-form4-p0-raw-capture"
COLLECTOR_VERSION = f"{COLLECTOR_NAME}/1"


def git_commit(root: Path) -> str:
    """Resolve HEAD without a subprocess. ``unknown`` when there is no repo."""
    git_dir = Path(root) / ".git"
    if git_dir.is_file():  # a worktree: .git is a pointer file
        try:
            pointer = git_dir.read_text(encoding="utf-8").strip()
        except OSError:
            return "unknown"
        if pointer.startswith("gitdir:"):
            git_dir = Path(pointer.split(":", 1)[1].strip())
    head = git_dir / "HEAD"
    if not head.exists():
        return "unknown"
    try:
        content = head.read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"
    if not content.startswith("ref:"):
        return content
    ref = content.split(":", 1)[1].strip()
    direct = git_dir / ref
    if direct.exists():
        try:
            return direct.read_text(encoding="utf-8").strip()
        except OSError:
            return "unknown"
    packed = git_dir / "packed-refs"
    if packed.exists():
        try:
            for line in packed.read_text(encoding="utf-8").splitlines():
                if line.startswith("#") or " " not in line:
                    continue
                sha, name = line.split(" ", 1)
                if name.strip() == ref:
                    return sha.strip()
        except OSError:
            return "unknown"
    return "unknown"
