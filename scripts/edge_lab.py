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
    for name in ("init", "status", "next", "render", "queue", "plan", "live", "discovery-queue"):
        sub.add_parser(name)
    discovery_execute = sub.add_parser("discovery-execute", help="Publish one frozen Discovery claim before the explicit economic runner")
    discovery_execute.add_argument("identity")
    discovery_execute.add_argument("--cache-dir", required=True)
    discovery_execute.add_argument("--invocation-id")
    tick = sub.add_parser("tick")
    tick.add_argument("--actor", default="manual")
    tick.add_argument("--offline", action="store_true")
    tick.add_argument("--observations", help="Allowlisted branch-head metadata JSON from connector; no outcomes")
    tick.add_argument("--enabled-confirmed", action="store_true")
    for name in ("pause", "resume"):
        command = sub.add_parser(name)
        command.add_argument("--reason", default="Owner instruction")
    for name in ("evidence", "freeze", "family", "decide", "build-question", "scheduler-disabled", "scheduler-configured", "scheduler-run-observed", "research-option", "reconcile-construction"):
        command = sub.add_parser(name)
        command.add_argument("packet", help="Versioned JSON packet; use primary evidence")
    reserve = sub.add_parser("reserve")
    reserve.add_argument("protocol")
    reserve.add_argument("fingerprint")
    admit = sub.add_parser("admit", help="Evidenced source/software/full-resource admission before a look")
    admit.add_argument("protocol")
    admit.add_argument("packet")
    claim = sub.add_parser("claim-question")
    claim.add_argument("identity")
    claim.add_argument("--actor", required=True)
    agent = sub.add_parser("worker-start", help="Fresh authority + CAS claim; no model/backtest invocation")
    agent.add_argument("--actor", required=True)
    agent.add_argument("--context", choices=("interactive", "scheduled-automation"), default="interactive")
    agent.add_argument("--invocation-id")
    recovery = sub.add_parser("worker-recover", help="Renew an expired reasoning lease on the exact original claim")
    recovery.add_argument("--actor", required=True)
    recovery.add_argument("--context", choices=("interactive", "scheduled-automation"), default="scheduled-automation")
    recovery.add_argument("--invocation-id")
    agent_finish = sub.add_parser("worker-finish", help="Publish an evidence-bound session receipt, no retry")
    agent_finish.add_argument("packet")
    preflight = sub.add_parser("legacy-preflight", help="Read-only exact EURUSD bundle; no capture/launch")
    preflight.add_argument("--claim-id", required=True)
    resources = sub.add_parser("synthetic-resources", help="Fixed full-calendar synthetic EURUSD capacity probe")
    resources.add_argument("--claim-id", required=True)
    reader = sub.add_parser("synthetic-reader", help="Fixed synthetic ZIP duplicate/CRC admission challenge")
    reader.add_argument("--claim-id", required=True)
    for name in ("legacy-plan", "adopt-eurusd"):
        command = sub.add_parser(name, help="Exact immutable legacy binding; never create original ref")
        command.add_argument("packet")
    reconcile = sub.add_parser("reconcile", help="Publish a saved execution receipt without launching/recalculating")
    reconcile.add_argument("protocol")
    reconcile.add_argument("receipt_dir")
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
    elif args.action == "build-question":
        lab.build_question(**strict_json(args.packet))
    elif args.action == "research-option":
        from quant.edge_lab.planning import register
        register(lab, strict_json(args.packet))
    elif args.action == "reconcile-construction":
        from quant.edge_lab.planning import reconcile_software
        reconcile_software(lab, **strict_json(args.packet))
    elif args.action == "plan":
        from quant.edge_lab.planning import project
        print(json.dumps(project(*lab.snapshot()), ensure_ascii=False))
        return
    elif args.action == "live":
        from quant.edge_lab.dashboard import live_state
        print(json.dumps(live_state(*lab.snapshot()), ensure_ascii=False))
        return
    elif args.action == "scheduler-disabled":
        lab.scheduler_disabled(strict_json(args.packet))
    elif args.action == "scheduler-configured":
        lab.scheduler_configured(strict_json(args.packet))
    elif args.action == "scheduler-run-observed":
        lab.scheduler_run_observed(strict_json(args.packet))
    elif args.action == "reserve":
        lab.reserve(args.protocol, args.fingerprint)
    elif args.action == "admit":
        lab.admit(args.protocol, strict_json(args.packet))
    elif args.action == "claim-question":
        print(json.dumps({"claim_id": lab.claim_decision(args.identity, args.actor)}))
    elif args.action == "queue":
        from quant.edge_lab.worker import queue
        print(json.dumps(queue(*lab.snapshot()), ensure_ascii=False))
        return
    elif args.action == "discovery-queue":
        from quant.edge_lab.discovery import load, project
        discovery = load(Path(args.state_dir) / "discovery")
        if discovery is None:
            raise Refused("Discovery state is missing; preserve Validation state")
        print(json.dumps(project(discovery, lab.snapshot()[1]), ensure_ascii=False))
        return
    elif args.action == "discovery-execute":
        from quant.edge_lab.discovery import execute
        from quant.edge_lab.remote import DiscoveryAuthority
        authority = DiscoveryAuthority(ROOT, args.state_dir)
        result = execute(Path(args.state_dir) / "discovery", ROOT, authority, args.identity,
                         args.cache_dir, args.invocation_id)
        print(json.dumps(result, ensure_ascii=False))
        return
    elif args.action in ("worker-start", "worker-recover", "worker-finish"):
        from quant.edge_lab.worker import start, recover, finish
        authority = GitAuthority(ROOT, args.state_dir)
        if args.action == "worker-start":
            result = start(lab, authority, args.actor, args.context, args.invocation_id)
        elif args.action == "worker-recover":
            result = recover(lab, authority, args.actor, args.context, args.invocation_id)
        else:
            result = finish(lab, authority, **strict_json(args.packet))
        print(json.dumps(result, ensure_ascii=False))
        return
    elif args.action == "legacy-preflight":
        from quant.edge_lab.legacy import inspect_eurusd
        print(json.dumps(inspect_eurusd(lab, ROOT, args.claim_id), ensure_ascii=False))
        return
    elif args.action == "execute":
        authority = GitAuthority(ROOT, args.state_dir)
        receipt = lab.execute(args.protocol, ROOT, authority.snapshot, authority.claim)
        print(json.dumps(receipt))
    elif args.action in ("legacy-plan", "adopt-eurusd"):
        from quant.edge_lab.legacy_adapter import plan, adopt
        packet = strict_json(args.packet)
        if args.action == "legacy-plan":
            print(json.dumps(plan(lab, ROOT, packet), ensure_ascii=False))
            return
        adopt(lab, ROOT, packet)
    elif args.action == "reconcile":
        authority = GitAuthority(ROOT, args.state_dir)
        print(json.dumps(lab.reconcile(args.protocol, args.receipt_dir, authority.snapshot, authority.claim)))
    elif args.action == "synthetic-resources":
        from quant.edge_lab.resources import probe_eurusd
        print(json.dumps(probe_eurusd(lab, ROOT, args.claim_id), ensure_ascii=False))
        return
    elif args.action == "synthetic-reader":
        from quant.edge_lab.resources import probe_reader
        print(json.dumps(probe_reader(lab, ROOT, args.claim_id), ensure_ascii=False))
        return
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
