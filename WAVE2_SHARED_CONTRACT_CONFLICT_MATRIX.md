# WAVE 2 — SHARED CONTRACT CONFLICT MATRIX

`WAVE2_SHARED_CONTRACT_CONFLICT_MATRIX`

Foreman-only preparation evidence. No sibling is merged here, no canonical global truth is emitted, and no `WAVE2_INTEGRATED_SHA` is authorized.

Formal base observed: `2b99d8aeb8a342f1ef32544247d366cb8a26037e`.

Base status: **formal base observed, seal unproven**. Historical sibling start: `97165db2faa3300cef1f23de0045ed93d25eb9cb`.

## Conflict matrix

| Contract / surface | Owners touching it | Base representation | Lane A delta | Lane B / consumer delta | Compatibility | Conflict class | Recommended resolution | Canonical owner | Required tests |
|---|---|---|---|---|---|---|---|---|---|
| Wave-2 base lineage | base convergence; all lanes | `2b99…` branch head, parent `97165…` | Multi/E directly use `2b99…` | B/C0/D0 were qualified from `97165…` | divergent lineage, semantic deltas largely additive | `GLOBAL_TRUTH_CONFLICT` | semantic-port B/C0/D0 deltas onto `2b99…`; never rebase siblings; rerun focused + seams + full suite | canonical Convergence #2 | ancestry, exact-base, base-repair preservation, exact-head qualification |
| Immutable-base seal truth | base owner / canonical integrator | no durable standalone seal found by foreman | sibling prose sometimes calls `2b99…` sealed | foreman search found no canonical `WAVE2_IMMUTABLE_BASE_SHA` artifact | unresolved authority truth | `GLOBAL_TRUTH_CONFLICT` | canonical owner must publish/identify durable seal; foreman remains `UNPROVEN` | canonical base owner | exact seal artifact + SHA/ref equality |
| Multi-Source final identity | Multi | manifest on `2b99…` | substantial implementation at `c003dd97…` | downstream B acceptance | semantics visible, seal intentionally pending | `UNKNOWN` | wait for exact-head CI/final manifest; do not infer final from volume of commits | Multi lane | exact-head manifest, clean tree, CI, authority/outcome scan |
| Source identity | source planner / Multi / RI | source ref + content/packet/record/blob identity + clocks | Multi source claims/context snapshot | B consumes lineage | additive if content identity is preserved | `SEMANTIC_OVERLAP` | preserve exact content/provenance identity; path/URL count is never novelty | source planner + producer contract | rename/copy, hash mismatch, stale revision, duplicate-content tests |
| IdeationSourceClaim | Multi | none as scheduler lease | passive atomic source claim | B consumes provenance only | compatible if never promoted to lease/task | `AUTHORITY_CONFLICT` if conflated | keep source claim passive and context-bound | Multi | no queue/lease mutation; same-source concurrency; transfer/reuse tests |
| Proposal Ledger | Multi / existing research law | scientific proposal lineage | passive idempotent/restartable ledger | RI/B consume scientific provenance | compatible if no queue semantics | `OWNERSHIP_CONFLICT` if used as queue | retain one scientific ledger and canonical task queue separately | Multi scientific owner / Control Plane operational owner | crash/restart, collision, no-queue tests |
| `ELIGIBLE_FOR_DISCOVERY` | Multi | no operational meaning | terminal scientific eligibility | B intake | compatible | `NO_CONFLICT` | pure deterministic intake validation only | Multi→B seam | no READY/task creation; stale/context/provenance tests |
| Research Intelligence decision | RI | canonical action/identity/memory screening | Multi reuses RI | B requires scheduler-neutral executable `RUN_PRODUCER` | compatible | `NO_CONFLICT` | no proposal→B shortcut around RI where RI qualification is required | RI | wrong action blocks; identity UNKNOWN not novelty |
| Candidate | canonical protocol / B / C0 | one canonical Candidate | B enriches discovery facts | C0 binds exact candidate snapshot/hash | additive but high-risk | `SEMANTIC_OVERLAP` | preserve one Candidate; C0 uses link/ref, not second dialect | canonical Candidate owner | round-trip identity, mutation/new generation, duplicate-expression, UNKNOWN |
| Candidate state vs task state | B / Control Plane | scientific and operational state machines distinct | B `DRAFT/VALIDATING/ADMISSIBLE/...` | runtime task `READY/CLAIMED/...` | must stay disjoint | `STATE_MACHINE_CONFLICT` if mapped directly | explicit membrane: scientific admission != operational admission | canonical integrator + Control Plane | prove B/Multi/C0 cannot create task READY |
| PIT/source clocks | Data/PIT / B / C0 | canonical public/available/effective/freeze timing | B retains clocks/conflicts | C0 cross-examines timing | compatible if exact facts retained | `SEMANTIC_OVERLAP` | consume refs; never recalculate divergent truth silently | Data/PIT canonical owner | exact clock retention; conflicting/missing clock remains BLOCK/UNKNOWN |
| Implementability | existing implementability law / B / C0 | canonical assessment | B reuses assessment | C0 consumes assumptions/gaps | compatible | `NO_CONFLICT` | no parallel registry | canonical implementability owner | exact receipt/ref; NOT_READY not coerced |
| Experiment/freeze identity | W1 Factory / C0 | registry/freeze/trial accounting/outcome firewall | B hands Candidate toward Factory | C0 exact-binds protocol/frozen hashes | compatible if C0 composes only | `OWNERSHIP_CONFLICT` if rebuilt | Factory remains canonical; C0 references exact frozen identity | W1 Factory | mutation→new generation; protocol/freeze drift blocks |
| Validator | canonical Validator / C0 / W1 ECON | independent validation readiness | C0 composes exact Validator ref | W1 ECON consumes/retains economic veto | risk of duplicate adjudication | `OWNERSHIP_CONFLICT` | one Validator truth; C0 cannot create competing validator | canonical Validator owner | producer != validator; missing validator = BLOCK; outcome firewall |
| Red Team | canonical Red Team / C0 / W1 ECON | negative-rights/blocking law | C0 composes Red Team | W1 ECON retains economic checks | compatible if negative rights preserved | `SEMANTIC_OVERLAP` | no self-issued negative evidence; Red Team blocker cannot alone produce KILL | canonical Red Team owner | blocker semantics, repair prohibition, no outcomes |
| Scientific disposition | C0 | no runtime authority | `PROMOTE/PARK/KILL/BLOCK` exact-subject disposition | W1 ECON consumes upstream science | compatible after base replay | `SEMANTIC_OVERLAP` | one exact-subject scientific receipt; preserve uncertainty/negative scope | C0 scientific owner; integrator binds | Candidate/protocol/ref tamper, UNKNOWN, BLOCKED!=FAILED |
| Semantic vs structural independence | C0 / upstream independence | structural reconstruction distinct from semantic review | C0 hardened confirmation counting | downstream economic layer must not overclaim | compatible | `NO_CONFLICT` after qualified hardening | retain distinct booleans/count law | C0/upstream independence | no-overclaim + explicit semantic-proof tests |
| EconomicIdentityRef | W1 ECON / D0 | canonical 12-dimension economic identity | C0 only promotes toward it | D0 consumes ref | compatible; D0 old-base pin exists | `IDENTITY_CONFLICT` on stale base pin | W1 ECON remains owner; rebind D0 base identity only | W1 ECON | exact ref hash, candidate-generation binding, W1 non-regression |
| PortfolioReadinessRef | W1 ECON / D0 | canonical structural portfolio readiness | C0 does not create it | D0 consumes ref | compatible | `NO_CONFLICT` after base replay | no D0 rebuild | W1 ECON | readiness hash exactness; empirical layer remains sealed |
| D0 lifecycle state | D0 / E | no operational task equivalence | lifecycle/shadow/review states | E may execute canonical tasks invoking D0 | compatible only with namespace separation | `STATE_MACHINE_CONFLICT` if conflated | lifecycle readiness never means task READY | D0 + Control Plane boundary | no task mint; no prospective authority; cadence not scheduler |
| Forward register / Shadow Book | D0 | existing/extended economic lifecycle persistence | D0 hardens lifecycle | future runtime may project only factual state | additive | `PERSISTENCE_CONFLICT` if treated as runtime queue | keep lifecycle persistence separate from operational queue/outbox | D0 | restart/idempotency/ref integrity; no outcomes fabricated |
| ResearchTask identity | Control Plane / E | canonical task schema | science lanes provide no direct task authority | E consumes canonical task/lease | compatible | `AUTHORITY_CONFLICT` on any direct science→READY path | only authorized downstream handoff or deterministic empty-queue refill may create READY | Control Plane | exact authority payload, derivation key, max-one refill, no same-wake producer |
| Queue / lease registry | Control Plane / E | one canonical queue/lease law | no scientific owner | E uses canonical security-definer lease/RPC path | compatible | `OWNERSHIP_CONFLICT` if second registry | no second scheduler/queue/lease registry | Control Plane/E runtime owner | stale lease, claim/release, crash/reboot, no blind steal |
| Capability registry | Control Plane / E | canonical capabilities | science expresses requirements only | E enforces capabilities | compatible | `GLOBAL_TRUTH_CONFLICT` if sibling rewrites final registry | integrator owns final merged registry truth | canonical integrator | capability mismatch fail-closed |
| Events | E / Live Lab | canonical event identities | E durable runtime generation/events | Live Lab projects facts | additive | `RUNTIME_CONFLICT` if sequence/generation lost | preserve event_id/session/action/seq/generation | E runtime | duplicate/replay/order/generation tests |
| Receipts | E / Live Lab | canonical receipt + authority assertions | E durable receipt/outbox | Live Lab evidence projection | compatible | `RUNTIME_CONFLICT` if receipt not bound to lease/task | exact task/lease/session/artifact refs | E runtime | receipt tamper, authority const-false, replay |
| Outbox | E / emitter | delivery persistence | durable outbox | Live Lab delivery | compatible | `PERSISTENCE_CONFLICT` if delivery creates new fact | outbox retries are delivery, not scientific/runtime fact creation | E/emitter | retry idempotency, crash/recovery, duplicate suppression |
| Live Lab projection | E / Live Lab | factual projection only | E supplies durable facts | adapter must preserve UNKNOWN/stale | compatible | `GLOBAL_TRUTH_CONFLICT` if synthetic animation treated as fact | facts only; UNKNOWN preferred to false IDLE/progress | Live Lab canonical projection owner | stale/disconnect/reboot/replay; global IDLE proof |
| Global STATE/config/registries | all lanes / integrator | shared truth | siblings may imply changes | convergence must reconcile | intentionally non-sibling-owned | `GLOBAL_TRUTH_CONFLICT` | classify each as `INTEGRATOR_MUST_OWN` or generated at convergence | canonical integrator | exact integrated-head scans/regression |
| Authority flags | every lane | all FALSE | all observed manifests FALSE | runtime receipts must remain FALSE | required identical | `AUTHORITY_CONFLICT` on any TRUE | fail closed immediately | global invariant | recursive config/schema/manifest/runtime scan |
| UNKNOWN semantics | Memory/RI/Multi/B/C0/D0/E projection | explicit unknown | each lane must retain | consumers must not coerce | required identical | `STATE_MACHINE_CONFLICT` if coerced | preserve UNKNOWN end-to-end | cross-lane | round-trip UNKNOWN fixtures |

