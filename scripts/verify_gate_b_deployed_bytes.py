#!/usr/bin/env python3
"""Index-independent verifier for a frozen Gate-B deployed Git tree.

The verifier never uses the worktree index as authority.  It reads the expected
tree via `git ls-tree`, hashes deployed bytes directly, rejects linked worktrees
and Git alternates, and emits canonical JSON plus a SHA-256 digest.
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

REPORT_SCHEMA = "quant-gate-b-deployed-byte-verification/v1"
DEFAULT_CRITICAL_PREFIXES = ("src", "deploy", "scripts")
HEX40 = set("0123456789abcdef")


class VerifyError(RuntimeError):
    pass


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha256_digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def git(repo: Path, *args: str) -> bytes:
    env = os.environ.copy()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env.pop("GIT_OBJECT_DIRECTORY", None)
    env.pop("GIT_ALTERNATE_OBJECT_DIRECTORIES", None)
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
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
    value = value.strip("/")
    if not value or value == "." or ".." in PurePosixPath(value).parts:
        raise VerifyError(f"invalid path prefix: {value!r}")
    return value


def under_prefix(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(prefix + "/")



def git_write_snapshot(repo: Path) -> dict[str, Any]:
    dotgit = repo / ".git"
    if not dotgit.is_dir():
        return {"index": None, "lock_paths": []}
    index = dotgit / "index"
    index_info = None
    if index.exists():
        st = index.stat()
        index_info = {
            "size": st.st_size,
            "mtime_ns": st.st_mtime_ns,
            "sha256": sha256_digest(index.read_bytes()),
        }
    lock_paths = sorted(
        path.relative_to(dotgit).as_posix()
        for path in dotgit.rglob("*.lock")
        if path.is_file() or path.is_symlink()
    )
    return {"index": index_info, "lock_paths": lock_paths}


def ensure_git_independence(repo: Path) -> dict[str, Any]:
    dotgit = repo / ".git"
    if dotgit.is_symlink():
        raise VerifyError(".git must not be a symlink")
    if not dotgit.is_dir():
        # Linked worktrees use a .git text file pointing at another worktree's metadata.
        if dotgit.is_file():
            raise VerifyError("linked worktree dependency detected (.git is a file)")
        raise VerifyError("release does not contain an independent .git directory")

    git_dir = Path(git(repo, "rev-parse", "--absolute-git-dir").decode().strip()).resolve()
    common_dir_raw = git(repo, "rev-parse", "--git-common-dir").decode().strip()
    common_dir = (repo / common_dir_raw).resolve() if not os.path.isabs(common_dir_raw) else Path(common_dir_raw).resolve()
    expected_git_dir = dotgit.resolve()
    if git_dir != expected_git_dir or common_dir != expected_git_dir:
        raise VerifyError("foreign/common Git metadata dependency detected")

    alternates = expected_git_dir / "objects" / "info" / "alternates"
    if alternates.exists():
        if alternates.is_symlink() or not alternates.is_file():
            raise VerifyError("Git alternates metadata is ambiguous")
        if alternates.read_bytes().strip():
            raise VerifyError("foreign Git alternate dependency detected")

    # Ask Git for the object stores it would actually consult. More than the local
    # object directory means an alternate (including environment/config mechanisms).
    object_dirs = git(repo, "rev-parse", "--git-path", "objects").decode().strip()
    objects_path = (repo / object_dirs).resolve() if not os.path.isabs(object_dirs) else Path(object_dirs).resolve()
    if objects_path != (expected_git_dir / "objects").resolve():
        raise VerifyError("Git object directory is not release-local")

    if os.environ.get("GIT_OBJECT_DIRECTORY") or os.environ.get("GIT_ALTERNATE_OBJECT_DIRECTORIES"):
        raise VerifyError("Git object-store override environment is present")

    return {
        "git_dir": str(git_dir),
        "common_dir": str(common_dir),
        "alternates_file_present": alternates.exists(),
        "object_directory": str(objects_path),
    }


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
        if path in entries:
            raise VerifyError(f"duplicate tree path: {path}")
        if typ != "blob":
            raise VerifyError(f"unsupported tracked object type {typ} at {path}")
        if mode not in {"100644", "100755", "120000"}:
            raise VerifyError(f"unsupported tracked mode {mode} at {path}")
        entries[path] = {"mode": mode, "oid": oid}
    return entries


def walk_filesystem(repo: Path, allowed_extra_prefixes: tuple[str, ...]) -> set[str]:
    observed: set[str] = set()
    for root, dirs, files in os.walk(repo, topdown=True, followlinks=False):
        root_path = Path(root)
        rel_root = root_path.relative_to(repo)
        if rel_root == Path("."):
            dirs[:] = [d for d in dirs if d != ".git" and not any(under_prefix(d, p) for p in allowed_extra_prefixes)]
        else:
            rel_root_posix = rel_root.as_posix()
            kept = []
            for d in dirs:
                p = f"{rel_root_posix}/{d}"
                if not any(under_prefix(p, prefix) for prefix in allowed_extra_prefixes):
                    kept.append(d)
            dirs[:] = kept

        # Directory symlinks appear in dirs when followlinks=False; record and remove.
        for d in list(dirs):
            full = root_path / d
            if full.is_symlink():
                rel = full.relative_to(repo).as_posix()
                observed.add(rel)
                dirs.remove(d)

        for name in files:
            full = root_path / name
            rel = full.relative_to(repo).as_posix()
            if any(under_prefix(rel, p) for p in allowed_extra_prefixes):
                continue
            observed.add(rel)
    return observed


def verify(
    release: Path,
    *,
    expected_sha: str,
    expected_tree: str,
    critical_prefixes: tuple[str, ...] = DEFAULT_CRITICAL_PREFIXES,
    allowed_extra_prefixes: tuple[str, ...] = (),
) -> tuple[dict[str, Any], str]:
    release = release.resolve(strict=True)
    if not release.is_dir():
        raise VerifyError("release path is not a directory")
    validate_hex40(expected_sha, "expected_sha")
    validate_hex40(expected_tree, "expected_tree")
    critical_prefixes = tuple(normalize_prefix(p) for p in critical_prefixes)
    allowed_extra_prefixes = tuple(normalize_prefix(p) for p in allowed_extra_prefixes)

    git_write_before = git_write_snapshot(release)
    independence = ensure_git_independence(release)
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
    observed_paths = walk_filesystem(release, allowed_extra_prefixes)

    mismatches: list[dict[str, str]] = []
    missing: list[str] = []
    expected_paths = set(entries)
    for path, entry in sorted(entries.items()):
        full = release / path
        if path not in observed_paths and not full.is_symlink():
            missing.append(path)
            continue
        try:
            st = full.lstat()
        except FileNotFoundError:
            missing.append(path)
            continue
        expected_mode = entry["mode"]
        if expected_mode == "120000":
            if not stat.S_ISLNK(st.st_mode):
                mismatches.append({"path": path, "kind": "type", "expected": "symlink", "observed": "non-symlink"})
                continue
            data = os.readlink(full).encode("utf-8", "surrogateescape")
        else:
            if not stat.S_ISREG(st.st_mode):
                mismatches.append({"path": path, "kind": "type", "expected": "regular", "observed": "non-regular"})
                continue
            data = full.read_bytes()
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

    extras = sorted(observed_paths - expected_paths)
    critical_extras = sorted(
        path for path in extras if any(under_prefix(path, prefix) for prefix in critical_prefixes)
    )
    noncritical_extras = sorted(path for path in extras if path not in set(critical_extras))
    git_write_after = git_write_snapshot(release)
    git_metadata_unchanged = git_write_before == git_write_after

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
        # Blue prestage requires unexpected release entries to be rejected unless
        # explicitly excluded; keep them separately visible from critical extras.
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
        "git_independence": independence,
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
