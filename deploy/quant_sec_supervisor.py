#!/usr/bin/env python3
"""External SEC supervisor with conservative, positively-attested lifecycle causes.

A replacement supervisor never infers an automatic cause from elapsed time,
kernel boot id, PID, INVOCATION_ID, or prior state. Those are observations, not
authority. The only automatic restart classified here is a child failure that
*this continuously-running supervisor* directly witnesses and restarts.

A deployment start has a separate, one-use durable authority created explicitly
with --authorize-deployment. Without that authority, every replacement
supervisor defaults to MANUAL_START, which invalidates an observation window.
No command in this file declares t0.
"""
from __future__ import annotations

import argparse
import ctypes
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

RESTART_DELAY_SECONDS = 15.0
RESTART_BURST_LIMIT = 5
RESTART_BURST_WINDOW_SECONDS = 600.0
SERVICE_NAME = "quant-sec-capture.service"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def supervisor_state_path(root: Path) -> Path:
    return Path(root) / "var" / "sec" / "supervisor_state.json"


def _authority_path(root: Path) -> Path:
    return Path(root) / "var" / "sec" / "deployment_authority.json"


def read_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {"state_invalid": True}
    except (OSError, json.JSONDecodeError):
        return {"state_invalid": True}


def write_state(path: Path, payload: dict) -> None:
    from quant.state import write_json
    write_json(path, payload)


def current_fingerprint(root: Path, environ: dict) -> str | None:
    try:
        from quant.dataplane.sec.fingerprint import acquisition_critical_fingerprint
        from quant.dataplane.sec.policy import policy_from_environment
        return acquisition_critical_fingerprint(
            policy_from_environment(environ), root=root, environ=environ)
    except Exception:
        return None


def classify(previous: dict, fingerprint: str | None, *, manual: bool,
             service_managed: bool, invocation_id: str | None,
             boot_id: str | None = None, now: datetime | None = None,
             authorized_deployment: bool = False) -> str:
    """Classify a *replacement supervisor*.

    Compatibility parameters remain because tests and diagnostics call this
    function directly. None of the heuristic inputs can authorize an automatic
    cause. A one-use deployment authority can; everything else is manual.
    """
    from quant.dataplane.sec.supervisor import DEPLOYMENT_RESTART, MANUAL_START
    return DEPLOYMENT_RESTART if authorized_deployment else MANUAL_START


