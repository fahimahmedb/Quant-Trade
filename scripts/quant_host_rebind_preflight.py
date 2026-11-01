#!/usr/bin/env python3
"""One-off existing-host backup and read-only canonical compatibility probe.

Never changes a config, unit, release, timer, model or remote Git ref. Private
rollback copies are the only host writes apart from normal read-side Git caches.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

TARGET = "code/canonical"
CONFIGS = {
    "v1": ("/etc/quant-research/worker.json", "766b69d5189783ce38b2147c2d0d46ebfb0299a454b22f2bfe0d2faf7c48c9ea",
           "f3943830e20b05d926d3013501573b8b21fdace7", "builder/oracle-economic-loop-recovery-20261019"),
    "v2": ("/etc/quant-research-v2/worker.json", "5767f593055ca729abd62c892a7ae0b0306768913b59bdb14e3d8ee5e6c21a8f",
           "a67ffec48fff895d5edc42171855e2213e49cf0d", "builder/oracle-v2-core-20261020"),
}
SOURCE_HASHES = {
    "research/research_os/oracle_worker.py": "b1e49faa575c79106acf03bad989f4ecb48c0e3da0c06f0249c407cba43d254e",
    "research/research_os/github_state.py": "f68e090d226e622ed1f4ca4bfd325381e82423a8eb1d69cbed7213a5c4dcae64",
    "research/research_os/oracle_worker_v2.py": "147b26ac6dc0a2d4ada82a5a9f00b34f75d29c2507c99e2d758c108ee5d15e4a",
    "research/research_os/expansion/v2_state.py": "02fec00e7ad23e9cb1063ff0f6cc470d6ede36fb28ff22611d403619c2f6251f",
    "deploy/oracle_v2_deploy.py": "0073965f912e90821797ae998c538aeefe1b574b20c406c2685028d47f8f5da6",
}
AUTHORITY = ("economic_experiment_authorized", "prospective_observation_authorized",
             "real_capital_authorized", "live_trading_authorized")


class Blocked(RuntimeError):
    pass


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def checked_bytes(path):
    path = Path(path)
    st = path.lstat()
    if not path.is_file() or path.is_symlink() or st.st_uid != 0 or st.st_mode & 0o022:
        raise Blocked("UNEXPECTED_ROOT_FILE_PERMISSIONS")
    return path.read_bytes()


def validate_config(raw, spec):
    path, expected, release, old = spec
    if digest(raw) != expected:
        raise Blocked("CONFIG_CHANGED_SINCE_OWNER_INVENTORY")
    value = json.loads(raw)
    if (value.get("branch") != old or value.get("release_sha") != release
            or value.get("repository") != "fahimahmedb/Quant-Trade"
            or any(value.get(k, False) is not False for k in AUTHORITY)):
        raise Blocked("CONFIG_IDENTITY_OR_AUTHORITY_CHANGED")
    return value


def unit_state(unit):
    p = subprocess.run(["systemctl", "show", unit, "--property=ActiveState,UnitFileState,InvocationID"],
                       capture_output=True, text=True, timeout=10, check=True)
    return dict(line.split("=", 1) for line in p.stdout.splitlines() if "=" in line)


def validate_probe(probe, canonical_sha, *, v2=False):
    if (probe.get("status") != "DRY_RUN" or probe.get("writes") != 0
            or probe.get("input_head") != canonical_sha or probe.get("state_branch") != TARGET
            or probe.get("selected_task") is not None or probe.get("claimed_tasks") != 0
            or probe.get("hosted_model_calls") != 0 or probe.get("model_calls") != 0
            or any(probe.get("authority", {}).get(k) is not False for k in AUTHORITY)):
        raise Blocked("READ_ONLY_CANONICAL_COMPATIBILITY_NOT_PROVEN")
    if v2 and (not probe.get("same_tasks_as_live_v2") or probe.get("v2_preflight") != "PASS"):
        raise Blocked("LIVE_V2_TASK_OR_POLICY_MISMATCH")


PROBE = r'''
import hashlib,json,sys
from pathlib import Path
release,config_path,flavor=sys.argv[1:]
sys.path.insert(0,release)
from research.research_os.github_state import GitHubStateStore
from research.research_os.oracle_worker import ResearchOSWorker
config=json.loads(Path(config_path).read_text())
old_branch=config['branch']
class ReadOnlyStore(GitHubStateStore):
    def commit(self,*a,**kw): raise RuntimeError('PREFLIGHT_REMOTE_WRITE_FORBIDDEN')
    def compact_if_due(self): raise RuntimeError('PREFLIGHT_COMPACTION_FORBIDDEN')
class NoModelCalls:
    calls=0
    def generate(self,*a,**kw): raise RuntimeError('PREFLIGHT_INFERENCE_FORBIDDEN')
    def reason(self,*a,**kw): raise RuntimeError('PREFLIGHT_INFERENCE_FORBIDDEN')
    def healthcheck(self,*a,**kw): raise RuntimeError('PREFLIGHT_MODEL_ACCESS_FORBIDDEN')
def task_blobs(s):
    return {p:h for p,h in s.blobs.items() if p.startswith('research/research_os/tasks/')}
old_tasks=None
if flavor=='v2':
    with ReadOnlyStore(cache=Path(config['cache']),repository=config['repository'],branch=old_branch).snapshot() as s:
        old_tasks=task_blobs(s)
config['branch']='code/canonical'
store=ReadOnlyStore(cache=Path(config['cache']),repository=config['repository'],branch=config['branch'])
if flavor=='v2':
    from research.research_os.oracle_worker_v2 import build_v2_worker
    worker=build_v2_worker(config,store=store,backend=NoModelCalls())
else:
    worker=ResearchOSWorker(store,lane=config.get('lane','auto'),worker_id=config['worker_id'],release_sha=config['release_sha'])
with worker.store.snapshot() as s:
    tasks=s.tasks()
    same=old_tasks==task_blobs(s) if old_tasks is not None else None
    claimed=sum(t.get('status')=='CLAIMED' for t in tasks)
result=worker.wake(mode='dry-run')
out={k:result.get(k) for k in ('status','writes','input_head','state_branch','selected_task','authority','hosted_model_calls')}
out.update(model_calls=0,claimed_tasks=claimed,task_count=len(tasks),same_tasks_as_live_v2=same,
           v2_preflight=(getattr(worker.store,'last_preflight',None) or {}).get('status'))
print(json.dumps(out,sort_keys=True))
'''


def backup_files(paths, destination):
    destination.mkdir(mode=0o700, parents=False, exist_ok=False)
    hashes = {}
    for path in paths:
        raw = checked_bytes(path)
        target = destination / str(path).lstrip("/")
        target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        shutil.copy2(path, target, follow_symlinks=False)
        os.chmod(target, 0o600)
        if target.read_bytes() != raw:
            raise Blocked("BACKUP_BYTE_VERIFICATION_FAILED")
        hashes[str(path)] = digest(raw)
    return hashes


def execute(canonical_sha):
    if os.geteuid() != 0 or not re.fullmatch(r"[a-f0-9]{40}", canonical_sha):
        raise Blocked("ROOT_AND_EXACT_CANONICAL_SHA_REQUIRED")
    configs = {key: validate_config(checked_bytes(spec[0]), spec) for key, spec in CONFIGS.items()}
    timer = unit_state("quant-research-worker-v2.timer")
    fallback = unit_state("quant-research-worker.timer")
    if timer.get("ActiveState") != "active" or timer.get("UnitFileState") != "enabled":
        raise Blocked("EXISTING_V2_TIMER_NOT_HEALTHY")
    if fallback.get("ActiveState") != "inactive" or fallback.get("UnitFileState") != "disabled":
        raise Blocked("V1_FALLBACK_NOT_DISABLED")
    paths = [Path(s[0]) for s in CONFIGS.values()]
    for key, spec in CONFIGS.items():
        release = Path("/opt/quant-research/releases") / spec[2]
        link = Path("/opt/quant-research-v2/current" if key == "v2" else "/opt/quant-research/current")
        if link.resolve() != release:
            raise Blocked("ACTIVE_RELEASE_CHANGED")
        for name, expected in SOURCE_HASHES.items():
            if key == "v1" and name not in ("research/research_os/oracle_worker.py", "research/research_os/github_state.py"):
                continue
            if digest(checked_bytes(release / name)) != expected:
                raise Blocked("DEPLOYED_WORKER_BYTES_CHANGED")
        paths.append(release / ".quant_release_receipt.json")
    paths += [Path("/etc/systemd/system") / unit for unit in (
        "quant-research-worker.service", "quant-research-worker.timer",
        "quant-research-worker-v2.service", "quant-research-worker-v2.timer")]
    paths += [Path("/etc/systemd/system/quant-research-worker-v2.service.d/50-native-live.conf"),
              Path("/etc/quant-research/worker.env")]
    paths += [Path("/usr/local/libexec") / name for name in (
        "quant-v1-qualify", "quant-v1-activate", "quant-v2-qualify", "quant-v2-activate", "quant-v2-status")]
    for path in paths:
        checked_bytes(path)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    destination = Path("/var/backups") / ("quant-canonical-rebind-" + stamp)
    metadata = {str(p): {"uid": p.stat().st_uid, "gid": p.stat().st_gid,
                         "mode": oct(p.stat().st_mode & 0o777)} for p in paths}
    hashes = backup_files(paths, destination)
    report = {"operation": "BACKUP_AND_READ_ONLY_CANONICAL_PREFLIGHT", "backup_directory": str(destination),
              "backup_sha256": hashes, "backup_file_metadata": metadata, "canonical_sha": canonical_sha,
              "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
              "timer_before": timer, "v1_timer_before": fallback, "config_mutations": 0,
              "timer_mutations": 0, "remote_writes": 0, "model_calls": 0, "probes": {}}
    try:
        for key, spec in CONFIGS.items():
            release = "/opt/quant-research/releases/" + spec[2]
            cmd = ["runuser", "-u", "quant-research", "--", "env", "HOME=/var/lib/quant-research",
                   "PYTHONDONTWRITEBYTECODE=1", "/usr/bin/python3.12", "-I", "-B", "-c", PROBE,
                   release, spec[0], key]
            child = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if child.returncode:
                raise Blocked("READ_ONLY_" + key.upper() + "_PROBE_FAILED_NO_BINDING_CHANGED")
            value = json.loads(child.stdout)
            validate_probe(value, canonical_sha, v2=key == "v2")
            report["probes"][key] = value
        if timer != unit_state("quant-research-worker-v2.timer"):
            raise Blocked("TIMER_IDENTITY_CHANGED_DURING_PREFLIGHT")
        for key, spec in CONFIGS.items():
            validate_config(checked_bytes(spec[0]), spec)
        report.update(status="PASS_BACKUP_AND_READ_ONLY_COMPATIBILITY",
                      fixed_status_old_branch_gate="PRESENT_IN_HASH_VERIFIED_A67_CONTROL; migrate status validation before changing binding")
    except Exception as exc:
        report.update(status="BLOCK_NO_BINDING_CHANGED", error= str(exc) if isinstance(exc, Blocked) else type(exc).__name__)
    (destination / "preflight.json").write_text(json.dumps(report, sort_keys=True) + "\n")
    os.chmod(destination / "preflight.json", 0o600)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical-sha", required=True)
    args = parser.parse_args()
    try:
        result = execute(args.canonical_sha)
    except Exception as exc:
        result = {"operation": "BACKUP_AND_READ_ONLY_CANONICAL_PREFLIGHT", "status": "BLOCK_NO_BINDING_CHANGED",
                  "error": str(exc) if isinstance(exc, Blocked) else type(exc).__name__}
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("status") == "PASS_BACKUP_AND_READ_ONLY_COMPATIBILITY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
