"""Fast rail H-002: run the pre-registered lane once through the factory worker.

    PYTHONPATH=src python3 research/fast_rail/run_h002.py

Discovery then validation via ``quant.factory.workers.run_lane`` (the same
protocol the Clock runs), state under ``var/fast_rail_h002``. Adds the
H-002-specific capacity figure (1% of the smaller leg's trailing 30-session
mean daily notional) and writes ``research/fast_rail/h002_result.json``.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from quant.dataplane.ingest import register_committed_snapshots  # noqa: E402
from quant.dataplane.panel import PricePanel, Window  # noqa: E402
from quant.dataplane.registry import DatasetRegistry  # noqa: E402
from quant.events import EventLog  # noqa: E402
from quant.factory.evaluate import walk_forward  # noqa: E402
from quant.factory.lanes import PERP_HL_DYDX_DATASET  # noqa: E402
from quant.factory.signals import StrategySpec  # noqa: E402
from quant.factory.strategies import StrategyRegistry  # noqa: E402
from quant.factory.workers import ResearchContext, run_lane  # noqa: E402
from quant.paths import QuantPaths  # noqa: E402
from quant.state import read_json  # noqa: E402

LANE = "perp_funding_spread_hl_dydx_hold"


def capacity(panel: PricePanel, rows: list[dict], participation: float = 0.01) -> dict:
    per_leg = []
    for row in rows:
        legs = [s for s, w in row["weights"].items() if abs(w) > 1e-12]
        if not legs:
            continue
        adv = []
        for symbol in legs:
            dates = [d for d in panel.dates_for(symbol) if d <= row["signal_date"]][-30:]
            adv.append(statistics.fmean(panel.price(d, symbol, "volume") for d in dates))
        per_leg.append(participation * min(adv))
    if not per_leg:
        return {}
    return {"per_leg_notional_usd_median": statistics.median(per_leg),
            "per_leg_notional_usd_p10": sorted(per_leg)[len(per_leg) // 10],
            "active_days": len(per_leg)}


def main() -> None:
    paths = QuantPaths(ROOT, state="var/fast_rail_h002").ensure()
    datasets = DatasetRegistry(paths.dataset_registry, paths.root)
    log = EventLog(paths.events)
    register_committed_snapshots(paths, datasets, log)
    record = datasets.get(PERP_HL_DYDX_DATASET)
    universe = list(record.symbols)
    context = ResearchContext(paths, datasets, StrategyRegistry(paths.strategies), log)
    outcome = run_lane(context, LANE, universe, PERP_HL_DYDX_DATASET)
    ticket = read_json(paths.research_tickets / f"{outcome['ticket_id']}.json")
    result = {"outcome": outcome, "ticket": ticket}
    validation = ticket.get("test_result") or {}
    if validation:
        spec = StrategySpec(**ticket["candidate_data"]["ranked_expressions"][0]["spec"])
        panel = PricePanel.load(ROOT / record.path)
        windows = ticket["candidate_data"]["windows"]
        visible = panel.restrict(end=windows["VALIDATION"]["end"])
        window = Window(**windows["VALIDATION"])
        rows = walk_forward(visible, spec, window, 6.0)
        result["capacity_1pct_min_leg_adv"] = capacity(visible, rows)
        result["validation_gross_cost_net"] = {
            "gross_sum": sum(r["gross_return"] for r in rows),
            "cost_sum": sum(r["cost"] for r in rows),
            "net_sum": sum(r["net_return"] for r in rows)}
    out = ROOT / "research" / "fast_rail" / "h002_result.json"
    out.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({"outcome": outcome["outcome"], "lesson": outcome["lesson"],
                      "validation": {k: validation.get(k) for k in
                                     ("net_return", "gross_return", "sharpe_zero_rate",
                                      "t_statistic", "market_beta", "active_observations",
                                      "annual_turnover")},
                      "falsification": {k: (ticket.get("validation_result") or {}).get(k)
                                        for k in ("failed_tests", "required_t_statistic",
                                                  "net_return_at_stress_costs",
                                                  "subperiod_returns",
                                                  "expressions_tested_on_dataset")},
                      "capacity": result.get("capacity_1pct_min_leg_adv"),
                      "costs": result.get("validation_gross_cost_net"),
                      "discovery": ticket["candidate_data"].get("ranked_expressions")},
                     indent=1, default=str))


if __name__ == "__main__":
    main()
