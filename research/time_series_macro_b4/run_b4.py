#!/usr/bin/env python3
"""B4: MACRO-TSMOM-001, time-series momentum on SPY/TLT/GLD. Read-only, single execution, pre-registered.

Pre-registration: research/time_series_macro_b4/PREREGISTRATION_2026-10-08.md
  SHA-256 11f77332f9551028dc6b19f91a1fc939513511f0e1c2188d6fdffef83d9c7c5d
Erratum 1 (accepted by the orchestrator, comment 6057563728):
  research/time_series_macro_b4/ERRATUM_1_2026-10-08.md
  SHA-256 e561a9c684d041b0bb0f66fed914e865726e6fe42dc1d7e4220ab953e074637b
Claims no discovery, no independent validation, no tradable strategy. The 2022-03-09..2025-03-11 window is spent at
dataset level. No bar dated 2025-03-12 or later is ever parsed. Writes exactly one new file (the result).

Usage: PYTHONPATH=src python3 -B research/time_series_macro_b4/run_b4.py <result.json>   (result directory must exist)
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # before any project import: no __pycache__ may be created

import csv
import hashlib
import json
import math
import os
import platform
import re
import statistics
import subprocess
from pathlib import Path

from quant.dataplane.panel import PricePanel

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/datasets/us_sector_etf_daily.csv"
REGISTRY = ROOT / "var/strategies.json"
STATE_MD = ROOT / "STATE.md"
FINGERPRINT = "sha256:f108a6f41552afdb42100d3188d7194006de1aae6a27bd7722330818e6dcb6d1"
PREREG_SHA256 = "11f77332f9551028dc6b19f91a1fc939513511f0e1c2188d6fdffef83d9c7c5d"
ERRATUM_SHA256 = "e561a9c684d041b0bb0f66fed914e865726e6fe42dc1d7e4220ab953e074637b"
DATASET_ID = "us_sector_etf_daily"
INSTRUMENTS = ("SPY", "TLT", "GLD")
BORROW_INSTRUMENTS = ("TLT", "GLD")
LOOKBACKS = (21, 63, 126, 252)
BOUNDS = {"DISCOVERY": ("2016-09-12", "2022-03-08"), "EVALUATION": ("2022-03-09", "2025-03-11")}
FIRST_FORBIDDEN_DATE = "2025-03-12"
LAST_RESEARCH_DATE = "2025-03-11"
PRIOR_TRIALS = 36
TRIAL_COUNT = 40
T_THRESHOLD = 3.227          # pre-registered; never rounded down or recomputed
COST_BP, BORROW_BP = 5.0, 100.0
STRESS_COST_BP, STRESS_BORROW_BP = 10.0, 300.0
TRADING_DAYS = 252
SELF_REL_TOL = 1e-9
TIE = 1e-12


class InvalidInput(Exception):
    pass


class InvalidTrialCount(InvalidInput):
    pass


# ---------------------------------------------------------------- input gates
def file_fingerprint(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def build_research_panel(path: Path) -> tuple[PricePanel, int]:
    """Drop every row dated FIRST_FORBIDDEN_DATE or later BEFORE any numeric conversion or PricePanel construction."""
    kept, skipped = [], 0
    with path.open(encoding="utf-8", newline="") as handle:
        for record in csv.DictReader(handle):
            if record["date"] >= FIRST_FORBIDDEN_DATE:
                skipped += 1
                continue
            if record["symbol"] in INSTRUMENTS:
                kept.append(record)
    return PricePanel(kept), skipped


def trial_count_source(registry: Path = REGISTRY, state_md: Path = STATE_MD) -> str:
    """Erratum E2: a readable registry must say exactly 36; with no registry, STATE.md's recorded 36; conflict = invalid."""
    if registry.exists():
        try:
            payload = json.loads(registry.read_text(encoding="utf-8"))
            trials = payload.get("trials") or {}
            count = sum(int(v) for k, v in trials.items() if k == DATASET_ID or k.startswith(DATASET_ID + "@"))
        except (ValueError, TypeError, AttributeError) as exc:
            raise InvalidTrialCount(f"registry unreadable or ambiguous: {exc}")
        if count != PRIOR_TRIALS:
            raise InvalidTrialCount(f"registry records {count} expressions on the dataset, pre-registered {PRIOR_TRIALS}")
        return "REGISTRY"
    if not state_md.exists():
        raise InvalidTrialCount("no registry and no STATE.md")
    found = {int(n) for n in re.findall(r"after\s+(\d+)\s+declared expressions", state_md.read_text(encoding="utf-8"), re.I)}
    if found != {PRIOR_TRIALS}:
        raise InvalidTrialCount(f"STATE.md records {sorted(found)} declared expressions, pre-registered {PRIOR_TRIALS}")
    return "STATE_MD_NO_REGISTRY"


