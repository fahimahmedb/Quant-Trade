#!/usr/bin/env python3
"""Standalone Owner/root bootstrap; reuse V1 assets and leave V1 running."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import subprocess
import urllib.request

QUALIFICATION_SOURCE_BRANCHES = (
    "builder/oracle-v2-core-20261020", "builder/v2-forward-20261020",
)
V2_UNITS = ("quant-research-worker-v2.timer", "quant-research-worker-v2.service")


def assert_bootstrap_target_idle():
    """Read host state before publishing an archive; this is not an upgrade path."""
    if os.geteuid() != 0:
        raise ValueError("ROOT_REQUIRED_FOR_V2_PREPARATION")
    for unit in V2_UNITS:
        result = subprocess.run(["systemctl", "show", unit, "--property=LoadState,ActiveState"],
                                capture_output=True, text=True)
        states = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
        absent = (states.get("LoadState") == "not-found" and states.get("ActiveState") == "inactive"
                  and result.returncode in (0, 1, 4))
        if (result.returncode and not absent) or states.get("LoadState") not in ("loaded", "not-found"):
            raise ValueError("V2_BOOTSTRAP_RUNTIME_STATE_UNAVAILABLE:" + unit)
        if states.get("ActiveState") in ("active", "activating", "reloading", "deactivating"):
            raise ValueError("V2_RUNNING_RELEASE_REQUIRES_EXPLICIT_REPAIR_HANDOFF")
        if states.get("ActiveState") not in ("inactive", "failed"):
            raise ValueError("V2_BOOTSTRAP_RUNTIME_STATE_UNAVAILABLE:" + unit)


def prepare_installed_release(release, v2_run, sec_run, *, qualification_source_branch=None):
    # CP1 imports research modules while the archive still lives in staging.
    # After its atomic rename, cached package __path__ values point to the old
    # directory. A fresh interpreter binds imports to the published release.
    if (qualification_source_branch is not None
            and qualification_source_branch not in QUALIFICATION_SOURCE_BRANCHES):
        raise ValueError("V2_QUALIFICATION_SOURCE_BRANCH_NOT_AUTHORIZED")
    keyword = ',qualification_source_branch=sys.argv[4]' if qualification_source_branch is not None else ''
    program = ('import json,os,sys; p=sys.argv[1]; os.chdir(p); sys.path.insert(0,p); '
               'from deploy.oracle_v2_deploy import prepare; from pathlib import Path; '
               'print(json.dumps(prepare(Path(p),int(sys.argv[2]),int(sys.argv[3])' + keyword + '),sort_keys=True))')
    extra = [qualification_source_branch] if qualification_source_branch is not None else []
    subprocess.run([sys.executable, "-I", "-B", "-c", program, str(release), str(v2_run), str(sec_run), *extra],
                   cwd="/", check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--v2-ci-run", required=True, type=int)
    parser.add_argument("--sec-ci-run", required=True, type=int)
    parser.add_argument("--qualification-source-branch", choices=QUALIFICATION_SOURCE_BRANCHES,
                        default=QUALIFICATION_SOURCE_BRANCHES[0])
    args = parser.parse_args()
    if len(args.sha) != 40 or any(c not in "0123456789abcdef" for c in args.sha):
        raise ValueError("EXACT_RELEASE_SHA_REQUIRED")
    assert_bootstrap_target_idle()
    for run_id, name in ((args.v2_ci_run, "Oracle V2 Core"), (args.sec_ci_run, "SEC P0 pre-t0 gate")):
        request = urllib.request.Request(f"https://api.github.com/repos/fahimahmedb/Quant-Trade/actions/runs/{run_id}",
                                         headers={"User-Agent": "Quant-Trade-V2-bootstrap"})
        with urllib.request.urlopen(request, timeout=30) as response:
            run = json.loads(response.read(2 * 1024 * 1024))
        if (run.get("head_sha") != args.sha or run.get("head_branch") != args.qualification_source_branch
                or run.get("name") != name or run.get("status") != "completed" or run.get("conclusion") != "success"):
            raise ValueError("V2_BOOTSTRAP_REQUIRES_BOTH_EXACT_RELEASE_CI_GATES")
    url = "https://raw.githubusercontent.com/fahimahmedb/Quant-Trade/f3943830e20b05d926d3013501573b8b21fdace7/deploy/oracle_v1_host_prepare.py"
    data = urllib.request.urlopen(url, timeout=30).read(262145)
    if len(data) > 262144 or hashlib.sha256(data).hexdigest() != "4f16891393a7adaea4b9c55ff29c479860ffc08d770b82e48ec24a0211a1e44f":
        raise ValueError("PINNED_V1_BOOTSTRAP_HASH_MISMATCH")
    namespace = {"__name__": "v1_installer_bootstrap", "__file__": url}
    exec(compile(data, url, "exec"), namespace)
    # Recheck after remote qualification/download, immediately before publication.
    assert_bootstrap_target_idle()
    receipt = namespace["bootstrap"](args.sha)
    release = Path(receipt["path"])
    prepare_installed_release(release, args.v2_ci_run, args.sec_ci_run,
                              qualification_source_branch=args.qualification_source_branch)


if __name__ == "__main__": main()
