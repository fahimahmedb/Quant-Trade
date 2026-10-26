# BLUE — GATE B RUN AUTHORITY REPAIR SPEC — 2026-09-21

## 0. Authority, scope and status

This is the authoritative Blue repair specification for the defects found by the independent Astra review of:

- Builder delivery: `builder/gate-b-run-authority-mechanisms-2026-09-21@845dfa3609a9bbb2f81b76cd4375189a30ec2232`
- Builder exact-head CI: `35585585066 = COMPLETED / SUCCESS`
- Astra review: `astra/gate-b-run-authority-mechanisms-independent-review-2026-09-21@02432fae0ceb6440d2aec2182d06756f7151c648`
- Astra exact-head CI: `35588182384 = COMPLETED / SUCCESS`
- Astra verdict: `ASTRA_GATE_B_RUN_AUTHORITY_REVIEW = BLOCKED_REAL_DEFECTS_M1_DURABILITY_M2_FRESHNESS_BINDING_M4_GIT_INDIRECTION`

This repair does not reopen F1, F5 or the completed V4 materialization/activation prestage.

Current safety state remains:

```text
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
TARGET_HOST_TOUCHED_BY_THIS_REPAIR = FALSE
```

The frozen release identity remains:

```text
CANDIDATE_SHA = 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
GIT_TREE = 4d15ef6f471213ee6ab56337b555d2906ef9bf16
```

## 1. Repair lanes and ownership

### Lane R1 — M1/M2/M3 run authority state

Owns A1, A2, A3, A4, A5 and the M1/M2/M3 portions of A9.

Primary implementation surface:

`scripts/quant_gate_b_runctl.py`

R1 may add or modify only M1/M2/M3-specific tests plus its own handoff and a purely mechanical `STATE.md` proof-inventory refresh if required by repository tooling.

R1 must not modify `scripts/verify_gate_b_deployed_bytes.py`.

### Lane R2 — M4 deployed-byte verifier

Owns A6, A7, A8, the M4 portions of A9 and A10 mitigation/residual classification.

Primary implementation surface:

`scripts/verify_gate_b_deployed_bytes.py`

R2 may add or modify only M4-specific tests plus its own handoff and a purely mechanical `STATE.md` proof-inventory refresh if required by repository tooling.

R2 must not modify `scripts/quant_gate_b_runctl.py`.

The lanes must not edit the same implementation file. Prefer dedicated targeted test files rather than a shared test file. If an implementation-file conflict becomes necessary, stop and return to Blue rather than improvising a third repair.

## 2. Global repair rules

1. Fail closed on ambiguity.
2. A green Builder CI is necessary but not sufficient.
3. A Builder may end only with `READY_FOR_INDEPENDENT_REVIEW` or an explicit blocker.
4. No Builder may claim independent closure, Gate B PASS, production readiness or t0 readiness.
5. No target-host mutation is authorized by this spec.
6. No frozen V4 `src/` modification is authorized.
7. Tests use disposable temporary directories/repositories/processes only.
8. Do not weaken existing valid invariants while repairing these findings.
9. Do not reinterpret previous green CI as evidence against Astra findings.
10. Repository code must not claim to prove host properties that require activation-time or target-host evidence.

## 3. A1 — short writes can be reported as success

Classification: `REAL_DEFECT`

Failure mechanism:
- registry append performs one raw write and does not require the full intended byte count;
- receipt write has the same weakness;
- a short write can therefore return success while durable state is incomplete.

Required invariant after repair:
- every durability-critical raw write must complete every intended byte before success;
- `EINTR` must be retried correctly;
- zero-progress write must fail;
- no consume-authority return path may survive incomplete registry bytes;
- receipt bytes must be reopened/revalidated or equivalently proven exact before success.

Mandatory RED-before / GREEN-after:
- injected short registry write;
- repeated partial registry writes;
- injected short receipt write;
- repeated partial receipt writes;
- `EINTR` during write;
- zero-progress write;
- externally visible assertion that authority is not returned on incomplete state.

Allowed implementation surface:
- R1 implementation and R1 tests only.

Forbidden shortcuts:
- assuming regular-file writes are always full;
- calling `fsync` after a short write and treating that as success;
- testing only a helper without checking the public fail-closed behavior.

Acceptance:
- all intended bytes are proven written and durable or the public operation fails;
- a failed/partial consume never creates reusable authority.

Closure type:
- repository-provable for write-loop semantics;
- actual filesystem durability properties remain subject to later host binding.