# ------------------------------------------------------------------ evaluation
def sign(x: float) -> int:
    return 1 if x > 0 else (-1 if x < 0 else 0)


def rows_for(panel: PricePanel, lookback: int) -> list[dict]:
    """One row per executable day. Signal from adj_close through the close of t; weights signal/3; entry at the adjusted
    open of t+1; exit at the adjusted open of t+2. Turnover = sum |change in target weight|, from the previous row
    (zero before the first signal). Rows exist only from the first causal signal (k >= L); earlier days are cash."""
    dates = panel.aligned_dates(INSTRUMENTS)
    rows, previous = [], {name: 0.0 for name in INSTRUMENTS}
    for k in range(lookback, len(dates) - 2):
        t, entry, exit_ = dates[k], dates[k + 1], dates[k + 2]
        weights, returns = {}, {}
        for name in INSTRUMENTS:
            past = panel.price(dates[k - lookback], name)
            weights[name] = sign(panel.price(t, name) / past - 1.0 if past else 0.0) / 3.0
            returns[name] = panel.adjusted(exit_, name, "open") / panel.adjusted(entry, name, "open") - 1.0
        turnover = {name: abs(weights[name] - previous[name]) for name in INSTRUMENTS}
        rows.append({"signal_date": t, "entry_date": entry, "exit_date": exit_, "k": k,
                     "weights": weights, "returns": returns, "turnover": turnover})
        previous = weights
    return rows


def in_window(row: dict, bounds: tuple[str, str]) -> bool:
    return all(bounds[0] <= row[key] <= bounds[1] for key in ("signal_date", "entry_date", "exit_date"))


def net_parts(row: dict, cost_bp: float, borrow_bp: float) -> dict:
    """Per-instrument net contribution for one row; the sum over instruments is the row's net return."""
    parts = {}
    for name in INSTRUMENTS:
        gross = row["weights"][name] * row["returns"][name]
        cost = row["turnover"][name] * cost_bp / 10_000.0
        short = abs(row["weights"][name]) if (name in BORROW_INSTRUMENTS and row["weights"][name] < 0) else 0.0
        borrow = short * borrow_bp / 10_000.0 / TRADING_DAYS
        parts[name] = {"gross": gross, "cost": cost, "borrow": borrow, "net": gross - cost - borrow}
    return parts


def net_series(rows, cost_bp=COST_BP, borrow_bp=BORROW_BP) -> list[float]:
    return [sum(p["net"] for p in net_parts(r, cost_bp, borrow_bp).values()) for r in rows]


def compound(values) -> float:
    total = 1.0
    for v in values:
        total *= 1.0 + v
    return total - 1.0


def sharpe(values) -> float:
    if len(values) < 2:
        return 0.0
    sd = statistics.stdev(values)
    return (statistics.fmean(values) * TRADING_DAYS / (sd * math.sqrt(TRADING_DAYS))) if sd else 0.0


def t_stat(values) -> float:
    if len(values) < 2:
        return 0.0
    sd = statistics.stdev(values)
    return statistics.fmean(values) / (sd / math.sqrt(len(values))) if sd else 0.0


def beta_vs(values, market) -> float:
    if len(values) < 2:
        return 0.0
    mv, mm = statistics.fmean(values), statistics.fmean(market)
    var = sum((m - mm) ** 2 for m in market)
    return sum((v - mv) * (m - mm) for v, m in zip(values, market)) / var if var else 0.0


