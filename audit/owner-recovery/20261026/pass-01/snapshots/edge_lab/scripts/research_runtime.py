"""Operator CLI for the persistent Quant research campaign."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from autonomous_research.orchestrator import ResearchCampaign  # noqa: E402
from autonomous_research.watchdog import inspect_health  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("start", "tick", "inspect", "pause", "resume", "watchdog"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--reason", default="operator-requested pause")
    parser.add_argument("--max-cycles", type=int)
    args = parser.parse_args()
    campaign = ResearchCampaign(args.root, max_cycles=args.max_cycles)
    if args.command == "start":
        campaign.seed_from_opportunity_map()
        while campaign.run_once() == "COMPLETED":
            pass
    elif args.command == "tick":
        campaign.run_once()
    elif args.command == "pause":
        campaign.pause(args.reason)
    elif args.command == "resume":
        campaign.resume()
    output = campaign.inspect()
    if args.command == "watchdog":
        output["watchdog_alerts"] = inspect_health(campaign.state, campaign.queue)
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
