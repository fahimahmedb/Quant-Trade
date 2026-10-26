# ASTRA — GATE B RUN-AUTHORITY MECHANISMS INDEPENDENT RECHECK — 2026-09-21

## 0. Final status

`ASTRA_GATE_B_RUN_AUTHORITY_REVIEW = BLOCKED_REAL_DEFECT_LOCK_PATH_IDENTITY`

`PASS_REPOSITORY_EVIDENCE = NOT_ESTABLISHED`

Return control to Blue.

The repaired A1-A10 matrix is independently GREEN at repository level, but Astra found a new repository-local atomicity defect outside the known repair matrix: replacement of the registry lock pathname can create a second independently lockable inode while another process still holds the original inode. That breaks the single-lock-domain invariant used by every registry mutation.

This review did not patch the audited implementation.

## 1. Exact audit object and authority

Repository:

`fahimahmedb/Quant-Trade`

Assigned Astra branch:

`astra/gate-b-run-authority-mechanisms-recheck-2026-09-21`

Exact audited integrated candidate:

`644da76eb0227be275b8e3448118dac0cc7096ca`

Integrated candidate branch:

`blue/gate-b-run-authority-repair-integration-2026-09-21`

Live ref verification during this review confirmed that branch still resolved exactly to:

`644da76eb0227be275b8e3448118dac0cc7096ca`

Candidate exact-head GitHub Actions:

`35598077120 = COMPLETED / SUCCESS`

The workflow metadata binds that run to:

- head branch: `blue/gate-b-run-authority-repair-integration-2026-09-21`;
- head SHA: `644da76eb0227be275b8e3448118dac0cc7096ca`;
- status: `completed`;
- conclusion: `success`.

The Astra branch descends exactly from the audited integrated object. Before this final handoff, the independent evidence HEAD was:

`64457e10ea7294e1796a47ee85abf4d47629862a`

Comparison `644da76... -> 64457e10...` was:

- ahead: 6;
- behind: 0;
- merge base: exact audited candidate.

Astra-only changed paths before this handoff were limited to:

- `handoff/ASTRA_GATE_B_RUN_AUTHORITY_MECHANISMS_RECHECK_MISSION_2026-09-21.md`;
- `tests/test_astra_gate_b_run_authority_recheck_probe.py`;
- `STATE.md` mechanical proof-inventory refresh from 444 to 445 tests.

No Builder implementation file and no frozen V4 `src/` file was modified on the Astra branch.

## 2. Integrated changed-path verification

The integrated candidate was compared against shared repair dispatch:

`58b559767ddbb965c1ab6448dd7ec89dc46ec821`

The integrated delta was exactly:

- `scripts/quant_gate_b_runctl.py`;
- `scripts/verify_gate_b_deployed_bytes.py`;
- `tests/test_gate_b_run_authority_m1_m3_repair.py`;
- `tests/test_gate_b_deployed_byte_verifier_m4_repair.py`;
- `handoff/BUILDER_GATE_B_RUN_AUTHORITY_M1_M3_REPAIR_2026-09-21.md`;
- `handoff/BUILDER_GATE_B_DEPLOYED_BYTE_VERIFIER_M4_REPAIR_2026-09-21.md`;
- `STATE.md`.

Therefore:

- M1/M2/M3 implementation ownership remained `scripts/quant_gate_b_runctl.py`;
- M4 implementation ownership remained `scripts/verify_gate_b_deployed_bytes.py`;
- both dedicated repair test suites were present;
- frozen V4 production `src/` was not changed by the integration.

The integrated proof inventory was 444 tests before the Astra-only independent probe. The Astra probe adds one independent unittest, so the audit branch inventory is 445.

## 3. Review method and independence

Astra read, in authority order:

1. `QUANT_NORTH_STAR.md`;
2. the Astra recheck mission;
3. `governance/BLUE_GATE_B_RUN_AUTHORITY_REPAIR_SPEC_2026-09-21.md`;
4. the original independent review at `02432fae0ceb6440d2aec2182d06756f7151c648`;
5. both Builder repair handoffs only after understanding the original defects;
6. the exact repaired implementation and dedicated test paths.