def metrics(rows: list[dict]) -> dict:
    """Years are calendar years of the exit date (the day the return is earned)."""
    net = net_series(rows)
    stress = net_series(rows, STRESS_COST_BP, STRESS_BORROW_BP)
    middle = len(net) // 2
    years: dict[str, float] = {}
    contributions = {name: 0.0 for name in INSTRUMENTS}
    costs = borrow = 0.0
    for row, value in zip(rows, net):
        years[row["exit_date"][:4]] = years.get(row["exit_date"][:4], 0.0) + value
        parts = net_parts(row, COST_BP, BORROW_BP)
        for name in INSTRUMENTS:
            contributions[name] += parts[name]["net"]
            costs += parts[name]["cost"]
            borrow += parts[name]["borrow"]
    positive_total = sum(max(v, 0.0) for v in years.values())
    return {"observations": len(net), "net_return": compound(net), "net_sharpe": sharpe(net), "t_statistic": t_stat(net),
            "halves": [compound(net[:middle]), compound(net[middle:])],
            "stress_net_return": compound(stress),
            "annual_net_sums": years, "positive_annual_total": positive_total,
            "max_year_share": (max(max(v, 0.0) for v in years.values()) / positive_total) if positive_total > 0 else None,
            "instrument_net_contribution": contributions,
            "instrument_contribution_sum": sum(contributions.values()), "arithmetic_net_sum": sum(net),
            "total_transaction_cost": costs, "total_borrow": borrow,
            "annual_turnover": sum(sum(r["turnover"].values()) for r in rows) / len(rows) * TRADING_DAYS if rows else 0.0,
            "mean_signed_exposure": statistics.fmean([sum(r["weights"].values()) for r in rows]) if rows else 0.0,
            "first_signal_date": rows[0]["signal_date"] if rows else None,
            "last_exit_date": rows[-1]["exit_date"] if rows else None}


def criteria(m: dict) -> dict:
    positive_instruments = sum(1 for v in m["instrument_net_contribution"].values() if v > 0)
    return {
        "1_net_return_positive": m["net_return"] > 0,
        "2_net_sharpe_positive": m["net_sharpe"] > 0,
        "3_t_statistic_at_least_threshold": m["t_statistic"] >= T_THRESHOLD,
        "4_both_halves_positive": min(m["halves"]) > 0,
        "5_stress_net_positive": m["stress_net_return"] > 0,
        "6_no_year_above_60pct": m["positive_annual_total"] > 0 and m["max_year_share"] <= 0.6,
        "7_at_least_two_instruments_positive": positive_instruments >= 2}


def comparators(panel: PricePanel, rows: list[dict]) -> dict:
    """Cash, equal-weight buy-and-hold, permanent +1/3 (daily rebalanced), and SPY, over the same rows."""
    first_entry, last_exit = rows[0]["entry_date"], rows[-1]["exit_date"]
    hold = {n: panel.adjusted(last_exit, n, "open") / panel.adjusted(first_entry, n, "open") - 1.0 for n in INSTRUMENTS}
    permanent = [sum(r["returns"][n] for n in INSTRUMENTS) / 3.0 for r in rows]
    spy = [r["returns"]["SPY"] for r in rows]
    return {"cash": 0.0, "buy_and_hold_equal_weight": sum(hold.values()) / 3.0, "buy_and_hold_by_instrument": hold,
            "permanent_one_third_daily_rebalanced": compound(permanent), "spy_open_to_open": compound(spy)}


def common_discovery_rows(rows: list[dict], bounds: tuple[str, str]) -> list[dict]:
    """Discovery rows on the common intersection: from the first causal signal of the longest lookback."""
    return [r for r in rows if r["k"] >= max(LOOKBACKS) and in_window(r, bounds)]


def select_lookback(scores: dict) -> int:
    """Highest net central discovery Sharpe; ties within 1e-12 go to the smaller L (a later L must win by more than TIE)."""
    best = None
    for L in sorted(scores):
        if best is None or scores[L] > scores[best] + TIE:
            best = L
    return best


