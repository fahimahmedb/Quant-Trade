"""Minimal economic dashboard. Reports what is recorded, and nothing else.

    python3 scripts/economic_dashboard.py --evidence var/evidence.jsonl [--json]

The mission asks for falsification velocity, research cost, killed versus
continued, and expected economic value — with no cosmetics. So every figure here
is derived from a persistent artifact, and anything the artifacts do not contain
is printed as ``UNAVAILABLE`` rather than estimated. A dashboard that fills gaps
with plausible numbers is the most expensive kind of cosmetic.

Expected net economic value in particular is ``UNAVAILABLE`` until a consumable
MEUE evaluation exists: the economic recipe reports RECIPE_PROVISIONAL while any
consumed cost parameter lacks calibration authority, and a provisional threshold
cannot produce an authoritative expected value.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.state import read_jsonl  # noqa: E402

UNAVAILABLE = "UNAVAILABLE"

KILL_DECISIONS = ("KILL", "REJECT_RESEARCH", "RETIRE")
CONTINUE_DECISIONS = ("CONTINUE", "VALIDATED")


def _instant(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def summarise(evidence_path: Path) -> dict[str, Any]:
    accepted: list[dict[str, Any]] = []
    incomplete = 0
    for record in read_jsonl(evidence_path):
        state = record.get("state")
        if state == "EVIDENCE_RECORDED":
            accepted.append(record)
        elif state == "EVIDENCE_CHAIN_INCOMPLETE":
            incomplete += 1

    labels = Counter(str(record.get("label")) for record in accepted)
    decisions = Counter(str(record.get("decision")) for record in accepted)
    killed = sum(count for decision, count in decisions.items()
                 if decision in KILL_DECISIONS)
    continued = sum(count for decision, count in decisions.items()
                    if decision in CONTINUE_DECISIONS)

    instants = sorted(filter(None, (_instant(str(record.get("recorded_at", "")))
                                    for record in accepted)))
    span_days = None
    if len(instants) >= 2:
        span_days = (instants[-1] - instants[0]).total_seconds() / 86_400.0
    velocity = (len(accepted) / span_days if span_days and span_days > 0 else None)

    return {
        "evidence_path": str(evidence_path),
        "records_accepted": len(accepted),
        "records_incomplete": incomplete,
        "labels": dict(sorted(labels.items())),
        "decisions": dict(sorted(decisions.items())),
        "killed": killed,
        "continued": continued,
        "killed_to_continued": (killed / continued) if continued else UNAVAILABLE,
        "observed_span_days": span_days if span_days is not None else UNAVAILABLE,
        "falsification_velocity_decisions_per_day": (
            round(velocity, 4) if velocity is not None else UNAVAILABLE),
        "forward_confirmations": labels.get("FORWARD_CONFIRMATION", 0),
        # Research cost is not recorded by the evidence registry. Estimating it
        # here would invent a number the system does not hold.
        "research_cost_builder_days": UNAVAILABLE,
        "expected_net_economic_value": UNAVAILABLE,
        "expected_net_economic_value_reason": (
            "no consumable MEUE evaluation: the economic recipe stays "
            "RECIPE_PROVISIONAL while any consumed cost parameter lacks calibration "
            "authority"),
        "real_capital_authorized": False,
    }


def render(summary: dict[str, Any]) -> str:
    lines = ["QUANT ECONOMIC DASHBOARD (minimal)", "=" * 42]
    order = ["records_accepted", "records_incomplete", "killed", "continued",
             "killed_to_continued", "forward_confirmations", "observed_span_days",
             "falsification_velocity_decisions_per_day", "research_cost_builder_days",
             "expected_net_economic_value", "real_capital_authorized"]
    width = max(len(key) for key in order)
    for key in order:
        lines.append(f"{key.ljust(width)} : {summary[key]}")
    lines.append("")
    lines.append("labels    : " + (", ".join(f"{key}={value}"
                                             for key, value in summary["labels"].items())
                                   or "none"))
    lines.append("decisions : " + (", ".join(f"{key}={value}"
                                             for key, value in summary["decisions"].items())
                                   or "none"))
    lines.append("")
    lines.append(summary["expected_net_economic_value_reason"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True,
                        help="path to an evidence registry JSONL file")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    arguments = parser.parse_args()
    summary = summarise(arguments.evidence)
    print(json.dumps(summary, indent=2, sort_keys=True) if arguments.json
          else render(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
