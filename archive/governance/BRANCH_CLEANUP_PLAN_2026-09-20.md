# BRANCH CLEANUP PLAN — 2026-09-20

Authority: Blue / Mission Control.

This document governs branch cleanup after historical PR cleanup reached **0 open PRs**.

Cleanup objective is authority clarity, not deletion count. Deleting a branch ref must never destroy the ability to reconstruct a scientific, audit, CI, or governance claim.

## 1. Non-negotiable rules

- Do not modify or delete the frozen Gate A v3 candidate.
- Do not delete the final Astra Gate A v3 audit branch; it is canonical independent evidence.
- Do not delete a branch merely because it is old.
- A branch whose tip is a strict ancestor of a retained authority can generally lose its ref without losing its commits.
- A diverged branch needs an explicit content/evidence decision before deletion.
- Branch deletion is more conservative than PR closure.
- Gate A v3 review is closed. Retain divergent Gate A falsifier/audit refs where branch-level discoverability still carries unique replay or audit value.
- The stale repository default branch is not changed as incidental cleanup.
- No Forward/Economic/Product integration decision is made by this cleanup.

Current post-cleanup snapshot:
- branches = 40;
- open PRs = 0;
- Blue authority = `blue/master-v2-2026-09-20`;
- Gate A v3 = `REPOSITORY_PASS / CLOSED`;
- frozen Gate A v3 = `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`;
- final Astra v3 audit = `33995d03c8632e5c3a7b77a12b87366fb06b4d30`, CI `35517935710 = SUCCESS`;
- target-host qualification remains governed separately; repository cleanup makes no target-host readiness claim;
- delete-ready operational index = `governance/BRANCH_DELETE_READY_INDEX_2026-09-20.md`, 34 refs executed.

## 2. KEEP — current authority / canonical / final evidence

These refs are not deletion candidates:

- `blue/master-v2-2026-09-20`
- `blue/p0-gate-a-v2-final-2026-09-20`
- `blue/p0-gate-a-v3-frozen-2026-09-20`
- `builder/p0-gate-a-v3-2026-09-20`
- `astra/p0-gate-a-v2-independent-audit-2026-09-20`
- `astra/p0-gate-a-v3-independent-audit-2026-09-20`
- `astra/p0-deep-adversarial-pre-t0`
- `parallel/claude-forward-data-2026-09-20`
- `parallel/claude-economic-v2-2026-09-20`
- `blue/integration-readiness-2026-09-20`
- `reviewer/v1-final-red-team`
- repository default `blue/master-v2-2026-09-20`; former default `claude/nasdaq-trading-model-design-h3mp4n` retained as historical rollback/reference.

## 3. POST-GATE PROOF REF DISPOSITION

The former `KEEP_UNTIL_ASTRA` category is closed because the independent Gate A v3 audit is complete.

Current authority:
`governance/POST_GATE_A_PROOF_REF_REVIEW_2026-09-20.md`.

### Delete-ready absorbed proof refs

The following five refs are now delete-ready because their exact tips are strict ancestors of retained authorities and their evidentiary SHAs are durably indexed:

- `blue/p0-direct-reconcile-fix-2026-09-20`
- `blue/p0-gate-a-final-2026-09-20`
- `builder/p0-integrity-blockers-fingerprint-v1`
- `builder/sec-form4-p0-raw-capture-v2`
- `codex/reprendre-mission-astra-p0-pre-t0`

### Preserve divergent historical evidence

Keep these branch refs because they retain unique divergent falsifier/audit/recovery history:

- `blue/p0-calendar-direct-reconcile-red-2026-09-20`
- `blue/p0-manual-probe-red-2026-09-20`
- `blue/p0-audit-authority-red-2026-09-20`
- `blue/checkpoint-gate-a-v2-audit-2026-09-20`
- `astra/checkpoint-gate-a-v2-independent-audit-2026-09-20`
- `astra/p0-deep-adversarial-2026-09-19`
- `builder/sec-form4-p0-raw-capture`

Do not infer that "rejected" or "old" means deletable; divergence and evidence value govern this category.

## 4. DELETE_NOW_SAFE — first branch-cleanup tranche

