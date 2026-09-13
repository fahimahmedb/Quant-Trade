"""The status surface.

``SYSTEM_ARCHITECTURE.md`` calls this an architectural checksum: every field is
read out of persistent state, and a field that cannot be filled truthfully is
shown as unavailable rather than invented. If a number here looks wrong, the
state is wrong.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..state import parse_ts


WIDTH = 78


def _rule(character: str = "-") -> str:
    return character * WIDTH


def _row(label: str, value: str) -> str:
    return f"{label:<22}{value}"


def _money(value: float) -> str:
    return f"{value:>14,.2f}"


def _duration(since: str | None) -> str:
    if not since:
        return "unavailable"
    delta = datetime.now(timezone.utc) - parse_ts(since)
    seconds = int(delta.total_seconds())
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes = seconds // 60
    return f"{days}d {hours:02d}h {minutes:02d}m"


def render_status(snapshot: dict[str, Any]) -> str:
    control = snapshot["control"]
    book = snapshot["book"]
    evaluation = snapshot["evaluation"]
    components = snapshot["components"]
    data = snapshot["data"]
    research = snapshot["research"]
    learning = snapshot["learning"]
    tickets = snapshot["tickets"]

    lines = [_rule("="),
             f"QUANT SYSTEM V1{'':<8}mode: {control['mode']:<16}"
             f"status: {control['status']}",
             _rule("=")]

    lines += [
        _row("UPTIME", f"{_duration(control['created_at'])}   "
                       f"(boots {control['boots']}, ticks {control['ticks']})"),
        _row("HEARTBEAT", f"{control['last_heartbeat']}"),
        _row("BANK / NAV", f"{_money(book['nav'])} {book['currency']}   "
                           f"({book['authority']} ledger)"),
        _row("P&L", f"{_money(book['nav'] - book['initial_capital'])}   "
                    f"{book['total_return']:+.2%} since "
                    f"{book['inception_date'] or 'inception'}"),
        _row("CASH", _money(book["cash"])),
        _row("REALIZED / FEES", f"{_money(book['realized_pnl'])} / "
                                f"{book['fees_paid']:,.2f}"),
        _row("DRAWDOWN", f"{book['drawdown']:+.2%}"),
        _row("POSITIONS", f"{book['open_positions']} open, gross "
                          f"{book['gross_exposure_ratio']:.2f}x, net "
                          f"{book['net_exposure_ratio']:+.3f}x"),
        _row("SESSIONS BOOKED", f"{book['sessions']} sessions, {book['fills']} fills, "
                                f"last {book['last_session_date'] or 'none'}"),
    ]

    lifecycle = research["lifecycle"]
    active = [name for state in ("SHADOW", "ACTIVE_SHADOW", "DECAYING")
              for name in lifecycle.get(state, [])]
    lines += [
        _row("ACTIVE STRATEGIES", f"{len(active)} tradable"
                                  + (f": {', '.join(active)}" if active else
                                     "  (no strategy holds a tradable lifecycle state)")),
        _row("STRATEGY LIFECYCLE", ", ".join(f"{state} {len(names)}"
                                             for state, names in lifecycle.items()
                                             if names) or "none registered"),
        _row("TICKETS", ", ".join(f"{status} {count}" for status, count
                                  in sorted(tickets["by_status"].items()))
             or "none"),
    ]

    lines += ["", _rule(), "CAPITAL DESK", _rule()]
    for name in ("SCAN", "VET", "SIZE", "RISK", "FILLS", "BOOK"):
        status = components.get(name, {})
        detail = status.get("detail") or ""
        lines.append(f"{name:<9}{status.get('state', 'UNKNOWN'):<10}{detail[:55]}")

    lines += ["", _rule(), "PLANES", _rule()]
    for name in ("CONTROL", "DATA", "RESEARCH", "LEARNING", "BUILD"):
        status = components.get(name, {})
        detail = status.get("detail") or ""
        lines.append(f"{name:<9}{status.get('state', 'UNKNOWN'):<10}{detail[:55]}")

    lines += ["", _rule(), "DATA", _rule()]
    health = data["health"]
    lines.append(_row("HEALTH", f"{'healthy' if health['healthy'] else 'degraded'}   "
                                f"{health['by_availability']}"))
    for dataset_id, record in sorted(data["datasets"].items()):
        lines.append(f"  {dataset_id:<26}{record['availability']:<11}"
                     f"{record['rows']:>7,} rows  {record['first_date']} -> "
                     f"{record['last_date']}")
        lines.append(f"  {'':<26}{(record['fingerprint'] or 'no fingerprint')[:30]}")

    lines += ["", _rule(), "RESEARCH", _rule()]
    lines.append(_row("QUEUE", ", ".join(f"{key} {value}" for key, value
                                         in research["queue"].items() if value)))
    for task in research["tasks"]:
        result = task.get("result") or {}
        tail = result.get("outcome") or task.get("blocked_reason") or ""
        lines.append(f"  {task['task_id'][:40]:<42}{task['status']:<11}{tail[:24]}")
    lines.append(_row("LESSONS", str(learning["lessons"])))
    if learning.get("latest_lesson"):
        lines.append("  latest: " + learning["latest_lesson"][:WIDTH - 12])

    quality = learning["decision_quality"]
    lines += ["", _rule(), "DECISION QUALITY (counterfactual evaluation ledger)", _rule(),
              _row("EVALUATION NAV", f"{_money(evaluation['nav'])}   "
                                     f"{evaluation['total_return']:+.2%}"),
              _row("REJECTIONS SCORED", f"{quality.get('strategies_evaluated', 0)} "
                                        f"(true rejects {quality.get('true_rejects', 0)}, "
                                        f"false rejects {quality.get('false_rejects', 0)}, "
                                        f"undetermined {quality.get('undetermined', 0)})"),
              _row("COUNTERFACTUAL P&L", _money(quality.get("counterfactual_pnl", 0.0)))]

    lines += ["", _rule(), "RECENT DECISIONS", _rule()]
    for ticket in tickets["recent"][:6]:
        lines.append(f"  {ticket['session_date']}  {ticket['status']:<9}"
                     f"{ticket['stage']:<7}{(ticket['reason'] or '')[:40]}")

    alerts = snapshot["health"]
    build = snapshot["build_tasks"]
    lines += ["", _rule(), "SYSTEM", _rule(),
              _row("FAULTS", f"{len(alerts)} open"
                             + (": " + "; ".join(alert["code"] for alert in alerts)
                                if alerts else "")),
              _row("BUILD TASKS", f"{len(build)} open capability gaps"
                                  + (": " + ", ".join(task["capability"][:28]
                                                      for task in build[:2]) if build else "")),
              _row("EVENTS", f"{snapshot['events']['total']} recorded, "
                             f"{snapshot['events']['faults']} faults"),
              _row("NEXT EVENT", (control["next_action"] or "unknown")[:54]),
              _rule("=")]
    return "\n".join(lines)
