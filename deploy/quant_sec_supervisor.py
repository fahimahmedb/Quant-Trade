#!/usr/bin/env python3
"""External supervisor for the SEC capture service.

This process exists to answer one question the collector is not allowed to
answer about itself: *why did this instance start?*

``BLUE_P0_RAW_CAPTURE_CHECKPOINT_ADDENDUM_2026-09-18.md §5.2`` makes
``MANUAL_START`` after a stop or failure an intervention that invalidates the
observation window. A process that classified its own origin would be grading
its own homework, so the classification is made here, from state this supervisor
keeps and the collector cannot reach:

* first launch of a deployment            -> ``SCHEDULED_START``
* child exited non-zero, relaunching      -> ``AUTOMATIC_RESTART_AFTER_FAILURE``
* the acquisition fingerprint changed     -> ``DEPLOYMENT_RESTART``
* a human passed ``--manual``             -> ``MANUAL_START``

The cause, a fresh boot id and the boot time are handed to the child through the
environment. The child records them verbatim and never invents them.

Restart timing is part of the acquisition fingerprint, because a supervisor that
restarts on a different schedule changes the expected acquisition timeline.

    python3 deploy/quant_sec_supervisor.py --root . [--manual] [--max-restarts N]
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

#: Restart pacing. Mirrored in the systemd unit and digested into the manifest.
RESTART_DELAY_SECONDS = 15.0
RESTART_BURST_LIMIT = 5
RESTART_BURST_WINDOW_SECONDS = 600.0


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def supervisor_state_path(root: Path) -> Path:
    return Path(root) / "var" / "sec" / "supervisor_state.json"


def read_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_state(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    os.replace(temporary, path)


def current_fingerprint(root: Path) -> str | None:
    """Read the active fingerprint, if the identity is configured."""
    try:
        from quant.dataplane.sec.fingerprint import acquisition_critical_fingerprint
        from quant.dataplane.sec.policy import policy_from_environment
        return acquisition_critical_fingerprint(policy_from_environment(), root=root)
    except Exception:
        return None


def classify(previous: dict, fingerprint: str | None, manual: bool) -> str:
    from quant.dataplane.sec.supervisor import (AUTOMATIC_RESTART_AFTER_FAILURE,
                                                DEPLOYMENT_RESTART, MANUAL_START,
                                                SCHEDULED_START)
    if manual:
        return MANUAL_START
    if not previous:
        return SCHEDULED_START
    if fingerprint and previous.get("fingerprint") and fingerprint != previous["fingerprint"]:
        return DEPLOYMENT_RESTART
    if previous.get("last_child_exit_code") not in (0, None):
        return AUTOMATIC_RESTART_AFTER_FAILURE
    return SCHEDULED_START


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manual", action="store_true",
                        help="a human is starting this; recorded as MANUAL_START")
    parser.add_argument("--max-restarts", type=int, default=None,
                        help="stop after this many child launches (testing)")
    parser.add_argument("--poll-seconds", type=float, default=60.0)
    parser.add_argument("--max-waits", type=int, default=None)
    args = parser.parse_args()

    root = args.root.resolve()
    state_path = supervisor_state_path(root)
    supervisor_id = read_state(state_path).get("supervisor_id") or uuid.uuid4().hex[:16]
    launches = 0
    restart_times: list[float] = []

    while True:
        previous = read_state(state_path)
        fingerprint = current_fingerprint(root)
        cause = classify(previous, fingerprint, args.manual and launches == 0)
        boot_id = uuid.uuid4().hex[:16]
        boot_at = utc_now()

        environment = dict(os.environ)
        environment.update({
            "QUANT_SEC_BOOT_ID": boot_id,
            "QUANT_SEC_LIFECYCLE_CAUSE": cause,
            "QUANT_SEC_BOOT_AT_UTC": boot_at,
            "QUANT_SEC_SUPERVISOR_ID": supervisor_id,
            "PYTHONPATH": str(root / "src"),
        })

        write_state(state_path, {
            "supervisor_id": supervisor_id, "boot_id": boot_id,
            "lifecycle_cause": cause, "boot_at_utc": boot_at,
            "fingerprint": fingerprint, "launches": launches + 1,
            "last_child_exit_code": None,
            "restart_delay_seconds": RESTART_DELAY_SECONDS})

        command = [sys.executable, str(root / "scripts" / "quant.py"), "sec-serve",
                   "--root", str(root), "--poll-seconds", str(args.poll_seconds)]
        if args.max_waits is not None:
            command += ["--max-waits", str(args.max_waits)]
        print(f"[supervisor] launching boot={boot_id} cause={cause}", flush=True)
        completed = subprocess.run(command, env=environment, cwd=str(root))
        launches += 1

        state = read_state(state_path)
        state["last_child_exit_code"] = completed.returncode
        state["last_child_exit_at_utc"] = utc_now()
        write_state(state_path, state)
        print(f"[supervisor] child exited {completed.returncode}", flush=True)

        if args.max_restarts is not None and launches >= args.max_restarts:
            return completed.returncode
        if completed.returncode == 0:
            return 0

        now = time.monotonic()
        restart_times = [stamp for stamp in restart_times
                         if now - stamp < RESTART_BURST_WINDOW_SECONDS]
        if len(restart_times) >= RESTART_BURST_LIMIT:
            print("[supervisor] restart burst limit reached; stopping", flush=True)
            return completed.returncode
        restart_times.append(now)
        time.sleep(RESTART_DELAY_SECONDS)


if __name__ == "__main__":
    raise SystemExit(main())