def _repo_commit(root: Path) -> str:
    from quant.dataplane.sec.version import git_commit
    return git_commit(root)


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def attest_effective_unit(root: Path) -> str:
    """Bind the real installed systemd unit, not only the repository copy.

    Drop-ins are refused before t0. The installed FragmentPath must be byte-for-
    byte equal to the reviewed unit in the repository. The effective properties
    are then hashed and exported into the runtime fingerprint.
    """
    completed = subprocess.run(
        ["/usr/bin/systemctl", "show", SERVICE_NAME, "--no-pager",
         "--property=FragmentPath,DropInPaths,ExecStart,WorkingDirectory,Restart,"
         "KillMode,KillSignal,TimeoutStopUSec,EnvironmentFiles"],
        capture_output=True, text=True, timeout=10)
    if completed.returncode != 0:
        raise RuntimeError("SYSTEMD_UNIT_UNATTESTED")
    values = {}
    for line in completed.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    fragment = values.get("FragmentPath")
    if not fragment:
        raise RuntimeError("SYSTEMD_FRAGMENT_PATH_MISSING")
    installed = Path(fragment)
    reviewed = root / "deploy" / "quant-sec-capture.service"
    if not installed.exists() or not reviewed.exists() or _sha256(installed) != _sha256(reviewed):
        raise RuntimeError("SYSTEMD_UNIT_DIFFERS_FROM_REVIEWED")
    if values.get("DropInPaths"):
        raise RuntimeError("SYSTEMD_DROPINS_NOT_FROZEN")
    expected_exec = (
        f"/usr/bin/python3 {root}/deploy/quant_sec_supervisor.py "
        f"--root {root} --qualifying")
    if values.get("WorkingDirectory") != str(root):
        raise RuntimeError("SYSTEMD_WORKING_DIRECTORY_MISMATCH")
    if expected_exec not in (values.get("ExecStart") or ""):
        raise RuntimeError("SYSTEMD_EXECSTART_MISMATCH")
    if values.get("Restart") != "no" or values.get("KillMode") != "control-group":
        raise RuntimeError("SYSTEMD_EFFECTIVE_RESTART_POLICY_MISMATCH")
    canonical = json.dumps(values, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def _write_authority(root: Path) -> dict:
    """Create one explicit deployment-start authority. Never overwrite."""
    from quant.state import write_json_exclusive
    from quant.dataplane.sec.supervisor import host_boot_id
    payload = {
        "schema": "p0_deployment_authority/v1",
        "nonce": uuid.uuid4().hex,
        "cause": "DEPLOYMENT_RESTART",
        "git_commit": _repo_commit(root),
        "host_boot_id": host_boot_id(),
        "authorized_at_utc": utc_now(),
    }
    write_json_exclusive(_authority_path(root), payload)
    return payload


def _consume_authority(root: Path) -> dict | None:
    """Consume an authority exactly once, before a child can be launched."""
    from quant.state import append_jsonl, fsync_directory
    from quant.dataplane.sec.supervisor import host_boot_id
    path = _authority_path(root)
    if not path.exists():
        return None
    value = read_state(path)
    ledger = root / "var" / "sec" / "deployment_authorities.jsonl"
    used = {row.get("nonce") for row in __import__(
        "quant.state", fromlist=["read_jsonl"]).read_jsonl(ledger)}
    try:
        age = (datetime.now(timezone.utc) -
               datetime.fromisoformat(value["authorized_at_utc"])).total_seconds()
        valid = (
            value["schema"] == "p0_deployment_authority/v1"
            and value["cause"] == "DEPLOYMENT_RESTART"
            and value["git_commit"] == _repo_commit(root)
            and value["host_boot_id"] == host_boot_id()
            and value["nonce"] not in used
            and 0 <= age <= 3600
        )
    except (KeyError, TypeError, ValueError):
        valid = False
    if not valid:
        raise RuntimeError("DEPLOYMENT_AUTHORITY_INVALID")
    append_jsonl(ledger, {**value, "consumed_at_utc": utc_now()})
    path.unlink()
    fsync_directory(path.parent)
    return value


def materialize_if_absent(root: Path, environment: dict) -> str | None:
    """Materialize once; validate any existing manifest rather than repairing it."""
    fingerprint_file = root / "var" / "sec" / "acquisition_fingerprint.json"
    command = [sys.executable, "-s", str(root / "scripts" / "quant.py"),
               "sec-fingerprint", "--root", str(root)]
    completed = subprocess.run(command, env=environment, cwd=str(root),
                               capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError("FINGERPRINT_MATERIALIZATION_FAILED")
    try:
        return json.loads(fingerprint_file.read_text(encoding="utf-8"))[
            "acquisition_critical_fingerprint"]
    except (OSError, json.JSONDecodeError, KeyError):
        raise RuntimeError("FINGERPRINT_MATERIALIZATION_INVALID") from None


def _child_environment(args: argparse.Namespace, root: Path,
                       effective_unit_digest: str) -> tuple[dict, float]:
    from quant.dataplane.sec.policy import policy_from_environment
    poll_seconds = args.poll_seconds
    if poll_seconds is None:
        poll_seconds = policy_from_environment().discovery_poll_seconds
    environment = dict(os.environ)
    for name in ("PYTHONSTARTUP", "PYTHONINSPECT", "PYTHONHOME"):
        environment.pop(name, None)
    environment.update({
        "PYTHONPATH": str(root / "src"),
        "QUANT_SEC_SERVICE_POLL_SECONDS": str(poll_seconds),
        "QUANT_SEC_SERVICE_MAX_WAITS": "" if args.max_waits is None else str(args.max_waits),
        "QUANT_SEC_SERVICE_RESTART_DELAY_SECONDS": str(RESTART_DELAY_SECONDS),
        "QUANT_SEC_SERVICE_RESTART_BURST_LIMIT": str(RESTART_BURST_LIMIT),
        "QUANT_SEC_QUALIFYING_MODE": "1" if args.qualifying else "0",
        "QUANT_SEC_EFFECTIVE_UNIT_DIGEST": effective_unit_digest,
    })
    return environment, poll_seconds


def _arm_parent_death_signal() -> None:
    """Linux: kill the acquisition child if its attesting supervisor disappears."""
    parent = os.getppid()
    libc = ctypes.CDLL(None, use_errno=True)
    # PR_SET_PDEATHSIG = 1. The supervisor is single-threaded before Popen, so
    # this deliberately-small preexec hook is safe for this dedicated process.
    if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))
    # Close the race where the parent died between fork() and prctl().
    if os.getppid() != parent or parent == 1:
        os.kill(os.getpid(), signal.SIGKILL)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--qualifying", action="store_true")
    parser.add_argument("--manual", action="store_true")
    parser.add_argument("--max-restarts", type=int)
    parser.add_argument("--poll-seconds", type=float)
    parser.add_argument("--max-waits", type=int)
    parser.add_argument("--authorize-deployment", action="store_true",
                        help="create one-use deployment authority; does not start t0")
    args = parser.parse_args()
    root = args.root.resolve()

    area = root / "var" / "sec"
    area.mkdir(parents=True, exist_ok=True)
    lock_fd = os.open(area / "supervisor.lock", os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(lock_fd)
        print("[supervisor] ALREADY_RUNNING", flush=True)
        return 2

    child: subprocess.Popen | None = None
    stopping = False
    handlers = {}
    state_path = supervisor_state_path(root)
    try:
        if args.authorize_deployment:
            if args.qualifying or args.manual or args.max_restarts is not None:
                print("[supervisor] invalid deployment-authority invocation", flush=True)
                return 2
            payload = _write_authority(root)
            print(f"[supervisor] deployment authority {payload['nonce'][:12]} recorded",
                  flush=True)
            return 0

        from quant.dataplane.sec.supervisor import (
            AUTOMATIC_RESTART_AFTER_FAILURE, DEPLOYMENT_RESTART, MANUAL_START,
            host_boot_id, service_manager_provenance)

        managed = service_manager_provenance(os.environ)
        if args.qualifying:
            refused = [name for name, value in (
                ("--poll-seconds", args.poll_seconds), ("--max-waits", args.max_waits),
                ("--max-restarts", args.max_restarts)) if value is not None]
            if refused or args.manual:
                print("[supervisor] QUALIFYING_OVERRIDE_REFUSED", flush=True)
                return 2
            if not managed["service_managed"]:
                print("[supervisor] SERVICE_MANAGER_UNATTESTED", flush=True)
                return 2
            effective_unit_digest = attest_effective_unit(root)
        else:
            effective_unit_digest = "UNATTESTED"

        environment, poll_seconds = _child_environment(args, root, effective_unit_digest)
        fingerprint = current_fingerprint(root, environment)
        if fingerprint is None:
            raise RuntimeError("ACTIVE_FINGERPRINT_UNAVAILABLE")

        previous = read_state(state_path)
        if previous.get("state_invalid"):
            from quant.state import append_jsonl
            append_jsonl(area / "supervisor_faults.jsonl", {
                "event": "SUPERVISOR_STATE_INVALID", "recorded_at_utc": utc_now()})
        authority = _consume_authority(root)
        cause = classify(previous, fingerprint, manual=args.manual,
                         service_managed=managed["service_managed"],
                         invocation_id=managed["invocation_id"],
                         boot_id=host_boot_id(),
                         authorized_deployment=authority is not None)
        if cause == DEPLOYMENT_RESTART and authority is None:
            raise RuntimeError("DEPLOYMENT_CAUSE_WITHOUT_AUTHORITY")
        if args.qualifying and cause == MANUAL_START:
            # It may run to collect, but can never be "ready" for a qualifying
            # window. The lifecycle journal will carry the invalidating cause.
            pass

        supervisor_id = uuid.uuid4().hex
        kernel_boot_id = host_boot_id()
        restart_times: list[float] = []
        launches = 0

        def stop(_signum, _frame):
            nonlocal stopping
            stopping = True
            if child is not None and child.poll() is None:
                try:
                    os.killpg(child.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass

        for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            handlers[sig] = signal.signal(sig, stop)

        while not stopping:
            child_boot_id = uuid.uuid4().hex[:16]
            boot_at = utc_now()
            environment.update({
                "QUANT_SEC_BOOT_ID": child_boot_id,
                "QUANT_SEC_LIFECYCLE_CAUSE": cause,
                "QUANT_SEC_BOOT_AT_UTC": boot_at,
                "QUANT_SEC_SUPERVISOR_ID": supervisor_id,
            })
            write_state(state_path, {
                "schema": "p0_supervisor/v2",
                "supervisor_id": supervisor_id,
                "supervisor_pid": os.getpid(),
                "supervisor_invocation_id": managed["invocation_id"],
                "supervisor_running": True,
                "child_boot_id": child_boot_id,
                "boot_id": child_boot_id,
                "host_boot_id": kernel_boot_id,
                "lifecycle_cause": cause,
                "boot_at_utc": boot_at,
                "fingerprint": fingerprint,
                "last_child_exit_code": None,
                "service_managed": managed["service_managed"],
                "qualifying_mode": bool(args.qualifying),
                "effective_poll_seconds": poll_seconds,
                "effective_max_waits": args.max_waits,
                "effective_unit_digest": effective_unit_digest,
                "launch_authority_nonce": authority.get("nonce") if authority else None,
            })

            materialized = materialize_if_absent(root, environment)
            if materialized != fingerprint:
                raise RuntimeError("MATERIALIZED_FINGERPRINT_NOT_ACTIVE")

            command = [sys.executable, "-s", str(root / "scripts" / "quant.py"),
                       "sec-serve", "--root", str(root),
                       "--poll-seconds", str(poll_seconds)]
            if args.max_waits is not None:
                command += ["--max-waits", str(args.max_waits)]
            child = subprocess.Popen(command, env=environment, cwd=str(root),
                                     start_new_session=True,
                                     preexec_fn=_arm_parent_death_signal)
            launches += 1
            while child.poll() is None:
                try:
                    child.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    if not stopping:
                        continue
                    try:
                        child.wait(timeout=25)
                    except subprocess.TimeoutExpired:
                        try:
                            os.killpg(child.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        child.wait()
            exit_code = child.returncode
            state = read_state(state_path)
            state["last_child_exit_code"] = exit_code
            state["last_child_exit_at_utc"] = utc_now()
            write_state(state_path, state)

            if stopping:
                return 0
            if exit_code == 0:
                return 0
            if args.max_restarts is not None and launches >= args.max_restarts:
                return exit_code

            now = time.monotonic()
            restart_times = [stamp for stamp in restart_times
                             if now - stamp < RESTART_BURST_WINDOW_SECONDS]
            if len(restart_times) >= RESTART_BURST_LIMIT:
                return exit_code
            restart_times.append(now)
            end = now + RESTART_DELAY_SECONDS
            while not stopping and time.monotonic() < end:
                time.sleep(min(0.2, end - time.monotonic()))
            # Positive proof: this exact supervisor observed this child's failure.
            cause = AUTOMATIC_RESTART_AFTER_FAILURE
            authority = None
        return 0
    except Exception as exc:
        try:
            from quant.state import write_json
            write_json(area / "supervisor_fault.json", {
                "state": "BLOCKED", "error_class": type(exc).__name__,
                "recorded_at_utc": utc_now()})
        except OSError:
            pass
        print("[supervisor] BLOCKED " + type(exc).__name__, flush=True)
        return 2
    finally:
        if child is not None and child.poll() is None:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            child.wait()
        for sig, handler in handlers.items():
            signal.signal(sig, handler)
        state = read_state(state_path)
        if state and not state.get("state_invalid"):
            state["supervisor_running"] = False
            state["supervisor_exited_at_utc"] = utc_now()
            try:
                write_state(state_path, state)
            except OSError:
                pass
        os.close(lock_fd)


if __name__ == "__main__":
    raise SystemExit(main())
