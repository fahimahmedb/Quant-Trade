# BLUE — HYBRID P0 PRE-PROMOTION EVIDENCE BINDER — 2026-09-21

## Status

`HYBRID_PRE_PROMOTION_BINDER = PREPARED / NOT_AUTHORITATIVE_AMENDMENT`

`P14D_PROMOTION_READY = FALSE`

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

`t0 = NOT DECLARED`

Purpose: bind every proof domain already closed before the independent Astra
review of the Codex fault-matrix package returns.

This file is a point-in-time evidence binder, not the superseding amendment.

## 1. Architecture authority

North Star blob:
`QUANT_NORTH_STAR.md@8295041a8d253636d8f8aab941b811dce64939d9`.

Terminal objective and proof-domain separation remain unchanged.

## 2. Frozen production candidate

Candidate ref:
`blue/p0-gate-a-v4-frozen-2026-09-20`

Candidate SHA:
`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Git tree:
`4d15ef6f471213ee6ab56337b555d2906ef9bf16`

Selected candidate exact-head CI:
`35536353538 = COMPLETED / SUCCESS`

Blue Builder reception:
`handoff/BLUE_GATE_A_V4_RECEPTION_2026-09-20.md`

## 3. Independent Gate A v4 correction review

Independent Astra final HEAD:
`afe25984b0ddd261fda143d858106c3c71e45149`

Exact-head runs:
- `35545297473 = COMPLETED / SUCCESS` — Astra Gate A v4 independent audit;
- `35545297451 = COMPLETED / SUCCESS` — SEC P0 pre-t0 gate.

Independent verdict:
`AUDIT_GATE_A_V4 = PASS_REPOSITORY_CORRECTION`

Blue reception:
`handoff/BLUE_GATE_A_V4_FINAL_INDEPENDENT_RECEPTION_2026-09-21.md`

Blue repository disposition:
`GATE_A_V4_REPOSITORY_DISPOSITION = PASS`

This proof domain is closed repository-side only.

## 4. Hybrid accelerated evidence already delivered

Durable predecessor:
`builder/p0-hybrid-qualification-harness-2026-09-20@d4d446c412258b2a9e4792cdcd9e2442ef24b615`

Exact-head CI:
`35541420721 = COMPLETED / SUCCESS`

Closed predecessor evidence:
- timing matrix;
- calendar matrix;
- 14 virtual days;
- 2,016 obligations;
- accountable clean horizon;
- zero unexplained obligations;
- stable fingerprint;
- complete coverage;
- negative unanswered-obligation discriminant.

## 5. Codex fault-matrix delivery

Delivery SHA:
`686f77a383fb0e8c7ecd1b4a737585bedb544701`

Delivery exact-head CI:
`35544777822 = COMPLETED / SUCCESS`

Final Codex checkpoint HEAD:
`e5c4c720e758cd8ab3f0e04faf541b26e204be16`

Final checkpoint exact-head CI:
`35545784230 = COMPLETED / SUCCESS`

Delta from predecessor is limited to:
- `tools/p0_qualification/gate_a/fault_matrix.py`;
- `tools/p0_qualification/evidence/gate_a/fault_matrix.json`;
- `handoff/BUILDER_CODEX_P0_HYBRID_FAULT_MATRIX_CHECKPOINT_2026-09-21.md`.

Production code changed:
`FALSE`.

Received matrix:
- rows = 19;
- existing discriminating proofs = 15;
- new discriminating proofs = 4;
- builder-declared missing proof = 0;
- builder-declared real defects = 0;
- restart_burst_limit = repository-side new discriminating proof;
- physical service-manager behavior remains target-host residual.

Blue reception:
`handoff/BLUE_CODEX_P0_HYBRID_FAULT_MATRIX_RECEPTION_2026-09-21.md`

Disposition:
`PASS_FOR_INDEPENDENT_REVIEW`

## 6. Independent fault-matrix review — OPEN

Branch:
`astra/p0-hybrid-fault-matrix-independent-review-2026-09-21`

Mission dispatch commit:
`2f6c134f1202c6e22943638379be4e3435ecded0`

Expected independent final handoff:
`handoff/ASTRA_P0_HYBRID_FAULT_MATRIX_INDEPENDENT_REVIEW_2026-09-21.md`

Current state:
`OPEN / NOT_YET_EVIDENCED`

This is the remaining independent repository-evidence gate before method
promotion can be considered.

## 7. Exact input-tree proof — important non-transfer rule

The committed file:

`handoff/SEC_FORM4_P0_VERIFICATION.json`

at the V4/Codex lineage is NOT the exact-head V4 verification artifact.

Its committed contents still identify:
- `verified_sha = 1450af4a7352ccbe938030a49f774c33b7d61a80`;
- `verified_tree_digest = sha256:36e5f26720f907b40aac81b40a26bff05d155e305b00c2366fa1a71266ef6858`.

Therefore these values MUST NOT be attributed to candidate
`4d06bdbf...`.

The candidate workflows generated exact-head verification artifacts at runtime.
Their existence is execution evidence, but the exact candidate input-tree digest
must be recovered from the exact-head CI artifact or regenerated under the
authoritative verifier before a document claims that digest.

Current classification:

`CANDIDATE_EXACT_VERIFIED_INPUT_TREE_DIGEST = UNKNOWN_IN_DURABLE_PUBLIC_BINDER`

`CLASSIFICATION = MISSING_BINDING_METADATA / NOT_A_PRODUCTION_DEFECT`

This does not negate the known Git tree
`4d15ef6f471213ee6ab56337b555d2906ef9bf16`.

It prevents a stale verification artifact from being silently transferred to V4.

## 8. Hybrid method governance

Final Blue Red Team:
`governance/BLUE_P14D_FINAL_RED_TEAM_2026-09-21.md`

Candidate amendment:
`governance/BLUE_P14D_HYBRID_AMENDMENT_CANDIDATE_V2_2026-09-21.md`

Promotion checklist:
`governance/BLUE_P14D_HYBRID_PROMOTION_CHECKLIST_2026-09-21.md`

Gate-B-to-t0 candidate:
`governance/BLUE_GATE_B_TO_T0_ENTRANCE_BINDING_SPEC_2026-09-21.md`

Target-host reconciliation plan:
`governance/BLUE_TARGET_HOST_RUNBOOK_RECONCILIATION_PLAN_2026-09-21.md`

No fixed P14D authority has yet been superseded.

## 9. Remaining binary gates

Before promotion:
1. independent fault-matrix verdict must be received and Blue-disposed;
2. exact candidate verification/input-tree binding metadata must be resolved
   or the promotion contract must explicitly establish why Git-tree binding is
   the relevant repository identity and defer verifier digest to Gate B;
3. final consistency review must incorporate independent fault-matrix findings;
4. current-state documents must be updated atomically with the superseding
   amendment.

If Astra returns a REAL_DEFECT or blocking MISSING_PROOF, promotion stops.

## 10. Safety state

`GATE_A_V4_REPOSITORY_DISPOSITION = PASS`

`TARGET_HOST_READY = FALSE`

`GATE_B = NOT_STARTED`

`P14D_PROMOTION_READY = FALSE`

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

`t0 = NOT DECLARED`

`PRODUCT_INTEGRATION = PAUSED`

`REAL_CAPITAL_AUTHORIZED = FALSE`
