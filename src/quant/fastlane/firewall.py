"""Firewall for the fast-lane lineage ``QUANT_FASTLANE_HPIT_V1``.

The fast lane (``handoff/CLAUDE_DELEGATED_DECISIONS_AND_PLAN_2026-09-23.md`` D5)
must own its data space, its ledgers and its registry, and must never write
into the frozen lineage ``FORM4_FIRST_VERTICAL_MULTI_COHORT_V1``.

Every fast-lane read or write goes through :class:`Firewall`:

* data (raw zips, derived tables, ledgers) lives under ``var/fastlane/``
  (git-ignored);
* small committed artifacts (manifests, census, protocol, sealed prereg) live
  under ``research/fastlane/``;
* ``governance/`` and ``handoff/`` may be read (hashed) read-only, to bind a
  cited rule to its bytes;
* any path that names the frozen lineage, or resolves outside those roots
  (including through a symlink), is refused.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

LINEAGE_ID = "QUANT_FASTLANE_HPIT_V1"
FROZEN_LINEAGE_ID = "FORM4_FIRST_VERTICAL_MULTI_COHORT_V1"
# Any path component containing one of these tokens belongs to the frozen
# first-vertical family (FORM4_FIRST_VERTICAL_V1 and its multi-cohort lineage).
FROZEN_PATH_TOKENS = ("FORM4_FIRST_VERTICAL",)

DATA_ROOT_REL = Path("var") / "fastlane"
ARTIFACT_ROOT_REL = Path("research") / "fastlane"
READONLY_REFERENCE_ROOTS_REL = (Path("governance"), Path("handoff"))


class FirewallViolation(PermissionError):
    """A fast-lane operation tried to leave its own space."""


def _refuse_frozen(path: Path) -> None:
    for part in path.parts:
        upper = part.upper()
        for token in FROZEN_PATH_TOKENS:
            if token in upper:
                raise FirewallViolation(
                    f"path {path} names the frozen lineage {FROZEN_LINEAGE_ID}; "
                    f"{LINEAGE_ID} may not read or write it")


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


@dataclass(frozen=True)
class Firewall:
    repo_root: Path

    def __post_init__(self) -> None:
        object.__setattr__(self, "repo_root", Path(self.repo_root).resolve())

    # --- roots ---------------------------------------------------------------
    @property
    def data_root(self) -> Path:
        return self.repo_root / DATA_ROOT_REL

    @property
    def artifact_root(self) -> Path:
        return self.repo_root / ARTIFACT_ROOT_REL

    def data(self, *parts: str) -> Path:
        return self.guard(self.data_root.joinpath(*parts), write=True)

    def artifact(self, *parts: str) -> Path:
        return self.guard(self.artifact_root.joinpath(*parts), write=True)

    # --- the guard -----------------------------------------------------------
    def guard(self, path: Path | str, *, write: bool) -> Path:
        """Return the resolved path if the fast lane may touch it, else raise."""
        raw = Path(path)
        if not raw.is_absolute():
            raw = self.repo_root / raw
        _refuse_frozen(raw)
        resolved = raw.resolve()
        _refuse_frozen(resolved)
        allowed = [self.data_root, self.artifact_root]
        if not write:
            allowed += [self.repo_root / rel for rel in READONLY_REFERENCE_ROOTS_REL]
        if not any(_within(resolved, root.resolve()) for root in allowed):
            mode = "write" if write else "read"
            raise FirewallViolation(
                f"{LINEAGE_ID} may not {mode} {resolved}: outside "
                f"{DATA_ROOT_REL}/ and {ARTIFACT_ROOT_REL}/")
        return resolved

    # --- guarded I/O ---------------------------------------------------------
    def read_bytes(self, path: Path | str) -> bytes:
        return self.guard(path, write=False).read_bytes()

    def read_json(self, path: Path | str) -> Any:
        return json.loads(self.read_bytes(path).decode("utf-8"))

    def sha256_file(self, path: Path | str) -> str:
        return sha256_file(self.guard(path, write=False))

    def write_bytes_atomic(self, path: Path | str, payload: bytes) -> Path:
        target = self.guard(path, write=True)
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(target.name + ".tmp")
        with open(tmp, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, target)
        _fsync_dir(target.parent)
        return target

    def write_json_atomic(self, path: Path | str, obj: Any) -> Path:
        text = json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False,
                          allow_nan=False) + "\n"
        return self.write_bytes_atomic(path, text.encode("utf-8"))

    def write_text_atomic(self, path: Path | str, text: str) -> Path:
        return self.write_bytes_atomic(path, text.encode("utf-8"))

    def create_exclusive(self, path: Path | str, payload: bytes) -> Path:
        """Write a file exactly once, atomically; raise FileExistsError if it exists.

        The bytes go to a private temp file (fsynced) which is then hard-linked
        to the target: ``link`` fails if the target exists and never exposes a
        partially written file, so a crash leaves either nothing or the whole file.
        """
        target = self.guard(path, write=True)
        target.parent.mkdir(parents=True, exist_ok=True)
        # A crash between the temp write and the link leaves a dot-prefixed
        # ``.<name>.*.tmp`` (git-ignored); clear such leftovers before each write.
        for stale in target.parent.glob(f".{target.name}.*.tmp"):
            try:
                stale.unlink()
            except FileNotFoundError:
                pass
        tmp = target.with_name(f".{target.name}.{os.getpid()}.{os.urandom(6).hex()}.tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        try:
            os.write(fd, payload)
            os.fsync(fd)
        finally:
            os.close(fd)
        try:
            os.link(tmp, target)
        finally:
            os.unlink(tmp)
        _fsync_dir(target.parent)
        return target

    def mkdirs(self, path: Path | str) -> Path:
        target = self.guard(path, write=True)
        target.mkdir(parents=True, exist_ok=True)
        return target

    def iter_files(self, path: Path | str, pattern: str = "*") -> Iterable[Path]:
        base = self.guard(path, write=False)
        if not base.exists():
            return []
        return sorted(p for p in base.glob(pattern) if p.is_file())


def _fsync_dir(directory: Path) -> None:
    try:
        fd = os.open(directory, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            block = handle.read(chunk)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def default_repo_root() -> Path:
    # src/quant/fastlane/firewall.py -> repo root
    return Path(__file__).resolve().parents[3]
