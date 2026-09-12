"""Run preregistered P0-E1 and write machine-readable and narrative outputs."""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from economic_value import evaluate, ewma_exposures  # noqa: E402

DATA = ROOT / "data" / "nasdaq_composite_daily.txt"
TRAIN = 750


def load_returns():
    with DATA.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    closes = [float(row["clot"]) for row in rows]
    dates = [row["date"].split()[0] for row in rows]
    logs = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
    simple = [closes[i] / closes[i - 1] - 1 for i in range(1, len(closes))]
    return dates[1:], logs, simple


def as_dict(perf):
    return {key: getattr(perf, key) for key in perf.__dataclass_fields__}


dates, logs, simple = load_returns()
oos = simple[TRAIN:]
base = [1.0] * len(oos)
primary_exp = ewma_exposures(logs, TRAIN)

result = {
    "experiment": "P0-E1",
    "data": {"rows": len(logs) + 1, "train_returns": TRAIN, "oos_returns": len(oos),
             "oos_start": dates[TRAIN], "oos_end": dates[-1]},
    "primary": {
        "cost_bps": 2,
        "benchmark": as_dict(evaluate(oos, base, 2)),
        "strategy": as_dict(evaluate(oos, primary_exp, 2)),
    },
    "cost_stress": {},
    "parameter_stress": {},
}
for cost in (0, 5, 10):
    result["cost_stress"][str(cost)] = as_dict(evaluate(oos, primary_exp, cost))
for lam, target in ((0.90, 0.20), (0.97, 0.20), (0.94, 0.12), (0.94, 0.18)):
    key = f"lambda={lam:.2f},target={target:.2f}"
    exp = ewma_exposures(logs, TRAIN, lam=lam, target_volatility=target)
    result["parameter_stress"][key] = as_dict(evaluate(oos, exp, 2))

mid = len(oos) // 2
result["split_half"] = {
    "first": as_dict(evaluate(oos[:mid], primary_exp[:mid], 2)),
    "second": as_dict(evaluate(oos[mid:], primary_exp[mid:], 2)),
}
net_daily = [e * r for e, r in zip(primary_exp, oos)]
order = sorted(range(len(net_daily)), key=net_daily.__getitem__)
keep = [i for i in range(len(oos)) if i not in set(order[:5] + order[-5:])]
result["trim_five_best_and_worst"] = as_dict(
    evaluate([oos[i] for i in keep], [primary_exp[i] for i in keep], 2)
)
result["exposure"] = {
    "minimum": min(primary_exp), "mean": sum(primary_exp) / len(primary_exp),
    "days_below_one": sum(x < 1 for x in primary_exp),
}
result["decision"] = (
    "VALIDATE_MORE" if result["primary"]["strategy"]["terminal_wealth"]
    > result["primary"]["benchmark"]["terminal_wealth"] else "KILL"
)

raw = ROOT / "results" / "phase0_e1.json"
raw.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

p = result["primary"]
report = f"""# Phase 0 — Forensic audit and first value-of-information experiment

## Repository reality

The initial checkout had two commits, one unproven five-year NASDAQ Composite
OHLC file, three source modules, two scripts, and two generated reports. It had
no tests, dependency lock file, data provenance, tradable instrument, dividend,
spread, financing, or execution data. The reference branch could not be fetched
through the environment proxy. Python sources compile, but the original reports
could not be regenerated because all five undeclared runtime dependencies were
absent and package download was blocked.

## Bottleneck and selected experiment

The central gap was economic: lower volatility-forecast loss had never been
connected to a causal, costed allocation decision. P0-E1 tests the cheapest such
connection. Full details and thresholds were committed before execution in
`research/EXPERIMENT_PROTOCOL.md`.

## Known

The file has 1,251 ordered rows and internally coherent OHLC values according
to the existing checks. The checked-in reports claim an OOS forecast-loss
advantage, but that is not presently reproducible here. The original forecast
recursion initializes from the full return vector and its EWMA helper recenters
that same full vector, so the nominal walk-forward path contains avoidable
future-sample information (small after burn-in, but disqualifying as clean
point-in-time evidence).

## Plausible but unproven

Volatility persistence and asymmetric equity-index responses are plausible. A
forecast may improve sizing, but the original project never showed that its
incremental accuracy increased net wealth.

## Unknown / decision-critical

The data vendor, extraction time, corrections, license, corporate-action and
total-return conventions are unknown. So are results on a directly tradable
vehicle, across multiple regimes, with financing and executable fills.

## Raw result

OOS: {result['data']['oos_start']} to {result['data']['oos_end']}, {len(oos)} returns.

| Rule (2 bp) | Terminal wealth | CAGR | Ann. vol | Max drawdown | Turnover |
|---|---:|---:|---:|---:|---:|
| Buy-and-hold | {p['benchmark']['terminal_wealth']:.4f} | {p['benchmark']['cagr']:.2%} | {p['benchmark']['annual_volatility']:.2%} | {p['benchmark']['max_drawdown']:.2%} | {p['benchmark']['turnover']:.2f} |
| EWMA target | {p['strategy']['terminal_wealth']:.4f} | {p['strategy']['cagr']:.2%} | {p['strategy']['annual_volatility']:.2%} | {p['strategy']['max_drawdown']:.2%} | {p['strategy']['turnover']:.2f} |

Exposure averaged {result['exposure']['mean']:.3f}, fell below one on
{result['exposure']['days_below_one']} days, and reached a minimum of
{result['exposure']['minimum']:.3f}. Costs of 0/5/10 bp produced terminal wealth
of {result['cost_stress']['0']['terminal_wealth']:.4f},
{result['cost_stress']['5']['terminal_wealth']:.4f}, and
{result['cost_stress']['10']['terminal_wealth']:.4f}.

## Adversarial tests

The split-half strategy wealth values were
{result['split_half']['first']['terminal_wealth']:.4f} and
{result['split_half']['second']['terminal_wealth']:.4f}. Removing its five best
and five worst days left {result['trim_five_best_and_worst']['terminal_wealth']:.4f}.
All preregistered parameter perturbations are preserved in the JSON output; none
is selected as a replacement model.

## Decision

**Researcher: {result['decision']}.** The primary terminal-wealth criterion
{'passed' if result['decision'] != 'KILL' else 'failed'}. Forecast accuracy is
not enough to justify this allocation. Even a pass could not establish a
tradable edge because the Composite is not directly tradable and the sample,
data provenance, dividends, financing, and actual fills are inadequate.

**Judge: {'NEEDS_MORE_EVIDENCE' if result['decision'] != 'KILL' else 'REJECT'}.**
The implementation is causal and discloses costs and variants, but this consumed
sample cannot validate a production claim. No parameter rescue is permitted.

## What we learned and next experiment

Known: volatility clusters and a transparent allocation can be evaluated
causally. Plausible but unproven: volatility forecasts may aid sizing on a
tradable total-return instrument. Decision-critical unknowns are performance on
provenance-preserving, point-in-time, multi-regime tradable data and realistic
implementation costs. **One next experiment:** acquire and checksum a
dividend-adjusted QQQ total-return series spanning at least 2000–2026, reserve a
new untouched terminal period, and preregister the same rule once—without model
selection—against costed QQQ buy-and-hold.
"""
(ROOT / "results" / "phase0_forensic_audit.md").write_text(report, encoding="utf-8")
print(json.dumps(result, indent=2, sort_keys=True))
