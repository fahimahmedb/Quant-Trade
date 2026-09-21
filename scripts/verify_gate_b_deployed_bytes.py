#!/usr/bin/env python3
"""Index-independent verifier for a frozen Gate-B deployed Git tree.

The verifier treats Git object authority and worktree bytes as separate trust
surfaces.  It rejects metadata/object-store indirection, disables replacement
objects for every authoritative Git read, traverses the deployed tree through
directory file descriptors with no-follow semantics, and emits canonical JSON
plus a SHA-256 digest.

Repository code can harden inspection-time races, but it cannot prove that the
release stays immutable after verification.  That residual boundary remains a
target-host activation/mount property.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
from typing import Any, Iterable

REPORT_SCHEMA = "quant-gate-b-deployed-byte-verification/v2"
DEFAULT_CRITICAL_PREFIXES = ("src", "deploy", "scripts")
HEX40 = set("0123456789abcdef")
TARGET_HOST_ONLY_IMMUTABILITY = (
    "TARGET_HOST_ONLY: immutability of the frozen release for the "
    "verification-to-first-mutation authority window"
)
REJECTED_GIT_ENV = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_COMMON_DIR",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_REPLACE_REF_BASE",
    "GIT_GRAFT_FILE",
    "GIT_NAMESPACE",
    "GIT_QUARANTINE_PATH",
)


class VerifyError(RuntimeError):
    pass


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha256_digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _validate_platform_primitives() -> None:
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise VerifyError("platform lacks required O_NOFOLLOW/O_DIRECTORY primitives")
    if os.open not in getattr(os, "supports_dir_fd", set()):
        raise VerifyError("platform os.open lacks dir_fd support")
    if os.stat not in getattr(os, "supports_dir_fd", set()):
        raise VerifyError("platform os.stat lacks dir_fd support")
    if os.readlink not in getattr(os, "supports_dir_fd", set()):
        raise VerifyError("platform os.readlink lacks dir_fd support")
    if os.listdir not in getattr(os, "supports_fd", set()):
        raise VerifyError("platform os.listdir lacks fd support")


def _reject_git_environment_overrides() -> None:
    present = [name for name in REJECTED_GIT_ENV if os.environ.get(name)]
    if present:
        raise VerifyError("Git authority override environment is present: " + ",".join(sorted(present)))


def _git_env() -> dict[str, str]:
    _reject_git_environment_overrides()
    env = os.environ.copy()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    env["GIT_NO_LAZY_FETCH"] = "1"
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env


def git(repo: Path, *args: str) -> bytes:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=_git_env(),
        check=False,
    )
    if proc.returncode != 0:
        raise VerifyError(f"git {' '.join(args)} failed: {proc.stderr.decode('utf-8', 'replace').strip()}")
    return proc.stdout


def validate_hex40(value: str, field: str) -> None:
    if len(value) != 40 or any(c not in HEX40 for c in value):
        raise VerifyError(f"{field} must be 40 lowercase hex characters")


def git_blob_oid(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def normalize_prefix(value: str) -> str:
    if value != value.strip():
        raise VerifyError(f"invalid path prefix: {value!r}")
    if not value or value == "." or value.startswith("/") or value.endswith("/"):
        raise VerifyError(f"invalid path prefix: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise VerifyError(f"invalid path prefix: {value!r}")
    normalized = path.as_posix()
    if normalized != value:
        raise VerifyError(f"invalid path prefix: {value!r}")
    return value


def under_prefix(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(prefix + "/")


def _stat_identity(st: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (st.st_dev, st.st_ino, st.st_mode, st.st_size, st.st_mtime_ns, st.st_ctime_ns)


def _same_object(a: os.stat_result, b: os.stat_result) -> bool:
    return (a.st_dev, a.st_ino, stat.S_IFMT(a.st_mode)) == (b.st_dev, b.st_ino, stat.S_IFMT(b.st_mode))


def _open_dir_nofollow(name: str | os.PathLike[str], *, dir_fd: int | None = None) -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    flags |= getattr(os, "O_CLOEXEC", 0)
    try:
        return os.open(name, flags, dir_fd=dir_fd)
    except OSError as exc:
        raise VerifyError(f"failed no-follow directory open for {name!r}: {exc}") from exc


def _read_fd_all(fd: int) -> bytes:
    chunks: list[bytes] = []
    while True:
        chunk = os.read(fd, 1024 * 1024)
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks)


def _read_regular_path_nofollow(path: Path) -> tuple[bytes, os.stat_result]:
    flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise VerifyError(f"failed no-follow file open for {path}: {exc}") from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise VerifyError(f"expected regular file at {path}")
        data = _read_fd_all(fd)
        after = os.fstat(fd)
        if _stat_identity(before) != _stat_identity(after):
            raise VerifyError(f"file changed while being read: {path}")
        return data, after
    finally:
        os.close(fd)


def _lexical_abs(base: Path, value: str) -> Path:
    if os.path.isabs(value):
        return Path(os.path.abspath(value))
    return Path(os.path.abspath(os.path.join(str(base), value)))


def _reject_symlink(path: Path, label: str, *, allow_missing: bool = False) -> os.stat_result | None:
    try:
        st = path.lstat()
    except FileNotFoundError:
        if allow_missing:
            return None
        raise VerifyError(f"missing required {label}: {path}")
    if stat.S_ISLNK(st.st_mode):
        raise VerifyError(f"{label} must not be a symlink: {path}")
    return st


def _scan_tree_for_symlinks(root: Path, label: str) -> None:
    for dirpath, dirs, files in os.walk(root, topdown=True, followlinks=False):
        base = Path(dirpath)
        for name in list(dirs):
            p = base / name
            if p.is_symlink():
                raise VerifyError(f"{label} contains symlink indirection: {p}")
        for name in files:
            p = base / name
            if p.is_symlink():
                raise VerifyError(f"{label} contains symlink indirection: {p}")


def ensure_git_independence(repo: Path) -> dict[str, Any]:
    _reject_git_environment_overrides()
    dotgit = repo / ".git"
    dotgit_st = _reject_symlink(dotgit, ".git")
    assert dotgit_st is not None
    if not stat.S_ISDIR(dotgit_st.st_mode):
        if stat.S_ISREG(dotgit_st.st_mode):
            raise VerifyError("linked worktree dependency detected (.git is a file)")
        raise VerifyError("release does not contain an independent .git directory")

    commondir = dotgit / "commondir"
    if commondir.exists() or commondir.is_symlink():
        raise VerifyError("Git common-dir indirection metadata is not allowed")

    objects = dotgit / "objects"
    objects_st = _reject_symlink(objects, ".git/objects")
    assert objects_st is not None
    if not stat.S_ISDIR(objects_st.st_mode):
        raise VerifyError(".git/objects must be a real local directory")

    _scan_tree_for_symlinks(objects, "Git object store")

    for rel in ("HEAD", "refs", "packed-refs", "config"):
        p = dotgit / rel
        st = _reject_symlink(p, f".git/{rel}", allow_missing=True)
        if st is not None and rel == "refs" and not stat.S_ISDIR(st.st_mode):
            raise VerifyError(".git/refs must be a directory when present")
    refs_dir = dotgit / "refs"
    if refs_dir.is_dir():
        _scan_tree_for_symlinks(refs_dir, "Git refs")

    expected_git_dir = Path(os.path.abspath(dotgit))
    git_dir_raw = git(repo, "rev-parse", "--absolute-git-dir").decode().strip()
    common_dir_raw = git(repo, "rev-parse", "--git-common-dir").decode().strip()
    object_dir_raw = git(repo, "rev-parse", "--git-path", "objects").decode().strip()
    git_dir = _lexical_abs(repo, git_dir_raw)
    common_dir = _lexical_abs(repo, common_dir_raw)
    object_dir = _lexical_abs(repo, object_dir_raw)

    if git_dir != expected_git_dir:
        raise VerifyError("absolute Git directory is not release-local")
    if common_dir != expected_git_dir:
        raise VerifyError("foreign/common Git metadata dependency detected")
    expected_object_dir = Path(os.path.abspath(objects))
    if object_dir != expected_object_dir:
        raise VerifyError("Git object directory is not release-local")

    alternates = objects / "info" / "alternates"
    if alternates.exists() or alternates.is_symlink():
        raise VerifyError("Git alternates metadata must be absent")

    grafts = dotgit / "info" / "grafts"
    if grafts.exists() or grafts.is_symlink():
        raise VerifyError("legacy Git graft replacement metadata must be absent")

    replace_dir = dotgit / "refs" / "replace"
    if replace_dir.is_symlink():
        raise VerifyError("Git replace-ref directory must not be a symlink")
    replace_refs = [
        line.decode("utf-8", "replace")
        for line in git(repo, "for-each-ref", "--format=%(refname)", "refs/replace/").splitlines()
        if line
    ]
    if replace_refs:
        raise VerifyError("Git replace refs are present: " + ",".join(replace_refs))

    return {
        "git_dir": str(git_dir),
        "common_dir": str(common_dir),
        "object_directory": str(object_dir),
        "object_store_locality_proven": True,
        "object_store_symlink_scan": "recursive_lstat_no_follow",
        "alternates_absent": True,
        "replace_refs_absent": True,
        "replacement_objects_disabled": True,
        "replacement_object_semantics_disabled": True,
        "legacy_grafts_absent": True,
        "rejected_git_authority_environment": list(REJECTED_GIT_ENV),
    }


def _snapshot_lock_paths(dotgit: Path) -> list[str]:
    paths: list[str] = []
    for root, dirs, files in os.walk(dotgit, topdown=True, followlinks=False):
        base = Path(root)
        dirs[:] = [d for d in dirs if not (base / d).is_symlink()]
        for name in files:
            if name.endswith(".lock"):
                paths.append((base / name).relative_to(dotgit).as_posix())
        for name in dirs:
            if name.endswith(".lock"):
                paths.append((base / name).relative_to(dotgit).as_posix())
    return sorted(set(paths))


def git_write_snapshot(repo: Path) -> dict[str, Any]:
    dotgit = repo / ".git"
    index = dotgit / "index"
    index_info = None
    try:
        st = index.lstat()
    except FileNotFoundError:
        st = None
    if st is not None:
        if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
            raise VerifyError(".git/index must be a regular non-symlink file when present")
        data, stable = _read_regular_path_nofollow(index)
        index_info = {
            "device": stable.st_dev,
            "inode": stable.st_ino,
            "size": stable.st_size,
            "mtime_ns": stable.st_mtime_ns,
            "ctime_ns": stable.st_ctime_ns,
            "sha256": sha256_digest(data),
        }
    return {"index": index_info, "lock_paths": _snapshot_lock_paths(dotgit)}


def _validate_tree_path(path: str) -> tuple[str, ...]:
    pp = PurePosixPath(path)
    if pp.is_absolute() or not pp.parts or any(part in {"", ".", ".."} for part in pp.parts):
        raise VerifyError(f"unsafe path in expected Git tree: {path!r}")
    if pp.as_posix() != path:
        raise VerifyError(f"non-canonical path in expected Git tree: {path!r}")
    return pp.parts


def expected_entries(repo: Path, expected_tree: str) -> dict[str, dict[str, str]]:
    raw = git(repo, "ls-tree", "-r", "-z", "--full-tree", expected_tree)
    entries: dict[str, dict[str, str]] = {}
    fsenc = sys.getfilesystemencoding()
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            meta, path_bytes = record.split(b"\t", 1)
            mode_b, type_b, oid_b = meta.split(b" ", 2)
            path = path_bytes.decode(fsenc, "surrogateescape")
            mode = mode_b.decode("ascii")
            typ = type_b.decode("ascii")
            oid = oid_b.decode("ascii")
        except Exception as exc:
            raise VerifyError("malformed git ls-tree output") from exc
        _validate_tree_path(path)
        if path in entries:
            raise VerifyError(f"duplicate tree path: {path}")
        if typ != "blob":
            raise VerifyError(f"unsupported tracked object type {typ} at {path}")
        if mode not in {"100644", "100755", "120000"}:
            raise VerifyError(f"unsupported tracked mode {mode} at {path}")
        validate_hex40(oid, f"tree oid for {path}")
        entries[path] = {"mode": mode, "oid": oid}
    return entries


def _open_parent_chain(root_fd: int, parts: tuple[str, ...]) -> tuple[int, list[tuple[int, str, int, os.stat_result]]]:
    current_fd = root_fd
    chain: list[tuple[int, str, int, os.stat_result]] = []
    for component in parts[:-1]:
        child_fd = _open_dir_nofollow(component, dir_fd=current_fd)
        child_st = os.fstat(child_fd)
        if not stat.S_ISDIR(child_st.st_mode):
            os.close(child_fd)
            raise VerifyError(f"tracked parent component is not a directory: {component!r}")
        chain.append((current_fd, component, child_fd, child_st))
        current_fd = child_fd
    return current_fd, chain


def _recheck_parent_chain(chain: Iterable[tuple[int, str, int, os.stat_result]]) -> None:
    for parent_fd, component, child_fd, opened_st in reversed(list(chain)):
        try:
            current = os.stat(component, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError as exc:
            raise VerifyError(f"tracked parent path changed during verification: {component!r}") from exc
        child_now = os.fstat(child_fd)
        if not _same_object(opened_st, child_now) or not _same_object(opened_st, current):
            raise VerifyError(f"tracked parent path identity changed during verification: {component!r}")


def _close_parent_chain(chain: Iterable[tuple[int, str, int, os.stat_result]]) -> None:
    for _, _, child_fd, _ in reversed(list(chain)):
        try:
            os.close(child_fd)
        except OSError:
            pass


def _read_tracked_entry(root_fd: int, path: str, expected_mode: str) -> tuple[bytes, os.stat_result]:
    parts = _validate_tree_path(path)
    parent_fd, chain = _open_parent_chain(root_fd, parts)
    name = parts[-1]
    try:
        try:
            before_path = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            raise

        if expected_mode == "120000":
            if not stat.S_ISLNK(before_path.st_mode):
                raise VerifyError(f"tracked path type changed: expected symlink at {path}")
            target = os.readlink(os.fsencode(name), dir_fd=parent_fd)
            if not isinstance(target, bytes):
                target = os.fsencode(target)
            after_path = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            if _stat_identity(before_path) != _stat_identity(after_path):
                raise VerifyError(f"tracked symlink changed during verification: {path}")
            _recheck_parent_chain(chain)
            return target, after_path

        flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
        try:
            fd = os.open(name, flags, dir_fd=parent_fd)
        except OSError as exc:
            raise VerifyError(f"failed no-follow tracked file open for {path}: {exc}") from exc
        try:
            before_fd = os.fstat(fd)
            if not stat.S_ISREG(before_fd.st_mode):
                raise VerifyError(f"tracked path type changed: expected regular file at {path}")
            if not _same_object(before_path, before_fd):
                raise VerifyError(f"tracked pathname changed before open completed: {path}")
            data = _read_fd_all(fd)
            after_fd = os.fstat(fd)
            if _stat_identity(before_fd) != _stat_identity(after_fd):
                raise VerifyError(f"tracked file changed while being read: {path}")
            try:
                after_path = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError as exc:
                raise VerifyError(f"tracked pathname disappeared during verification: {path}") from exc
            if not _same_object(after_fd, after_path):
                raise VerifyError(f"tracked pathname identity changed during verification: {path}")
            if _stat_identity(before_path) != _stat_identity(after_path):
                raise VerifyError(f"tracked pathname metadata changed during verification: {path}")
            _recheck_parent_chain(chain)
            return data, after_fd
        finally:
            os.close(fd)
    finally:
        _close_parent_chain(chain)


def _walk_fd(
    dir_fd: int,
    rel_prefix: str,
    allowed_extra_prefixes: tuple[str, ...],
    observed: set[str],
) -> None:
    before_dir = os.fstat(dir_fd)
    names = os.listdir(dir_fd)
    for name in names:
        rel = f"{rel_prefix}/{name}" if rel_prefix else name
        if rel == ".git" and not rel_prefix:
            continue
        if any(under_prefix(rel, p) for p in allowed_extra_prefixes):
            continue
        try:
            st = os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
        except FileNotFoundError as exc:
            raise VerifyError(f"filesystem entry changed during enumeration: {rel}") from exc
        if stat.S_ISDIR(st.st_mode):
            child_fd = _open_dir_nofollow(name, dir_fd=dir_fd)
            try:
                opened = os.fstat(child_fd)
                if not _same_object(st, opened):
                    raise VerifyError(f"directory identity changed during traversal: {rel}")
                _walk_fd(child_fd, rel, allowed_extra_prefixes, observed)
                after_opened = os.fstat(child_fd)
                after_path = os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
                if _stat_identity(opened) != _stat_identity(after_opened):
                    raise VerifyError(f"directory metadata changed during traversal: {rel}")
                if not _same_object(opened, after_path):
                    raise VerifyError(f"directory pathname changed during traversal: {rel}")
            finally:
                os.close(child_fd)
        else:
            observed.add(rel)
    after_dir = os.fstat(dir_fd)
    if _stat_identity(before_dir) != _stat_identity(after_dir):
        raise VerifyError(f"directory changed during filesystem walk: {rel_prefix or '.'}")


def walk_filesystem_fd(root_fd: int, allowed_extra_prefixes: tuple[str, ...]) -> set[str]:
    observed: set[str] = set()
    _walk_fd(root_fd, "", allowed_extra_prefixes, observed)
    return observed


# Compatibility surface retained for the adversarial discriminant that substitutes
# a tracked pathname between enumeration and byte inspection.
def walk_filesystem(root_fd: int, allowed_extra_prefixes: tuple[str, ...]) -> set[str]:
    return walk_filesystem_fd(root_fd, allowed_extra_prefixes)


def verify(
    release: Path,
    *,
    expected_sha: str,
    expected_tree: str,
    critical_prefixes: tuple[str, ...] = DEFAULT_CRITICAL_PREFIXES,
    allowed_extra_prefixes: tuple[str, ...] = (),
) -> tuple[dict[str, Any], str]:
    _validate_platform_primitives()
    _reject_git_environment_overrides()

    supplied_release = Path(os.path.abspath(os.fspath(release)))
    try:
        supplied_st = supplied_release.lstat()
    except FileNotFoundError as exc:
        raise VerifyError("release path does not exist") from exc
    if stat.S_ISLNK(supplied_st.st_mode):
        raise VerifyError("release root must not be a symlink")
    if not stat.S_ISDIR(supplied_st.st_mode):
        raise VerifyError("release path is not a directory")
    release = supplied_release.resolve(strict=True)

    validate_hex40(expected_sha, "expected_sha")
    validate_hex40(expected_tree, "expected_tree")
    critical_prefixes = tuple(normalize_prefix(p) for p in critical_prefixes)
    allowed_extra_prefixes = tuple(normalize_prefix(p) for p in allowed_extra_prefixes)
    for allowed in allowed_extra_prefixes:
        if any(
            under_prefix(allowed, critical) or under_prefix(critical, allowed)
            for critical in critical_prefixes
        ):
            raise VerifyError(
                f"allowed-extra prefix overlaps execution-critical authority: {allowed}"
            )

    independence = ensure_git_independence(release)
    git_write_before = git_write_snapshot(release)

    object_format = git(release, "rev-parse", "--show-object-format").decode().strip()
    if object_format != "sha1":
        raise VerifyError(f"unsupported Git object format: {object_format}")

    observed_sha = git(release, "rev-parse", "--verify", "HEAD").decode().strip()
    observed_head_tree = git(release, "rev-parse", "--verify", "HEAD^{tree}").decode().strip()
    if observed_sha != expected_sha:
        raise VerifyError(f"HEAD mismatch: expected {expected_sha}, observed {observed_sha}")
    if observed_head_tree != expected_tree:
        raise VerifyError(f"HEAD tree mismatch: expected {expected_tree}, observed {observed_head_tree}")

    entries = expected_entries(release, expected_tree)

    root_fd = _open_dir_nofollow(release)
    try:
        root_before = os.fstat(root_fd)
        observed_paths = walk_filesystem(root_fd, allowed_extra_prefixes)

        mismatches: list[dict[str, str]] = []
        missing: list[str] = []
        expected_paths = set(entries)
        for path, entry in sorted(entries.items()):
            if path not in observed_paths:
                missing.append(path)
                continue
            expected_mode = entry["mode"]
            try:
                data, st = _read_tracked_entry(root_fd, path, expected_mode)
            except FileNotFoundError:
                missing.append(path)
                continue
            except VerifyError as exc:
                mismatches.append({
                    "path": path,
                    "kind": "inspection_race_or_type",
                    "expected": expected_mode,
                    "observed": str(exc),
                })
                continue

            if expected_mode == "120000":
                if not stat.S_ISLNK(st.st_mode):
                    mismatches.append({"path": path, "kind": "type", "expected": "symlink", "observed": "non-symlink"})
                    continue
            else:
                if not stat.S_ISREG(st.st_mode):
                    mismatches.append({"path": path, "kind": "type", "expected": "regular", "observed": "non-regular"})
                    continue
                executable = bool(st.st_mode & 0o111)
                expected_exec = expected_mode == "100755"
                if executable != expected_exec:
                    mismatches.append({
                        "path": path,
                        "kind": "mode",
                        "expected": expected_mode,
                        "observed": "100755" if executable else "100644",
                    })

            oid = git_blob_oid(data)
            if oid != entry["oid"]:
                mismatches.append({"path": path, "kind": "blob", "expected": entry["oid"], "observed": oid})

        observed_paths_after = walk_filesystem(root_fd, allowed_extra_prefixes)
        if observed_paths_after != observed_paths:
            raise VerifyError("release filesystem entry set changed during verification")

        root_after = os.fstat(root_fd)
        root_stable = _stat_identity(root_before) == _stat_identity(root_after)
    finally:
        os.close(root_fd)

    extras = sorted(observed_paths - expected_paths)
    critical_extras = sorted(
        path for path in extras if any(under_prefix(path, prefix) for prefix in critical_prefixes)
    )
    critical_extra_set = set(critical_extras)
    noncritical_extras = sorted(path for path in extras if path not in critical_extra_set)

    entries_after = expected_entries(release, expected_tree)
    if entries_after != entries:
        raise VerifyError("expected Git tree authority changed during verification")
    observed_sha_after = git(release, "rev-parse", "--verify", "HEAD").decode().strip()
    observed_tree_after = git(release, "rev-parse", "--verify", "HEAD^{tree}").decode().strip()
    if observed_sha_after != observed_sha or observed_tree_after != observed_head_tree:
        raise VerifyError("HEAD authority changed during verification")
    independence_after = ensure_git_independence(release)
    if independence_after != independence:
        raise VerifyError("Git object authority changed during verification")

    git_write_after = git_write_snapshot(release)
    git_metadata_unchanged = git_write_before == git_write_after
    before_locks = set(git_write_before["lock_paths"])
    after_locks = set(git_write_after["lock_paths"])
    new_lock_paths = sorted(after_locks - before_locks)

    status = "GREEN"
    reasons: list[str] = []
    if missing:
        status = "RED"
        reasons.append("missing_tracked_file")
    if mismatches:
        status = "RED"
        reasons.append("tracked_byte_or_mode_mismatch")
    if critical_extras:
        status = "RED"
        reasons.append("untracked_execution_critical_path")
    if noncritical_extras:
        status = "RED"
        reasons.append("unexpected_untracked_path")
    if not root_stable:
        status = "RED"
        reasons.append("release_root_changed_during_verification")
    if not git_metadata_unchanged:
        status = "RED"
        reasons.append("git_metadata_write_detected")
    if new_lock_paths:
        status = "RED"
        reasons.append("new_git_lock_file_detected")

    report = {
        "schema": REPORT_SCHEMA,
        "status": status,
        "reasons": reasons,
        "release_path": str(release),
        "expected_sha": expected_sha,
        "observed_sha": observed_sha,
        "expected_tree": expected_tree,
        "observed_head_tree": observed_head_tree,
        "git_optional_locks": "0",
        "replacement_objects_disabled": True,
        "replace_refs_absent": independence["replace_refs_absent"],
        "legacy_grafts_absent": independence["legacy_grafts_absent"],
        "git_independence": independence,
        "path_access": {
            "method": "root_fd+dir_fd/openat-style+O_NOFOLLOW+lstat/fstat identity recheck",
            "root_fd_anchored": True,
            "nofollow_traversal": True,
            "opened_object_fstat_before_after": True,
            "pathname_identity_rechecked": True,
            "directory_mutation_checks": True,
            "release_root_stable_during_verification": root_stable,
            "residual_boundary": TARGET_HOST_ONLY_IMMUTABILITY,
        },
        "git_metadata_before": git_write_before,
        "git_metadata_after": git_write_after,
        "git_metadata_unchanged": git_metadata_unchanged,
        "new_git_lock_paths": new_lock_paths,
        "expected_entry_count": len(expected_paths),
        "observed_non_git_entry_count": len(observed_paths),
        "missing_tracked_paths": missing,
        "tracked_mismatches": mismatches,
        "untracked_execution_critical_paths": critical_extras,
        "untracked_other_paths": noncritical_extras,
        "critical_prefixes": list(critical_prefixes),
        "allowed_extra_prefixes": list(allowed_extra_prefixes),
        "target_host_only_residual": TARGET_HOST_ONLY_IMMUTABILITY,
        "residual_immutability_boundary": TARGET_HOST_ONLY_IMMUTABILITY,
    }
    digest = sha256_digest(canonical_json_bytes(report))
    return report, digest


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--release", required=True, type=Path)
    p.add_argument("--expected-sha", required=True)
    p.add_argument("--expected-tree", required=True)
    p.add_argument("--critical-prefix", action="append", default=None)
    p.add_argument("--allow-extra-prefix", action="append", default=[])
    args = p.parse_args(argv)
    try:
        report, digest = verify(
            args.release,
            expected_sha=args.expected_sha,
            expected_tree=args.expected_tree,
            critical_prefixes=tuple(args.critical_prefix) if args.critical_prefix else DEFAULT_CRITICAL_PREFIXES,
            allowed_extra_prefixes=tuple(args.allow_extra_prefix),
        )
        out = {"report": report, "report_sha256": digest}
        sys.stdout.write(canonical_json_bytes(out).decode("ascii") + "\n")
        return 0 if report["status"] == "GREEN" else 2
    except (VerifyError, OSError) as exc:
        failure = {
            "schema": REPORT_SCHEMA,
            "status": "RED",
            "reasons": ["verifier_precondition_failure"],
            "error": str(exc),
            "replacement_objects_disabled": True,
            "target_host_only_residual": TARGET_HOST_ONLY_IMMUTABILITY,
        }
        digest = sha256_digest(canonical_json_bytes(failure))
        sys.stdout.write(canonical_json_bytes({"report": failure, "report_sha256": digest}).decode("ascii") + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
