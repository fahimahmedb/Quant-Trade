# WAVE 2 — SHARED CONTRACT CONFLICT MATRIX

This matrix is pre-convergence evidence only. It does not integrate sibling builders and does not emit canonical Wave2 truth.

Canonical sealed base: `2b99d8aeb8a342f1ef32544247d366cb8a26037e`.
Historical B/D0 sibling start: `97165db2faa3300cef1f23de0045ed93d25eb9cb`.

## Current matrix

| Contract / surface | Current observed producer/owner | Current observed consumer/other owner | Compatibility | Conflict class | Required Convergence #2 action | Required proof |
|---|---|---|---|---|---|---|
| Wave2 immutable base identity | sealed base `2b99d8ae…` | B and D0 were created from `97165db2…`; E directly from sealed base | B content port clean; D0 embeds old SHA semantically | `BASE_BINDING_CONFLICT_D0` | port B/D0 semantic deltas onto sealed base; explicitly rebind D0 old base pin | exact-base ancestry/content, focused suites, clean diff |
| Multi-Source branch | branch exists at exact sealed base `2b99d8ae…` | Research Intelligence / B | correct ancestry but no implementation delta | `IMPLEMENTATION_MISSING` | sibling must implement against foreman acceptance pack; foreman must not implement it | exact sibling head, focused acceptance suite, exact-head receipt |
| Source/document identity | sealed `frontier_source_planner_v2` binds source ref, packet/content hash, record hash, optional blob, clocks | Multi-Source intake then RI/B | canonical law exists | `OWNERSHIP_CONFLICT_IF_MULTISOURCE_REDEFINES` | reuse exact source qualification/content-identity semantics | source-ref mismatch reject; missing hash reject; rename/copy not novelty |
| Source revision / stale snapshot | source packets retain revision/period/retrieval/freeze metadata | future Multi-Source | required but no sibling implementation yet | `REQUALIFICATION_CONFLICT_PENDING_MULTISOURCE` | material source/snapshot/clock revision must create new binding or requalification, never inherit silently | source revision fixture; stale old receipt cannot pass |
| Multi-source composition | no dedicated implementation yet | future Multi-Source | unresolved | `SEMANTIC_CONFLICT_PENDING_MULTISOURCE` | preserve per-source roles/conflicts; source count cannot majority-vote truth | duplicate-content multi-URL; conflicting-source UNKNOWN/BLOCK fixtures |
| Scientific Memory | canonical `scientific_memory.py` + RI memory relation | Multi-Source / B | canonical single store exists | `OWNERSHIP_CONFLICT_IF_MULTISOURCE_DUPLICATES` | Multi-Source may reference/screen but must not create second store or collapse dispositions | NEGATIVE/BLOCKED/UNEXECUTED/INVALIDATED_PROTOCOL/POSITIVE_BUT_INSUFFICIENT remain distinct |
| Generation mandate -> RI | `research_refill_policy.py` emits pure `GENERATE_MECHANISM`, novelty unresolved | queue replenisher / later RI | compatible | `NO_CONFLICT_OBSERVED` | preserve generation-vs-candidate distinction | UNKNOWN identity not novelty; scheduler mutation false |
| Operational ResearchTask READY | canonical bounded `queue_replenisher.py` | future Multi-Source and scientific lanes must not own it | compatible only with membrane | `AUTHORITY_CONFLICT_IF_MULTISOURCE_MINTS_READY` | retain one bounded operational adapter; intake never writes queue/task state | max-one refill; no same-wake producer; no direct READY from intake |
| Research Intelligence decision -> B | RI owns semantic identity/memory/action selection; B requires `RUN_PRODUCER`, executable true, scheduler false | B | compatible and explicit | `NO_CONFLICT_OBSERVED` | Multi-Source must pass through RI; no direct proposal->B shortcut | proposal/GENERATE_MECHANISM sent to B blocks with RI-not-qualified reason |
| Candidate | MEGA B additively enriches canonical Candidate under `candidate.discovery` | C0 | provisionally compatible | `SEMANTIC_OVERLAP_PENDING_C0_IMPLEMENTATION` | preserve one Candidate; C0 binds exact snapshot/hash/generation | B->C0 round trip; mutation/new-generation test; UNKNOWN preservation |
| Source/PIT clocks in B/C0 | B retains published/available/effective/freeze/entry/exit clocks and blocks conflicts/leakage | C0 cross-examination | compatible if same facts retained | `SEMANTIC_OVERLAP` | C0 consumes exact B facts/provenance rather than recalculating divergent truth | exact clocks retained; conflicts remain blockers |
| Duplicate/novelty identity | RI/B use structural semantic/mechanism/exposure identity; path/lexical similarity is not scientific novelty | Multi-Source/C0/Memory | compatible if identity namespaces remain separate | `SEMANTIC_OVERLAP` | no path/source-count/correlation shortcut to novelty | rename/copy, same mechanism, wrapper-equivalence, UNKNOWN fixtures |
| Implementability | B reuses canonical `assess_implementability_depth` | Factory/C0 | compatible | `NO_CONFLICT_OBSERVED` | no parallel implementability registry | canonical receipt exactness; NOT_READY remains blocked |
| Factory / freeze | B explicitly leaves `experiment_frozen=false`; sealed Factory owns freeze/registry/replay/receipt | C0 | compatible if reused | `OWNERSHIP_CONFLICT_IF_C0_REDEFINES` | C0 consumes canonical frozen identity; material Candidate change requires new generation | candidate/protocol/source/code mutation tests |
| Validator | sealed base already owns `validator_economic_readiness_v3` / `validation_readiness.py` | W1 ECON already composes it; C0 expected to expose/reuse scientific adjudication | canonical law already exists | `OWNERSHIP_CONFLICT_IF_C0_DUPLICATES` | extract/compose existing Validator; do not create second independent truth engine | producer != validator; binding/outcome firewall/UNKNOWN tests |
| Red Team | sealed `red_team_negative_rights_v2` | W1 ECON already composes it; C0 expected to reuse | canonical negative-rights law exists | `OWNERSHIP_CONFLICT_IF_C0_DUPLICATES` | reuse exact negative-rights semantics; no repair/retune/profit optimization | blockers may only block; repair/mutation/outcome opening remain false |
| W1 ECON scientific composition | `economic_test_readiness_v1.py` currently invokes Validator + Red Team | future C0 then W1 ECON seam | risk of double-adjudication divergence | `DOUBLE_ADJUDICATION_CONFLICT_PENDING_C0` | converge onto one exact-subject scientific receipt/shared primitive; W1 ECON may verify/consume, not manufacture divergent parallel truth | one candidate/protocol/trial disposition; mutation produces mismatch/block |
| Scientific disposition | C0 implementation absent; foreman acceptance schema is intent only | W1 ECON then D0 | unresolved | `IMPLEMENTATION_MISSING_C0` | C0 must bind exact Candidate/freeze/trial/provenance/blockers/uncertainty | C0 acceptance matrix exact-head green on sibling |
| Scientific readiness vs operational READY | B/C0/Multi-Source scientific states | E/Control Plane owns operational admission | compatible only with membrane | `AUTHORITY_CONFLICT_IF_CONFLATED` | never map scientific states directly to task READY | no enqueue/control-plane mutation from B/C0/D0/Multi-Source |
| EconomicIdentityRef | W1 ECON canonical structural identity | D0 consumes/ref-hashes it | semantically compatible | `BASE_BINDING_CONFLICT_D0` | keep W1 ECON law; rebind D0 Wave2 base pin to `2b99d8ae…` | identity ref validation; W1 ECON non-regression |
| PortfolioReadinessRef | W1 ECON canonical portfolio readiness | D0 consumes it | compatible | `BASE_BINDING_CONFLICT_D0` | same local base-pin repair; no readiness rebuild | hash exactness; empirical layer sealed; return series not consumed |
| D0 lifecycle readiness | D0 `SHADOW_READY_AWAITING_AUTHORITY` / upstream-blocked lifecycle states | E runtime may invoke through canonical tasks | compatible if namespace kept separate | `STATE_MACHINE_CONFLICT_IF_CONFLATED` | lifecycle readiness never becomes task READY | no task creation; no prospective-observation authority |
| D0 review cadence | D0 rejects scheduler ownership | E scheduler/runtime | compatible | `NO_CONFLICT_OBSERVED` | only E/Control Plane owns scheduling | canonical task invocation; D0 scheduler ownership false |
| D0 outcome/decay boundary | D0 rejects raw outcomes and accepts externally qualified evidence refs | future evaluator outside D0 | compatible | `NO_CONFLICT_OBSERVED` | preserve evaluator separation | raw outcomes rejected; D0 cannot self-issue evidence |
| ResearchTask / queue / leases | canonical Research OS Control Plane and qualified E | scientific lanes | E exact-head qualified; ownership is explicit | `NO_CONFLICT_IF_MEMBRANE_PRESERVED` | retain canonical task/lease identity and bounded refill | E exact-head + seam tests; stale claim/replay safety |
| Runtime recovery / outbox / Live Lab | qualified E `2d5ff9d…` | canonical task/event/receipt state | compatible with B+D0 simulation | `NO_CONFLICT_OBSERVED_CURRENT_E` | integrate E semantic delta only; no second scheduler/emitter | E 75, Live Lab 2/57, recovery/replay receipts |
| Global STATE/config/registries | all lanes may imply changes | canonical integrator owns final truth | intentionally not sibling-owned | `GLOBAL_TRUTH_CONFLICT` | reconcile only in canonical Convergence #2 | exact-head integrated docs/config/tests |
| Authority flags | all observed qualified law keeps economic/prospective/capital/trading false | all lanes | must remain identical | `AUTHORITY_CONFLICT_ON_ANY_TRUE` | fail immediately on unexpected TRUE | recursive config/task/receipt/manifest scan; no outcomes accessed |
| UNKNOWN semantics | Scientific Memory/RI/B/D0 preserve UNKNOWN materially | Multi-Source/C0/E seams | must remain | `STATE_MACHINE_CONFLICT_IF_COERCED` | never coerce missing evidence to negative/zero/idle/profitable | seam round trips with UNKNOWN |

