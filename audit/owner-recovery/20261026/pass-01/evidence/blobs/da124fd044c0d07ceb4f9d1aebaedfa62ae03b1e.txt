# QUANT — LANE PORTFOLIO DOCTRINE V1 — 2026-09-21

`STATUS = PROPOSED / NON_AUTHORIZING`

## 1. Breadth of mechanisms, not breadth of names

Established 2026-09-21: cross-sectional width is not sample size. 500 names at
mean residual pairwise `rho = 0.05` give effective breadth ~19.

Lanes are more independent than names, but they are **not** independent, and
the first draft's `IR_total = IR*sqrt(k)` was wrong. The correct form:

```text
IR_total = IR_lane * sqrt( k / (1 + (k-1)*rho) )
CEILING  = IR_lane / sqrt(rho)          as k -> infinity
```

At `IR_lane = 0.30`:

```text
rho     k=4    k=10   k=25   k=100   ceiling
0.05    0.56   0.79   1.01   1.23    1.34
0.10    0.53   0.69   0.81   0.91    0.95
0.20    0.47   0.57   0.62   0.66    0.67
0.30    0.44   0.49   0.52   0.54    0.55
```

Three consequences, all against the first draft:

1. `k=25` at `rho=0.2` gives **0.62, not 1.50** — a 2.4x overstatement.
2. There is a **hard ceiling**. No number of lanes beats `IR_lane/sqrt(rho)`.
   Reaching 1.5 from 0.30-lanes needs `rho < 0.04` across all of them.
3. Past `k ~ 10` the marginal lane buys almost nothing. Lane count is not a
   scaling strategy; lane *decorrelation* is.

A one-person-plus-agents shop realistically accesses a handful of genuinely
distinct mechanisms — cross-sectional equity, vol/carry, momentum,
microstructure/cost, perhaps one or two more. "25 lanes" would in practice be
25 parameterisations of 4-6 mechanisms, which this document's own `rho > 0.5`
rule collapses back to 4-6.

```text
k IS CAPPED at the count of mechanisms with pairwise rho < 0.3 measured against
REAL strategy returns, never at the count of lane labels.
```

### 1.1 The programme is alpha-bounded before it is idea-bounded

Under the multiplicity regime already adopted (`W0 = 0.025`,
bid `= min(W/2, 0.010)`, payout only on forward-confirmed rejection), a run of
failures exhausts the budget almost immediately:

```text
lane 1  bid 0.01000 -> W 0.01500
lane 2  bid 0.00750 -> W 0.00750
lane 3  bid 0.00375 -> W 0.00375
lane 4  bid 0.00188 -> W 0.00188
lane 5  bid 0.00094  BELOW USABLE POWER -> ADMISSION_CLOSED
```

**Four lanes, not twenty-five.** The doctrine and the multiplicity regime were
in direct contradiction and the multiplicity regime wins. Either the owner
re-capitalises alpha wealth explicitly, or the programme admits four lanes at a
time and must earn refills through forward-confirmed rejections.

## 2. Frequency is the only internal IR lever

```text
IR_ann = IC * sqrt(BR) ,  BR = N_eff * f   (rebalances per year)
```

With `IC = 0.03` and `N_eff = 19`: monthly `f=12` gives `IR = 0.45`;
reaching `IR = 1.5` at the same IC needs `BR ~ 2500`, i.e. `f ~ 130/yr`.

This assumed `IC` is invariant in `f`. It is not. Raising frequency shortens the
signal horizon, and IC typically *shrinks* with it — microstructure noise, and
the mean-reversion of the edge itself. `IR = IC*sqrt(N_eff*f)` therefore
overstates what is reachable at `f ~ 130/yr`.

Restated correctly:

```text
BINDING CONSTRAINT = IC decay and cost, jointly
IC(f) must be measured empirically before any f target is set
```

Execution quality alone is not the binding constraint. It is the half of the
constraint that is cheap to measure and cheap to improve, which is why it is
still the right place to start — but the claim has been narrowed.

## 3. Cost reduction is a lane with deterministic proof

A 10 bp saving per trade is measured, not inferred. It needs no `sqrt(T)`.

```text
COST_LANE  own budget, own owner, own metrics
           evidence horizon = days
           it raises the feasible f in §2, therefore raises IR in every lane
```

It is the only work in the system whose payoff is certain and immediate.

## 4. Small capital is an advantage, not a phase

Edges that do not scale are precisely the edges that are not arbitraged. At
small notional the system can harvest capacity-constrained niches that no fund
can touch. That advantage is structural and it **disappears on growth**.

Consequence: lanes should be screened *for* capacity constraint, not against
it. The earlier packet selected candidate lanes (cross-sectional ETF,
momentum/reversion, vol/regime) for data abundance — and abundance correlates
with crowding. That screen was backwards.

## 5. Point-in-time history is shared infrastructure

It is the only remaining honest accelerator of `T`. It is budgeted, acquired and
fingerprinted **once**, amortised across every future lane, and owned by the
Data Plane — never by a lane. A lane may cite it; no lane may fund or gate it.

## 6. Refused

More lanes without alpha accounting. Counting correlated lanes as independent,
or counting lane labels instead of measured-decorrelated mechanisms. Asserting
IC invariance in frequency.
Screening lanes by data convenience. Leverage as a substitute for IR.
