# BLUE — ROADMAP: FIRST FAST ECONOMIC LANE — 2026-09-21

`STATUS = PREPARED / NON_AUTHORIZING`
`CONCURRENCY_CAP_RESPECTED = TRUE (no third workstream started)`

Product objective after Rail A and Rail B close:
**find the first strategy for which Quant can accumulate clean, falsifiable
evidence within months, while `FORM4_CONFIRMATORY_V1` runs untouched for years.**

## Phase 0 — NOW (no change to current allocation)

Rail A and Rail B remain the only active substantial workstreams.

```text
RAIL A  close ACTIVATION_SEAL_PREP -> Gate B -> t0
RAIL B  independent review of the vertical shadow loop -> integrate
THIS    packet sits prepared; nothing starts
```

Forbidden in this phase: admitting a lane, collecting outcomes under an
unfilled pre-registration, touching Form-4 parameters, any real exposure.

## Phase 1 — Production-as-shadow

Gate: `t0 DECLARED` **and** `RAIL_B_VERTICAL_INTEGRATED`, whichever is later.

```text
Quant runs continuously in paper/shadow
Forward -> Research -> Economic -> SIZE -> RISK -> simulated FILLS -> BOOK -> Learning
restart-safe, idempotent, one causal timeline
```

Exit criteria: a continuous window with no restart/idempotency violation, no
information-timeline violation, and a populated Book with per-sleeve
attribution.

## Phase 2 — Admit FAST_VERTICAL_V1

Gate: Phase 1 exit criteria met.

```text
1  fill the pre-registration template in full
2  complete the power derivation (§6) — this is the admission test
3  draw the alpha share from the family-wise budget
4  record the digest and date in the lineage registry
5  begin accrual; no unscheduled looks
```

If the power derivation does not show a materially shorter time to decision
than Form-4, the candidate is rejected and another is proposed. Rejection at
this step is cheap and is the intended filter.

## Phase 3 — Execution-realism instrument

Runs in parallel with Phase 2 accrual, and depends on no research outcome.

```text
build  kill-switch · daily-loss cap · position and notional caps
build  expected-vs-realized fill reconciliation, recorded per order
build  decay monitor per sleeve
then   a LIVE_CANARY becomes technically possible
```

Until all four exist, `LIVE_CANARY` is unreachable regardless of evidence.

## Phase 4 — Exposure, only on independent proof

```text
lineage QUALIFIED under its own stopping rule
  -> forward confirmation window
  -> owner authorization artifact (dated, expiring)
  -> LIVE_CANARY  (frictions measured, edge NOT claimed)
  -> realized frictions inside assumed envelope?
       no  -> falsified on frictions, back to SHADOW
       yes -> fresh authorization -> SMALL_CAPITAL
  -> SCALE only on capacity evidence, per increment
```

## Honest timeline

```text
weeks        Rail A + Rail B closed; Quant running 24/7 in shadow
weeks        FAST_VERTICAL_V1 candidate proposed and power-tested
1-3 months   first lanes FALSIFIED or INSUFFICIENT — the expected outcome
6-18 months  plausible window for a first QUALIFIED fast lane, not guaranteed
years        FORM4_CONFIRMATORY_V1 continues untouched in the background
```

The `1-3 months` figure is a falsification horizon, not a qualification
horizon. A quarter that kills three lanes cheaply is a successful quarter.

## Invariants this roadmap must never break

1. Form-4 parameters are frozen; schedule pressure is never a reason to relax.
2. Evidence never transfers between lineages.
3. A state name is never a capability claim.
4. No real capital without a dated, expiring owner authorization.
5. Demotion always precedes any further promotion.

## Owner decisions still open

See §5 of `governance/BLUE_THREE_TIER_PRODUCTIZATION_CHALLENGE_2026-09-21.md`.
