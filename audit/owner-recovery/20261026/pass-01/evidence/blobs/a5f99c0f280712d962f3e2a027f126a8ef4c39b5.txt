# ASTRA — P0 HYBRID FAULT MATRIX INDEPENDENT REVIEW MISSION — 2026-09-21

Role: independent Astra / Red Team reviewer.
Decision authority: Blue / Mission Control.
Architectural authority: `QUANT_NORTH_STAR.md`.

## 0. Immutable audit object

Builder/Codex predecessor:
`builder/p0-hybrid-qualification-harness-2026-09-20@d4d446c412258b2a9e4792cdcd9e2442ef24b615`

Codex delivery commit:
`686f77a383fb0e8c7ecd1b4a737585bedb544701`

Codex final checkpoint HEAD:
`builder/codex-p0-hybrid-fault-matrix-2026-09-21@e5c4c720e758cd8ab3f0e04faf541b26e204be16`

Frozen production candidate bound by the evidence:
`blue/p0-gate-a-v4-frozen-2026-09-20@4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Independent review branch:
`astra/p0-hybrid-fault-matrix-independent-review-2026-09-21`

This branch is created exactly from the Codex final checkpoint HEAD.

Do not modify the Builder/Codex branch or frozen production candidate.
Audit-only tests/scripts/evidence/checkpoints/handoff may be committed here.

## 1. Read first

Read:

1. `QUANT_NORTH_STAR.md`
2. current Blue:
   `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`
3. Blue Codex reception:
   `handoff/BLUE_CODEX_P0_HYBRID_FAULT_MATRIX_RECEPTION_2026-09-21.md`
4. Codex checkpoint:
   `handoff/BUILDER_CODEX_P0_HYBRID_FAULT_MATRIX_CHECKPOINT_2026-09-21.md`
5. evidence artifact:
   `tools/p0_qualification/evidence/gate_a/fault_matrix.json`
6. harness:
   `tools/p0_qualification/gate_a/fault_matrix.py`
7. predecessor checkpoint:
   `handoff/BUILDER_P0_HYBRID_QUALIFICATION_CHECKPOINT_3_2026-09-20.md`
8. current hybrid promotion checklist:
   `governance/BLUE_P14D_HYBRID_PROMOTION_CHECKLIST_2026-09-21.md`

Do not start from Codex's conclusion.

## 2. Mission

Determine whether the Codex fault-matrix package honestly closes the repository-side Gate-A fault-matrix blocker.

You are auditing the evidence package, not re-certifying the entire Gate A v4 correction.

The key claims to attack are:

- 19 required rows are actually covered;
- 15 existing citations are discriminating and target the right property;
- 4 new discriminants are real discriminants rather than tautologies;
- `MISSING_PROOF_COUNT = 0` is honest;
- no row that should be `TARGET_HOST_ONLY` is incorrectly claimed as repository proof;
- `restart_burst_limit` is honestly closed repository-side;
- artifact generation is deterministic/reproducible;
- evidence is bound to exact frozen candidate `4d06bdbf...`;
- no production file was changed;
- the package does not silently transfer proof from another SHA.

## 3. Mandatory attacks

### F1 — lineage and scope

Verify independently:

- merge-base(predecessor, Codex) = predecessor SHA;
- delivery and final checkpoint relationship;
- final checkpoint is docs-only over delivery;
- changed paths are exactly the bounded harness/evidence/checkpoint paths;
- no existing `src/`, `deploy/`, `scripts/`, production test, workflow or completed timing/calendar/long-history harness path was modified.

### F2 — row completeness

Compare the matrix rows against the required Blue minimum:

- raw write;
- file fsync;
- hardlink/publication;
- directory fsync;
- envelope append;
- attempt completion;
- cursor advancement;
- successor scheduler obligation;
- cooldown persistence;
- supervisor death;
- child death;
- torn/corrupt journal;
- duplicate replay;
- state newer than journal;
- journal newer than state;
- missing fingerprint;
- foreign fingerprint;
- missing deployment authority;
- restart burst limit.

No requirement may disappear by renaming.

### F3 — existing-proof citation fidelity

For each of the 15 `EXISTING_DISCRIMINATING_PROOF` rows:

- resolve the cited test;
- inspect what the test actually proves;
- determine whether it discriminates the named property;
- reject wrong-target or stale citations;
- do not accept test-name semantics without inspecting the body when material.

If a citation is insufficient:
`MISSING_PROOF` or `TEST_DEFECT`, not PASS.

### F4 — new file-fsync discriminant

Attack the new regular-file fsync discriminant.

Ask:
- can it pass without the production path actually calling fsync at the required boundary?
- does monkeypatching intercept the exact primitive production uses?
- does the negative/failure case prove that acknowledgment/publication does not escape?
- is the target/staging-state assertion strong enough?

Independently alter/bypass the expected primitive if useful to demonstrate discriminating power.

### F5 — state/journal divergence discriminants

Attack both:
- state newer than journal;
- journal newer than state.

Require fail-closed behavior tied to the actual production loader/commit lineage.

Check for:
- fixture-only behavior;
- impossible synthetic state;
- assertion on the wrong error path;
- silent self-repair;
- asymmetry not covered by the shared discriminant.

### F6 — restart_burst_limit

This is high priority.

Codex claims:
`NEW_DISCRIMINATING_PROOF / FACT / NON_ISSUE`.

Independently verify:
- the frozen constant/value is really 5;
- exact loaded value 5 is accepted;
- at least one wrong value is rejected;
- the harness reaches the real systemd-definition validation path, not a reimplemented oracle;
- the cited runtime guard is actually relevant;
- repository proof is not being confused with physical systemd restart behavior.

If repository binding is closed but physical behavior remains host-only, state that split explicitly.

### F7 — missing-proof challenge

Try actively to force at least one row into:
- `MISSING_PROOF`;
- or `TARGET_HOST_ONLY`.

Do not accept `MISSING_PROOF_COUNT = 0` because the artifact says so.

Ask for each row:
"What exact property remains unproved after this repository test?"

Residual target-host physical behavior may remain without making the repository-side row missing, but the boundary must be explicit and honest.

### F8 — artifact reproducibility

Run the harness independently at least twice.

Verify:
- byte-identical or otherwise contractually deterministic artifact;
- report digest stable;
- frozen candidate SHA stable;
- no current time/random/environment leakage except explicitly bounded metadata;
- no branch-name-only identity.

### F9 — artifact self-consistency

Cross-check:
- row count;
- proof-class counts;
- defect-class counts;
- restart-burst disposition;
- no-t0/no-P14D/no-target-host claims;
- all row reproduction commands;
- exact SHA fields;
- report digest calculation.

Look for duplicated row, missing row, inconsistent counts or stale metadata.

### F10 — discriminating-power falsification

For each of the four new discriminants, try to create a minimal mutation or monkeypatch that should violate the claimed invariant and confirm the discriminant turns red.

A harness that only passes on the good code without demonstrated sensitivity may be `MISSING_PROOF`.

Do not edit the frozen production candidate permanently; use audit-only temporary mutation/patching/discriminants.

## 4. Classification

Every material finding must be classified:

- `REAL_DEFECT`
- `TEST_DEFECT`
- `MISSING_PROOF`
- `TARGET_HOST_ONLY`
- `NON_ISSUE`

Also distinguish:
FACT / CLAIM / INFERENCE / RECOMMENDATION / UNKNOWN.

## 5. Independence boundary

The prior Astra v4 audit is already closed at:

`astra/p0-gate-a-v4-independent-audit-2026-09-20@afe25984b0ddd261fda143d858106c3c71e45149`

Do not redo the entire v4 audit.

Use it only as already-established context where relevant.

This mission is specifically about the new fault-matrix evidence package.

## 6. Test requirements

At minimum run:

- the fault matrix harness;
- all cited tests or a justified exact subset plus automated citation resolution;
- independent red/green discriminants for the four new proofs;
- artifact reproducibility check;
- focused tests needed by findings.

Run broader regression only if the audit changes executable audit code or finds a reason to suspect a regression.

Green CI is execution evidence, not proof by itself.

## 7. REAL_DEFECT stop rule

If a production REAL_DEFECT is independently reproduced:

1. preserve the red evidence;
2. classify it;
3. commit/push audit evidence;
4. STOP;
5. do not repair production.

Return to Blue.

## 8. Durable checkpoint / handoff

If long, push checkpoint(s).

Final handoff:

`handoff/ASTRA_P0_HYBRID_FAULT_MATRIX_INDEPENDENT_REVIEW_2026-09-21.md`

Must include:

- exact Codex delivery SHA;
- exact Codex final checkpoint HEAD;
- exact final Astra review HEAD;
- ancestry/scope verification;
- F1–F10 results;
- row-by-row or complete summary classification;
- independent disposition of the four new discriminants;
- independent disposition of `restart_burst_limit`;
- exact MISSING_PROOF / TARGET_HOST_ONLY residuals;
- reproducibility result;
- focused test results;
- CI run ID/status if audit workflow is added;
- final verdict.

Allowed final verdicts:

- `ASTRA_FAULT_MATRIX = PASS_REPOSITORY_EVIDENCE`
- `ASTRA_FAULT_MATRIX = BLOCKED_REAL_DEFECT`
- `ASTRA_FAULT_MATRIX = BLOCKED_MISSING_PROOF`

Do not declare P14D amended.
Do not declare Gate B.
Do not declare t0.
Do not declare target-host readiness.
Do not authorize capital.

After final handoff and exact-head CI observation, STOP and return control to Blue.
