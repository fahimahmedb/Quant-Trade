#!/usr/bin/env python3
"""Bounded migration of the two existing host ref bindings.

Default preflight writes only private rollback copies and read-side Git caches.
Explicit apply changes only selected config branch strings and the existing V2
status wrapper, after a fresh successful backup/preflight under the worker lock.
Rollback restores exact saved bytes/permissions and refuses newer owner edits.
No action changes a release, unit, timer, model, scientific state or remote ref.
"""
import argparse
import contextlib
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import shutil
import shlex
import subprocess
import sys
import tempfile
import time

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
def stable_surface(s):
    ignored=('research/research_os/runtime/worker_wakes/','research/research_os/artifacts/live-observation/')
    value={p:h for p,h in s.blobs.items() if not p.startswith(ignored)}
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
old_tasks=None
old_surface=None
if flavor=='v2':
    with ReadOnlyStore(cache=Path(config['cache']),repository=config['repository'],branch=old_branch).snapshot() as s:
        old_tasks=task_blobs(s)
        old_surface=stable_surface(s)
config['branch']='code/canonical'
store=ReadOnlyStore(cache=Path(config['cache']),repository=config['repository'],branch=config['branch'])
if flavor=='v2':
    from research.research_os.oracle_worker_v2 import build_v2_worker
    worker=build_v2_worker(config,store=store,backend=NoModelCalls())
else:
    worker=ResearchOSWorker(store,lane=config.get('lane','auto'),worker_id=config['worker_id'],release_sha=config['release_sha'])
with worker.store.snapshot() as s:
    first_head=s.head
    state_surface=stable_surface(s)
    tasks=s.tasks()
    same=old_tasks==task_blobs(s) if old_tasks is not None else None
    claimed=sum(t.get('status')=='CLAIMED' for t in tasks)
result=worker.wake(mode='dry-run')
if first_head!=result.get('input_head'):raise RuntimeError('PREFLIGHT_SNAPSHOT_MOVED_RETRY_FRESH_STATE')
out={k:result.get(k) for k in ('status','writes','input_head','state_branch','selected_task','authority','hosted_model_calls')}
out.update(model_calls=0,claimed_tasks=claimed,task_count=len(tasks),same_tasks_as_live_v2=same,
           stable_canonical_surface_sha256=state_surface,stable_old_surface_sha256=old_surface,
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
        with target.open("rb") as stream:
            os.fsync(stream.fileno())
        if target.read_bytes() != raw:
            raise Blocked("BACKUP_BYTE_VERIFICATION_FAILED")
        hashes[str(path)] = digest(raw)
    for parent in sorted({destination, destination.parent, *(p.parent for p in destination.rglob("*") )},
                         key=lambda p: len(p.parts), reverse=True):
        fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(fd)
        finally: os.close(fd)
    return hashes


def selected_specs(scope):
    if scope not in ("both", "v1", "v2"):
        raise Blocked("INVALID_MIGRATION_SCOPE")
    return {key: spec for key, spec in CONFIGS.items() if scope == "both" or scope == key}


def release_signatures(scope):
    result={}
    for key,spec in selected_specs(scope).items():
        root=Path('/opt/quant-research/releases')/spec[2]
        link=Path('/opt/quant-research-v2/current' if key=='v2' else '/opt/quant-research/current')
        if link.resolve()!=root:
            raise Blocked('DEPLOYED_RELEASE_POINTER_CHANGED')
        tree=hashlib.sha256();total=0;count=0
        for path in sorted(root.rglob('*')):
            if path.is_symlink():raise Blocked('RELEASE_TREE_SYMLINK_UNEXPECTED')
            if not path.is_file():continue
            st=path.stat();total+=st.st_size;count+=1
            if total>512*1024*1024 or count>50000:raise Blocked('RELEASE_FINGERPRINT_BOUND_EXCEEDED')
            one=hashlib.sha256()
            with path.open('rb') as stream:
                for block in iter(lambda:stream.read(262144),b''):one.update(block)
            row=[str(path.relative_to(root)),st.st_uid,st.st_gid,st.st_mode & 0o777,one.hexdigest()]
            tree.update(json.dumps(row,separators=(',',':')).encode()+b'\n')
        if not count:raise Blocked('DEPLOYED_RELEASE_EMPTY')
        result[key]=dict(release_sha=spec[2],tree_sha256=tree.hexdigest(),files=count,bytes=total)
    return result


def bounded_probe(cmd):
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, start_new_session=True)
    try:
        stdout, _ = child.communicate(timeout=300)
    except subprocess.TimeoutExpired:
        os.killpg(child.pid, signal.SIGKILL)
        child.communicate()
        raise Blocked("READ_ONLY_PROBE_TIMEOUT_PROCESS_GROUP_STOPPED") from None
    if child.returncode:
        raise Blocked("READ_ONLY_PROBE_FAILED_NO_BINDING_CHANGED")
    return json.loads(stdout)


