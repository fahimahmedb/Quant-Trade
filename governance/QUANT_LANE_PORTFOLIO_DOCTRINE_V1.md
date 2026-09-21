# QUANT — LANE PORTFOLIO DOCTRINE V1 — 2026-09-21

`STATUS = PROPOSED / NON_AUTHORIZING`

## 1. Breadth of mechanisms, not breadth of names

Established 2026-09-21: cross-sectional width is not sample size. 500 names at
mean residual pairwise `rho = 0.05` give effective breadth ~19.

Lanes are different. Distinct economic mechanisms are independent in a way that
two names in one index never are.

```text
k lanes at IR = 0.30, approximately independent  ->  IR_total = 0.30*sqrt(k)
k = 4   -> 0.60        k = 25  -> 1.50
```

A single lane at `IR >= 1.5` is not a credible target. Twenty-five weak,
cheap, genuinely distinct lanes are. This inverts the factory's objective:

```text
OLD  find the strategy
NEW  minimise the marginal cost of proposing, testing and killing a lane
```

Independence is asserted, not assumed: lane pairs whose realized shadow returns
correlate `> 0.5` count as one lane for this arithmetic.

## 2. Frequency is the only internal IR lever

```text
IR_ann = IC * sqrt(BR) ,  BR = N_eff * f   (rebalances per year)
```

With `IC = 0.03` and `N_eff = 19`: monthly `f=12` gives `IR = 0.45`;
reaching `IR = 1.5` at the same IC needs `BR ~ 2500`, i.e. `f ~ 130/yr`.

Frequency is bounded by cost. **Therefore execution quality is the binding
constraint on economic speed**, not research throughput. This is the load-
bearing conclusion of the whole programme.

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

More lanes without alpha accounting. Counting correlated lanes as independent.
Screening lanes by data convenience. Leverage as a substitute for IR.
