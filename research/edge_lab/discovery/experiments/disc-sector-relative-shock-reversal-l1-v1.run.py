from __future__ import annotations

import csv
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

EXPERIMENT_ID = "disc-sector-relative-shock-reversal-l1-v1"
INVOCATION_ID = "owner-manual-20261012-a1"
PREDECLARATION_COMMIT = "d959e32bedb2871f963c666743d391f1c7d76d89"
CLAIM_COMMIT = "f632ad20295283384d73d125929738ff6c7b9f18"
DATA = Path("data/datasets/us_sector_etf_daily.csv")
META = Path("data/datasets/us_sector_etf_daily.meta.json")
RESULT = Path(__file__).with_name("disc-sector-relative-shock-reversal-l1-v1.result.json")
EXPECTED_FINGERPRINT = "sha256:f108a6f41552afdb42100d3188d7194006de1aae6a27bd7722330818e6dcb6d1"
SECTORS = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
POS_THRESHOLD = 0.0200
NEG_THRESHOLD = -0.0200
CENTRAL_COST = 0.0008
STRESS_COST = 0.0015
BLOCK1_END = "2021-12-31"
BLOCK2_START = "2022-01-01"


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
        "real_capital_authorized": False,
        "live_trading_authorized": False,
        "paid_usd": 0,
        "claim_ceiling": "PROMOTE_EXPRESSION",
        "frozen": {
            "dataset": str(DATA),
            "expected_fingerprint": EXPECTED_FINGERPRINT,
            "sectors": SECTORS,
            "positive_residual_threshold": POS_THRESHOLD,
            "negative_residual_threshold": NEG_THRESHOLD,
            "central_roundtrip_cost": CENTRAL_COST,
            "stress_roundtrip_cost": STRESS_COST,
            "payoff": "next aligned session open-to-close",
        },
    }

    if not DATA.exists() or not META.exists():
        park_data(base, "Frozen committed dataset or metadata file is missing.")

    meta = json.loads(META.read_text(encoding="utf-8"))
    meta_fingerprint = meta.get("fingerprint")
    if meta_fingerprint != EXPECTED_FINGERPRINT:
        park_data(base, "Frozen dataset metadata fingerprint does not match the predeclared fingerprint.", {
            "observed_meta_fingerprint": meta_fingerprint,
            "expected_meta_fingerprint": EXPECTED_FINGERPRINT,
        })

    raw_sha256 = hashlib.sha256(DATA.read_bytes()).hexdigest()
    base["dataset_proof"] = {
        "meta_fingerprint": meta_fingerprint,
        "raw_csv_sha256_observed": "sha256:" + raw_sha256,
        "meta_rows": meta.get("rows"),
        "meta_first_date": meta.get("first_date"),
        "meta_last_date": meta.get("last_date"),
    }

    rows_by_symbol = {s: {} for s in SECTORS}
    with DATA.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        required = {"date", "symbol", "open", "close"}
        if not required.issubset(fields):
            park_data(base, "Required exact CSV columns are absent; aliases are forbidden after claim.", {
                "required_columns": sorted(required),
                "observed_columns": fields,
            })
        for row in reader:
            symbol = row["symbol"]
            if symbol not in rows_by_symbol:
                continue
            date = row["date"]
            if date in rows_by_symbol[symbol]:
                park_data(base, "Duplicate symbol/date row in frozen dataset.", {"symbol": symbol, "date": date})
            try:
                o = float(row["open"])
                c = float(row["close"])
            except Exception as e:
                park_data(base, "Non-numeric required price field in frozen dataset.", {
                    "symbol": symbol, "date": date, "error": f"{type(e).__name__}: {e}"
                })
            if not (o > 0 and c > 0):
                park_data(base, "Non-positive required raw price in frozen dataset.", {"symbol": symbol, "date": date})
            rows_by_symbol[symbol][date] = {"open": o, "close": c}

    date_sets = {s: set(rows_by_symbol[s]) for s in SECTORS}
    if any(not date_sets[s] for s in SECTORS):
        park_data(base, "At least one required sector has no rows.", {
            "rows_by_symbol": {s: len(rows_by_symbol[s]) for s in SECTORS}
        })
    common_dates = set.intersection(*(date_sets[s] for s in SECTORS))
    if any(date_sets[s] != common_dates for s in SECTORS):
        park_data(base, "Nine-sector panel is not exactly aligned; post-claim alignment repair is forbidden.", {
            "rows_by_symbol": {s: len(rows_by_symbol[s]) for s in SECTORS},
            "common_dates": len(common_dates),
        })
    dates = sorted(common_dates)
    if len(dates) < 2:
        park_data(base, "Aligned sector panel has fewer than two sessions.")

    # Fail-closed corporate-action/split contamination guard is evaluated before any payoff.
    max_abs_raw_cc = 0.0
    max_abs_raw_cc_where = None
    daily_sector_returns = {}
    for idx in range(1, len(dates)):
        d = dates[idx]
        prev = dates[idx - 1]
        day = {}
        for s in SECTORS:
            r = rows_by_symbol[s][d]["close"] / rows_by_symbol[s][prev]["close"] - 1.0
            day[s] = r
            if abs(r) > max_abs_raw_cc:
                max_abs_raw_cc = abs(r)
                max_abs_raw_cc_where = {"symbol": s, "date": d, "raw_close_to_close_return": r}
        daily_sector_returns[d] = day
    base["schema_checks"] = {
        "aligned_sessions": len(dates),
        "first_date": dates[0],
        "last_date": dates[-1],
        "rows_by_symbol": {s: len(rows_by_symbol[s]) for s in SECTORS},
        "max_abs_raw_sector_close_to_close_return": max_abs_raw_cc,
        "max_abs_raw_sector_close_to_close_where": max_abs_raw_cc_where,
    }
    if max_abs_raw_cc > 0.25:
        park_data(base, "Predeclared >25% raw sector close-to-close contamination guard fired; no economic payoff was computed.", max_abs_raw_cc_where)

    # Build frozen qualifying events from close-known information only.
    qualifying = []
    for idx in range(1, len(dates) - 1):
        d = dates[idx]
        next_d = dates[idx + 1]
        day = daily_sector_returns[d]
        med = median(list(day.values()))
        residuals = {s: day[s] - med for s in SECTORS}
        max_s = max(SECTORS, key=lambda s: (residuals[s], s))
        min_s = min(SECTORS, key=lambda s: (residuals[s], s))
        if residuals[max_s] >= POS_THRESHOLD:
            qualifying.append({
                "signal_date": d,
                "next_date": next_d,
                "symbol": max_s,
                "side": "POSITIVE_SHOCK",
                "residual": residuals[max_s],
                "signal": -1,
            })
        if residuals[min_s] <= NEG_THRESHOLD:
            qualifying.append({
                "signal_date": d,
                "next_date": next_d,
                "symbol": min_s,
                "side": "NEGATIVE_SHOCK",
                "residual": residuals[min_s],
                "signal": 1,
            })

    observed = []
    missing_endpoints = []
    for e in qualifying:
        row = rows_by_symbol[e["symbol"]].get(e["next_date"])
        if not row or not (row["open"] > 0 and row["close"] > 0):
            missing_endpoints.append({"symbol": e["symbol"], "signal_date": e["signal_date"], "next_date": e["next_date"]})
            continue
        gross = e["signal"] * (row["close"] / row["open"] - 1.0)
        observed.append({
            **e,
            "gross": gross,
            "central_net": gross - CENTRAL_COST,
            "stress_net": gross - STRESS_COST,
        })

    side_counts = {
        side: sum(1 for e in qualifying if e["side"] == side)
        for side in ("POSITIVE_SHOCK", "NEGATIVE_SHOCK")
    }
    coverage = len(observed) / len(qualifying) if qualifying else 0.0
    base["adequacy"] = {
        "qualifying_events": len(qualifying),
        "qualifying_by_side": side_counts,
        "observed_events": len(observed),
        "missing_endpoints": len(missing_endpoints),
        "coverage": coverage,
        "requires_total_at_least": 80,
        "requires_each_side_at_least": 25,
        "requires_coverage_at_least": 0.90,
    }
    adequate = (
        len(qualifying) >= 80
        and side_counts["POSITIVE_SHOCK"] >= 25
        and side_counts["NEGATIVE_SHOCK"] >= 25
        and coverage >= 0.90
    )
    if not adequate:
        park_data(base, "Frozen adequacy gate failed; no threshold/window/cost/universe change is allowed.", base["adequacy"])

    gross = [e["gross"] for e in observed]
    central = [e["central_net"] for e in observed]
    stress = [e["stress_net"] for e in observed]
    by_side_central = {
        side: fmean([e["central_net"] for e in observed if e["side"] == side])
        for side in ("POSITIVE_SHOCK", "NEGATIVE_SHOCK")
    }
    block1 = [e["central_net"] for e in observed if e["signal_date"] <= BLOCK1_END]
    block2 = [e["central_net"] for e in observed if e["signal_date"] >= BLOCK2_START]
    by_symbol = {
        s: {
            "events": sum(1 for e in observed if e["symbol"] == s),
            "mean_central_net": fmean([e["central_net"] for e in observed if e["symbol"] == s]),
        }
        for s in SECTORS
    }
    yearly = defaultdict(list)
    for e in observed:
        yearly[e["signal_date"][:4]].append(e["central_net"])

    primary = {
        "mean_signed_gross_return": fmean(gross),
        "mean_central_net_return": fmean(central),
        "mean_stress_net_return": fmean(stress),
        "median_central_net_return": median(central),
        "central_net_hit_rate": sum(1 for x in central if x > 0) / len(central),
        "mean_central_net_by_side": by_side_central,
        "mean_central_net_2016_09_12_to_2021_12_31": fmean(block1),
        "mean_central_net_2022_01_01_to_2026_09_11": fmean(block2),
        "block_event_counts": {"first": len(block1), "second": len(block2)},
        "by_symbol": by_symbol,
        "yearly": {
            y: {"events": len(xs), "mean_central_net": fmean(xs), "sum_central_net": sum(xs)}
            for y, xs in sorted(yearly.items())
        },
        "worst_central_net_return": min(central),
        "best_central_net_return": max(central),
    }
    base["economics_computed"] = True
    base["primary"] = primary

    # Hash the full event/payoff population so the compact result remains auditable without bloating the repo.
    event_bytes = json.dumps(observed, sort_keys=True, separators=(",", ":")).encode("utf-8")
    base["event_population_sha256"] = hashlib.sha256(event_bytes).hexdigest()

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
            and all(v is not None and v > 0 for v in by_side_central.values())
            and primary["mean_central_net_2016_09_12_to_2021_12_31"] is not None
            and primary["mean_central_net_2016_09_12_to_2021_12_31"] > 0
            and primary["mean_central_net_2022_01_01_to_2026_09_11"] is not None
            and primary["mean_central_net_2022_01_01_to_2026_09_11"] > 0
        )
        if passes_primary:
            year_sums = {y: sum(xs) for y, xs in yearly.items()}
            remove_year = sorted(year_sums, key=lambda y: (-year_sums[y], y))[0]
            remaining = [e["central_net"] for e in observed if e["signal_date"][:4] != remove_year]
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
            "short_borrow_locate_modelled": False,
            "causal_identification": False,
            "capacity": "UNKNOWN",
            "alpha_validated": False,
            "closed_daily_etf_b2_b4_reopened": False,
        },
    })
    write_result(base)


if __name__ == "__main__":
    main()