Builder conclusions and the candidate's green CI were not accepted as proof.

The independent probe is:

`tests/test_astra_gate_b_run_authority_recheck_probe.py`

It constructs its own disposable:

- registry and receipt roots;
- local Git repositories;
- self-contained frozen-candidate clone;
- independent lock-holding processes;
- Git replacement-object fixture;
- object-store indirection fixtures;
- race/mutation fixtures.

It does not use the target host.

The GitHub runner executed the complete repository suite with:

`PYTHONPATH=src python3 -m unittest discover -s tests -v`

The audit checkout also passed:

`python3 scripts/status_artifacts.py --check`

before entering the full unit suite.

## 4. Independent A1-A10 disposition

### A1 — durability-critical write completion

Classification after recheck: `NON_ISSUE`

Independently exercised:

- repeated partial registry writes;
- mid-write hard failure after partial progress;
- EINTR then retry;
- zero-progress registry write;
- repeated partial receipt writes;
- zero-progress receipt write after consumption was committed;
- post-failure externally visible registry/receipt state.

Observed:

- partial writes are completed by the full-write loop;
- EINTR is retried;
- zero progress fails closed;
- a mid-registry failure returns no reusable authority;
- receipt write failure after the consumption event leaves the activation consumed;
- no second consume succeeds.

### A2 — directory durability and receipt placement

Classification after recheck: `NON_ISSUE`

Independently exercised:

- first registry creation with containing-directory fsync failure;
- append to existing registry;
- receipt final-directory fsync failure;
- receipt link/placement failure;
- pre-existing final receipt collision;
- consumption committed followed by receipt-materialization failure.

Observed:

- first-create directory durability failure is surfaced;
- existing append remains valid without pretending to recreate the directory entry;
- receipt placement/directory durability failures are surfaced;
- a pre-existing final receipt is not overwritten;
- once `ACTIVATION_CONSUMED` is committed, later receipt failure does not roll back consumption;
- second consume stays RED.

### A3 — freshness while waiting for the authority lock

Classification after recheck: `NON_ISSUE`

A real independent local process held the actual `flock` lock for longer than the activation's remaining validity.

A second consumer began while the activation was valid, blocked on the lock, then continued only after expiry.

Observed result:

- the consumer rejected the activation after acquiring the lock;
- no `ACTIVATION_CONSUMED` event was appended.

This confirms freshness is evaluated using post-lock time for the ordinary stable-lock-path case.

### A4 — activation chronology

Classification after recheck: `NON_ISSUE`

Independently rejected:

- issued in the future;
- not-before in the future;
- issued > not-before;
- not-before == expires;
- not-before > expires;
- already expired;
- exact expiry boundary;
- malformed timestamp;
- non-UTC timestamp.

A valid finite-window positive control consumed successfully.

The implemented chronology observed by the probe is:

`issued_at <= now`

`issued_at <= not_before < expires`

`not_before <= now < expires`

### A5 — evidence binding to exact consumed activation

Classification after recheck: `NON_ISSUE`

Independently rejected:

- digest from another run;
- sealed but unconsumed activation;
- digest different from the actual consumed activation;
- ordinal string `"1"`;
- boolean ordinal;
- ordinal 0;
- negative ordinal;
- duplicate ordinal;
- unknown authority-relevant field;
- malformed artifact digest;
- malformed artifact type.

A strict valid binding positive control succeeded.

Binding is therefore tied to the exact consumed activation for the stable-lock-path case.

### A6 — repository-local Git object authority

Classification after recheck: `NON_ISSUE`

Independently exercised and rejected:

- `.git` symlink;
- `.git` pointer / linked-worktree form;
- linked worktree;
- `.git/objects` symlink to foreign object store;
- nested object-store symlink;
- alternates file;
- `GIT_OBJECT_DIRECTORY`;
- `GIT_ALTERNATE_OBJECT_DIRECTORIES`;
- empty object-directory override presence;
- foreign common-dir metadata;
- symlinked release ancestry.

