#!/usr/bin/env python3
"""Install/enable the non-authoritative Oracle V2 -> Live Lab emitter.

This helper never creates or rotates the ingress secret. It only validates a
root-owned secret file already provisioned out-of-band, verifies the exact V2
release contains the audited bridge, installs the emitter unit, and enables it.
The scientific worker never receives the Site secret.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import pwd
import re
import stat
import subprocess

from deploy.oracle_release_install import _validate_release_receipt, validate_sha

SITE_URL = "https://quant-trade-lab.sassylime.chatgpt.site"
PRINCIPAL = "oracle-research-live"
V2_PREFIX = "oracle-research-v2."
ENV_FILE = Path("/etc/quant-research/worker.env")
CURRENT = Path("/opt/quant-research-v2/current")
EMITTER_UNIT = "quant-live-lab-emitter-v2.service"
WORKER_UNIT = "quant-research-worker-v2.service"
SYSTEMD_DIR = Path("/etc/systemd/system")
OUTBOX = Path("/var/lib/quant-research-v2/live-lab-outbox")
REQUIRED_ENV = (
    "QT_ORACLE_SITE_BASE_URL",
    "QT_ORACLE_INGRESS_KEY",
    "QT_ORACLE_PRINCIPAL",
    "QT_ORACLE_SITE_WORKER_PREFIX",
)
SAFE_SECRET = re.compile(r"^[!-~]{32,512}$")


def checked(argv: list[str]) -> str:
    result = subprocess.run(argv, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            raise ValueError("LIVE_LAB_ENV_LINE_INVALID")
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if value[:1] == value[-1:] and value[:1] in ("'", '"'):
            value = value[1:-1]
        if key in values:
            raise ValueError("LIVE_LAB_ENV_DUPLICATE_KEY:" + key)
        values[key] = value
    missing = [key for key in REQUIRED_ENV if not values.get(key)]
    if missing:
        raise ValueError("LIVE_LAB_ENV_MISSING:" + ",".join(missing))
    return values


def validate_secret_file(path: Path) -> dict[str, str]:
    if not path.is_file() or path.is_symlink():
        raise ValueError("LIVE_LAB_ENV_MUST_BE_REGULAR_FILE")
    info = path.stat()
    quant = pwd.getpwnam("quant-research")
    if info.st_uid != 0 or info.st_gid != quant.pw_gid:
        raise ValueError("LIVE_LAB_ENV_OWNER_MUST_BE_ROOT_QUANT_RESEARCH")
    if stat.S_IMODE(info.st_mode) != 0o640:
        raise ValueError("LIVE_LAB_ENV_MODE_MUST_BE_0640")
    values = parse_env(path)
    if values["QT_ORACLE_SITE_BASE_URL"].rstrip("/") != SITE_URL:
        raise ValueError("LIVE_LAB_SITE_URL_MISMATCH")
    if values["QT_ORACLE_PRINCIPAL"] != PRINCIPAL:
        raise ValueError("LIVE_LAB_PRINCIPAL_MISMATCH")
    if values["QT_ORACLE_SITE_WORKER_PREFIX"] != V2_PREFIX:
        raise ValueError("LIVE_LAB_SITE_PREFIX_MUST_ACCEPT_REAL_V2_IDENTITY")
    if not SAFE_SECRET.fullmatch(values["QT_ORACLE_INGRESS_KEY"]):
        raise ValueError("LIVE_LAB_SECRET_FORMAT_INVALID")
    return values


def validate_release(expected_sha: str) -> Path:
    sha = validate_sha(expected_sha)
    if not CURRENT.is_symlink():
        raise ValueError("V2_CURRENT_RELEASE_SYMLINK_REQUIRED")
    release = CURRENT.resolve()
    if release.name != sha:
        raise ValueError("V2_CURRENT_RELEASE_SHA_MISMATCH")
    receipt_path = release / ".quant_release_receipt.json"
    receipt = _validate_release_receipt(json.loads(receipt_path.read_text()), sha)
    if Path(receipt["path"]).resolve() != release:
        raise ValueError("V2_RELEASE_RECEIPT_PATH_MISMATCH")
    required = (
        "research/research_os/live_lab_contract.py",
        "research/research_os/live_lab_bridge.py",
        "research/research_os/live_lab_emitter.py",
        "research/research_os/oracle_worker_v2_live.py",
        "deploy/systemd/quant-live-lab-emitter-v2.service",
        "deploy/systemd/quant-research-worker-v2.service",
    )
    for rel in required:
        if not (release / rel).is_file():
            raise ValueError("LIVE_LAB_BRIDGE_RELEASE_FILE_MISSING:" + rel)
    worker = (release / "deploy/systemd" / WORKER_UNIT).read_text()
    emitter = (release / "deploy/systemd" / EMITTER_UNIT).read_text()
    if "oracle_worker_v2_live" not in worker:
        raise ValueError("V2_WORKER_NOT_USING_OUTBOX_ENTRYPOINT")
    if "EnvironmentFile=" in worker or "QT_ORACLE_INGRESS_KEY" in worker:
        raise ValueError("SCIENTIFIC_WORKER_MUST_NOT_RECEIVE_SITE_SECRET")
    if "EnvironmentFile=/etc/quant-research/worker.env" not in emitter:
        raise ValueError("LIVE_LAB_EMITTER_ENV_FILE_NOT_PINNED")
    if "research.research_os.live_lab_emitter" not in emitter:
        raise ValueError("LIVE_LAB_EMITTER_ENTRYPOINT_MISSING")
    return release


def atomic_write(path: Path, data: bytes, mode: int = 0o644) -> None:
    temp = path.with_name("." + path.name + ".tmp")
    fd = os.open(temp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, mode)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp, mode)
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def install(expected_sha: str, *, enable: bool) -> dict[str, object]:
    if os.geteuid() != 0:
        raise ValueError("ROOT_REQUIRED_FOR_LIVE_LAB_BRIDGE_INSTALL")
    release = validate_release(expected_sha)
    env = validate_secret_file(ENV_FILE)
    quant = pwd.getpwnam("quant-research")
    OUTBOX.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chown(OUTBOX, quant.pw_uid, quant.pw_gid)
    os.chmod(OUTBOX, 0o700)

    emitter_source = release / "deploy/systemd" / EMITTER_UNIT
    target = SYSTEMD_DIR / EMITTER_UNIT
    atomic_write(target, emitter_source.read_bytes())
    checked(["systemd-analyze", "verify", str(target), str(SYSTEMD_DIR / WORKER_UNIT)])
    checked(["systemctl", "daemon-reload"])
    checked(["systemctl", "disable", "--now", EMITTER_UNIT])
    if enable:
        checked(["systemctl", "enable", "--now", EMITTER_UNIT])
        if checked(["systemctl", "is-active", EMITTER_UNIT]) != "active":
            raise ValueError("LIVE_LAB_EMITTER_NOT_ACTIVE_AFTER_ENABLE")
    return {
        "status": "LIVE_LAB_BRIDGE_ENABLED" if enable else "LIVE_LAB_BRIDGE_VALIDATED_DISABLED",
        "release_sha": release.name,
        "site_url": env["QT_ORACLE_SITE_BASE_URL"],
        "principal": env["QT_ORACLE_PRINCIPAL"],
        "worker_prefix": env["QT_ORACLE_SITE_WORKER_PREFIX"],
        "secret_present": True,
        "secret_value_exposed": False,
        "scientific_worker_receives_site_secret": False,
        "emitter_enabled": enable,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-sha", required=True)
    parser.add_argument("--enable", action="store_true")
    args = parser.parse_args()
    print(json.dumps(install(args.release_sha, enable=args.enable), sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, sort_keys=True))
        raise SystemExit(1)
