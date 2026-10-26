# BUILDER MISSION — GATE B DEPLOYED-BYTE VERIFIER M4 REPAIR — 2026-09-21

## 0. Mission identity

Role: implementation Builder.

Repository: `fahimahmedb/Quant-Trade`

Work only on:

`builder/gate-b-deployed-byte-verifier-m4-repair-2026-09-21`

Do not create another branch.

This mission is dispatched from:

`blue/gate-b-run-authority-repair-dispatch-2026-09-21`

The exact shared Builder starting SHA is the immutable dispatch commit from which Blue creates both repair branches after this mission file and its R1 sibling are present. Because a Git commit cannot literally contain its own SHA, do not accept a stale hard-coded self-reference: at mission start resolve the assigned Builder branch, verify the sibling R1 Builder branch was created from the same parent if it exists, and verify the Blue reception record names the same exact dispatch SHA.

Audited defective ancestor:

`845dfa3609a9bbb2f81b76cd4375189a30ec2232`

Astra defect authority:

`astra/gate-b-run-authority-mechanisms-independent-review-2026-09-21@02432fae0ceb6440d2aec2182d06756f7151c648`

Astra exact-head CI:

`35588182384 = COMPLETED / SUCCESS`

Frozen candidate:

```text
CANDIDATE_SHA = 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
GIT_TREE = 4d15ef6f471213ee6ab56337b555d2906ef9bf16
```

## 1. Read before implementation

Read in full:

1. `QUANT_NORTH_STAR.md`
2. `governance/BLUE_GATE_B_RUN_AUTHORITY_REPAIR_SPEC_2026-09-21.md`
3. this mission file
4. `handoff/ASTRA_GATE_B_RUN_AUTHORITY_MECHANISMS_INDEPENDENT_REVIEW_2026-09-21.md` from the Astra commit above
5. `handoff/BUILDER_GATE_B_RUN_AUTHORITY_RETENTION_PRESTAGE_2026-09-21.md` from its authoritative prestage branch

The Blue repair spec is the implementation contract. Astra's reproduced attacks are the adversarial oracle.

## 2. Scope

Repair only:

- A6 `REAL_DEFECT` — foreign object store via `.git/objects` symlink/indirection;
- A7 `REAL_DEFECT` — Git replace refs poison authoritative object reads;
- A8 `TEST_DEFECT` — fake exact-frozen positive control;
- A9 `MISSING_PROOF` — M4 negative-control gaps;
- A10 `MISSING_PROOF` — pathname-race / TOCTOU assumptions.

Primary implementation:

`scripts/verify_gate_b_deployed_bytes.py`

Prefer dedicated R2 tests to avoid conflict with R1.

May modify:
- `scripts/verify_gate_b_deployed_bytes.py`;
- M4-specific tests;
- `handoff/BUILDER_GATE_B_DEPLOYED_BYTE_VERIFIER_M4_REPAIR_2026-09-21.md`;
- `STATE.md` only for a mechanical proof-inventory refresh legitimately required by repository tooling.

Must not modify:
- `scripts/quant_gate_b_runctl.py`;
- frozen V4 `src/`;
- target-host state;
- Gate-B activation state;
- F1;
- F5;
- t0 authority.

## 3. A6 — object-store locality hardening

Do not use `resolve()` equality in a way that turns a symlink into apparent locality.

Independently verify and fail closed unless:
- `.git` is a real local directory, not a symlink;
- `.git` is not a linked-worktree pointer file;
- `.git/objects` is a real local directory, not a symlink;
- relevant Git metadata/object path components are not symlinked or foreign;
- absolute git-dir is release-local;
- common-dir is local and identical to intended release-local Git metadata;
- object dir is release-local without indirection;
- alternates are absent;
- `GIT_OBJECT_DIRECTORY` is absent/rejected;
- `GIT_ALTERNATE_OBJECT_DIRECTORIES` is absent/rejected.

Use `lstat`/no-follow semantics for path-type authority.

Mandatory exact attack:
1. make a legitimate local Git repo containing sufficient expected objects;
2. move/copy object store to a foreign directory;
3. replace `.git/objects` with a symlink to the foreign object store;
4. show Git can still read the expected commit/tree;
5. repaired verifier must reject before trusting expected-tree data.

## 4. A7 — replacement-object hardening

All authoritative Git reads must be immune to replacement-object semantics.

At minimum:
- run authoritative Git object reads with replacement objects disabled;
- explicitly enumerate and reject `refs/replace/*`;
- explicitly inspect/disposition legacy graft/replacement metadata relevant to installed Git;
- any replacement ambiguity is RED.

