from __future__ import annotations

import csv
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

EXPERIMENT_ID = "disc-monthend-pension-rebalance-spytlt-l1-v1"
INVOCATION_ID = "owner-manual-20261012-a1"
PREDECLARATION_COMMIT = "6f4a2d5160ba9aef62b841057fee4a95a0df338f"
CLAIM_COMMIT = "05c32f46b01ebaa2e933c34b0cb7dc913ff96aec"
DATA = Path("data/datasets/us_sector_etf_daily.csv")
META = Path("data/datasets/us_sector_etf_daily.meta.json")
RESULT = Path(__file__).with_name("disc-monthend-pension-rebalance-spytlt-l1-v1.result.json")
EXPECTED_FINGERPRINT = "sha256:f108a6f41552afdb42100d3188d7194006de1aae6a27bd7722330818e6dcb6d1"
SYMBOLS = ["SPY", "TLT"]
CENTRAL_COST = 0.0008
STRESS_COST = 0.0016


def fmean(xs):
    return statistics.fmean(xs) if xs else None


def median(xs):
    return statistics.median(xs) if xs else None


def write_result(obj):
    RESULT.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def park_data(base, reason, details=None):
    base.update({
        "typed_verdict": "PARK_DATA",
        "decision": "PARK_DATA",
        "economics_computed": False,
        "edge_validated": False,
        "reason": reason,
    })
    if details is not None:
        base["details"] = details
    write_result(base)
    raise SystemExit(0)


def ym(date_str: str) -> str:
    return date_str[:7]


