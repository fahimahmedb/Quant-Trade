# Research OS — Aggressive Wave 3 Checkpoint — 2026-10-15

## Status

`RESEARCH_OS_AGGRESSIVE_WAVE3 = PASS`

This is an architecture/dev checkpoint only. No real source has been activated and no economic outcome has been consumed.

## What Wave 3 proves

### 1. Design-only real-source adapter contracts

Five adapter families are modeled behind immutable contracts:

- regulatory filings;
- corporate investor-relations documents;
- exchange reference data;
- public index / rebalance rules;
- official macro / policy publications.

Every adapter must declare permission model, clock semantics, revision handling, survivorship handling and locator template.

Current invariant:

```text
activation_state = DESIGN_ONLY_NOT_CONNECTED
network_access = false
contains_market_outcome = false
outcome_access_authorized = false
activated = false
```

The registry rejects silent mutation of an adapter under the same adapter id.

### 2. Four research engines now carry structured dossiers

The shared CandidateHypothesis contract remains unchanged.

`QUANT_MECHANISM` now requires a structured dossier covering trigger, payer/forced actor, structural reason, expression, universe, confounders and active disconfirmation.

`FUNDAMENTAL` now requires issuer identity, statements, earnings/guidance, estimate revisions, valuation frame, balance-sheet quality, cash-flow quality, competitive position, catalysts and active disconfirmation.

`EVENT_DOCUMENT` now requires event identity, document clock, eligibility, novel information, diffusion hypothesis, confounders and active disconfirmation.

`INSTITUTIONAL_FLOW` now requires forced actor, constraint rule, implementation clock, affected universe, expected footprint, capacity constraints, confounders and active disconfirmation.

Every dossier additionally requires:

```text
source_clock_frozen = true
active_disconfirmation = true
outcome_accessed = false
```

### 3. Scientific blocking remains orthogonal to dossier completeness

`SYN-FLOW-001` has a complete engine dossier and valid design-only adapter bindings, but remains blocked by the Wave 2 experiment/validator gate because cost/capacity implementability has not been qualified.

That is intentional and proves the architecture does not confuse a well-specified idea with an admissible economic experiment.

### 4. Candidate integrity is hash-checked

Wave 3 hashes the primary CandidateHypothesis set before and after dossier/adaptor processing.

Required result:

```text
candidate_integrity.unchanged = true
candidate_mutations = 0
```

### 5. No hidden source activation

Required registry result:

```text
adapter_count = 5
activated_count = 0
network_enabled_count = 0
outcome_authorized_count = 0
```

## CI evidence before this checkpoint commit

Workflow: `Research OS wave3 engine depth CI`

Run: `38744190909`

Commit: `a2d766db0bbb9eeb9e74630650f2bfc036922ed0`

Conclusion: `success`

## Authority boundary

```text
REAL_SOURCE_ACTIVATION_AUTHORIZED = FALSE
NETWORK_ACCESS_AUTHORIZED = FALSE
ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
```

## Next build surface

The next architecture wave should add an acquisition firewall and typed normalization layer so a future permitted source adapter cannot directly feed research engines. The required shape is:

```text
Adapter Spec
  -> Permission / Clock Preflight
  -> Acquisition Plan (no fetch in current authority state)
  -> Content Firewall
  -> Typed PIT Record
  -> Provenance Manifest
  -> Engine Dossier
```

This keeps network activation and outcome-bearing content as separate future Owner gates rather than implicit consequences of defining a source adapter.
