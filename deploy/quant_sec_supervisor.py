#!/usr/bin/env python3
"""External supervisor for the SEC/Form-4 P0 acquisition service.

The collector cannot authoritatively classify why it started.  This supervisor
therefore uses a deliberately asymmetric rule:

* only the same continuously-running supervisor may attest an automatic child
  restart, because it directly observed the child exit;
* any replacement supervisor defaults to MANUAL_START;
* a deployment start/restart is non-invalidating only when a distinct durable,
  one-use authorization was written explicitly before launch.

Boot ids, invocation ids and timestamps are retained as observations.  They are
never sufficient by themselves to upgrade an otherwise invalidating start.
This file never declares t0.
"""
from __future__ import annotations

import argparse
import ctypes
import fcntl
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
DEPLOYMENT_AUTHORITY_MAX_AGE_SECONDS = 3600.0


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def supervisor_state_path(root: Path) -> Path:
    return Path(root) / "var" / "sec" / "supervisor_state.json"


def authority_path(root: Path) -> Path:
    return Path(root) / "var" / "sec" / "deployment_authority.json"


def authority_ledger_path(root: Path) -> Path:
    return Path(root) / "var" / "sec" / "deployment_authorities.jsonl"


def read_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"state_invalid": True}
    return value if isinstance(value, dict) else {"state_invalid": True}


