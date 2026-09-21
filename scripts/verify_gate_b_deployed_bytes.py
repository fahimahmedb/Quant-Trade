#!/usr/bin/env python3
"""Index-independent verifier for a frozen Gate-B deployed Git tree.

Expected object metadata is read with replacement objects disabled.  Deployed
bytes are inspected from a root directory descriptor with no-follow traversal,
so the Git index and pathname dereference are never authority for release bytes.
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
from typing import Any

REPORT_SCHEMA = "quant-gate-b-deployed-byte-verification/v2"
DEFAULT_CRITICAL_PREFIXES = ("src", "deploy", "scripts")
HEX40 = set("0123456789abcdef")
REJECTED_GIT_ENV = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_COMMON_DIR",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_REPLACE_REF_BASE",
)
TARGET_HOST_ONLY_BOUNDARY = (
    "TARGET_HOST_ONLY: immutability of the frozen release for the "
    "verification-to-first-mutation authority window"
)


class VerifyError(RuntimeError):
    pass


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha256_digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _reject_external_git_overrides() -> None:
    present = sorted(name for name in REJECTED_GIT_ENV if os.environ.get(name))
    if present:
        raise VerifyError("Git authority override environment is present: " + ",".join(present))


def _git_env() -> dict[str, str]:
    _reject_external_git_overrides()
    env = os.environ.copy()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_CONFIG_GLOBAL"] = os.devnull
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
    if not isinstance(value, str):
        raise VerifyError("path prefix must be a string")
    candidate = value.strip("/")
    raw_parts = value.split("/")
    if (
        not candidate
        or candidate == "."
        or value.startswith("/")
        or value.endswith("/")
        or "//" in value
        or "." in raw_parts
        or ".." in raw_parts
    ):
        raise VerifyError(f"invalid path prefix: {value!r}")
    return candidate


def under_prefix(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(prefix + "/")


def _mode_snapshot(st: os.stat_result) -> dict[str, int]:
    return {
        "dev": st.st_dev,
        "ino": st.st_ino,
        "mode": stat.S_IFMT(st.st_mode) | stat.S_IMODE(st.st_mode),
        "size": st.st_size,
        "mtime_ns": st.st_mtime_ns,
        "ctime_ns": st.st_ctime_ns,
    }


def _same_identity(a: os.stat_result, b: os.stat_result) -> bool:
    return a.st_dev == b.st_dev and a.st_ino == b.st_ino and stat.S_IFMT(a.st_mode) == stat.S_IFMT(b.st_mode)


def _assert_absolute_path_components_nosymlink(path: Path) -> None:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        st = os.lstat(current)
        if stat.S_ISLNK(st.st_mode):
            raise VerifyError(f"release path contains symlink component: {current}")


def _open_dir_nofollow(path: Path) -> int:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    before = os.lstat(path)
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
        raise VerifyError(f"directory authority is not a real directory: {path}")
    fd = os.open(path, flags)
    try:
        opened = os.fstat(fd)
        if not _same_identity(before, opened) or not stat.S_ISDIR(opened.st_mode):
            raise VerifyError(f"directory identity changed while opening: {path}")
        after = os.lstat(path)
        if not _same_identity(opened, after):
            raise VerifyError(f"directory identity changed during inspection: {path}")
        return fd
    except Exception:
        os.close(fd)
        raise


def _open_child_dir(parent_fd: int, name: str, display: str) -> int:
    before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
        raise VerifyError(f"path component is not a real directory: {display}")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(name, flags, dir_fd=parent_fd)
    opened = os.fstat(fd)
    if not _same_identity(before, opened) or not stat.S_ISDIR(opened.st_mode):
        os.close(fd)
        raise VerifyError(f"directory path raced while opening: {display}")
    return fd


def _assert_fd_tree_no_symlinks(root_fd: int, label: str) -> None:
    def visit(fd: int, prefix: str) -> None:
        try:
            entries = sorted(os.scandir(fd), key=lambda item: item.name)
        except OSError as exc:
            raise VerifyError(f"cannot inspect {label}: {prefix or '.'}: {exc}") from exc
        for entry in entries:
            rel = f"{prefix}/{entry.name}" if prefix else entry.name
            st = entry.stat(follow_symlinks=False)
            if stat.S_ISLNK(st.st_mode):
                raise VerifyError(f"{label} contains symlink indirection: {rel}")
            if stat.S_ISDIR(st.st_mode):
                child = _open_child_dir(fd, entry.name, f"{label}/{rel}")
                try:
                    visit(child, rel)
                finally:
                    os.close(child)
    visit(root_fd, "")


def _lexical_path(raw: str, *, base: Path) -> Path:
    return Path(os.path.abspath(raw if os.path.isabs(raw) else os.path.join(str(base), raw)))


def ensure_git_independence(repo: Path) -> dict[str, Any]:
    _reject_external_git_overrides()
    dotgit = repo / ".git"
    try:
        dotgit_st = os.lstat(dotgit)
    except FileNotFoundError as exc:
        raise VerifyError("release does not contain an independent .git directory") from exc
    if stat.S_ISLNK(dotgit_st.st_mode):
        raise VerifyError(".git must not be a symlink")
    if not stat.S_ISDIR(dotgit_st.st_mode):
        if stat.S_ISREG(dotgit_st.st_mode):
            raise VerifyError("linked worktree dependency detected (.git is a file)")
        raise VerifyError("release does not contain an independent .git directory")

    commondir_marker = dotgit / "commondir"
    if os.path.lexists(commondir_marker):
        raise VerifyError("Git common-dir indirection marker is not allowed")

    objects = dotgit / "objects"
    objects_st = os.lstat(objects)
    if stat.S_ISLNK(objects_st.st_mode) or not stat.S_ISDIR(objects_st.st_mode):
        raise VerifyError(".git/objects must be a real release-local directory")
    objects_fd = _open_dir_nofollow(objects)
    try:
        _assert_fd_tree_no_symlinks(objects_fd, ".git/objects")
    finally:
        os.close(objects_fd)

    refs = dotgit / "refs"
    if os.path.lexists(refs):
        refs_fd = _open_dir_nofollow(refs)
        try:
            _assert_fd_tree_no_symlinks(refs_fd, ".git/refs")
        finally:
            os.close(refs_fd)
    for metadata_name in ("HEAD", "config", "packed-refs"):
        metadata_path = dotgit / metadata_name
        if not os.path.lexists(metadata_path):
            continue
        metadata_st = os.lstat(metadata_path)
        if stat.S_ISLNK(metadata_st.st_mode) or not stat.S_ISREG(metadata_st.st_mode):
            raise VerifyError(f"Git metadata indirection is not allowed: .git/{metadata_name}")

    expected_git_dir = Path(os.path.abspath(dotgit))
    git_dir_raw = git(repo, "rev-parse", "--absolute-git-dir").decode().strip()
    git_dir = _lexical_path(git_dir_raw, base=repo)
    common_raw = git(repo, "rev-parse", "--git-common-dir").decode().strip()
    common_dir = _lexical_path(common_raw, base=repo)
    objects_raw = git(repo, "rev-parse", "--git-path", "objects").decode().strip()
    objects_path = _lexical_path(objects_raw, base=repo)
    expected_objects = expected_git_dir / "objects"

    if git_dir != expected_git_dir:
        raise VerifyError("absolute git-dir is not the intended release-local .git directory")
    if common_dir != expected_git_dir:
        raise VerifyError("foreign/common Git metadata dependency detected")
    if objects_path != expected_objects:
        raise VerifyError("Git object directory is not release-local")

    alternates = expected_objects / "info" / "alternates"
    if os.path.lexists(alternates):
        raise VerifyError("Git alternates file must be absent")

    return {
        "git_dir": str(git_dir),
        "common_dir": str(common_dir),
        "object_directory": str(objects_path),
        "dotgit_real_directory": True,
        "objects_real_directory": True,
        "object_tree_symlink_free": True,
        "common_dir_indirection_absent": True,
        "alternates_file_present": False,
        "object_store_override_environment_absent": True,
    }


def ensure_replacement_independence(repo: Path) -> dict[str, Any]:
    refs = git(repo, "for-each-ref", "--format=%(refname)", "refs/replace/").decode().splitlines()
    refs = sorted(line.strip() for line in refs if line.strip())
    if refs:
        raise VerifyError("Git replace refs are not allowed: " + ",".join(refs))
    grafts_raw = git(repo, "rev-parse", "--git-path", "info/grafts").decode().strip()
    grafts = _lexical_path(grafts_raw, base=repo)
    expected = Path(os.path.abspath(repo / ".git" / "info" / "grafts"))
    if grafts != expected:
        raise VerifyError("legacy graft metadata path is not release-local")
    if os.path.lexists(grafts):
        raise VerifyError("legacy Git graft metadata is not allowed")
    return {
        "replacement_object_semantics_disabled": True,
        "replace_refs_absent": True,
        "legacy_grafts_absent": True,
        "legacy_grafts_disposition": "rejected_if_present_at_.git/info/grafts",
    }


def _stable_read_file(path: Path) -> bytes:
    before = os.lstat(path)
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise VerifyError(f"Git metadata file is not a real regular file: {path}")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags)
    try:
        opened = os.fstat(fd)
        if not _same_identity(before, opened):
            raise VerifyError(f"Git metadata file identity raced: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after_fd = os.fstat(fd)
        after_path = os.lstat(path)
        if _mode_snapshot(opened) != _mode_snapshot(after_fd) or not _same_identity(after_fd, after_path):
            raise VerifyError(f"Git metadata file changed during inspection: {path}")
        return b"".join(chunks)
    finally:
        os.close(fd)


def git_write_snapshot(repo: Path) -> dict[str, Any]:
    dotgit = repo / ".git"
    index = dotgit / "index"
    index_info = None
    if os.path.lexists(index):
        data = _stable_read_file(index)
        st = os.lstat(index)
        index_info = {
            "dev": st.st_dev,
            "ino": st.st_ino,
            "size": st.st_size,
            "mtime_ns": st.st_mtime_ns,
            "sha256": sha256_digest(data),
        }
    lock_info: list[dict[str, Any]] = []
    for root, dirs, files in os.walk(dotgit, topdown=True, followlinks=False):
        dirs[:] = [d for d in dirs if not (Path(root) / d).is_symlink()]
        for name in sorted(files):
            if not name.endswith(".lock"):
                continue
            path = Path(root) / name
            st = os.lstat(path)
            lock_info.append({
                "path": path.relative_to(dotgit).as_posix(),
                "dev": st.st_dev,
                "ino": st.st_ino,
                "mode": stat.S_IFMT(st.st_mode) | stat.S_IMODE(st.st_mode),
                "size": st.st_size,
                "mtime_ns": st.st_mtime_ns,
            })
    return {"index": index_info, "lock_paths": lock_info}


def expected_entries(repo: Path, expected_tree: str) -> dict[str, dict[str, str]]:
    raw = git(repo, "ls-tree", "-r", "-z", "--full-tree", expected_tree)
    entries: dict[str, dict[str, str]] = {}
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            meta, path_bytes = record.split(b"\t", 1)
            mode_b, type_b, oid_b = meta.split(b" ", 2)
            path = path_bytes.decode("utf-8")
            mode = mode_b.decode("ascii")
            typ = type_b.decode("ascii")
            oid = oid_b.decode("ascii")
        except Exception as exc:
            raise VerifyError("malformed git ls-tree output") from exc
        pure = PurePosixPath(path)
        if pure.is_absolute() or not pure.parts or "." in pure.parts or ".." in pure.parts:
            raise VerifyError(f"unsafe tracked path in expected tree: {path!r}")
        if path in entries:
            raise VerifyError(f"duplicate tree path: {path}")
        if typ != "blob":
            raise VerifyError(f"unsupported tracked object type {typ} at {path}")
        if mode not in {"100644", "100755", "120000"}:
            raise VerifyError(f"unsupported tracked mode {mode} at {path}")
        entries[path] = {"mode": mode, "oid": oid}
    return entries


def walk_filesystem(root_fd: int, allowed_extra_prefixes: tuple[str, ...]) -> set[str]:
    observed: set[str] = set()

    def visit(fd: int, prefix: str) -> None:
        entries = sorted(os.scandir(fd), key=lambda item: item.name)
        for entry in entries:
            rel = f"{prefix}/{entry.name}" if prefix else entry.name
            if rel == ".git" or rel.startswith(".git/"):
                continue
            if any(under_prefix(rel, allowed) for allowed in allowed_extra_prefixes):
                continue
            st = entry.stat(follow_symlinks=False)
            if stat.S_ISDIR(st.st_mode):
                child = _open_child_dir(fd, entry.name, rel)
                try:
                    visit(child, rel)
                finally:
                    os.close(child)
            else:
                observed.add(rel)

    visit(root_fd, "")
    return observed


def _open_parent_chain(root_fd: int, path: str) -> tuple[int, str, list[tuple[int, str, int, os.stat_result]]]:
    parts = PurePosixPath(path).parts
    if not parts:
        raise VerifyError("empty tracked path")
    current = os.dup(root_fd)
    chain: list[tuple[int, str, int, os.stat_result]] = []
    try:
        for index, name in enumerate(parts[:-1]):
            display = "/".join(parts[: index + 1])
            before = os.stat(name, dir_fd=current, follow_symlinks=False)
            child = _open_child_dir(current, name, display)
            chain.append((current, name, child, before))
            current = child
        return current, parts[-1], chain
    except Exception:
        seen: set[int] = set()
        for parent, _, child, _ in reversed(chain):
            for fd in (child, parent):
                if fd not in seen:
                    seen.add(fd)
                    try:
                        os.close(fd)
                    except OSError:
                        pass
        if current not in seen:
            try:
                os.close(current)
            except OSError:
                pass
        raise


def _close_chain(parent_fd: int, chain: list[tuple[int, str, int, os.stat_result]]) -> None:
    fds = {parent_fd}
    for parent, _, child, _ in chain:
        fds.add(parent)
        fds.add(child)
    for fd in fds:
        try:
            os.close(fd)
        except OSError:
            pass


def _verify_chain_stable(chain: list[tuple[int, str, int, os.stat_result]], path: str) -> None:
    for parent_fd, name, child_fd, before in chain:
        now_path = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        now_fd = os.fstat(child_fd)
        if not _same_identity(before, now_fd) or not _same_identity(now_path, now_fd):
            raise VerifyError(f"tracked parent path changed during inspection: {path}")


def read_tracked_blob(root_fd: int, path: str, expected_mode: str) -> tuple[bytes | None, dict[str, str] | None]:
    parent_fd, leaf, chain = _open_parent_chain(root_fd, path)
    try:
        try:
            before = os.stat(leaf, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return None, {"path": path, "kind": "missing", "expected": expected_mode, "observed": "missing"}

        if expected_mode == "120000":
            if not stat.S_ISLNK(before.st_mode):
                return None, {"path": path, "kind": "type", "expected": "symlink", "observed": "non-symlink"}
            target = os.readlink(os.fsencode(leaf), dir_fd=parent_fd)
            after = os.stat(leaf, dir_fd=parent_fd, follow_symlinks=False)
            _verify_chain_stable(chain, path)
            if _mode_snapshot(before) != _mode_snapshot(after):
                raise VerifyError(f"tracked symlink changed during inspection: {path}")
            return target if isinstance(target, bytes) else os.fsencode(target), None

        if not stat.S_ISREG(before.st_mode):
            return None, {"path": path, "kind": "type", "expected": "regular", "observed": "non-regular"}

        flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(leaf, flags, dir_fd=parent_fd)
        try:
            opened = os.fstat(fd)
            if not stat.S_ISREG(opened.st_mode) or not _same_identity(before, opened):
                raise VerifyError(f"tracked file identity raced while opening: {path}")
            chunks: list[bytes] = []
            while True:
                chunk = os.read(fd, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            after_fd = os.fstat(fd)
        finally:
            os.close(fd)
        after_path = os.stat(leaf, dir_fd=parent_fd, follow_symlinks=False)
        _verify_chain_stable(chain, path)
        if _mode_snapshot(opened) != _mode_snapshot(after_fd) or not _same_identity(after_fd, after_path):
            raise VerifyError(f"tracked file changed during inspection: {path}")
        executable = bool(after_fd.st_mode & 0o111)
        expected_exec = expected_mode == "100755"
        if executable != expected_exec:
            return b"".join(chunks), {
                "path": path,
                "kind": "mode",
                "expected": expected_mode,
                "observed": "100755" if executable else "100644",
            }
        return b"".join(chunks), None
    finally:
        _close_chain(parent_fd, chain)


def verify(
    release: Path,
    *,
    expected_sha: str,
    expected_tree: str,
    critical_prefixes: tuple[str, ...] = DEFAULT_CRITICAL_PREFIXES,
    allowed_extra_prefixes: tuple[str, ...] = (),
) -> tuple[dict[str, Any], str]:
    _reject_external_git_overrides()
    release = Path(os.path.abspath(os.fspath(release)))
    _assert_absolute_path_components_nosymlink(release)
    validate_hex40(expected_sha, "expected_sha")
    validate_hex40(expected_tree, "expected_tree")
    critical_prefixes = tuple(normalize_prefix(p) for p in critical_prefixes)
    allowed_extra_prefixes = tuple(normalize_prefix(p) for p in allowed_extra_prefixes)

    root_fd = _open_dir_nofollow(release)
    root_initial = os.fstat(root_fd)
    try:
        independence_before = ensure_git_independence(release)
        replacement_before = ensure_replacement_independence(release)
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
        observed_paths = walk_filesystem(root_fd, allowed_extra_prefixes)

        mismatches: list[dict[str, str]] = []
        missing: list[str] = []
        expected_paths = set(entries)
        for path, entry in sorted(entries.items()):
            try:
                data, mismatch = read_tracked_blob(root_fd, path, entry["mode"])
            except FileNotFoundError:
                data, mismatch = None, {"path": path, "kind": "missing", "expected": entry["mode"], "observed": "missing"}
            if mismatch is not None:
                if mismatch["kind"] == "missing":
                    missing.append(path)
                else:
                    mismatches.append(mismatch)
                continue
            assert data is not None
            oid = git_blob_oid(data)
            if oid != entry["oid"]:
                mismatches.append({"path": path, "kind": "blob", "expected": entry["oid"], "observed": oid})

        extras = sorted(observed_paths - expected_paths)
        critical_extras = sorted(path for path in extras if any(under_prefix(path, p) for p in critical_prefixes))
        critical_extra_set = set(critical_extras)
        noncritical_extras = sorted(path for path in extras if path not in critical_extra_set)

        replacement_after = ensure_replacement_independence(release)
        independence_after = ensure_git_independence(release)
        if independence_before != independence_after:
            raise VerifyError("Git object authority changed during verification")
        if replacement_before != replacement_after:
            raise VerifyError("Git replacement authority changed during verification")

        git_write_after = git_write_snapshot(release)
        git_metadata_unchanged = git_write_before == git_write_after
        root_after_fd = os.fstat(root_fd)
        root_after_path = os.lstat(release)
        if _mode_snapshot(root_initial) != _mode_snapshot(root_after_fd) or not _same_identity(root_after_fd, root_after_path):
            raise VerifyError("release root identity changed during verification")

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
        if not git_metadata_unchanged:
            status = "RED"
            reasons.append("git_metadata_write_detected")

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
            "replacement_object_semantics_disabled": True,
            "replace_refs_absent": True,
            "legacy_grafts_absent": True,
            "git_independence": independence_after,
            "replacement_independence": replacement_after,
            "path_access_race_hardening": {
                "root_directory_fd_anchored": True,
                "tracked_parent_traversal": "dir_fd/openat-style",
                "nofollow": "O_NOFOLLOW where available plus lstat/fstat identity checks",
                "regular_file_mutation_detection": "lstat/open/fstat/read/fstat/lstat identity+metadata",
                "symlink_mutation_detection": "lstat/readlink/lstat identity+metadata",
            },
            "residual_immutability_boundary": TARGET_HOST_ONLY_BOUNDARY,
            "git_metadata_before": git_write_before,
            "git_metadata_after": git_write_after,
            "git_metadata_unchanged": git_metadata_unchanged,
            "expected_entry_count": len(expected_paths),
            "observed_non_git_entry_count": len(observed_paths),
            "missing_tracked_paths": missing,
            "tracked_mismatches": mismatches,
            "untracked_execution_critical_paths": critical_extras,
            "untracked_other_paths": noncritical_extras,
            "critical_prefixes": list(critical_prefixes),
            "allowed_extra_prefixes": list(allowed_extra_prefixes),
        }
        digest = sha256_digest(canonical_json_bytes(report))
        return report, digest
    finally:
        os.close(root_fd)


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
        }
        digest = sha256_digest(canonical_json_bytes(failure))
        sys.stdout.write(canonical_json_bytes({"report": failure, "report_sha256": digest}).decode("ascii") + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
