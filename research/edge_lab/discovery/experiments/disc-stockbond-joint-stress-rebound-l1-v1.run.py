from __future__ import annotations

import csv
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

EXPERIMENT_ID = "disc-stockbond-joint-stress-rebound-l1-v1"
INVOCATION_ID = "owner-manual-20261012-a1"
PREDECLARATION_COMMIT = "6c6797b608fb702032b38f44691c8042d86f74e0"
CLAIM_COMMIT = "56506050acaca7212e3c684bfb367a67804b8b3e"
DATA = Path("data/datasets/us_sector_etf_daily.csv")
META = Path("data/datasets/us_sector_etf_daily.meta.json")
RESULT = Path(__file__).with_name("disc-stockbond-joint-stress-rebound-l1-v1.result.json")
EXPECTED_FINGERPRINT = "sha256:f108a6f41552afdb42100d3188d7194006de1aae6a27bd7722330818e6dcb6d1"
SYMBOLS = ["SPY", "TLT"]
SPY_THRESHOLD = -0.0100
TLT_THRESHOLD = -0.0050
CENTRAL_COST = 0.0008
STRESS_COST = 0.0015


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
        "claim_ceiling": "PROMOTE_EXPRESSION",
        "real_capital_authorized": False,
        "live_trading_authorized": False,
        "paid_usd": 0,
        "frozen": {
            "dataset": str(DATA),
            "expected_fingerprint": EXPECTED_FINGERPRINT,
            "symbols": SYMBOLS,
            "spy_close_to_close_threshold": SPY_THRESHOLD,
            "tlt_close_to_close_threshold": TLT_THRESHOLD,
            "payoff": "next aligned session equal-weight SPY/TLT open-to-close",
            "central_roundtrip_cost": CENTRAL_COST,
            "stress_roundtrip_cost": STRESS_COST,
        },
    }

    if not DATA.exists() or not META.exists():
        park_data(base, "Frozen committed dataset or metadata file missing.")

    meta = json.loads(META.read_text(encoding="utf-8"))
    if meta.get("fingerprint") != EXPECTED_FINGERPRINT:
        park_data(base, "Frozen metadata fingerprint mismatch.", {
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
            park_data(base, "Required exact CSV columns absent; aliases forbidden.", {
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
        park_data(base, "SPY/TLT panels not exactly aligned; post-claim repair forbidden.", {
            "rows_by_symbol": {s: len(rows[s]) for s in SYMBOLS}, "common_dates": len(common)
        })
    dates = sorted(common)
    if len(dates) < 3:
        park_data(base, "Aligned panel too short.")

    # Fail-closed contamination check before event or payoff computation.
    cc = {s: {} for s in SYMBOLS}
    max_abs = 0.0
    max_where = None
    for i in range(1, len(dates)):
        d, p = dates[i], dates[i - 1]
        for s in SYMBOLS:
            r = rows[s][d]["close"] / rows[s][p]["close"] - 1.0
            cc[s][d] = r
            if abs(r) > max_abs:
                max_abs = abs(r)
                max_where = {"symbol": s, "date": d, "raw_close_to_close_return": r}
    base["schema_checks"] = {
        "aligned_sessions": len(dates),
        "first_date": dates[0],
        "last_date": dates[-1],
        "max_abs_raw_close_to_close_return": max_abs,
        "max_abs_raw_close_to_close_where": max_where,
    }
    if max_abs > 0.25:
        park_data(base, "Predeclared >25% raw close-to-close contamination guard fired before payoff computation.", max_where)

    qualifying = []
    for i in range(1, len(dates) - 1):
        d = dates[i]
        if cc["SPY"][d] <= SPY_THRESHOLD and cc["TLT"][d] <= TLT_THRESHOLD:
            qualifying.append({
                "signal_date": d,
                "next_date": dates[i + 1],
                "spy_close_to_close": cc["SPY"][d],
                "tlt_close_to_close": cc["TLT"][d],
            })

    observed = []
    for e in qualifying:
        nd = e["next_date"]
        spy = rows["SPY"].get(nd)
        tlt = rows["TLT"].get(nd)
        if not spy or not tlt:
            continue
        spy_oc = spy["close"] / spy["open"] - 1.0
        tlt_oc = tlt["close"] / tlt["open"] - 1.0
        gross = 0.5 * spy_oc + 0.5 * tlt_oc
        observed.append({
            **e,
            "spy_next_open_to_close": spy_oc,
            "tlt_next_open_to_close": tlt_oc,
            "gross": gross,
            "central_net": gross - CENTRAL_COST,
            "stress_net": gross - STRESS_COST,
        })

    block1_count = sum(1 for e in qualifying if e["signal_date"] <= "2021-12-31")
    block2_count = sum(1 for e in qualifying if e["signal_date"] >= "2022-01-01")
    coverage = len(observed) / len(qualifying) if qualifying else 0.0
    base["adequacy"] = {
        "qualifying_events": len(qualifying),
        "observed_events": len(observed),
        "through_2021_events": block1_count,
        "from_2022_events": block2_count,
        "endpoint_coverage": coverage,
        "requires_total_at_least": 20,
        "requires_each_block_at_least": 5,
        "requires_endpoint_coverage": 1.0,
    }
    if not (len(qualifying) >= 20 and block1_count >= 5 and block2_count >= 5 and coverage == 1.0):
        park_data(base, "Frozen adequacy gate failed; no threshold/sample/instrument/cost change allowed.", base["adequacy"])

    gross = [e["gross"] for e in observed]
    central = [e["central_net"] for e in observed]
    stress = [e["stress_net"] for e in observed]
    block1 = [e["central_net"] for e in observed if e["signal_date"] <= "2021-12-31"]
    block2 = [e["central_net"] for e in observed if e["signal_date"] >= "2022-01-01"]
    yearly = defaultdict(list)
    for e in observed:
        yearly[e["signal_date"][:4]].append(e["central_net"])

    primary = {
        "mean_gross_return": fmean(gross),
        "mean_central_net_return": fmean(central),
        "mean_stress_net_return": fmean(stress),
        "median_central_net_return": median(central),
        "central_net_hit_rate": sum(1 for x in central if x > 0) / len(central),
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
        json.dumps(observed, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    if primary["mean_central_net_return"] <= 0:
        decision = "KILL_EXPRESSION"
        red_team = {"executed": False, "passed": False, "reason": "primary kill rule"}
    else:
        passes_primary = (
            primary["mean_gross_return"] >= 0.0020
            and primary["mean_central_net_return"] >= 0.0010
            and primary["mean_stress_net_return"] > 0
            and primary["median_central_net_return"] > 0
            and primary["central_net_hit_rate"] >= 0.55
            and primary["mean_central_net_through_2021"] is not None
            and primary["mean_central_net_through_2021"] > 0
            and primary["mean_central_net_from_2022"] is not None
            and primary["mean_central_net_from_2022"] > 0
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
            "leverage_financing_modelled": False,
            "forced_flow_observed": False,
            "causal_identification": False,
            "capacity": "UNKNOWN",
            "alpha_validated": False,
            "closed_daily_etf_b2_b4_reopened": False,
        },
    })
    write_result(base)


if __name__ == "__main__":
    main()
