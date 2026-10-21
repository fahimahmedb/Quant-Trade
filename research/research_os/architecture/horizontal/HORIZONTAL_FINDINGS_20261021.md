# Horizontal findings — Phase A

BASE_SHA=01c2e520fa4116645870f96acf6770ea83f1881c
NORTH_STAR_BLOB=a328b4e6d7d71dafd532938888ebf9818b1b610f

The Owner's current mission overrides historical routing and campaign names.
In particular, older files named `wave2_hardening`, `wave3_engine_depth` or
`wave4_acquisition_firewall` are existing source evidence, not qualification of
the upcoming MEGA B/C0/D0/E and Multi-Source packages.

## Current horizontal omissions repaired

### H001 — legitimate FAILED task class absent from queue accounting

Classification: CURRENT_REQUIRED_CAPABILITY. Owner: HORIZONTAL. Status: REPAIRED.
Module: task / queue accounting.

The current `contracts/research-task.schema.json` permits FAILED alongside
READY, CLAIMED, BLOCKED, COMPLETE and CANCELLED. `queue_summary` accounted for
every other canonical state, plus historical KILLED, but omitted FAILED. A
singleton FAILED queue reported task_count=1, active_count=0, terminal_count=0.
The existing queue observer could not account for this legitimate contract class.

Repair: include FAILED in the existing terminal-state set. Legitimate followup
remains possible; no historical result, task or authority is rewritten. The
contract-enumeration test checks every canonical state; a separate followup test
checks FAILED does not stop ordinary research continuation.

### H002 — unknown queue class had no accounting or fail-closed refill disposition

Classification: CURRENT_REQUIRED_CAPABILITY. Owner: HORIZONTAL. Status: REPAIRED.
Module: task / queue state and empty-queue stewardship.

North Star §§5, 12 and 15 require blockers, explainable scheduling, factual state
and fail-closed missing assumptions. The existing queue module had no unknown
state bucket or unsupported-state refusal. A queue containing UNKNOWN or an
unrecognized future state was treated as empty and derived a new task.

Repair: add `unknown_count` to the existing summary and return
`BLOCKED_UNKNOWN_TASK_STATUS` with no task from the existing refill function.
Missing status receives the same disposition. This concerns absent input-class
and output-disposition coverage, rather than parser stress or a field lost at an
inter-module handoff. Known active work can still be selected; this guard applies
to a refill decision, not a global cancellation or stop command. Inactive
frontiers retain their existing no-op disposition and still expose the count.

The existing worker persists the refusal in `runtime/worker_wakes/`. Tests exercise
the helper, real disposable Git worker persistence/restart/correction and the real
V2 source-aware refill path. No model call, source acquisition or economic action
is required to prove this surface. A later recognized-state correction permits
normal continuation. No new scheduler, state registry or wake mechanism exists.

## Future and deferred capability ledger

