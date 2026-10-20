# BUILDER CHECKPOINT 005 — SOURCE-AWARE FRONTIER REFILL

CHECKPOINT_ID: BUILDER_CP_005_SOURCE_AWARE_FRONTIER_REFILL_20261020
TASK_CAPABILITY: Prevent autonomous frontier recycling/inexecutable work by binding unused qualified documentary sources
BUILDER_ROLE: V2 Forward Builder / Quant Engineer
WORKING_BRANCH: builder/v2-forward-20261020
TASK_BASE_SHA: db5bcc0d24f4254ec48d4f8c43bb4301c214a989
CURRENT_BUILDER_HEAD_DESCRIBED: 8b99fc216d76cadab791089e6d9884322ca11627
FRESH_ORACLE_HEAD_OBSERVED_DURING_TASK: e817e6c3d8782b04e09231910375948670b9eb7d
UPSTREAM_RELATED_BRANCHES:
- builder/oracle-v2-core-20261020
- audit/forensic-checkpoint-20261019

## Objective

Close the concrete autonomous-work defect proven by CP003/CP004 without weakening duplicate screening, inventing research inputs, reading outcomes, or changing economic authority.

## Implemented capability

### 1. Pure frontier documentary-source planner

Added:

`research/research_os/frontier_source_planner_v2.py`

The planner:
- maps producer task types to their existing engine family;
- inspects only caller-supplied durable source records;
- requires the exact documentary wrapper contract (`source_ref`, `freeze_time`, `documentary_packet`);
- rejects capture-support/non-documentary records;
- delegates semantic family compatibility to the existing authoritative `qualify_document_packet(...)` contract;
- tracks already-consumed source identities per frontier;
- treats pre-planner historical tasks conservatively by marking their known hard-coded fallback path consumed;
- binds path, packet content hash, canonical wrapper hash, and Git blob SHA when available;
- returns `SOURCE_SELECTED`, `NO_ADMISSIBLE_DOCUMENTARY_SOURCE`, or `NO_UNUSED_ADMISSIBLE_SOURCE` without executing research.

### 2. Source-aware queue replenisher

Updated:

`research/research_os/queue_replenisher.py`

When a source catalog is supplied, refill eligibility now requires an unused engine-qualified source. The replenisher:
- excludes frontiers that have no admissible source;
- excludes frontiers whose admissible sources are already consumed;
- emits `NOOP_NO_ADMISSIBLE_NOVEL_SOURCE` when no frontier has new qualified material;
- includes exact source identity in the derivation payload/key;
- persists source path/blob/packet hash/record hash in the new task input;
- keeps one-task-per-refill and all authority restrictions unchanged;
- preserves legacy direct-call behavior only when no catalog is supplied;
- `derive_from_repo(...)` now supplies the repository source catalog by default.

### 3. V2-only strict runtime integration

Updated:

`research/research_os/oracle_worker_v2.py`

V1 orchestration was intentionally left untouched. V2 now:
- builds the source catalog from the fresh GitHub snapshot, including exact blob SHA;
- calls the source-aware replenisher;
- reacquires queue + source identities before atomic task publication;
- verifies the bound source on task selection and every lease transition;
- fails closed if source path disappears or blob/record/packet hash changes;
- writes `source_bound=true` in the refill event for a derived V2 task.

### 4. Institutional Flow action-contract repair

Updated:

`research/research_os/runtime/RESEARCH_FRONTIER.json`

`INSTITUTIONAL_FLOW_DISTINCT_MECHANISM.allowed_actions` now explicitly authorizes:

`research one bounded institutional-flow mechanism from admissible public rules and documentary evidence`

This fixes the observed `STAGE_NOT_EXPLICITLY_AUTHORIZED:mechanism_research` failure without broadening or weakening `require_stage_authorized`.

### 5. Focused tests

Added:

`tests/test_research_os_frontier_source_planner_v2.py`

Coverage includes:
- SEC staff FAQ selected after the historical default CFR rule source is conservatively marked consumed;
- EVENT_DOCUMENT and FUNDAMENTAL current single-source frontiers report exhausted after legacy use;
- QUANT with no qualified documentary source returns `NOOP_NO_ADMISSIBLE_NOVEL_SOURCE` rather than a READY task;
- source-aware refill skips unavailable/exhausted frontiers and binds the SEC FAQ;
- capture-support JSON is rejected as producer input;
- changed source blob fails closed;
- Institutional Flow now explicitly passes `mechanism_research` authorization.

## Commits produced in this block

