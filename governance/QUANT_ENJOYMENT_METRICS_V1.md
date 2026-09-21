# QUANT — TIME-TO-VALUE METRICS V1 — 2026-09-21

`STATUS = PROPOSED / NON_AUTHORIZING`

The project has no measure of how close it is to being useful, so nothing
optimises for it. Three goods, three clocks, three metrics.

## 1. Metrics

```text
M1 OPERATIONAL   consecutive_decision_days
                 days with a full Forward->...->BOOK->Learning cycle, no
                 restart/idempotency fault. Clock = weeks. Target: unbroken.

M2 EPISTEMIC     lanes_terminated_per_builder_week
                 admitted lanes reaching FALSIFIED or INSUFFICIENT per unit of
                 builder effort. Clock = controllable. This is the true lever.

M3 ECONOMIC      realised_net_pnl and IR_post (sizing doc §3)
                 Clock = IR*sqrt(T). Reported, never optimised directly.
```

M3 is a lagging report. Optimising it directly is how a research programme
starts fitting noise. M1 and M2 are the operating targets.

## 2. Marginal lane cost — the central number

```text
MARGINAL_LANE_COST = builder-days from proposal to terminal state
CURRENT  ~3 weeks (estimated: template, power test, harness, review)
TARGET   ~3 days
```

A 7x reduction multiplies programme speed 7x with no statistics moving at all.
That is the cheapest acceleration available anywhere in the system, and it is
pure engineering. Where it comes from:

```text
- admission power test as a script, not a document exercise
- universe/parameter files and digest produced by the harness
- one shared evaluation harness; lanes are configuration, not code
- termination is automatic at the pre-declared stopping rule
```

## 3. Instrumentation

Each metric must be emitted by the running system into the Status plane, not
computed by hand in a review. A metric that requires a human to assemble it
will not survive contact with a busy quarter.

## 4. Refused

Optimising M3. Counting a lane that was never admitted as "terminated".
Reporting M1 across a restart that lost state.
