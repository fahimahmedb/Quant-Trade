# BUILDER CHECKPOINT 004 — FRONTIER SOURCE ADMISSIBILITY + AUTHORITY MISMATCH

CHECKPOINT_ID: BUILDER_CP_004_FRONTIER_SOURCE_ADMISSIBILITY_20261020
TASK_CAPABILITY: Prove source admissibility and current frontier execution blockers before mutation
BUILDER_ROLE: V2 Forward Builder / Quant Engineer
WORKING_BRANCH: builder/v2-forward-20261020
TASK_BASE_SHA: 6ae13c8bfcf8c853f4654c879dc75250541f79ae
FRESH_OBSERVED_ORACLE_V2_HEAD: e817e6c3d8782b04e09231910375948670b9eb7d
UPSTREAM_RELATED_BRANCHES:
- builder/oracle-v2-core-20261020
- audit/forensic-checkpoint-20261019

## Objective

Continue CP003 by proving which durable source packets are actually admissible under the current engine contracts, and identify any blocker that would make a source-planning fix insufficient by itself.

## Fresh runtime evidence

Oracle V2 advanced independently during this Builder session.

At observed Oracle head `e9c80c37641c0f41dd4e082107569a726eb74d22`, task `FRONTIER-INSTITUTIONAL-FLOW-DISTINCT-MECHANISM-009` was blocked at `mechanism_research` with:

`STAGE_NOT_EXPLICITLY_AUTHORIZED:mechanism_research`

This is not a source-qualification failure. The current `INSTITUTIONAL_FLOW_DISTINCT_MECHANISM.allowed_actions` contains inspection/mapping language but none of the exact authorization tokens matched by `require_stage_authorized(..., mechanism_research)` (`research|mechanism|discovery`). The task objective mentions mechanism, but the guard intentionally evaluates `allowed_actions`, not objective prose.

At fresh Oracle head `e817e6c3d8782b04e09231910375948670b9eb7d` (2026-10-20T14:50:15Z), the autonomous queue refill derived `FRONTIER-QUANT-MECHANISM-DISTINCT-009` with status `DERIVED_ONE_READY_TASK` even though the worker has no default documentary source for `QUANT_MECHANISM`. The derived task contains no `inputs.documentary_source` binding. This directly demonstrates the CP003 failure mode in live durable state.

## Source admissibility proof

### Institutional Flow

Two durable source wrappers are present:

1. `research/research_os/sources/sec_t1_operative_rule.json`
   - `rule_kind = STANDARD_SETTLEMENT_OPERATIVE_RULE`
   - official CFR capture
   - already the hard-coded current fallback source

2. `research/research_os/sources/sec_t1_staff_faq.json`
   - `rule_kind = STANDARD_SETTLEMENT_CONSTRAINT_EXPLANATION`
   - SEC staff FAQ, explicitly nonbinding

The second source is not merely filename-compatible. Current code proves compatibility:

- `qualify_document_packet(..., family='INSTITUTIONAL_FLOW')` selects `sec_t1_rule_packet` for `STANDARD_SETTLEMENT_OPERATIVE_RULE` and `sec_t1_packet` otherwise.
- `sec_t1_packet(...)` is the exact adapter that reconstructs and validates the persisted FAQ packet.
- `documentary_candidate(...)` has an explicit `INSTITUTIONAL_FLOW` branch accepting both `STANDARD_SETTLEMENT_CONSTRAINT_EXPLANATION` and `STANDARD_SETTLEMENT_OPERATIVE_RULE`.

Therefore `sec_t1_staff_faq.json` is a legitimate second current engine-contract input for the institutional-flow producer.

### Event Document

`apple_dividend_announcements.json` is the one qualified current event-document producer wrapper. The sibling `apple_dividend_announcements_capture.json` is capture support, not an engine wrapper and must not be treated as a second source.

### Fundamental

`apple_fy2025_statement_cells.json` is the one qualified current fundamental producer wrapper.

### Quant Mechanism

No current durable source wrapper has been proven to satisfy the `QUANT_MECHANISM` documentary contract. The current live refill nevertheless issued a generic QUANT task. That is scientifically incorrect scheduling: an administrative mandate exists, but no admissible producer input is bound.