## Global-file ownership classification

### `SIBLING_CAN_OWN`

Lane-local engines, lane-local schemas/contracts, lane-local tests, lane-local qualification workflows and documentary manifests that do not assert global convergence truth.

### `INTEGRATOR_MUST_OWN`

Final merged `CONTROL_PLANE.json`, capability/workflow/global-status truth, canonical schema registry decisions, global authority truth, final cross-lane adapters where ownership would otherwise be ambiguous, and any final Wave-2 integration manifest.

### `GENERATED_AT_CONVERGENCE`

Integrated exact-head receipts, whole-system regression evidence, merged schema/generated-contract indexes, final conflict-resolution evidence, canonical port ledger and any `WAVE2_INTEGRATED_SHA` emission.

### `DOCUMENTARY_ONLY`

Foreman readiness boards, conflict matrices, binding/test/port plans, sibling CP/final notes and rehearsal receipts explicitly marked non-canonical.

## Exact-base conflict resolution law

B, C0 and D0 must **not** be rebased by the foreman. Canonical Convergence #2 must:

1. start from the formally authorized Wave-2 base after seal proof;
2. inspect each lane's exact semantic delta from `97165…`;
3. port only the qualified semantic delta;
4. preserve the `97165… → 2b99…` exact-base repair;
5. make D0's base-identity rebind explicit;
6. run lane-focused qualification;
7. run producer→consumer seam qualification;
8. defer global-truth reconciliation to the integrator;
9. run full exact-head regression only after all ports.

