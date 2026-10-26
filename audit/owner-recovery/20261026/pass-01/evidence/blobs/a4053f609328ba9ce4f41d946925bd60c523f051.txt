# BRANCH SECOND PASS — 2026-10-20

Authority: CP12 deep organizational audit.

This supplements `BRANCH_FAMILY_DISPOSITION_2026-10-20.md` by classifying the largest remainder outside Weather/Gate-B/P0/Live-Lab/F1/Research-OS families.

No destructive action is authorized.

---

## 1. Claude session namespace — 36 refs

Observed refs:

- `claude/charming-allen-948kd8`
- `claude/confident-allen-xw7eb6`
- `claude/confident-mendel-h4qqo4`
- `claude/data-feeds-6vr22g`
- `claude/dazzling-dirac-foklrv`
- `claude/deep-research-project-6vr22g`
- `claude/dreamy-franklin-1vki4t`
- `claude/epic-cannon-1sy39m`
- `claude/exciting-edison-w68tos`
- `claude/exciting-planck-uq6rir`
- `claude/gallant-cerf-e0rpao`
- `claude/hopeful-dirac-4ahy2z`
- `claude/hopeful-hamilton-81rab1`
- `claude/intelligent-gates-msidml`
- `claude/magical-ramanujan-wsktyr`
- `claude/nasdaq-trading-model-design-h3mp4n`
- `claude/new-session-0ydmkg`
- `claude/new-session-3ujgeu`
- `claude/new-session-3ujgeu-wip-h002`
- `claude/new-session-3ujgeu-wip-h004`
- `claude/new-session-3ujgeu-wip-h006`
- `claude/new-session-8msq33`
- `claude/new-session-kfwf1b`
- `claude/new-session-qr4nsz`
- `claude/new-session-z4pdlx`
- `claude/order-12b-anytime-valid`
- `claude/project-review-audit-q5kfb9`
- `claude/prompt-recherche-praticiens-dfy1l0`
- `claude/prototype-futures-trend-carry-6vr22g`
- `claude/relaxed-johnson-mqca45`
- `claude/restaurant-stock-management-mvp-6oq43e`
- `claude/two-speed-cleanup-6vr22g`
- `claude/weather-v3-s0-compute-2026-10-02`
- `claude/weather-v3-s1-data-archaeology-2026-10-02`
- `claude/weather-v3-s2-capture-architecture-2026-10-02`
- `claude/zen-einstein-9moyry`

### Known semantic subsets

#### Data/research source candidates

- `claude/data-feeds-6vr22g` → `SOURCE_IMPORT_REVIEW_REQUIRED` (Data Plane relevance)
- `claude/deep-research-project-6vr22g` → `SCIENTIFIC/ARCHITECTURE_REVIEW_REQUIRED`
- `claude/prototype-futures-trend-carry-6vr22g` → `SCIENTIFIC_MEMORY_REVIEW_REQUIRED`
- `claude/prompt-recherche-praticiens-dfy1l0` → `RESEARCH_DESIGN_MEMORY_REVIEW_REQUIRED`

#### Weather V3 source/memory

- `claude/weather-v3-s0-compute-2026-10-02`
- `claude/weather-v3-s1-data-archaeology-2026-10-02`
- `claude/weather-v3-s2-capture-architecture-2026-10-02`

Class: `WEATHER_PREDECESSOR_MEMORY`. Their scientifically material content should be folded into the canonical Weather archaeology/memory package before refs disappear.

#### Governance / audit / cleanup proposals

