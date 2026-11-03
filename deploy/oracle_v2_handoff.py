"""Explicit transaction for the existing V2 timer; no scientific canary or V1 start.

Private snapshots survive interruption. A killed/rebooted transaction leaves the
timer disabled; --action rollback restores the saved V2 before it is restarted.
"""
import base64
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import stat
import subprocess
import sys
import uuid

from deploy import oracle_v2_deploy as control
from deploy.oracle_v1_host_prepare import write_atomic

BACKUPS = Path("/var/backups")
CONTROL_LOCK = Path("/run/quant-research-v2-control")
ENV = Path("/etc/quant-research-v2/codex.env")
DROPIN = Path("/etc/systemd/system/quant-research-worker-v2.service.d/90-codex-handoff.conf")
SHARED_ENV = Path("/etc/quant-research/worker.env")
WORKER_LOCK = Path("/var/lib/quant-research")
ROOT_UID, ROOT_GID = 0, 0
SYSTEMD = Path("/etc/systemd/system")
LIBEXEC = Path("/usr/local/libexec")
SUDOERS = Path("/etc/sudoers.d/quant-v2-bounded-recovery")
V1_CONFIG = Path("/etc/quant-research/worker.json")
REQUIRED = (
    "QUANT_REPOSITORY", "QUANT_CODEX_ISSUE_NUMBER", "QUANT_CODEX_TARGET_BRANCH",
    "QUANT_CODEX_EXPECTED_HEAD_SHA", "QUANT_CODEX_TASK_ID", "QUANT_CODEX_PROMPT",
    "QUANT_GITHUB_TOKEN", "QUANT_GITHUB_ACTOR", "QUANT_GPT_OSS_COMMAND",
)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def query(unit):
    result = subprocess.run(["systemctl", "show", unit,
        "--property=LoadState,ActiveState,UnitFileState,DropInPaths"],
        capture_output=True, text=True, timeout=20)
    value = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
    if result.returncode or value.get("LoadState") != "loaded":
        raise ValueError("SYSTEMD_STATE_UNAVAILABLE:" + unit)
    return value


def quiesce():
    control.checked(["systemctl", "stop", control.TIMER, control.SERVICE])
    control.checked(["systemctl", "disable", control.TIMER])
    if any(query(u)["ActiveState"] != "inactive" for u in (control.TIMER, control.SERVICE)):
        raise ValueError("V2_NOT_QUIESCENT")


