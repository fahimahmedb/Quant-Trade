#!/usr/bin/env python3
"""B2: read-only re-execution of the recorded sector relative-value lanes (negative replication only).

Pre-registration: research/weather_forward/v4/team/Q21_B2_NEGATIVE_REPLICATION_PREREGISTRATION_2026-10-08.md
(SHA-256 5734f3daca021af27268a0af5cab8c4967ba6ceffdce2c4a5d8d8f27e9bbff58).
This re-runs existing code (walk_forward, summarize, falsify); it is NOT an independent reimplementation and
claims no discovery, validation or tradable strategy. It calls no state-mutating API (no StrategyRegistry,
EventLog, run_lane) and writes exactly one new result file.

Usage: PYTHONPATH=src python3 research/sector_xrev_b2/run_b2.py <result.json>
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import subprocess
import sys
from pathlib import Path

from quant.dataplane.ingest import SECTOR_DATASET, SECTOR_UNIVERSE
from quant.dataplane.panel import PricePanel
from quant.factory.evaluate import falsify, summarize, walk_forward
from quant.factory.lanes import BENCHMARK, COST_BPS, WINDOWS, lane_definitions
from quant.factory.signals import StrategySpec

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/datasets/us_sector_etf_daily.csv"
FINGERPRINT = "sha256:f108a6f41552afdb42100d3188d7194006de1aae6a27bd7722330818e6dcb6d1"
PREREG_SHA256 = "5734f3daca021af27268a0af5cab8c4967ba6ceffdce2c4a5d8d8f27e9bbff58"
UNIVERSE = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
EXPECTED_WINDOWS = {"DISCOVERY": ("2016-09-12", "2022-03-08"),
                    "VALIDATION": ("2022-03-09", "2025-03-11"),
                    "SHADOW": ("2025-03-12", "2026-09-11")}
LAST_RESEARCH_DATE = "2025-03-11"
FIRST_FORBIDDEN_DATE = "2025-03-12"
LANE1, LANE2 = "xs_daily_relative_value", "xs_execution_aware_relative_value"
GRID_SIZES = {LANE1: 24, LANE2: 12}
TRIALS_AFTER_LANE2 = 36

# Recorded figures (STATE.md "Current research evidence") with tolerances equal to the printed precision.
# Declared before any result was read (comment 6057191303).
RECORDED = {
    "lane1_best_discovery_sharpe": (-0.015, 0.0005),
    "lane2_expression": "xs_momentum_l21_z0.5_h5_b0.05",
    "lane2_discovery_sharpe": (0.363, 0.0005),
    "lane2_oos_net_return": (-0.0608, 0.00005),
    "lane2_oos_gross_return": (-0.0137, 0.00005),
    "lane2_total_costs": (0.0490, 0.00005),
    "lane2_annual_turnover": (32.9, 0.05),
    "lane2_market_beta": (-0.062, 0.0005),
    "lane2_t_statistic": (-0.39, 0.005),
    "lane2_required_t": (3.20, 0.005),
    "lane2_benchmark_return": (0.3834, 0.00005),
}
SELF_REL_TOL = 1e-9


class InvalidInput(Exception):
    pass


def file_fingerprint(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def assert_no_shadow(panel: PricePanel) -> None:
    late = [d for d in panel.dates if d >= FIRST_FORBIDDEN_DATE]
    if late:
        raise InvalidInput(f"research view contains {len(late)} date(s) from {FIRST_FORBIDDEN_DATE}: {late[:3]}")


def assert_windows(windows) -> None:
    got = {name: (w.start, w.end) for name, w in windows.items()}
    if got != EXPECTED_WINDOWS:
        raise InvalidInput(f"window bounds {got} differ from pre-registered {EXPECTED_WINDOWS}")


def _scan(visible, grid, discovery):
    scanned = []
    for spec in grid:
        summary = summarize(walk_forward(visible, spec, discovery, COST_BPS), visible, BENCHMARK, COST_BPS)
        scanned.append({"expression": spec.label, "spec": spec.to_dict(),
                        "discovery_sharpe": summary.get("sharpe_zero_rate", 0.0),
                        "discovery_net": summary.get("net_return"), "discovery_gross": summary.get("gross_return")})
    scanned.sort(key=lambda item: item["discovery_sharpe"], reverse=True)
    return scanned


def compute(data_path: Path = DATA, lane_defs=lane_definitions, windows_spec=WINDOWS,
            fingerprint: str = FINGERPRINT) -> dict:
    """Pure computation. Raises InvalidInput on any pre-registered precondition failure."""
    before = file_fingerprint(data_path)
    if before != fingerprint:
        raise InvalidInput(f"dataset fingerprint {before} != {fingerprint}")
    if list(SECTOR_UNIVERSE) != UNIVERSE or SECTOR_DATASET != "us_sector_etf_daily":
        raise InvalidInput("universe or dataset id differs from the pre-registration")
    panel = PricePanel.load(data_path)
    if sorted(panel.symbols) != sorted(UNIVERSE + ["GLD", "SPY", "TLT"]):
        raise InvalidInput(f"symbols {panel.symbols}")
    windows = panel.split(windows_spec, symbols=UNIVERSE)
    assert_windows(windows)
    visible = panel.restrict(end=windows["VALIDATION"].end)
    assert_no_shadow(visible)
    defs = lane_defs(UNIVERSE, SECTOR_DATASET)
    for lane, size in GRID_SIZES.items():
        if len(defs[lane]["grid"]) != size:
            raise InvalidInput(f"{lane} declares {len(defs[lane]['grid'])} expressions, pre-registered {size}")
    discovery, validation = windows["DISCOVERY"], windows["VALIDATION"]

    out = {"lane1": {}, "lane2": {}}
    scan1 = _scan(visible, defs[LANE1]["grid"], discovery)
    out["lane1"] = {"best": scan1[0]["expression"], "best_discovery_sharpe": scan1[0]["discovery_sharpe"],
                    "filtered": scan1[0]["discovery_sharpe"] <= 0,
                    "gross_positive_net_nonpositive": sum(1 for s in scan1 if s["discovery_gross"] > 0 >= s["discovery_net"])}
    if not out["lane1"]["filtered"]:  # recorded history says it was filtered; follow the same code path if not
        spec = StrategySpec(**scan1[0]["spec"])
        rows = walk_forward(visible, spec, validation, COST_BPS)
        summ = summarize(rows, visible, BENCHMARK, COST_BPS)
        out["lane1"]["validation"] = {"summary": summ, "verdict": falsify(rows, summ, visible, BENCHMARK, spec, GRID_SIZES[LANE1])}
    scan2 = _scan(visible, defs[LANE2]["grid"], discovery)
    best2 = scan2[0]
    out["lane2"] = {"best": best2["expression"], "best_discovery_sharpe": best2["discovery_sharpe"]}
    if best2["discovery_sharpe"] > 0:
        spec = StrategySpec(**best2["spec"])
        rows = walk_forward(visible, spec, validation, COST_BPS)
        summ = summarize(rows, visible, BENCHMARK, COST_BPS)
        verdict = falsify(rows, summ, visible, BENCHMARK, spec, TRIALS_AFTER_LANE2)
        out["lane2"].update({"filtered": False, "oos_summary": summ, "oos_verdict": verdict})
    else:
        out["lane2"]["filtered"] = True
    after = file_fingerprint(data_path)
    if after != before:
        raise InvalidInput("dataset changed during the run")
    out["fingerprint_before"], out["fingerprint_after"] = before, after
    out["last_date_read"] = max(visible.dates)
    out["windows"] = {name: list(w) for name, w in EXPECTED_WINDOWS.items()}
    out["family_size"] = "36 EXISTING + 0 DISCOVERY CLAIMS"
    return out


def _close(a, b, tol_abs=0.0, rel=SELF_REL_TOL) -> bool:
    return math.isclose(a, b, rel_tol=rel, abs_tol=max(tol_abs, 1e-12))


def same(a, b) -> bool:
    """Run-to-run equality: discrete exact, floats to relative 1e-9."""
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, float) or isinstance(b, float):
        return isinstance(a, (int, float)) and isinstance(b, (int, float)) and _close(float(a), float(b))
    return a == b


def judge(run1: dict, run2: dict) -> tuple[str, list[str]]:
    problems = []
    if not same(run1, run2):
        problems.append("two executions of the same harness differ beyond 1e-9")
    l1, l2 = run1["lane1"], run1["lane2"]
    centre, tol = RECORDED["lane1_best_discovery_sharpe"]
    if not l1["filtered"]:
        problems.append("lane 1 was not filtered before validation (recorded: filtered)")
    if abs(l1["best_discovery_sharpe"] - centre) > tol:
        problems.append(f"lane 1 best discovery Sharpe {l1['best_discovery_sharpe']:.4f} vs recorded {centre}")
    if l2["best"] != RECORDED["lane2_expression"]:
        problems.append(f"lane 2 selected {l2['best']} vs recorded {RECORDED['lane2_expression']}")
    if l2.get("filtered"):
        problems.append("lane 2 was filtered (recorded: validated out of sample and rejected)")
    else:
        s, v = l2["oos_summary"], l2["oos_verdict"]
        pairs = [("lane2_discovery_sharpe", l2["best_discovery_sharpe"]), ("lane2_oos_net_return", s["net_return"]),
                 ("lane2_oos_gross_return", s["gross_return"]), ("lane2_total_costs", s["total_costs"]),
                 ("lane2_annual_turnover", s["annual_turnover"]), ("lane2_market_beta", s["market_beta"]),
                 ("lane2_t_statistic", s["t_statistic"]), ("lane2_required_t", v["required_t_statistic"]),
                 ("lane2_benchmark_return", s["market_return_same_window"])]
        for key, value in pairs:
            centre, tol = RECORDED[key]
            if abs(value - centre) > tol:
                problems.append(f"{key} {value:.5f} vs recorded {centre} (tol {tol})")
        if v["decision"] != "REJECT_RESEARCH":
            problems.append(f"lane 2 decision {v['decision']} vs recorded REJECT_RESEARCH")
    return ("NEGATIVE_REPLICATION_CONFIRMED" if not problems else "REPLICATION_DIVERGENCE"), problems


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    target = Path(argv[1]).resolve()
    if target.exists():
        print(f"STOP: {target} already exists; B2 is a single execution")
        return 2
    forbidden = [ROOT / "data", ROOT / "var", ROOT / "src"]
    if any(str(target).startswith(str(p) + "/") for p in forbidden):
        print("STOP: the result may not be written under data/, var/ or src/")
        return 2
    command = " ".join(argv)
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    result = {"preregistration_sha256": PREREG_SHA256, "command": command, "git_commit": commit,
              "python": platform.python_version(), "cost_bps": COST_BPS, "benchmark": BENCHMARK,
              "tolerance": {k: v for k, v in RECORDED.items()}, "self_rel_tol": SELF_REL_TOL,
              "limits": ["harness re-executes existing code; not an independent reimplementation",
                         "adj_close is retroactively restated and not strictly point-in-time",
                         "cost envelope does not model short-leg borrow cost; no net figure is realistic",
                         "36 existing expressions; this run adds no discovery claim"]}
    try:
        run1 = compute()
        run2 = compute()
        status, problems = judge(run1, run2)
        result.update({"result": status, "problems": problems, "run": run1})
        rc = 0
    except InvalidInput as exc:
        result.update({"result": "INVALID_INPUT", "problems": [str(exc)]})
        rc = 1
    result.update({"LESSON": "The re-execution establishes whether recorded figures reproduce; it claims no discovery.",
                   "PRIORITY_UPDATE": "abandon or audit the family; do not recycle the validation window",
                   "NEXT_ACTION": "choose a family outside cross-sectional relative value with a clean window, or improve the cost model",
                   "DISCOVERY_CLAIM": False, "VALIDATION_CLAIM": False, "SHADOW_READ": False,
                   "TRADABLE_STRATEGY": False, "REAL_CAPITAL_AUTHORIZED": False, "return_code": rc})
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "x", encoding="utf-8") as handle:  # 'x': never overwrite
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"RESULT: {result['result']}")
    for p in result["problems"]:
        print(f"  - {p}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
