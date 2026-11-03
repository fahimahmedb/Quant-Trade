"""End-to-end demonstration of Quant System V1.

Runs the real system over the committed, fingerprinted dataset in an isolated
directory, stops it mid-campaign, restarts it as a new process object, and
checks that the same system resumed rather than a new one starting.

Every line it prints is read back out of persistent state. The checks are
assertions, so this script fails loudly if an invariant breaks.

    python3 scripts/demo_quant_system.py
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.clock import QuantSystem  # noqa: E402
from quant.desk.journal import DeskJournal  # noqa: E402
from quant.dataplane.ingest import register_committed_snapshots  # noqa: E402
from quant.dataplane.registry import DatasetRegistry  # noqa: E402
from quant.events import EventLog  # noqa: E402
from quant.paths import QuantPaths  # noqa: E402
from quant.status.brief import write_chief_brief  # noqa: E402
from quant.status.render import render_status  # noqa: E402

CHECKS: list[tuple[str, bool]] = []


class DemoTimer:
    """Records waits instead of performing them, so the demo stays fast."""

    def __init__(self):
        self.slept: list[float] = []
        self._now = datetime.now(timezone.utc)

    def now(self):
        return self._now

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self._now += timedelta(seconds=seconds)


def read_recent_tickets(root: Path, limit: int = 20) -> list[dict]:
    path = root / "var" / "opportunities.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines()[-limit:] if line.strip()]


def check(description: str, condition: bool) -> None:
    CHECKS.append((description, bool(condition)))
    print(f"   [{'PASS' if condition else 'FAIL'}] {description}")


def replay_proven(pending: dict, tickets: list[dict]) -> bool:
    """Require an actual, non-empty journal replay, never a vacuous all()."""
    if len(pending) != 1:
        return False
    opportunity_id, plan = next(iter(pending.items()))
    fills = plan.get("fills") or []
    if not fills:
        return False
    matching = [ticket for ticket in tickets
                if ticket.get("opportunity_id") == opportunity_id]
    if len(matching) != 1:
        return False
    ticket = matching[0]
    return (ticket.get("strategy_id") == plan.get("strategy_id")
            and ticket.get("ledger") == plan.get("ticket", {}).get("ledger")
            and ticket.get("status") == "BOOKED"
            and bool(ticket.get("stage_trace"))
            and ticket["stage_trace"][-1].get("stage") == "BOOK"
            and ticket.get("book_effect", {}).get("replayed_operations") == len(fills))


def emit(stage: str, system: QuantSystem) -> None:
    state = system.state
    print(json.dumps({
        "stage": stage, "status": state.status, "boots": state.boots, "ticks": state.ticks,
        "research_runs": state.research_runs, "desk_sessions": state.desk_sessions,
        "desk_cursor": state.desk_cursor,
        "capital_nav": round(system.desk.capital.nav, 2),
        "evaluation_nav": round(system.desk.evaluation.nav, 2),
        "queue": system.queue.counts(), "next_action": state.next_action}, sort_keys=True))


def stage(title: str) -> None:
    print(f"\n=== {title} ===")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="quant-system-demo-") as directory:
        demo = Path(directory)
        (demo / "data").mkdir()
        (demo / "research").mkdir()
        shutil.copytree(ROOT / "data" / "datasets", demo / "data" / "datasets")
        shutil.copy2(ROOT / "research" / "opportunity_map.json", demo / "research")

        stage("1. Data Plane: register the committed, fingerprinted snapshot offline")
        paths = QuantPaths(demo).ensure()
        registry = DatasetRegistry(paths.dataset_registry, demo)
        log = EventLog(paths.events)
        registered = register_committed_snapshots(paths, registry, log)
        print(json.dumps({"registered": registered, "health": registry.health()},
                         sort_keys=True))
        record = registry.get("us_sector_etf_daily")
        check("the panel validated and is AVAILABLE", record.availability == "AVAILABLE")
        check("the dataset carries a fingerprint", bool(record.fingerprint))
        check("the dataset carries provenance caveats", bool(record.caveats))

        stage("2. Control Plane: first boot")
        system = QuantSystem(demo)
        boot = system.boot()
        emit("booted", system)
        check("research work was seeded", bool(boot["seeded"]))
        check("blocked lanes are named, not silent",
              any(task.blocked_reason for task in system.queue.tasks.values()))

        stage("3. Research Factory: run the research lanes")
        while True:
            outcome = system.tick()
            if outcome != "RESEARCH":
                break
        emit("research_complete", system)
        check("more than one lane ran", system.state.research_runs >= 2)
        check("a follow-up lane was promoted by evidence",
              any(task.parent for task in system.queue.tasks.values()))
        check("every strategy carries its evidence",
              all(definition.evidence for definition in system.strategies.strategies.values()))

        stage("4. Capital Desk: run part of the shadow window, then stop abruptly")
        for _ in range(40):
            if system.tick() != "SESSION":
                break
        emit("mid_campaign", system)
        cursor = system.state.desk_cursor
        evaluation_nav = system.desk.evaluation.nav
        capital_nav = system.desk.capital.nav
        sessions = system.state.desk_sessions
        fills = system.desk.evaluation.state.fills
        # Leave a task mid-flight so restart recovery has something to repair.
        interrupted = next(iter(system.queue.tasks.values()))
        interrupted.status = "RUNNING"
        system.queue.save()
        del system

        stage("5. Restart: a new process object resumes the same system")
        resumed = QuantSystem(demo)
        recovery = resumed.boot()
        emit("resumed", resumed)
        check("boot count advanced", resumed.state.boots == 2)
        check("the desk cursor resumed exactly", resumed.state.desk_cursor == cursor)
        check("no session was replayed", resumed.state.desk_sessions == sessions)
        check("the shadow bankroll carried forward",
              abs(resumed.desk.evaluation.nav - evaluation_nav) < 1e-6)
        check("the capital bankroll carried forward",
              abs(resumed.desk.capital.nav - capital_nav) < 1e-6)
        check("fills were not lost", resumed.desk.evaluation.state.fills == fills)
        check("interrupted work was requeued", interrupted.task_id in recovery["recovered"])
        runs_before = resumed.state.research_runs
        check("research history was preserved", runs_before >= 2)
        while resumed.tick() == "RESEARCH":
            pass
        check("requeued work on unchanged data was skipped, not repeated",
              resumed.state.research_runs == runs_before)

        stage("6. Crash after durable evaluation fills; replay the original intent")
        original = DeskJournal.commit
        crash: dict = {}

        def interrupt_filled_evaluation(journal, opportunity_id, *args, **kwargs):
            plan = journal.pending_plan(opportunity_id)
            if (plan and plan.get("fills")
                    and plan["ticket"]["ledger"] == "EVALUATION"):
                operations = {f"{opportunity_id}:{fill['symbol']}"
                              for fill in plan["fills"]}
                if operations.issubset(
                        set(resumed.desk.evaluation.state.applied_operations)):
                    crash.update(opportunity_id=opportunity_id,
                                 strategy_id=plan["strategy_id"],
                                 fill_count=len(plan["fills"]),
                                 operations=sorted(operations))
                    raise RuntimeError("killed after durable evaluation fills")
            return original(journal, opportunity_id, *args, **kwargs)

        DeskJournal.commit = interrupt_filled_evaluation
        crashed = False
        try:
            # Stop at the first eligible actual fill, not an arbitrary next tick
            # that may contain only NO_TRADE or no pending journal entry.
            for _ in range(400):
                if resumed.tick() != "SESSION":
                    break
        except RuntimeError as exc:
            if str(exc) != "killed after durable evaluation fills":
                raise
            crashed = True
        finally:
            DeskJournal.commit = original
        check("a non-empty evaluation plan was interrupted after durable fills",
              crashed and bool(crash))
        if not crashed:
            return 1
        sessions_before = resumed.state.desk_sessions
        del resumed

        recovered = QuantSystem(demo)
        recovered.boot()
        pending = dict(recovered.desk.journal.pending)
        plan = pending.get(crash["opportunity_id"])
        check("the original fill-bearing intent survived a cold restart",
              bool(plan) and plan["strategy_id"] == crash["strategy_id"]
              and len(plan["fills"]) == crash["fill_count"])
        book = recovered.desk.evaluation
        state = book.state
        financial_before = (
            state.cash, state.fills, state.fees_paid, state.realized_pnl,
            json.dumps(state.attribution, sort_keys=True))
        operations_before = list(state.applied_operations)
        check("the recorded operations were already in the durable Book",
              set(crash["operations"]).issubset(set(operations_before)))

        result = recovered.tick()
        tickets = read_recent_tickets(demo, limit=10_000)
        check("a real pending ticket was replayed exactly once",
              result == "SESSION" and replay_proven(pending, tickets))
        check("replay preserved Book cash, fills, costs, attribution and operation ids",
              financial_before == (
                  state.cash, state.fills, state.fees_paid, state.realized_pnl,
                  json.dumps(state.attribution, sort_keys=True))
              and list(state.applied_operations) == operations_before)
        check("the crashed session was counted exactly once",
              recovered.state.desk_sessions == sessions_before + 1)
        check("the journal committed the original opportunity and cleared the intent",
              recovered.desk.journal.is_processed(crash["opportunity_id"])
              and recovered.desk.journal.pending_plan(crash["opportunity_id"]) is None)
        emit("recovered_from_crash", recovered)

        stage("7. Continue to completion")
        recovered.run()
        emit("idle", recovered)
        resumed = recovered
        check("the system is IDLE, not stopped", resumed.state.status == "IDLE")
        check("IDLE still names the next action", bool(resumed.state.next_action))
        check("the book marked every executable session once",
              resumed.desk.capital.state.sessions == len(
                  {point["date"] for point in resumed.desk.capital.state.nav_history}))
        check("marks never ran backward",
              [point["date"] for point in resumed.desk.capital.state.nav_history]
              == sorted(point["date"] for point in resumed.desk.capital.state.nav_history))
        check("rejections were scored against their counterfactual",
              resumed.learning.decision_quality.get("strategies_evaluated", 0) > 0)
        check("replayed strategy identity reached persistent Learning",
              crash["strategy_id"] in resumed.desk.evaluation.state.attribution
              and any(item["strategy_id"] == crash["strategy_id"]
                      for item in resumed.learning.decision_quality.get(
                          "assessments", [])))

        stage("8. IDLE stays alive and wakes on due work")
        timer = DemoTimer()
        alive = QuantSystem(demo, timer=timer)
        alive.boot()
        entry = alive.serve(poll_seconds=15.0, max_cycles=3)
        check("the clock waited instead of exiting", timer.slept == [15.0, 15.0, 15.0])
        check("waiting is recorded as liveness, not completion",
              entry["waits"] == 3 and alive.state.status == "IDLE")
        check("a waiting clock still names its next action", bool(alive.state.next_action))

        stage("9. A second restart changes nothing")
        final_nav = resumed.desk.evaluation.nav
        final_sessions = resumed.state.desk_sessions
        del resumed
        again = QuantSystem(demo)
        again.boot()
        check("still IDLE after restart", again.tick() == "IDLE")
        check("no duplicate sessions", again.state.desk_sessions == final_sessions)
        check("bankroll unchanged", abs(again.desk.evaluation.nav - final_nav) < 1e-6)

        stage("10. Status surface and Chief Brief, rendered from the recovered state")
        snapshot = again.snapshot()
        surface = render_status(snapshot)
        (demo / "status.txt").write_text(surface, encoding="utf-8")
        write_chief_brief(snapshot, demo / "CHIEF_BRIEF.md")
        print(surface)
        check("the surface reports the recovered NAV",
              f"{snapshot['book']['nav']:,.2f}" in surface)
        check("the brief was generated from the same state",
              (demo / "CHIEF_BRIEF.md").read_text().count(
                  snapshot["data"]["datasets"]["us_sector_etf_daily"]["fingerprint"]) > 0)
        check("no unresolved faults", not snapshot["health"])

    failed = [description for description, ok in CHECKS if not ok]
    print(f"\n{'=' * 78}\n{len(CHECKS) - len(failed)}/{len(CHECKS)} checks passed")
    if failed:
        print("FAILED:\n" + "\n".join(f"  - {item}" for item in failed))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
