# WAVE 2 — CONVERGENCE #2 READINESS BOARD

Foreman role: parallel pre-convergence accelerator only. This document is diagnostic preparation, not canonical integration truth.

## Campaign/base evidence

- Owner-supplied observed campaign anchor: `97165db2faa3300cef1f23de0045ed93d25eb9cb`.
- Observed branch `builder/convergence-cp079-wave2-base-20261021` points to that SHA.
- Formal immutable-base seal manifest: **not reacquired/proven at this checkpoint**.
- Therefore: `FORMAL_WAVE2_IMMUTABLE_BASE_SHA=UNPROVEN_SEAL`.
- North Star blob identity reacquired: `a328b4e6d7d71dafd532938888ebf9818b1b610f`.

No sibling head is called FINAL merely because a branch exists or has moved.

## Readiness board

| Lane | Branch | Base | Observed head | Final head | Status | safe_to_integrate | Contracts mapped | Conflicts known | Fixtures ready | Binding plan ready | Focused tests ready | Blockers | Canonical integration readiness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Multi-Source | expected `builder/multi-source-ideation-intake-20261021`; exact ref unresolved | UNKNOWN | NOT_FOUND | UNAVAILABLE | BLOCKED_EXTERNAL | FALSE | PARTIAL_FROM_EXPECTED_SEAM_ONLY | UNKNOWN | SPEC_ONLY | PARTIAL | SPEC_ONLY | exact branch/head/final manifest absent | NOT_READY |
| MEGA B | `builder/mega-b-discovery-engine-20261021` | `97165db2…` | `2669f973887dde95451cecdb1a0e0f9ad9fa8c8a` | UNAVAILABLE | MOVING | FALSE | YES_CP001_PLUS_BASE | Candidate/C0/runtime membrane risks mapped | SPEC_ONLY | YES_PROVISIONAL | SPEC_ONLY | implementation/final qualification absent | NOT_READY |
| MEGA C0 | `builder/mega-c0-scientific-adjudication-20261021` | `97165db2…` | `97165db2faa3300cef1f23de0045ed93d25eb9cb` | UNAVAILABLE | MOVING | FALSE | BASE_ONLY | Candidate/freeze/verdict/D0 seams unresolved | SPEC_ONLY | YES_PROVISIONAL | SPEC_ONLY | no observed semantic delta/final manifest | NOT_READY |
| MEGA D0 | `builder/mega-d0-economic-lifecycle-20261021` | `97165db2…` | `e9268c89c3307e47b810add2719d1c1c76df8a44` | UNAVAILABLE | MOVING | FALSE | YES_CP001_PLUS_BASE | C0→economic/lifecycle state risk mapped | SPEC_ONLY | YES_PROVISIONAL | SPEC_ONLY | implementation/final qualification absent | NOT_READY |
| MEGA E | `builder/mega-e-autonomous-runtime-20261021` | `97165db2…` | `97165db2faa3300cef1f23de0045ed93d25eb9cb` | UNAVAILABLE | MOVING | FALSE | BASE_RUNTIME_ONLY | task/scheduler/global-truth/runtime ownership high risk | SPEC_ONLY | YES_PROVISIONAL | SPEC_ONLY | no observed semantic delta/final manifest | NOT_READY |

All observed sibling heads above are `PROVISIONAL_HEAD` unless a durable sibling final manifest later proves otherwise.

## LANE_CONTRACT_MAP — Multi-Source

- lane: `MULTI_SOURCE_IDEATION_V2`
- observed_head: `NOT_FOUND`
- head_status: `BLOCKED_EXTERNAL / REF_UNRESOLVED`
- base_sha: `UNKNOWN`
- input contracts: expected Research Intelligence decision/context + qualified documentary/source facts; exact contract unresolved
- output contracts: expected ideation object/state carrying `ELIGIBLE_FOR_DISCOVERY`; exact schema unresolved
- shared contracts touched: source identity/provenance, context snapshot, scientific memory refs, discovery admission boundary
- new schemas / modified schemas / enums: `UNKNOWN`
- identity fields: exact semantics unresolved; must preserve stable source/idea identity and context snapshot identity
- provenance fields: must preserve source claim/document lineage; exact fields unresolved
- authority fields: must not create operational `READY`; all economic/prospective/capital/trading flags remain false
- persistence surfaces: expected Proposal/Ideation ledger surfaces, exact paths unresolved
- global files touched: `UNKNOWN`
- runtime surfaces touched: none are allowed merely by scientific eligibility
- tests introduced: unknown
- known blockers: exact branch/head and durable final manifest unavailable
- expected downstream consumers: MEGA B discovery intake

## LANE_CONTRACT_MAP — MEGA B

