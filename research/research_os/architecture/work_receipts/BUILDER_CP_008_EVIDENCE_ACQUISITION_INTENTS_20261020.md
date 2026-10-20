# BUILDER CP008 — Evidence-gap → acquisition-intent projection qualified

CHECKPOINT_ID: BUILDER_CP_008_EVIDENCE_ACQUISITION_INTENTS_20261020
TASK_CAPABILITY: deterministic pre-outcome evidence-gap → acquisition-intent projection
BUILDER_ROLE: isolated forward-builder / no autonomous runtime ownership
WORKING_BRANCH: builder/v2-forward-20261020
CP007_SHA: bf0ec73757e586bebbd46c97a65d6dd46e3ec70f
IMPLEMENTATION_SHA: 561c7e01215de6822c58be72d6765ee47a8931f0
INITIAL_TEST_SHA: 23c995041852e25092b320aad695567451d5002c
CI_WORKFLOW_SHA: f2162f7003ab78c92e1f876e449e99f7b705649d
TEST_CORRECTION_SHA: 9996036d31054d0f94b01dd45aa9b18484020829
CURRENT_BUILDER_HEAD_DESCRIBED: 9996036d31054d0f94b01dd45aa9b18484020829
FRESH_OBSERVED_ORACLE_V2_HEAD: 8eff2fc38235a4cea3b1c3ea37f90e21058169a0
SAFE_TO_CONTINUE: TRUE

## Objective

Close only the confirmed CP007 integration gap:

`explicit producer readiness data requirement`
→ deterministic bounded intent projection
→ existing acquisition firewall
→ `PLAN_ONLY_NO_NETWORK`

No source discovery, source activation, network execution, outcome access, economic experiment, prospective observation, real capital, or live trading is added.

## New capability

Added:

`research/research_os/expansion/evidence_acquisition_intents_v2.py`

Primary entrypoint:

`build_evidence_acquisition_intents(readiness, *, declared_routes, validated_adapters)`

The projection is pure and fail-closed.

### Upstream binding

The bridge:

1. requires a producer-readiness object;
2. requires `outcome_accessed == false`;
3. requires `economic_result == NOT_OBSERVED`;
4. re-runs `qualify_producer_test_readiness` over the exact specification;
5. requires the supplied upstream readiness hash to match the recomputed readiness hash;
6. preserves that exact upstream artifact identity rather than canonicalizing away upstream changes.

### Evidence requirement extraction

Only explicit `data_requirements` with status `REQUIRED` or `PARTIAL` are considered.

Requirements are sorted/deduplicated for projection ordering, but the exact upstream readiness artifact remains hash-bound.

### Declared-route semantics

The bridge does not semantically infer a provider.

A route must match the requirement text exactly and explicitly declare:

- requirement;
- adapter_id;
- content_classes;
- entity_scope;
- clock_cutoff;
- version_policy;
- optional locator_parameters.

No exact declared route:
`UNRESOLVED_NO_DECLARED_ROUTE`

Multiple exact routes:
`BLOCK_AMBIGUOUS_DECLARED_ROUTE`

Missing validated adapter:
`UNRESOLVED_ADAPTER_NOT_DECLARED`

No route/provider/source is invented.

### PIT and version safety

The bridge requires a timezone-aware `clock_cutoff` and a non-UNKNOWN version policy.

Missing/naive PIT cutoff or undeclared version policy blocks before a request reaches the acquisition firewall.

### Outcome firewall

Outcome-like scientific requirements are blocked before route matching, including return/PnL/profit/loss/payoff/outcome/market-response/price-response/future-observation/post-event/post-release variants.

Existing `acquisition_firewall_v1.FORBIDDEN_CONTENT_CLASSES` are also enforced before request construction.

The existing acquisition firewall remains final plan authority.

### Output semantics

Possible intent statuses include:

- READY_PLAN_ONLY
- UNRESOLVED_NO_DECLARED_ROUTE
- UNRESOLVED_ADAPTER_NOT_DECLARED
- BLOCK_AMBIGUOUS_DECLARED_ROUTE
- BLOCK_INVALID_DECLARED_ROUTE
- BLOCK_FORBIDDEN_REQUIREMENT
- BLOCK_FORBIDDEN_CONTENT_CLASS
- BLOCK_FIREWALL

Overall projection statuses:

- NO_EXPLICIT_DATA_REQUIREMENTS
- READY_PLAN_ONLY
- INCOMPLETE_UNRESOLVED
- BLOCK

All outputs preserve:

- projection_only = true
- network_execution_authorized = false
- network_call_performed = false
- outcome_accessed = false
- economic_result = NOT_OBSERVED
- four authority flags = false

The projection emits a deterministic `projection_hash`.

## Tests added

Added:

`tests/test_research_os_evidence_acquisition_intents_v2.py`

Focused adversarial cases prove:

1. declared documentary gap + explicit matching adapter/route → existing firewall `READY_AWAITING_SOURCE_ACTIVATION_AUTHORITY` / bridge `READY_PLAN_ONLY`;
2. no declared route → unresolved without invented source;
3. declared route but absent validated adapter → unresolved;
4. outcome-like requirement → hard block before matching;
5. forbidden content class → hard block;
6. missing or timezone-naive PIT cutoff → hard block;
7. UNKNOWN version policy → hard block;
8. multiple exact routes → ambiguity block;
9. same exact upstream readiness artifact remains deterministic even if declared-route order changes;
10. upstream readiness-hash corruption and outcome-bearing readiness fail closed.

