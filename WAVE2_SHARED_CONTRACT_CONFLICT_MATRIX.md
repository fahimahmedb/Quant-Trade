# WAVE 2 — SHARED CONTRACT CONFLICT MATRIX

This matrix is pre-convergence evidence only. It does not integrate sibling builders and does not emit canonical Wave2 truth.

Canonical sealed base: `2b99d8aeb8a342f1ef32544247d366cb8a26037e`.
Historical sibling start: `97165db2faa3300cef1f23de0045ed93d25eb9cb`.

## Current matrix

| Contract / surface | Current observed producer/owner | Current observed consumer/other owner | Compatibility | Conflict class | Required Convergence #2 action | Required proof |
|---|---|---|---|---|---|---|
| Wave2 immutable base identity | sealed base `2b99d8ae…` | B and D0 were created from `97165db2…` | content repair is narrow, but D0 embeds old SHA semantically | `BASE_BINDING_CONFLICT` | port sibling deltas onto sealed-base content; D0 must replace old base pin and regenerate derived refs/hashes through tests | exact-base ancestry/content, focused suite, clean diff |
| Candidate | MEGA B now additively enriches canonical Candidate under `candidate.discovery` | C0 final delta unavailable | provisionally compatible | `SEMANTIC_OVERLAP_PENDING_C0` | preserve one Candidate; C0 must bind exact snapshot/hash/generation and not mint a second dialect | B->C0 round trip, mutation/generation test, UNKNOWN preservation |
| Research Intelligence decision -> B | B requires already-qualified `RUN_PRODUCER`, `executable=true`, selected capability match, `scheduler_mutation=false` | upstream Research Intelligence | compatible | `NO_CONFLICT_OBSERVED` | preserve exact decision provenance and capability route | rejected decision cannot execute producer; capability mismatch blocks |
| Scientific readiness vs operational READY | B emits `READY_FOR_FACTORY` / `EXPERIMENT_READY_HANDOFF`; Multi-Source may emit scientific eligibility | E/Control Plane owns ResearchTask `READY` | compatible only with membrane | `AUTHORITY_CONFLICT_IF_CONFLATED` | never map scientific states directly to queue READY; operational admission remains Control Plane-owned | no enqueue/control-plane mutation from B/C0/D0; explicit task-admission tests |
| Multi-Source source claim / source provenance | exact branch/schema unavailable | B consumes source refs, evidence identity and clocks | unresolved | `IDENTITY_CONFLICT_PENDING_MULTISOURCE` | preserve exact source/document identity, clocks, qualification and stale/reopen semantics | source-ref round trip; stale source blocks/requalifies; no substitution |
| Source/PIT clocks | B checks published/available/effective/entry/exit clocks and leakage | C0 must cross-examine same factual timing | compatible if same facts retained | `SEMANTIC_OVERLAP` | C0 should consume B facts/provenance rather than recalculate into a divergent truth | exact clocks retained; conflicts remain blockers |
| Duplicate/novelty identity | B uses mechanism/exposure/expression identity; lexical similarity and empirical correlation are not used | C0/Memory may inspect ancestry/duplicate evidence | provisionally compatible | `SEMANTIC_OVERLAP` | C0 may challenge B novelty but must preserve B provenance and cannot rewrite historical identity | duplicate mechanism, same exposure/different wrapper, UNKNOWN identity fixtures |
| Implementability | B reuses canonical `assess_implementability_depth` | Factory/C0 downstream | compatible | `NO_CONFLICT_OBSERVED` | no parallel implementability registry; carry canonical receipt | canonical receipt exactness; NOT_READY remains blocked |
| Factory / freeze | B explicitly leaves `experiment_frozen=false`, `factory_law_redefined=false` | C0 consumes frozen/preregistered identity via Factory law | compatible if C0 composes rather than replaces | `IDENTITY_CONFLICT_PENDING_C0` | material post-freeze Candidate change must create new generation | protocol hash/generation/freeze identity tests |
| Validator / Red Team | B explicitly does not invoke them | C0 expected owner/composer | compatible | `OWNERSHIP_CONFLICT_IF_C0_DUPLICATES` | C0 must use canonical independent validation/Red Team surfaces | producer cannot self-validate; blockers cannot be overridden |
| Scientific verdict | C0 unavailable | W1 ECON then D0 | unresolved | `SCHEMA_VERSION_CONFLICT_PENDING_C0` | verdict envelope must bind exact Candidate/freeze/trial identity, uncertainty and provenance | exact subject binding; blockers/uncertainty survive; no outcome leakage |
| EconomicIdentityRef | D0 calls canonical W1 `structural_identity`, requires verified candidate binding and hashes it | C0/Economic boundary upstream | semantically compatible | `BASE_BINDING_CONFLICT` only | keep W1 ECON law; update D0 Wave2 base pin from `97165db2…` to `2b99d8ae…` during canonical port | identity hash/ref validation; W1 ECON non-regression |
| PortfolioReadinessRef | D0 consumes canonical `portfolio-diagnostics.v2`, requires empirical layer `SEALED_BY_AUTHORITY` | W1 ECON upstream | compatible | `BASE_BINDING_CONFLICT` only | same base-pin repair; do not rebuild readiness | readiness hash exact; return-series consumed false; empirical layer sealed |
| D0 lifecycle readiness | D0 uses `SHADOW_READY_AWAITING_AUTHORITY` / `BLOCKED_BY_UPSTREAM_READINESS` | future E runtime may invoke lifecycle operations | compatible if names never collide semantically with task READY | `STATE_MACHINE_CONFLICT_IF_CONFLATED` | keep lifecycle readiness separate from scheduler status | no task creation; no prospective observation authority; BLOCKED != FAILED |
| D0 review cadence | D0 policy explicitly rejects `scheduler_owned_by_d0=true` | E scheduler/runtime | compatible | `NO_CONFLICT_OBSERVED` | E may schedule canonical tasks that call D0, but D0 never owns scheduler | scheduler ownership false; invocation through canonical task identity |
| D0 outcome/decay boundary | D0 recursively rejects raw outcome aliases and accepts only externally qualified evidence refs | future evaluator outside D0 | compatible with closed outcome membrane | `NO_CONFLICT_OBSERVED` | preserve external evaluator separation | raw outcomes rejected; D0 cannot self-issue evidence; exact observation identity |
| ResearchTask | canonical Research OS task schema | E final implementation unavailable; B/C0/D0 must not own task state | unresolved pending E | `OWNERSHIP_CONFLICT_PENDING_E` | retain one operational unit and one task state machine | schema validation; BLOCKED != FAILED; idempotent handoff; lease generation |
| Queue replenishment | canonical `control_integrator` bounded refill | E must harden/reuse | unresolved pending E | `AUTHORITY_CONFLICT_PENDING_E` | no producer/model/scientific state may mint READY directly | global zero READY/CLAIMED proof; max one derivation; no same-wake producer run |
| Runtime scheduler identity | modern Research OS Control Plane/Oracle plus legacy `src/autonomous_research` overlap already exists | E must resolve/bridge/quarantine | unresolved | `RUNTIME_CONFLICT_PENDING_E` | E must not create a third scheduler and must designate canonical path explicitly | scheduler uniqueness; legacy bypass impossible; restart/recovery proof |
| Lease / claim protocol | canonical Git-backed task/lease generation | E final unavailable | unresolved | `PERSISTENCE_CONFLICT_PENDING_E` | preserve canonical lease identity or explicit adapter only | stale claim rejection; generation monotonic; concurrent claim race |
| WorkerEvent / WorkerReceipt | canonical contracts already exist | E + Live Lab | likely additive | `SCHEMA_VERSION_CONFLICT_PENDING_E` | preserve required identities; optional additions only unless explicit migration | seq/generation, task/lease continuity, authority const false |
| Outbox/emitter | expected E responsibility; final delta unavailable | Live Lab delivery | unresolved | `RUNTIME_CONFLICT_PENDING_E` | one durable emission path; delivery state is not research truth | persist/send crash, retry, duplicate, replay, ordering |
| Live Lab projection | existing native adapter is explicit-fact only | E runtime evidence | compatible if E remains factual | `GLOBAL_TRUTH_CONFLICT_IF_SYNTHETIC` | keep unsupported facts UNKNOWN; worker inactivity != global queue idle | stale/UNKNOWN/replay; queue proof required for global idle |
| Global STATE/config/registries | all lanes may imply changes | canonical integrator owns final truth | intentionally not sibling-owned | `GLOBAL_TRUTH_CONFLICT` | reconcile only in canonical Convergence #2 | exact-head integrated docs/config/tests |
| Authority flags | all current observed B/D0 code keep economic/prospective/capital/trading false | C0/E unavailable | must remain identical | `AUTHORITY_CONFLICT_ON_ANY_TRUE` | fail integration immediately on unexpected TRUE | recursive config/task/receipt/manifest scan; no outcomes accessed |
| UNKNOWN semantics | B and D0 preserve UNKNOWN materially | C0/E unavailable | must remain | `STATE_MACHINE_CONFLICT_IF_COERCED` | never coerce missing evidence to negative/zero/idle/profitable | seam round trips with UNKNOWN |