def execute(canonical_sha, scope="both"):
    if os.geteuid() != 0 or not isinstance(canonical_sha, str) or not re.fullmatch(r"[a-f0-9]{40}", canonical_sha):
        raise Blocked("ROOT_AND_EXACT_CANONICAL_SHA_REQUIRED")
    specs = selected_specs(scope)
    configs = {key: validate_config(checked_bytes(spec[0]), spec) for key, spec in specs.items()}
    timer = unit_state("quant-research-worker-v2.timer")
    fallback = unit_state("quant-research-worker.timer")
    if timer.get("ActiveState") != "active" or timer.get("UnitFileState") != "enabled":
        raise Blocked("EXISTING_V2_TIMER_NOT_HEALTHY")
    if fallback.get("ActiveState") != "inactive" or fallback.get("UnitFileState") != "disabled":
        raise Blocked("V1_FALLBACK_NOT_DISABLED")
    paths = [Path(s[0]) for s in CONFIGS.values()]
    for key, spec in specs.items():
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
              "backup_sha256": hashes, "backup_file_metadata": metadata, "canonical_sha": canonical_sha, "scope": scope,
              "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
              "timer_before": timer, "v1_timer_before": fallback, "config_mutations": 0,
              "timer_mutations": 0, "remote_writes": 0, "model_calls": 0, "probes": {},
              "release_signatures": release_signatures(scope)}
    try:
        for key, spec in specs.items():
            release = "/opt/quant-research/releases/" + spec[2]
            cmd = ["runuser", "-u", "quant-research", "--", "env", "HOME=/var/lib/quant-research",
                   "PYTHONDONTWRITEBYTECODE=1", "/usr/bin/python3.12", "-I", "-B", "-c", PROBE,
                   release, spec[0], key]
            value = bounded_probe(cmd)
            validate_probe(value, canonical_sha, v2=key == "v2")
            report["probes"][key] = value
        if timer != unit_state("quant-research-worker-v2.timer"):
            raise Blocked("TIMER_IDENTITY_CHANGED_DURING_PREFLIGHT")
        for key, spec in specs.items():
            validate_config(checked_bytes(spec[0]), spec)
        if release_signatures(scope)!=report['release_signatures']:
            raise Blocked('DEPLOYED_RELEASE_BYTES_CHANGED_DURING_PREFLIGHT')
        report.update(status="PASS_BACKUP_AND_READ_ONLY_COMPATIBILITY",
                      fixed_status_old_branch_gate="PRESENT_IN_HASH_VERIFIED_A67_CONTROL; migrate status validation before changing binding")
    except Exception as exc:
        report.update(status="BLOCK_NO_BINDING_CHANGED", error= str(exc) if isinstance(exc, Blocked) else type(exc).__name__)
    atomic_file(destination / "preflight.json", (json.dumps(report, sort_keys=True) + "\n").encode(),
                dict(uid=0, gid=0, mode="0o600"))
    return report


STATUS_PATH = Path("/usr/local/libexec/quant-v2-status")
ORIGINAL_STATUS_SHA256 = "ef7b72d1b15ff497c36c01d3b7eda023725c2d810a21b4d845583bf0f8cda074"
CORE = "/opt/quant-research/releases/a67ffec48fff895d5edc42171855e2213e49cf0d"


