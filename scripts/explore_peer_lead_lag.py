"""Exploratory run of the peer lead-lag family. EXPLORATION evidence only.

    python3 scripts/explore_peer_lead_lag.py [--out handoff/....json]

This is development evidence and is labelled as such everywhere it is written. It
is not confirmation of anything: the dataset already existed when the hypothesis
was written, so the only thing a good number here establishes is that the lane is
worth a forward test.

Three constraints the run respects:

* only the DISCOVERY window is touched. VALIDATION and SHADOW are untouched, so
  they remain usable later;
* the trial budget is charged with every expression in *both* declared lane grids
  plus this one, not just the one that produced the best number;
* the same walk-forward, rebalance rule and turnover cost path as the existing
  family, so the two families are compared on one set of rules.

No economic verdict is produced. The MEUE recipe in ``quant.economics`` is built
for the Form 4 lane; this lane has no consumable economic threshold, and inventing
one to make the result look decided would be worse than reporting the gap.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.dataplane.panel import PricePanel  # noqa: E402
from quant.factory.evaluate import compound, summarize, walk_forward  # noqa: E402
from quant.factory.families import (FAMILY_PEER_LEAD_LAG, declared_trial_count,  # noqa: E402
                                    lead_lag_lane_definition, weights_for_family)
from quant.factory.lanes import BENCHMARK, COST_BPS, WINDOWS, lane_definitions  # noqa: E402
from quant.operations.registry import EvidenceRecord  # noqa: E402
from quant.science.inference import MultiplicityBudget  # noqa: E402
from quant.state import read_json  # noqa: E402

DATASET_ID = "us_sector_etf_daily"
UNIVERSE = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
EVIDENCE_LABEL = "EXPLORATION"


def dataset_record() -> dict[str, Any]:
    registry = read_json(ROOT / "var" / "dataset_registry.json", {"datasets": {}}) or {}
    record = registry.get("datasets", {}).get(DATASET_ID)
    if record is None:
        raise SystemExit(f"{DATASET_ID} is not registered; nothing may be run on it")
    if record.get("availability") != "AVAILABLE":
        raise SystemExit(f"{DATASET_ID} availability is {record.get('availability')}")
    return record


def trial_budget() -> MultiplicityBudget:
    """Every declared expression on this dataset, including the ones that lose."""
    existing = sum(len(entry["grid"])
                   for entry in lane_definitions(UNIVERSE, DATASET_ID).values())
    declared = declared_trial_count(UNIVERSE, DATASET_ID)
    budget = MultiplicityBudget(declared_trials=existing + declared)
    budget.charge(existing, "expressions already declared on this dataset")
    budget.charge(declared, "peer lead-lag grid declared before this run")
    return budget


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=None,
                        help="write the exploration artifact to this path")
    arguments = parser.parse_args()

    record = dataset_record()
    panel = PricePanel.load(ROOT / record["path"])
    windows = panel.split(WINDOWS, UNIVERSE)
    discovery = windows["DISCOVERY"]
    budget = trial_budget()
    threshold = budget.threshold()

    grid = lead_lag_lane_definition(UNIVERSE, DATASET_ID)["peer_lead_lag_diffusion"]["grid"]
    results: list[dict[str, Any]] = []
    for spec in grid:
        # StrategySpec.label is written for the cross-sectional family, so qualify
        # it: a row labelled "xs_..." for a peer-return signal would misdescribe
        # which family produced the number.
        label = f"{spec.family}:{spec.label}"
        rows = walk_forward(panel, spec, discovery, COST_BPS, weights_fn=weights_for_family)
        if not rows:
            results.append({"label": label, "state": "NO_OBSERVATIONS"})
            continue
        summary = summarize(rows, panel.restrict(end=discovery.end), BENCHMARK, COST_BPS)
        results.append({
            "label": label, "state": "RUN",
            "lookback_days": spec.lookback_days, "direction": spec.direction,
            "holding_days": spec.holding_days, "min_abs_score": spec.min_abs_score,
            "observations": summary["observations"],
            "active_observations": summary["active_observations"],
            "gross_return": summary["gross_return"],
            "net_return": summary["net_return"],
            "t_statistic": summary["t_statistic"],
            "market_beta": summary["market_beta"],
            "clears_multiplicity_threshold": summary["t_statistic"] >= threshold,
        })

    ran = [row for row in results if row["state"] == "RUN"]
    best = max(ran, key=lambda row: row["t_statistic"], default=None)
    clearing = [row["label"] for row in ran if row["clears_multiplicity_threshold"]]

    evidence = EvidenceRecord(
        evidence_id="CLAUDE_WAVE1_PEER_LEAD_LAG_EXPLORATION",
        dataset_version=f"{DATASET_ID}@{record['fingerprint']}",
        protocol_hash="declared-grid:" + str(len(grid)),
        code_sha="see FINAL_SHA in handoff/PARALLEL_WAVE1_CLAUDE_2026-09-19.md",
        result_summary=(f"{len(ran)} expressions run on DISCOVERY; "
                        f"{len(clearing)} clear t>={threshold:.3f}"),
        decision="EXPLORATION_RECORDED_NO_PROMOTION",
        label=EVIDENCE_LABEL,
        note="development evidence; VALIDATION and SHADOW windows untouched")

    artifact = {
        "family": FAMILY_PEER_LEAD_LAG,
        "evidence_label": EVIDENCE_LABEL,
        "is_independent_confirmation": False,
        "dataset": {"dataset_id": DATASET_ID, "fingerprint": record["fingerprint"],
                    "first_date": record["first_date"], "last_date": record["last_date"],
                    "source": record["source"], "point_in_time": record["point_in_time"],
                    "caveats": record.get("caveats", [])},
        "window": {"name": "DISCOVERY", **discovery.to_dict()},
        "windows_untouched": ["VALIDATION", "SHADOW"],
        "universe": UNIVERSE,
        "cost_bps_one_way": COST_BPS,
        "multiplicity": budget.to_dict(),
        "required_t_statistic": threshold,
        "expressions": results,
        "expressions_clearing_threshold": clearing,
        "best_by_t_statistic": best,
        "economic_verdict": "UNAVAILABLE",
        "economic_verdict_reason": ("no consumable MEUE exists for this lane; the "
                                    "economic recipe in quant.economics is built for the "
                                    "Form 4 lane"),
        "evidence_record": evidence.to_dict(),
    }

    print(f"family                    : {FAMILY_PEER_LEAD_LAG}")
    print(f"window                    : DISCOVERY {discovery.start} -> {discovery.end}")
    print(f"expressions run           : {len(ran)} of {len(grid)}")
    print(f"trials charged             : {budget.effective_trials}")
    print(f"required |t|              : {threshold:.3f}")
    print(f"clearing the threshold    : {len(clearing)}")
    if best is not None:
        print(f"best by t                 : {best['label']} "
              f"net={best['net_return']:.4f} t={best['t_statistic']:.3f} "
              f"beta={best['market_beta']:.3f}")
    print(f"evidence label            : {EVIDENCE_LABEL} (not confirmation)")
    if arguments.out:
        arguments.out.parent.mkdir(parents=True, exist_ok=True)
        arguments.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n",
                                 encoding="utf-8")
        print(f"artifact                  : {arguments.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
