"""CHIEF_BRIEF.md generation.

``NEXT_BUILD_MISSION.md`` section G: the brief is generated from persistent
state at meaningful milestones. It is written for a reviewer who wants to know
what the system actually did, so every claim in it is traceable to a number in
``var/`` and a fingerprinted dataset.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _percent(value: float) -> str:
    return f"{value:+.2%}"


def build_chief_brief(snapshot: dict[str, Any]) -> str:
    control = snapshot["control"]
    book = snapshot["book"]
    evaluation = snapshot["evaluation"]
    data = snapshot["data"]
    research = snapshot["research"]
    learning = snapshot["learning"]
    tickets = snapshot["tickets"]
    quality = learning["decision_quality"]

    lines = [
        "# Chief Brief",
        "",
        "Generated from persistent system state. Do not edit by hand: "
        "`python3 scripts/quant.py brief` regenerates it.",
        "",
        f"- generated at: {datetime.now(timezone.utc).isoformat()}",
        f"- system: `{control['system_id']}` in `{control['mode']}` mode, "
        f"status `{control['status']}`",
        f"- boots: {control['boots']}, ticks: {control['ticks']}, "
        f"research runs: {control['research_runs']}, "
        f"desk sessions: {control['desk_sessions']}",
        "",
        "## System health",
        "",
    ]
    alerts = snapshot["health"]
    lines.append("No open faults." if not alerts else
                 "Open faults:\n" + "\n".join(f"- `{item['code']}`: {item['detail']}"
                                              for item in alerts))
    lines += ["", "Component state:", ""]
    for name, status in snapshot["components"].items():
        lines.append(f"- `{name}`: **{status['state']}** "
                     f"{('- ' + status['detail']) if status['detail'] else ''}")

    lines += ["", "## Data", "",
              f"Registry health: `{data['health']['by_availability']}`.", ""]
    for dataset_id, record in sorted(data["datasets"].items()):
        lines.append(f"- **{dataset_id}** ({record['availability']}) - "
                     f"{record['rows']:,} rows, {len(record['symbols'])} symbols, "
                     f"{record['first_date']} to {record['last_date']}, "
                     f"`{record['fingerprint']}`")
        lines.append(f"  - source: {record['source']}")
        for caveat in record["caveats"]:
            lines.append(f"  - caveat: {caveat}")

    capture = snapshot.get("sec_capture") or {}
    if capture:
        # Opaque acquisition telemetry only: no filing body, no parsed field, no
        # identifying locator and no filing count reaches this brief.
        storage = capture.get("storage") or {}
        rate = capture.get("rate_limit") or {}
        policy = capture.get("policy") or {}
        lines += ["", "## SEC Form-4 raw capture (P0 acquisition lane)", "",
                  f"- collector `{capture.get('state')}`: {capture.get('detail')}",
                  f"- liveness: **{capture.get('liveness')}**, last attempt "
                  f"{capture.get('last_attempt_at_utc') or 'never'}, last validated "
                  f"discovery {capture.get('last_validated_discovery_at_utc') or 'never'}",
                  f"- coverage: **{capture.get('coverage_state')}** - "
                  f"{capture.get('coverage_detail')}",
                  f"- last result: `{capture.get('last_result_state') or 'none'}`"
                  + (f" (`{capture['last_error_class']}`)"
                     if capture.get("last_error_class") else ""),
                  f"- continuity cursor: `{capture.get('cursor_identity_digest') or 'not established'}`",
                  f"- work in flight: {'yes' if capture.get('work_in_flight') else 'no'}",
                  f"- raw store: {storage.get('raw_bytes', 0):,} bytes, append-only "
                  f"{storage.get('append_only')}, content-addressed "
                  f"{storage.get('content_addressed')}, incomplete evidence present "
                  f"{storage.get('incomplete_present')}",
                  f"- request policy: {policy.get('max_requests_per_second')} req/s cap "
                  f"(SEC documented maximum "
                  f"{policy.get('documented_sec_max_requests_per_second')}), concurrency "
                  f"{policy.get('max_concurrency')}, poll "
                  f"{policy.get('discovery_poll_seconds')}s, backoff "
                  f"{policy.get('backoff_schedule_seconds')}",
                  f"- cooldown: {'active until ' + str(rate.get('cooldown_until_utc')) if rate.get('cooldown_active') else 'none'}"
                  f", requests spent {rate.get('requests_spent', 0)}",
                  f"- states: `{capture.get('capture_state')}` / "
                  f"`{capture.get('visibility_state')}` / "
                  f"`{capture.get('admissibility_state')}`"]
        for source in policy.get("policy_sources") or []:
            lines.append(f"- SEC policy source consulted {source['consulted_at_utc']}: "
                         f"{source['url']} (page revision {source['reviewed_or_updated']})")
        for gap in capture.get("open_gap_intervals") or []:
            span = ", ".join(f"{key} {value}" for key, value in gap.items()
                             if key not in ("gap_id",))
            lines.append(f"- open coverage gap `{gap['gap_id']}`: {span}")

    lines += ["", "## Research", "",
              f"Queue: `{research['queue']}`.", ""]
    for task in research["tasks"]:
        result = task.get("result") or {}
        tail = (result.get("outcome") or task.get("blocked_reason") or "")
        lines.append(f"- `{task['task_id']}` - **{task['status']}** {tail}")
    lines += ["", "Strategy lifecycle: " +
              (", ".join(f"`{state}` {len(names)}" for state, names
                         in research["lifecycle"].items() if names) or "none registered"), ""]
    for strategy_id, definition in sorted(research["strategies"].items()):
        evidence = definition["evidence"].get("validation", {})
        verdict = definition["evidence"].get("falsification", {})
        stats = research.get("desk_stats", {}).get(strategy_id, {})
        lines.append(f"- **{strategy_id}** - lifecycle `{definition['lifecycle']}`"
                     + (", evaluation track" if definition.get("evaluation_track") else "")
                     + (f", {len(definition.get('previous_versions', []))} superseded version(s)"
                        if definition.get("previous_versions") else ""))
        if evidence:
            lines.append(f"  - out of sample: {_percent(evidence.get('net_return', 0.0))} net, "
                         f"beta {evidence.get('market_beta', 0.0):+.3f}, "
                         f"turnover {evidence.get('annual_turnover', 0.0):.0f}x/yr, "
                         f"t={verdict.get('t_statistic', 0.0):.2f} against a required "
                         f"{verdict.get('required_t_statistic', 0.0):.2f}")
        if verdict.get("failed_tests"):
            lines.append(f"  - failed: {', '.join(verdict['failed_tests'])}")
        lines.append(f"  - desk: {stats.get('booked', 0)} rebalances, "
                     f"{stats.get('no_trade', 0)} no-trade, "
                     f"{stats.get('vetoed', 0)} vetoed")

    lines += ["", "## Strongest evidence and rejections", ""]
    if learning.get("latest_lesson"):
        lines.append(f"Latest lesson: {learning['latest_lesson']}")
    lines += ["", f"Lessons recorded: {learning['lessons']}.",
              "", "Lane priorities after learning: " +
              ", ".join(f"`{lane}` {value}" for lane, value
                        in learning["lane_priorities"].items()), ""]

    lines += ["## Capital state", "",
              f"- authoritative ledger `{book['ledger_id']}` ({book['authority']}, "
              f"{book['mode']})",
              f"- NAV {book['nav']:,.2f} {book['currency']} from "
              f"{book['initial_capital']:,.2f} initial "
              f"({_percent(book['total_return'])})",
              f"- cash {book['cash']:,.2f}, realized {book['realized_pnl']:,.2f}, "
              f"fees {book['fees_paid']:,.2f}",
              f"- {book['open_positions']} open positions, gross "
              f"{book['gross_exposure_ratio']:.2f}x, net "
              f"{book['net_exposure_ratio']:+.3f}x",
              f"- {book['sessions']} sessions marked, {book['fills']} fills, "
              f"inception {book['inception_date']}, last {book['last_session_date']}",
              "",
              "## Decision quality", "",
              f"- evaluation ledger NAV {evaluation['nav']:,.2f} "
              f"({_percent(evaluation['total_return'])}) over "
              f"{evaluation['sessions']} sessions and {evaluation['fills']} fills",
              f"- rejections scored: {quality.get('strategies_evaluated', 0)} "
              f"(true rejects {quality.get('true_rejects', 0)}, false rejects "
              f"{quality.get('false_rejects', 0)}, undetermined "
              f"{quality.get('undetermined', 0)})",
              f"- counterfactual P&L of rejected strategies: "
              f"{quality.get('counterfactual_pnl', 0.0):,.2f}",
              f"- desk tickets: {tickets['by_status']}",
              ""]

    build = snapshot["build_tasks"]
    lines += ["## Blockers and capability gaps", ""]
    blocked = [task for task in research["tasks"] if task["status"] == "BLOCKED"]
    if blocked:
        for task in blocked:
            lines.append(f"- `{task['task_id']}` blocked: {task['blocked_reason']}")
    else:
        lines.append("- no blocked research tasks")
    for task in build:
        lines.append(f"- build task `{task['task_id']}`: {task['capability']} "
                     f"(acceptance: {task['acceptance']})")

    lines += ["", "## Next autonomous action", "",
              f"{control['next_action'] or 'unknown'}", ""]
    return "\n".join(lines) + "\n"


def write_chief_brief(snapshot: dict[str, Any], path: Path) -> Path:
    path.write_text(build_chief_brief(snapshot), encoding="utf-8")
    return path