def status_wrapper():
    """Preserve all original validators, adapting only their historical ref check.

    The validation copy is never written or supplied to the scientific worker.
    Qualification/activation controls and immutable releases stay unchanged.
    """
    code = '''import hashlib,json,os,sys
from pathlib import Path
core=Path("CORE_PATH")
assert os.geteuid()==0 and len(sys.argv)==1
assert hashlib.sha256((core/"deploy/oracle_v2_deploy.py").read_bytes()).hexdigest()=="0073965f912e90821797ae998c538aeefe1b574b20c406c2685028d47f8f5da6"
sys.path.insert(0,str(core))
from deploy import oracle_v2_deploy as original
config=json.loads(original.CONFIG.read_text())
assert config.get("branch") in ("code/canonical",original.BRANCH)
validation=dict(config,branch=original.BRANCH)
assert original.validate_config(validation)==core
assert original.CURRENT.resolve()==core
os.chdir(core)
result=original.status(config)
result["state_branch"]=config["branch"]
print(json.dumps(result,sort_keys=True))
'''.replace("CORE_PATH", CORE)
    return ("#!/bin/sh\n[ \"$#\" -eq 0 ] || exit 64\nexec /usr/bin/env -i "
            "PATH=/usr/sbin:/usr/bin:/sbin:/bin HOME=/root GIT_TERMINAL_PROMPT=0 "
            "/usr/bin/python3.12 -I -B -c " + shlex.quote(code) + "\n").encode()


def ref_only_bytes(raw, spec):
    value = validate_config(raw, spec)
    pattern = rb'("branch"\s*:\s*")' + re.escape(spec[3].encode()) + rb'(")'
    updated, count = re.subn(pattern, lambda m: m[1] + TARGET.encode() + m[2], raw)
    if count != 1 or json.loads(updated) != dict(value, branch=TARGET):
        raise Blocked("REF_ONLY_SEMANTIC_EQUIVALENCE_NOT_PROVEN")
    return updated