## Base-repair intersection analysis

The sealed-base repair `97165db2… -> 2b99d8ae…` touches exactly three paths:

1. `research/research_os/legacy/LEGACY_RESEARCH_LEDGER.imported.json`;
2. `research/research_os/tests/test_economic_identity_portfolio_readiness.py`;
3. `research/research_os/tests/test_economic_readiness_integration.py`.

Observed B and D0 semantic deltas do not textually overlap those paths. D0 nevertheless embeds the old Wave2 base SHA in `research/research_os/expansion/economic_lifecycle.py`, so intentional rebinding and requalification remain mandatory.

`TEXTUAL_BASE_REPAIR_CONFLICT_B=FALSE`

`TEXTUAL_BASE_REPAIR_CONFLICT_D0=FALSE`

`CONTRACT_CHANGE_REQUIRED=TRUE_FOR_D0_BASE_REBIND`

## New foreman conflict findings

### C0 is not a green-field Validator/Red Team build

W1 ECON already composes the canonical Validator and Red Team. The C0 acceptance pack therefore treats the problem as extraction/reuse and exact-subject binding. Any C0 implementation that introduces independent competing Validator, Red Team, experiment registry, freeze, trial-accounting or outcome-firewall semantics creates a convergence conflict.

Foreman proof: `Wave2 C2 C0 Acceptance Pack Preflight`, run `39660073926` SUCCESS on checkpoint `e239c55a5d3711f3b24f793b5d9cc0a079188c79`.