@contextmanager
def locked():
    CONTROL_LOCK.mkdir(mode=0o700, exist_ok=True)
    fd = os.open(CONTROL_LOCK, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        os.close(fd)


def image(path):
    path = Path(path)
    if any(p.is_symlink() for p in path.parents):
        raise ValueError("SYMLINK_PARENT_REFUSED:" + str(path))
    if not os.path.lexists(path):
        return {"kind": "absent"}
    st = path.lstat()
    result = dict(uid=st.st_uid, gid=st.st_gid, mode=stat.S_IMODE(st.st_mode))
    if stat.S_ISLNK(st.st_mode) and path == control.CURRENT:
        result.update(kind="link", target=os.readlink(path))
    elif stat.S_ISREG(st.st_mode):
        result.update(kind="file", data=base64.b64encode(path.read_bytes()).decode())
    else:
        raise ValueError("UNSAFE_SNAPSHOT_PATH:" + str(path))
    return result


def restore(path, saved):
    path = Path(path)
    if saved["kind"] == "absent":
        if os.path.lexists(path):
            path.unlink()
    elif saved["kind"] == "file":
        write_atomic(path, base64.b64decode(saved["data"], validate=True), saved["mode"],
                     uid=saved["uid"], gid=saved["gid"])
    else:
        pending = path.with_name(".quant-handoff-" + uuid.uuid4().hex)
        pending.symlink_to(saved["target"])
        os.lchown(pending, saved["uid"], saved["gid"])
        pending.replace(path)


def paths_to_save(states):
    paths = {control.CONFIG, control.ROOT_QUALIFICATION, control.CURRENT, ENV, DROPIN, SHARED_ENV,
             V1_CONFIG, SUDOERS}
    for unit in (control.TIMER, control.SERVICE):
        paths.add(SYSTEMD / unit)
        paths.update(Path(p) for p in states[unit].get("DropInPaths", "").split())
    paths.update(LIBEXEC / ("quant-v2-" + a) for a in ("qualify", "activate", "status"))
    return sorted(paths, key=str)


def save(directory, record):
    write_atomic(directory / "transaction.json", (json.dumps(record, sort_keys=True) + "\n").encode(), 0o600)
    fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def secure_directory(directory):
    if directory.parent != BACKUPS or not directory.name.startswith("quant-v2-handoff-"):
        raise ValueError("PRIVATE_BACKUP_LOCATION_REQUIRED")
    st = directory.lstat()
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != ROOT_UID or stat.S_IMODE(st.st_mode) != 0o700:
        raise ValueError("PRIVATE_ROOT_BACKUP_REQUIRED")


def rollback(directory, record=None):
    secure_directory(directory)
    if record is None:
        p = directory / "transaction.json"
        st = p.lstat()
        if not stat.S_ISREG(st.st_mode) or st.st_uid != ROOT_UID or stat.S_IMODE(st.st_mode) != 0o600:
            raise ValueError("PRIVATE_ROOT_MANIFEST_REQUIRED")
        record = json.loads(p.read_text())
    if record.get("phase") == "ROLLED_BACK":
        return {"status": "ALREADY_ROLLED_BACK", "backup_directory": str(directory)}
    quiesce()
    # Preserve later Owner edits, even to surfaces written by this transaction.
    for name, original in record["files"].items():
        current = image(name)
        expected = record.get("intended", {}).get(name, original)
        if current != original and current != expected:
            raise ValueError("OWNER_OR_EXTERNAL_EDIT_BLOCKS_ROLLBACK:" + name)
    for name in record["mutable"]:
        restore(name, record["files"][name])
    control.checked(["systemctl", "daemon-reload"])
    for name, original in record["files"].items():
        if image(name) != original:
            raise ValueError("RESTORATION_MISMATCH:" + name)
    # A transaction is admitted only from inactive V1 and a waiting V2 worker.
    if any(query(u)["ActiveState"] != "inactive" for u in (control.V1_TIMER, control.V1_SERVICE)):
        raise ValueError("V1_UNEXPECTEDLY_ACTIVE_DURING_ROLLBACK")
    control.checked(["systemctl", "enable", "--now", control.TIMER])
    if query(control.TIMER)["ActiveState"] != "active" or query(control.TIMER)["UnitFileState"] != "enabled":
        raise ValueError("V2_ROLLBACK_TIMER_NOT_RESTORED")
    record["phase"] = "ROLLED_BACK"
    save(directory, record)
    return {"status": "V2_RESTORED", "release_sha": record["old_sha"],
            "backup_directory": str(directory), "f3_proven": False}


def replace_file(directory, record, path, raw, mode, gid=None):
    gid = ROOT_GID if gid is None else gid
    record["intended"][str(path)] = dict(kind="file", uid=ROOT_UID, gid=gid, mode=mode,
                                       data=base64.b64encode(raw).decode())
    save(directory, record)  # Intent precedes replacement, including crash recovery.
    write_atomic(path, raw, mode, uid=ROOT_UID, gid=gid)


def verify_effective_unit():
    result = subprocess.run(["systemctl", "show", control.SERVICE,
        "--property=ExecStart,EnvironmentFiles,ReadWritePaths,WorkingDirectory"],
        capture_output=True, text=True, timeout=20)
    fields = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
    if (result.returncode or "research.research_os.host_wake --worker-version v2" not in fields.get("ExecStart", "")
            or str(ENV) not in fields.get("EnvironmentFiles", "")
            or str(control.STATE) not in fields.get("ReadWritePaths", "")
            or fields.get("WorkingDirectory") != str(control.CURRENT)):
        raise ValueError("EFFECTIVE_F3_UNIT_NOT_BOUND")


def configuration(path, release):
    st = path.lstat()
    if not stat.S_ISREG(st.st_mode) or st.st_uid != ROOT_UID or stat.S_IMODE(st.st_mode) != 0o600:
        raise ValueError("ROOT_0600_ORCHESTRATION_JSON_REQUIRED")
    values = json.loads(path.read_text())
    if not isinstance(values, dict) or set(values) != set(REQUIRED):
        raise ValueError("EXACT_ORCHESTRATION_KEYS_REQUIRED")
    if any(not isinstance(v, str) or not v.strip() or any(c in v for c in "\n\r\0") for v in values.values()):
        raise ValueError("SINGLE_LINE_NONEMPTY_ORCHESTRATION_VALUES_REQUIRED")
    if values["QUANT_REPOSITORY"] != "fahimahmedb/Quant-Trade" or values["QUANT_CODEX_TARGET_BRANCH"] != control.BRANCH:
        raise ValueError("CANONICAL_ENGINEERING_SUBJECT_REQUIRED")
    if not re.fullmatch(r"[0-9a-f]{40}", values["QUANT_CODEX_EXPECTED_HEAD_SHA"]) or not values["QUANT_CODEX_ISSUE_NUMBER"].isdigit():
        raise ValueError("EXACT_GITHUB_SUBJECT_REQUIRED")
    if values["QUANT_GPT_OSS_COMMAND"] == "AUTO_LOCAL_BACKEND":
        values["QUANT_GPT_OSS_COMMAND"] = shlex.join([
            "/usr/bin/python3.12", str(release / "scripts/gpt_oss_orchestrator.py"),
            "--decision-config", str(control.CONFIG)])
    command = shlex.split(values["QUANT_GPT_OSS_COMMAND"])
    if not command or not Path(command[0]).is_absolute():
        raise ValueError("EXPLICIT_MODEL_EXECUTABLE_REQUIRED")
    values.update(QUANT_CODEX_ORCHESTRATION_ENABLED="1",
                  QUANT_CODEX_ORCHESTRATION_ROOT=str(control.STATE / "codex_control_plane"),
                  QUANT_CODEX_MAX_DISPATCH_ATTEMPTS="1", QUANT_CODEX_MAX_REVIEW_ATTEMPTS="1",
                  QUANT_CODEX_MAX_NO_DELTA_CYCLES="6")
    # JSON string encoding matches systemd EnvironmentFile double-quoted values.
    return values, ("\n".join(k + "=" + json.dumps(v, ensure_ascii=False) for k, v in sorted(values.items())) + "\n").encode()


def qualify_f3(config, values, release):
    """Actual service-principal, GitHub GET and local model checks; no dispatch."""
    program = '''import json,os,sys
from autonomous_research.codex_policy import FencedGitHubIssueClient
from scripts.gpt_oss_orchestrator import subprocess_json_decider
v=os.environ
c=FencedGitHubIssueClient(v['QUANT_REPOSITORY'],int(v['QUANT_CODEX_ISSUE_NUMBER']),v['QUANT_GITHUB_TOKEN'],expected_actor=v['QUANT_GITHUB_ACTOR'])
c._verify_identity()
if c.branch_head(v['QUANT_CODEX_TARGET_BRANCH']) != v['QUANT_CODEX_EXPECTED_HEAD_SHA']: raise ValueError('STALE_CODEX_SUBJECT')
p=c._request('GET','/repos/'+v['QUANT_REPOSITORY']+'/pulls/'+v['QUANT_CODEX_ISSUE_NUMBER'])
if p.get('head',{}).get('ref')!=v['QUANT_CODEX_TARGET_BRANCH'] or p.get('head',{}).get('sha')!=v['QUANT_CODEX_EXPECTED_HEAD_SHA']: raise ValueError('EXACT_CODE_PR_CONTEXT_REQUIRED')
c.comments()
d=subprocess_json_decider(v['QUANT_GPT_OSS_COMMAND'])({'event':'ENGINEERING_PREFLIGHT','allowed_actions':['PARK'],'instruction':'Return a JSON action PARK and reason for this deployment rehearsal. No scientific queue, dispatch or mutation.'})
if d.get('action') != 'PARK': raise ValueError('MODEL_PREFLIGHT_PARK_REQUIRED')
print(json.dumps({'principal_verified':True,'github_read_verified':True,'local_decision_verified':True,'remote_writes':0,'scientific_queue_opened':False}))
'''
    process = subprocess.run(["/usr/sbin/runuser", "-u", "quant-research", "--",
        "/usr/bin/python3.12", "-B", "-s", "-c", program], cwd=release,
        env={"PATH": "/usr/bin:/bin", "HOME": "/var/lib/quant-research",
             "PYTHONPATH": str(release / "src") + ":" + str(release), **values},
        capture_output=True, text=True, timeout=240)
    if process.returncode:
        # No raw stderr: model/client errors may contain credentials or responses.
        raise ValueError("F3_SERVICE_PRINCIPAL_PREFLIGHT_FAILED")
    return json.loads(process.stdout)


def handoff(release, expected_sha, v2_run, sec_run, orchestration_config):
    old = json.loads(control.CONFIG.read_text())
    if old.get("release_sha") != expected_sha or control.validate_config(old) != control.CURRENT.resolve():
        raise ValueError("EXPECTED_V2_ROLLBACK_RELEASE_MISMATCH")
    states = {u: query(u) for u in (control.TIMER, control.SERVICE, control.V1_TIMER, control.V1_SERVICE)}
    if (states[control.TIMER]["ActiveState"] != "active" or states[control.TIMER]["UnitFileState"] != "enabled"
            or any(states[u]["ActiveState"] != "inactive" for u in (control.SERVICE, control.V1_TIMER, control.V1_SERVICE))
            or states[control.V1_TIMER]["UnitFileState"] != "disabled"):
        raise ValueError("WAITING_V2_ENABLED_V1_DISABLED_REQUIRED")
    for p in states[control.SERVICE].get("DropInPaths", "").split():
        if Path(p) == DROPIN and DROPIN.read_bytes() == managed_dropin():
            continue
        if Path(p).name >= DROPIN.name:
            raise ValueError("LATER_DROPIN_REQUIRES_RECONCILIATION")
    values, env_bytes = configuration(orchestration_config, release)
    config = dict(old, release_sha=release.name, runtime_mode="codex_engineering",
                  qualification_source_branch=control.BRANCH,
                  qualification_ci_runs={"v2_core": int(v2_run), "sec_p0": int(sec_run)})
    if control.validate_config(config) != release:
        raise ValueError("EXACT_INSTALLED_TARGET_REQUIRED")
    control.verify_ci(config)
    control.instance_identity(config["vm_ocid"])
    control.backend_from_config(config).healthcheck()
    # Qualify before downtime; the same bound checks run again before activation.
    qualify_f3(config, values, release)
    directory = BACKUPS / ("quant-v2-handoff-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8])
    directory.mkdir(mode=0o700)
    mutable = [str(p) for p in (control.CONFIG, control.CURRENT, ENV, DROPIN, control.ROOT_QUALIFICATION)]
    record = dict(phase="SNAPSHOT", old_sha=expected_sha, target_sha=release.name,
                  states=states, mutable=mutable, intended={},
                  files={str(p): image(p) for p in paths_to_save(states)})
    save(directory, record)
    worker_fd = None
    try:
        record["phase"] = "QUIESCING"; save(directory, record)
        quiesce()
        worker_fd = os.open(WORKER_LOCK, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        fcntl.flock(worker_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if any(image(p) != v for p, v in record["files"].items()):
            raise ValueError("HOST_DRIFT_AFTER_SNAPSHOT")
        record["phase"] = "APPLYING"; save(directory, record)
        replace_file(directory, record, control.CONFIG, (json.dumps(config, indent=2) + "\n").encode(), 0o640,
                     gid=control.CONFIG.stat().st_gid)
        replace_file(directory, record, ENV, env_bytes, 0o640, gid=control.CONFIG.stat().st_gid)
        DROPIN.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        replace_file(directory, record, DROPIN, managed_dropin(), 0o644)
        pending = control.CURRENT.with_name(".current-handoff-" + uuid.uuid4().hex)
        record["intended"][str(control.CURRENT)] = dict(kind="link", uid=ROOT_UID, gid=ROOT_GID, mode=0o777, target=str(release))
        save(directory, record)
        pending.symlink_to(release); pending.replace(control.CURRENT)
        record["phase"] = "REBOUND"; save(directory, record)
        control.checked(["systemctl", "daemon-reload"])
        verify_effective_unit()
        proof = qualify_f3(config, values, release)
        proof.update(status="PASS_F3_PREDEPLOY_ONLY", release_sha=release.name,
                     config_hash=control.canonical_hash(config), f3_proven=False)
        replace_file(directory, record, control.ROOT_QUALIFICATION, (json.dumps(proof) + "\n").encode(), 0o600)
        control.verify_ci(config)
        if image(SHARED_ENV) != record["files"][str(SHARED_ENV)]:
            raise ValueError("SHARED_ENV_CHANGED")
        control.checked(["systemctl", "enable", "--now", control.TIMER])
        if query(control.TIMER)["ActiveState"] != "active" or any(query(u)["ActiveState"] != "inactive" for u in (control.V1_TIMER, control.V1_SERVICE)):
            raise ValueError("V2_SINGLE_SCHEDULER_NOT_RESTORED")
        record["phase"] = "ACTIVE_F3_PROOF_PENDING"; save(directory, record)
        return {"status": record["phase"], "release_sha": release.name,
                "backup_directory": str(directory), "f3_proven": False}
    except BaseException:
        try:
            rollback(directory, record)
        except BaseException:
            raise RuntimeError("V2_ROLLBACK_REQUIRES_RECOVERY:" + str(directory)) from None
        raise RuntimeError("HANDOFF_FAILED_V2_RESTORED:" + str(directory)) from None
    finally:
        if worker_fd is not None:
            os.close(worker_fd)


def managed_dropin():
    return ("[Service]\nEnvironmentFile=" + str(ENV) + "\nExecStart=\nExecStart="
        "/usr/bin/flock --nonblock --conflict-exit-code=0 /var/lib/quant-research "
        "/usr/bin/python3.12 -B -s -m research.research_os.host_wake --worker-version v2 --config "
        + str(control.CONFIG) + "\nReadWritePaths=" + str(control.STATE) + "\n").encode()


def execute(args):
    with locked():
        if args.action == "rollback":
            if args.backup_directory is None:
                raise ValueError("BACKUP_DIRECTORY_REQUIRED")
            return rollback(args.backup_directory)
        if any(v is None for v in (args.release, args.expected_current_sha, args.v2_ci_run,
                                    args.sec_ci_run, args.orchestration_config)):
            raise ValueError("EXPLICIT_HANDOFF_ARGUMENTS_REQUIRED")
        return handoff(args.release, args.expected_current_sha, args.v2_ci_run,
                       args.sec_ci_run, args.orchestration_config)
