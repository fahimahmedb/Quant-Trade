#!/usr/bin/env python3
"""Exact-SHA V2 preparation, bounded canary and gated authority transfer."""
import argparse
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import pwd
import signal
import subprocess
import urllib.request
import hashlib

from deploy.oracle_h24_canary import instance_identity
from deploy.oracle_release_install import _validate_release_receipt, validate_sha
from deploy.oracle_v1_host_prepare import checked, write_atomic, wrapper
from research.research_os.expansion.v2_core import assert_authority_closed, canonical_hash
from research.research_os.oracle_worker import backend_from_config
from research.research_os.oracle_worker_v2 import _require_v2_config

BRANCH = "builder/oracle-v2-core-20261020"
CONFIG = Path("/etc/quant-research-v2/worker.json")
ROOT_QUALIFICATION = CONFIG.parent / "qualification.root.json"
STATE = Path("/var/lib/quant-research-v2")
CURRENT = Path("/opt/quant-research-v2/current")
EXPORTS = Path("/var/lib/quant-research-v2-observations")
V1_TIMER, V1_SERVICE = "quant-research-worker.timer", "quant-research-worker.service"
TIMER, SERVICE = "quant-research-worker-v2.timer", "quant-research-worker-v2.service"
GATES = ("exact_release_ci", "oracle_identity", "real_readonly_entrypoint", "local_gpt_oss_reasoning",
         "v1_quiesced_during_writes", "canonical_migration", "trial_before_ideation", "claim_expiry_recovered",
         "v2_sidecars_persisted", "no_duplicate_replay", "authority_closed")


def verify_ci(config):
    evidence = {}
    for key, name in (("v2_core", "Oracle V2 Core"), ("sec_p0", "SEC P0 pre-t0 gate")):
        run_id = int(config["qualification_ci_runs"][key])
        url = f"https://api.github.com/repos/fahimahmedb/Quant-Trade/actions/runs/{run_id}"
        request = urllib.request.Request(url, headers={"User-Agent": "Quant-Trade-V2-qualification"})
        with urllib.request.urlopen(request, timeout=30) as response:
            run = json.loads(response.read(2 * 1024 * 1024))
        if (run.get("head_sha") != config["release_sha"] or run.get("head_branch") != BRANCH
                or run.get("name") != name or run.get("status") != "completed" or run.get("conclusion") != "success"):
            raise ValueError("V2_EXACT_RELEASE_CI_NOT_SUCCESSFUL:" + key)
        evidence[key] = {k: run[k] for k in ("id", "head_sha", "conclusion", "html_url")}
    return evidence


def validate_config(config):
    sha = validate_sha(config["release_sha"])
    _require_v2_config(config)
    assert_authority_closed(config)
    if (config.get("repository") != "fahimahmedb/Quant-Trade" or config.get("branch") != BRANCH
            or config.get("cache") != str(STATE / "github.git") or config.get("lane") != "auto"):
        raise ValueError("V2_CANONICAL_CONFIG_REQUIRED")
    release = Path("/opt/quant-research/releases") / sha
    receipt = _validate_release_receipt(json.loads((release / ".quant_release_receipt.json").read_text()), sha)
    if Path(receipt["path"]).resolve() != release:
        raise ValueError("V2_EXACT_RELEASE_PATH_MISMATCH")
    backend = backend_from_config(config)
    if backend is None or config["model_backend"]["implementation"] != "gpt_oss":
        raise ValueError("QUALIFIED_LOCAL_GPT_OSS_REQUIRED")
    return release


def verify_qualification(report, config, now=None):
    if (report.get("status") != "PASS_V2_PRE_ACTIVATION" or report.get("evidence_scope") != "LIVE_ORACLE_V2_CORE"
            or report.get("release_sha") != config["release_sha"] or report.get("config_hash") != canonical_hash(config)
            or report.get("instance", {}).get("id") != config["vm_ocid"]):
        raise ValueError("MATCHING_LIVE_V2_QUALIFICATION_REQUIRED")
    if set(report.get("gates", {})) != set(GATES) or not all(report["gates"][k] is True for k in GATES):
        raise ValueError("V2_QUALIFICATION_GATE_NOT_PASSED")
    assert_authority_closed(report.get("authority", {}))
    if report.get("scheduler_enabled") is not False or report.get("outcome_accessed") is not False:
        raise ValueError("V2_QUALIFICATION_SCHEDULER_OR_OUTCOME_UNSAFE")
    completed = datetime.fromisoformat(report["completed_at"])
    elapsed = (now or datetime.now(timezone.utc)) - completed
    if not timedelta(0) <= elapsed <= timedelta(hours=6) or report.get("hosted_model_calls") != 0:
        raise ValueError("V2_QUALIFICATION_EXPIRED_OR_UNSAFE")
    return report


def active(unit):
    return subprocess.run(["systemctl", "is-active", unit], capture_output=True, text=True).stdout.strip()


