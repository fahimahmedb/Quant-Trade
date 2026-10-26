# BUILDER CHECKPOINT 003 — FRONTIER DUPLICATE RECYCLING DIAGNOSIS

CHECKPOINT_ID: BUILDER_CP_003_FRONTIER_DUPLICATE_DIAGNOSIS_20261020
TASK_CAPABILITY: Diagnose autonomous frontier work recycling before mutation
BUILDER_ROLE: V2 Forward Builder / Quant Engineer
WORKING_BRANCH: builder/v2-forward-20261020
TASK_BASE_SHA: 83469f5a7205cafa2478971adf0ddabdf7457587
CURRENT_BUILDER_HEAD_DESCRIBED: 83469f5a7205cafa2478971adf0ddabdf7457587
FRESH_OBSERVED_ORACLE_V2_HEAD: e9c80c37641c0f41dd4e082107569a726eb74d22
UPSTREAM_RELATED_BRANCHES:
- builder/oracle-v2-core-20261020
- audit/forensic-checkpoint-20261019

## Objective

Explain why the qualified autonomous V2 runtime can keep creating frontier tasks that consume wakes but regenerate exact-current candidate hypotheses, while preserving the duplicate gate rather than weakening it.

## Concrete observed failure mode

A later EVENT_DOCUMENT frontier task (`FRONTIER-EVENT-DOCUMENT-DISTINCT-MECHANISM-008`) regenerated the already-current candidate `DOC-EVENT-d8d19dbf0b1291ce` from the same Apple dividend documentary packet and was correctly stopped by `BLOCK_EXACT_CURRENT_DUPLICATE`.

This is not a duplicate-screen defect. The duplicate screen behaved correctly. The upstream work derivation supplied no novel admissible research input.

## Root cause proven from code

### 1. Frontier replenishment varies sequence, not research input

`research/research_os/queue_replenisher.py::derive_refill_task`:
- counts prior emissions per `frontier_id`;
- selects the least-issued frontier;
- increments `sequence`;
- derives a new task ID and derivation key from frontier metadata + sequence;
- places objective/frontier/legacy/source-policy metadata in `inputs`;
- DOES NOT bind a `documentary_source`;
- DOES NOT bind a source identity/hash;
- DOES NOT check whether the frontier's currently usable source would deterministically reproduce an existing candidate;
- DOES NOT persist a truthful `NO_ADMISSIBLE_NOVEL_WORK` condition.

The frontier currently permits `max_issued_per_frontier = 12`, so a family can receive multiple nominally distinct tasks even when its admissible producer input is unchanged.

### 2. Producer worker falls back to one fixed source per family

`research/research_os/worker_stages.py` maps:
- FUNDAMENTAL -> `apple_fy2025_statement_cells.json`
- EVENT_DOCUMENT -> `apple_dividend_announcements.json`
- INSTITUTIONAL_FLOW -> `sec_t1_operative_rule.json`
- QUANT_MECHANISM -> no default source

When a task has no explicit `inputs.documentary_source`, the worker selects that fixed default. The deterministic engine therefore receives the same source again and can only regenerate the same candidate for that family/source combination.

### 3. Source inventory is narrower than the frontier mandate

Current `research/research_os/sources/` contains the principal producer surfaces:
- `apple_dividend_announcements.json`
- `apple_fy2025_statement_cells.json`
- `sec_t1_operative_rule.json`
- `sec_t1_staff_faq.json`
plus capture support.

Consequences:
- EVENT_DOCUMENT currently has one obvious canonical producer packet and repeated generic frontier tasks replay it.
- FUNDAMENTAL currently has one obvious canonical producer packet and repeated generic frontier tasks replay it.
- INSTITUTIONAL_FLOW has at least two SEC documentary surfaces, but the generic fallback always selects only `sec_t1_operative_rule.json`; alternate admissibility/engine compatibility still needs explicit verification before use.
- QUANT_MECHANISM has no `DEFAULT_SOURCES` entry, so the replenisher can derive a generic QUANT task that the worker cannot execute without an explicit documentary source.

### 4. Frontier semantics promise distinct discovery that task derivation cannot currently supply

`runtime/RESEARCH_FRONTIER.json` says every enabled frontier should find one causally distinct mechanism/thesis and allows up to 12 issued tasks per frontier. Yet the derived task contains only a broad objective and source policy, not a distinct evidence packet or source-selection decision.

This makes `sequence` look like research diversification while it is only administrative diversification.

## Scientific interpretation

The correct behavior is NOT to weaken `BLOCK_EXACT_CURRENT_DUPLICATE`, generate random prose, or vary parameters until a different hypothesis ID appears.

When no unused admissible producer input exists, truthful autonomy must be able to say:

`NO_ADMISSIBLE_NOVEL_WORK`

That state is scientifically preferable to repeatedly spending wakes on deterministic duplicates.

