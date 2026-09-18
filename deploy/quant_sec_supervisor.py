#!/usr/bin/env python3
"""External supervisor for the SEC capture service.

This process answers the one question the collector is not allowed to answer
about itself: *why did this instance start?*

``BLUE_P0_RAW_CAPTURE_CHECKPOINT_ADDENDUM_2026-09-18.md §5.2`` makes
``MANUAL_START`` after a stop or failure an intervention that invalidates the
observation window. Blue's review of the first version found three ways the answer
could still be wrong, each addressed here.

**Omission cannot buy a clean record.** The first version derived ``MANUAL_START``
from an ``--manual`` flag, so a human who ran the command without it was recorded
as ``SCHEDULED_START``. Now the classification starts from service-manager
provenance: without a recognised manager and its per-invocation identity, the
launch is ``MANUAL_START`` and non-qualifying, whatever flags were passed. The
``--manual`` flag remains only so an operator can be explicit; it can make a
launch manual, never scheduled.

**The supervisor's own death is visible.** Durable state records that a supervisor
is running and under which invocation identity. A new supervisor that finds a
previous one still marked running, under a different identity, reports
``AUTOMATIC_RESTART_AFTER_SUPERVISOR_FAILURE``. Previously that case read the
``last_child_exit_code = null`` written before launch and concluded
``SCHEDULED_START``.

**Effective timing is frozen or refused.** ``--poll-seconds`` changes the wake
cadence and ``--max-waits`` bounds the service lifetime, neither of which shows up
in a source-file digest. In qualifying mode both are refused: cadence comes from
the frozen policy and a qualifying service does not stop after N waits. In any
mode the effective values are exported and folded into the fingerprint manifest,
so two services from identical code with different arguments cannot share a
fingerprint.

    # qualifying service, launched by systemd (see quant-sec-capture.service)
    python3 deploy/quant_sec_supervisor.py --root /opt/quant --qualifying

    # non-qualifying local run; recorded as MANUAL_START
    python3 deploy/quant_sec_supervisor.py --root . --poll-seconds 30 --max-waits 3
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

#: Restart pacing. Mirrored in the systemd unit and bound into the manifest.
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


def current_fingerprint(root: Path, environ: dict) -> str | None:
    """Read the active fingerprint, if the identity is configured."""
    try:
        from quant.dataplane.sec.fingerprint import acquisition_critical_fingerprint
        from quant.dataplane.sec.policy import policy_from_environment
        return acquisition_critical_fingerprint(policy_from_environment(environ),
                                                root=root, environ=environ)
    except Exception:
        return None


def classify(previous: dict, fingerprint: str | None, *, manual: bool,
             service_managed: bool, invocation_id: str | None) -> str:
    """Decide why this instance is starting.

    Order matters. Anything that cannot be shown to be an automatic action by a
    real service manager falls to ``MANUAL_START``, which is the conservative
    answer because it is the one that invalidates the window.
    """
    from quant.dataplane.sec.supervisor import (
        AUTOMATIC_RESTART_AFTER_FAILURE, AUTOMATIC_RESTART_AFTER_SUPERVISOR_FAILURE,
        DEPLOYMENT_RESTART, MANUAL_START, SCHEDULED_START)
    if manual:
        return MANUAL_START
    if not service_managed:
        # No service manager launched this. Absence of provenance is never a
        # scheduled start; that inversion is the point of this function.
        return MANUAL_START
    if fingerprint and previous.get("fingerprint") and fingerprint != previous["fingerprint"]:
        return DEPLOYMENT_RESTART
    if previous.get("supervisor_running") and previous.get("supervisor_invocation_id") \
            and previous.get("supervisor_invocation_id") != invocation_id:
        # A previous supervisor was still marked running under a different
        # invocation, so it died rather than exiting cleanly.
        return AUTOMATIC_RESTART_AFTER_SUPERVISOR_FAILURE
    if previous.get("last_child_exit_code") not in (0, None):
        return AUTOMATIC_RESTART_AFTER_FAILURE
    if not previous:
        return SCHEDULED_START
    return SCHEDULED_START


class QualifyingModeViolation(SystemExit):
    """A qualifying service was asked to run with unbound acquisition timing."""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--qualifying", action="store_true",
                        help="run as the qualifying observation service; refuses "
                             "acquisition-critical overrides and requires a service manager")
    parser.add_argument("--manual", action="store_true",
                        help="a human is starting this; recorded as MANUAL_START")
    parser.add_argument("--max-restarts", type=int, default=None,
                        help="stop after this many child launches (testing only)")
    parser.add_argument("--poll-seconds", type=float, default=None,
                        help="override the wake cadence; forbidden in qualifying mode")
    parser.add_argument("--max-waits", type=int, default=None,
                        help="stop after this many idle waits; forbidden in qualifying mode")
    args = parser.parse_args()

    root = args.root.resolve()
    from quant.dataplane.sec.supervisor import service_manager_provenance

    managed = service_manager_provenance(os.environ)

    # --- qualifying-mode gate ------------------------------------------------
    if args.qualifying:
        refused = [name for name, value in (("--poll-seconds", args.poll_seconds),
                                           ("--max-waits", args.max_waits),
                                           ("--max-restarts", args.max_restarts))
                   if value is not None]
        if refused:
            print(f"[supervisor] refusing qualifying mode: acquisition-critical "
                  f"overrides not permitted: {', '.join(refused)}", flush=True)
            return 2
        if args.manual:
            print("[supervisor] refusing qualifying mode: a manual start cannot be "
                  "the qualifying observation service", flush=True)
            return 2
        if not managed["service_managed"]:
            print("[supervisor] refusing qualifying mode: no recognised service "
                  "manager provenance (needs QUANT_SEC_SERVICE_MANAGER and an "
                  "invocation identity)", flush=True)
            return 2

    # Cadence comes from the frozen policy unless explicitly overridden, which is
    # only possible outside qualifying mode.
    poll_seconds = args.poll_seconds
    if poll_seconds is None:
        try:
            from quant.dataplane.sec.policy import policy_from_environment
            poll_seconds = policy_from_environment().discovery_poll_seconds
        except Exception:
            poll_seconds = 60.0

    state_path = supervisor_state_path(root)
    supervisor_id = read_state(state_path).get("supervisor_id") or uuid.uuid4().hex[:16]
    invocation_id = managed["invocation_id"] or f"unmanaged-{uuid.uuid4().hex[:12]}"
    launches = 0
    restart_times: list[float] = []
    exit_code = 0

    try:
        while True:
            previous = read_state(state_path)
            # The effective configuration is exported before the fingerprint is
            # computed, so the fingerprint describes the service actually launched.
            environment = dict(os.environ)
            environment.update({
                "QUANT_SEC_SERVICE_POLL_SECONDS": str(poll_seconds),
                "QUANT_SEC_SERVICE_MAX_WAITS": ("" if args.max_waits is None
                                                else str(args.max_waits)),
                "QUANT_SEC_SERVICE_RESTART_DELAY_SECONDS": str(RESTART_DELAY_SECONDS),
                "QUANT_SEC_SERVICE_RESTART_BURST_LIMIT": str(RESTART_BURST_LIMIT),
                "QUANT_SEC_QUALIFYING_MODE": "1" if args.qualifying else "0",
                "PYTHONPATH": str(root / "src"),
            })
            fingerprint = current_fingerprint(root, environment)
            cause = classify(previous, fingerprint, manual=args.manual and launches == 0,
                             service_managed=managed["service_managed"],
                             invocation_id=invocation_id)
            boot_id = uuid.uuid4().hex[:16]
            boot_at = utc_now()
            environment.update({
                "QUANT_SEC_BOOT_ID": boot_id,
                "QUANT_SEC_LIFECYCLE_CAUSE": cause,
                "QUANT_SEC_BOOT_AT_UTC": boot_at,
                "QUANT_SEC_SUPERVISOR_ID": supervisor_id,
            })

            write_state(state_path, {
                "supervisor_id": supervisor_id, "boot_id": boot_id,
                "lifecycle_cause": cause, "boot_at_utc": boot_at,
                "fingerprint": fingerprint, "launches": launches + 1,
                "last_child_exit_code": None,
                # Set before the child runs and cleared only on a clean exit, so a
                # supervisor that dies leaves this true and its successor can tell.
                "supervisor_running": True,
                "supervisor_invocation_id": invocation_id,
                "service_managed": managed["service_managed"],
                "qualifying_mode": bool(args.qualifying),
                "effective_poll_seconds": poll_seconds,
                "effective_max_waits": args.max_waits,
                "restart_delay_seconds": RESTART_DELAY_SECONDS})

            command = [sys.executable, str(root / "scripts" / "quant.py"), "sec-serve",
                       "--root", str(root), "--poll-seconds", str(poll_seconds)]
            if args.max_waits is not None:
                command += ["--max-waits", str(args.max_waits)]
            print(f"[supervisor] launching boot={boot_id} cause={cause} "
                  f"qualifying={bool(args.qualifying)} managed={managed['service_managed']}",
                  flush=True)
            completed = subprocess.run(command, env=environment, cwd=str(root))
            launches += 1
            exit_code = completed.returncode

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
    finally:
        # A clean exit clears the running marker. A crash does not reach here,
        # which is exactly how the next supervisor detects the failure.
        state = read_state(state_path)
        if state:
            state["supervisor_running"] = False
            state["supervisor_exited_at_utc"] = utc_now()
            write_state(state_path, state)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
