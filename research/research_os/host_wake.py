"""Route one existing systemd timer wake to exactly one bounded worker.

Default behavior is the already-qualified Research OS worker.  When the explicit
Codex orchestration feature flag is enabled, the same timer wake executes one
synthetic GPT-OSS/Codex control-plane step instead.  This module never runs both
paths in one wake and does not create another daemon or timer.
"""
from __future__ import annotations

import argparse
import os
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

    src = str(_release_root() / "src")
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src + (os.pathsep + existing if existing else "")
    return env


def _exec_one(config: str, worker_version="v1") -> None:
    flag = os.environ.get("QUANT_CODEX_ORCHESTRATION_ENABLED", "0").strip()
    if flag not in ("", "0", "1"):
        raise SystemExit("INVALID_QUANT_CODEX_ORCHESTRATION_ENABLED")

    if flag == "1":
        env = _codex_environment(worker_version)
        script = _release_root() / "scripts" / "gpt_oss_orchestrator.py"
        argv = [sys.executable, str(script)]
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
