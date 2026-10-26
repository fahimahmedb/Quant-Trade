# BUILDER — GATE B RUN-AUTHORITY M1/M2/M3 REPAIR — 2026-09-21

## 0. Final Builder disposition

`GATE_B_RUN_AUTHORITY_M1_M3_REPAIR = READY_FOR_INDEPENDENT_REVIEW`

This is a bounded repository-only M1/M2/M3 defect repair. It is not an independent PASS, does not authorize Gate B mutation, does not touch the target host, and does not declare t0.

## 1. Authority and exact scope

Repository:

`fahimahmedb/Quant-Trade`

Builder branch:

`builder/gate-b-run-authority-m1-m3-repair-2026-09-21`

Audited defective Builder ancestor:

`845dfa3609a9bbb2f81b76cd4375189a30ec2232`

Astra defect authority:

`astra/gate-b-run-authority-mechanisms-independent-review-2026-09-21@02432fae0ceb6440d2aec2182d06756f7151c648`

Shared Blue dispatch / Builder starting SHA resolved at mission start:

`58b559767ddbb965c1ab6448dd7ec89dc46ec821`

The live Blue dispatch branch, this R1 branch before implementation, and the sibling M4 Builder branch all resolved exactly to that same SHA. The R1 branch descended from the audited defective ancestor with no divergence. Before implementation, the only commits above the audited delivery were Blue governance/mission authority; no implementation code had changed.

Read and followed before implementation:

- `QUANT_NORTH_STAR.md`
- `governance/BLUE_GATE_B_RUN_AUTHORITY_REPAIR_SPEC_2026-09-21.md`
- `handoff/BUILDER_GATE_B_RUN_AUTHORITY_M1_M3_REPAIR_MISSION_2026-09-21.md`
- Astra independent review at the exact SHA above
- `handoff/BUILDER_GATE_B_RUN_AUTHORITY_RETENTION_PRESTAGE_2026-09-21.md`

Blue's repair specification is the implementation contract. Astra's A1-A5 attack mechanisms are the adversarial oracle.

Implementation/content HEAD immediately before this handoff:

`14278db0700c52202790b026f71b2d063b6de88f`

A Git commit cannot truthfully contain its own future SHA. Therefore this handoff records the immutable implementation parent above; the final live branch SHA after committing this handoff must be resolved and verified from the branch ref rather than hard-coded self-referentially into this file.

## 2. Changed paths

Implementation scope is limited to:

- `scripts/quant_gate_b_runctl.py`
- `tests/test_gate_b_run_authority_m1_m3_repair.py`
- `STATE.md` — mechanical generated proof-inventory refresh only, from 392 to 418 discovered tests
- this handoff

Explicitly untouched:

- `scripts/verify_gate_b_deployed_bytes.py`
- frozen V4 `src/`
- target-host state
- F1 evidence-schema repair
- F5 lifecycle/sanitization
- V3 -> V4 transition/materialization design
- Gate-C/t0 authority

The repaired runctl blob observed on GitHub is:

`a18b4b5589a0e9f94e4b4e5ecd3bb9c557644a61`

The dedicated R1 test blob observed on GitHub is:

`8b3950871a89db97bc6103267bd33d16e3f61a0b`

Those remote blobs matched the exact locally exercised contents.

## 3. A1 — short / partial write success

Original failure:

- registry append used one unchecked `os.write`;
- receipt temp materialization used one unchecked `os.write`;
- a legal short write could therefore be followed by fsync and a false success return;
- zero progress and EINTR had no explicit exact-write semantics.

Repair:

- introduced `_write_all(fd, data)`;
- loops until every byte is written;
- retries `InterruptedError` / `EINTR`;
- rejects zero/nonpositive progress;
- converts other raw write errors to fail-closed `AuthorityError("write failed")`;
- used for authoritative registry event bytes and receipt temporary bytes.

Discriminants:

- short registry write;
- repeated partial registry writes;
- interrupted registry write;
- zero-progress registry write;
- injected partial write followed by EIO during consume;
- short receipt write;
- repeated partial receipt writes.

Observed Builder result:

- dedicated R1 suite: 26/26 tests GREEN;
- injected short writes are completed exactly;
- zero progress and EIO surface failure instead of authority success;
- a partial registry event left by an injected mid-write hard failure is subsequently detected as truncated rather than laundered as a valid ledger.

Remaining limitation:

Repository tests prove the writer's fail-closed call/return semantics and byte-loop behavior. Concrete target-host storage hardware/filesystem guarantees remain activation-time/host evidence, not a repository-only claim.

