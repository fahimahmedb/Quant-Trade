# Phase 0 — Forensic audit and first value-of-information experiment

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

OOS: 11/07/2024 to 10/07/2026, 500 returns.

| Rule (2 bp) | Terminal wealth | CAGR | Ann. vol | Max drawdown | Turnover |
|---|---:|---:|---:|---:|---:|
| Buy-and-hold | 1.4091 | 18.87% | 22.20% | -24.32% | 1.00 |
| EWMA target | 1.2810 | 13.29% | 18.65% | -20.38% | 6.01 |

Exposure averaged 0.919, fell below one on
193 days, and reached a minimum of
0.338. Costs of 0/5/10 bp produced terminal wealth
of 1.2826,
1.2787, and
1.2748.

## Adversarial tests

The split-half strategy wealth values were
1.0211 and
1.2542. Removing its five best
and five worst days left 1.3099.
All preregistered parameter perturbations are preserved in the JSON output; none
is selected as a replacement model.

## Decision

**Researcher: KILL.** The primary terminal-wealth criterion
failed. Forecast accuracy is
not enough to justify this allocation. Even a pass could not establish a
tradable edge because the Composite is not directly tradable and the sample,
data provenance, dividends, financing, and actual fills are inadequate.

**Judge: REJECT.**
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
