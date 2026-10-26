# Research OS — Aggressive Wave 2 Checkpoint — 2026-10-15

## Status

`RESEARCH_OS_AGGRESSIVE_WAVE2 = PASS`

This checkpoint records architecture/dev hardening only. It does **not** authorize or claim economic evidence, prospective observation, capital allocation, or trading.

## Proven in Wave 2

1. **Source/PIT qualification layer**
   - immutable source route registry;
   - explicit source class, locator, permission, PIT mode, revision policy, survivorship policy, timezone and availability clock;
   - outcome-bearing routes are blocked in this build phase;
   - source route mutations under the same route id are rejected.

2. **Reproducible Experiment Runner — dry-run only**
   - frozen protocol hash;
   - dataset manifest hash;
   - code hash;
   - environment hash;
   - deterministic seed;
   - source route hashes;
   - replay hash verification;
   - no economic outcome access.

3. **Independent Validator v2 diagnostics**
   - producer independence;
   - protocol freeze;
   - PIT qualification;
   - revision policy;
   - survivorship policy;
   - reproducible execution plan;
   - no-outcome-access invariant;
   - trial accounting distinction;
   - multiplicity declaration;
   - explicit claim ceiling.

4. **Economic Identity / Portfolio diagnostics v2**
   - structural overlap by payer, asset, horizon, liquidity, tail exposure and economic tags;
   - structural novelty score;
   - statistical correlation and covariance remain `UNAVAILABLE_BY_DESIGN` without admissible return data;
   - no capital allocation, position sizing or orders.

5. **Forward Registry v2**
   - explicit states: `DRAFT`, `READY_AWAITING_OWNER_AUTHORITY`, `AUTHORIZED_FOR_EXACT_SCOPE`, `CLOSED`;
   - immutable generation contract hash;
   - material change requires new generation;
   - observation must be strictly after T0;
   - observation scope must match exact Owner-authorized scope;
   - current authorized count = 0;
   - current future outcomes consumed = 0.

## Deterministic fixture result

Five synthetic candidates are carried through the Wave 2 layer.

- 4 candidates reach `READY_FOR_REPRODUCIBLE_DRY_RUN` and Validator v2 PASS.
- `SYN-FLOW-001` remains blocked because the earlier implementability layer has not qualified its cost/capacity path; the system does not manufacture a PASS.
- Overall architecture status remains PASS because correct blocking is a successful system behavior, not a failed research result.

## CI evidence before this checkpoint commit

Workflow: `Research OS wave2 hardening CI`

Run: `38743259684`

Commit: `b5b94d955bb2fdc8608b946110b979c525e6e51f`

Conclusion: `success`

## Hard authority boundary

```text
ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
```

## What is still thin / next build surface

The architecture is now materially harder to misuse, but the next build wave is still needed before real research-source activation:

- source adapters currently prove contracts and PIT semantics with synthetic routes; real permitted adapters are not active here;
- Fundamental, Event/Document, Quant/Mechanism and Institutional Flow engines remain thin producers behind stable interfaces;
- Experiment Runner proves reproducibility planning but does not execute economic experiments;
- Validator v2 checks scientific contracts but does not yet include richer dataset-level distribution diagnostics;
- Portfolio v2 is structural only; empirical covariance/marginal contribution is intentionally unavailable;
- Forward Registry v2 is readiness/authority infrastructure only; no prospective observation is authorized;
- decay remains inactive by authority.

The next aggressive wave should deepen the four research engines and introduce **real-source adapter interfaces + permission/PIT manifests in dev**, while continuing to forbid economic outcome access until separately authorized.
