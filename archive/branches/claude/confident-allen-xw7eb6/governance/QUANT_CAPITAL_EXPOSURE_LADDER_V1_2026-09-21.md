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
any further promotion of the affected sleeve.

```text
kill-switch fired                      -> immediate halt + SHADOW
daily-loss cap breached                -> halt for session, review required
realized frictions outside envelope    -> falsified on frictions -> SHADOW
decay guard tripped on the lineage     -> one stage down
authorization artifact expired         -> one stage down
restart/idempotency invariant violated -> HALT ALL SLEEVES; no sleeve may
                                          promote until the invariant is
                                          re-proven
```

The last line is a halt, not a stage write. An earlier draft read "whole desk to
`PAPER`", which contradicted §1 (the unit that occupies a stage is a sleeve,
never the system) and would have performed a state mutation during exactly the
condition in which state mutation is untrustworthy.

Demotion is itself a Book mutation and carries its own deterministic
`operation_id`, so a demotion written during a failed replay is not applied
twice. A demotion is latched, never recomputed from current state.

Each trigger above presumes a detector that does not exist yet. The prerequisite
detector is a post-session invariant recompute (cash plus marked positions
against NAV, `applied_operations` cardinality) raising a persistent fault.
Without it these lines are intentions, not controls.

**Operative safety today:** a sleeve with no live decay monitor may not hold a
stage above `PAPER`. No decay monitor exists. `LIVE_CANARY` is therefore
currently unreachable regardless of any evidence, and that is the intended
state.

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

**Enforcing surface.** `clock.py::tick()` has no authorization scan and
`ControlState` holds no authorization list, so nothing in the runtime can fire
"authorization expired". Until that surface exists, expiry is **owner-manual**
and this document says so rather than implying a control. Any expiring artifact
added later must name the surface that enforces it.

## 6. Implementation note

None of this exists in `src/` yet, and this document deliberately does not add
a lifecycle enum. When it is implemented, the ordering is: expected-vs-realized
fill reconciliation and kill-switch first, stage enum last. A stage enum added
before the mechanisms would assert a capability the system does not have.