Mandatory attack:
1. create legitimate expected commit/tree;
2. create malicious tree;
3. install replace authority for `EXPECTED_TREE`;
4. keep expected identifiers apparently resolving;
5. deploy malicious bytes matching replacement tree;
6. demonstrate unrepaired semantics can be poisoned;
7. repaired verifier rejects before trusting poisoned `ls-tree`.

Do not protect only one Git command. Every authoritative read that can be affected must use hardened semantics.

## 5. Continuing index independence

Continue to prohibit authoritative dependence on:
- `git status`;
- `git diff`;
- `git ls-files`;
- cached index cleanliness.

All Git subprocesses must set:

`GIT_OPTIONAL_LOCKS=0`

Snapshot relevant index and lock metadata before/after.

No Git command may:
- refresh/write index;
- create lock files;
- write Git objects.

A passing verification must prove relevant index bytes/mtime are unchanged and no unexpected Git lock appeared.

## 6. A10 — path/TOCTOU hardening

Address inspection-time races as far as repository code can actually prove.

Prefer:
- root directory-FD anchoring;
- `dir_fd` / openat-style traversal;
- `O_NOFOLLOW` where available;
- `lstat` for path policy;
- `fstat` for the actually opened object;
- validation of opened object type/mode/identity;
- mutation detection during reads via before/after fstat or an equivalently strong strategy;
- no implicit symlink dereference.

Fail closed if a tracked path changes type, identity, metadata or contents during inspection in a way that makes the result ambiguous.

Do not claim repository code proves bytes cannot change after verification.

Preserve this residual boundary if irreducible:

`TARGET_HOST_ONLY: immutability of the frozen release for the verification-to-first-mutation authority window`

That later condition must be sealed by Blue activation/mount controls.

## 7. A8 — exact frozen positive control

The committed positive control must actually verify:

```text
candidate = 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
tree      = 4d15ef6f471213ee6ab56337b555d2906ef9bf16
```

Do not create a new synthetic commit and call it exact-frozen.

Use a disposable self-contained local clone/copy of repository objects.

Do not use:
- linked worktree;
- alternates;
- foreign object store;
- hardlink/object-storage behavior that undermines the self-contained-independence proof.

The test must not require network access.

The real frozen candidate positive control must be GREEN.

## 8. Mandatory R2 negative controls

At minimum commit/reproduce:

- tracked byte mutation;
- executable-bit mutation;
- tracked regular file -> symlink;
- expected symlink -> regular file where applicable;
- missing tracked file;
- critical untracked file;
- noncritical untracked file;
- linked worktree;
- `.git` symlink;
- `.git` linked-worktree text file;
- `.git/objects` symlink to foreign store;
- alternates file;
- `GIT_OBJECT_DIRECTORY`;
- `GIT_ALTERNATE_OBJECT_DIRECTORIES`;
- foreign/indirected common dir;
- foreign/indirected object dir;
- replace refs;
- any legacy graft/replacement mechanism explicitly relevant to installed Git;
- invalid allowed-extra prefix;
- traversal attempt;
- index bytes/mtime unchanged;
- no new Git lock files;
- exact frozen candidate GREEN.

Where practical, add independent concurrent/path mutation discriminants:
- substitution between enumeration and read;
- tracked type change during verification;
- content mutation during verification.

Tests use disposable temporary directories/repositories only.

## 9. Canonical report

Retain deterministic canonical JSON plus SHA-256.

Any object-authority ambiguity is RED.

The report must explicitly state:
- replacement-object semantics disabled;
- replace refs absent;
- object-store locality proof;
- path-access/race-hardening method;
- index/lock no-write result;
- residual TARGET_HOST_ONLY immutability assumption, if any.

## 10. Regression

Run:
- all R2 targeted repair tests;
- relevant existing Gate-B verifier/run-authority tests;
- repository-required test command/CI.

Do not delete or weaken a negative control to make the implementation pass.

## 11. Handoff

Write:

`handoff/BUILDER_GATE_B_DEPLOYED_BYTE_VERIFIER_M4_REPAIR_2026-09-21.md`

For A6-A10 provide:
- original attack/failure;
- exact repair;
- exact discriminant/test;
- observed result;
- residual host-only boundary;
- changed paths;
- exact final Builder HEAD;
- exact-head CI only if actually observed.

Final status may be only:

`GATE_B_DEPLOYED_BYTE_VERIFIER_M4_REPAIR = READY_FOR_INDEPENDENT_REVIEW`

or a precise blocker.

Do not self-award `PASS_REPOSITORY_EVIDENCE`.

## 12. Commit / safety

Commit and push only to:

`builder/gate-b-deployed-byte-verifier-m4-repair-2026-09-21`

Verify final remote SHA.

Never fabricate CI completion.

```text
TARGET_HOST_TOUCHED = FALSE
FROZEN_V4_SRC_MODIFIED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
```
