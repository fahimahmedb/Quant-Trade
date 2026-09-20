"""Manual Forward Data capture runner.

This is intentionally a thin caller of the exact Control-Plane seam:
``due(...)`` decides whether work is eligible and
``execute_forward_capture(...)`` performs exactly one attempt.

It creates no scheduler, loop, background thread or retry layer.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.dataplane.forward_capture import (  # noqa: E402
    ATTEMPT_SUCCEEDED,
    VALIDATION_OK,
    AdapterCallable,
    AttemptJournal,
    ForwardCaptureRequest,
    ForwardCaptureTaskStore,
    ForwardTimebase,
    due,
    execute_forward_capture,
    yahoo_forward_adapter,
)
from quant.dataplane.forward_recorder import ForwardRecorder  # noqa: E402


def state_paths(root: Path) -> dict[str, Path]:
    directory = Path(root) / "var" / "forward_capture"
    return {
        "directory": directory,
        "observations": directory / "observations.jsonl",
        "attempts": directory / "attempts.jsonl",
        "tasks": directory / "tasks.json",
    }


def run_capture(
    root: Path,
    symbols: Sequence[str],
    *,
    source_id: str = "yahoo_daily_chart",
    market_session: str = "REGULAR",
    min_interval_seconds: int = 3600,
    lookback_range: str = "5d",
    adapter: AdapterCallable | None = None,
    timebase: ForwardTimebase | None = None,
    attempt_id: str | None = None,
) -> dict[str, Any]:
    """Run at most one due capture through the production Forward seam."""
    paths = state_paths(Path(root))
    paths["directory"].mkdir(parents=True, exist_ok=True)

    request = ForwardCaptureRequest(
        source_id=source_id,
        symbols=tuple(symbols),
        market_session=market_session,
        min_interval_seconds=min_interval_seconds,
        lookback_range=lookback_range,
    )
    recorder = ForwardRecorder(paths["observations"])
    journal = AttemptJournal(paths["attempts"])
    task_store = ForwardCaptureTaskStore(paths["tasks"])
    clock = timebase or ForwardTimebase()
    task = task_store.get(source_id)

    if not due(task, request, clock.now()):
        return {
            "state": "NOT_DUE",
            "source_id": source_id,
            "symbols": list(symbols),
            "last_attempt_at": task.last_attempt_at,
            "minimum_interval_seconds": min_interval_seconds,
            "attempts_journaled": len(journal.all()),
            "ledger_fingerprint": recorder.ledger_fingerprint(),
        }

    result = execute_forward_capture(
        request,
        recorder,
        journal,
        task_store,
        adapter or yahoo_forward_adapter(range_=lookback_range),
        clock,
        attempt_id=attempt_id,
    )
    attempt = result.attempt
    return {
        "state": "ATTEMPTED",
        "source_id": source_id,
        "symbols": list(symbols),
        "attempt_id": attempt.attempt_id,
        "attempt_outcome": attempt.outcome,
        "failure_state": attempt.failure_state,
        "validation_state": attempt.validation_state,
        "fetch_started_at": attempt.fetch_started_at,
        "fetch_completed_at": attempt.fetch_completed_at,
        "payload_hash": attempt.payload_hash,
        "sessions_observed": list(attempt.sessions_observed),
        "symbols_observed": list(attempt.symbols_observed),
        "accepted_count": result.accepted_count,
        "attempts_journaled": len(journal.all()),
        "ledger_fingerprint": recorder.ledger_fingerprint(),
    }


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description="Run one due Forward Data capture attempt")
    command.add_argument("--root", type=Path, default=ROOT)
    command.add_argument("--symbols", nargs="+", required=True)
    command.add_argument("--source-id", default="yahoo_daily_chart")
    command.add_argument("--market-session", default="REGULAR")
    command.add_argument("--min-interval-seconds", type=int, default=3600)
    command.add_argument("--lookback-range", default="5d")
    command.add_argument("--attempt-id")
    command.add_argument("--json-output", type=Path)
    return command


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    summary = run_capture(
        args.root,
        args.symbols,
        source_id=args.source_id,
        market_session=args.market_session,
        min_interval_seconds=args.min_interval_seconds,
        lookback_range=args.lookback_range,
        attempt_id=args.attempt_id,
    )
    rendered = json.dumps(summary, indent=2, sort_keys=True)
    print(rendered)

    if args.json_output is not None:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(rendered + "\n", encoding="utf-8")

    if summary["state"] == "NOT_DUE":
        return 0
    return 0 if (
        summary.get("attempt_outcome") == ATTEMPT_SUCCEEDED
        and summary.get("validation_state") == VALIDATION_OK
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