### Multi-Source is not a second replenisher

The exact branch now exists at the sealed base but contains no delta. Existing source planning already rejects source-ref mismatch/non-documentary/missing-content-hash inputs, binds qualified content identity, and does not treat path rename/copy as novelty. Existing Research Intelligence refuses to treat unknown identity as novelty. Existing bounded queue replenishment owns operational task creation.

Therefore Multi-Source must produce a provenance-bound ideation/proposal envelope that enters the existing Research Intelligence chain. It may not bypass to B or mint operational task state.

## Highest-risk unresolved zones

1. **C0 implementation missing**: acceptance law is green, sibling delta absent and branch remains pre-sealed-base.
2. **Multi-Source implementation missing**: branch exists at sealed base but has zero delta.
3. **Double-adjudication risk**: C0 must reuse existing Validator/Red Team while W1 ECON retains economic identity/structural veto, without two divergent scientific verdicts.
4. **Live Multi-Source -> RI -> RUN_PRODUCER -> B seam unproven**.
5. **Live B -> C0 -> W1 ECON -> rebound D0 seam unproven**.
6. **D0 old base pin** remains a controlled canonical-port repair.
7. No full canonical exact-head Wave2 integration/regression exists.

## Authority

`ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE`

`PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE`

`REAL_CAPITAL_AUTHORIZED=FALSE`

`LIVE_TRADING_AUTHORIZED=FALSE`

`OUTCOME_ACCESSED=FALSE`