If multiple admissible inputs do exist, source selection must be explicit, PIT-safe, provenance-bound and reproducible. A task should know which qualified source it is consuming before producer execution.

## Proposed bounded fix direction

Do not change the duplicate gate.

Introduce a deterministic pre-derivation frontier input planner / selector that:
1. maps producer task types to actually admissible durable source packets;
2. excludes source packets already consumed by prior frontier tasks for the same frontier when their durable source blob is unchanged;
3. emits exactly one explicit `documentary_source` binding when an unused admissible source exists;
4. emits `NOOP_NO_ADMISSIBLE_NOVEL_SOURCE` / equivalent truthful state when none exists;
5. never invents a source, candidate, result or outcome;
6. keeps all four authority flags false;
7. remains bounded to one derived task per refill wake;
8. leaves existing historical task files untouched;
9. preserves reproducibility through source path + blob/hash binding;
10. keeps QUANT blocked/no-op until an admissible documentary source is explicitly available instead of deriving unusable generic work.

Before implementation, verify whether `sec_t1_staff_faq.json` is a valid INSTITUTIONAL_FLOW producer packet under the existing engine/qualification contract. Do not assume compatibility from filename alone.

## Files / surfaces modified

- This checkpoint only.

No runtime, frontier, source, task, worker, policy, epoch, Site, Capital Desk or Book state was modified.

## Tests / evidence checks run

Repository-level forensic inspection only:
- `worker_stages.py`
- `queue_replenisher.py`
- `runtime/RESEARCH_FRONTIER.json`
- current source inventory
- concrete duplicate task/artifact evidence from EVENT_DOCUMENT

No implementation tests are claimed at this diagnosis checkpoint.

## Adversarial / falsification checks

- Hypothesis: duplicate gate itself is too strict -> rejected. It correctly detects an exact-current duplicate.
- Hypothesis: sequence number creates scientific novelty -> rejected. Sequence changes task derivation metadata only; no new documentary input is bound.
- Hypothesis: worker autonomously chooses among repository sources -> rejected. It uses an explicit source if supplied, otherwise a single hard-coded default per mapped family.
- Hypothesis: all frontiers have a default executable source -> rejected. QUANT_MECHANISM has no default source mapping.
- Hypothesis: simply increasing `max_issued_per_frontier` increases search breadth -> rejected under current deterministic source reuse.

## Authority / safety

ECONOMIC_EXPERIMENT_AUTHORIZED: FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED: FALSE
REAL_CAPITAL_AUTHORIZED: FALSE
LIVE_TRADING_AUTHORIZED: FALSE
OUTCOME_ACCESS_STATUS: NOT_ACCESSED
ACTIVE_EPOCH_MUTATION_BY_BUILDER: NONE

## What is now proven

- Autonomous duplicate recycling is caused upstream by task derivation/source binding, not by duplicate screening.
- Generic frontier sequence increments do not produce new evidence inputs.
- Current fallback source selection can deterministically replay already-known candidates.
- QUANT frontier derivation is structurally capable of issuing a task without a default producer source.
- A truthful no-novel-work state is needed when source breadth is exhausted.

## What is not proven

- `sec_t1_staff_faq.json` has not yet been proven engine-compatible as an alternate institutional-flow producer packet.
- No source acquisition expansion is authorized or implemented.
- No claim is made that source exhaustion is permanent; only current durable inventory is assessed.
- No runtime/reboot/Site qualification is asserted.
- No economic result is observed or inferred.

## Known risks

- A naive source-rotation fix could treat captures/support files as producer packets even when they do not satisfy the engine contract.
- Source path alone is insufficient across changing blobs; durability must bind content/blob identity.
- Historical tasks may not carry source-binding metadata, so backward-compatible consumed-source reconstruction must be conservative.
- Oracle V2 is advancing independently; any later integration must reacquire and reconcile fresh HEAD.

## Unresolved questions

- Exact compatibility of `sec_t1_staff_faq.json` with the institutional-flow engine.
- Whether the cleanest location is `queue_replenisher.py` itself or a small pure source-planning helper imported by it.
- Whether existing source qualification helpers can be reused directly without creating dependency cycles.

NEXT_RECOMMENDED_TASK: prove admissibility/engine compatibility of each durable source packet, then implement a pure deterministic source planner and queue-replenisher binding with fail-closed no-novel-source behavior.
EXACT_RESUME_ACTION: read CP003; reacquire fresh Oracle V2 HEAD; inspect `sec_t1_staff_faq.json`, source qualification/engine input contracts, and queue replenisher tests; then implement only on `builder/v2-forward-20261020`.
FINAL_INTEGRATOR_IMPLICATION: future convergence should import the source-planning fix before permitting further frontier refill loops; do not weaken duplicate screening.
SAFE_TO_CONTINUE: TRUE