## 4. A2 — directory durability is missing

Classification: `REAL_DEFECT`

Failure mechanism:
- registry file is fsync'd but containing-directory durability is not established for first creation;
- receipt temp file is fsync'd and linked, but the final receipt directory entry is not fsync'd before success.

Required invariant after repair:
- registry file durability plus required containing-directory durability;
- first registry creation explicitly covers parent directory fsync;
- receipt temp bytes are fully written and fsync'd;
- final no-overwrite placement is proven;
- final directory entry is fsync'd before success;
- final receipt bytes/digest are exact.

Mandatory RED-before / GREEN-after:
- first registry creation with parent-directory fsync failure;
- existing-registry append path;
- receipt final-placement directory fsync failure;
- link/materialization failure;
- pre-existing final receipt collision;
- event committed + receipt failure returns failure and leaves activation consumed.

Allowed implementation surface:
- R1 implementation and R1 tests only.

Forbidden shortcuts:
- relying on file fsync alone for first creation/link durability;
- overwriting a pre-existing receipt;
- rolling back or deleting the already committed consumption event after later receipt failure.

Acceptance:
- no public success before required file and directory durability points complete;
- post-consumption receipt failure is visible and second consumption remains RED.

Closure type:
- repository-provable semantics; concrete host filesystem/persistence still target-host/activation-time.

## 5. A3 — freshness time is captured before lock acquisition

Classification: `REAL_DEFECT`

Failure mechanism:
- consumer captures current time before acquiring the exclusive authority lock;
- an activation can expire while blocked and still be consumed using stale pre-lock time.

Required invariant after repair:
- production current time used for consume freshness is acquired after the exclusive authority lock is held and immediately before validation/append;
- no stale pre-lock timestamp may authorize consumption;
- consumption event timestamp reflects the authoritative under-lock decision time.

Mandatory RED-before / GREEN-after:
- process A holds the actual lock;
- process B begins consume while activation is still valid;
- activation expires while B is blocked;
- A releases lock;
- B must reject.

Allowed implementation surface:
- R1 implementation and R1 tests only.

Forbidden shortcuts:
- mock-only lock simulation in place of at least one real independent-process contention test;
- extending expiry to make the test pass.

Acceptance:
- independently contending processes reproduce post-lock expiry rejection.

Closure type:
- repository-provable.

## 6. A4 — future issued_at and chronology are not enforced

Classification: `REAL_DEFECT`

Failure mechanism:
- `issued_at_utc` is parsed but not required to be at or before current time;
- chronology among issued/not-before/expiry is not fully constrained.

Required invariant after repair:
- exact UTC parsing;
- `issued_at_utc <= now`;
- `issued_at_utc <= not_before_utc < expires_at_utc`, or an explicitly stricter documented equivalent;
- now must be inside the finite authorized interval;
- malformed/non-UTC timestamps fail.

Mandatory RED-before / GREEN-after:
- future-issued activation;
- future not-before activation;
- issued > not-before;
- not-before == expires;
- not-before > expires;
- expired activation;
- exact expiry boundary;
- malformed/non-UTC time;
- valid finite interval positive control.

Allowed implementation surface:
- R1 implementation and R1 tests only.

Forbidden shortcuts:
- checking only `not_before <= now < expires`;
- silently normalizing malformed timezone data.

Acceptance:
- all invalid chronology/time cases are RED and valid finite-window control is GREEN.

Closure type:
- repository-provable.

## 7. A5 — evidence binding is not tied to the activation actually consumed

Classification: `REAL_DEFECT`

Failure mechanism:
- binding verifies that a run has some consumed activation but does not require the envelope's `activation_digest` to equal that exact consumed digest;
- `artifact_ordinal` is weakly typed and duplicate checks can be bypassed by type changes.

Required invariant after repair:
- binding `activation_digest` equals the exact `ACTIVATION_CONSUMED` digest for the same run;
- exact strict binding schema, with unknown/missing fields rejected where authority-relevant;
- reservation/run/candidate/host identity is immutable;
- `artifact_ordinal` is integer, non-bool, >= 1;
- semantically duplicate ordinals cannot be bypassed via type substitution;
- authority-relevant artifact digest/type fields are strictly validated.

Mandatory RED-before / GREEN-after:
- another run's activation digest;
- a sealed but unconsumed activation digest;
- mismatch against the run's actual consumed activation;
- ordinal `"1"`;
- ordinal `true`/`false`;
- ordinal 0;
- negative ordinal;
- duplicate ordinal;
- exact valid binding positive control.