These refs are safe to remove from the repository namespace **without losing their commits or current authority**, subject to the actual deletion operation being available.

### Absorbed strict ancestors

GitHub compare independently verified each of the following as a strict ancestor of current Blue, with `behind_by = 0` from the branch tip to Blue:

- `autonomous-quant-rebuild`
- `claude/quant-code-mandate-q0l644`
- `claude-config-bootstrap`
- `codex/add-task-acknowledgment-and-tracking`
- `codex/build-persistent-research-campaign-orchestrator`
- `codex/complete-v1-integrity-pass-for-codex`
- `quant-system-v1`
- `runtime/persistent-research-v1`
- `tmp-ignore`
- `codex/alignment-bootstrap` — strict ancestor of preserved `research/design-v1`; no unique tip content remains outside that retained design line.
- `codex/optimiser-recherche-persistente-avec-intelligence++` — closed PR #11 alternative runtime implementation; deliberately not selected. Current Blue carries the selected persistent runtime/orchestrator lineage instead. Preserve PR history, but the branch is not current authority or required evidence.
- `builder/research-factory-core-v2-proof-scratch` — exact strict ancestor of preserved `builder/research-factory-core-v2` (final core is 3 commits ahead / 0 behind).

Additional duplicate-ref facts:
- `tmp-ignore` and `claude-config-bootstrap` point to the same commit `002b9b04a2a62e26229b4fc17a39d64c109f53c6`.
- `quant-system-v1` and the stale repository default `claude/nasdaq-trading-model-design-h3mp4n` point to the same commit `8fea558143d0c46bc6eeb9f2aa57527b4e6c1fce`; keep the default only until explicit default migration, making `quant-system-v1` redundant as a ref.
- `codex/alignment-bootstrap` is an exact ancestor of retained `research/design-v1` (12 commits ahead / 0 behind from alignment to design).

### Economic ancestor absorbed by canonical Economic

- `parallel/claude-wave1-economic-system-2026-09-19`

GitHub compare against canonical Economic reports the canonical leaf 9 commits ahead / 0 behind with exact merge-base equal to the wave1 branch tip.

### Unrelated repository clutter

The existing Blue branch registry already classifies the following as unrelated/legacy content with no current Quant authority:

- `claude/memoire-finance-presentation-9p2q5g`
- `claude/political-prediction-token-optimization-di47f2`
- `claude/price-prediction-model-ykhog1`
- `claude/nasdaq-quant-trading-model-emdbg5`

They are not inputs to current Gate A, Forward, Economic, Product integration, or Blue governance.

DELETE_NOW_SAFE_COUNT = 17.

### Owner retention override

`claude/restaurant-stock-management-mvp-6oq43e@e083cc70e3f4c2ce31ea04f4fc43be35e9549ab0` was previously classified as unrelated cleanup clutter but was explicitly retained by the owner on 2026-09-20. It is therefore removed from the operational delete-ready batch.

`RETAIN_OWNER_REQUEST = TRUE`

Physical deletion was later executed under the repository-hygiene runbook; see `handoff/BLUE_REPOSITORY_HYGIENE_EXECUTION_2026-09-20.md`.

## 5. POST-GATE DELETE-READY CONSOLIDATION

The former `DELETE_AFTER_ASTRA` waiting state is closed.

Twelve strict-ancestor refs were rechecked after Gate A PASS and moved to delete-ready in:
`governance/POST_GATE_A_BRANCH_DELETE_BATCH_2026-09-20.md`.

Together with the first 17 safe refs and five newly absorbed proof refs, the single operational deletion authority is now:

`governance/BRANCH_DELETE_READY_INDEX_2026-09-20.md`

Current verified total:
`DELETE_READY = 34`

Execution result:
- 34/34 passed post-migration preflight;
- 34/34 were physically deleted;
- 0 delete-ready survivors remain;
- live branch count after cleanup = 40.

Any old branch-specific status in this plan is subordinate to the consolidated delete-ready index and later Blue governance.

## 6. PRESERVE_UNIQUE_PRODUCT_CAPABILITIES

