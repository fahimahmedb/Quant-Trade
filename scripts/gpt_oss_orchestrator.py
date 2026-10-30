#!/usr/bin/env python3
"""Feature-flagged one-shot entry point for the existing ResearchCampaign scheduler."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

from autonomous_research.codex_adapter import (
    CodexOrchestrationWorker,
    GitHubIssueClient,
    OrchestrationConfig,
)
from autonomous_research.orchestrator import ResearchCampaign


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

    root = Path(os.environ.get("QUANT_RESEARCH_ROOT", ".")).resolve()
    repository = _required("QUANT_REPOSITORY")
    issue_number = int(_required("QUANT_CODEX_ISSUE_NUMBER"))
    target_branch = _required("QUANT_CODEX_TARGET_BRANCH")
    token = _required("QUANT_GITHUB_TOKEN")
    gpt_oss_command = _required("QUANT_GPT_OSS_COMMAND")

    config = OrchestrationConfig(
        root=root,
        repository=repository,
        issue_number=issue_number,
        target_branch=target_branch,
        poll_seconds=float(os.environ.get("QUANT_CODEX_POLL_SECONDS", "15")),
        max_poll_seconds=float(os.environ.get("QUANT_CODEX_MAX_POLL_SECONDS", "120")),
        max_no_delta_cycles=int(os.environ.get("QUANT_CODEX_MAX_NO_DELTA_CYCLES", "240")),
    )
    client = GitHubIssueClient(repository, issue_number, token)
    worker = CodexOrchestrationWorker(config, client, subprocess_json_decider(gpt_oss_command))
    campaign = ResearchCampaign(root, workers={"codex_orchestrator": worker})
    status = campaign.run_once()
    print(json.dumps({"campaign_status": status, "inspection": campaign.inspect()},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
