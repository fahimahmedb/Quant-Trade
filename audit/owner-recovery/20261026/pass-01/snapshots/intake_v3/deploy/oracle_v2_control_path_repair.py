#!/usr/bin/env python3
"""Repair only the three fixed root wrapper environments; preserve V1 and V2 releases."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

QUALIFIED_SHA = "a67ffec48fff895d5edc42171855e2213e49cf0d"
ROOT_PATH = "/usr/sbin:/usr/bin:/sbin:/bin"
ACTIONS = ("qualify", "activate", "status")


def repaired_bytes(original):
    if original.count(b"PATH=/usr/bin:/bin") != 1:
        raise ValueError("ORIGINAL_BOUNDED_WRAPPER_TEMPLATE_REQUIRED")
    return original.replace(b"PATH=/usr/bin:/bin", ("PATH=" + ROOT_PATH).encode())


def main():
    if os.geteuid() != 0:
        raise ValueError("ROOT_REQUIRED_TO_REPAIR_ROOT_WRAPPER_ENVIRONMENT")
    release = Path("/opt/quant-research/releases") / QUALIFIED_SHA
    sys.path.insert(0, str(release))
    from deploy.oracle_v1_host_prepare import wrapper, write_atomic
    from deploy.oracle_v2_deploy import CONFIG, CURRENT, TIMER, SERVICE, V1_TIMER, active, validate_config, verify_ci
    import fcntl
    control_lock = Path("/run/quant-research-v2-control")
    control_lock.mkdir(mode=0o700, exist_ok=True)
    fd = os.open(control_lock, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        config = json.loads(CONFIG.read_text())
        if validate_config(config) != release or CURRENT.resolve() != release:
            raise ValueError("QUALIFIED_A67FFEC_RELEASE_REQUIRED")
        verify_ci(config)
        if active(V1_TIMER) != "active" or any(active(u) in ("active", "activating", "reloading") for u in (TIMER, SERVICE)):
            raise ValueError("V1_RUNNING_V2_QUIESCED_REQUIRED")
        if shutil.which("runuser", path=ROOT_PATH) != "/usr/sbin/runuser":
            raise ValueError("EXPECTED_UBUNTU_RUNUSER_NOT_FOUND")
        subprocess.run(["/usr/sbin/runuser", "--version"], check=True, capture_output=True, timeout=10)
        changes = []
        for action in ACTIONS:
            path = Path("/usr/local/libexec/quant-v2-" + action)
            original = wrapper(release, "deploy.oracle_v2_deploy", ["--action", action])
            patched = repaired_bytes(original)
            actual = path.read_bytes()
            if path.is_symlink() or path.stat().st_uid != 0 or actual not in (original, patched):
                raise ValueError("UNEXPECTED_ROOT_WRAPPER_REFUSE_OVERWRITE:" + action)
            changes.append((path, original, patched))
        # Verify all controls before the first mutation. Each replacement is
        # atomic, root-owned and idempotently resumable after interruption.
        for path, original, patched in changes:
            write_atomic(path, patched, 0o755)
        report = dict(status="V2_CONTROL_ENVIRONMENT_REPAIRED", release_sha=QUALIFIED_SHA,
                      root_control_path=ROOT_PATH, runuser="/usr/sbin/runuser",
                      wrapper_sha256={p.name: hashlib.sha256(data).hexdigest() for p, _, data in changes},
                      v1_timer=active(V1_TIMER), v2_timer=active(TIMER), private_key_exported=False,
                      release_code_modified=False, scheduler_activated=False)
        write_atomic(CONFIG.parent / "control-environment-repair.json",
                     (json.dumps(report, sort_keys=True, indent=2) + "\n").encode(), 0o600)
        print(json.dumps(report, sort_keys=True))
    finally:
        os.close(fd)


if __name__ == "__main__":
    main()