def main():
    if RESULT.exists():
        raise SystemExit("result already exists; replay forbidden")

    base = {
        "experiment_id": EXPERIMENT_ID,
        "invocation_id": INVOCATION_ID,
        "predeclaration_commit": PREDECLARATION_COMMIT,
        "claim_commit": CLAIM_COMMIT,
        "attempt": 1,
        "replay_allowed": False,
        "label": "EXPLORATORY",
        "claim_ceiling": "PROMOTE_EXPRESSION",
        "real_capital_authorized": False,
        "live_trading_authorized": False,
        "paid_usd": 0,
        "frozen": {
            "dataset": str(DATA),
            "expected_fingerprint": EXPECTED_FINGERPRINT,
            "symbols": SYMBOLS,
            "signal": "negative sign of SPY minus TLT month-to-date raw close return at penultimate session",
            "payoff": "final-session SPY minus TLT open-to-close relative spread",
            "central_roundtrip_cost": CENTRAL_COST,
            "stress_roundtrip_cost": STRESS_COST,
        },
    }

    if not DATA.exists() or not META.exists():
        park_data(base, "Frozen committed dataset or metadata file is missing.")

    meta = json.loads(META.read_text(encoding="utf-8"))
    if meta.get("fingerprint") != EXPECTED_FINGERPRINT:
        park_data(base, "Frozen dataset metadata fingerprint mismatch.", {
            "observed": meta.get("fingerprint"), "expected": EXPECTED_FINGERPRINT
        })

    raw_sha256 = hashlib.sha256(DATA.read_bytes()).hexdigest()
    base["dataset_proof"] = {
        "meta_fingerprint": meta.get("fingerprint"),
        "raw_csv_sha256_observed": "sha256:" + raw_sha256,
        "meta_rows": meta.get("rows"),
        "meta_first_date": meta.get("first_date"),
        "meta_last_date": meta.get("last_date"),
    }

    rows = {s: {} for s in SYMBOLS}
    with DATA.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        required = {"date", "symbol", "open", "close"}
        if not required.issubset(fields):
            park_data(base, "Required exact CSV columns are absent; aliases are forbidden after claim.", {
                "required_columns": sorted(required), "observed_columns": fields
            })
        for row in reader:
            s = row["symbol"]
            if s not in rows:
                continue
            d = row["date"]
            if d in rows[s]:
                park_data(base, "Duplicate symbol/date row.", {"symbol": s, "date": d})
            try:
                o = float(row["open"])
                c = float(row["close"])
            except Exception as e:
                park_data(base, "Non-numeric price field.", {"symbol": s, "date": d, "error": str(e)})
            if not (o > 0 and c > 0):
                park_data(base, "Non-positive raw price.", {"symbol": s, "date": d})
            rows[s][d] = {"open": o, "close": c}

    date_sets = {s: set(rows[s]) for s in SYMBOLS}
    common = set.intersection(*(date_sets[s] for s in SYMBOLS))
    if any(date_sets[s] != common for s in SYMBOLS):
        park_data(base, "SPY/TLT panels are not exactly aligned; post-claim repair is forbidden.", {
            "rows_by_symbol": {s: len(rows[s]) for s in SYMBOLS},
            "common_dates": len(common),
        })
    dates = sorted(common)
    if len(dates) < 3:
        park_data(base, "Aligned SPY/TLT panel too short.")

    # Predeclared contamination guard before any payoff calculation.
    max_abs_cc = 0.0
    max_where = None
    for i in range(1, len(dates)):
        d, p = dates[i], dates[i-1]
        for s in SYMBOLS:
            r = rows[s][d]["close"] / rows[s][p]["close"] - 1.0
            if abs(r) > max_abs_cc:
                max_abs_cc = abs(r)
                max_where = {"symbol": s, "date": d, "raw_close_to_close_return": r}
    base["schema_checks"] = {
        "aligned_sessions": len(dates),
        "first_date": dates[0],
        "last_date": dates[-1],
        "max_abs_raw_close_to_close_return": max_abs_cc,
        "max_abs_raw_close_to_close_where": max_where,
    }
    if max_abs_cc > 0.25:
        park_data(base, "Predeclared >25% raw close-to-close contamination guard fired before payoff calculation.", max_where)

    months = defaultdict(list)
    for d in dates:
        months[ym(d)].append(d)
    ordered_months = sorted(months)

    events = []
    skipped = []
    for idx in range(1, len(ordered_months)):
        m = ordered_months[idx]
        prev_m = ordered_months[idx - 1]
        current_dates = sorted(months[m])
        prev_dates = sorted(months[prev_m])
        # Require calendar-consecutive months so the truncated first/last panel cannot silently bridge gaps.
        py, pm = map(int, prev_m.split("-"))
        cy, cm = map(int, m.split("-"))
        next_y, next_m = (py + 1, 1) if pm == 12 else (py, pm + 1)
        if (cy, cm) != (next_y, next_m):
            skipped.append({"month": m, "reason": "non-consecutive calendar month"})
            continue
        if len(current_dates) < 2 or not prev_dates:
            skipped.append({"month": m, "reason": "insufficient sessions"})
            continue
        prev_end = prev_dates[-1]
        penultimate = current_dates[-2]
        final = current_dates[-1]
        r_spy_mtd = rows["SPY"][penultimate]["close"] / rows["SPY"][prev_end]["close"] - 1.0
        r_tlt_mtd = rows["TLT"][penultimate]["close"] / rows["TLT"][prev_end]["close"] - 1.0
        relative_mtd = r_spy_mtd - r_tlt_mtd
        if relative_mtd == 0.0:
            skipped.append({"month": m, "reason": "exact zero relative MTD"})
            continue
        signal = -1 if relative_mtd > 0 else 1
        spy_oc = rows["SPY"][final]["close"] / rows["SPY"][final]["open"] - 1.0
        tlt_oc = rows["TLT"][final]["close"] / rows["TLT"][final]["open"] - 1.0
        relative_oc = spy_oc - tlt_oc
        gross = signal * relative_oc
        events.append({
            "month": m,
            "prev_end": prev_end,
            "penultimate": penultimate,
            "final": final,
            "relative_mtd": relative_mtd,
            "signal": signal,
            "gross": gross,
            "central_net": gross - CENTRAL_COST,
            "stress_net": gross - STRESS_COST,
        })

    signal_counts = {
        "+1": sum(1 for e in events if e["signal"] == 1),
        "-1": sum(1 for e in events if e["signal"] == -1),
    }
    base["adequacy"] = {
        "eligible_events": len(events),
        "signal_counts": signal_counts,
        "skipped_months": len(skipped),
        "requires_total_at_least": 100,
        "requires_each_signal_at_least": 40,
        "endpoint_coverage": 1.0,
    }
    if not (len(events) >= 100 and signal_counts["+1"] >= 40 and signal_counts["-1"] >= 40):
        park_data(base, "Frozen adequacy gate failed; no signal threshold, window, cost or instrument change is allowed.", base["adequacy"])

    gross = [e["gross"] for e in events]
    central = [e["central_net"] for e in events]
    stress = [e["stress_net"] for e in events]
    by_signal = {
        str(sig): fmean([e["central_net"] for e in events if e["signal"] == sig])
        for sig in (1, -1)
    }
    block1 = [e["central_net"] for e in events if e["final"] <= "2021-12-31"]
    block2 = [e["central_net"] for e in events if e["final"] >= "2022-01-01"]
    yearly = defaultdict(list)
    for e in events:
        yearly[e["final"][:4]].append(e["central_net"])

    primary = {
        "mean_signed_gross_return": fmean(gross),
        "mean_central_net_return": fmean(central),
        "mean_stress_net_return": fmean(stress),
        "median_central_net_return": median(central),
        "central_net_hit_rate": sum(1 for x in central if x > 0) / len(central),
        "mean_central_net_by_signal": by_signal,
        "mean_central_net_through_2021": fmean(block1),
        "mean_central_net_from_2022": fmean(block2),
        "block_event_counts": {"through_2021": len(block1), "from_2022": len(block2)},
        "yearly": {
            y: {"events": len(xs), "mean_central_net": fmean(xs), "sum_central_net": sum(xs)}
            for y, xs in sorted(yearly.items())
        },
        "worst_central_net_return": min(central),
        "best_central_net_return": max(central),
    }
    base["economics_computed"] = True
    base["primary"] = primary
    base["event_population_sha256"] = hashlib.sha256(
        json.dumps(events, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    if primary["mean_central_net_return"] <= 0:
        decision = "KILL_EXPRESSION"
        red_team = {"executed": False, "passed": False, "reason": "primary kill rule"}
    else:
        passes_primary = (
            primary["mean_signed_gross_return"] >= 0.0015
            and primary["mean_central_net_return"] >= 0.0005
            and primary["mean_stress_net_return"] > 0
            and primary["median_central_net_return"] > 0
            and primary["central_net_hit_rate"] >= 0.53
            and all(v is not None and v > 0 for v in by_signal.values())
            and primary["mean_central_net_through_2021"] is not None
            and primary["mean_central_net_through_2021"] > 0
            and primary["mean_central_net_from_2022"] is not None
            and primary["mean_central_net_from_2022"] > 0
        )
        if passes_primary:
            year_sums = {y: sum(xs) for y, xs in yearly.items()}
            remove_year = sorted(year_sums, key=lambda y: (-year_sums[y], y))[0]
            remaining = [e["central_net"] for e in events if e["final"][:4] != remove_year]
            remaining_mean = fmean(remaining)
            passed = remaining_mean is not None and remaining_mean > 0
            red_team = {
                "executed": True,
                "test": "remove calendar year with largest positive central-net sum",
                "removed_year": remove_year,
                "removed_year_central_net_sum": year_sums[remove_year],
                "remaining_events": len(remaining),
                "remaining_mean_central_net_return": remaining_mean,
                "passed": passed,
            }
            decision = "PROMOTE_EXPRESSION" if passed else "PARK_ECONOMICS"
        else:
            decision = "PARK_ECONOMICS"
            red_team = {"executed": False, "passed": False, "reason": "primary promotion hurdle not met"}

    base.update({
        "typed_verdict": decision,
        "decision": decision,
        "edge_validated": False,
        "red_team": red_team,
        "limits": {
            "daily_bars_are_fills": False,
            "borrow_financing_leg_risk_modelled": False,
            "actual_pension_flow_observed": False,
            "causal_identification": False,
            "capacity": "UNKNOWN",
            "alpha_validated": False,
            "closed_daily_etf_b2_b4_reopened": False,
        },
    })
    write_result(base)


if __name__ == "__main__":
    main()
