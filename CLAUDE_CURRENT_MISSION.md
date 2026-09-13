# Claude Current Mission - PR #12 Corrective Integrity Pass

This mission is a corrective engineering pass on draft PR #12. Preserve the useful Quant System V1 implementation. Do not start Phase 2 until these invariants are repaired and re-audited.

## Goal

Make V1 truthful and restart-safe in paper/shadow mode.

## Required corrections

### 1. One causal market timeline

Use one timeline everywhere:

`information through close(t) -> decision after close(t) -> earliest simulated fill open(t+1) -> mark t+1 or later`

Research must not receive a return interval that starts before the simulated order can execute. Desk marking must never move backward in time after a later-dated fill.

Add an adversarial overnight-gap regression test. Recompute published research metrics after the correction and update `STATE.md` and `CHIEF_BRIEF.md`.

### 2. Crash-idempotent simulated execution

A crash after durable simulated fills but before session completion must not duplicate those fills on restart.

Introduce deterministic operation identities and durable session/recovery semantics. Replaying an already-applied operation must leave cash, positions, P&L, fill count, attribution and session history unchanged.

Add crash-injection tests and compare uninterrupted versus crash/restart outcomes.

### 3. Strategy sleeves inside the Book

A position keyed only by symbol cannot safely represent multiple strategies.

Preserve strategy-level sleeves/ownership while exposing aggregate symbol and portfolio exposure separately. Two strategies must be able to hold opposing simulated exposure in the same symbol without overwriting attribution.

Add a regression test that validates both sleeve attribution and aggregate exposure.

### 4. IDLE remains alive

Keep bounded `run` behavior if useful, but add a genuine long-running operating mode:

`RUN -> IDLE -> wait -> due event/time/data -> RUN`

The persistent Clock must not exit merely because nothing is due now. Make waiting/time injectable so tests remain deterministic.

### 5. RISK evaluates the final simulated portfolio

When a proposal is throttled or rescaled, recompute final gross, net and concentration on the state that would actually be simulated. Hard limits must be checked after transformation, not only before it.

Add a multi-strategy regression test with existing Book exposure plus a new proposal that requires scaling.

### 6. Watchdog semantics

`RUNNING` is not `STUCK`.

Track enough timing/liveness metadata to distinguish healthy running work from work whose lease/deadline/heartbeat is stale. Add tests for both states.

## Truthfulness audit

After fixes, audit `README.md`, `STATE.md`, `CHIEF_BRIEF.md` and PR #12 claims.

Do not call the strategy registry historically version-preserving unless old versions remain inspectable. Do not claim autonomous alpha-decay management merely because lifecycle states exist. Label limitations precisely.

Negative research results are valid. Do not tune until something looks successful.

## Verification gate

Run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/demo_quant_system.py
python3 scripts/generate_schemas.py --check
```

Also prove deterministically that:

`uninterrupted run == crash after durable state mutation + restart + replay`

for Book cash, positions, fills, attribution, NAV and session cursor/history.

## Ultracode division of work

Use parallel work only where independent. Preferred split:

1. causal research/execution timeline + result recomputation;
2. Book sleeves + crash idempotence;
3. Clock liveness + watchdog + RISK regression;
4. independent review/proof after implementation.

Keep the workflow small. Do not create many agents to inspect the same files.

## Completion

Update the existing draft PR #12. Do not open another PR and do not merge it.

Before stopping, run `/quant-proof` and then `/quant-handoff`.

The handoff must contain only: fixes completed, tests added, recomputed results, remaining known limitations, and HEAD SHA.
