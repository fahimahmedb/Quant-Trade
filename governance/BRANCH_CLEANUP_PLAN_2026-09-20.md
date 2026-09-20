# BRANCH CLEANUP PLAN — 2026-09-20

Authority: Blue / Mission Control.

This document governs branch cleanup after historical PR cleanup reached **0 open PRs**.

Cleanup objective is authority clarity, not deletion count. Deleting a branch ref must never destroy the ability to reconstruct a scientific, audit, CI, or governance claim.

## 1. Non-negotiable rules

- Do not modify or delete the frozen Gate A v3 candidate.
- Do not delete the active Astra Gate A v3 audit branch.
- Do not delete a branch merely because it is old.
- A branch whose tip is a strict ancestor of a retained authority can generally lose its ref without losing its commits.
- A diverged branch needs an explicit content/evidence decision before deletion.
- Branch deletion is more conservative than PR closure.
- During independent Astra Gate A v3 review, retain all Gate A refs needed for replay, anti-redirection, audit history, or exact-SHA reconstruction.
- The stale repository default branch is not changed as incidental cleanup.
- No Forward/Economic/Product integration decision is made by this cleanup.

Live snapshot at classification start:
- branches = 71;
- open PRs = 0;
- Blue authority = `blue/master-v2-2026-09-20`;
- frozen Gate A v3 = `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`;
- Astra v3 audit = active/no verdict yet.

## 2. KEEP — current authority / canonical / active audit

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
- current repository default `claude/nasdaq-trading-model-design-h3mp4n` until an explicit default-branch migration decision.

## 3. KEEP_UNTIL_ASTRA — Gate A / P0 proof refs

Do not delete these while the independent Gate A v3 audit is open, even where their commits are reachable elsewhere:

- `blue/p0-calendar-direct-reconcile-red-2026-09-20`
- `blue/p0-manual-probe-red-2026-09-20`
- `blue/p0-direct-reconcile-fix-2026-09-20`
- `blue/p0-audit-authority-red-2026-09-20`
- `blue/checkpoint-gate-a-v2-audit-2026-09-20`
- `astra/checkpoint-gate-a-v2-independent-audit-2026-09-20`
- `astra/p0-deep-adversarial-2026-09-19`
- `blue/p0-gate-a-final-2026-09-20`
- `builder/p0-integrity-blockers-fingerprint-v1`
- `blue/frontier-p0-continuity-rule-2026-09-18`
- `blue/frontier-p0-fingerprint-v1-2026-09-18`
- `blue/frontier-p0-integrity-blockers-2026-09-18`
- `blue/frontier-p0-operational-2026-09-18`
- `builder/sec-form4-p0-raw-capture`
- `builder/sec-form4-p0-raw-capture-v2`
- `codex/reprendre-mission-astra-p0-pre-t0`.

These are retained for replay convenience, historical falsifiers, or P0 lineage. Re-evaluate after Astra handoff.

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
- `claude/restaurant-stock-management-mvp-6oq43e`
- `claude/nasdaq-quant-trading-model-emdbg5`

They are not inputs to current Gate A, Forward, Economic, Product integration, or Blue governance.

DELETE_NOW_SAFE_COUNT = 17.

No deletion has been executed by this document.

## 5. DELETE_AFTER_ASTRA — absorbed or superseded P0/governance refs

These are strong deletion candidates, but their refs should remain until Astra returns because they are close to the current P0 proof lineage:

