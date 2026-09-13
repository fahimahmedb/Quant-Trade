#!/usr/bin/env python3
"""Operate the persistent campaign runtime without live-capital side effects."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from autonomous_research.runtime import CampaignRuntime, ResearchTask, TaskOutcome  # noqa: E402


def unavailable_data_worker(payload: dict) -> TaskOutcome:
    dataset = payload.get("dataset", "required dataset")
    return TaskOutcome(
        "BLOCKED", f"Research lane retained, but {dataset} is not locally available.",
        next_action="Continue other executable scans; revisit when point-in-time data is available.",
        blocked_reason=f"missing dataset: {dataset}",
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("command", choices=("run-once", "run", "inspect", "seed"))
    result.add_argument("--state", type=Path, default=ROOT / "research/campaign_state.json")
    result.add_argument("--queue", type=Path, default=ROOT / "research/campaign_queue.json")
    result.add_argument("--poll-seconds", type=float, default=60.0)
    return result


def main() -> None:
    args = parser().parse_args()
    runtime = CampaignRuntime(args.state, args.queue, {"data_requirement": unavailable_data_worker})
    if args.command == "seed":
        runtime.enqueue(ResearchTask(
            "ETF-PANEL-001", "data_requirement", 100.0,
            {"dataset": "synchronized point-in-time ETF total-return and quote panel"},
        ))
    elif args.command == "run-once":
        runtime.run_once()
    elif args.command == "run":
        runtime.run_forever(args.poll_seconds)
    print(json.dumps(runtime.state, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