- `db5bcc0d24f4254ec48d4f8c43bb4301c214a989` — CP004 admissibility/authority diagnosis
- `cc2a2daf4f5fc1fabd6e349ee31514192d7cb55a` — fail-closed frontier source planner
- `92237d6aba13c3fe52348b559a3a048c42f6482d` — source-aware queue replenisher
- `6ba744bde94b0bf53444a592a0c2eaf127bf9784` — V2 source binding and mutation checks
- `8aecad086085e671b7aa585d793433380157f00e` — explicit institutional mechanism-research authorization
- `678c1a5eb345093ec1a682cd569bea20d325f090` — focused source-aware tests
- `8b99fc216d76cadab791089e6d9884322ca11627` — Builder-rail Oracle V2 CI coverage

## Independent CI proof

GitHub Actions run:

- Workflow: `Oracle V2 Core`
- Run ID: `39444124806`
- Exact head SHA: `8b99fc216d76cadab791089e6d9884322ca11627`
- Job: `v2-core`
- Conclusion: `success`

Successful steps:
1. checkout/setup;
2. compile V2 Core including new `edge_observability_v2.py`, `frontier_source_planner_v2.py`, `queue_replenisher.py`, `oracle_worker_v2.py`;
3. V2 Core contract/bridge/pipeline/worker/whole-loop tests plus new observability and source-planner tests;
4. V2 policy fail-closed verification;
5. V2 claim-ceiling verification;
6. exact-head V2 qualification receipt generation;
7. real V2 entrypoint against fresh GitHub state with remote writes disabled;
8. qualification artifact upload.

All steps completed `success`.

## Adversarial / falsification results

- Sequence-only novelty: blocked by source eligibility.
- QUANT task without source: now no-op under V2 source-aware refill.
- Reuse of current Event/Fundamental default source: no-op after historical consumption.
- Alternate Institutional source by filename only: not allowed; actual packet must pass existing qualifier.
- Capture-support JSON: rejected.
- Source changes after task derivation: fail closed by blob/record/packet binding.
- Institutional action contract: repaired explicitly; guard remains unchanged.
- Duplicate gate: untouched.
- Economic outcome access: none introduced.
- Capital/observation/live-trading authority: unchanged false.

## Authority / safety

ECONOMIC_EXPERIMENT_AUTHORIZED: FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED: FALSE
REAL_CAPITAL_AUTHORIZED: FALSE
LIVE_TRADING_AUTHORIZED: FALSE
OUTCOME_ACCESS_STATUS: NOT_ACCESSED
ACTIVE_EPOCH_MUTATION_BY_BUILDER: NONE

## What is now proven

- V2 can distinguish administrative frontier capacity from actual scientific input capacity.
- Current durable Institutional Flow inventory contains two engine-qualified packets; the FAQ can be selected after the CFR default is consumed.
- Current QUANT frontier has no qualified durable documentary input and should not be scheduled merely because its issue count is low.
- Current Event/Fundamental single-source inventory can truthfully become exhausted rather than being replayed under new task IDs.
- Source identity is frozen at derivation and checked again before/during execution.
- The full existing V2 CI surface remains green on the exact Builder head.

## What is not proven

- No new economic edge, alpha or profitability.
- No source acquisition expansion has been performed.
- No claim that the current source inventory is economically broad enough.
- No Oracle runtime deployment/reboot of these Builder changes has been performed; this remains an isolated import candidate.
- No final Site/Live Lab convergence is claimed.
- Historical scientific-memory reconciliation remains outside this block.

## Known risks / integration notes

- `builder/oracle-v2-core-20261020` continues to advance independently. Final integration must reacquire its fresh HEAD and reconcile runtime-state commits without overwriting them.
- The Builder workflow branch addition is verification scaffolding; Final Integrator can retain or drop the `builder/v2-forward-20261020` trigger when importing.
- Existing pre-planner tasks are deliberately conservative about source consumption because they lack historical source hashes.
- New source expansion must pass the existing engine packet qualifier; adding files alone must never increase schedulable breadth.

## Next coherent task

Reacquire fresh Oracle state after the live QUANT-009 cycle and determine the next real North-Star gap. Priority order:
1. verify the current autonomous queue behavior/effects and whether additional invalid retries expose another scheduler/authority defect;
2. assess source breadth as a mechanism-specific research-capability gap, without indiscriminate connector expansion;
3. assess whether current negative/scientific memory can express `NO_ADMISSIBLE_NOVEL_SOURCE` durably enough for Owner observability and future refill decisions;
4. avoid Site/Closure overlap reserved for Final Integrator.

EXACT_RESUME_ACTION: read CP005, reacquire fresh `builder/oracle-v2-core-20261020` HEAD and recent commits, then inspect only new evidence since `e817e6c...` before choosing the next implementation block.
SAFE_TO_CONTINUE: TRUE