## Actual residual gap

The repair requires two bounded changes, not one:

1. **Source-aware refill planning**
   - discover only actual durable documentary wrappers;
   - qualify each wrapper against the target engine family using the existing authoritative `qualify_document_packet` contract;
   - exclude already-consumed source identities conservatively;
   - bind exactly one source path + packet hash + source record/blob identity into any new frontier task;
   - emit a truthful no-op (`NOOP_NO_ADMISSIBLE_NOVEL_SOURCE`) when no unused qualified source exists;
   - include source identity in the derivation key;
   - never weaken duplicate screening or invent research input.

2. **Institutional frontier action-contract repair**
   - explicitly authorize bounded `mechanism_research` in `allowed_actions` for `INSTITUTIONAL_FLOW_DISTINCT_MECHANISM`;
   - do not broaden `require_stage_authorized` or infer authorization from objective prose.

## Consumption semantics

Historical pre-planner frontier tasks did not persist source hashes. Their known hard-coded fallback path must therefore be treated conservatively as consumed for that frontier:

- EVENT_DOCUMENT -> `apple_dividend_announcements.json`
- FUNDAMENTAL_RESEARCH -> `apple_fy2025_statement_cells.json`
- INSTITUTIONAL_FLOW -> `sec_t1_operative_rule.json`
- QUANT_MECHANISM -> no default source exists

New planner-derived tasks should bind exact source path, packet content hash, canonical wrapper hash and Git blob SHA when available. A later worker stage must fail closed if that bound source changes before research.

## Files / surfaces modified

- This checkpoint only.

No runtime task, frontier config, source, worker, policy, epoch, Site, Capital Desk or Book state was mutated in this checkpoint.

## Tests / evidence checks

Repository-contract inspection:
- `research/research_os/queue_replenisher.py`
- `research/research_os/worker_stages.py`
- `research/research_os/runtime/RESEARCH_FRONTIER.json`
- `research/research_os/engines/builtin.py`
- `research/research_os/expansion/engine_dossiers_v1.py`
- `research/research_os/expansion/source_adapters_v1.py`
- current source inventory
- fresh Oracle V2 runtime commits `e9c80c3...` and `e817e6c...`

No implementation-test claim is made yet.

## Adversarial conclusions

- Weakening `BLOCK_EXACT_CURRENT_DUPLICATE` remains rejected.
- Treating sequence number as scientific novelty remains rejected.
- Treating capture-support JSON as a new producer source remains rejected.
- Inferring stage authority from broad objective text is rejected; `allowed_actions` must explicitly authorize the stage.
- Deriving QUANT work without an admissible source is now directly observed, not hypothetical.
- SEC staff FAQ admissibility is proven by the current adapter + engine contract, not inferred from naming.

## Authority / safety

ECONOMIC_EXPERIMENT_AUTHORIZED: FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED: FALSE
REAL_CAPITAL_AUTHORIZED: FALSE
LIVE_TRADING_AUTHORIZED: FALSE
OUTCOME_ACCESS_STATUS: NOT_ACCESSED
ACTIVE_EPOCH_MUTATION_BY_BUILDER: NONE

## Next implementation block

Implement on `builder/v2-forward-20261020` only:

1. a pure frontier documentary-source planner using current `qualify_document_packet` as the authoritative compatibility gate;
2. queue-refill integration that selects only frontiers with an unused qualified source;
3. exact source binding in derived task inputs and derivation payload;
4. worker-side source-binding verification before producer execution;
5. explicit institutional-flow `mechanism_research` authorization in frontier config;
6. focused tests for:
   - SEC FAQ selected after legacy default rule path is consumed;
   - QUANT no-source returns no-op instead of READY task;
   - EVENT/FUND source exhaustion returns no-op;
   - capture support is rejected;
   - source identity is bound and source mutation fails closed;
   - authority remains closed and duplicate gate unchanged.

EXACT_RESUME_ACTION: implement the above block on the Builder rail, run focused tests, push code commit, then immediately push CP005 with SHAs/test evidence.
SAFE_TO_CONTINUE: TRUE