Allowed implementation surface:
- R1 implementation and R1 tests only.

Forbidden shortcuts:
- accepting “some activation consumed”;
- coercing string/bool ordinals to integers;
- changing top-level run metadata while leaving contradictory activation identity.

Acceptance:
- every accepted evidence binding proves the exact run/reservation/candidate/host and exact consumed activation.

Closure type:
- repository-provable.

## 8. A6 — foreign object store via Git metadata indirection

Classification: `REAL_DEFECT`

Failure mechanism:
- resolving `.git/objects` before comparing paths lets a symlink to a foreign object store appear “equal” and local.

Required invariant after repair:
- never resolve away a symlink and then use equality as locality proof;
- reject `.git` symlink;
- reject `.git` linked-worktree text file/pointer;
- reject `.git/objects` symlink;
- reject foreign common dir;
- reject foreign object dir;
- reject alternates;
- reject object-store environment overrides;
- inspect relevant path components with lstat/no-follow semantics.

Mandatory RED-before / GREEN-after:
- exact attack replacing `.git/objects` with a symlink to a foreign object store containing enough expected objects;
- `.git` symlink;
- linked-worktree `.git` file;
- alternates file;
- `GIT_OBJECT_DIRECTORY`;
- `GIT_ALTERNATE_OBJECT_DIRECTORIES`;
- common-dir/object-dir indirection.

Allowed implementation surface:
- R2 implementation and R2 tests only.

Forbidden shortcuts:
- `resolve()`-equality as proof of locality;
- accepting a local-looking Git command result without independent path-type checks.

Acceptance:
- every foreign/indirected object authority attack fails before expected-tree bytes are trusted.

Closure type:
- repository-provable for verifier logic; actual target release still requires host execution.

## 9. A7 — replace refs can poison authoritative Git object reads

Classification: `REAL_DEFECT`

Failure mechanism:
- authoritative Git reads currently permit replacement-object semantics;
- `refs/replace/*` can make expected identifiers appear unchanged while `ls-tree` reads malicious replacement content.

Required invariant after repair:
- all authoritative Git object reads run with replacement-object semantics disabled;
- explicitly enumerate/reject `refs/replace/*`;
- inspect and explicitly disposition legacy graft/replacement mechanisms relevant to installed Git;
- any replacement ambiguity is RED.

Mandatory RED-before / GREEN-after:
- construct expected commit/tree;
- construct malicious tree;
- install replace authority for expected tree;
- deploy malicious bytes;
- prove unrepaired semantics can be poisoned;
- repaired verifier rejects before trusting poisoned `ls-tree`.

Allowed implementation surface:
- R2 implementation and R2 tests only.

Forbidden shortcuts:
- checking only HEAD/tree identifiers;
- disabling replacement for one command while leaving another authoritative Git read exposed.

Acceptance:
- no authoritative expected-tree read is affected by replace/graft authority.

Closure type:
- repository-provable.

## 10. A8 — exact frozen-tree positive control is fake

Classification: `TEST_DEFECT`

Failure mechanism:
- existing test named as exact frozen-tree control actually verifies a synthetic commit/tree.

Required invariant after repair:
- positive control really uses:
  - candidate `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`;
  - tree `4d15ef6f471213ee6ab56337b555d2906ef9bf16`;
- temporary repository is self-contained, not a linked worktree and not dependent on alternates/hardlink assumptions that defeat the independence claim;
- no network dependency is required by the test.

Mandatory RED-before / GREEN-after:
- demonstrate old test did not use the frozen candidate;
- new exact-frozen control verifies the real frozen candidate/tree GREEN.

Allowed implementation surface:
- R2 tests and minimal R2 verifier support only.

Forbidden shortcuts:
- generating a new synthetic commit and naming it “exact frozen”;
- linked worktree;
- alternate object store dependency.

Acceptance:
- committed test explicitly asserts the real candidate SHA/tree and passes from a self-contained disposable local object store.

Closure type:
- repository-provable.

## 11. A9 — mandatory proof gaps

Classification: `MISSING_PROOF`

### R1 mandatory tests

At minimum:
- true independent-process flock contention;
- short/partial writes;
- injected write failure;
- zero-progress write;
- first registry creation durability;
- pre-existing receipt collision;
- event committed + receipt failure remains consumed and returns failure;
- future-issued;
- not-yet-valid;
- invalid chronology;
- expiry while waiting on lock;
- wrong activation binding;
- sealed-but-unconsumed activation binding;
- ordinal type/range bypass;
- duplicate ordinal.