## 4. A2 — missing directory durability

Original failure:

- registry file fd was fsynced, but first creation of the authoritative registry directory entry was not;
- receipt temp file was fsynced and hard-linked, but the final receipt directory entry was not fsynced;
- previous handoff language therefore overstated directory durability.

Repair:

- added `_fsync_dir(path)` using a directory fd with no-follow semantics where available;
- registry append detects whether the registry path existed before open;
- on first registry creation, file bytes are fully written and file-fsynced, then parent directory is fsynced before success returns;
- receipt materialization now fully writes temp bytes, fsyncs the temp file, closes it, uses hard-link no-overwrite placement, fsyncs the final receipt directory, reopens the final path with no-follow semantics, and verifies exact final bytes/digest before returning success;
- final receipts are never deleted after the consumption event has committed merely because a later durability verification step fails.

Discriminants:

- first registry creation records the parent-directory fsync path;
- injected first-registry parent fsync failure is surfaced;
- existing-registry append does not pretend a new-entry fsync is needed;
- receipt parent-directory fsync path;
- injected receipt-directory fsync failure after consumption;
- pre-existing final receipt collision;
- injected receipt-link failure after consumption.

Observed Builder result:

- first-create parent durability path is exercised;
- receipt placement directory durability path is exercised;
- collision never overwrites foreign final bytes;
- post-consumption receipt failure is returned as failure;
- the already-appended `ACTIVATION_CONSUMED` remains authoritative and a second consume stays RED.

Remaining limitation:

If a system reports `fsync` success but the actual target storage stack violates its documented durability semantics, repository code cannot prove the hardware. That is a target-host/storage qualification boundary, not silently converted into repository PASS.

## 5. A3 — stale freshness timestamp captured before flock

Original failure:

`consume_activation()` captured `now` before entering the exclusive registry mutation lock. A consumer could begin while an activation was valid, wait behind another process until after expiry, then authorize with the stale pre-lock timestamp.

Repair:

- activation parsing remains non-mutating;
- production wall-clock acquisition (`now is None`) now occurs inside the locked mutation callback, after exclusive `flock` acquisition and immediately before chronology/freshness checks;
- the same post-lock decision timestamp is used for `ACTIVATION_CONSUMED.event_time_utc` and receipt `consumed_at_utc`;
- explicit injected `now` remains supported for deterministic tests, but it is normalized/evaluated inside the locked callback.

Mandatory discriminant:

- a real independent Python process opens the actual `.lock` file and holds `flock(LOCK_EX)`;
- activation is valid before the consumer starts waiting;
- activation expires while the consumer is blocked;
- after the other process releases the lock, the production-time consumer recomputes current time and rejects `stale/expired`;
- no `ACTIVATION_CONSUMED` event exists afterward.

Observed Builder result:

GREEN.

This is an actual second-process flock contention test, not a mocked lock.

## 6. A4 — future-issued / incoherent chronology

Original failure:

The parser checked UTC syntax, but consumption only enforced:

`not_before_utc <= now < expires_at_utc`

It did not require future-issued rejection or coherent issued/not-before/expiry order.

Repair:

Consumption now requires, under the lock:

- `issued_at_utc <= now`;
- `issued_at_utc <= not_before_utc`;
- `not_before_utc < expires_at_utc`;
- `now >= not_before_utc`;
- `now < expires_at_utc`.

Strict UTC timestamps must be canonical `Z`-suffixed UTC input; malformed/non-UTC input is rejected.

Discriminants:

- future-issued activation;
- not-yet-valid activation;
- issued-after-not-before chronology;
- equal not-before/expiry zero validity;
- reversed validity;
- exact-expiry boundary;
- valid finite-window positive control;
- non-`Z` timestamp.

Observed Builder result:

All RED cases reject; valid finite-window control consumes successfully.

## 7. A5 — evidence not tied to the exact consumed activation / weak ordinal typing

Original failure:

- `bind_evidence()` only required that the run had some `ACTIVATION_CONSUMED`;
- it did not require the binding envelope's `activation_digest` to equal the digest actually consumed for that run;
- ledger validation repeated the same weakness;
- `artifact_ordinal` lacked strict type/range checks, so `1` and `"1"` could evade semantic duplicate protection.

Repair:

Added strict evidence-binding parsing and ledger validation:

