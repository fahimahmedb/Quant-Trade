#!/usr/bin/env python3
"""Feature-flagged one-step hook for the existing VM scheduler/GPT-OSS runtime.

This executable deliberately does not open or execute the scientific ResearchCampaign
queue. The existing VM scheduler is the wake source; this script advances exactly
one synthetic engineering-orchestration state-machine step per invocation.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

from autonomous_research.codex_adapter import OrchestrationConfig
from autonomous_research.codex_policy import (
    FencedGitHubIssueClient,
    PolicyFencedCodexOrchestrationWorker,
)
from autonomous_research.runtime import ResearchTask


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"missing required environment variable: {name}")
    return value


def subprocess_json_decider(command: str):
    argv = shlex.split(command)
    if not argv:
        raise SystemExit("QUANT_GPT_OSS_COMMAND is empty")

    def decide(context):
        completed = subprocess.run(
            argv,
            input=json.dumps(context, sort_keys=True),
            text=True,
            capture_output=True,
            timeout=int(os.environ.get("QUANT_GPT_OSS_TIMEOUT_SECONDS", "180")),
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"GPT-OSS decision command failed ({completed.returncode}): "
                f"{completed.stderr[-1000:]}")
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("GPT-OSS decision command did not return one JSON object") from exc
        if not isinstance(payload, dict):
            raise RuntimeError("GPT-OSS decision output must be a JSON object")
        return payload

    return decide


def main() -> int:
    if os.environ.get("QUANT_CODEX_ORCHESTRATION_ENABLED") != "1":
        print("codex orchestration feature flag disabled")
        return 0

    project_root = Path(os.environ.get("QUANT_RESEARCH_ROOT", ".")).resolve()
    # Keep orchestration state physically separate from the validated scientific
    # ResearchCampaign queue/state. The default lives under runtime but never
    # opens project_root/runtime/research_queue.json or campaign_state.json.
    orchestration_root = Path(
        os.environ.get(
            "QUANT_CODEX_ORCHESTRATION_ROOT",
            str(project_root / "runtime" / "codex_control_plane"),
        )
    ).resolve()

    repository = _required("QUANT_REPOSITORY")
    issue_number = int(_required("QUANT_CODEX_ISSUE_NUMBER"))
    target_branch = _required("QUANT_CODEX_TARGET_BRANCH")
    expected_head_sha = _required("QUANT_CODEX_EXPECTED_HEAD_SHA")
    task_id = _required("QUANT_CODEX_TASK_ID")
    initial_prompt = _required("QUANT_CODEX_PROMPT")
    token = _required("QUANT_GITHUB_TOKEN")
    github_actor = _required("QUANT_GITHUB_ACTOR")
    gpt_oss_command = _required("QUANT_GPT_OSS_COMMAND")

    config = OrchestrationConfig(
        root=orchestration_root,
        repository=repository,
        issue_number=issue_number,
        target_branch=target_branch,
        poll_seconds=float(os.environ.get("QUANT_CODEX_POLL_SECONDS", "15")),
        max_poll_seconds=float(os.environ.get("QUANT_CODEX_MAX_POLL_SECONDS", "120")),
        max_no_delta_cycles=int(os.environ.get("QUANT_CODEX_MAX_NO_DELTA_CYCLES", "240")),
        max_dispatch_attempts=int(os.environ.get("QUANT_CODEX_MAX_DISPATCH_ATTEMPTS", "12")),
        max_review_attempts=int(os.environ.get("QUANT_CODEX_MAX_REVIEW_ATTEMPTS", "3")),
    )
    client = FencedGitHubIssueClient(
        repository,
        issue_number,
        token,
        expected_actor=github_actor,
    )
    worker = PolicyFencedCodexOrchestrationWorker(
        config,
        client,
        subprocess_json_decider(gpt_oss_command),
        trusted_orchestrator_actor=github_actor,
    )

    # Synthetic engineering/control task only. No economic/scientific authority is
    # carried into Phase 1 and no scientific queue is opened by this executable.
    task = ResearchTask(
        task_id=task_id,
        lane="engineering_orchestration",
        priority=100.0,
        reason="advance the bounded GPT-OSS/Codex control loop",
        worker="codex_orchestrator",
        metadata={
            "expected_head_sha": expected_head_sha,
            "codex_prompt": initial_prompt,
            "authority": {
                "real_capital_authorized": False,
                "live_trading_authorized": False,
                "scientific_unblinding_authorized": False,
                "frozen_protocol_redefinition_authorized": False,
                "irreversible_external_mutation_authorized": False,
            },
        },
    )

    # Advance one state-machine step. The existing VM scheduler supplies future
    # wakes, which makes this restart-safe and prevents a second daemon/timer.
    outcome = worker.step(task)
    print(json.dumps({
        "task_id": task_id,
        "terminal": outcome["terminal"],
        "result": outcome["result"],
        "orchestration_root": str(orchestration_root),
        "scientific_queue_opened": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
