#!/usr/bin/env python3
"""Real V2 subprocess + fresh public GitHub reads, with remote writes disabled."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
REPOSITORY = "fahimahmedb/Quant-Trade"
BRANCH = "builder/oracle-v2-core-20261020"
AUTHORITY_KEYS = (
    "economic_experiment_authorized", "prospective_observation_authorized",
    "real_capital_authorized", "live_trading_authorized",
)


def prove(sha, output, scope):
    if not re.fullmatch(r"[a-f0-9]{40}", sha):
        raise ValueError("EXACT_CODE_SHA_REQUIRED")
    git = shutil.which("git")
    if not git:
        raise ValueError("GIT_REQUIRED")
    installed = ROOT / ".quant_release_receipt.json"
    if installed.exists():
        from deploy.oracle_release_install import _validate_release_receipt
        receipt = _validate_release_receipt(json.loads(installed.read_text()), sha)
        if Path(receipt["path"]).resolve() != ROOT:
            raise ValueError("EXECUTABLE_RELEASE_PATH_MISMATCH")
    else:
        observed = subprocess.check_output([git, "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        if observed != sha:
            raise ValueError("CODE_HEAD_MISMATCH")
        dirty = subprocess.check_output([git, "status", "--porcelain", "--untracked-files=normal", "--",
                                         "research", "scripts/prove_oracle_v2_dry_run.py"], cwd=ROOT)
        if dirty:
            raise ValueError("DIRTY_EXECUTABLE_TREE_CANNOT_PROVE_EXACT_SHA")
    with tempfile.TemporaryDirectory(prefix="quant-v2-readonly-") as directory:
        temp = Path(directory)
        trace = temp / "git-trace.jsonl"
        # No inherited credential helper, SSH agent or injected Git config. Only
        # actual HTTPS read transport is allowed. Any push is rewritten to a
        # nonexistent file URL, whose protocol is itself forbidden.
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k not in (
            "GH_TOKEN", "GITHUB_TOKEN", "SSH_AUTH_SOCK", "OPENAI_API_KEY", "ANTHROPIC_API_KEY")}
        if os.environ.get("GIT_SSL_CAINFO"):
            env["GIT_SSL_CAINFO"] = os.environ["GIT_SSL_CAINFO"]
        env.update(HOME=str(temp), GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                   GIT_TERMINAL_PROMPT="0", GIT_ALLOW_PROTOCOL="https", GIT_CONFIG_COUNT="2",
                   GIT_CONFIG_KEY_0="url." + (temp / "FORBIDDEN_PUSH").as_uri() + "/.pushInsteadOf",
                   GIT_CONFIG_VALUE_0="https://github.com/", GIT_CONFIG_KEY_1="credential.helper",
                   GIT_CONFIG_VALUE_1="", GIT_TRACE2_EVENT=str(trace), PYTHONDONTWRITEBYTECODE="1")
        config = dict(repository=REPOSITORY, branch=BRANCH, release_sha=sha, cache=str(temp / "state.git"),
                      worker_id="v2-readonly-proof", lane="auto", research_contract_version="v2-core")
        config.update({key: False for key in AUTHORITY_KEYS})
        config_path = temp / "worker.json"
        config_path.write_text(json.dumps(config))
        process = subprocess.run([sys.executable, "-B", "-s", "-m", "research.research_os.oracle_worker_v2",
                                  "--config", str(config_path), "--mode", "dry-run"],
                                 cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
        if process.returncode:
            raise RuntimeError("REAL_V2_ENTRYPOINT_FAILED:" + process.stdout[-1500:] + process.stderr[-500:])
        result = json.loads(process.stdout)
        events = [json.loads(line) for line in trace.read_text().splitlines()]
        starts = [event["argv"] for event in events if event.get("event") == "start"]
        pushes = [args for args in starts if "push" in args or "send-pack" in args]
        fetches = [args for args in starts if "fetch" in args]
        if pushes or len(fetches) < 2:
            raise ValueError("NO_WRITE_OR_FRESH_FETCH_PROOF_FAILED")
        head = subprocess.check_output([git, "--git-dir=" + config["cache"], "rev-parse", "refs/quant/observed"],
                                       env=env, text=True, timeout=10).strip()
        if (result.get("status") != "DRY_RUN" or result.get("writes") != 0
                or result.get("research_contract_version") != "v2-core"
                or result.get("input_head") != head or result.get("hosted_model_calls") != 0
                or result.get("preflight", {}).get("status") != "PASS"
                or any(result.get("authority", {}).get(key) is not False for key in AUTHORITY_KEYS)):
            raise ValueError("V2_DRY_RUN_CONTRACT_NOT_PROVEN")
        proof = dict(schema_version="oracle-v2-real-github-dry-run-v1", status="PASS",
                     evidence_scope=scope, executable_sha=sha, github_state_head=head,
                     repository=REPOSITORY, branch=BRANCH, research_contract_version="v2-core",
                     entrypoint="research.research_os.oracle_worker_v2", real_subprocess=True,
                     mocks_used=False, github_writes=0, push_attempts=0, real_fetch_commands=len(fetches),
                     hosted_model_calls=0, model_configured=False, authority=result["authority"],
                     worker_result=result, git_trace_sha256=hashlib.sha256(trace.read_bytes()).hexdigest(),
                     limitations="Read-only integration proof; does not prove runtime activation or scientific throughput.")
        if scope == "LIVE_ORACLE_GITHUB_READ_ONLY":
            from deploy.oracle_h24_canary import instance_identity
            proof["instance"] = instance_identity("ocid1.instance.oc1.eu-paris-1.anrwiljrtoradqacmugziwzu3sls2orieua6i7vkjveiq7q5wsiypa3mejpa")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(proof, sort_keys=True, indent=2) + "\n")
        return proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--scope", choices=("CI_GITHUB_READ_ONLY", "LOCAL_GITHUB_READ_ONLY", "LIVE_ORACLE_GITHUB_READ_ONLY"),
                        default="LOCAL_GITHUB_READ_ONLY")
    args = parser.parse_args()
    proof = prove(args.sha, args.output, args.scope)
    print(json.dumps({key: proof[key] for key in ("status", "executable_sha", "github_state_head", "github_writes",
                                                "push_attempts", "real_fetch_commands", "research_contract_version")}))


if __name__ == "__main__":
    main()
