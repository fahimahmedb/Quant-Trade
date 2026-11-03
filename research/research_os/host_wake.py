"""Route one existing systemd timer wake to exactly one bounded worker.

Default behavior is the already-qualified Research OS worker.  When the explicit
Codex orchestration feature flag is enabled, the same timer wake executes one
synthetic GPT-OSS/Codex control-plane step instead.  This module never runs both
paths in one wake and does not create another daemon or timer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import sys

STATE_ROOT = Path("/var/lib/quant-research")


def _release_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _codex_environment(worker_version="v1") -> dict[str, str]:
    env = os.environ.copy()
    raw_root = env.get("QUANT_CODEX_ORCHESTRATION_ROOT", "").strip()
    if not raw_root:
        raise SystemExit("QUANT_CODEX_ORCHESTRATION_ROOT_REQUIRED_ON_HOST")
    root = Path(raw_root).resolve()
    state_root = (STATE_ROOT if worker_version == "v1" else Path("/var/lib/quant-research-v2")).resolve()
    if root == state_root or not root.is_relative_to(state_root):
        raise SystemExit("QUANT_CODEX_ORCHESTRATION_ROOT_MUST_BE_STATE_SUBDIRECTORY")

    # The systemd unit has ProtectSystem=strict and only /var/lib/quant-research
    # is writable. Require the orchestration ledger there rather than silently
    # falling back to the read-only release tree.
    env["QUANT_CODEX_ORCHESTRATION_ROOT"] = str(root)

    # The outer orchestration script imports autonomous_research from src, while
    # its nested local GPT-OSS decision process imports research.* from the
    # release root.  Supply both paths once at the wake boundary so the runtime
    # matches the already-qualified handoff preflight environment.
    release = _release_root()
    existing = env.get("PYTHONPATH", "")
    bootstrap = [str(release / "src"), str(release)]
    if existing:
        bootstrap.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(bootstrap)
    return env



def _terminal_continuation(env):
    """Verify frozen read-only Codex completion before a subsequent V2 research wake."""
    task_id = env.get("QUANT_CODEX_TASK_ID", "").strip()
    if not task_id:
        return None
    safe = hashlib.sha256(task_id.encode("utf-8")).hexdigest()[:24]
    root = Path(env["QUANT_CODEX_ORCHESTRATION_ROOT"]) / "runtime" / "codex_orchestration"
    state_file = root / (safe + ".json")
    receipt_file = root / (safe + ".receipts.jsonl")
    if not state_file.is_file():
        return None
    state_raw = state_file.read_bytes()
    try:
        state = json.loads(state_raw)
    except (ValueError, UnicodeError) as exc:
        raise SystemExit("F4_INVALID_DURABLE_STATE") from exc
    if not isinstance(state, dict):
        raise SystemExit("F4_INVALID_DURABLE_STATE")
    if state.get("status") != "DONE":
        return None

    def reject(reason):
        raise SystemExit("F4_CAUSAL_REJECT_" + reason)

    sha = state.get("expected_head_sha")
    project_sha = state.get("project_head_sha")
    if (not isinstance(sha, str) or re.fullmatch(r"[0-9a-f]{40}", sha) is None
            or env.get("QUANT_CODEX_EXPECTED_HEAD_SHA") != sha
            or state.get("result_sha") != sha):
        reject("HEAD")
    if (state.get("task_id") != task_id
            or state.get("repository") != env.get("QUANT_REPOSITORY")
            or str(state.get("issue_number")) != env.get("QUANT_CODEX_ISSUE_NUMBER")
            or state.get("target_branch") != env.get("QUANT_CODEX_TARGET_BRANCH")
            or state.get("project_branch") != env.get("QUANT_CODEX_PROJECT_BRANCH")
            or state.get("readonly_probe") is not True):
        reject("SUBJECT")
    if not isinstance(project_sha, str) or re.fullmatch(r"[0-9a-f]{40}", project_sha) is None:
        reject("PROJECT")
    attempt = state.get("attempt")
    if type(attempt) is not int or attempt < 1:
        reject("ATTEMPT")
    dispatch = hashlib.sha256(f"{task_id}\0{sha}\0{attempt}".encode("utf-8")).hexdigest()
    if state.get("dispatch_id") != dispatch or (state.get("last_decision") or {}).get("action") != "DONE":
        reject("DISPATCH_OR_DECISION")
    if not receipt_file.is_file():
        reject("MISSING_RECEIPTS")
    receipts_raw = receipt_file.read_bytes()
    try:
        receipts = [json.loads(line) for line in receipts_raw.splitlines() if line.strip()]
    except (ValueError, UnicodeError) as exc:
        raise SystemExit("F4_INVALID_DURABLE_RECEIPTS") from exc
    required = ["PROJECT_AUTHORITY_FENCED", "RESULT_CAUSALLY_BOUND",
                "READ_ONLY_PROBE_RESULT_CONSUMED", "TERMINAL_DONE"]
    observed = []
    for item in receipts:
        if item.get("task_id") != task_id or item.get("dispatch_id") != dispatch:
            continue
        event = item.get("event")
        if event not in required:
            continue
        if item.get("expected_head_sha") != sha:
            reject("RECEIPT_HEAD")
        if event != required[0] and item.get("result_sha") != sha:
            reject("RECEIPT_RESULT")
        if event == required[2] and (
                (item.get("details") or {}).get("action") != "DONE"
                or (item.get("details") or {}).get("code_promotion_authorized") is not False):
            reject("UNCONSUMED_RESULT")
        if event == required[3] and item.get("status") != "DONE":
            reject("TERMINAL_STATUS")
        observed.append(event)
    if observed != required or not receipts or receipts[-1].get("event") != required[-1]:
        reject("CAUSAL_CHAIN")
    if state_file.read_bytes() != state_raw or receipt_file.read_bytes() != receipts_raw:
        reject("MOVED_DURING_READ")
    return {
        "schema": "f4-terminal-research-v1",
        "predecessor_task_id": task_id,
        "predecessor_dispatch_id": dispatch,
        "predecessor_project_sha": project_sha,
        "predecessor_result_sha": sha,
        "predecessor_terminal_receipt_sha256": hashlib.sha256(receipts_raw).hexdigest(),
    }


def _exec_one(config: str, worker_version="v1") -> None:
    flag = os.environ.get("QUANT_CODEX_ORCHESTRATION_ENABLED", "0").strip()
    if flag not in ("", "0", "1"):
        raise SystemExit("INVALID_QUANT_CODEX_ORCHESTRATION_ENABLED")

    if flag == "1":
        env = _codex_environment(worker_version)
        cause = _terminal_continuation(env) if worker_version == "v2" else None
        if cause is None:
            script = _release_root() / "scripts" / "gpt_oss_orchestrator.py"
            argv = [sys.executable, str(script)]
        else:
            env["QUANT_F4_CAUSAL_PREDECESSOR"] = json.dumps(cause, sort_keys=True)
            argv = [sys.executable, "-m", "research.research_os.oracle_worker_v2",
                    "--config", config]
    else:
        env = os.environ.copy()
        argv = [
            sys.executable,
            "-m",
            "research.research_os.oracle_worker" + ("_v2" if worker_version == "v2" else ""),
            "--config",
            config,
        ]

    # execve replaces this router process in production, preserving the
    # one-process/one-wake semantics and the existing systemd lock/sandbox.
    os.execve(sys.executable, argv, env)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--worker-version", choices=("v1", "v2"), default="v1")
    args = parser.parse_args(argv)
    _exec_one(args.config, args.worker_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
