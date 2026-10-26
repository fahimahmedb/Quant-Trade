# BUILDER CP007 — Evidence-gap → acquisition-intent bridge audit

CHECKPOINT_ID: BUILDER_CP_007_EVIDENCE_ACQUISITION_BRIDGE_GAP_20261020
TASK_CAPABILITY: deterministic pre-outcome evidence-demand projection
BUILDER_ROLE: isolated forward-builder / no runtime ownership
WORKING_BRANCH: builder/v2-forward-20261020
TASK_BASE_SHA: 1206ca91349aea9efec69c6d19059050517f78e9
CURRENT_BUILDER_HEAD_DESCRIBED: 1206ca91349aea9efec69c6d19059050517f78e9
FRESH_OBSERVED_ORACLE_V2_HEAD: 468bd7829626cde4d6b03b0c0b601ccf58fed847
HISTORICAL_PRODUCER_READINESS_HEAD: d48eaf78487d1d617cf9feddbdd16c199925684d
SAFE_TO_CONTINUE: TRUE

## Objective

Determine whether the repository already contains a deterministic bridge from an explicit scientific/documentary evidence gap to a bounded acquisition request/intent before adding any new architecture.

North-Star property: a missing piece of evidence must be representable as a reproducible, point-in-time-safe demand for admissible source material without inventing a source, touching a network, inspecting outcomes, or opening economic/prospective/capital/live authority.

## Fresh state evidence

- Builder remained unchanged at `1206ca91349aea9efec69c6d19059050517f78e9` during the capability audit.
- Autonomous Oracle V2 was independently observed at `468bd7829626cde4d6b03b0c0b601ccf58fed847`, commit message `Research OS mechanism_research FRONTIER-QUANT-MECHANISM-DISTINCT-009-g2-de26f389489e [skip ci]`.
- No write was made to the autonomous Oracle branch.

## Existing capabilities — proven present

### 1. Engine dossier / scientific evidence status

`research/research_os/expansion/engine_dossiers_v1.py` already produces family-specific documentary dossiers and field-level evidence states such as `SUPPORTED`, `PARTIAL`, and `UNKNOWN`, with blockers and source binding.

Current Builder blob:
`e9399e5cde42e640d3de73a90ab619a319e61536`

Historical Producer Readiness has the exact same blob, proving that capability was absorbed rather than lost.

### 2. Acquisition firewall / plan validation

`research/research_os/expansion/acquisition_firewall_v1.py::build_acquisition_plan(validated_adapter, request)` already:

- requires a pre-structured request with `request_id`, `entity_scope`, `content_classes`, `clock_cutoff`, and `version_policy`;
- checks requested content against the validated adapter contract;
- rejects outcome-bearing content classes;
- requires adapter state to remain inactive/no-network/no-outcome-authority;
- emits `PLAN_ONLY_NO_NETWORK`;
- sets `network_execution_authorized = false`;
- sets `network_call_performed = false`;
- sets `outcome_access_authorized = false`;
- sets `outcome_accessed = false`.

The firewall therefore validates/bounds an already-declared request. It does not infer scientific demand from dossier gaps.

Current Builder blob:
`7c6569e0c304bb2e18ee9cd26b8a4abb36a30664`

Historical Producer Readiness carries the same firewall blob.

### 3. Source qualification / provider-specific adapters

Existing source qualification and adapter surfaces already own source-specific admissibility/PIT semantics. They must remain authoritative; a new bridge must not duplicate or loosen them.

### 4. Implementability and readiness

Existing implementability/readiness paths assess whether declared data/PIT/cost/capacity requirements are sufficient. They do not create an acquisition request from a dossier evidence gap.

### 5. Forward registry

`research/research_os/expansion/forward_v2.py` concerns prospective contracts after readiness. It does not create documentary acquisition intents and must remain separate from evidence acquisition.

## Falsification search performed

The audit explicitly looked for an already-existing bridge before authorizing any implementation:

1. Current Builder expansion directory inspected.
2. Current Builder test directory inspected for acquisition/request/intent-specific surfaces.
3. Current Builder `acquisition_firewall_v1.py` inspected semantically, not only by filename.
4. Current Builder `engine_dossiers_v1.py`, implementability paths, and `forward_v2.py` inspected for hidden request generation.
5. Historical branch `builder/econ-readiness-producer-evidence-20261016` expansion surfaces inspected.
6. Historical Producer Readiness `final_shape.py` inspected; no acquisition-request construction exists there.
7. Repository tree/name search found no separate evidence-request/acquisition-intent bridge.