- lane: `MEGA_B_DISCOVERY_ENGINE`
- observed_head: `2669f973887dde95451cecdb1a0e0f9ad9fa8c8a`
- head_status: `PROVISIONAL_HEAD / MOVING`
- base_sha: `97165db2faa3300cef1f23de0045ed93d25eb9cb`
- input contracts: Research Intelligence decisions/context; future Multi-Source discovery-eligible intake; Scientific Memory refs; qualified evidence/provenance
- output contracts: canonical `Candidate` in `research/research_os/engines/protocol.py`, with planned additive discovery metadata rather than a second Candidate dialect
- shared contracts touched: Candidate identity, source lineage, mechanism identity, clocks, ancestry/duplicate identity, implementability metadata
- new schemas / modified schemas / enums: none implemented at observed CP001
- identity fields: canonical `hypothesis_id`, `generation_id`, mechanism, source refs; planned ancestry/duplicate identity
- provenance fields: existing source refs/document evidence plus planned source/evidence clocks
- authority fields: no outcome access, no operational task admission, no capital/trading authority
- persistence surfaces: not implemented at observed head
- global files touched: CP001 handoff only
- runtime surfaces touched: none implemented; future scientific outputs must not bypass Control Plane
- tests introduced: none yet
- known blockers: implementation and final qualification absent; exact Multi-Source producer contract unresolved
- expected downstream consumers: MEGA C0 / protocol freeze; Control Plane only through explicitly authorized operational handoff rules

## LANE_CONTRACT_MAP — MEGA C0

- lane: `MEGA_C0_SCIENTIFIC_ADJUDICATION`
- observed_head: campaign anchor
- head_status: `PROVISIONAL_HEAD / MOVING`
- base_sha: `97165db2faa3300cef1f23de0045ed93d25eb9cb`
- input contracts: canonical Candidate-like input, Factory freeze/registry/trial semantics
- output contracts: expected provenance-preserving scientific disposition/verdict bound to exact frozen subject
- shared contracts touched: Candidate, experiment identity, protocol hash, Validator, Red Team, verdict provenance, uncertainty, trial/epoch identity
- new schemas / modified schemas / enums: `UNKNOWN`
- identity/provenance/authority/persistence/global/runtime surfaces: final delta not yet observable
- tests introduced: none observed
- known blockers: no semantic delta/final manifest available
- expected downstream consumers: Economic Identity / Portfolio Readiness and MEGA D0

## LANE_CONTRACT_MAP — MEGA D0

- lane: `MEGA_D0_ECONOMIC_LIFECYCLE`
- observed_head: `e9268c89c3307e47b810add2719d1c1c76df8a44`
- head_status: `PROVISIONAL_HEAD / MOVING`
- base_sha: `97165db2faa3300cef1f23de0045ed93d25eb9cb`
- input contracts: existing `economic_identity_v1` + canonical portfolio readiness/diagnostics; exact Candidate/economic-identity binding
- output contracts: planned lifecycle kernel for shadow/prospective contract identity, observation identity, decay evidence, review state, resize/park/retire/replacement lineage
- shared contracts touched: `EconomicIdentityRef`, `PortfolioReadinessRef`, forward readiness, decay guard, scientific subject binding
- new schemas / modified schemas / enums: none implemented at observed CP001
- identity fields: candidate binding, hypothesis/generation, economic structural identity; planned immutable prospective observation identity and predecessor/successor ancestry
- provenance fields: existing economic/candidate provenance; future lifecycle evidence must retain source and verdict provenance
- authority fields: prospective observation remains not authorized; no outcomes; no capital/trading
- persistence surfaces: existing `forward_register`/`decay_guard` are upstream starting surfaces; implementation not yet present
- global files touched: CP001 handoff only
- runtime surfaces touched: review cadence metadata must not become scheduler ownership
- tests introduced: none yet
- known blockers: C0 output contract and D0 implementation/final qualification absent
- expected downstream consumers: later owner-authorized prospective lifecycle/evaluation machinery, not current outcome creation

## LANE_CONTRACT_MAP — MEGA E

- lane: `MEGA_E_AUTONOMOUS_RUNTIME_RECOVERY_LIVE_LAB`
- observed_head: campaign anchor
- head_status: `PROVISIONAL_HEAD / MOVING`
- base_sha: `97165db2faa3300cef1f23de0045ed93d25eb9cb`
- input contracts: admitted operational `ResearchTask`, Control Plane routing/capabilities/authority, durable task/lease state
- output contracts: WorkerEvent, WorkerReceipt, task progress/completion, outbox/emitter/replay projection, Live Lab factual state
- shared contracts touched: `research-task.schema.json`, worker event/receipt schemas, `CONTROL_PLANE.json`, `CAPABILITY_REGISTRY.json`, `WORKFLOW_LANES.json`, `RESEARCH_FRONTIER.json`, Oracle/runtime state, Live Lab mapper
- new schemas / modified schemas / enums: `UNKNOWN` until E moves
- identity fields: `task_id`, task lineage, lease generation, worker/session/action/event/receipt identities
- provenance fields: input head, output commit, evidence refs, event source refs
- authority fields: operational worker launch may be authorized; economic experiment/prospective observation/real capital/live trading remain false
- persistence surfaces: tasks, events, receipts, runtime registry/control files; exact E delta unknown
- global files touched: expected high-risk surface; no delta observed yet
- runtime surfaces touched: broad; Oracle, queue, leases/retries, events/receipts/outbox/Live Lab
- tests introduced: none observed
- known blockers: no semantic delta/final manifest; must not create second scheduler/task/authority registry
- expected downstream consumers: Oracle workers and factual Live Lab projection

