# ASTRA GATE A V4 INDEPENDENT AUDIT MISSION — 2026-09-20

Role: independent Astra / Red Team auditor.
Decision authority: Blue / Mission Control.
Architectural authority: `QUANT_NORTH_STAR.md`.

## 0. Immutable audited candidate

Frozen candidate:

`blue/p0-gate-a-v4-frozen-2026-09-20@4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Audit branch:

`astra/p0-gate-a-v4-independent-audit-2026-09-20`

The audit branch was created exactly from the frozen candidate.

Do not modify the frozen branch.

Audit-only tests, scripts, checkpoints and handoffs may be committed on the Astra branch, but production corrections are out of scope.

## 1. Read first

Before making any finding, read:

1. `QUANT_NORTH_STAR.md`
2. from current Blue:
   `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`
3. from current Blue:
   `handoff/BLUE_GATE_A_V4_RECEPTION_2026-09-20.md`
4. from current Blue:
   `handoff/BLUE_TARGET_HOST_REAL_DEFECT_EFFECTIVE_UNIT_DIGEST_2026-09-20.md`
5. Builder mission:
   `handoff/BUILDER_P0_EFFECTIVE_UNIT_DIGEST_STABILITY_V4_MISSION_2026-09-20.md`
6. Builder final handoff as present on the frozen candidate:
   `handoff/BUILDER_P0_EFFECTIVE_UNIT_DIGEST_STABILITY_V4_HANDOFF_2026-09-20.md`
7. `governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md`
8. `governance/TARGET_HOST_RODAGE_ENTRANCE_CONTRACT_2026-09-20.md`

Builder conclusions are claims/evidence inputs, not audit conclusions.

## 2. Historical defect

The historical v3 target-host candidate was:

`2da079d8ad75c69eb3fc2990c512735cb4bdc02b`

Real target-host evidence showed the materialized effective-unit digest changed from:

`sha256:33d166b68a337947f7737ae659b386df88545867012ce88d0b30bcdbcf070b3d`

to:

`sha256:c6394ef740c3f66c35e2920ebd4f21d27ff1417d11be5ab93b457f0f7e355c22`

without loaded unit byte drift or drop-ins.

Restricted defect-artifact binding:

`sha256:cb402bb3151a59708c6e3b6406323fe8671680b0e2785c9bb92ff47064639442`

Blue classified the defect as `REAL_DEFECT`.

Do not merely restate that classification. Reproduce the mechanism independently from source/fixture evidence.

## 3. Mission

Determine whether candidate `4d06bdbf...` actually closes the effective-unit-digest instability without creating a new bypass, false stability, or weakening of acquisition-critical systemd binding.

The audit is not limited to proving the 12 Builder tests pass.

Search actively for:
- wrong-target tests;
- parser ambiguities;
- semantic drift accidentally normalized away;
- runtime observations still leaking into the digest;
- systemd representation variants;
- authority/materialization regressions;
- second-order bypasses not named by Builder.

## 4. Mandatory independent attacks

### A1 — old-defect reproduction

Against the historical implementation or an independently reconstructed old-code discriminant:

- same semantic unit;
- changed only transient execution observations;
- demonstrate digest instability.

The reproduction must not depend on the corrected function to define expected behavior.

### A2 — corrected transient stability

On frozen v4:

- change `start_time`;
- `stop_time`;
- `pid`;
- `code`;
- `status`;

while holding configuration semantics fixed.

Require identical effective-unit digest.

### A3 — real command drift

Attack:
- executable path;
- Python interpreter path;
- supervisor path;
- `--root`;
- root argument value;
- `--qualifying`;
- extra acquisition-relevant argv;
- removed argv.

Show that real semantic changes are not silently normalized into the same accepted state.

### A4 — parser fidelity

Adversarially probe `_canonicalize_exec_start()` with systemd-like representations relevant to the current frozen unit:

- whitespace variation;
- empty/missing fields;
- duplicated fields;
- unknown configuration fields;
- malformed braces;
- repeated structs;
- semicolons;
- values containing delimiters/escaping where systemd may emit them.

Distinguish:
- current-unit reachable defect;
- hypothetical future-unit limitation.

Do not promote an unreachable hypothetical into a current blocker without evidence.

### A5 — exact qualifying authority

Try:
- `--qualifying-disabled`;
- prefix/suffix lookalikes;
- duplicate flags;
- whitespace variants;
- value-like tokens.

Confirm the frozen service's qualifying semantics cannot pass by substring accident.

### A6 — existing systemd contract regression

Re-attack:
- repository fragment byte mismatch;
- non-empty DropInPaths;
- WorkingDirectory drift;
- EnvironmentFiles drift;
- Restart drift;
- RestartUSec;
- StartLimitIntervalUSec;
- StartLimitBurst;
- KillMode;
- KillSignal;
- TimeoutStopUSec;
- unavailable/unparseable systemctl output.

### A7 — digest binding

Check that:
- transient observations do not move digest;
- unknown stable configuration fields are either bound or rejected appropriately;
- canonicalization ordering does not make semantically different configurations collide;
- multiple accepted representations of identical semantics do not create accidental instability.

### A8 — materialization / authority lifecycle

Re-check the critical sequence:

`effective environment -> fingerprint -> one-use deployment authority -> consume -> materialization validation -> CHILD_LAUNCH_AUTHORIZED -> child`

Search for any regression introduced by the correction.

At minimum:
- stale materialized fingerprint still fails closed;
- valid authority is not invalidated solely by transient ExecStart observations;
- authority replay remains impossible;
- no child launch becomes authorized without correct binding;
- correction does not silently rematerialize stale evidence.

### A9 — Builder-test falsification

For each important Builder test, ask:
- can it pass while the real defect remains?
- is the mocked `systemctl show` shape faithful enough?
- is the assertion checking the correct authority boundary?

Add independent discriminants where needed.

### A10 — second-order search

Search the surrounding fingerprint/service-definition code for another runtime-mutating field that could produce the same class of instability or another unbound semantic field that could produce false equality.

Do not assume `ExecStart` is the only possible surface.

## 5. Scope / classification

Every finding must be labeled one of:

- `REAL_DEFECT`
- `TEST_DEFECT`
- `MISSING_PROOF`
- `TARGET_HOST_ONLY`
- `NON_ISSUE`

Also state:
- FACT;
- INFERENCE;
- CLAIM;
- UNKNOWN;
- RECOMMENDATION where applicable.

A green CI run is not scientific or target-host certification.

## 6. Required proof discipline

- Verify branch/SHA ancestry yourself.
- Verify exact candidate bytes yourself.
- Do not start from Builder's verdict.
- Do not edit the frozen candidate.
- Reproduce suspected defects with an independent discriminant before proposing a fix.
- Preserve red evidence if a defect is found.
- Do not silently transfer old v3 proof to v4.
- Do not claim target-host proof from mocked/container-only tests.
- Do not declare t0 or P14D continuity.

## 7. Test / CI requirements

Run:
- focused independent tests;
- relevant existing Phase5/Phase7/Phase8 tests;
- full unit suite;
- SEC P0 lane suite;
- V1 end-to-end regression;
- schema/status freshness where applicable.

Push audit-only commits/checkpoints to the Astra branch.

Require exact-head GitHub Actions evidence for the final Astra audit HEAD.

Expected workflow:
`SEC P0 pre-t0 gate`

A deliberately red audit branch may have expected-red CI during investigation. Classify such runs explicitly rather than calling them production regressions.

## 8. Durable checkpoints

If the audit spans multiple commits, push a checkpoint containing:
- candidate SHA;
- audit branch HEAD;
- reproduced attacks;
- open findings;
- CI state;
- next discriminant.

Do not let substantive audit state exist only in chat.

## 9. Final handoff

Write:

`handoff/ASTRA_GATE_A_V4_INDEPENDENT_AUDIT_2026-09-20.md`

The final handoff must contain:

- exact frozen candidate SHA;
- exact final Astra HEAD;
- ancestry proof;
- changed audit-only paths;
- old-defect reproduction;
- each mandatory attack result;
- new bypass search result;
- defect classifications;
- focused/full test results;
- exact-head CI run ID/status;
- residual TARGET_HOST_ONLY / MISSING_PROOF items;
- final independent repository verdict.

Allowed repository verdict forms include:

- `AUDIT_GATE_A_V4 = PASS_REPOSITORY_CORRECTION`
- `AUDIT_GATE_A_V4 = BLOCKED_REAL_DEFECT`
- `AUDIT_GATE_A_V4 = BLOCKED_MISSING_PROOF`

Do not decide target-host readiness or t0.

After final handoff, stop and return control to Blue.