Independent file checks found that several diverged Builder branches contain modules that do **not** exist on the frozen Gate A v3 P0 candidate. They therefore carry unique product-side implementation and are not cleanup noise:

- `builder/evidence-store-identity-v2`
  - unique modules include `src/quant/dataplane/evidence.py`, `identity.py`, corporate-action/PIT identity schemas and adversarial evidence tests;
  - these files are absent from frozen P0 v3.
- `builder/research-factory-core-v2`
  - unique modules include `experiments.py`, `outcome_firewall.py`, power/geometry and experiment-registry proof;
  - these files are absent from frozen P0 v3.
- `builder/sec-form4-census-v2a`
  - unique product-side census implementation `src/quant/dataplane/sec_form4.py`, schemas, calendar data and census tests;
  - `sec_form4.py` is absent from the frozen P0 v3 tree.

These refs survive until Blue explicitly decides how their capabilities map into the Product integration runtime. P0 isolation is not evidence that product-side capabilities are obsolete.

The scratch ref `builder/research-factory-core-v2-proof-scratch` is **not** required: GitHub compare proves `builder/research-factory-core-v2` is 3 commits ahead / 0 behind with merge-base exactly the scratch tip. The scratch ref therefore moves to DELETE_NOW_SAFE while the final core ref is preserved.

## 7. PRESERVE_SPECIAL_EVIDENCE / GOVERNANCE

- `blue/long-horizon-research-2026-09-20`
  - contains the explicit **DRAFT ONLY / NOT AUTHORITATIVE** proposal to replace fixed P14D with a hybrid event-based qualification;
  - current authority still says fixed P14D/frozen;
  - Gate A/Astra disposition is now complete; preserve until a later explicit Blue governance decision adopts, revises or rejects the P14D amendment.
- `recovery/claude-sec-local-20260914`
  - contains recovery-only SEC census artifacts, including an acceptance manifest described by its commit as requiring roughly eight hours of SEC fair-access acquisition;
  - explicitly not certification/economic authority, but expensive reproduction material;
  - preserve until the relevant product/census lineage has a durable replacement.
- `codex/test`
  - contains the historical Phase-0 P0-E1 economic value experiment and forensic report;
  - result was `KILL / REJECT`: lower volatility did not improve terminal wealth versus buy-and-hold under the tested setup, and the data/instrument provenance was inadequate for a production edge claim;
  - preserve as historical learning/memory evidence, not as current scientific authority.

## 8. HOLD_FOR_INTEGRATION_OR_CONTENT_REVIEW — do not delete yet

These refs contain distinct concepts or alternate implementations that are not current authority but should not be discarded before their successor integration decisions:

- `blue/forward-finalization-2026-09-20`
  - diverged 2 ahead / 2 behind canonical Forward;
  - unique `forward-live-smoke` workflow concept remains queued for reimplementation against canonical runner semantics.
- `builder/forward-market-recorder-v2`
  - distinct `src/quant/recorders/**` recorder architecture plus recorder schemas/restart/live-proof tests;
  - canonical Forward uses a different `src/quant/dataplane/forward_*` architecture;
  - preserve until Blue determines whether any recorder semantics need porting.
- `parallel/codex-wave1-economic-system-2026-09-19`
  - three unique commits from the old Wave-1 base, including compact provenance-bound `economics/engine.py`;
  - canonical Economic V2 is substantially broader/modular but is not yet integrated/qualified;
  - preserve until semantic supersession is explicitly recorded during Economic reception.
- `research/design-v1`
  - contains unique Alpha Factory, market-selection, abstention and launch-doctrine documents;
  - preserve as design reference until useful content is either adopted or explicitly superseded.

## 9. Cleanup disposition

`REPOSITORY_HYGIENE = CLOSED`

- default migration: executed and verified;
- physical deletion: 34/34 complete;
- delete-ready survivors: 0;
- restaurant branch: retained by explicit owner request;
- open PRs/issues: 0/0;
- Product integration remains paused;
- P0/V4/P14D remain separate workstreams.

Durable execution handoff:
`handoff/BLUE_REPOSITORY_HYGIENE_EXECUTION_2026-09-20.md`

Separate future action: review branch/ruleset protection for critical retained refs.