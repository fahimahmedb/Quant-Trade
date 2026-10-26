# Phase-A module coverage and limits

Base: `01c2e520fa4116645870f96acf6770ea83f1881c`.
North Star: blob `a328b4e6d7d71dafd532938888ebf9818b1b610f`.

This inventory uses the 25 existing nodes in the base's CP085 coverage index as
a routing map, with the existing scientific snapshot ledger explicitly itemized
as an additional row in CP017. It does **not** inherit that index's Q labels as vertical depth
qualification. All mapped tests were executed locally, along with the new
vertical adversaries. No current capability is declared universally D3/D4 from
aggregate green test counts. New depth counts in the final manifest refer only
to the 18 explicit capability units below the table.

| Existing module/node | Reacquired implementation and executed evidence | Phase-A finding/depth boundary |
| --- | --- | --- |
| Owner/governance | v2_core/v2_state; epoch blinding, policy/preflight, membrane suites | CP002 guards; CP010 optimizer-safe denial. Authentication/transport and policy-change races unproven. |
| Control/clock | local runtime, GitHubStateStore, native worker; oracle_worker/scheduler and V2 worker tests | CP007/CP015 local clocks, stale/terminal fencing and shared-instance publication recovery. Existing real local-Git lease races, expiry, owner rewind, lost ACK and restart tests pass. Local selection/claim is not atomic. No production reboot proof. |
| Data/research | evidence, identity, source qualification, source-PIT clocks, raw-capture/admission suites | CP003 concurrent evidence/index and exact references; CP009 action boundaries. Vendor/source truth and all identity interval conflicts unproven. |
| Data/control recovery | Quant clock dependency recovery and V1 data-validation suites | Existing durable BLOCK/recovery behavior regressed. No new live capture or outage experiment. |
| Scientific memory snapshots | scientific_store; CP017 alias, malformed chain, threaded append and atomic publication/retry tests | D3 for same-instance scientific hash ledger; public entries, independent publishers and authenticated rollback anchoring unproven. |
| Canonical research core | v2_core, canonical depth, persistent state, freeze/trial accounting suites | CP002 serialized reconstruction repaired; durable freeze/immutable registry cases regressed. Full concurrent epoch lifecycle unproven. |
| Producer families | engines/builtin/protocol, documentary dossiers; multi-engine, primary-event, operative-rule, independent-reconstruction suites | Existing four-family contracts and claim ceilings regressed. Semantic creativity/economic validity unproven; no missing-family implementation. |
| Archaeology/search | Legacy knowledge base, archaeology; canonical-spine and historical-source recovery suites | Pinned imported ledger materialized and blob verified. Historical scope, negative/blocked distinctions regressed. Unrecovered provenance remains unresolved. |
| Early implementability | implementability_depth and contract/readiness suites | Existing tri-state and declaration blockers regressed. Complete liquidity/cost/capacity truth for real candidates unproven. |
| Experiment infrastructure | experiment_runner/persistent_state; freeze bindings, receipt, frozen-input and execute/replay suites | Immutable PREPARED/COMPLETED, tamper/replay and denial cases pass. Concurrent whole-scientific freeze/physical crash coverage incomplete. |
| Native trial/challenge | native trial lineage and canonical-freeze binding suites | Candidate/epoch/generation/trial negative controls pass. No new cross-lane binding or future adjudication work. |
| Cross-examination | engines/cross_exam and native independent-challenge suites | Existing source/structure challenge regressed. Diverse semantic/cognitive independence remains NOT_PROVEN. |
| Independent validator | validation_v2/readiness, independent reconstruction suites | Existing malformed/foreign/changed-hash/claim ceiling and noncomplete decision cases pass. No economic validation claim. |
| Red team | red_team_v2, economic-readiness and scientific-claim admission suites | Existing machine-readable negative rights regressed. Exhaustive contradictory validator/context combinations unproven. |
| Economic identity | final_shape/portfolio_v2; documentary scope and frozen declaration suites | Existing hashes/declarations and provenance ceilings pass. No new empirical or source-fact promotion. |
| Portfolio map | structural UNKNOWN/overlap and economic-identity portfolio suites | Missing support remains UNKNOWN; correlation unavailable and marginal contribution not estimated. Extreme/malformed nested structural values not exhaustive. |
| Shadow/prospective | shadow, ForwardRegistryV2; CP010 forged-import/save/reload tests and existing suites | Observation denied through existing public entrypoints. Active ingestion inactive by authority; no absent future surface counted as defect. |
| Sealed evaluation/feedback | v2_core/v2_pipeline; feedback, export and membrane suites | CP002 tuple guard bypass repaired. Actual process/transport isolation and covert prose channels unproven. |
| Decay monitoring | final_shape.decay_guard and engines/decay | CP010 explicit denial under normal/-O/-OO. Active decay remains inactive; zero consumed is not a monitoring capability claim. |
| Capital Desk chain | desk, risk, execution, journal; whole Quant and V1 red-team suites | CP006 numerical RISK, CP008 causal/capacity guards and CP012/CP016 journal fencing, frozen intent and shared-instance recovery/read composition. Entire multi-file concurrent Desk transaction remains unproven. No real orders. |
| Persistent Book | ledger; CP001/CP013/CP016 and V1 end-to-end crash/replay tests | D4 for scoped mutation/recovery/identity-read composition; D3 exact-payload replay. Legacy applied IDs without payload proof block replay; raw state/view concurrency and hostile whole-Book schemas remain unproven. |
| Learning/search | learning store, replenisher; CP004/CP014 and queue/research runtime suites | D3 identity replay across retention, stale-writer fencing and shared-instance publication/crash recovery. Already-discarded IDs, reentrant callbacks, unguarded attribute access and whole research transactions remain unproven. |
| Acquisition firewall | acquisition_firewall/source adapters/intents/frontier planner suites | Existing plan-only route and permission/PIT/content denials regressed. No network acquisition or new Multi-Source family. |
| Receipts/Live Lab/status | EventLog/state, status projections, live_lab_contract; Python composition and 57 JS tests | CP005 journal recovery. Existing reducer/idempotency/projection tests pass; no production Site/D1/SSE proof. |
| Build/release/resume | release/bootstrap/provenance/deploy helpers and suites | CP011 exact-source generator binding repaired. No deployment, hosted CI, non-Git installed-release or authenticated attestation claim. |
| Wide/cheap/narrow/deep | worker preflight, source planner, replenisher and canonical-spine suites | Existing duplicates/blockers run before expensive stages in regression fixtures. Economic information-value optimality unproven. |