| ID | Module / capability | Classification | Evidence and Phase-A disposition | Phase-B recheck |
| --- | --- | --- | --- | --- |
| F001 | Research Intelligence: broad search intelligence, diversity, richer NO_ACTION receipts | FUTURE_WAVE2_CAPABILITY | Current frontier, source planner, priority sidecars and idle receipts exist. Those do not establish complete MEGA A intelligence. Separate convergence is in progress. | Inspect the integrated intelligence contracts and their actual producers/consumers, including no-action states. |
| F002 | Multi-Source ideation intake | FUTURE_WAVE2_CAPABILITY | Qualified single-packet sources and adapters exist. Multiple records inside one capture are not a unified multi-source ideation capability. | Review source classes, ambiguity/conflict/blocked dispositions and intake receipts. |
| F003 | MEGA B: broad Quant/mechanism discovery | FUTURE_WAVE2_CAPABILITY | Quant engine and candidate extension exist; source-aware planner explicitly returns NO_ADMISSIBLE_DOCUMENTARY_SOURCE for the present real Quant catalog. | Require an admissible producer path and consumer recognition for each promised source/mechanism family. |
| F004 | MEGA B: event novelty and fundamental mispricing | FUTURE_WAVE2_CAPABILITY | Accounting/distribution transforms and falsifiable dossiers exist. Valuation, expectations, novelty and mispricing often remain UNKNOWN/PARTIAL. Favorable facts alone do not establish edge. | Enumerate intended economic thesis families and evidence prerequisites, beyond stylistic dossier variants. |
| F005 | MEGA B: forced flows beyond rule existence | FUTURE_WAVE2_CAPABILITY | Operative rule and nonbinding FAQ are distinguished; actor pressure, eligible population, quantity, instrument and payoff remain unresolved. | Require actual qualified flow premises and retain RULE_EXISTS != FORCED_FLOW. |
| F006 | MEGA C0: scientific semantic adjudication | FUTURE_WAVE2_CAPABILITY | Native independent reconstruction and distinct-process/source checks exist. Policy explicitly limits PASS to deterministic R0 and semantic diverse review to NOT_PROVEN. | Check complete adjudication dispositions, independence evidence and no-admissible-review behavior. |
| F007 | MEGA D0: economic lifecycle and replacement lineage | FUTURE_WAVE2_CAPABILITY | Structural identity/portfolio and inactive decay guard exist; active decay mechanisms and replacement lineage are not established. | Enumerate park/retire/replace/reopen lineage and decay input/output families. |
| F008 | MEGA E: final runtime task operations | FUTURE_WAVE2_CAPABILITY | Leases, permissions, retries, model/resource bounds and terminal task representation exist. CANCELLED is represented; no cancellation producer/command was established in this review. | Check cancellation/expiry/no-work/block/fault durable transitions; do not infer a producer from an enum. |
| F009 | MEGA E: outbox and recovery breadth | FUTURE_WAVE2_CAPABILITY | Current native observer persists PENDING/ACK/error evidence and retries identical packets in-session. It deliberately does not replay old starts after lease loss; it is not a full restart outbox. | Check new lifecycle delivery/reconciliation surfaces while preserving scientific lease and observation boundaries. |
| F010 | MEGA E: truthful whole-lifecycle Live Lab | FUTURE_WAVE2_CAPABILITY | Native mapper/reducer, unknown progress, source-scoped blockers and receipts are tested. Full production lifecycle projection is not established by these tests. | Recheck UNKNOWN/BLOCKED and every new durable disposition against real producer state. |
| D001 | Scientific Memory historical completeness | INTENTIONALLY_DEFERRED | CP079-first convergence is separately integrating this capability. Pinned imported ledger and scoped reviews are present; unrecovered primary provenance remains partial. No convergence merge is allowed here. | Re-evaluate recovered negative/blocked/unexecuted/protocol-invalid/insufficient-positive classes against final memory. |
| D002 | Data / Evidence / PIT / SEC census completeness | INTENTIONALLY_DEFERRED | Raw-byte capture, route clocks, source versioning and availability exist. Separate convergence/source imports remain owned elsewhere. Missing permission or dataset is not invented. | Check qualified source classes, effective/publication/availability/revision clocks, unavailable/ambiguous state and actual consumers. |
| D003 | Factory geometry, power/MDE and evidence firewall convergence | INTENTIONALLY_DEFERRED | Frozen protocol and deterministic runner exist. CP085 preserves Factory source-import-required disposition. Actual cohort/calendar/effect premises are not supplied by a generic calculator. | Review integrated cohort/power/column-lineage surface with its admissibility and missing-premise states. |
| D004 | Economic convergence | INTENTIONALLY_DEFERRED | Frozen declarations and documentary support ceilings are present. Separate Economic convergence is not merged or superseded by this branch. | Re-evaluate identity/portfolio/lifecycle contracts on the exact integrated result. |
| D005 | Prospective/economic outcome ingestion, evaluation, empirical portfolio metrics and active decay | INTENTIONALLY_DEFERRED | Four Owner authorities remain FALSE. Registration/denial/export/feedback guards are represented and tested; active economic capability is not qualified. | Inspect surface existence without opening authority or constructing economic truth. |
| D006 | Real capital, broker orders and live trading | INTENTIONALLY_DEFERRED | Existing V1 fixture Desk/Fills/Book surfaces are preserved. No current V2 economic dispatch or broker execution is authorized. | Maintain separate authority domains; Wave-2 integration alone grants nothing. |
| D007 | Production release, VM/Site/D1/SSE/reboot qualification | INTENTIONALLY_DEFERRED | Source review and disposable regressions only. No host deployment or live service mutation forms part of this mission. | Qualify operationally only under its own authorized mission. |
| HST001 | CP081/CP084 documentary/frozen declaration handoff repairs | HISTORICAL_ONLY | Both fixes are already in the immutable base and have executable regression evidence. | Diagnostic history; do not blindly cherry-pick or re-emit as current defects. |
| U001 | Starvation aging / measured global VOI allocation | UNKNOWN_OWNERSHIP | Current V2 source labels starvation DISABLED and resource costs UNIFORM_DECLARED_UNIT_NOT_MEASURED. North Star requires explainable priorities/budgets, not a specific fairness/VOI algorithm. No present omission is proved. | Resolve against actual Wave-2 specification; do not invent an allocator. |

## Cross-axis boundary record

VERTICAL_FINDINGS=0_NEW_CONFIRMED
LONGITUDINAL_FINDINGS=0_NEW_CONFIRMED

This is not a clean bill of health on either axis. Existing parsers, leases,
freeze checks, recovery and handoffs were inspected only to establish surface
presence. No new reproduced deep robustness defect or semantic handoff defect
was established. CP081/084 are historical fixed handoff evidence. Concurrency
stress, exhaustive malformed nesting, fault combinations and final integrated
handoff semantics are outside this rail. Future/deferred entries are not emitted
as current cross-axis defects.

## Phase-B handoff law

Wait for an explicit `WAVE2_INTEGRATED_SHA` from the Owner, meaning the qualified
result after B/C0/D0/E, Multi-Source, convergence #2, cross-lane bindings and full
regression. Start a **new** branch from that exact SHA. Reacquire the architecture
and reclassify every row/finding. Do not rebase this branch, merge convergence or
blindly cherry-pick H001/H002. The final implementation may already cover them
through different task contracts.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