def prepare(release, v2_run, sec_run):
    if os.geteuid() != 0:
        raise ValueError("ROOT_REQUIRED_FOR_V2_PREPARATION")
    old = json.loads(Path("/etc/quant-research/worker.json").read_text())
    account = pwd.getpwnam("quant-research")
    if account.pw_uid == 0 or account.pw_dir != "/var/lib/quant-research":
        raise ValueError("QUALIFIED_V1_ACCOUNT_REQUIRED")
    config = dict(old, release_sha=release.name, branch=BRANCH, cache=str(STATE / "github.git"),
                  worker_id="oracle-research-v2", lane="auto", research_contract_version="v2-core",
                  qualification_ci_runs={"v2_core": int(v2_run), "sec_p0": int(sec_run)})
    for key in ("economic_experiment_authorized", "prospective_observation_authorized", "real_capital_authorized", "live_trading_authorized"):
        config[key] = False
    validate_config(config)
    verify_ci(config)
    instance_identity(config["vm_ocid"])
    backend_from_config(config).healthcheck()
    if any(active(unit) in ("active", "activating", "reloading") for unit in (TIMER, SERVICE)):
        raise ValueError("V2_RUNNING_RELEASE_REQUIRES_EXPLICIT_REPAIR_HANDOFF")
    STATE.mkdir(mode=0o700, exist_ok=True)
    os.chown(STATE, account.pw_uid, account.pw_gid)
    EXPORTS.mkdir(mode=0o750, exist_ok=True)
    os.chown(EXPORTS, 0, pwd.getpwnam("ocarun").pw_gid)
    os.chmod(EXPORTS, 0o750)
    CONFIG.parent.mkdir(mode=0o750, exist_ok=True)
    os.chown(CONFIG.parent, 0, account.pw_gid)
    write_atomic(CONFIG, (json.dumps(config, indent=2) + "\n").encode(), 0o640, gid=account.pw_gid)
    for root, _, files in os.walk(release):
        os.chown(root, 0, 0); os.chmod(root, 0o755)
        for name in files:
            path = Path(root) / name
            if path.is_symlink():
                raise ValueError("V2_RELEASE_SYMLINK_UNEXPECTED")
            os.chown(path, 0, 0); os.chmod(path, 0o644)
    CURRENT.parent.mkdir(mode=0o755, exist_ok=True)
    pending = CURRENT.with_name(".current-pending")
    if pending.is_symlink(): pending.unlink()
    pending.symlink_to(release, target_is_directory=True); pending.replace(CURRENT)
    for unit in (SERVICE, TIMER):
        write_atomic(Path("/etc/systemd/system") / unit, (release / "deploy/systemd" / unit).read_bytes())
    checked(["systemd-analyze", "verify", "/etc/systemd/system/" + SERVICE, "/etc/systemd/system/" + TIMER])
    checked(["systemctl", "daemon-reload"])
    checked(["systemctl", "disable", TIMER])
    libexec = Path("/usr/local/libexec")
    rules = []
    for action in ("qualify", "activate", "status"):
        name = "quant-v2-" + action
        write_atomic(libexec / name, wrapper(release, "deploy.oracle_v2_deploy", ["--action", action]), 0o755)
        rules.append(f'ocarun ALL=(root) NOPASSWD: /usr/local/libexec/{name} ""')
    data = ("\n".join(rules) + "\n").encode()
    import tempfile
    with tempfile.NamedTemporaryFile() as test:
        test.write(data); test.flush(); checked(["visudo", "-cf", test.name])
    write_atomic(Path("/etc/sudoers.d/quant-v2-bounded-recovery"), data, 0o440)
    return dict(status="V2_PREPARED_V1_UNCHANGED", release_sha=release.name,
                v1_current=str(Path("/opt/quant-research/current").resolve()), v1_timer=active(V1_TIMER),
                v2_timer=active(TIMER), model_reused=True, private_key_exported=False,
                required_next="Run fixed V2 qualifier, inspect live gates, then gated activation and natural wake/reboot proof.")


def run_as_worker(arguments, timeout):
    command = ["runuser", "-u", "quant-research", "--", "env", "HOME=/var/lib/quant-research",
               "PYTHONDONTWRITEBYTECODE=1", "/usr/bin/python3.12", "-B", "-s", *arguments]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, start_new_session=True)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise RuntimeError("V2_BOUNDED_CHILD_TIMEOUT_PROCESS_GROUP_KILLED") from None
    if process.returncode:
        raise RuntimeError("V2_CHILD_FAILED:" + stderr[-500:])
    return stdout


