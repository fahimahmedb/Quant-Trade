"""Manual runner for the forward market-data capture lane (non-P0).

    python3 scripts/forward_capture_runner.py declare-universe
    python3 scripts/forward_capture_runner.py declare-sessions
    python3 scripts/forward_capture_runner.py run-once [--force]
    python3 scripts/forward_capture_runner.py status
    python3 scripts/forward_capture_runner.py coverage

This script calls exactly the same contract a future Control Plane change
would call -- ``forward_capture.due`` and ``forward_capture.
execute_forward_capture`` -- and nothing else. It contains no loop of its own:
running it once performs at most one capture attempt (or none, if the
declared minimum interval has not elapsed and ``--force`` is not given), then
exits. Repeated forward capture today means invoking this script repeatedly
(by hand, or from an operator-managed scheduler such as cron/systemd-timer,
analogous to ``deploy/quant-sec-capture.service`` for the P0 lane) -- it is
deliberately not a second autonomous scheduler.

This is the P0 boundary for this script, restated: it never reads
``src/quant/dataplane/sec/**``, ``var/sec/**`` or any ``handoff/SEC_FORM4_*.json``
artifact, and it never modifies ``src/quant/clock.py`` or ``scripts/quant.py``.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.dataplane.forward_capture import (  # noqa: E402
    AttemptJournal, ForwardCaptureRequest, ForwardCaptureTaskStore, ForwardTimebase,
    due, execute_forward_capture, yahoo_forward_adapter)
from quant.dataplane.forward_coverage import (  # noqa: E402
    ExpectedCalendar, ForwardCoverageLedger, seed_expected_sessions_from_dataset)
from quant.dataplane.forward_recorder import ForwardRecorder  # noqa: E402
from quant.dataplane.ingest import BENCHMARK, CONTEXT, SECTOR_DATASET, SECTOR_UNIVERSE  # noqa: E402
from quant.paths import QuantPaths  # noqa: E402

SOURCE_ID = "yahoo_daily_chart"
FORWARD_UNIVERSE = tuple(SECTOR_UNIVERSE + [BENCHMARK] + CONTEXT)


def _request() -> ForwardCaptureRequest:
    return ForwardCaptureRequest(source_id=SOURCE_ID, symbols=FORWARD_UNIVERSE)


def _print(document: object) -> None:
    print(json.dumps(document, indent=2, sort_keys=True, default=str))


def cmd_declare_universe(paths: QuantPaths, args: argparse.Namespace) -> int:
    calendar = ExpectedCalendar(paths.forward_expected_sessions, paths.forward_expected_universe)
    declaration = calendar.declare_universe(
        FORWARD_UNIVERSE, effective_from=args.effective_from,
        note="the same SECTOR_UNIVERSE + BENCHMARK + CONTEXT already authorized "
             "and used by dataplane.ingest for us_sector_etf_daily")
    _print(declaration.to_dict())
    return 0


def cmd_declare_sessions(paths: QuantPaths, args: argparse.Namespace) -> int:
    dataset_csv = paths.root / "data" / "datasets" / f"{args.from_dataset}.csv"
    if not dataset_csv.exists():
        print(f"BLOCKED_BY: dataset snapshot not found at {dataset_csv}", file=sys.stderr)
        return 1
    calendar = ExpectedCalendar(paths.forward_expected_sessions, paths.forward_expected_universe)
    added = seed_expected_sessions_from_dataset(calendar, dataset_csv)
    _print({"seeded_from": str(dataset_csv), "new_sessions_declared": added,
           "total_expected_sessions": len(calendar.expected_sessions())})
    return 0


def cmd_run_once(paths: QuantPaths, args: argparse.Namespace) -> int:
    recorder = ForwardRecorder(paths.forward_observations)
    journal = AttemptJournal(paths.forward_attempts)
    task_store = ForwardCaptureTaskStore(paths.forward_tasks)
    timebase = ForwardTimebase()
    request = _request()
    task = task_store.get(request.source_id)
    now = timebase.now()

    if not args.force and not due(task, request, now):
        _print({"ran": False, "reason": "not due yet",
               "last_attempt_at": task.last_attempt_at,
               "min_interval_seconds": request.min_interval_seconds,
               "hint": "pass --force to attempt anyway"})
        return 0

    adapter = yahoo_forward_adapter(range_=request.lookback_range)
    result = execute_forward_capture(request, recorder, journal, task_store, adapter, timebase)

    sessions_declared = 0
    if result.attempt.sessions_observed:
        # A session this attempt's payload actually contained is an observed
        # fact, not a forward-looking claim: declaring it here only lets the
        # coverage ledger classify cells that already have evidence,
        # independent of how stale the static dataset snapshot is. It never
        # retroactively changes whether any attempt succeeded or failed.
        calendar = ExpectedCalendar(paths.forward_expected_sessions,
                                    paths.forward_expected_universe)
        sessions_declared = calendar.declare_sessions(
            result.attempt.sessions_observed,
            note=f"observed directly by capture attempt {result.attempt.attempt_id}")

    _print({"ran": True, "new_sessions_declared_from_this_attempt": sessions_declared,
           **result.to_dict()})
    return 0 if result.attempt.outcome == "ATTEMPT_SUCCEEDED" else 2


def cmd_status(paths: QuantPaths, args: argparse.Namespace) -> int:
    recorder = ForwardRecorder(paths.forward_observations)
    task_store = ForwardCaptureTaskStore(paths.forward_tasks)
    _print({"task": task_store.get(SOURCE_ID).to_dict(),
           "ledger_coverage": recorder.coverage(),
           "ledger_fingerprint": recorder.ledger_fingerprint(),
           "earliest_recorded_at": recorder.earliest_recorded_at()})
    return 0


def cmd_coverage(paths: QuantPaths, args: argparse.Namespace) -> int:
    calendar = ExpectedCalendar(paths.forward_expected_sessions, paths.forward_expected_universe)
    recorder = ForwardRecorder(paths.forward_observations)
    journal = AttemptJournal(paths.forward_attempts)
    ledger = ForwardCoverageLedger(calendar, recorder, journal, SOURCE_ID)
    summary = ledger.summary(datetime.now(timezone.utc), session_from=args.since)
    if not args.all_cells:
        summary = {**summary, "cells": f"{len(summary['cells'])} cells omitted; pass --all-cells"}
    _print(summary)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="Quant system root (default: the repository root)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    declare_universe = subparsers.add_parser(
        "declare-universe", help="declare the forward-capture symbol universe")
    declare_universe.add_argument("--effective-from", default=datetime.now(timezone.utc)
                                  .date().isoformat())

    declare_sessions = subparsers.add_parser(
        "declare-sessions",
        help="seed expected sessions from an already-validated committed dataset")
    declare_sessions.add_argument("--from-dataset", default=SECTOR_DATASET)

    run_once = subparsers.add_parser(
        "run-once", help="perform at most one capture attempt, then exit")
    run_once.add_argument("--force", action="store_true",
                          help="attempt even if the minimum interval has not elapsed")

    subparsers.add_parser("status", help="print current task and ledger state")

    coverage = subparsers.add_parser("coverage", help="print the forward coverage ledger summary")
    coverage.add_argument("--all-cells", action="store_true",
                          help="include every individual (session, symbol) cell")
    coverage.add_argument("--since", default=None,
                          help="only report sessions on/after this date (e.g. 2026-09-01); "
                               "narrows the report only, declares nothing")

    arguments = parser.parse_args()
    paths = QuantPaths(arguments.root).ensure_forward()
    handlers = {"declare-universe": cmd_declare_universe, "declare-sessions": cmd_declare_sessions,
               "run-once": cmd_run_once, "status": cmd_status, "coverage": cmd_coverage}
    return handlers[arguments.command](paths, arguments)


if __name__ == "__main__":
    raise SystemExit(main())