def evaluate_family(panel: PricePanel, bounds=BOUNDS) -> dict:
    """Pure: select on discovery (common intersection, net central Sharpe, ties to the smaller L), then evaluate."""
    all_rows = {L: rows_for(panel, L) for L in LOOKBACKS}
    discovery = {L: common_discovery_rows(all_rows[L], bounds["DISCOVERY"]) for L in LOOKBACKS}
    scores = {L: sharpe(net_series(discovery[L])) for L in LOOKBACKS}
    best = select_lookback(scores)
    evaluation = {L: [r for r in all_rows[L] if in_window(r, bounds["EVALUATION"])] for L in LOOKBACKS}
    per_expression = {}
    for L in LOOKBACKS:
        eligible_discovery = [r for r in all_rows[L] if in_window(r, bounds["DISCOVERY"])]
        per_expression[str(L)] = {
            "discovery_common_intersection_net_sharpe": scores[L],
            "discovery_own_eligible_period": {"label": "own eligible period; not used for selection",
                                              "net_sharpe": sharpe(net_series(eligible_discovery)),
                                              "observations": len(eligible_discovery)},
            "evaluation": metrics(evaluation[L]),
            "evaluation_comparison_only_not_for_selection": True}
    candidate = metrics(evaluation[best])
    checks = criteria(candidate)
    return {"selected_lookback": best, "selection_scores": {str(L): scores[L] for L in LOOKBACKS},
            "per_expression": per_expression, "candidate_metrics": candidate, "criteria": checks,
            "failed_criteria": sorted(k for k, ok in checks.items() if not ok),
            "all_criteria_true": all(checks.values()),
            "comparators": comparators(panel, evaluation[best]),
            "candidate_spy_beta": beta_vs(net_series(evaluation[best]), [r["returns"]["SPY"] for r in evaluation[best]]),
            "reconciliation_error": abs(candidate["instrument_contribution_sum"] - candidate["arithmetic_net_sum"])}


def compute(data_path: Path = DATA, fingerprint: str = FINGERPRINT, bounds=BOUNDS, registry: Path = REGISTRY,
            state_md: Path = STATE_MD) -> dict:
    before = file_fingerprint(data_path)  # raw-byte hash; no bar is parsed for it
    if before != fingerprint:
        raise InvalidInput(f"dataset fingerprint {before} != {fingerprint}")
    if dict(bounds) != BOUNDS:
        raise InvalidInput(f"window bounds {dict(bounds)} differ from pre-registered {BOUNDS}")
    source = trial_count_source(registry, state_md)
    panel, skipped = build_research_panel(data_path)
    late = [d for d in panel.dates if d >= FIRST_FORBIDDEN_DATE]
    if late:
        raise InvalidInput(f"research view contains dates from {FIRST_FORBIDDEN_DATE}: {late[:3]}")
    if sorted(panel.symbols) != sorted(INSTRUMENTS):
        raise InvalidInput(f"instruments {panel.symbols}")
    if panel.dates[0] != BOUNDS["DISCOVERY"][0] or panel.dates[-1] != LAST_RESEARCH_DATE:
        raise InvalidInput(f"research view spans {panel.dates[0]}..{panel.dates[-1]}")
    out = evaluate_family(panel, bounds)
    if out["reconciliation_error"] > 1e-12:
        raise InvalidInput(f"instrument contributions do not reconcile with net return: {out['reconciliation_error']}")
    after = file_fingerprint(data_path)
    if after != before:
        raise InvalidInput("dataset changed during the run")
    out.update({"fingerprint_before": before, "fingerprint_after": after, "last_date_read": max(panel.dates),
                "rows_skipped_before_parsing": skipped, "TRIAL_COUNT_SOURCE": source,
                "DATASET_LEVEL_TRIAL_COUNT": TRIAL_COUNT, "T_THRESHOLD": T_THRESHOLD})
    return out


# ------------------------------------------------------------------ judgement
def same(a, b) -> bool:
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, float) or isinstance(b, float):
        return (isinstance(a, (int, float)) and isinstance(b, (int, float))
                and math.isclose(float(a), float(b), rel_tol=SELF_REL_TOL, abs_tol=1e-12))
    return a == b


