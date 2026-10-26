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

Gate: `RAIL_B_VERTICAL_INTEGRATED` **alone** (decided 2026-09-21).

Phase 1 exercises `clock.py`, `desk/` and `book/` only. Rail A's t0 qualifies
Form-4 *capture*, and gating runtime continuity on a currently blocked data item
would park weeks of evidence behind it. Worse, the continuity evidence is
exactly what should exist *before* t0 declares a capture cursor that must not be
replayed twice. Form-4 accrual stays gated on `t0 DECLARED`; only Phase 1 is
decoupled.

```text
Quant runs continuously in paper/shadow
Forward -> Research -> Economic -> SIZE -> RISK -> simulated FILLS -> BOOK -> Learning
restart-safe, idempotent, one causal timeline
```

Exit criteria: a continuous window with no restart/idempotency violation, no
information-timeline violation, and a populated Book with per-sleeve
attribution.

## Phase 2 — Admit FAST_VERTICAL_V1

Gate: Phase 1 exit criteria met **and** `t0 DECLARED` (the later-of gate is
retained here, where it belongs: admitting a competing lineage while Form-4
accrual has not started would put the two lineages in schedule conflict).

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

`SIZE = 6-10 BUILDER_WEEKS + INDEPENDENT_REVIEW`
`CLASSIFICATION = QUARTER_SCALE_WORKSTREAM, NOT A PARALLEL SIDE-QUEST`
`OWNER = UNASSIGNED`

An earlier draft priced this as one bullet of four and ran it in parallel with
Phase 2. Both were wrong: that would be a third workstream under a cap of two,
and the sizing was off by an order of magnitude.

```text
kill-switch + latched caps          ~3-5 days   (restart-safe latch + replay test)
post-session invariant recompute    ~3-5 days   (prerequisite for all demotion)
ORDER_INTENT_RECORD                 ~3-5 days   (implementable now, useful in paper)
REALIZED_FILL_INGEST + reconcile    ~2-4 weeks  (needs a broker adapter: none exists)
per-sleeve decay monitor            ~2-3 weeks  (mostly research-integrity design)
```

`desk/execution.py` currently produces a single object that is simultaneously
the expectation and the booked realization, and `journal.begin()` persists that
same list as intent. There is nothing to reconcile against — the residual is
identically zero by construction. So the requirement splits:

```text
ORDER_INTENT_RECORD   distinct from fill: reference price, expected slippage
                      envelope, expected cost. Buildable now against execution.py.
REALIZED_FILL_INGEST  broker adapter, partials, rejects, latency, tolerance
                      policy tied to the lineage friction envelope. Out of scope
                      until Phase 3 has a named owner.
```

Phase 3 starts only when a rail frees capacity. Until all of the above exist,
`LIVE_CANARY` is unreachable regardless of evidence.

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
weeks        Rail B integrated; Quant running 24/7 in shadow (does not wait on t0)
weeks        FAST_VERTICAL_V1 candidate proposed and power-tested
1-3 months   most candidates rejected AT ADMISSION on the power test alone —
             the cheapest possible kill, and the expected outcome
quarter      Phase 3 execution-realism build, once a rail frees capacity
12-24 months plausible window for a first QUALIFIED fast lane, and only if it
             draws power from pre-registered point-in-time history
years        FORM4_CONFIRMATORY_V1 continues untouched in the background
```

The `1-3 months` figure is a falsification horizon, not a qualification
horizon. A quarter that kills three lanes cheaply is a successful quarter.

The window widened from `6-18` to `12-24 months` because the corrected power law
(registry §6) removes the speed the original plan expected from a wide
cross-section. A forward-only fast lane needs net `IR >= ~1.5` to decide in
~4 years, which is not a credible ask in crowded space. Point-in-time depth is
now the only honest accelerator, and acquiring it is itself work.

## Invariants this roadmap must never break

1. Form-4 parameters are frozen; schedule pressure is never a reason to relax.
2. Evidence never transfers between lineages.
3. A state name is never a capability claim.
4. No real capital without a dated, expiring owner authorization.
5. Demotion always precedes any further promotion.

## Decisions taken

All three formerly open decisions were resolved on 2026-09-21 after adversarial
review. See `governance/BLUE_THREE_TIER_ADVERSARIAL_REVIEW_DECISIONS_2026-09-21.md`.
