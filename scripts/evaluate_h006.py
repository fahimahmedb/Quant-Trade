"""H-006 (Hyperliquid new-listing fade): run the declared lane, then the event view.

    PYTHONPATH=src python3 scripts/evaluate_h006.py [--state var/h006_research]

The lane goes through the ordinary Research Factory worker (``run_lane``):
discovery ranks the six pre-registered expressions, only the best is run on
the validation window, ``falsify`` decides. Every run records its trials in
the state's strategy registry; a rerun on the same frozen cohort is idempotent
there, but it is still a look and must be reported as one.

The event view (listings per window, mean net per event, top-10% share of
gains, capacity at 1% ADV) is computed on the selected expression's own rows
and prices; it is descriptive and never feeds back into selection.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.dataplane.ingest import register_committed_snapshots  # noqa: E402
from quant.dataplane.panel import PricePanel, Window  # noqa: E402
from quant.dataplane.registry import DatasetRegistry  # noqa: E402
from quant.events import EventLog  # noqa: E402
from quant.factory.evaluate import walk_forward  # noqa: E402
from quant.factory.lanes import (HL_LISTINGS_COST_BPS, HL_LISTINGS_DATASET,  # noqa: E402
                                 lane_definitions)
from quant.factory.signals import StrategySpec  # noqa: E402
from quant.factory.strategies import StrategyRegistry  # noqa: E402
from quant.factory.workers import ResearchContext, run_lane  # noqa: E402
from quant.paths import QuantPaths  # noqa: E402

LANE = "hl_listing_fade"
MIN_CAPACITY_USD = 10_000.0
ADV_SHARE = 0.01


def events(panel: PricePanel, spec: StrategySpec, window: Window, rows: list[dict],
           cost_bps: float) -> dict:
    """One event per eligible listing whose first decision date lies in ``window``."""
    calendar = [day for day in panel.dates_for(spec.calendar_symbol) if day <= window.end]
    held = {}
    for row in rows:
        for symbol, weight in row["weights"].items():
            if weight < 0:
                held.setdefault(symbol, []).append((row, weight))
    out = []
    for symbol in spec.universe:
        if symbol == spec.calendar_symbol:
            continue
        days = [day for day in panel.dates_for(symbol)
                if panel.feature(day, symbol, "listing_eligible") == 1.0
                and 1 <= (panel.feature(day, symbol, "listing_age_days") or 0) <= spec.lookback_days]
        if not days or not window.contains(days[0]):
            continue
        # Unit short (plus unit long hedge) over the same executable intervals
        # the walk-forward uses: signal d, entry open(d+1), exit open(d+2).
        value, intervals, volumes = 1.0, 0, []
        for day in days:
            if day not in calendar:
                continue
            position = calendar.index(day)
            if position + 2 >= len(calendar):
                continue
            entry, exit_ = calendar[position + 1], calendar[position + 2]
            if not (panel.has(entry, symbol) and panel.has(exit_, symbol)):
                continue
            r = -(panel.price(exit_, symbol) / panel.price(entry, symbol) - 1.0) \
                + (panel.feature(exit_, symbol, "carry_rate") or 0.0)
            if spec.hedge_symbol:
                h = spec.hedge_symbol
                r += (panel.price(exit_, h) / panel.price(entry, h) - 1.0) \
                    - (panel.feature(exit_, h, "carry_rate") or 0.0)
            value *= 1.0 + r
            intervals += 1
            volumes.append(panel.price(day, symbol, "volume"))
        if not intervals:
            continue
        legs = 2 if spec.hedge_symbol else 1
        net = value - 1.0 - 2 * legs * cost_bps / 10_000.0
        weights = [abs(weight) for _, weight in held.get(symbol, [])]
        adv = statistics.fmean(volumes)
        weight = max(weights) if weights else spec.max_weight
        out.append({"symbol": symbol, "first_decision": days[0], "intervals": intervals,
                    "net_unit": net, "adv_usd": adv,
                    "capacity_usd": ADV_SHARE * adv / weight if weight else None})
    gains = sorted((item["net_unit"] for item in out if item["net_unit"] > 0), reverse=True)
    top = max(1, math.ceil(0.1 * len(out))) if out else 0
    capacities = sorted(item["capacity_usd"] for item in out if item["capacity_usd"])
    return {
        "events": len(out),
        "mean_net_per_event": statistics.fmean(i["net_unit"] for i in out) if out else None,
        "median_net_per_event": statistics.median(i["net_unit"] for i in out) if out else None,
        "hit_rate": sum(1 for i in out if i["net_unit"] > 0) / len(out) if out else None,
        "top_10pct_share_of_gains": sum(gains[:top]) / sum(gains) if gains else None,
        "capacity_usd_at_1pct_adv": {
            "median": statistics.median(capacities) if capacities else None,
            "p10": capacities[len(capacities) // 10] if capacities else None,
            "min": capacities[0] if capacities else None},
        "capacity_test_passed": bool(capacities) and statistics.median(capacities) >= MIN_CAPACITY_USD,
        "items": sorted(out, key=lambda item: item["first_decision"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="var/h006_research")
    parser.add_argument("--out", type=Path, default=ROOT / "research/fast_rail/h006_result.json")
    args = parser.parse_args()
    paths = QuantPaths(ROOT, state=args.state).ensure()
    registry = DatasetRegistry(paths.dataset_registry, paths.root)
    log = EventLog(paths.events)
    register_committed_snapshots(paths, registry, log)
    record = registry.get(HL_LISTINGS_DATASET)
    meta = json.loads((ROOT / "data/datasets" / f"{HL_LISTINGS_DATASET}.csv.meta.json").read_text())
    universe = meta["expected_symbols"]
    strategies = StrategyRegistry(paths.strategies)
    context = ResearchContext(paths, registry, strategies, log)
    outcome = run_lane(context, LANE, universe, HL_LISTINGS_DATASET)
    ticket = json.loads((paths.research_tickets / f"{outcome['ticket_id']}.json").read_text())
    windows = {name: Window(**value) for name, value in
               ticket["candidate_data"]["windows"].items()}
    panel = PricePanel.load(ROOT / record.path)
    visible = panel.restrict(end=windows["VALIDATION"].end)
    grid = lane_definitions(universe, HL_LISTINGS_DATASET)[LANE]["grid"]
    best = StrategySpec(**ticket["candidate_data"]["ranked_expressions"][0]["spec"])
    view = {}
    for name in ("DISCOVERY", "VALIDATION"):
        rows = walk_forward(visible, best, windows[name], HL_LISTINGS_COST_BPS)
        view[name] = events(visible, best, windows[name], rows, HL_LISTINGS_COST_BPS)
    listings_per_window = {}
    for name, window in windows.items():
        listings_per_window[name] = sum(
            1 for symbol in universe if symbol != "HL.BTC" and any(
                window.contains(day) and panel.feature(day, symbol, "listing_eligible") == 1.0
                and panel.feature(day, symbol, "listing_age_days") == 1.0
                for day in panel.dates_for(symbol)[:3]))
    result = {"hypothesis": "H-006", "lane": LANE, "dataset": HL_LISTINGS_DATASET,
              "dataset_fingerprint": record.fingerprint, "outcome": outcome,
              "windows": {k: v.to_dict() for k, v in windows.items()},
              "expressions_declared": len(grid),
              "cumulative_trials": ticket["candidate_data"]["cumulative_expressions_tested_on_dataset"],
              "ranked_discovery": ticket["candidate_data"]["ranked_expressions"],
              "selected": best.label,
              "validation_summary": ticket.get("test_result"),
              "falsification": ticket.get("validation_result"),
              "listings_per_window_age1_row": listings_per_window,
              "event_view": {name: {k: v for k, v in item.items() if k != "items"}
                             for name, item in view.items()},
              "validation_events": view["VALIDATION"]["items"]}
    for item in result["ranked_discovery"]:
        item.pop("spec", None)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: result[k] for k in ("selected", "cumulative_trials", "event_view",
                                             "listings_per_window_age1_row")},
                     indent=1, default=str))
    print(json.dumps({"falsification": result["falsification"],
                      "summary": result["validation_summary"]}, indent=1, default=str)[:4000])


if __name__ == "__main__":
    main()