### R2 mandatory tests

At minimum:
- tracked byte mutation;
- executable-bit mutation;
- tracked regular-file -> symlink substitution;
- tracked symlink -> regular-file substitution where applicable;
- missing tracked file;
- critical and noncritical untracked files;
- `.git` symlink/file;
- `.git/objects` symlink;
- alternates;
- `GIT_OBJECT_DIRECTORY`;
- `GIT_ALTERNATE_OBJECT_DIRECTORIES`;
- common-dir/object-dir indirection;
- replace refs;
- any relevant legacy graft/replacement mechanism;
- traversal/bad allowed-extra prefixes;
- index bytes/mtime unchanged;
- no new Git lock files;
- exact frozen candidate positive control.

Required invariant after repair:
- all listed negative controls are committed and reproducible, not merely reasoned about statically.

Forbidden shortcuts:
- omitting an attack because code inspection “looks safe”;
- using only same-process lock tests.

Acceptance:
- lane-specific suites cover the listed controls and integrated candidate later runs their union without dropping tests.

Closure type:
- repository-provable for committed tests; target-host-only observations remain outside A9 repository closure.

## 12. A10 — verifier TOCTOU/pathname-race assumption

Classification: `MISSING_PROOF`

Failure mechanism:
- pathname enumeration, lstat and later pathname opens allow substitution/race windows;
- repository verifier cannot by itself prove release immutability after verification.

Required invariant after repair:
- improve pathname-race resistance with directory-FD anchored/no-follow access where reasonably possible;
- use `dir_fd`/openat-style traversal and `O_NOFOLLOW` where supported;
- verify opened object type/identity with `fstat`;
- detect mutation during reads where feasible, including before/after identity/metadata checks;
- fail closed on ambiguous type/identity/content changes during verification.

Mandatory RED-before / GREEN-after:
- concurrent substitution between enumeration and read where feasible;
- type change race;
- content mutation during inspection;
- static symlink substitution remains RED;
- deterministic valid release remains GREEN.

Allowed implementation surface:
- R2 implementation and R2 tests only.

Forbidden shortcuts:
- claiming repository code proves the release remains immutable after verification;
- treating pathname-only lstat + later open as race-proof.

Acceptance:
- verifier is materially hardened and fails closed for reproduced inspection-time races;
- any irreducible post-verification mutation window is explicitly preserved as:
  `TARGET_HOST_ONLY: immutability of the frozen release for the verification-to-first-mutation authority window`.

Closure type:
- repository-provable only for implemented race-hardening behavior;
- post-verification immutability is TARGET_HOST_ONLY and must later be sealed by Blue activation/mount controls.

## 13. M4 continuing index-independence requirements

The repaired verifier must continue to:
- avoid authoritative dependence on `git status`, `git diff`, `git ls-files` or cached index cleanliness;
- set `GIT_OPTIONAL_LOCKS=0` for all Git subprocesses;
- snapshot relevant index/lock metadata before/after;
- create no Git lock files;
- perform no Git command that writes objects or refreshes the index;
- emit deterministic canonical JSON plus SHA-256;
- make object-authority ambiguity RED.

The canonical report must state at least:
- replacement-object semantics disabled;
- replace refs absent;
- object-store locality proof;
- path-access/race-hardening method;
- residual TARGET_HOST_ONLY immutability boundary, if any.

## 14. No Builder self-certification

A Builder may say only:

`READY_FOR_INDEPENDENT_REVIEW`

It may not say:
- defect closed independently;
- Gate B safe;
- Gate B PASS;
- production-ready;
- t0-ready.

A green Builder CI is necessary but not sufficient.

## 15. Required post-repair flow

1. R1 Builder completes its lane and pushes exact-head green CI.
2. R2 Builder completes its lane and pushes exact-head green CI.
3. Blue integrates both lanes from the shared dispatch ancestry without manually reimplementing their fixes.
4. Integrated exact-head CI must be COMPLETED / SUCCESS.
5. Blue dispatches a new Astra adversarial recheck of A1-A10 plus search for new bypasses.
6. Only independent Astra may state `PASS_REPOSITORY_EVIDENCE`.
7. Even that status does not mean Gate B PASS. Target-host/activation-time boundaries remain separate.

## 16. Explicit non-reopen / non-authorization record

```text
F1_REOPENED = FALSE
F5_REOPENED = FALSE
V4_PRESTAGE_REOPENED = FALSE
TARGET_HOST_TOUCHED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
```