def atomic_file(path, raw, metadata):
    path = Path(path)
    if path.is_symlink():
        raise Blocked("SYMLINK_DESTINATION_REFUSED")
    fd, pending = tempfile.mkstemp(prefix=".quant-ref-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            if path.exists():
                # Keep existing extended attributes/ACLs as well as uid/gid/mode.
                shutil.copystat(path, pending, follow_symlinks=False)
            os.fchown(stream.fileno(), int(metadata["uid"]), int(metadata["gid"]))
            os.fchmod(stream.fileno(), int(metadata["mode"], 8))
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        os.replace(pending, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(directory)
        finally: os.close(directory)
    finally:
        if os.path.exists(pending): os.unlink(pending)


def replace_transaction(before, after, metadata, *, write=atomic_file):
    """Real byte/permission rollback; never clobber an intervening owner edit."""
    for path, raw in before.items():
        st=Path(path).stat()
        identity=dict(uid=st.st_uid,gid=st.st_gid,mode=oct(st.st_mode & 0o777))
        if Path(path).read_bytes() != raw or identity!=metadata[str(path)]:
            raise Blocked("TARGET_CHANGED_BEFORE_TRANSACTION")
    written = []
    try:
        for path, raw in after.items():
            st=Path(path).stat()
            identity=dict(uid=st.st_uid,gid=st.st_gid,mode=oct(st.st_mode & 0o777))
            if Path(path).read_bytes() != before[path] or identity!=metadata[str(path)]:
                raise Blocked("TARGET_CHANGED_IMMEDIATELY_BEFORE_REPLACE")
            written.append(path)
            write(path, raw, metadata[str(path)])
            if Path(path).read_bytes() != raw:
                raise Blocked("REPLACEMENT_BYTE_VERIFICATION_FAILED")
    except Exception:
        for path in reversed(written):
            current = Path(path).read_bytes()
            st=Path(path).stat()
            identity=dict(uid=st.st_uid,gid=st.st_gid,mode=oct(st.st_mode & 0o777))
            if identity!=metadata[str(path)]:
                raise Blocked("OWNER_EDIT_PRESERVED_MANUAL_ROLLBACK_REQUIRED") from None
            if current == before[path]:
                continue
            if current != after[path]:
                raise Blocked("OWNER_EDIT_PRESERVED_MANUAL_ROLLBACK_REQUIRED") from None
            atomic_file(path, before[path], metadata[str(path)])
        raise Blocked("TRANSACTION_FAILED_ROLLBACK_COMPLETED") from None


@contextlib.contextmanager
def worker_lock():
    fd = os.open("/var/lib/quant-research", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        try: fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: raise Blocked("CURRENT_WAKE_RUNNING_RETRY_WITHOUT_KILLING_IT") from None
        yield
    finally: os.close(fd)


def apply_binding(canonical_sha, scope):
    if os.geteuid() != 0:
        raise Blocked("ROOT_REQUIRED")
    with worker_lock():
        report = execute(canonical_sha, scope)
        if report.get("status") != "PASS_BACKUP_AND_READ_ONLY_COMPATIBILITY":
            return report
        directory = Path(report["backup_directory"])
        before, after = {}, {}
        if scope in ("both", "v2"):
            raw = checked_bytes(STATUS_PATH)
            if digest(raw) != ORIGINAL_STATUS_SHA256:
                raise Blocked("FIXED_STATUS_WRAPPER_CHANGED_REVIEW_BEFORE_REPLACING")
            before[STATUS_PATH], after[STATUS_PATH] = raw, status_wrapper()
        for key, spec in selected_specs(scope).items():
            path = Path(spec[0]); raw = checked_bytes(path)
            before[path], after[path] = raw, ref_only_bytes(raw, spec)
        # Reject concurrent root/config/unit/env changes after the read-only probe.
        for path, expected in report["backup_sha256"].items():
            if digest(checked_bytes(path)) != expected:
                raise Blocked("HOST_SURFACE_CHANGED_AFTER_BACKUP")
        if release_signatures(scope)!=report['release_signatures']:
            raise Blocked('DEPLOYED_RELEASE_BYTES_CHANGED_AFTER_PREFLIGHT')
        receipt = dict(operation="EXISTING_HOST_REF_ONLY_MIGRATION", status="PREPARED",
                       canonical_sha=canonical_sha, scope=scope, backup_directory=str(directory),
                       before={str(p): digest(v) for p,v in before.items()},
                       after={str(p): digest(v) for p,v in after.items()},
                       boot_id=report["boot_id"], applied_monotonic_us=time.monotonic_ns() // 1000,
                       observed_automatic_wakes=[], timer_mutations=0, release_mutations=0,
                       model_mutations=0, remote_writes=0)
        record = directory / "migration.json"
        atomic_file(record, (json.dumps(receipt, sort_keys=True)+"\n").encode(), dict(uid=0,gid=0,mode="0o600"))
        try:
            replace_transaction(before, after, report["backup_file_metadata"])
            if unit_state("quant-research-worker-v2.timer") != report["timer_before"]:
                raise Blocked("TIMER_CHANGED_DURING_TRANSACTION")
            if unit_state("quant-research-worker.timer") != report["v1_timer_before"]:
                raise Blocked("FALLBACK_TIMER_CHANGED_DURING_TRANSACTION")
            if release_signatures(scope)!=report['release_signatures']:
                raise Blocked('DEPLOYED_RELEASE_BYTES_CHANGED_DURING_TRANSACTION')
            if scope in ("both", "v2"):
                control = subprocess.run([str(STATUS_PATH)], capture_output=True, text=True, timeout=40)
                value = json.loads(control.stdout) if control.returncode == 0 else {}
                if (value.get("state_branch") != TARGET or value.get("model_health",{}).get("status") != "PASS"
                        or value.get("release_sha") != CONFIGS["v2"][2] or value.get("timer") != "active/enabled"):
                    raise Blocked("POST_REBIND_STATUS_NOT_HEALTHY")
        except Exception:
            # Includes status/continuity failure after the three successful writes.
            current = {p: Path(p).read_bytes() for p in before}
            if any(current[p] not in (before[p], after[p]) for p in before):
                receipt["status"] = "BLOCK_OWNER_EDIT_PRESERVED"
            else:
                replace_transaction(current, before, report["backup_file_metadata"])
                receipt["status"] = "BLOCK_ROLLED_BACK"
            atomic_file(record, (json.dumps(receipt,sort_keys=True)+"\n").encode(), dict(uid=0,gid=0,mode="0o600"))
            return receipt
        receipt.update(status="REBOUND_TWO_AUTOMATIC_WAKES_PENDING", applied_at=datetime.now(timezone.utc).isoformat())
        atomic_file(record, (json.dumps(receipt,sort_keys=True)+"\n").encode(), dict(uid=0,gid=0,mode="0o600"))
        return receipt


def rollback_binding(directory):
    if os.geteuid() != 0:
        raise Blocked("ROOT_REQUIRED")
    directory = Path(directory)
    if directory.parent != Path("/var/backups") or not re.fullmatch(r"quant-canonical-rebind-[0-9TZ.]+", directory.name):
        raise Blocked("UNEXPECTED_BACKUP_DIRECTORY")
    if directory.is_symlink() or directory.stat().st_uid != 0 or directory.stat().st_mode & 0o077:
        raise Blocked("BACKUP_DIRECTORY_NOT_PRIVATE_ROOT_OWNED")
    pre = json.loads(checked_bytes(directory / "preflight.json"))
    receipt = json.loads(checked_bytes(directory / "migration.json"))
    allowed = {str(STATUS_PATH), *(s[0] for s in CONFIGS.values())}
    if not receipt["before"] or not set(receipt["before"]) <= allowed or set(receipt["before"]) != set(receipt["after"]):
        raise Blocked("ROLLBACK_TARGET_OUTSIDE_FIXED_BINDINGS")
    with worker_lock():
        if release_signatures(receipt['scope'])!=pre['release_signatures']:
            raise Blocked('RELEASE_CHANGED_CANONICAL_RECOVERY_REQUIRED')
        for key,spec in selected_specs(receipt['scope']).items():
            probe_code=ROLLBACK_SNAPSHOT_PROBE
            cmd=['runuser','-u','quant-research','--','env','HOME=/var/lib/quant-research',
                 '/usr/bin/python3.12','-I','-B','-c',probe_code,
                 '/opt/quant-research/releases/'+spec[2],spec[0],spec[3],key]
            try: proof=bounded_probe(cmd)
            except Exception: raise Blocked('OLD_REF_UNAVAILABLE_CANONICAL_RECOVERY_REQUIRED') from None
            validate_rollback_surface(pre['probes'][key],proof,v2=key=='v2')
        before, restore = {}, {}
        for name, old_hash in reversed(list(receipt["before"].items())):
            path = Path(name); current = checked_bytes(path)
            raw = checked_bytes(directory / name.lstrip("/"))
            if digest(raw) != old_hash or digest(current) not in (old_hash, receipt["after"][name]):
                raise Blocked("ROLLBACK_HASH_MISMATCH_OR_OWNER_EDIT")
            before[path], restore[path] = current, raw
        replace_transaction(before, restore, pre["backup_file_metadata"])
        receipt.update(status="ROLLED_BACK_EXACT_BYTES_AND_PERMISSIONS", rolled_back_at=datetime.now(timezone.utc).isoformat())
        atomic_file(directory / "migration.json", (json.dumps(receipt,sort_keys=True)+"\n").encode(),dict(uid=0,gid=0,mode="0o600"))
        return receipt


ROLLBACK_SNAPSHOT_PROBE=r'''
import hashlib,json,sys
from pathlib import Path
release,config_path,old_branch,flavor=sys.argv[1:]
sys.path.insert(0,release)
from research.research_os.github_state import GitHubStateStore
config=json.loads(Path(config_path).read_text())
class ReadOnlyStore(GitHubStateStore):
    def commit(self,*a,**kw):raise RuntimeError('ROLLBACK_REMOTE_WRITE_FORBIDDEN')
def surface(snapshot):
    ignored=('research/research_os/runtime/worker_wakes/','research/research_os/artifacts/live-observation/')
    value={p:h for p,h in snapshot.blobs.items() if not p.startswith(ignored)}
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
old=ReadOnlyStore(cache=Path(config['cache']),repository=config['repository'],branch=old_branch)
old._git('fetch','--no-tags',old.remote,'refs/heads/'+old_branch)
old_digest=None
if flavor=='v2':
    with old.snapshot() as s:old_digest=surface(s)
canonical=ReadOnlyStore(cache=Path(config['cache']),repository=config['repository'],branch='code/canonical')
with canonical.snapshot() as s:canonical_digest=surface(s)
print(json.dumps(dict(old_ref_exists=True,stable_canonical_surface_sha256=canonical_digest,
                     stable_old_surface_sha256=old_digest)))
'''


def validate_rollback_surface(before, proof, *, v2=False):
    canonical=before.get('stable_canonical_surface_sha256')
    if (not proof.get('old_ref_exists') or not canonical
            or proof.get('stable_canonical_surface_sha256')!=canonical
            or (v2 and (not before.get('stable_old_surface_sha256')
                        or proof.get('stable_old_surface_sha256')!=before['stable_old_surface_sha256']))):
        raise Blocked('STATE_ADVANCED_OR_OLD_REF_RETIRED_CANONICAL_RECOVERY_REQUIRED')


def automatic_wake(timer, service, rows, receipt):
    """One observed timer trigger, successful service invocation and its JSON.

    Observe twice on separate triggers; never infer two automatic wakes merely
    from two old journal entries or from an active timer.
    """
    if timer.get("ActiveState") != "active" or timer.get("UnitFileState") != "enabled":
        return None
    if service.get("Result") != "success" or service.get("ExecMainStatus") != "0":
        return None
    try:
        trigger = int(timer["LastTriggerUSecMonotonic"])
        start = int(service["ExecMainStartTimestampMonotonic"])
    except (KeyError, ValueError, TypeError):
        return None
    if trigger <= receipt["applied_monotonic_us"] or not 0 <= start - trigger <= 10_000_000:
        return None
    invocation = service.get("InvocationID")
    if not invocation:
        return None
    for row in reversed(rows):
        if row.get("_SYSTEMD_INVOCATION_ID") != invocation:
            continue
        try: value = json.loads(row.get("MESSAGE", ""))
        except (ValueError, TypeError): continue
        if (value.get("state_branch") != TARGET or value.get("release_sha") != CONFIGS["v2"][2]
                or not re.fullmatch(r"[a-f0-9]{40}", value.get("input_head", "")) or value.get("hosted_model_calls") != 0
                or any(value.get("authority", {}).get(k) is not False for k in AUTHORITY)
                or value.get("status") in (None, "BLOCKED", "RETRY_FRESH_STATE_NEXT_WAKE", "DRY_RUN")):
            continue
        return dict(invocation_id=invocation, timer_trigger_monotonic_us=trigger,
                    service_start_monotonic_us=start,
                    journal_timestamp_us=row.get("__REALTIME_TIMESTAMP"),
                    **{k:value.get(k) for k in ("status","release_sha","state_branch","input_head","output_commit","writes","authority","hosted_model_calls")})
    return None


def append_automatic_witness(receipt, witness):
    prior=receipt['observed_automatic_wakes']
    if not witness or len(prior)>=2 or witness['invocation_id'] in {w['invocation_id'] for w in prior}:
        return False
    if prior and witness['timer_trigger_monotonic_us']<=prior[-1]['timer_trigger_monotonic_us']:
        return False
    prior.append(witness)
    return True


def show_properties(unit, properties):
    child = subprocess.run(["systemctl","show",unit,*["--property="+p for p in properties]],
                           capture_output=True,text=True,check=True,timeout=10)
    return dict(line.split("=",1) for line in child.stdout.splitlines() if "=" in line)


def observe_wakes(directory, wait_seconds=0):
    if os.geteuid()!=0 or not 0 <= wait_seconds <= 1560:
        raise Blocked("ROOT_AND_BOUNDED_OBSERVATION_REQUIRED")
    directory=Path(directory)
    if (directory.parent!=Path('/var/backups') or directory.is_symlink()
            or not re.fullmatch(r'quant-canonical-rebind-[0-9TZ.]+',directory.name)
            or directory.stat().st_uid!=0 or directory.stat().st_mode & 0o077):
        raise Blocked("UNEXPECTED_PRIVATE_MIGRATION_DIRECTORY")
    path=directory/'migration.json'
    receipt=json.loads(checked_bytes(path))
    pre=json.loads(checked_bytes(directory/'preflight.json'))
    if receipt.get('scope') not in ('v2','both') or receipt.get('status') not in (
            'REBOUND_TWO_AUTOMATIC_WAKES_PENDING','PASS_TWO_AUTOMATIC_WAKES'):
        raise Blocked("SUCCESSFUL_V2_REBIND_RECEIPT_REQUIRED")
    deadline=time.monotonic()+wait_seconds
    if release_signatures(receipt['scope'])!=pre['release_signatures']:
        raise Blocked('DEPLOYED_RELEASE_BYTES_CHANGED_SINCE_APPLICATION')
    while True:
        if Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=receipt['boot_id']:
            raise Blocked("BOOT_CHANGED_RECONCILE_OBSERVATION_IDENTITY")
        for name,expected in receipt['after'].items():
            if digest(checked_bytes(name))!=expected:
                raise Blocked("REBIND_BYTES_CHANGED_SINCE_APPLICATION")
        for name,expected in pre['backup_sha256'].items():
            if name not in receipt['after'] and digest(checked_bytes(name))!=expected:
                raise Blocked("UNIT_RELEASE_ENV_OR_ROLLBACK_SURFACE_CHANGED")
        timer=show_properties('quant-research-worker-v2.timer',('ActiveState','UnitFileState','LastTriggerUSec','LastTriggerUSecMonotonic'))
        if timer.get('ActiveState')!='active' or timer.get('UnitFileState')!='enabled':
            raise Blocked("EXISTING_V2_TIMER_NO_LONGER_ACTIVE_ENABLED")
        fallback=unit_state('quant-research-worker.timer')
        if fallback.get('ActiveState')!='inactive' or fallback.get('UnitFileState')!='disabled':
            raise Blocked('V1_FALLBACK_NO_LONGER_INACTIVE_DISABLED')
        service=show_properties('quant-research-worker-v2.service',('InvocationID','Result','ExecMainStatus','ExecMainStartTimestampMonotonic'))
        child=subprocess.run(['journalctl','--boot','--unit=quant-research-worker-v2.service','--output=json','--no-pager','-n','200'],
                             capture_output=True,text=True,check=True,timeout=15)
        rows=[]
        for line in child.stdout.splitlines():
            try: rows.append(json.loads(line))
            except ValueError: continue
        witness=automatic_wake(timer,service,rows,receipt)
        if append_automatic_witness(receipt,witness):
            atomic_file(path,(json.dumps(receipt,sort_keys=True)+'\n').encode(),dict(uid=0,gid=0,mode='0o600'))
        if len(receipt['observed_automatic_wakes'])>=2:
            if release_signatures(receipt['scope'])!=pre['release_signatures']:
                raise Blocked('DEPLOYED_RELEASE_BYTES_CHANGED_DURING_OBSERVATION')
            control=subprocess.run([str(STATUS_PATH)],capture_output=True,text=True,timeout=40)
            value=json.loads(control.stdout) if control.returncode==0 else {}
            if (value.get('state_branch')!=TARGET or value.get('model_health',{}).get('status')!='PASS'
                    or value.get('timer')!='active/enabled' or value.get('v1_timer')!='inactive'):
                raise Blocked("POST_TWO_WAKE_STATUS_OR_FALLBACK_NOT_HEALTHY")
            receipt.update(status='PASS_TWO_AUTOMATIC_WAKES',verified_at=datetime.now(timezone.utc).isoformat(),
                           model_health='PASS',v1_timer='inactive',manual_worker_starts_by_this_tool=0)
            atomic_file(path,(json.dumps(receipt,sort_keys=True)+'\n').encode(),dict(uid=0,gid=0,mode='0o600'))
            return receipt
        if time.monotonic()>=deadline:
            return receipt
        time.sleep(min(15,max(0,deadline-time.monotonic())))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical-sha")
    parser.add_argument("--action", choices=("preflight", "apply", "rollback", "observe"), default="preflight")
    parser.add_argument("--scope", choices=("both", "v1", "v2"), default="both")
    parser.add_argument("--backup-directory")
    parser.add_argument("--wait-seconds",type=int,default=0)
    args = parser.parse_args()
    try:
        if args.action == "rollback":
            result = rollback_binding(args.backup_directory or "")
        elif args.action == "observe":
            result = observe_wakes(args.backup_directory or "",args.wait_seconds)
        elif args.action == "apply":
            result = apply_binding(args.canonical_sha, args.scope)
        else:
            result = execute(args.canonical_sha, args.scope)
    except Exception as exc:
        result = {"operation": "BACKUP_AND_READ_ONLY_CANONICAL_PREFLIGHT", "status": "BLOCK_NO_BINDING_CHANGED",
                  "error": str(exc) if isinstance(exc, Blocked) else type(exc).__name__}
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("status") in ("PASS_BACKUP_AND_READ_ONLY_COMPATIBILITY", "REBOUND_TWO_AUTOMATIC_WAKES_PENDING", "ROLLED_BACK_EXACT_BYTES_AND_PERMISSIONS", "PASS_TWO_AUTOMATIC_WAKES") else 2


if __name__ == "__main__":
    raise SystemExit(main())