- exact fixed schema keyset;
- canonical JSON required;
- exact run ID / attempt / reservation / candidate triple / target host;
- SHA-256 type/shape checks for activation, reservation, binding and artifact digests as applicable;
- strict artifact type syntax;
- `artifact_ordinal` must be an integer, bool forbidden, and `>= 1`;
- ledger records the exact digest from `ACTIVATION_CONSUMED`;
- binding must name exactly that consumed activation digest;
- sealed-but-unconsumed activation is insufficient;
- duplicate ordinal check is applied to the normalized strict integer domain;
- cross-run raw-artifact ownership rule remains fail-closed;
- `artifact_type` is now retained in the authoritative `EVIDENCE_BOUND` event.

Discriminants:

- activation binding from another run;
- binding naming a sealed but unconsumed activation;
- binding naming a digest different from the actual consumed activation;
- ordinal `True`;
- ordinal `False`;
- ordinal string `"1"`;
- ordinal zero;
- ordinal negative;
- duplicate integer ordinal;
- unknown binding field;
- malformed artifact digest;
- malformed artifact type;
- valid strict binding positive control.

Observed Builder result:

All laundering/type-bypass controls reject; strict positive binding remains GREEN.

## 8. Relevant A9 missing-proof closure

The R1 test lane adds the Blue-assigned M1/M2/M3 missing proof rather than broadening into M4.

Covered explicitly:

- short registry write;
- short receipt write;
- interrupted write;
- zero-progress write;
- first registry creation + parent-directory durability;
- receipt placement + parent-directory durability;
- pre-existing receipt collision;
- injected failure after the consumption event;
- second consume after such failure remains RED;
- true independent-process flock contention;
- expiry while waiting for lock;
- future-issued;
- not-yet-valid;
- invalid chronology;
- binding from another run;
- binding naming an unconsumed activation;
- ordinal bool/string/zero/negative;
- duplicate ordinal;
- strict binding digest/type/schema validation.

All test state is created under disposable temporary directories. The cross-process contention test uses a disposable registry lock and does not touch the target host.

## 9. Regression evidence

Builder-local targeted execution:

```text
tests/test_gate_b_run_authority_m1_m3_repair.py
Ran 26 tests in 4.353s
OK
```

Builder-local existing M1/M2/M3 regression replay:

```text
tests/test_gate_b_run_authority.py :: GateBRunAuthorityTests
Ran 14 tests in 0.026s
OK
```

For that focused local replay, the M4 verifier import was stubbed only so unittest could select the existing run-authority class without cloning the full repository object environment. No M4 behavior was counted as local R1 proof.

Repository CI for implementation/content HEAD:

- run: `35593480573`
- head SHA: `14278db0700c52202790b026f71b2d063b6de88f`
- branch: exact R1 Builder branch
- at handoff creation time, observed successful steps include:
  - fail-closed SEC identity check;
  - generated schema drift;
  - status artifact freshness;
  - full unit suite;
  - SEC P0 lane suite;
  - V1 end-to-end regression.
- the workflow was still executing its exact-head verification-artifact tail when this handoff was committed; therefore this file does **not** claim that run as `COMPLETED / SUCCESS`.

The final post-handoff branch HEAD necessarily differs from the implementation parent because this document itself is a commit. Its exact SHA and exact-head GitHub Actions result must be verified live after push. That live observation is the authoritative final CI record and avoids an impossible self-referential SHA/CI claim inside the commit being identified.

## 10. Remaining boundaries

This repair does not claim closure of:

- M4 A6/A7/A8/A10 or any M4-specific A9 item;
- concrete target-host registry/receipt filesystem identity, ownership, ACL and persistence qualification;
- installation/sealing of this consumer as immutable target-host bytes;
- F6 evidence-root/journald/headroom/reboot observations;
- F1 evidence schema;
- F4 transition/materialization;
- F5 lifecycle/sanitization;
- concrete Blue activation;
- actual Gate-B execution;
- Gate-B PASS;
- Gate C;
- t0.

Astra must independently replay the repaired R1 attacks. Blue remains the only authority for any later promotion or concrete mutation activation.

## 11. Safety / final state

```text
TARGET_HOST_TOUCHED = FALSE
FROZEN_V4_SRC_MODIFIED = FALSE
M4_VERIFIER_MODIFIED = FALSE
F1_MODIFIED = FALSE
F5_MODIFIED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
PASS_REPOSITORY_EVIDENCE = NOT_CLAIMED_BY_BUILDER
GATE_B_RUN_AUTHORITY_M1_M3_REPAIR = READY_FOR_INDEPENDENT_REVIEW
```
