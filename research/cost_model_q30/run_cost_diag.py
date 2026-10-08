#!/usr/bin/env python3
"""Q30 path 2: cost-robustness DIAGNOSTIC of the already-published B2 and B4 evaluation rows. Read-only, single execution.

Specification : research/weather_forward/v4/team/Q30_PATH2_COST_MODEL_SPECIFICATION_2026-10-08.md
                SHA-256 2d534927a6aa69ec3b7e51f93dc09cd2e2b0b152b75932561b7d959dbfa8bda8
Erratum 1     : research/weather_forward/v4/team/Q30_PATH2_COST_MODEL_ERRATUM_1_2026-10-08.md (Builder proposal)
Descriptive only: it cannot change the B2/B4 rejections, selects nothing, claims no discovery and modifies no desk stage.
Costs: the central scenario IS the desk model (`ExecutionModel`, called, not re-implemented); borrow, financing and the
stress values are LABELLED ASSUMPTIONS (`ASSUMED_NOT_ESTIMATED`), never measurements. A participation above the desk limit is a
capacity REFUSAL (CAPACITY_BREACH), not a silent truncation.

Usage: PYTHONPATH=src python3 -B research/cost_model_q30/run_cost_diag.py <result.json>   (result directory must exist)
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # before any project import

import csv
import hashlib
import importlib.util
import json
import math
import platform
import re
import subprocess
from pathlib import Path

from quant.dataplane.panel import PricePanel, Window
from quant.desk.execution import ExecutionModel
from quant.factory.evaluate import required_t_statistic, walk_forward
from quant.factory.lanes import COST_BPS, lane_definitions
from quant.factory.signals import StrategySpec

ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


B4_PATH = "research/time_series_macro_b4/run_b4.py"
B4_BLOB_SHA256 = "30ede2a379d0f72c2349df37ec96854d8fdd129f523777b3589c8c3631a30706"
b4 = _load("run_b4_frozen", B4_PATH)

DATA = b4.DATA
FINGERPRINT = b4.FINGERPRINT
SPEC_SHA256 = "2d534927a6aa69ec3b7e51f93dc09cd2e2b0b152b75932561b7d959dbfa8bda8"
FIRST_FORBIDDEN_DATE = "2025-03-12"
LAST_RESEARCH_DATE = "2025-03-11"
B2_WINDOW = ("2022-03-09", "2025-03-11")
B2_EXPRESSION = "xs_momentum_l21_z0.5_h5_b0.05"
B2_UNIVERSE = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
B2_PANEL_SYMBOLS = B2_UNIVERSE + ["SPY"]
B2_TRIALS = 36
NAV_GRID = (1_000_000.0, 100_000_000.0, 1_000_000_000.0)
MULTIPLIERS = (0.0, 0.5, 1.0, 2.0, 3.0)
TRADING_DAYS = 252
SELF_REL_TOL = 1e-9
ROBUSTNESS_SHARE = 0.5

# Labelled assumptions. The first three central values ARE the desk's defaults (called through ExecutionModel).
CENTRAL = {"commission_bps": 0.5, "half_spread_bps": 1.0, "impact_bps_at_5pct": 10.0, "borrow_bps_year": 100.0, "financing_bps_year": 0.0}
STRESS = {"commission_bps": 1.0, "half_spread_bps": 5.0, "impact_bps_at_5pct": 25.0, "borrow_bps_year": 300.0, "financing_bps_year": 500.0}
POSTS = ("commission", "spread", "impact", "borrow", "financing")


class InvalidInput(Exception):
    pass


# ------------------------------------------------------------------ input gates
def build_panel(path: Path, symbols) -> tuple[PricePanel, int]:
    """Filter RAW LINES by leading ISO date before any CSV field splitting, then keep only the wanted symbols."""
    kept, skipped = [], 0
    with path.open(encoding="utf-8", newline="") as handle:
        header = handle.readline()
        if not header.startswith("date,"):
            raise InvalidInput("unexpected CSV header")
        kept.append(header)
        for line in handle:
            if not b4.DATE_PREFIX.match(line):
                raise InvalidInput(f"line without a leading ISO date: {line[:30]!r}")
            if line[:10] >= FIRST_FORBIDDEN_DATE:
                skipped += 1
                continue
            kept.append(line)
    wanted = set(symbols)
    return PricePanel([r for r in csv.DictReader(kept) if r["symbol"] in wanted]), skipped


def check_frozen_dependency() -> None:
    digest = hashlib.sha256((ROOT / B4_PATH).read_bytes()).hexdigest()
    if digest != B4_BLOB_SHA256:
        raise InvalidInput(f"the frozen B4 harness changed: {digest}")


# ------------------------------------------------------------------ cost engine
def model_for(params: dict, multiplier: float = 1.0) -> ExecutionModel:
    """The desk model, parameterised. Commission, half spread and impact scale together with the multiplier."""
    return ExecutionModel(commission_bps=params["commission_bps"] * multiplier,
                          half_spread_bps=params["half_spread_bps"] * multiplier,
                          impact_bps_at_full_participation=params["impact_bps_at_5pct"] * multiplier)


def price_rows(rows: list[dict], panel: PricePanel, nav: float, params: dict, multiplier: float = 1.0,
               initial: dict | None = None) -> dict:
    """Per-row, per-instrument cost accounting. `rows` need: signal_date, entry_date, exit_date, weights{sym}, returns{sym}.
    Weight changes are measured against the previous row; `initial` is the position held before the first row (default flat). One absolute weight change feeds ALL posts
    (no second turnover count). Returns series and per-instrument post totals; no compensation between posts."""
    model = model_for(params, multiplier)
    borrow_rate = params["borrow_bps_year"] * multiplier / 10_000.0 / TRADING_DAYS
    financing_rate = params["financing_bps_year"] * multiplier / 10_000.0 / TRADING_DAYS
    previous: dict[str, float] = dict(initial or {})
    out = {"gross": [], "net": [], "posts": {p: [] for p in POSTS}, "by_instrument": {}, "breaches": [], "undetermined": [],
           "turnover": [], "gross_exposure": [], "short_exposure": [], "max_participation": 0.0}
    for row in rows:
        symbols = set(row["weights"]) | set(previous)
        gross = sum(row["weights"].get(s, 0.0) * row["returns"].get(s, 0.0) for s in symbols)
        post = dict.fromkeys(POSTS, 0.0)
        turnover = 0.0
        for symbol in sorted(symbols):
            weight, delta = row["weights"].get(symbol, 0.0), abs(row["weights"].get(symbol, 0.0) - previous.get(symbol, 0.0))
            inst = out["by_instrument"].setdefault(symbol, dict.fromkeys(("gross",) + POSTS, 0.0))
            inst["gross"] += weight * row["returns"].get(symbol, 0.0)
            c = s_ = i_ = 0.0
            if delta > 0:
                turnover += delta
                adv = model.adv(panel, symbol, row["signal_date"])
                if not adv > 0:
                    out["undetermined"].append({"symbol": symbol, "date": row["signal_date"], "why": "ADV missing or zero"})
                else:
                    # The desk's own fill model computes the impact (no re-implementation); a truncated fill is a capacity REFUSAL here.
                    fill = model.fill(panel, symbol, delta * nav / panel.adjusted(row["entry_date"], symbol, "open"),
                                      row["signal_date"], row["entry_date"])
                    out["max_participation"] = max(out["max_participation"], delta * nav / adv)
                    if fill["capacity_truncated"]:
                        out["breaches"].append({"symbol": symbol, "date": row["signal_date"], "participation": delta * nav / adv})
                    c = delta * model.commission_bps / 10_000.0
                    s_ = delta * model.half_spread_bps / 10_000.0
                    i_ = delta * fill["impact_bps"] / 10_000.0
            short = abs(weight) if weight < 0 else 0.0
            b_, f_ = short * borrow_rate, abs(weight) * financing_rate
            for name, value in zip(POSTS, (c, s_, i_, b_, f_)):
                post[name] += value
                inst[name] += value
        net = gross - sum(post.values())
        out["gross"].append(gross)
        out["net"].append(net)
        for name in POSTS:
            out["posts"][name].append(post[name])
        out["turnover"].append(turnover)
        out["gross_exposure"].append(sum(abs(v) for v in row["weights"].values()))
        out["short_exposure"].append(sum(-v for v in row["weights"].values() if v < 0))
        previous = dict(row["weights"])
    return out


def reconciliation_error(priced: dict) -> float:
    """sum(gross) - sum(all posts) - sum(net), and per-instrument gross - posts vs the instrument totals."""
    total = sum(priced["gross"]) - sum(sum(v) for v in priced["posts"].values()) - sum(priced["net"])
    by_inst = sum(v["gross"] - sum(v[p] for p in POSTS) for v in priced["by_instrument"].values()) - sum(priced["net"])
    return max(abs(total), abs(by_inst))


def break_even(rows, panel, nav, key: str, lo: float = 0.0, hi: float = 10_000.0, tol: float = 1e-6, initial=None):
    """Value (bp) of one assumption at which the arithmetic net P&L is zero, others at central; NOT_BRACKETED otherwise."""
    def net_sum(value):
        params = dict(CENTRAL)
        params[key] = value
        return sum(price_rows(rows, panel, nav, params, initial=initial)["net"])
    f_lo, f_hi = net_sum(lo), net_sum(hi)
    if f_lo == 0:
        return lo
    if f_lo * f_hi > 0:
        return {"status": "NOT_BRACKETED", "net_at_low": f_lo, "net_at_high": f_hi}
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = net_sum(mid)
        if f_mid == 0 or (hi - lo) / 2 < tol:
            return mid
        if f_lo * f_mid < 0:
            hi = mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2


# ------------------------------------------------------------------ metrics and criteria
def metrics_from(rows: list[dict], priced: dict, stress_priced: dict) -> dict:
    net = priced["net"]
    middle = len(net) // 2
    years: dict[str, float] = {}
    for row, value in zip(rows, net):
        years[row["exit_date"][:4]] = years.get(row["exit_date"][:4], 0.0) + value
    positive_total = sum(max(v, 0.0) for v in years.values())
    contributions = {s: v["gross"] - sum(v[p] for p in POSTS) for s, v in priced["by_instrument"].items()}
    gross_total = sum(priced["gross"])
    post_totals = {p: sum(priced["posts"][p]) for p in POSTS}
    return {"observations": len(net), "net_return": b4.compound(net), "net_sharpe": b4.sharpe(net),
            "t_statistic": b4.t_stat(net), "halves": [b4.compound(net[:middle]), b4.compound(net[middle:])],
            "stress_net_return": b4.compound(stress_priced["net"]), "positive_annual_total": positive_total,
            "max_year_share": (max(max(v, 0.0) for v in years.values()) / positive_total) if positive_total > 0 else None,
            "instrument_net_contribution": contributions, "gross_pnl_arithmetic": gross_total,
            "post_totals": post_totals, "net_pnl_arithmetic": sum(net),
            "annual_turnover": (sum(priced["turnover"]) / len(net) * TRADING_DAYS) if net else 0.0,
            "mean_gross_exposure": (sum(priced["gross_exposure"]) / len(net)) if net else 0.0,
            "mean_short_exposure": (sum(priced["short_exposure"]) / len(net)) if net else 0.0,
            "annual_net_sums": years, "max_participation": priced["max_participation"]}


def b2_criteria(m: dict, market: list[float], net: list[float], active: int) -> dict:
    """The seven tests of `quant.factory.evaluate.falsify`, evaluated on the NEW net series; the stress test is the labelled
    stress scenario (the original 2x-cost test is replaced). Same definitions (halves n//2, top-5 share, beta, t threshold)."""
    positives = sorted((v for v in net if v > 0), reverse=True)
    total_positive = sum(positives)
    top5 = (sum(positives[:5]) / total_positive) if total_positive > 0 else 1.0
    mean_m = sum(market) / len(market)
    mean_n = sum(net) / len(net)
    var = sum((x - mean_m) ** 2 for x in market)
    beta = sum((a - mean_n) * (b - mean_m) for a, b in zip(net, market)) / var if var else 0.0
    return {"net_profitable": m["net_return"] > 0, "stress_net_profitable": m["stress_net_return"] > 0,
            "profitable_in_both_subperiods": min(m["halves"]) > 0, "market_beta_below_0_15": abs(beta) < 0.15,
            "top_5_days_below_half_of_gains": top5 < 0.5,
            "t_statistic_survives_multiple_testing": m["t_statistic"] >= required_t_statistic(B2_TRIALS),
            "at_least_100_active_observations": active >= 100}


def status_for(central: dict, stress: dict, criteria_central: dict, criteria_stress: dict, priced: dict) -> dict:
    """Single status per target and NAV (specification section 5 plus erratum E3/E5). UNDETERMINED > INFEASIBLE > SENSITIVE > ROBUST."""
    reasons = []
    if priced["undetermined"]:
        return {"status": "COST_UNDETERMINED", "reasons": [f"{len(priced['undetermined'])} undetermined cost inputs (ADV)"]}
    if priced["breaches"]:
        reasons.append(f"CAPACITY_BREACH on {len(priced['breaches'])} orders (max participation {priced['max_participation']:.4f})")
    if central["net_return"] <= 0:
        reasons.append("central net return not positive")
    failed = sorted(k for k, ok in criteria_central.items() if not ok)
    if failed:
        reasons.append(f"pre-registered criteria failing under the central scenario: {failed}")
    gross = central["gross_pnl_arithmetic"]
    if gross <= 0:
        reasons.append("gross P&L not positive (post-share test not evaluated)")
    if reasons:
        return {"status": "COST_INFEASIBLE", "reasons": reasons}
    sensitive = []
    failed_stress = sorted(k for k, ok in criteria_stress.items() if not ok)
    if failed_stress:
        sensitive.append(f"criteria failing under stress: {failed_stress}")
    big = {p: v / gross for p, v in central["post_totals"].items() if v / gross >= ROBUSTNESS_SHARE}
    if big:
        sensitive.append(f"a single post consumes at least {ROBUSTNESS_SHARE:.0%} of positive gross P&L: {big}")
    if sensitive:
        return {"status": "COST_SENSITIVE", "reasons": sensitive}
    return {"status": "COST_ROBUST", "reasons": []}


# ------------------------------------------------------------------ targets
def b4_targets(panel3: PricePanel) -> dict:
    out = {}
    for L in b4.LOOKBACKS:
        full = b4.rows_for(panel3, L)
        rows = [r for r in full if b4.in_window(r, b4.BOUNDS["EVALUATION"])]
        first = full.index(rows[0])
        # Same convention as B4: the first evaluation row inherits the position held on the previous row.
        out[f"B4_L{L}"] = {"rows": rows, "criteria": "b4", "panel": panel3, "initial": dict(full[first - 1]["weights"]) if first else {}}
    return out


def b2_target(panel12: PricePanel) -> dict:
    grid = {s.label: s for s in lane_definitions(B2_UNIVERSE, "us_sector_etf_daily")["xs_execution_aware_relative_value"]["grid"]}
    spec = StrategySpec(**grid[B2_EXPRESSION].to_dict())
    window = Window("VALIDATION", *B2_WINDOW)
    raw = walk_forward(panel12, spec, window, COST_BPS)
    rows = []
    for r in raw:
        symbols = set(r["weights"])
        returns = {s: panel12.adjusted(r["exit_date"], s, "open") / panel12.adjusted(r["entry_date"], s, "open") - 1.0 for s in symbols}
        rows.append({"signal_date": r["signal_date"], "entry_date": r["entry_date"], "exit_date": r["exit_date"],
                     "weights": dict(r["weights"]), "returns": returns, "positions": r["positions"]})
    market = [panel12.adjusted(r["exit_date"], "SPY", "open") / panel12.adjusted(r["entry_date"], "SPY", "open") - 1.0 for r in rows]
    return {"B2_lane2_selected": {"rows": rows, "criteria": "b2", "panel": panel12, "market": market, "initial": {}}}


def analyse_target(target: dict, nav: float) -> dict:
    rows, panel, initial = target["rows"], target["panel"], target.get("initial")
    central = price_rows(rows, panel, nav, CENTRAL, initial=initial)
    stress = price_rows(rows, panel, nav, STRESS, initial=initial)
    m_c, m_s = metrics_from(rows, central, stress), metrics_from(rows, stress, stress)
    if target["criteria"] == "b4":
        crit_c, crit_s = b4.criteria(m_c), b4.criteria(m_s)
    else:
        active = sum(1 for r in rows if r.get("positions", 0) > 0)
        crit_c = b2_criteria(m_c, target["market"], central["net"], active)
        crit_s = b2_criteria(m_s, target["market"], stress["net"], active)
    grid = {}
    for mult in MULTIPLIERS:
        pr = price_rows(rows, panel, nav, CENTRAL, mult, initial=initial)
        grid[str(mult)] = {"net_return": b4.compound(pr["net"]), "net_sharpe": b4.sharpe(pr["net"]),
                           "post_totals": {p: sum(pr["posts"][p]) for p in POSTS}, "breaches": len(pr["breaches"]),
                           "note": "0x is a gross diagnostic, never an admissibility scenario" if mult == 0.0 else ""}
    hist = price_rows(rows, panel, nav, {"commission_bps": 5.0, "half_spread_bps": 0.0, "impact_bps_at_5pct": 0.0,
                                         "borrow_bps_year": 0.0, "financing_bps_year": 0.0}, initial=initial)
    return {"nav": nav, "COST_INPUT_KIND": "ASSUMED_NOT_ESTIMATED", "central": m_c, "stress": m_s,
            "criteria_central": crit_c, "criteria_stress": crit_s,
            "status": status_for(m_c, m_s, crit_c, crit_s, central),
            "capacity_breaches": central["breaches"][:5], "capacity_breach_count": len(central["breaches"]),
            "undetermined": central["undetermined"][:5],
            "reconciliation_error": max(reconciliation_error(central), reconciliation_error(stress)),
            "break_even": {"half_spread_bps": break_even(rows, panel, nav, "half_spread_bps", initial=initial),
                           "borrow_bps_year": break_even(rows, panel, nav, "borrow_bps_year", initial=initial),
                           "financing_bps_year": break_even(rows, panel, nav, "financing_bps_year", initial=initial)},
            "multiplier_grid": grid,
            "historical_5bp_model_diagnostic": {"label": "5 pb par unité de turnover, sans borrow ni financement : diagnostic de modèle, pas une preuve économique",
                                                "net_return": b4.compound(hist["net"]), "net_sharpe": b4.sharpe(hist["net"])}}


def compute(data_path: Path = DATA, fingerprint: str = FINGERPRINT, meta_path: Path = b4.META) -> dict:
    check_frozen_dependency()
    before = b4.file_fingerprint(data_path)
    if before != fingerprint:
        raise InvalidInput(f"dataset fingerprint {before} != {fingerprint}")
    b4.check_metadata(meta_path, fingerprint)
    panel12, skipped = build_panel(data_path, B2_PANEL_SYMBOLS + ["TLT", "GLD"])
    late = [d for d in panel12.dates if d >= FIRST_FORBIDDEN_DATE]
    if late:
        raise InvalidInput(f"research view contains dates from {FIRST_FORBIDDEN_DATE}: {late[:3]}")
    if panel12.dates[-1] != LAST_RESEARCH_DATE:
        raise InvalidInput(f"research view ends {panel12.dates[-1]}")
    panel3 = panel12.restrict(symbols=b4.INSTRUMENTS)
    targets = {**b2_target(panel12.restrict(symbols=B2_PANEL_SYMBOLS)), **b4_targets(panel3)}
    out = {"targets": {}}
    for name, target in targets.items():
        out["targets"][name] = [analyse_target(target, nav) for nav in NAV_GRID]
    after = b4.file_fingerprint(data_path)
    if after != before:
        raise InvalidInput("dataset changed during the run")
    out.update({"fingerprint_before": before, "fingerprint_after": after, "last_date_read": panel12.dates[-1],
                "rows_skipped_before_parsing": skipped})
    return out


# ------------------------------------------------------------------ run protocol
def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    target = Path(argv[1]).resolve()
    if target.exists():
        print(f"STOP: {target} already exists; the diagnostic is a single execution")
        return 2
    if any(str(target).startswith(str(ROOT / p) + "/") for p in ("data", "var", "src")):
        print("STOP: the result may not be written under data/, var/ or src/")
        return 2
    if not target.parent.is_dir():
        print(f"STOP: the result directory {target.parent} must already exist (the harness creates no directory)")
        return 2
    snap_before = b4.snapshot(ROOT)
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    result = {"specification_sha256": SPEC_SHA256, "command": " ".join(argv), "git_commit": commit,
              "python": platform.python_version(), "assumptions": {"central": CENTRAL, "stress": STRESS, "nav_grid": NAV_GRID,
                                                                    "multipliers": MULTIPLIERS},
              "limits": ["every spread, impact, borrow and financing value is an ASSUMPTION, not a measurement",
                         "borrow is charged on ALL short exposure (specification: 'exposition short'), including SPY and sector ETFs",
                         "financing is charged on gross exposure with no interest credited on cash",
                         "descriptive only: B2 and B4 rejections are unchanged by any status here; the spent window is not reopened for selection",
                         "raw bytes of the CSV were hashed for the fingerprint; lines dated 2025-03-12 or later were counted and discarded by their leading date without parsing"]}
    try:
        run1 = compute()
        run2 = compute()
        result.update({"RESULT": "REPRODUCTION_DIVERGENCE" if not b4.same(run1, run2) else "DIAGNOSTIC_COMPLETE", "run": run1, "problems": []})
        rc = 0
    except InvalidInput as exc:
        result.update({"RESULT": "INVALID_INPUT", "problems": [str(exc)]})
        rc = 1
    spurious = b4.delta(snap_before, b4.snapshot(ROOT))
    result["filesystem_delta_before_result_write"] = spurious
    if spurious:
        result["RESULT"], rc = "INVALID_INPUT", 1
        result["problems"] = result.get("problems", []) + [f"unexpected filesystem change before the result write: {spurious[:5]}"]
    result.update({"DISCOVERY_CLAIM": False, "VALIDATION_CLAIM": False, "SHADOW_BAR_ANALYSED": False, "STRATEGY_PROMOTION_AUTHORIZED": False,
                   "TRADABLE_STRATEGY": False, "REAL_CAPITAL_AUTHORIZED": False, "NEW_MARKET_DATA_USED": False, "return_code": rc})
    with open(target, "x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    unexpected = [p for p in b4.delta(snap_before, b4.snapshot(ROOT)) if p not in (str(target), str(target.parent))]
    if unexpected:
        print(f"FILESYSTEM DELTA BEYOND THE RESULT FILE: {unexpected[:5]}")
        rc = 3
        result.update({"RESULT": "INVALID_INPUT", "return_code": 3,
                       "problems": result.get("problems", []) + [f"filesystem change after the result write: {unexpected[:5]}"]})
        with open(target, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(f"RESULT: {result['RESULT']}")
    for p in result["problems"]:
        print(f"  - {p}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
