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

SEC Form-4 P0 raw capture (requires QUANT_SEC_USER_AGENT, else it fails closed):

    python3 scripts/quant.py sec-status     opaque acquisition telemetry
    python3 scripts/quant.py sec-enable     arm the capture lane
    python3 scripts/quant.py sec-disable    disarm it, keeping all evidence
    python3 scripts/quant.py sec-probe      one discovery poll plus a bounded drain
    python3 scripts/quant.py sec-reconcile  compare a closed day's daily index
    python3 scripts/quant.py sec-verify     re-hash every stored raw object
    python3 scripts/quant.py sec-serve      run the capture service (supervisor entry)
    python3 scripts/quant.py sec-fingerprint  materialize ACQUISITION_CRITICAL_FINGERPRINT
    python3 scripts/quant.py sec-readiness   pre-t0 instrumentation readiness
    python3 scripts/quant.py sec-audit       reconcile scheduler intent against attempts
"""

from __future__ import annotations

import argparse
import json
import sys
import fcntl
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.clock import QuantSystem  # noqa: E402
from quant.status.brief import write_chief_brief  # noqa: E402
from quant.status.render import render_status  # noqa: E402


def sec_command(system: QuantSystem, args: argparse.Namespace) -> int:
    """Operator entry points for the P0 capture lane.

    Everything printed here is opaque acquisition telemetry: the lane can report
    that it is alive, compliant and honest about coverage without publishing any
    interpretable Form-4 content.
    """
    collector = system.sec
    if args.command == "sec-readiness":
        readiness = collector.t0_readiness()
        print(json.dumps(readiness, indent=2, sort_keys=True, default=str))
        # Exit code is the gate signal: 0 only when the pre-t0 instrumentation is
        # actually in place. Blue still decides t0; this only reports whether the
        # preconditions hold.
        return 0 if readiness["instrumentation_ready"] else 1
    if args.command == "sec-audit":
        from datetime import datetime as _datetime
        from quant.dataplane.sec.audit import audit_observation_window
        window_start = (_datetime.fromisoformat(args.window_start)
                        if args.window_start else None)
        report = audit_observation_window(collector, window_start=window_start)
        public = {key: report.get(key) for key in (
            "accountable", "findings", "fingerprint_stable", "coverage_state",
            "p0_continuous_service_state")}
        print(json.dumps(public, indent=2, sort_keys=True, default=str))
        return 0 if report["accountable"] else 1
    if args.command == "sec-status":
        print(json.dumps(collector.telemetry(), indent=2, sort_keys=True, default=str))
        return 0
    if args.command == "sec-verify":
        broken = collector.store.verify_objects()
        print(json.dumps({"integrity_verified": not broken,
                          "address_mismatch_present": bool(broken)},
                         indent=2, sort_keys=True))
        return 1 if broken else 0
    if not collector.configured:
        # Fail closed, loudly, with the remedy named.
        print(json.dumps({"state": "BLOCKED", "reason": collector.policy_error,
                          "remedy": "export QUANT_SEC_USER_AGENT='Name contact@example.com'"},
                         indent=2))
        return 2
    if args.command == "sec-fingerprint":
        payload = collector.materialize_fingerprint()
        # The effective service configuration is part of the manifest, so the
        # fingerprint depends on the environment this ran in. Printed so a
        # hand-run outside the service environment is visibly a different freeze.
        print(json.dumps({"acquisition_critical_fingerprint":
                          payload["acquisition_critical_fingerprint"],
                          "materialized_at_utc": payload["materialized_at_utc"],
                          "git_commit": payload["git_commit"],
                          "manifest_members": sorted(payload["manifest"]),
                          "effective_service_invocation":
                          payload["manifest"]["supervisor"][
                              "effective_service_invocation"]},
                         indent=2, sort_keys=True))
        return 0
    if args.command == "sec-serve":
        effective = collector.lifecycle.get("effective_service_configuration") or {}
        if collector.lifecycle.get("qualifying_service_mode"):
            if (effective.get("poll_seconds") != args.poll_seconds
                    or effective.get("max_waits") != args.max_waits):
                print(json.dumps({"state": "BLOCKED",
                                  "reason": "CLI_RUNTIME_MISMATCH"}))
                return 2
            collector.require_active_materialization()
        # main() acquired the single-writer lock before QuantSystem constructed.
        system.boot()
        if not collector.state.enabled:
            collector.enable()
        entry = system.serve_sec(
            poll_seconds=args.poll_seconds, max_cycles=args.max_waits)
        print(json.dumps({"service_exit": "STOPPED",
                          "mode": entry["mode"]}, sort_keys=True))
        return 0
    if args.command == "sec-enable":
        collector.enable()
    elif args.command == "sec-disable":
        collector.disable(args.reason)
    elif args.command == "sec-probe":
        if not collector.state.enabled:
            collector.enable()
        collector.poll()
        if args.drain:
            collector.drain(max_items=args.drain)
        print(json.dumps({"collector": collector.telemetry()},
                         indent=2, sort_keys=True, default=str))
    elif args.command == "sec-reconcile":
        from datetime import date as _date
        day = (_date.fromisoformat(args.day) if args.day else collector.reconciliation_due())
        if day is None:
            print(json.dumps({"reconciliation": "no closed day is due"}, indent=2))
            return 0
        collector.reconcile(day)
        print(json.dumps({"collector": collector.telemetry()},
                         indent=2, sort_keys=True, default=str))
    state, detail = collector.component_state()
    system.components.set("SEC_CAPTURE", state, detail)
    print(json.dumps({"collector": state, "detail": detail,
                      "coverage_state": collector.state.coverage_state,
                      "liveness": collector.liveness()}, indent=2, sort_keys=True))
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("boot", "tick", "run", "serve", "status",
                                            "brief", "health", "snapshot", "pause", "resume",
                                            "sec-status", "sec-enable", "sec-disable",
                                            "sec-probe", "sec-reconcile", "sec-verify",
                                            "sec-serve", "sec-fingerprint",
                                            "sec-readiness", "sec-audit"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--market", choices=("etf", "futures", "futures-broad", "calendar"),
                        default="etf",
                        help="which market instance to drive; futures keeps its own "
                             "state under var/futures and never touches the ETF Book")
    parser.add_argument("--max-ticks", type=int, default=10_000)
    parser.add_argument("--reason", default="operator-requested pause")
    parser.add_argument("--capital", type=float, default=1_000_000.0)
    parser.add_argument("--poll-seconds", type=float, default=60.0,
                        help="how long serve waits between wake-ups while IDLE")
    parser.add_argument("--max-waits", type=int,
                        help="stop serve after this many idle waits (default: never)")
    parser.add_argument("--drain", type=int, default=1,
                        help="filings a single sec-probe may acquire after discovery")
    parser.add_argument("--day", help="closed day to reconcile, as YYYY-MM-DD")
    parser.add_argument("--window-start",
                        help="Blue-declared t0/window start as timezone-aware ISO-8601")
    args = parser.parse_args()

    # Mutating SEC commands share the service lock and acquire it before
    # QuantSystem constructs the collector. A concurrent operator command
    # therefore cannot load stale state and write it back over the live service.
    mutating_sec = {
        "sec-enable", "sec-disable", "sec-probe", "sec-reconcile",
        "sec-serve", "sec-fingerprint",
    }
    sec_lock_fd: int | None = None
    if args.command in mutating_sec:
        lock_path = args.root / "var" / "sec" / "collector_service.lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        sec_lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(sec_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(sec_lock_fd)
            print(json.dumps({"state": "BLOCKED",
                              "reason": "COLLECTOR_ALREADY_RUNNING"}))
            raise SystemExit(2)

    if args.command.startswith("sec-") and args.market != "etf":
        print(json.dumps({"state": "REFUSED",
                          "reason": "the SEC capture lane belongs to the etf instance"}))
        raise SystemExit(2)
    if args.command.startswith("sec-"):
        try:
            system = QuantSystem(args.root, initial_capital=args.capital)
            raise SystemExit(sec_command(system, args))
        finally:
            if sec_lock_fd is not None:
                os.close(sec_lock_fd)

    if args.market == "futures":
        from quant.dataplane.futures import FUTURES_DATASET, FUTURES_UNIVERSE
        system = QuantSystem(args.root, initial_capital=args.capital,
                             universe=FUTURES_UNIVERSE, dataset_id=FUTURES_DATASET,
                             state_dir="var/futures")
    elif args.market == "calendar":
        system = QuantSystem(args.root, initial_capital=args.capital,
                             universe=["SPY", "TLT", "SPY_ON"],
                             dataset_id="us_calendar_legs_daily", state_dir="var/calendar",
                             calendar=["SPY"])
    elif args.market == "futures-broad":
        from quant.dataplane.futures import FUTURES_BENCHMARK, FUTURES_BROAD_DATASET
        from quant.dataplane.ingest import metadata_path  # noqa: F401  (documented path)
        import json as _json
        meta = _json.loads((args.root / "data" / "datasets"
                            / f"{FUTURES_BROAD_DATASET}.csv.meta.json").read_text())
        system = QuantSystem(args.root, initial_capital=args.capital,
                             universe=meta["expected_symbols"],
                             dataset_id=FUTURES_BROAD_DATASET,
                             state_dir="var/futures_broad", calendar=[FUTURES_BENCHMARK])
    else:
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
        name = {"etf": "CHIEF_BRIEF.md", "futures": "CHIEF_BRIEF_FUTURES.md",
                "calendar": "CHIEF_BRIEF_CALENDAR.md",
                "futures-broad": "CHIEF_BRIEF_FUTURES_BROAD.md"}[args.market]
        path = write_chief_brief(snapshot, args.root / name)
        print(f"wrote {path}")
    elif args.command == "health":
        print(json.dumps({"alerts": snapshot["health"],
                          "components": snapshot["components"]}, indent=2, sort_keys=True))
    else:
        print(json.dumps(snapshot, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
