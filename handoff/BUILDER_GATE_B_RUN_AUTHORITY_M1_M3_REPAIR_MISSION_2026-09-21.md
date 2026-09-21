# BUILDER MISSION — GATE B RUN AUTHORITY M1/M2/M3 REPAIR — 2026-09-21

## 0. Mission identity

Role: implementation Builder.

Repository: `fahimahmedb/Quant-Trade`

Work only on:

`builder/gate-b-run-authority-m1-m3-repair-2026-09-21`

Do not create another branch.

This mission is dispatched from:

`blue/gate-b-run-authority-repair-dispatch-2026-09-21`

The exact shared Builder starting SHA is the immutable dispatch commit from which Blue creates both repair branches after this mission file and its M4 sibling are present. Because a Git commit cannot literally contain its own SHA, do not accept a stale hard-coded self-reference: at mission start resolve the assigned Builder branch, verify the sibling M4 Builder branch was created from the same parent if it exists, and verify the Blue reception record names the same exact dispatch SHA.

Audited defective ancestor:

`845dfa3609a9bbb2f81b76cd4375189a30ec2232`

Astra defect authority:

`astra/gate-b-run-authority-mechanisms-independent-review-2026-09-21@02432fae0ceb6440d2aec2182d06756f7151c648`

Astra exact-head CI:

`35588182384 = COMPLETED / SUCCESS`

## 1. Read before implementation

Read in full:

1. `QUANT_NORTH_STAR.md`
2. `governance/BLUE_GATE_B_RUN_AUTHORITY_REPAIR_SPEC_2026-09-21.md`
3. this mission file
4. `handoff/ASTRA_GATE_B_RUN_AUTHORITY_MECHANISMS_INDEPENDENT_REVIEW_2026-09-21.md` from the Astra commit above
5. `handoff/BUILDER_GATE_B_RUN_AUTHORITY_RETENTION_PRESTAGE_2026-09-21.md` from its authoritative prestage branch

The Blue repair spec is the implementation contract. Astra's reproduced failure mechanisms are the adversarial oracle. Do not weaken either.

## 2. Scope

Repair only:

- A1 `REAL_DEFECT` — partial/short write success;
- A2 `REAL_DEFECT` — missing directory durability;
- A3 `REAL_DEFECT` — freshness time captured before authority lock;
- A4 `REAL_DEFECT` — future issued-at / chronology not enforced;
- A5 `REAL_DEFECT` — evidence binding not tied to consumed activation; weak ordinal typing;
- A9 `MISSING_PROOF` — M1/M2/M3 proof gaps assigned by Blue.

Primary implementation:

`scripts/quant_gate_b_runctl.py`

Prefer a dedicated R1 targeted test file to avoid conflict with the M4 lane.

May modify:
- `scripts/quant_gate_b_runctl.py`;
- R1-specific tests;
- `handoff/BUILDER_GATE_B_RUN_AUTHORITY_M1_M3_REPAIR_2026-09-21.md`;
- `STATE.md` only for a mechanical proof-inventory refresh legitimately required by repository tooling.

Must not modify:
- `scripts/verify_gate_b_deployed_bytes.py`;
- frozen V4 `src/`;
- F1;
- F5;
- V4 transition/materialization design;
- target-host state;
- Gate C/t0 authority.

## 3. Required engineering

### A1 full writes

Implement one robust exact-write primitive used by every R1 durability-critical raw write introduced or retained by this repair.

It must:
- loop until every byte is written;
- retry `EINTR` correctly;
- reject zero progress;
- reject incomplete writes;
- never return authority after incomplete registry state.

Use it for registry event bytes and receipt temp bytes.

Before receipt success, prove exact final bytes/digest by reopening/revalidating or an equivalently strong exact-byte mechanism.

### A2 durability

Registry:
- exact event bytes fully written;
- file fsync completes;
- required containing directory fsync completes;
- first registry creation explicitly covered.

Receipt:
- temp bytes fully written;
- temp file fsync completes;
- final no-overwrite placement is proven;
- final directory fsync completes;
- final receipt bytes/digest are exact.

If `ACTIVATION_CONSUMED` has been durably appended and receipt materialization then fails:
- return failure;
- never make the activation reusable;
- leave the ledger unambiguously consumed or fail closed as recovery-required;
- a second consume must remain RED.

### A3 freshness under lock

Authoritative production current time for consume validation must be acquired only after the exclusive authority lock is held, immediately before freshness validation and consume append.

A timestamp captured while waiting for the lock cannot authorize consumption.

### A4 chronology

Require exact UTC timestamps and at minimum:

```text
issued_at_utc <= now
issued_at_utc <= not_before_utc
not_before_utc < expires_at_utc
not_before_utc <= now < expires_at_utc
```

Reject:
- future-issued;
- not-yet-valid;
- expired;
- zero/negative validity interval;
- issued > not-before;
- malformed/non-UTC time.

### A5 evidence binding

An accepted evidence binding must prove:
- exact run ID;
- exact attempt/reservation;
- exact candidate SHA/tree/input-tree digest;
- exact target host opaque ID;
- exact activation digest actually consumed for that run.

Do not accept “some activation consumed”.

Strictly validate authority-relevant binding schema and digest/type fields.

`artifact_ordinal`:
- integer only;
- bool forbidden;
- >= 1;
- duplicate checks cannot be bypassed by `"1"` vs `1`.

## 4. Mandatory R1 tests

At minimum commit/reproduce:

- short registry write;
- repeated partial registry writes;
- short receipt write;
- repeated partial receipt writes;
- interrupted write / `EINTR`;
- zero-progress write;
- injected registry write failure;
- first registry creation + parent-directory durability;
- receipt placement + parent-directory durability;
- pre-existing receipt collision;
- injected receipt failure after consumption event;
- second consume after that failure remains RED;
- true independent-process `flock` contention;
- activation expiring while consumer waits on that lock;
- future-issued activation;
- not-yet-valid activation;
- invalid chronology;
- malformed/non-UTC timestamp;
- evidence binding from another run's activation;
- evidence binding naming sealed-but-unconsumed activation;
- activation digest mismatch with the actual consumed digest;
- ordinal bool;
- ordinal string;
- ordinal zero/negative;
- duplicate ordinal;
- valid finite-window/binding positive controls.

Use temporary directories only.

Fault injection must assert the externally visible fail-closed property, not only an internal helper.

## 5. Regression

Run:
- all R1 targeted repair tests;
- existing `tests/test_gate_b_run_authority.py`;
- any repository-required test command/CI.

Do not modify tests merely to make incorrect behavior pass.

If an old test encoded defective behavior, document and replace it transparently.

## 6. Handoff

Write:

`handoff/BUILDER_GATE_B_RUN_AUTHORITY_M1_M3_REPAIR_2026-09-21.md`

For A1-A5 and R1 A9 items provide:
- original failure;
- exact code change;
- exact discriminant/test;
- observed result;
- remaining limitation;
- changed paths;
- exact final Builder HEAD;
- exact-head CI only if actually observed.

Final status may be only:

`GATE_B_RUN_AUTHORITY_M1_M3_REPAIR = READY_FOR_INDEPENDENT_REVIEW`

or a precise blocker.

Do not write `PASS_REPOSITORY_EVIDENCE`; only Astra may do that.

## 7. Commit / safety

Commit and push only to:

`builder/gate-b-run-authority-m1-m3-repair-2026-09-21`

Verify remote HEAD after push.

Never fabricate CI completion.

```text
TARGET_HOST_TOUCHED = FALSE
FROZEN_V4_SRC_MODIFIED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
```
