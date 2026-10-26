# BLUE GATE A V4 BUILDER RECEPTION — PENDING EXACT-HEAD CI — 2026-09-20

Authority: Blue / Mission Control.
Architectural authority: `QUANT_NORTH_STAR.md`.
Context root: `handoff/BLUE_CONTEXT_REACQUISITION_2026-09-20.md`.

Status:
`BLUE_V4_RECEPTION = PENDING_FINAL_EXACT_HEAD_CI`

## 1. Builder delivery received

Builder branch:
`builder/p0-effective-unit-digest-stability-v4-2026-09-20`

Exact frozen implementation baseline:
`2da079d8ad75c69eb3fc2990c512735cb4bdc02b`

Implementation commit:
`0bdd397d7409b01529c1f958c68781499679a95e`

Current final Builder branch HEAD:
`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

The final HEAD is one documentation-only commit after the implementation commit. Exact delta `0bdd397d...4d06bdbf` contains only:
- `handoff/BUILDER_P0_EFFECTIVE_UNIT_DIGEST_STABILITY_V4_CHECKPOINT_2026-09-20.md`;
- `handoff/BUILDER_P0_EFFECTIVE_UNIT_DIGEST_STABILITY_V4_HANDOFF_2026-09-20.md`.

No production/test code changed after `0bdd397d`.

## 2. Exact final-head CI

Workflow:
`SEC P0 pre-t0 gate`

Final-head run:
`35536353538`

Bound SHA:
`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Status at this Blue checkpoint:
`IN_PROGRESS / NO CONCLUSION`

Therefore Blue MUST NOT yet declare:
`PASS_FOR_INDEPENDENT_ASTRA_REVIEW`

The earlier implementation-head run:
`35535347844 @ 0bdd397d7409b01529c1f958c68781499679a95e = COMPLETED / SUCCESS`

is strong evidence for the implementation commit, but it does not replace exact-head CI for the final Builder delivery HEAD.

## 3. Blue preliminary independent scope review

Exact baseline-to-final delta is linear:
`2da079d8... -> b3fc705f... -> 0bdd397d... -> 4d06bdbf...`

Production/test delta relative to v3 is limited to:
- `deploy/quant_sec_supervisor.py`;
- `tests/test_astra_pre_t0.py`;
- mechanical generated proof-inventory update in `STATE.md`.

Mission/handoff documents are additional documentation only.

No Blue governance, Product integration, Forward/Economic runtime, P14D authority, Gate B, t0 or real-capital code was changed by the Builder implementation.

Preliminary scope verdict:
`SCOPE_CONFORMANT = TRUE`

## 4. Defect correction reviewed by Blue

Original target-host REAL_DEFECT:
raw `systemctl show ExecStart` serialization entered the effective-unit digest and carried mutable runtime fields:
- `start_time`;
- `stop_time`;
- `pid`;
- `code`;
- `status`.

Builder adds `_canonicalize_exec_start()` and removes those transient observation keys before the effective-unit definition is hashed.

The corrected path still preserves the pre-existing fail-closed checks for:
- loaded fragment byte equality;
- no unbound drop-ins;
- Restart / RestartUSec;
- StartLimitIntervalUSec / StartLimitBurst;
- KillMode / KillSignal;
- TimeoutStopUSec;
- WorkingDirectory;
- EnvironmentFiles.

It also tightens `--qualifying` from substring recognition to an exact argv token.

Preliminary Blue assessment:
`FIX_MECHANISM_MATCHES_REPRODUCED_DEFECT = TRUE`

This is not independent certification.

## 5. Builder evidence reviewed

Builder final handoff reports:
- old defect independently reproduced against unmodified baseline;
- same semantic ExecStart with changed runtime metadata produced different digests on baseline;
- corrected implementation produced identical digest;
- 12 new Phase8 discriminating tests;
- discriminating-power replay: 4 relevant tests fail against baseline, then pass with fix;
- full local suite: 423 tests PASS;
- SEC P0 lane: 287 PASS;
- V1 demo: 35/35 PASS;
- implementation-head exact CI run `35535347844 = SUCCESS`.

Blue verified the final handoff exists and that the final delivery commit is documentation-only over the code SHA.

## 6. Residual review targets for Astra

If final-head CI succeeds and Blue promotes this to independent review, Astra must attack at least:

1. `_canonicalize_exec_start()` parser fidelity:
   - semicolon splitting;
   - repeated/malformed structs;
   - unexpected but valid systemd formatting;
   - unknown configuration fields.

2. exact `argv[]` semantic binding:
   - altered executable;
   - altered root/path;
   - qualifying flag variants;
   - whitespace/escaping behavior relevant to the frozen unit.

3. stability versus real semantic drift:
   - transient runtime observations must not move digest;
   - actual loaded command/configuration drift must still fail closed or move the digest.

4. target-host defect reproduction:
   - independently reproduce the original old-code mechanism from evidence/fixture;
   - do not use Builder conclusions as certification.

5. no regression of deployment authority / fingerprint materialization ordering.

The current frozen repository unit has one fixed `ExecStart` directive and byte equality remains mandatory, so unsupported hypothetical unit structures are not automatically blockers unless they can affect the current frozen service contract.

## 7. Blue decision boundary

If and only if run `35536353538` completes SUCCESS on exact final HEAD `4d06bdbf...`, Blue may perform the final reception transition:

`BLUE_V4_RECEPTION = PASS_FOR_INDEPENDENT_ASTRA_REVIEW`

At that point Blue should:
- freeze the exact Builder final delivery candidate/ref without modifying candidate bytes;
- create an independent Astra audit branch from the exact frozen candidate;
- write the Astra v4 mission contract;
- require independent defect reproduction and adversarial tests;
- keep target-host qualification paused until Astra + subsequent Blue disposition.

Until then:

`BLUE_V4_RECEPTION = PENDING_FINAL_EXACT_HEAD_CI`

`t0 = NOT_DECLARED`

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

`TARGET_HOST_READY = FALSE`

`PRODUCT_INTEGRATION = PAUSED`

`REAL_CAPITAL_AUTHORIZED = FALSE`