- `claude/project-review-audit-q5kfb9`
- `claude/two-speed-cleanup-6vr22g`
- `claude/new-session-z4pdlx` (historical proposal PR #21, now closed)

Class: `HISTORICAL_GOVERNANCE_PROPOSAL`. These do not become current authority; retain only unique recommendations/audit evidence not already captured in CP12/V2.

#### Historical NASDAQ / rollback reference

- `claude/nasdaq-trading-model-design-h3mp4n`

Class: `HISTORICAL_PRODUCT/RESEARCH_REFERENCE`. Prior audits treated historical NASDAQ work as evidence/reusable code, not current product definition.

#### Owner retention override

- `claude/restaurant-stock-management-mvp-6oq43e`

Class: `OWNER_RETENTION_OVERRIDE`. Explicitly retained by Owner during earlier hygiene. Exclude from cleanup unless that decision is reversed.

#### Opaque/session refs

All other friendly-name/new-session/WIP branches:

Class: `OPAQUE_SESSION_REVIEW_BATCH`.

Cleanup rule for this batch:

1. compare each tip against live V1, V2, canonical source and retained historical branches;
2. exact duplicate or strict ancestor with no unique file/result → candidate `ABSORBED_REF_DELETE_READY`;
3. unique files/commits → inspect changed paths and commit messages;
4. scientific result/exposure → index memory;
5. capability → import/reject;
6. otherwise historical session-only work → `ARCHIVE_AFTER_REVIEW`.

The default outcome should be aggressive ref retirement after proof; opaque session names are not intended as durable project navigation.

---

## 2. Parallel namespace — 11 refs

- `parallel/antigravity-gate-b-run-authority-adversarial-precheck-2026-09-21`
- `parallel/antigravity-post-p0-vertical-shadow-loop-design-2026-09-21`
- `parallel/claude-economic-question-falsification-map-2026-09-21`
- `parallel/claude-economic-v2-2026-09-20`
- `parallel/claude-first-slice-cohort-geometry-2026-09-21`
- `parallel/claude-forward-data-2026-09-20`
- `parallel/claude-post-p0-vertical-build-prep-2026-09-21`
- `parallel/claude-research-frozen-effect-estimate-prestage-2026-09-21`
- `parallel/claude-s11-dependence-interval-challenge-2026-09-21`
- `parallel/codex-wave1-economic-system-2026-09-19`
- `parallel/economic-acceleration-2026-09-21`

Current class: `HISTORICAL_DESIGN/ADVERSARIAL_EVIDENCE`.

Prior audit already singled out `parallel/codex-wave1-economic-system-2026-09-19` as containing unique economic implementation semantics. `parallel/claude-forward-data-2026-09-20` was also historically preserved.

Disposition:

- map unique design/implementation concepts into current V2/Data/Economic source review;
- map adversarial findings into regression/audit memory;
- after import/rejection, retire parallel-work branches as routing surfaces.

The parallel namespace should not remain a permanent architecture layer.

---

## 3. Research namespace — 11 refs

- `research/close-auction-source-readiness-20261017`
- `research/delta-research-pack-v1-20261015`
- `research/design-v1`
- `research/duebill-source-readiness-20261017`
- `research/economic-reorientation-checkpoint-2026-09-29`
- `research/economic-test-form144-supply-20261017`
- `research/edge-lab-continuous`
- `research/f2-primary-terms-decision-2026-10-09`
- `research/legacy-economic-reconciliation-20261015`
- `research/paused-lanes-qualification-20261015`
- `research/technical-signals-literature-2026-10-10`

These are not generic cleanup clutter. By name and known workstream context they contain source qualification, economic tests, research packs, paused-lane decisions, design or scientific memory.

Classification:

- `design-v1`, `edge-lab-continuous`, `legacy-economic-reconciliation`: already `SOURCE_IMPORT_REQUIRED` / memory sources;
- `f2-primary-terms-decision`: blocked-access scientific memory;
- `technical-signals-literature`: EURUSD frozen/unexecuted scientific memory;
- `economic-test-form144-supply`: executed/experimental research memory review required;
- close-auction/duebill readiness: source-readiness memory review required;
- delta research pack / paused-lanes / economic reorientation: architecture/research-priority memory review required.

Default: `SCIENTIFIC_MEMORY_OR_SOURCE_REVIEW_REQUIRED`, not blind archive/delete.

---

## 4. Sol scout namespace — 4 refs

- `sol/scout-crypto-20261008-1847`
- `sol/scout-events-f413d`
- `sol/scout-macro-tauc-gfs`
- `sol/scout-prediction-flb-nr`

Class: `SCOUT_INPUT_MEMORY`.

These are discovery/source-scoping inputs, not economic authority. Extract any unique mechanism/source candidates and their rejection/qualification status into V2 research memory; then retire session refs if no executable capability remains.

Do not convert a scout idea into an established edge merely by importing it.

---

## 5. Operator namespace — 4 refs

- `operator/gate-b-f5-route1-host-evidence-closure-2026-09-21`
- `operator/gate-b-f5-route1-host-feasibility-2026-09-21`
- `operator/gate-b-read-only-preflight-2026-09-21`
- `operator/gate-b-target-host-read-only-rebind-2026-09-21`

Already part of the 29-ref Gate-B family.

Class: `HISTORICAL_TARGET_HOST_EVIDENCE`.

Preserve final host evidence/failure lessons in Gate-B historical record, then retire operator refs.

---

## 6. Recovery / UX singleton refs

### `recovery/claude-sec-local-20260914`

Class: `PRESERVE_UNTIL_SEC_IMPORT_COMPLETE`.

Prior audit explicitly preserved this because it contains expensive-to-reproduce SEC recovery/census material. Do not delete until Evidence/Identity/SEC Census V2 reconciliation has a durable replacement.

### `ux/intake-20261015`

Class: `LIVE_LAB_PRODUCT_INPUT_REVIEW_REQUIRED`.

Reconcile any unique Owner/UX intake with the canonical Live Lab target; once represented in the product evidence/requirements record, retire as a standalone route if redundant.

---

## 7. Codex namespace — 4 refs

- `codex/test`
- `codex/weather-v3-s0-finish-2026-10-03`
- `codex/weather-v3-s4-forecast-hindcast-2026-10-03`
- `codex/weather-v3-s6-cohort-expansion-2026-10-03`

`codex/test` = `SCIENTIFIC_MEMORY_REQUIRED` due negative/KILL result.

Weather V3 refs = `WEATHER_PREDECESSOR_MEMORY`. Fold scientifically material Weather V3 outcomes/design into Weather archaeology/memory before retirement.

---

## 8. Second-pass conclusion

The major named families plus this second pass account for nearly the entire 229-ref namespace. The remaining small set consists mostly of individual Builder/Blue/Astra/economic/forward refs already named in historical 2026-09 authority/hygiene documents.

Practical consequence:

The future deletion manifest should NOT contain hundreds of one-off human judgments. It should be generated from a small number of workstream consolidation receipts:

1. Weather memory receipt;
2. Gate-B historical authority receipt;
3. P0/Data capability receipt;
4. Live Lab reconciliation receipt;
5. F1/Edge scientific-memory receipt;
6. Research OS/V2 capability import receipt;
7. Legacy reconciliation receipt;
8. Claude opaque-session ancestry review receipt;
9. Parallel/design import receipt;
10. workflow consolidation receipt.

Once these receipts exist, branch deletion can be very aggressive because evidence no longer depends on branch namespace discoverability.