- `blue/d05-d07-governance-2026-09-15` — strict ancestor of current Blue.
- `blue/handoff-memory-2026-09-15` — same tip as `blue/frontier-p0-integrity-blockers-2026-09-18`, strict ancestor of Blue.
- `blue/p0-calendar-holiday-red-2026-09-20` — strict ancestor of frozen v3.
- `blue/p0-gate-a-consolidated-2026-09-20` — strict ancestor of frozen v3.
- `blue/p0-gate-a-v2-2026-09-20` — strict ancestor of frozen v3.
- `blue/p0-audit-authority-fix-2026-09-20` — diverged alternate fix line; retain until audit confirms no unique falsifier remains.
- `blue/p0-calendar-dst-proof-2026-09-20` — diverged by one commit from later Gate lineage; retain until audit disposition.
- `blue/p0-continuity-qualification-2026-09-20` — diverged P0 qualification line.
- `blue/p0-gate-a-long-history-2026-09-20` — diverged long-history/stress proof.
- `blue/p0-gate-a-v2-staging-2026-09-20` — diverged staging consolidation.
- `blue/p0-manual-operator-provenance-fix-2026-09-20` — diverged alternate B3 fix.
- `blue/p0-manual-probe-fix-2026-09-20` — diverged partial B3 fix.
- `claude/quant-blue-master-2026-09-20-mogpvh` — superseded Blue authority; retain until Astra consumes current governance handoff cleanly.
- `checkpoint/blue-master-consolidated-2026-09-20`
- `checkpoint/blue-master-project-2026-09-20`.

Post-Astra deletion still requires a final citation/reachability check.

## 6. PRESERVE_UNIQUE_PRODUCT_CAPABILITIES

Independent file checks found that several diverged Builder branches contain modules that do **not** exist on the frozen Gate A v3 P0 candidate. They therefore carry unique product-side implementation and are not cleanup noise:

- `builder/evidence-store-identity-v2`
  - unique modules include `src/quant/dataplane/evidence.py`, `identity.py`, corporate-action/PIT identity schemas and adversarial evidence tests;
  - these files are absent from frozen P0 v3.
- `builder/research-factory-core-v2`
  - unique modules include `experiments.py`, `outcome_firewall.py`, power/geometry and experiment-registry proof;
  - these files are absent from frozen P0 v3.
- `builder/research-factory-core-v2-proof-scratch`
  - earlier proof lineage for the same Research Factory capability; retain until the final core branch has been integrated or explicitly archived.
- `builder/sec-form4-census-v2a`
  - unique product-side census implementation `src/quant/dataplane/sec_form4.py`, schemas, calendar data and census tests;
  - `sec_form4.py` is absent from the frozen P0 v3 tree.

These refs should survive until Blue explicitly decides how their capabilities map into the Product integration runtime. P0 isolation is not evidence that product-side capabilities are obsolete.

## 7. HOLD_FOR_INTEGRATION_OR_CONTENT_REVIEW — do not delete yet

These branches are diverged and can contain unique work or concepts. They are not current authority, but deletion is premature:

- `blue/forward-finalization-2026-09-20` — diverged 2 ahead / 2 behind canonical Forward; unique `forward-live-smoke` concept is still queued for reimplementation.
- `builder/forward-market-recorder-v2` — diverged old Forward implementation line. Tree inspection shows a distinct `src/quant/recorders/**` architecture and recorder schemas/tests not present by path in canonical Forward; preserve until Blue decides whether any recorder concepts need porting.
- `parallel/codex-wave1-economic-system-2026-09-19` — diverged alternate Economic line. It contains an older compact `economics/engine.py` implementation while canonical Economic V2 has a much broader modular economics stack; preserve until semantic supersession is explicitly recorded.
- `codex/test`
- `research/design-v1` — contains unique Alpha Factory / market-selection / abstention / launch doctrine documents; preserve as design reference until their useful content is either adopted or explicitly superseded
- `parallel/codex-wave1-economic-system-2026-09-19`
- `blue/long-horizon-research-2026-09-20`
- `recovery/claude-sec-local-20260914`.

For these, inspect unique commits/files or explicitly supersede their useful content before deleting the ref.

## 8. Next cleanup actions

1. Delete the 15 `DELETE_NOW_SAFE` refs when a branch-delete capability is available.
2. Do not emulate deletion by force-moving refs.
3. While Astra runs, inspect the remaining diverged HOLD set and promote any unique useful concept into a durable queue/index. Unique product capability branches identified in Section 6 are explicitly preserved.
4. After Astra handoff, re-run reachability/citation checks and shrink the `KEEP_UNTIL_ASTRA` + `DELETE_AFTER_ASTRA` sets.
5. Only after Gate disposition review the stale default branch migration.
6. Current tool limitation: GitHub connector exposes no branch-ref deletion operation. Do not substitute force-moving refs for deletion; actual ref removal requires a proper branch-delete capability or manual GitHub operation.