Additional existing surfaces: all root Edge Lab tests (hash-chained store,
discovery, worker sessions, resource budgets, remote adapters, scheduler and
dashboard) and all SEC acquisition/P0 adversarial tests were regressed. Their
green results retain their existing scope; this campaign adds no new blanket
depth label to them. Platform protocol-model harness tests use local fixtures.

Newly deepened units, with counts assigned once at maximum scoped depth:

| Unit | Depth | Checkpoint |
| --- | --- | --- |
| Book durable mutation/mark recovery, fencing and identity reads | D4 | CP001/CP016 |
| Detached Book view write denial | D2 | CP001 |
| Canonical artifact serialized reconstruction | D2 | CP002 |
| Research export/qualification sequence-content guard | D4 | CP002 |
| Evidence concurrent publication/index recovery | D3 | CP003 |
| Evidence exact typed references/nonfinite admission | D2 | CP003 |
| Learning retained replay, concurrent mutation and failed-write recovery | D3 | CP004/CP014 |
| Generic journal recovery/concurrent append | D3 | CP005 |
| RISK numerical admission | D2 | CP006 |
| Local queue clock/schema/identity admission | D2 | CP007 |
| Local queue durable publication/retry and stale writer fencing | D3 | CP007/CP015 |
| Execution causal capacity admission | D2 | CP008 |
| PIT action order and finite terms | D2 | CP009 |
| Closed decay guard under optimized execution/state composition | D4 | CP010 |
| Exact-source qualification receipt binding | D2 | CP011 |
| Desk journal frozen intent, completion, shared recovery and identity reads | D4 | CP012/CP016 |
| Book replay token bound to exact durable economic payload | D3 | CP013 |
| Scientific ledger detached append/verification and atomic snapshot publication | D3 | CP017 |

These are evidence limits, not claims that every edge case or every function in
every listed module has been exhausted. Whole multi-file session concurrency,
whole-epoch crash/recovery, memory conflict scopes, parser semantic truth and
hostile on-disk state remain priority adversarial ideas for later work. Existing
future-module absences are not cross-axis findings in this Phase-A campaign.