## Falsification event — CI found a bad test assumption

First exact-head qualification attempt:

- SHA: `f2162f7003ab78c92e1f876e449e99f7b705649d`
- GitHub Actions Oracle V2 Core run: `39447828099`
- job: `118714336202`
- compilation: PASS
- test result: 64/65 PASS, 1 FAIL

The failing test required two differently serialized upstream readiness artifacts, differing in requirement-list order, to produce the same complete projection object.

That expectation was scientifically wrong because `producer-test-readiness.v1` intentionally hashes the exact upstream specification. Making the implementation normalize that away would weaken provenance binding.

Disposition:

- module implementation NOT weakened;
- upstream readiness hash binding preserved;
- test corrected to require determinism for the same exact upstream artifact while proving declared-route order independence.

Correction commit:

`9996036d31054d0f94b01dd45aa9b18484020829`

## Exact-head independent CI proof

Successful Oracle V2 Core run:

- run ID: `39448140722`
- job ID: `118715433854`
- exact head SHA: `9996036d31054d0f94b01dd45aa9b18484020829`
- Python: 3.12
- compile V2 Core: PASS
- V2 contract/bridge/worker/whole-loop tests: PASS
- tests run: 65
- failures: 0
- policy fail-closed check: PASS
- V2 claim ceiling check: PASS
- exact-head qualification receipt: PASS
- qualification status: `AUTONOMOUS_PRE_OUTCOME_RESEARCH_PIPELINE_QUALIFIED`
- qualification verified commit: `9996036d31054d0f94b01dd45aa9b18484020829`
- real GitHub-state V2 entrypoint dry-run: PASS
- dry-run observed autonomous state head: `8eff2fc38235a4cea3b1c3ea37f90e21058169a0`
- GitHub writes: 0
- push attempts: 0
- real fetch commands: 2
- proof artifact ID: `12275729265`
- proof artifact SHA256: `7f028abd45ea07c3bdc23fe5160ff76ea694738a73e3bfec86f211249a657e39`

The separate SEC P0 pre-t0 gate for the same Builder SHA was still in progress at the moment this checkpoint was prepared; this checkpoint does not falsely claim a result for that unrelated longer-running gate.

## Fresh autonomous runtime observation

Fresh observed Oracle V2 branch head before checkpoint:

`8eff2fc38235a4cea3b1c3ea37f90e21058169a0`

Commit time:
`2026-10-20T15:20:17Z`

Message:
`Research OS canonical queue refill f1f144b4d4fe994614c49a91a288e9437cc514b7a8164825fa36fa542e550a23 [skip ci]`

No autonomous Oracle state was mutated by Builder.

## What is proven

- The CP007 gap was real: Wave4 consumed fixture-written requests rather than deriving them from producer data requirements.
- A pure deterministic bridge now exists.
- The bridge preserves exact upstream scientific provenance.
- The bridge cannot invent sources/providers from requirement prose.
- PIT cutoff/version metadata must be explicit.
- Existing validated adapters and acquisition firewall remain authoritative.
- Outcome-like demand is blocked before acquisition planning.
- No network call is performed by the bridge.
- No candidate is generated or mutated.
- No economic outcome is accessed.
- Existing V2 tests and deployment tests remain green on the exact Builder head.

## What is NOT proven / NOT authorized

- No proof that any missing evidence is obtainable.
- No proof that any adapter should be activated.
- No authorization for network acquisition.
- No runtime task creation from these intents.
- No automatic modification of source registries.
- No economic edge, alpha, return, profitability, correlation, or portfolio contribution claim.
- No prospective observation.
- No real-capital or live-trading authority.

## Authority invariants

ECONOMIC_EXPERIMENT_AUTHORIZED: FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED: FALSE
REAL_CAPITAL_AUTHORIZED: FALSE
LIVE_TRADING_AUTHORIZED: FALSE
OUTCOME_ACCESSED: FALSE
ECONOMIC_RESULT: NOT_OBSERVED

## NEXT_RECOMMENDED_TASK

Before any runtime wiring, audit whether owner-facing observability/readiness already has a truthful surface for:

- explicit evidence requirements;
- acquisition-intent readiness;
- unresolved no-route state;
- firewall-blocked state;
- network authorization remaining false.

Do not wire this bridge into autonomous Oracle until that observability/integration boundary is reconstructed and a specific missing capability is proven.

## EXACT_RESUME_ACTION

1. Read CP008.
2. Reacquire fresh Builder and autonomous Oracle V2 heads.
3. Inspect `edge_observability_v2.py`, V2 readiness sidecars, Site/owner projections, and any existing acquisition-plan summaries.
4. Determine whether evidence-demand/acquisition-intent status is already owner-observable.
5. If already present, record NO_BUILD disposition.
6. If absent, implement only a read-only projection/composition layer on Builder; do not activate network or mutate runtime tasks.
7. Run exact-head CI and checkpoint before considering runtime integration.

## FINAL_INTEGRATOR_IMPLICATION

Final Integrator may import `evidence_acquisition_intents_v2.py` as a pure pre-acquisition planning primitive upstream of the existing acquisition firewall. It should not be merged as an autonomous acquisition executor. Any future integration must preserve exact upstream readiness binding and keep acquisition execution/network authority independently gated.

SAFE_TO_CONTINUE: TRUE
