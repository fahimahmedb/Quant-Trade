#!/usr/bin/env python3
"""Run on the existing host as root. Read only; emits allowlisted metadata."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def service(unit):
    fields = ("ActiveState", "SubState", "UnitFileState", "Result", "ExecMainStatus",
              "InvocationID", "FragmentPath", "DropInPaths", "WorkingDirectory",
              "LastTriggerUSec", "NextElapseUSecRealtime")
    result = subprocess.run(["systemctl", "show", unit, *["--property=" + f for f in fields]],
                            capture_output=True, text=True, timeout=10)
    report = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
    report["query_exit"] = result.returncode
    # Only these known markers are emitted, never raw ExecStart or Environment.
    command = subprocess.run(["systemctl", "show", unit, "--property=ExecStart", "--value"],
                             capture_output=True, text=True, timeout=10).stdout
    report["entrypoint_markers"] = [name for name in (
        "research.research_os.oracle_worker",
        "research.research_os.oracle_worker_v2", "research.research_os.host_wake",
        "scripts/gpt_oss_orchestrator.py")
        if re.search(re.escape(name) + r"(?![A-Za-z0-9_])", command)]
    report["configured_worker_paths"] = sorted(set(re.findall(
        r"/etc/quant-research(?:-v2)?/worker\.json", command)))
    return report


def config(path):
    p = Path(path)
    if not p.exists():
        return {"exists": False}
    raw = p.read_bytes(); value = json.loads(raw); st = p.stat()
    keys = ("repository", "branch", "release_sha", "research_contract_version", "cache",
            "economic_experiment_authorized", "prospective_observation_authorized",
            "real_capital_authorized", "live_trading_authorized")
    return {"exists": True, "sha256": sha(raw), "uid": st.st_uid,
            "gid": st.st_gid, "mode": oct(st.st_mode & 0o777),
            "settings": {key: value[key] for key in keys if key in value}}


def release(path):
    p = Path(path)
    if not p.exists():
        return {"exists": False}
    receipt = p / ".quant_release_receipt.json"
    report = {"exists": True, "resolved_path": str(p.resolve())}
    if receipt.is_file():
        raw = receipt.read_bytes(); value = json.loads(raw)
        report.update(receipt_sha256=sha(raw), identity={key: value[key]
                      for key in ("sha", "commit_sha", "release_sha", "path") if key in value})
    return report


def inventory():
    if os.geteuid() != 0:
        raise ValueError("ROOT_READ_ACCESS_REQUIRED")
    return {"operation": "READ_ONLY_HOST_INVENTORY", "host_mutations": 0,
            "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
            "units": {unit: service(unit) for unit in (
                "quant-research-worker.service", "quant-research-worker.timer",
                "quant-research-worker-v2.service", "quant-research-worker-v2.timer")},
            "configs": {p: config(p) for p in (
                "/etc/quant-research/worker.json", "/etc/quant-research-v2/worker.json")},
            "releases": {p: release(p) for p in (
                "/opt/quant-research/current", "/opt/quant-research-v2/current")},
            "fallback_absence_proven": False,
            "next_action": "Review exact inventory, save private rollback copies, qualify ref-only change, then observe two automatic post-rebind wakes. No host mutation is implemented by this inventory job."}


if __name__ == "__main__":
    try:
        print(json.dumps(inventory(), sort_keys=True))
    except Exception as exc:
        # Do not serialize config payloads, command lines, credentials or tracebacks.
        print(json.dumps({"operation": "READ_ONLY_HOST_INVENTORY", "status": "BLOCK",
                          "error_type": type(exc).__name__}))
        raise SystemExit(2)
