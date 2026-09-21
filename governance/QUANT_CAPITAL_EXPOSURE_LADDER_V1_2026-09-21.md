# QUANT CAPITAL EXPOSURE LADDER V1 — 2026-09-21

`STATUS = PREPARED / NON_AUTHORIZING`
`REAL_CAPITAL_AUTHORITY = NOT_GRANTED`

This document defines the only admissible path from simulated decisions to real
exposure. It is a governance contract, not an implemented capability. No stage
past `PAPER` may be entered while this line reads `NOT_GRANTED`.

## 1. Stages

```text
SHADOW        decisions produced, no book impact claimed beyond observation
PAPER         full simulated book: SIZE, RISK, simulated FILLS, BOOK, Learning
LIVE_CANARY   minimal real exposure, execution-realism instrument only
SMALL_CAPITAL first stage where P&L is an economic objective
SCALE         capacity-bounded increase
```

The unit that occupies a stage is a **strategy sleeve**, never the system.
Different sleeves may sit at different stages simultaneously. Portfolio state
aggregates across sleeves; attribution stays per sleeve.

## 2. Entry requirements

### SHADOW
- Causal single-timeline information discipline.
- Pre-registration entry present in the lineage registry.

### PAPER
- Executable strategy object identical to the researched object.
- Frictions applied: fees, spread, slippage, financing, borrow, capacity.
- Restart-safe idempotent book mutation demonstrated by adversarial test.
- Risk approval describes the final post-transform/post-scale portfolio.

### LIVE_CANARY
- All PAPER requirements, continuously green.
- Strategy-independent proof of edge from its own lineage, qualified under its
  own pre-registered stopping rule. Evidence from another sleeve does not carry.
- Implemented and tested: kill-switch, daily-loss cap, position-count cap,
  per-order notional cap, zero leverage, no shorting unless the lineage
  pre-registered shorting.
- Expected-vs-realized fill reconciliation implemented and recorded per order.
- Dated owner authorization artifact.

### SMALL_CAPITAL
- `LIVE_CANARY` completed with realized frictions inside the envelope the
  research assumed. If realized cost exceeds the assumed envelope, the sleeve
  is falsified on frictions and returns to research, not to a larger size.
- Fresh dated owner authorization artifact.

### SCALE
- Capacity model validated against realized participation and market impact.
- Each increment requires additional evidence and its own authorization.

## 3. What LIVE_CANARY may and may not establish

May establish (falsifying power):
`fills · partials · rejects · latency · slippage vs expected · borrow · financing · fees · operational failure`

May never establish:
`edge · Sharpe · hit rate · expected return`

A canary P&L series is underpowered by construction. Citing it as evidence of
edge is a protocol violation.

## 4. Demotion

Demotion is automatic, requires no authorization, and always executes before
any further promotion anywhere in the system.

```text
kill-switch fired                      -> immediate halt + SHADOW
daily-loss cap breached                -> halt for session, review required
realized frictions outside envelope    -> falsified on frictions -> SHADOW
decay guard tripped on the lineage     -> one stage down
restart/idempotency invariant violated -> whole desk to PAPER
authorization artifact expired         -> one stage down
```

Absence of evidence of decay is not evidence of persistence. A sleeve with no
live decay monitor may not hold a stage above `PAPER`.

## 5. Authorization artifact

Required fields for any promotion past `PAPER`:

```text
sleeve_id · lineage_id · stage_from · stage_to · date
max_notional · max_positions · max_daily_loss · leverage=0
evidence_refs (lineage qualification digest, CI run, book invariants run)
expiry_date
owner_signature
```

Expiry is mandatory. An authorization without expiry is invalid.

## 6. Implementation note

None of this exists in `src/` yet, and this document deliberately does not add
a lifecycle enum. When it is implemented, the ordering is: expected-vs-realized
fill reconciliation and kill-switch first, stage enum last. A stage enum added
before the mechanisms would assert a capability the system does not have.
