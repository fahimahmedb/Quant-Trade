#!/usr/bin/env python3
"""Bounded entry point; never delegates startup to the historic Quant runtime."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.edge_lab.dashboard import render, server
from quant.edge_lab.engine import Lab, initialize
from quant.edge_lab.remote import GitAuthority
from quant.edge_lab.sources import monitor
from quant.edge_lab.store import Refused, strict_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", default=str(ROOT / "research/edge_lab"))
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("init", "status", "next", "render"):
        sub.add_parser(name)
    tick = sub.add_parser("tick")
    tick.add_argument("--actor", default="manual")
    tick.add_argument("--offline", action="store_true")
    tick.add_argument("--observations", help="Allowlisted branch-head metadata JSON from connector; no outcomes")
    tick.add_argument("--enabled-confirmed", action="store_true")
    for name in ("pause", "resume"):
        command = sub.add_parser(name)
        command.add_argument("--reason", default="Owner instruction")
    for name in ("evidence", "freeze", "family", "decide"):
        command = sub.add_parser(name)
        command.add_argument("packet", help="Versioned JSON packet; use primary evidence")
    reserve = sub.add_parser("reserve")
    reserve.add_argument("protocol")
    reserve.add_argument("fingerprint")
    execute = sub.add_parser("execute")
    execute.add_argument("protocol")
    serve = sub.add_parser("serve")
    serve.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    lab = Lab(args.state_dir)
    if args.action == "init":
        initialize(args.state_dir)
    elif args.action == "tick":
        if args.observations:
            lab.tick(strict_json(args.observations), actor=args.actor, enabled_confirmed=args.enabled_confirmed)
        elif args.offline:
            lab.tick(actor=args.actor, enabled_confirmed=args.enabled_confirmed)
        else:
            monitor(args.state_dir, ROOT, actor=args.actor, enabled_confirmed=args.enabled_confirmed)
    elif args.action in ("pause", "resume"):
        lab.store.pause(args.action == "pause", args.reason)
    elif args.action == "evidence":
        lab.evidence(strict_json(args.packet))
    elif args.action == "freeze":
        lab.freeze(strict_json(args.packet))
    elif args.action == "family":
        lab.family(**strict_json(args.packet))
    elif args.action == "decide":
        lab.decide(**strict_json(args.packet))
    elif args.action == "reserve":
        lab.reserve(args.protocol, args.fingerprint)
    elif args.action == "execute":
        authority = GitAuthority(ROOT, args.state_dir)
        receipt = lab.execute(args.protocol, ROOT, authority.snapshot, authority.claim)
        print(json.dumps(receipt))
    elif args.action == "serve":
        instance = server(args.state_dir, args.port)
        print(f"Local panel: http://127.0.0.1:{instance.server_port}", flush=True)
        try:
            instance.serve_forever()
        except KeyboardInterrupt:
            instance.server_close()
        return
    render(args.state_dir)
    state, control = lab.snapshot()
    if args.action == "next":
        print(json.dumps(lab.next_decision(), ensure_ascii=False))
    else:
        print(json.dumps({"paused": control["paused"], "last_tick": state["scheduler"]["last_tick"],
                          "looks": len(state["looks"]), "trial_charges": state["trial_charges"],
                          "evidence": len(state["evidence"]), "open_decisions": sum(x["status"] == "OPEN" for x in state["decisions"].values()),
                          "real_capital_authorized": False, "live_trading_authorized": False}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (Refused, KeyError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
