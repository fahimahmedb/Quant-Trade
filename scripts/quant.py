"""Operator CLI for the whole Quant system.

    python3 scripts/quant.py boot      resume persistent state and seed due work
    python3 scripts/quant.py tick      advance exactly one unit of due work
    python3 scripts/quant.py run       run until the system is IDLE (bounded batch)
    python3 scripts/quant.py serve     stay alive: work when due, wait when not
    python3 scripts/quant.py status    render the status surface from real state
    python3 scripts/quant.py brief     regenerate CHIEF_BRIEF.md from real state
    python3 scripts/quant.py health    watchdog report
    python3 scripts/quant.py snapshot  the full persistent state as JSON
    python3 scripts/quant.py pause | resume
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.clock import QuantSystem  # noqa: E402
from quant.status.brief import write_chief_brief  # noqa: E402
from quant.status.render import render_status  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("boot", "tick", "run", "serve", "status",
                                            "brief", "health", "snapshot", "pause", "resume"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--max-ticks", type=int, default=10_000)
    parser.add_argument("--reason", default="operator-requested pause")
    parser.add_argument("--capital", type=float, default=1_000_000.0)
    parser.add_argument("--poll-seconds", type=float, default=60.0,
                        help="how long serve waits between wake-ups while IDLE")
    parser.add_argument("--max-waits", type=int,
                        help="stop serve after this many idle waits (default: never)")
    args = parser.parse_args()

    system = QuantSystem(args.root, initial_capital=args.capital)

    if args.command == "boot":
        print(json.dumps(system.boot(), indent=2, sort_keys=True))
        return
    if args.command == "tick":
        system.boot()
        print(json.dumps({"outcome": system.tick(),
                          "next_action": system.state.next_action}, indent=2))
        return
    if args.command == "run":
        system.boot()
        print(json.dumps(system.run(max_ticks=args.max_ticks), indent=2, sort_keys=True))
        return
    if args.command == "serve":
        system.boot()
        print(json.dumps(system.serve(poll_seconds=args.poll_seconds,
                                      max_cycles=args.max_waits), indent=2, sort_keys=True))
        return
    if args.command == "pause":
        system.pause(args.reason)
        print(json.dumps({"status": system.state.status,
                          "pause_reason": system.state.pause_reason}, indent=2))
        return
    if args.command == "resume":
        system.resume()
        print(json.dumps({"status": system.state.status}, indent=2))
        return

    snapshot = system.snapshot()
    if args.command == "status":
        surface = render_status(snapshot)
        system.paths.status_surface.write_text(surface + "\n", encoding="utf-8")
        print(surface)
    elif args.command == "brief":
        path = write_chief_brief(snapshot, args.root / "CHIEF_BRIEF.md")
        print(f"wrote {path}")
    elif args.command == "health":
        print(json.dumps({"alerts": snapshot["health"],
                          "components": snapshot["components"]}, indent=2, sort_keys=True))
    else:
        print(json.dumps(snapshot, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