def judge(run1: dict, run2: dict) -> str:
    if not same(run1, run2):
        return "REPRODUCTION_DIVERGENCE"
    return "PROVISIONAL_POSITIVE_ON_SPENT_DATA" if run1["all_criteria_true"] else "FAMILY_REJECTED"


# ------------------------------------------------------------------ filesystem
def snapshot(root: Path) -> dict:
    seen = {}
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in dirs + files:
            full = os.path.join(base, name)
            st = os.lstat(full)
            seen[full] = (st.st_size, st.st_mtime_ns)
    return seen


def delta(before: dict, after: dict) -> list:
    return sorted([p for p in after if p not in before] + [p for p in before if p not in after or before[p] != after[p]])


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    target = Path(argv[1]).resolve()
    if target.exists():
        print(f"STOP: {target} already exists; B4 is a single execution")
        return 2
    if any(str(target).startswith(str(ROOT / p) + "/") for p in ("data", "var", "src")):
        print("STOP: the result may not be written under data/, var/ or src/")
        return 2
    if not target.parent.is_dir():
        print(f"STOP: the result directory {target.parent} must already exist (the harness creates no directory)")
        return 2
    snap_before = snapshot(ROOT)
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    result = {"preregistration_sha256": PREREG_SHA256, "erratum_1_sha256": ERRATUM_SHA256, "command": " ".join(argv),
              "git_commit": commit, "python": platform.python_version(),
              "costs": {"transaction_bp_per_unit_turnover": COST_BP, "borrow_bp_annual_tlt_gld_short": BORROW_BP,
                        "stress": [STRESS_COST_BP, STRESS_BORROW_BP]},
              "limits": ["adj_close is retroactively restated and not strictly point-in-time; TLT adj_close embeds later distributions, GLD does not",
                         "2022-03-09..2025-03-11 is already spent at dataset level; a positive result is exploratory only",
                         "the 2022 bond shock was known before this pre-registration",
                         "raw bytes of the CSV were hashed for the fingerprint; no bar from 2025-03-12 onward was parsed or analysed",
                         "cost envelope is simple (5 bp, 100 bp borrow); not a realistic execution model"]}
    try:
        run1 = compute()
        run2 = compute()
        status = judge(run1, run2)
        result.update({"RESULT": status, "run": run1, "problems": []})
        rc = 0
    except InvalidTrialCount as exc:
        result.update({"RESULT": "INVALID_TRIAL_COUNT", "problems": [str(exc)]})
        rc = 1
    except InvalidInput as exc:
        result.update({"RESULT": "INVALID_INPUT", "problems": [str(exc)]})
        rc = 1
    spurious = delta(snap_before, snapshot(ROOT))
    result["filesystem_delta_before_result_write"] = spurious
    result["raw_bytes_hashed_for_fingerprint_only"] = True
    if spurious:
        result["RESULT"], rc = "INVALID_INPUT", 1
        result["problems"] = result.get("problems", []) + [f"unexpected filesystem change before the result write: {spurious[:5]}"]
    result.update({"LESSON": "bounded finding, see RESULT and failed_criteria; no discovery claim",
                   "PRIORITY_UPDATE": "abandon or audit the family; do not recycle the spent window; next needs a causally different family on virgin data or authorised point-in-time data",
                   "NEXT_ACTION": "separate absence of edge, cost, beta and concentration in the reading",
                   "DISCOVERY_CLAIM": False, "INDEPENDENT_VALIDATION_CLAIM": False, "SHADOW_BAR_ANALYSED": False,
                   "TRADABLE_STRATEGY": False, "REAL_CAPITAL_AUTHORIZED": False, "return_code": rc})
    with open(target, "x", encoding="utf-8") as handle:  # 'x': never overwrite
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    unexpected = [p for p in delta(snap_before, snapshot(ROOT)) if p not in (str(target), str(target.parent))]
    if unexpected:
        print(f"FILESYSTEM DELTA BEYOND THE RESULT FILE: {unexpected[:5]}")
        rc = 3
    print(f"RESULT: {result['RESULT']}")
    for p in result["problems"]:
        print(f"  - {p}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
