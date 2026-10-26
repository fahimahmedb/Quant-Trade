# BLUE GATE A V4 BUILDER RECEPTION — 2026-09-20

Authority: Blue / Mission Control.
Architectural authority: `QUANT_NORTH_STAR.md`.

## 0. Disposition

`BLUE_GATE_A_V4_BUILDER_RECEPTION = PASS_FOR_INDEPENDENT_ASTRA_REVIEW`

This is **not** Gate A v4 PASS.

It means Blue accepts the Builder delivery as sufficiently scoped, reproducible and exact-head verified to become the immutable input of an independent audit.

`t0 = NOT DECLARED`

`TARGET_HOST_READY = FALSE`

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

`PRODUCT_INTEGRATION = PAUSED`

`REAL_CAPITAL_AUTHORIZED = FALSE`

## 1. Exact lineage

Rejected-for-target-host historical v3 baseline:

`2da079d8ad75c69eb3fc2990c512735cb4bdc02b`

Corrective implementation commit:

`0bdd397d7409b01529c1f958c68781499679a95e`

Selected final Builder delivery candidate:

`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Frozen v4 ref:

`blue/p0-gate-a-v4-frozen-2026-09-20@4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Builder branch subsequently advanced to `b10cde0dd193714346abdfe87afb841482e9b7c8` only to update its handoff/checkpoint with the CI result of `4d06bdbf...`.

That later commit changes only the two Builder handoff/checkpoint files.

Blue deliberately does **not** move the candidate to `b10cde0d...`.

Reason: `4d06bdbf...` is already the Builder-declared `DELIVERY_SHA`, contains the correction plus final handoff/checkpoint, and has exact-head CI SUCCESS. Advancing the candidate every time a documentation commit records the previous commit's CI would create an infinite documentation/CI self-reference loop.

Therefore:

`AUDITED_CANDIDATE = 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

`POST_DELIVERY_DOC_UPDATE_b10cde0d = EVIDENCE_ONLY / NOT_CANDIDATE`

No proof from `b10cde0d` is required to establish the code candidate selected here.

## 2. Exact CI evidence

Implementation-head run:

`35535347844 @ 0bdd397d7409b01529c1f958c68781499679a95e = COMPLETED / SUCCESS`

Selected final-delivery run:

`35536353538 @ 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072 = COMPLETED / SUCCESS`

The final-delivery run completed all workflow steps successfully:

- fail-closed check with no SEC identity;
- generated schema drift;
- status artifact freshness;
- full unit suite;
- SEC P0 lane suite;
- V1 end-to-end regression;
- exact-head verification artifact generation;
- artifact upload;
- committed-placeholder restoration;
- clean working tree.

The delta `0bdd397d...4d06bdbf` is documentation-only:

- `handoff/BUILDER_P0_EFFECTIVE_UNIT_DIGEST_STABILITY_V4_CHECKPOINT_2026-09-20.md`;
- `handoff/BUILDER_P0_EFFECTIVE_UNIT_DIGEST_STABILITY_V4_HANDOFF_2026-09-20.md`.

No code/test semantics changed between the implementation-head SUCCESS and final-delivery SUCCESS.

## 3. Blue reception review

Blue independently checked the baseline-to-delivery changed-file surface.

Implementation delta is limited to:

- `deploy/quant_sec_supervisor.py`;
- `tests/test_astra_pre_t0.py`;
- mechanically regenerated `STATE.md`;
- mission/handoff/checkpoint documentation.

No Forward/Economic/Product integration, P14D authority, target-host state, Gate B, t0 or real-capital code was modified.

`SCOPE_CONFORMANT = TRUE`

## 4. Corrective mechanism

The target-host REAL_DEFECT was:

`_effective_systemd_definition()` hashed raw `systemctl show ExecStart`, which mixes stable configuration with mutable runtime observations.

Mutable fields observed on the target host included:

- `start_time`;
- `stop_time`;
- `pid`;
- `code`;
- `status`.

The Builder correction canonicalizes the structured `ExecStart` representation and removes those transient observation fields before hashing.

It preserves the existing fail-closed checks for:

- repository unit / loaded fragment byte equality;
- unbound drop-ins;
- Restart policy;
- RestartUSec;
- StartLimitIntervalUSec;
- StartLimitBurst;
- KillMode;
- KillSignal;
- TimeoutStopUSec;
- WorkingDirectory;
- EnvironmentFiles.

It also tightens `--qualifying` recognition from substring presence to an exact argv token.

Blue preliminary assessment:

`FIX_MECHANISM_MATCHES_REPRODUCED_DEFECT = TRUE`

This is not independent certification.

## 5. Builder evidence accepted for audit input

Builder reports, and Blue verified the handoff contains:

- independent reproduction of the old digest-instability mechanism against the unmodified baseline;
- 12 new Phase8 discriminants;
- explicit discriminating-power replay showing four relevant tests fail against baseline then pass with the correction;
- local full suite 423 PASS;
- local SEC P0 lane 287 PASS;
- V1 demo 35/35 PASS;
- two exact-head GitHub CI runs SUCCESS as listed above.

These are Builder/repository evidence only.

## 6. Independent audit requirements

Astra must not begin from the assumption that the fix is correct.

At minimum, independently test:

1. **Original-defect reproduction**
   - reproduce the old target-host mechanism from the evidence/fixture without relying on Builder's conclusion.

2. **Transient-metadata stability**
   - stable executable/argv/configuration with different PID/timestamps/exit status must produce the same effective-unit digest.

3. **Real semantic drift**
   - executable/argv/root/qualifying semantic drift must be rejected or alter the accepted digest as intended.

4. **Parser fidelity**
   - adversarially test brace/semicolon parsing, malformed/repeated structs, unknown configuration fields, whitespace and escaping relevant to the frozen service form.

5. **Qualifying token**
   - altered/substr-lookalike qualifying flags must not pass.

6. **Existing systemd authority**
   - fragment byte mismatch, drop-ins, workdir, env-file, restart/timing/kill semantics remain fail-closed.

7. **Fingerprint/deployment authority ordering**
   - no new bypass or invalidation was introduced around materialization, one-use deployment authority or child launch authority.

8. **Second-order bypass search**
   - search beyond the Builder's named regression list.

Astra defect classes remain:

`REAL_DEFECT / TEST_DEFECT / MISSING_PROOF / TARGET_HOST_ONLY / NON_ISSUE`

Astra must not modify the frozen production candidate while auditing it.

## 7. Target-host boundary

This reception does not claim the corrected code works on the real target host.

Only after independent Astra review and a later Blue disposition may target-host qualification restart.

The old v3 target-host failure evidence remains preserved and must not be overwritten or presented as a v4 result.

## 8. P14D and repository-cleanup relationship

P14D hybrid-method review remains active in parallel.

Repository hygiene may also execute in parallel from the administrative clone under:

`governance/REPOSITORY_HYGIENE_EXECUTION_RUNBOOK_2026-09-20.md`

Neither workstream may mutate the frozen v4 candidate or the P0 target runtime.

## 9. Next transition

Next proof event:

`INDEPENDENT_ASTRA_GATE_A_V4_AUDIT`

Only after Astra returns does Blue decide:

- accept v4 for target-host re-entry;
- return a reproduced defect to Builder;
- or classify residual target-host-only proof.

No Gate A v4 PASS is declared here.
