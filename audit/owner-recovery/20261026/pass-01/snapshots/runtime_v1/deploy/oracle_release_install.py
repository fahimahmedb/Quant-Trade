#!/usr/bin/env python3
"""Install one exact Quant-Trade Research OS release on an Oracle VM.

This module is deliberately scheduler-free. It installs a content-addressed
release, materializes the pinned real Legacy ledger fail-closed, validates the
control plane, runs bounded pre-outcome verification, and only then publishes an
atomic installation receipt.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from typing import Any, Dict

REPOSITORY = "fahimahmedb/Quant-Trade"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
MAX_ARCHIVE_BYTES = 96 * 1024 * 1024
MAX_LEDGER_BYTES = 16 * 1024 * 1024
LOCAL_RECEIPT = ".quant_release_receipt.json"
AUTHORITY_KEYS = (
    "economic_experiment_authorized",
    "prospective_observation_authorized",
    "real_capital_authorized",
    "live_trading_authorized",
)


class InstallBlock(RuntimeError):
    """Fail-closed installation or scientific-preflight error."""


def validate_sha(value: str) -> str:
    value = (value or "").strip().lower()
    if not SHA_RE.fullmatch(value):
        raise InstallBlock("INVALID_DEPLOY_SHA")
    return value


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def fetch_bytes(url: str, *, max_bytes: int, timeout: int = 60) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        data = response.read(max_bytes + 1)
    if not data:
        raise InstallBlock(f"REMOTE_OBJECT_EMPTY:{url}")
    if len(data) > max_bytes:
        raise InstallBlock(f"REMOTE_OBJECT_TOO_LARGE:{url}")
    return data


def _json_object(data: bytes, label: str) -> Dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallBlock(f"{label}_INVALID_JSON:{exc}") from exc
    if not isinstance(value, dict):
        raise InstallBlock(f"{label}_NOT_OBJECT")
    return value


def _atomic_json(path: Path, value: Dict[str, Any]) -> None:
    pending = path.with_name(path.name + ".tmp")
    pending.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    pending.replace(path)


def verify_legacy_payload(manifest: Dict[str, Any], data: bytes) -> Dict[str, Any]:
    required = (
        "source_commit",
        "ledger_path",
        "ledger_blob_sha",
        "schema_version",
        "reconciliation_status",
        "historical_research_items_found",
        "governance",
    )
    missing = [key for key in required if key not in manifest]
    if missing:
        raise InstallBlock("LEGACY_MANIFEST_INCOMPLETE:" + ",".join(missing))

    source_commit = validate_sha(str(manifest["source_commit"]))
    expected_blob = str(manifest["ledger_blob_sha"])
    if not SHA_RE.fullmatch(expected_blob):
        raise InstallBlock("LEGACY_MANIFEST_INVALID_BLOB_SHA")
    actual_blob = git_blob_sha(data)
    if actual_blob != expected_blob:
        raise InstallBlock(
            f"LEGACY_LEDGER_BLOB_MISMATCH:expected={expected_blob}:actual={actual_blob}"
        )

    ledger = _json_object(data, "LEGACY_LEDGER")
    if ledger.get("schema_version") != manifest["schema_version"]:
        raise InstallBlock("LEGACY_LEDGER_SCHEMA_MISMATCH")

    ledger_governance = ledger.get("governance")
    manifest_governance = manifest.get("governance")
    if not isinstance(ledger_governance, dict) or not isinstance(manifest_governance, dict):
        raise InstallBlock("LEGACY_GOVERNANCE_MISSING")
    for governance, prefix in (
        (ledger_governance, "LEGACY_LEDGER"),
        (manifest_governance, "LEGACY_MANIFEST"),
    ):
        if governance.get("historical_result_immutability") is not True:
            raise InstallBlock(prefix + "_HISTORICAL_IMMUTABILITY_UNSAFE")
        if governance.get("REAL_CAPITAL_AUTHORIZED") is not False:
            raise InstallBlock(prefix + "_REAL_CAPITAL_AUTHORITY_UNSAFE")
        if governance.get("LIVE_TRADING_AUTHORIZED") is not False:
            raise InstallBlock(prefix + "_LIVE_TRADING_AUTHORITY_UNSAFE")

    records = ledger.get("records")
    declared_items = manifest.get("historical_research_items_found")
    if not isinstance(records, list) or not records:
        raise InstallBlock("LEGACY_LEDGER_EMPTY")
    if type(declared_items) is not int or declared_items <= 0:
        raise InstallBlock("LEGACY_MANIFEST_INVALID_HISTORICAL_ITEM_COUNT")

    # historical_research_items_found is a reconciliation census, not a stated
    # 1:1 record-count contract. Integrity is the pinned Git blob + non-empty
    # parsed ledger. Both census and materialized count are retained in receipts.
    return {
        "source_commit": source_commit,
        "ledger_path": str(manifest["ledger_path"]),
        "ledger_blob_sha": actual_blob,
        "schema_version": ledger["schema_version"],
        "reconciliation_status": manifest["reconciliation_status"],
        "manifest_historical_research_items_found": declared_items,
        "loaded_record_count": len(records),
        "historical_result_immutability": True,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
    }


def materialize_legacy(release: Path) -> Dict[str, Any]:
    manifest_path = release / "research" / "research_os" / "legacy" / "source_manifest.json"
    if not manifest_path.is_file():
        raise InstallBlock("LEGACY_SOURCE_MANIFEST_MISSING")
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallBlock(f"LEGACY_SOURCE_MANIFEST_INVALID:{exc}") from exc
    if not isinstance(manifest, dict):
        raise InstallBlock("LEGACY_SOURCE_MANIFEST_NOT_OBJECT")

    source_commit = validate_sha(str(manifest.get("source_commit", "")))
    ledger_path = str(manifest.get("ledger_path") or "")
    parts = Path(ledger_path).parts
    if not ledger_path or ledger_path.startswith("/") or ".." in parts:
        raise InstallBlock("LEGACY_LEDGER_PATH_UNSAFE")

    raw_url = (
        f"https://raw.githubusercontent.com/{REPOSITORY}/"
        f"{source_commit}/{ledger_path}"
    )
    data = fetch_bytes(raw_url, max_bytes=MAX_LEDGER_BYTES)
    result = verify_legacy_payload(manifest, data)

    destination = (
        release
        / "research"
        / "research_os"
        / "legacy"
        / "LEGACY_RESEARCH_LEDGER.imported.json"
    )
    pending = destination.with_name(destination.name + ".tmp")
    pending.write_bytes(data)
    pending.replace(destination)
    result["materialized_path"] = str(destination.relative_to(release))
    return result


def verify_control_plane(release: Path) -> Dict[str, Any]:
    sys.path.insert(0, str(release))
    try:
        from research.research_os.control_plane import load_control_plane
        from research.research_os.legacy import LegacyKnowledgeBase
    except Exception as exc:
        raise InstallBlock(
            f"RESEARCH_OS_IMPORT_FAILED:{type(exc).__name__}:{exc}"
        ) from exc

    base = release / "research" / "research_os"
    control = load_control_plane(base)
    if control.get("status") != "PASS":
        raise InstallBlock(
            "CONTROL_PLANE_FAIL:" + ",".join(control.get("errors") or [])
        )

    authority = control.get("global_authority") or {}
    for key in AUTHORITY_KEYS:
        if authority.get(key) is not False:
            raise InstallBlock(f"CONTROL_PLANE_AUTHORITY_UNSAFE:{key}")

    knowledge = LegacyKnowledgeBase.load(base)
    summary = knowledge.summary()
    if type(summary.get("loaded_record_count")) is not int or summary["loaded_record_count"] <= 0:
        raise InstallBlock("LEGACY_KB_EMPTY_AFTER_MATERIALIZATION")

    return {
        "status": "PASS",
        "authority": {key: authority[key] for key in AUTHORITY_KEYS},
        "legacy_summary": summary,
    }


def run_verification_suite(release: Path, *, log_path: Path) -> Dict[str, Any]:
    modules = [
        "research.research_os.tests.test_implementability_depth",
        "research.research_os.tests.test_experiment_runner_frozen_protocol",
        "research.research_os.tests.test_economic_readiness_validation",
        "research.research_os.tests.test_economic_identity_portfolio_readiness",
        "research.research_os.tests.test_producer_economic_readiness",
        "research.research_os.tests.test_economic_readiness_integration",
        "research.research_os.tests.test_queue_replenisher",
        "research.research_os.tests.test_model_backend",
        "research.research_os.tests.test_oracle_worker",
    ]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    with log_path.open("w") as log:
        completed = subprocess.run(
            [sys.executable, "-m", "unittest", *modules],
            cwd=release,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if completed.returncode:
        tail = log_path.read_text(errors="replace")[-4000:]
        raise InstallBlock("RESEARCH_OS_VERIFICATION_FAILED:\n" + tail)
    return {"status": "PASS", "modules": modules, "log": str(log_path)}


def run_real_legacy_readiness_smoke(release: Path) -> Dict[str, Any]:
    sys.path.insert(0, str(release))
    from research.research_os.expansion.economic_test_readiness_v1 import (
        AUTHORITY,
        READY,
        economic_test_readiness,
    )
    from research.research_os.legacy import LegacyKnowledgeBase
    from research.research_os.tests.test_economic_readiness_integration import fixture

    base = release / "research" / "research_os"
    knowledge = LegacyKnowledgeBase.load(base)
    result = economic_test_readiness(fixture(), legacy=knowledge)
    if result.get("status") != READY:
        raise InstallBlock(
            "REAL_LEGACY_READINESS_SMOKE_BLOCKED:"
            + ",".join(result.get("block_reasons") or [])
        )
    if result.get("authority") != AUTHORITY:
        raise InstallBlock("READINESS_AUTHORITY_MISMATCH")
    if result.get("outcome_accessed") is not False:
        raise InstallBlock("READINESS_OUTCOME_ACCESS_UNSAFE")
    if result.get("economic_result") != "NOT_OBSERVED":
        raise InstallBlock("READINESS_ECONOMIC_RESULT_UNSAFE")
    return {
        "status": result["status"],
        "outcome_accessed": False,
        "economic_result": "NOT_OBSERVED",
        "authority": result["authority"],
    }


def _safe_extract_tar(data: bytes, destination: Path, sha: str) -> Path:
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        archive.extractall(destination, filter="data")
    source = destination / f"Quant-Trade-{sha}"
    if not source.is_dir():
        raise InstallBlock("RELEASE_ARCHIVE_LAYOUT_UNEXPECTED")
    return source


def _validate_release_receipt(receipt: Any, sha: str) -> Dict[str, Any]:
    if not isinstance(receipt, dict):
        raise InstallBlock("RELEASE_RECEIPT_NOT_OBJECT")
    if receipt.get("sha") != sha:
        raise InstallBlock("RELEASE_RECEIPT_SHA_MISMATCH")
    if receipt.get("status") != "INSTALLED_VERIFIED_NO_SCHEDULER":
        raise InstallBlock("RELEASE_RECEIPT_STATUS_INVALID")
    if receipt.get("scheduler_started") is not False:
        raise InstallBlock("RELEASE_RECEIPT_SCHEDULER_UNSAFE")
    if receipt.get("outcome_accessed") is not False:
        raise InstallBlock("RELEASE_RECEIPT_OUTCOME_UNSAFE")
    authority = receipt.get("authority") or {}
    for key in AUTHORITY_KEYS:
        if authority.get(key) is not False:
            raise InstallBlock(f"RELEASE_RECEIPT_AUTHORITY_UNSAFE:{key}")
    legacy = receipt.get("legacy") or {}
    if type(legacy.get("loaded_record_count")) is not int or legacy["loaded_record_count"] <= 0:
        raise InstallBlock("RELEASE_RECEIPT_LEGACY_EMPTY")
    if not SHA_RE.fullmatch(str(legacy.get("ledger_blob_sha") or "")):
        raise InstallBlock("RELEASE_RECEIPT_LEGACY_BLOB_INVALID")
    return receipt


def _recover_existing_release(release: Path, receipt_path: Path, sha: str) -> Dict[str, Any]:
    local_path = release / LOCAL_RECEIPT
    if not local_path.is_file():
        raise InstallBlock("EXISTING_RELEASE_WITHOUT_LOCAL_RECEIPT")
    try:
        local = json.loads(local_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallBlock(f"EXISTING_LOCAL_RECEIPT_INVALID:{exc}") from exc
    local = _validate_release_receipt(local, sha)

    # The release-local receipt is written before the directory is atomically
    # published. If power is lost after rename but before the global pointer is
    # updated, this safely reconstructs the pointer without reinstalling.
    if receipt_path.is_file():
        try:
            current = json.loads(receipt_path.read_text())
        except (OSError, json.JSONDecodeError):
            current = None
        if isinstance(current, dict) and current.get("sha") == sha:
            _validate_release_receipt(current, sha)
            return current
    _atomic_json(receipt_path, local)
    return local


def install_release(sha: str, *, base: Path) -> Dict[str, Any]:
    sha = validate_sha(sha)
    if sys.version_info < (3, 12):
        raise InstallBlock("PYTHON_3_12_REQUIRED")

    base.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (base / "install.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise InstallBlock("INSTALL_ALREADY_RUNNING") from exc

        release = base / sha
        receipt_path = base / "installed.json"
        if release.exists():
            return _recover_existing_release(release, receipt_path, sha)

        archive_url = f"https://codeload.github.com/{REPOSITORY}/tar.gz/{sha}"
        archive = fetch_bytes(archive_url, max_bytes=MAX_ARCHIVE_BYTES)
        log_path = base / f"verification-{sha}.log"

        with tempfile.TemporaryDirectory(prefix=".install-", dir=base) as tmp_name:
            source = _safe_extract_tar(archive, Path(tmp_name), sha)
            legacy = materialize_legacy(source)
            control = verify_control_plane(source)
            verification = run_verification_suite(source, log_path=log_path)
            smoke = run_real_legacy_readiness_smoke(source)

            receipt = {
                "status": "INSTALLED_VERIFIED_NO_SCHEDULER",
                "sha": sha,
                "path": str(release),
                "python": platform.python_version(),
                "architecture": platform.machine(),
                "legacy": legacy,
                "control_plane": control,
                "verification": verification,
                "readiness_smoke": smoke,
                "outcome_accessed": False,
                "scheduler_started": False,
                "authority": {key: False for key in AUTHORITY_KEYS},
            }
            _validate_release_receipt(receipt, sha)
            _atomic_json(source / LOCAL_RECEIPT, receipt)
            source.rename(release)

        _atomic_json(receipt_path, receipt)
        return receipt


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--sha", required=True, help="Exact 40-hex Git commit to install")
    parser.add_argument(
        "--base",
        default=str(Path.home() / "Quant-Trade-qualified"),
        help="Content-addressed release root",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    result = install_release(args.sha, base=Path(args.base).expanduser())
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (InstallBlock, OSError, ValueError, KeyError, AssertionError) as exc:
        raise SystemExit("BLOCK_INSTALLATION: " + str(exc))