def qualify(config, release):
    verify_ci(config)
    instance_identity(config["vm_ocid"])
    if active(TIMER) in ("active", "activating"):
        raise ValueError("STOP_V2_SCHEDULER_BEFORE_REQUALIFICATION")
    v1_was_active = active(V1_TIMER) in ("active", "activating")
    checked(["systemctl", "stop", V1_TIMER, V1_SERVICE])
    try:
        run_as_worker(["-m", "deploy.oracle_v2_canary", "--config", str(CONFIG),
                       "--output", str(STATE / "qualification.json")], timeout=1800)
        report = json.loads((STATE / "qualification.json").read_text())
        verify_qualification(report, config)
        # A root-owned file in a worker-writable directory can be replaced.
        write_atomic(ROOT_QUALIFICATION, (json.dumps(report, sort_keys=True, indent=2) + "\n").encode(), 0o600)
        return dict(status=report["status"], release_sha=config["release_sha"], gates=report["gates"],
                    task_id=report["task_id"], config_hash=report["config_hash"], v1_restored_after_canary=v1_was_active)
    finally:
        if v1_was_active:
            checked(["systemctl", "start", V1_TIMER])


def activate(config):
    report = json.loads(ROOT_QUALIFICATION.read_text())
    verify_qualification(report, config)
    verify_ci(config)
    instance_identity(config["vm_ocid"])
    backend_from_config(config).healthcheck()
    # Qualification was a bounded rehearsal. Reconcile once more after stopping
    # V1, since it may have advanced while the builder reviewed the proof.
    checked(["systemctl", "stop", V1_TIMER, V1_SERVICE])
    try:
        migration = json.loads(run_as_worker(["-m", "deploy.oracle_v2_canary", "--config", str(CONFIG),
                                              "--migration-only"], timeout=300))
        if migration.get("current_epoch_binding") != report.get("epoch_binding"):
            raise ValueError("V2_EPOCH_CHANGED_AFTER_LIVE_QUALIFICATION")
        checked(["systemctl", "disable", V1_TIMER])
        checked(["systemctl", "enable", "--now", TIMER])
        if active(TIMER) != "active" or active(V1_TIMER) in ("active", "activating"):
            raise ValueError("V2_SINGLE_SCHEDULER_ACTIVATION_NOT_PROVEN")
    except Exception:
        checked(["systemctl", "stop", TIMER, SERVICE])
        checked(["systemctl", "enable", "--now", V1_TIMER])
        raise
    result = dict(status="V2_TIMER_ENABLED_RUNTIME_PROOF_PENDING", release_sha=config["release_sha"],
                  authority={k: config[k] for k in report["authority"]}, config_hash=canonical_hash(config),
                  source_head=migration["source_head"],
                  v1_rollback_release=str(Path("/opt/quant-research/current").resolve()))
    write_atomic(STATE / "activation.json", (json.dumps(result, indent=2) + "\n").encode(), 0o600)
    return result


def status(config):
    result = dict(release_sha=config["release_sha"], boot_id=Path("/proc/sys/kernel/random/boot_id").read_text().strip())
    for key, unit in (("v1_timer", V1_TIMER), ("v2_timer", TIMER), ("v2_service", SERVICE), ("model", "quant-local-model.service")):
        raw = checked(["systemctl", "show", unit, "--property=ActiveState,UnitFileState,Result,InvocationID,MemoryPeak,MemoryMax,LastTriggerUSec"])
        result[key] = dict(line.split("=", 1) for line in raw.splitlines() if "=" in line)
    raw = checked(["journalctl", "--boot", "--unit=" + SERVICE, "--output=json", "--no-pager", "-n", "200"])
    wakes = []
    for line in raw.splitlines():
        row = json.loads(line)
        try: value = json.loads(row.get("MESSAGE", ""))
        except (ValueError, TypeError): continue
        wakes.append(dict(invocation=row.get("_SYSTEMD_INVOCATION_ID"), timestamp=row.get("__REALTIME_TIMESTAMP"), result=value))
    result["wake_results"] = wakes
    result["model_health"] = backend_from_config(config).healthcheck()
    raw = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode()
    filename = "v2-status-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ") + ".json"
    write_atomic(EXPORTS / filename, raw, 0o640, gid=pwd.getpwnam("ocarun").pw_gid)
    return dict(boot_id=result["boot_id"], release_sha=config["release_sha"], v1_timer=result["v1_timer"]["ActiveState"],
                timer=result["v2_timer"]["ActiveState"] + "/" + result["v2_timer"]["UnitFileState"],
                service_result=result["v2_service"]["Result"], model_health=result["model_health"],
                wakes=[{"invocation": w["invocation"], "status": w["result"].get("status"),
                        "commit": w["result"].get("output_commit")} for w in wakes[-2:]],
                evidence_file=str(EXPORTS / filename), sha256=hashlib.sha256(raw).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--action", choices=("qualify", "activate", "status"), required=True)
    args = parser.parse_args()
    if os.geteuid() != 0: raise SystemExit("ROOT_REQUIRED_FOR_FIXED_V2_CONTROL")
    config = json.loads(CONFIG.read_text())
    release = validate_config(config)
    if CURRENT.resolve() != release: raise ValueError("V2_CURRENT_RELEASE_CHANGED")
    os.chdir(release)
    print(json.dumps({"qualify": lambda: qualify(config, release), "activate": lambda: activate(config),
                      "status": lambda: status(config)}[args.action](), sort_keys=True))


if __name__ == "__main__": main()