## Canonical base contract pins

### Scientific object

The existing `Candidate` remains the shared scientific producer contract. Its required core fields are `hypothesis_id`, `generation_id`, `mechanism`, `claim`, `falsification_scope`, `decision_map`, and `economic_tags`; source refs/evidence and no-observation authority state already exist. B must extend this representation additively or provide an explicit migration, not fork it.

### Experiment/freeze

The existing Factory/final-shape path already freezes candidate expression and protocol identity, tracks protocol hash/generation, preserves `outcome_opened=false`, and produces economic identity/portfolio readiness surfaces. C0/D0 must consume or additively extend these semantics.

### Operational task authority

The canonical Research OS contract is `research/research_os/contracts/research-task.schema.json`, whose status set is `READY | CLAIMED | BLOCKED | COMPLETE | FAILED | CANCELLED` and whose task embeds authority and lease state. `READY` is therefore an operational queue status, not a scientific eligibility label.

The current control plane makes `control_integrator` the sole empty-queue steward; it may derive at most one deterministic frontier-backed READY task only after a fresh global proof that no READY or CLAIMED work exists. An explicitly-authorized current task may create its exact downstream handoff. No other scientific state creates READY by implication.

### Runtime evidence

Canonical runtime evidence contracts already exist for WorkerEvent and WorkerReceipt. Worker events require event/session/worker/action identity, sequence/generation and payload. Worker receipts bind task/session/lease/input head, terminal status, artifacts/evidence and hard false authority assertions.

### Live Lab

The current native adapter maps only explicit supported WorkerEvent facts, keeps progress unknown unless proved, does not infer roles/identity/economic results, and carries event evidence refs. MEGA E must adapt this factual projection rather than create animated/synthetic truth.

## Global file ownership map

| Surface | Classification | Reason |
|---|---|---|
| sibling-local CP/final handoffs | DOCUMENTARY_ONLY | evidence, not integrated global truth |
| module-local additive implementation/tests | SIBLING_CAN_OWN | provided shared contracts/invariants are respected |
| `STATE.md`, architecture/runtime status docs | INTEGRATOR_MUST_OWN | one integrated system truth |
| `research/research_os/runtime/CONTROL_PLANE.json` | INTEGRATOR_MUST_OWN | shared authority/routing/task-admission truth |
| `CAPABILITY_REGISTRY.json` | INTEGRATOR_MUST_OWN | shared capability/authority registry |
| `WORKFLOW_LANES.json` | INTEGRATOR_MUST_OWN | shared workflow/state-machine ownership |
| `RESEARCH_FRONTIER.json` | INTEGRATOR_MUST_OWN | owner-governed operational work source |
| canonical task/event/receipt contracts | INTEGRATOR_MUST_OWN | shared runtime protocol |
| schema indexes / generated exports | GENERATED_AT_CONVERGENCE | regenerate from integrated head only |
| integrated Wave-2 manifest | GENERATED_AT_CONVERGENCE | canonical integrator only |
| Live Lab global projection/binding configuration | INTEGRATOR_MUST_OWN | one factual operational truth |

## Current canonical blockers

1. Formal Wave-2 immutable-base seal is not proven.
2. Multi-Source exact branch/head/final manifest is unresolved.
3. No lane has a reacquired durable `FINAL_QUALIFIED` manifest.
4. B and D0 have documentary CP001 only and explicitly are not safe to integrate yet.
5. C0 and E have no observed delta beyond the campaign anchor.
6. Shared Candidate/freeze/verdict/lifecycle contracts cannot be acceptance-tested against final implementations yet.
7. E's final relationship to existing Research OS Control Plane, canonical ResearchTask and legacy `src/autonomous_research` scheduler must be explicitly resolved without creating a second scheduler/queue/authority registry.

## Authority status

`ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE`

`PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE`

`REAL_CAPITAL_AUTHORIZED=FALSE`

`LIVE_TRADING_AUTHORIZED=FALSE`

`OUTCOME_ACCESSED=FALSE`

`READY_FOR_CANONICAL_CONVERGENCE2=FALSE`
