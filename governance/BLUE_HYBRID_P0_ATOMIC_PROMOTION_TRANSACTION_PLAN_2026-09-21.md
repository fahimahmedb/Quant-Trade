# BLUE — HYBRID P0 ATOMIC PROMOTION TRANSACTION PLAN — 2026-09-21

## Status

`PROMOTION_TRANSACTION = PREPARED / NOT_EXECUTED`

`P14D_PROMOTION_READY = FALSE`

This plan defines the exact governance transaction Blue should execute only if
the independent fault-matrix review returns admissible evidence and the final
lineage/consistency checks close.

It deliberately separates PREPARE from COMMIT.

## 1. Why an atomic transaction is required

Promoting the hybrid method changes the current authority from:

`P0_CONTINUOUS_OBSERVATION_MIN = P14D`

to:

`P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1`.

A partial update could leave different entry points giving contradictory
instructions about:
- P14D;
- t0;
- Gate B;
- target-host runbook semantics.

Therefore promotion must be treated as one Blue decision transaction.

## 2. Current precondition snapshots

At preparation time the following Blue blobs were observed:

- `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`
  blob `2265e80eefee62a0fa6c3648b8619dee31579878`;
- `handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`
  blob `113022175788b9ac26c8fd1fe4faa962b9a99e16`;
- `governance/BLUE_P14D_FINAL_RED_TEAM_2026-09-21.md`
  blob `444f0a2de6cb31d86cddab7d00f38060d77e60f8`;
- `governance/BLUE_P14D_HYBRID_AMENDMENT_CANDIDATE_V2_2026-09-21.md`
  blob `113b0294e5a13965305af90e84e87d9875e504e9`;
- `governance/BLUE_P14D_HYBRID_PROMOTION_CHECKLIST_2026-09-21.md`
  blob `9b8e38d587c5069bb5fc502693c02e389c7d82c9`;
- `governance/BLUE_GATE_B_TO_T0_ENTRANCE_BINDING_SPEC_2026-09-21.md`
  blob `92e36cc5bf478efdd788a5aeae39667f401cebc0`;
- `governance/BLUE_TARGET_HOST_RUNBOOK_RECONCILIATION_PLAN_2026-09-21.md`
  blob `92fde6e3cac71836483d8cd8e754f542414d14aa`.

These are conflict-detection snapshots, not permanent expected values.
Before execution, fetch current blobs again and reconcile any legitimate newer
changes. Never overwrite later evidence merely because this plan contains older
blob IDs.

## 3. Final decision inputs required

Required before execution:

- Gate A v4 frozen candidate:
  `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`;
- Gate A v4 Blue repository PASS;
- independent V4 Astra final HEAD:
  `afe25984b0ddd261fda143d858106c3c71e45149`;
- Codex matrix delivery:
  `686f77a383fb0e8c7ecd1b4a737585bedb544701`;
- Codex final checkpoint:
  `e5c4c720e758cd8ab3f0e04faf541b26e204be16`;
- final independent fault-matrix review HEAD/verdict;
- exact final evidence lineage;
- resolution of any final MISSING_PROOF.

## 4. Promotion transaction — files

When and only when all promotion gates pass:

### A. Create authoritative amendment

Create a NEW authority file, rather than silently relabeling the draft:

`governance/P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT_2026-09-21.md`

It must:
- explicitly supersede fixed P14D for future P0 qualification;
- bind the exact evidence lineage used for adoption;
- preserve Gate B before t0;
- use `PRECOMMITTED_NEXT_AUTHORIZED_QUALIFYING_LAUNCH`;
- preserve Gate C real-event requirements;
- define Gate D;
- define post-qualification surveillance/reopen semantics;
- preserve proof-domain separation.

### B. Update current governance

Update:
`governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`

Required state after promotion:
- fixed P14D = HISTORICAL / SUPERSEDED FOR FUTURE QUALIFICATION;
- `P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1`;
- `t0 = NOT DECLARED`;
- `GATE_B = NOT_STARTED`;
- target-host readiness still false until Gate B;
- no Product/capital authority change.

### C. Update Blue master state

Update:
`handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`

Record exact amendment commit/reference and next action:
reconcile authoritative target-host runbook against exact accepted candidate,
then Gate B.

### D. Close promotion checklist

Update:
`governance/BLUE_P14D_HYBRID_PROMOTION_CHECKLIST_2026-09-21.md`

Only checked evidence with exact refs may become complete.

### E. Reissue target-host operational authority

Do NOT mutate the old V3-pinned runbook into looking historically V4.

Prefer creating new current files, for example:

`governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md`

`governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md`

They must pin the exact accepted V4 lineage and incorporate the t0 precommit
semantics.

The old 2026-09-20 V3 runbook remains historical evidence and must be labeled
superseded, not rewritten as if it always targeted V4.

## 5. No implicit t0

The promotion transaction MUST end with:

`t0 = NOT DECLARED`

Adopting a qualification method is not executing Gate B and is not starting the
qualifying live interval.

## 6. Abort conditions

Abort promotion if:
- independent fault-matrix review finds REAL_DEFECT;
- independent review finds unresolved repository MISSING_PROOF material to the
  hybrid substitution;
- evidence lineage cannot be bound;
- current governance changed incompatibly during the transaction;
- candidate SHA differs;
- any update would imply target-host evidence not actually collected.

## 7. Post-promotion next action

Only after successful promotion:

1. issue exact-candidate Gate B contract/runbook;
2. execute destructive/offline Gate B on the real target host;
3. Blue receive Gate B evidence;
4. precommit the unique qualifying launch;
5. only that launch event establishes t0;
6. Gate C begins immediately.

## 8. Current non-action

Until a Blue promotion commit exists:

`P0_CONTINUOUS_OBSERVATION_MIN = P14D`

remains current authority.

No command in this plan authorizes target-host mutation.