`CONTRACT_CHANGE_REQUIRED=D0_BASE_IDENTITY_REBIND_AND_ANY_NON_ADDITIVE_DISCOVERY_FOUND_DURING_PORT`

No other breaking shared-contract change is currently proven necessary.

## Unresolved conflict inventory

Material unresolved classes currently present:

1. `GLOBAL_TRUTH_CONFLICT` — durable immutable-base seal not independently proven.
2. `GLOBAL_TRUTH_CONFLICT` — B/C0/D0 qualified against historical parent rather than observed formal base.
3. `UNKNOWN` — Multi-Source exact final/CI seal pending.
4. `IDENTITY_CONFLICT` — D0 old base identity requires explicit rebind.
5. `SEMANTIC_OVERLAP` — Multi→B source/proposal/identity seam must be proven on final Multi head.
6. `SEMANTIC_OVERLAP` — B→C0 exact Candidate/freeze seam must be replayed on formal base.
7. `SEMANTIC_OVERLAP` — C0→W1 ECON→D0 exact scientific/economic subject binding must be replayed.
8. `GLOBAL_TRUTH_CONFLICT` — no canonical whole-chain integrated exact head exists yet.

## Authority

`ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE`

`PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE`

`REAL_CAPITAL_AUTHORIZED=FALSE`

`LIVE_TRADING_AUTHORIZED=FALSE`

`OUTCOME_ACCESSED=FALSE`

`WAVE2_INTEGRATED_SHA_EMITTED=FALSE`