## Actual gap

CONFIRMED_BOUNDED_GAP:

The repository has both sides of the scientific boundary but no deterministic adapter between them:

`explicit dossier/evidence gap`
→ **MISSING BRIDGE**
→ `firewall-compatible bounded acquisition request`
→ existing `build_acquisition_plan(...)`

This is not a missing network connector, fetcher, autonomous source crawler, or outcome pipeline.

## Required bounded implementation contract

A valid Builder increment may only be a pure projection layer that:

1. accepts explicit evidence requirements/gaps plus an explicit declared adapter/request catalog;
2. never guesses a provider or URL;
3. maps only declared, supported scientific evidence needs to whitelisted content classes;
4. requires explicit entity scope, clock cutoff, and version policy;
5. refuses outcome-like requirements (`return`, `returns`, `pnl`, `profit`, `loss`, `payoff`, future/post-event/market-response content);
6. returns unresolved/no-intent when no declared adapter can satisfy the requirement;
7. never fetches, writes, mutates tasks, activates adapters, or performs network I/O;
8. preserves all four authority flags as false;
9. reports `outcome_accessed = false` and `economic_result = NOT_OBSERVED`;
10. produces a deterministic projection hash;
11. can optionally pass its structured request into the existing acquisition firewall, but may not bypass or weaken that firewall.

## Non-goals

- No data acquisition execution.
- No HTTP/network access.
- No dynamic provider discovery.
- No source fabrication.
- No candidate fabrication.
- No economic experiment.
- No prospective observation.
- No result/return/PnL access.
- No real capital or live trading.
- No modification of current Oracle runtime tasks.
- No replacement of source qualification or acquisition firewall contracts.

## Authority invariants

ECONOMIC_EXPERIMENT_AUTHORIZED: FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED: FALSE
REAL_CAPITAL_AUTHORIZED: FALSE
LIVE_TRADING_AUTHORIZED: FALSE
OUTCOME_ACCESSED: FALSE
ECONOMIC_RESULT: NOT_OBSERVED

## What is proven

- Dossier gap representation exists.
- Source/adaptor qualification exists.
- Acquisition firewall exists.
- PIT/source safety exists.
- Historical Producer Readiness did not contain the missing chaining layer.
- No current inspected orchestrator secretly constructs the missing request.
- The gap is therefore integration semantics, not missing top-level architecture.

## What is NOT proven

- No claim that any missing evidence is actually obtainable.
- No claim that satisfying a documentary gap creates economic edge.
- No claim that a source adapter should be activated.
- No claim that an acquisition plan authorizes network execution.
- No claim that future/prospective outcomes may be observed.

## Adversarial requirements for the next increment

Tests must prove at minimum:

- declared documentary requirement + matching explicit catalog entry → bounded intent;
- missing matching adapter → unresolved/no invented source;
- outcome/return/PnL/future requirement → hard block;
- missing PIT cutoff/version policy → hard block or unresolved, never guessed;
- unsupported content class → block;
- deterministic output/hash;
- all authority false;
- no network/write side effects;
- existing acquisition firewall remains final authority for plan readiness.

## NEXT_RECOMMENDED_TASK

Implement one small pure module for evidence-gap → acquisition-intent projection plus focused adversarial tests. Do not wire it into autonomous runtime yet. Run exact-head Builder CI. Persist a new checkpoint with implementation SHAs and CI evidence.

## EXACT_RESUME_ACTION

1. Read this CP007.
2. Reacquire fresh Builder and autonomous Oracle V2 HEADs.
3. Inspect exact adapter-spec field names needed by `build_acquisition_plan` / source qualification.
4. Implement only the pure bridge on `builder/v2-forward-20261020`.
5. Add adversarial tests.
6. Run exact-head CI on the Builder rail.
7. Persist CP008 before moving to any runtime integration question.

## FINAL_INTEGRATOR_IMPLICATION

If CP008 qualifies, Final Integrator may import the pure bridge as a pre-acquisition planning primitive. It should remain upstream of `acquisition_firewall_v1` and must not itself gain network, outcome, prospective, capital, or trading authority.

SAFE_TO_CONTINUE: TRUE