The verifier rejects Git authority ambiguity before trusting expected-tree bytes.

### A7 — replacement-object semantics

Classification after recheck: `NON_ISSUE`

A disposable repository independently demonstrated the original poisoning semantics:

- expected tree identifier remained apparent;
- ordinary Git `ls-tree` was redirected to malicious replacement-tree content.

The repaired verifier rejected the replace-ref state.

Legacy graft metadata was also independently rejected.

Authoritative Git reads set replacement semantics disabled.

### A8 — exact frozen candidate positive control

Classification after recheck: `NON_ISSUE`

Astra used a self-contained disposable local clone and checked out exactly:

candidate:

`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

tree:

`4d15ef6f471213ee6ab56337b555d2906ef9bf16`

The clone had no alternates file and was not a linked worktree.

The repaired verifier returned `GREEN` for that exact frozen candidate/tree.

### A9 — complete negative-control matrix

Classification after recheck: `NON_ISSUE`

The independent matrix covered the required R1/R2 dimensions, including:

- real-process flock contention;
- partial/EINTR/zero-progress/failure write behavior;
- first-create durability;
- receipt collision and post-consumption failure;
- future/not-yet-valid/invalid chronology;
- wrong/unconsumed activation binding;
- ordinal type/range/duplicate bypasses;
- tracked-byte mutation;
- executable-mode mutation;
- regular-to-symlink and expected-symlink-to-regular substitution;
- missing tracked file;
- critical and noncritical extras;
- explicit allowed noncritical extra positive control;
- invalid/traversing/critical allowed-extra prefixes;
- `.git` symlink/file;
- object-store indirection;
- alternates and environment overrides;
- common-dir indirection;
- replace refs and graft metadata;
- index bytes/mtime unchanged;
- no new Git lock paths;
- exact frozen candidate positive control.

### A10 — concurrent filesystem state changes

Classification after recheck: `NON_ISSUE` for repository-provable inspection-time races.

Independently exercised:

- pathname substitution after enumeration;
- regular-file to symlink type change;
- concurrent content mutation during file inspection;
- static symlink substitution.

Observed behavior was fail-closed / RED.

Static inspection also confirmed the intended M4 primitives are present:

- root directory FD anchoring;
- directory-relative traversal;
- `O_NOFOLLOW`;
- opened-object `fstat` checks;
- pre/post identity checks;
- directory mutation checks.

The post-verification immutability window remains `TARGET_HOST_ONLY`, not repository proof.

## 5. New finding beyond A1-A10

### F11 — lock pathname replacement splits the exclusive lock domain

Classification: `REAL_DEFECT`

Affected path/function:

`scripts/quant_gate_b_runctl.py :: Registry._locked()`

Expected invariant:

All registry mutations using the configured lock pathname must serialize on one stable lock object. If the lock pathname is replaced while another process holds the lock, a second consumer must not silently establish a new independent lock domain. Ambiguous lock identity must fail closed.

Independent reproduction:

1. create a disposable registry root;
2. process A opens the actual registry lock pathname and acquires `LOCK_EX`;
3. while A still holds that open inode, unlink the lock pathname;
4. create a new regular file at the same pathname;
5. invoke the audited `Registry._locked()` in process B / the audit process;
6. measure time to acquire;
7. process A continues holding the original inode for approximately three seconds.

Observed on the independent audit run:

`ASTRA_LOCK_REPLACEMENT_ACQUIRE_SECONDS=0.000036`

A prior independent run reproduced the same defect at approximately:

`0.000070 s`

The assertion required the second acquisition to remain blocked for at least 2 seconds while A held the original inode. It failed.

Mechanism:

`Registry._locked()`:

- opens the pathname with `O_NOFOLLOW`;
- checks whether the current pathname is a symlink;
- calls `flock(fd, LOCK_EX)`.

It does not establish that the opened lock inode remains the inode currently named by the lock pathname after acquisition. A pathname replacement therefore permits a new `open()` to obtain a different inode and a different `flock` domain.

`O_NOFOLLOW` prevents following a symlink at open time; it does not bind future pathname identity to the already-open inode.

Impact:

Every registry mutation enters through `_mut() -> _locked()`. Therefore the code's atomicity and cross-process serialization rely on the lock-path identity that this attack breaks.

This finding blocks `PASS_REPOSITORY_EVIDENCE`.

Astra did not patch the defect.

## 6. Audit CI evidence

Independent expanded-matrix evidence HEAD:

`64457e10ea7294e1796a47ee85abf4d47629862a`

GitHub Actions run:

`35602729254 = COMPLETED / FAILURE`

The failure is expected audit evidence, not a candidate-CI identity failure.

Before the blocking assertion, the log recorded:

`ASTRA_A1_OK`

`ASTRA_A2_OK`

`ASTRA_A3_OK`

`ASTRA_A4_OK`

`ASTRA_A5_OK`

`ASTRA_A6_OK`

`ASTRA_A7_OK`

`ASTRA_A8_OK`

`ASTRA_A9_OK`

`ASTRA_A10_OK`

`ASTRA_MATRIX_COMPLETENESS_OK`

It then recorded:

`ASTRA_LOCK_REPLACEMENT_ACQUIRE_SECONDS=0.000036`

and failed the explicit `REAL_DEFECT` assertion.

The full unit discovery reported:

`Ran 445 tests`

with exactly one failure: the Astra lock-path replacement discriminant.

Because that full-unit step intentionally failed on the reproduced defect, later workflow steps such as exact-head verification-artifact generation were skipped for this audit HEAD. This does not alter the already verified candidate exact-head run `35598077120 = COMPLETED / SUCCESS`.

## 7. Search beyond the known matrix

Astra additionally inspected:

- registry recovery / canonical JSON behavior;
- terminal-state validation;
- lock-path identity and type handling;
- receipt placement;
- duplicate/ambiguous structured data;
- timestamp boundaries;
- activation/revocation identity;
- evidence binding;
- Git environment/config/replacement channels;
- refs and object-store locality;
- worktree path handling;
- allowed-extra exclusions;
- report canonicalization and digest binding.

Canonical activation, binding and registry inputs are checked against canonical serialization, so duplicate/noncanonical JSON spellings were not accepted as a new bypass in this review.

No second independently reproduced repository blocker was established beyond F11.

F11 alone is sufficient to deny repository PASS.

## 8. Remaining repository and target-host boundaries

The following remain outside repository proof and are not closed by this review:

- actual installation and immutable digest of the authority consumer;
- actual external registry/receipt roots, ownership, permissions, filesystem identity and persistence;
- persistent active-run/resume state if required by the final activation design;
- F6 evidence-root / journald / disk/inode headroom observations;
- M4 execution against the actual frozen target release;
- `TARGET_HOST_ONLY: immutability of the frozen release for the verification-to-first-mutation authority window`;
- exact host / boot / mount bindings;
- Blue sealing of one concrete activation;
- consumption of that concrete activation;
- actual Gate-B execution;
- Blue Gate-B reception;
- Gate-B PASS;
- t0.

Target-host permissions must not be retroactively used as repository proof for F11. If Blue intends external filesystem permissions to make lock-path replacement impossible, that is a separate target-host property and does not remove the repository-local fact that the lock implementation itself does not detect identity replacement.

## 9. Safety state

```text
TARGET_HOST_TOUCHED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
```

No target host was accessed.

No Builder implementation was changed.

No integrated candidate object was changed.

No frozen V4 production source was changed.

## 10. Final disposition

`ASTRA_GATE_B_RUN_AUTHORITY_REVIEW = BLOCKED_REAL_DEFECT_LOCK_PATH_IDENTITY`

`PASS_REPOSITORY_EVIDENCE = NOT_ESTABLISHED`

`RETURN_CONTROL_TO = BLUE`