def write_state(path: Path, payload: dict) -> None:
    """Atomic + fsynced replacement with a unique staging name."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.parent / f".{path.name}.{uuid.uuid4().hex}.tmp"
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        _fsync_dir(path.parent)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(fd, (json.dumps(payload, sort_keys=True) + "\n").encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    _fsync_dir(path.parent)


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
             deployment_authorized: bool = False,
             witnessed_child_failure: bool = False) -> str:
    """Conservative lifecycle classification.

    Compatibility parameters are retained for the test/API surface, but boot id,
    timing, prior exit fields and service-manager invocation are observations,
    not authority for an automatic cause.
    """
    from quant.dataplane.sec.supervisor import (
        AUTOMATIC_RESTART_AFTER_FAILURE, DEPLOYMENT_RESTART, MANUAL_START)
    if witnessed_child_failure:
        return AUTOMATIC_RESTART_AFTER_FAILURE
    if deployment_authorized:
        return DEPLOYMENT_RESTART
    return MANUAL_START


def _effective_systemd_definition(root: Path) -> str:
    """Digest the unit systemd actually loaded, not only the repository file."""
    import hashlib
    executable = "/bin/systemctl" if Path("/bin/systemctl").exists() else "systemctl"
    properties = (
        "FragmentPath,DropInPaths,ExecStart,WorkingDirectory,Restart,RestartUSec,"
        "StartLimitIntervalUSec,StartLimitBurst,KillMode,KillSignal,TimeoutStopUSec,"
        "EnvironmentFiles"
    )
    completed = subprocess.run(
        [executable, "show", "quant-sec-capture.service", "--no-pager",
         f"--property={properties}"],
        capture_output=True, text=True, timeout=15)
    if completed.returncode != 0:
        raise RuntimeError("SYSTEMD_EFFECTIVE_UNIT_UNAVAILABLE")
    parsed = {}
    for line in completed.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            parsed[key] = value
    fragment = Path(parsed.get("FragmentPath") or "")
    if not fragment.is_file():
        raise RuntimeError("SYSTEMD_FRAGMENT_UNAVAILABLE")
    repo_unit = root / "deploy" / "quant-sec-capture.service"
    loaded_digest = hashlib.sha256(fragment.read_bytes()).hexdigest()
    repo_digest = hashlib.sha256(repo_unit.read_bytes()).hexdigest()
    if loaded_digest != repo_digest:
        raise RuntimeError("SYSTEMD_FRAGMENT_DIFFERS_FROM_REPOSITORY")
    if (parsed.get("DropInPaths") or "").strip():
        raise RuntimeError("SYSTEMD_DROPINS_UNBOUND")
    canonical = json.dumps(parsed, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def _effective_environment(args: argparse.Namespace, root: Path,
                           managed: dict) -> tuple[dict, float]:
    from quant.dataplane.sec.policy import policy_from_environment
    source = dict(os.environ)
    # The authority command fingerprints the service it authorizes, not the
    # shell process writing the token.
    qualifying_target = bool(args.qualifying or args.authorize_deployment)
    poll_seconds = args.poll_seconds
    if poll_seconds is None:
        poll_seconds = policy_from_environment(source).discovery_poll_seconds
    effective_unit = None
    if qualifying_target:
        if not managed["service_managed"] and not args.authorize_deployment:
            raise RuntimeError("SERVICE_MANAGER_UNATTESTED")
        effective_unit = _effective_systemd_definition(root)

    # Whitelist the child's ambient environment.  Acquisition semantics must
    # not depend on unbound PYTHONPATH/sitecustomize, proxy, git, locale or
    # arbitrary operator variables inherited from the service manager.
    environment = {
        "PATH": source.get("PATH", "/usr/bin:/bin"),
        "HOME": source.get("HOME", "/"),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "QUANT_SEC_USER_AGENT": source.get("QUANT_SEC_USER_AGENT", ""),
        "QUANT_SEC_SERVICE_MANAGER": source.get("QUANT_SEC_SERVICE_MANAGER", ""),
        "INVOCATION_ID": source.get("INVOCATION_ID", ""),
    }
    environment.update({
        "QUANT_SEC_SERVICE_POLL_SECONDS": str(poll_seconds),
        "QUANT_SEC_SERVICE_MAX_WAITS": (
            "" if args.max_waits is None else str(args.max_waits)),
        "QUANT_SEC_SERVICE_RESTART_DELAY_SECONDS": str(RESTART_DELAY_SECONDS),
        "QUANT_SEC_SERVICE_RESTART_BURST_LIMIT": str(RESTART_BURST_LIMIT),
        "QUANT_SEC_QUALIFYING_MODE": "1" if qualifying_target else "0",
        "QUANT_SEC_EFFECTIVE_UNIT_DIGEST": effective_unit or "UNATTESTED",
    })
    return environment, poll_seconds


def _write_deployment_authority(root: Path, fingerprint: str | None) -> dict:
    """Create, never replace, a one-use deployment authority."""
    if not fingerprint:
        raise RuntimeError("ACQUISITION_FINGERPRINT_UNAVAILABLE")
    from quant.dataplane.sec.supervisor import host_boot_id
    path = authority_path(root)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    payload = {
        "schema": "p0_deployment_authority/v1",
        "nonce": uuid.uuid4().hex,
        "cause": "DEPLOYMENT_RESTART",
        "acquisition_critical_fingerprint": fingerprint,
        "host_boot_id": host_boot_id(),
        "authorized_at_utc": utc_now(),
    }
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(fd, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    _fsync_dir(path.parent)
    return payload


def _consume_deployment_authority(root: Path, fingerprint: str | None) -> dict | None:
    """Validate and consume the external deployment authority exactly once."""
    from quant.dataplane.sec.supervisor import host_boot_id
    path = authority_path(root)
    if not path.exists():
        return None
    value = read_state(path)
    try:
        stamp = datetime.fromisoformat(value["authorized_at_utc"])
        if stamp.tzinfo is None:
            raise ValueError("naive authority time")
        age = (datetime.now(timezone.utc) - stamp).total_seconds()
        valid = (
            value["schema"] == "p0_deployment_authority/v1"
            and value["cause"] == "DEPLOYMENT_RESTART"
            and value["acquisition_critical_fingerprint"] == fingerprint
            and value.get("host_boot_id") == host_boot_id()
            and bool(value["nonce"])
            and 0 <= age <= DEPLOYMENT_AUTHORITY_MAX_AGE_SECONDS
        )
    except (KeyError, TypeError, ValueError):
        valid = False
    if not valid:
        raise RuntimeError("DEPLOYMENT_AUTHORITY_INVALID")
    _append_jsonl(authority_ledger_path(root),
                  {**value, "consumed_at_utc": utc_now()})
    path.unlink()
    _fsync_dir(path.parent)
    return value


def materialize_if_absent(root: Path, environment: dict) -> str | None:
    """Create the freeze once or validate the existing freeze before launch."""
    fingerprint_file = Path(root) / "var" / "sec" / "acquisition_fingerprint.json"
    active = current_fingerprint(root, environment)
    completed = subprocess.run(
        [sys.executable, "-I", str(Path(root) / "scripts" / "quant.py"),
         "sec-fingerprint", "--root", str(root)],
        env=environment, cwd=str(root), capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError("FINGERPRINT_MATERIALIZATION_OR_VALIDATION_FAILED")
    try:
        stored = json.loads(fingerprint_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise RuntimeError("FINGERPRINT_MATERIALIZATION_INVALID") from None
    if stored.get("acquisition_critical_fingerprint") != active:
        raise RuntimeError("FINGERPRINT_MATERIALIZED_MISMATCH")
    return active


def _child_parent_death_guard() -> None:
    """Linux child invariant: no collector may outlive its supervisor."""
    libc = ctypes.CDLL(None, use_errno=True)
    parent = os.getppid()
    PR_SET_PDEATHSIG = 1
    if libc.prctl(PR_SET_PDEATHSIG, signal.SIGKILL) != 0:
        os._exit(125)
    # Parent could have died between fork and prctl.
    if parent == 1 or os.getppid() != parent:
        os._exit(125)


def _terminate_group(child: subprocess.Popen, sig: int) -> None:
    if child.poll() is not None:
        return
    try:
        os.killpg(child.pid, sig)
    except ProcessLookupError:
        return


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--qualifying", action="store_true")
    parser.add_argument("--manual", action="store_true",
                        help="compatibility flag; can only make a start invalidating")
    parser.add_argument("--max-restarts", type=int, default=None)
    parser.add_argument("--poll-seconds", type=float, default=None)
    parser.add_argument("--max-waits", type=int, default=None)
    parser.add_argument("--authorize-deployment", action="store_true",
                        help="write a one-use deployment/start authority; does not start t0")
    args = parser.parse_args()
    root = args.root.resolve()

    from quant.dataplane.sec.supervisor import host_boot_id, service_manager_provenance

    managed = service_manager_provenance(os.environ)
    if args.qualifying or args.authorize_deployment:
        refused = [name for name, value in (
            ("--poll-seconds", args.poll_seconds),
            ("--max-waits", args.max_waits),
            ("--max-restarts", args.max_restarts),
        ) if value is not None]
        if refused:
            print("[supervisor] QUALIFYING_OVERRIDE_REFUSED", flush=True)
            return 2
        if args.manual:
            print("[supervisor] QUALIFYING_MANUAL_OVERRIDE_REFUSED", flush=True)
            return 2
        if not managed["service_managed"] and not args.authorize_deployment:
            print("[supervisor] SERVICE_MANAGER_UNATTESTED", flush=True)
            return 2

    try:
        environment, poll_seconds = _effective_environment(args, root, managed)
        fingerprint = current_fingerprint(root, environment)
    except Exception as exc:
        print(f"[supervisor] BLOCKED {type(exc).__name__}", flush=True)
        return 2

    if args.authorize_deployment:
        try:
            _write_deployment_authority(root, fingerprint)
        except Exception as exc:
            print(f"[supervisor] BLOCKED {type(exc).__name__}", flush=True)
            return 2
        print("[supervisor] DEPLOYMENT_AUTHORITY_RECORDED", flush=True)
        return 0

    sec_dir = root / "var" / "sec"
    sec_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock_fd = os.open(sec_dir / "supervisor.lock", os.O_CREAT | os.O_RDWR, 0o600)
    try:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("[supervisor] ALREADY_RUNNING", flush=True)
            return 2

        previous = read_state(supervisor_state_path(root))
        try:
            authority = _consume_deployment_authority(root, fingerprint)
        except Exception as exc:
            print(f"[supervisor] BLOCKED {type(exc).__name__}", flush=True)
            return 2

        cause = classify(
            previous, fingerprint, manual=args.manual,
            service_managed=managed["service_managed"],
            invocation_id=managed["invocation_id"],
            boot_id=host_boot_id(),
            deployment_authorized=authority is not None)

        # Each supervisor process has a fresh identity.  Child identities are
        # separate names so the kernel boot id cannot be shadowed accidentally.
        supervisor_id = uuid.uuid4().hex[:16]
        kernel_boot_id = host_boot_id()
        launches = 0
        restart_times: list[float] = []
        stopped = False
        child: subprocess.Popen | None = None
        handlers: dict[int, object] = {}

        def stop(signum, frame) -> None:
            nonlocal stopped
            stopped = True
            if child is not None:
                _terminate_group(child, signal.SIGTERM)

        for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            handlers[sig] = signal.signal(sig, stop)

        try:
            while not stopped:
                child_boot_id = uuid.uuid4().hex[:16]
                boot_at = utc_now()
                child_environment = dict(environment)
                child_environment.update({
                    "QUANT_SEC_BOOT_ID": child_boot_id,
                    "QUANT_SEC_LIFECYCLE_CAUSE": cause,
                    "QUANT_SEC_BOOT_AT_UTC": boot_at,
                    "QUANT_SEC_SUPERVISOR_ID": supervisor_id,
                    "QUANT_SEC_LAUNCH_AUTHORITY_NONCE": (
                        authority.get("nonce") if authority else ""),
                })

                # Existing materialization is validated before the child exists.
                materialize_if_absent(root, child_environment)

                state = {
                    "schema": "p0_supervisor/v2",
                    "supervisor_id": supervisor_id,
                    "supervisor_pid": os.getpid(),
                    "supervisor_running": True,
                    "supervisor_invocation_id": managed["invocation_id"],
                    "service_managed": managed["service_managed"],
                    "qualifying_mode": bool(args.qualifying),
                    "child_boot_id": child_boot_id,
                    "host_boot_id": kernel_boot_id,
                    "lifecycle_cause": cause,
                    "boot_at_utc": boot_at,
                    "fingerprint": fingerprint,
                    "launches": launches + 1,
                    "last_child_exit_code": None,
                    "effective_poll_seconds": poll_seconds,
                    "effective_max_waits": args.max_waits,
                    "restart_delay_seconds": RESTART_DELAY_SECONDS,
                    "deployment_authority_nonce": authority.get("nonce") if authority else None,
                    "previous_state_invalid": bool(previous.get("state_invalid")),
                }
                write_state(supervisor_state_path(root), state)

                command = [
                    sys.executable, "-I", str(root / "scripts" / "quant.py"), "sec-serve",
                    "--root", str(root), "--poll-seconds", str(poll_seconds),
                ]
                if args.max_waits is not None:
                    command += ["--max-waits", str(args.max_waits)]
                child = subprocess.Popen(
                    command, env=child_environment, cwd=str(root),
                    start_new_session=True, preexec_fn=_child_parent_death_guard)

                while child.poll() is None:
                    try:
                        child.wait(timeout=1.0)
                    except subprocess.TimeoutExpired:
                        if stopped:
                            _terminate_group(child, signal.SIGTERM)
                            try:
                                child.wait(timeout=25.0)
                            except subprocess.TimeoutExpired:
                                _terminate_group(child, signal.SIGKILL)
                                child.wait()
                        continue

                exit_code = child.returncode
                launches += 1
                state = read_state(supervisor_state_path(root))
                state.update({
                    "last_child_exit_code": exit_code,
                    "last_child_exit_at_utc": utc_now(),
                })
                write_state(supervisor_state_path(root), state)

                if stopped:
                    return 0
                if exit_code == 0:
                    return 0
                if args.max_restarts is not None and launches >= args.max_restarts:
                    return exit_code

                now = time.monotonic()
                restart_times = [
                    stamp for stamp in restart_times
                    if now - stamp < RESTART_BURST_WINDOW_SECONDS
                ]
                if len(restart_times) >= RESTART_BURST_LIMIT:
                    return exit_code
                restart_times.append(now)

                deadline = now + RESTART_DELAY_SECONDS
                while not stopped and time.monotonic() < deadline:
                    time.sleep(min(0.2, deadline - time.monotonic()))
                if stopped:
                    return 0

                # Positive authority: this exact live supervisor observed this
                # exact child fail and itself performs the next launch.
                cause = classify(
                    state, fingerprint, manual=False,
                    service_managed=managed["service_managed"],
                    invocation_id=managed["invocation_id"],
                    witnessed_child_failure=True)
                authority = None
            return 0
        finally:
            if child is not None and child.poll() is None:
                _terminate_group(child, signal.SIGKILL)
                child.wait()
            state = read_state(supervisor_state_path(root))
            if state and not state.get("state_invalid"):
                state.update({
                    "supervisor_running": False,
                    "supervisor_exited_at_utc": utc_now(),
                })
                write_state(supervisor_state_path(root), state)
            for sig, handler in handlers.items():
                signal.signal(sig, handler)
    finally:
        os.close(lock_fd)


if __name__ == "__main__":
    raise SystemExit(main())