## Base-repair intersection analysis

The sealed-base repair `97165db2… -> 2b99d8ae…` touches exactly three paths:

1. `research/research_os/legacy/LEGACY_RESEARCH_LEDGER.imported.json`;
2. `research/research_os/tests/test_economic_identity_portfolio_readiness.py`;
3. `research/research_os/tests/test_economic_readiness_integration.py`.

Observed B delta touches none of those paths.
Observed D0 delta touches none of those paths.

Therefore:

`TEXTUAL_BASE_REPAIR_CONFLICT_B=FALSE`

`TEXTUAL_BASE_REPAIR_CONFLICT_D0=FALSE`

But textual compatibility is not sufficient. D0's implementation embeds the old Wave2 base SHA in `research/research_os/expansion/economic_lifecycle.py`; its refs and validation semantics therefore require an intentional base-pin change plus requalification.

## Current contract-change decision

`CONTRACT_CHANGE_REQUIRED=TRUE_FOR_D0_BASE_REBIND`

This is **not** authorization to redesign W1 ECON or D0 lifecycle semantics. The required change is a local identity pin repair so D0-generated `EconomicIdentityRef`, `PortfolioReadinessRef`, shadow contract identity and downstream hashes bind to the actually sealed Wave2 base.

For B, no code-level immutable-base constant has been observed in its core discovery files; its current known requirement is sealed-base content inclusion plus requalification.

## Highest-risk unresolved zones

1. **C0 missing**: B -> C0 -> Economic subject/freeze/verdict contract cannot be finalized.
2. **E missing**: scientific eligibility -> operational task admission and runtime/recovery/Live Lab chain cannot be finalized.
3. **Multi-Source missing**: ideation/source provenance -> B seam remains spec-only.
4. **D0 old base pin**: local FINAL is not directly canonical-portable until pin is repaired to `2b99d8ae…` and exact-head tests rerun.

## Authority

`ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE`

`PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE`

`REAL_CAPITAL_AUTHORIZED=FALSE`

`LIVE_TRADING_AUTHORIZED=FALSE`

`OUTCOME_ACCESSED=FALSE`
