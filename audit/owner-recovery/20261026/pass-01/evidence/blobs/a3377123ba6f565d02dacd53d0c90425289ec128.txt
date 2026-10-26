# ASTRA — GATE B RUN-AUTHORITY MECHANISMS RECHECK MISSION — 2026-09-21

## 0. Role and authority

You are Astra, the independent adversarial reviewer for the repaired Quant Gate-B run-authority mechanisms.

You are **not** Blue and you are **not** either Builder.

Do not accept Builder conclusions, Blue reception language, or green CI as proof of correctness. Reproduce the attacks independently against the exact integrated object below and actively search for bypasses that the repair lanes did not anticipate.

Repository:

`fahimahmedb/Quant-Trade`

Work only on:

`astra/gate-b-run-authority-mechanisms-recheck-2026-09-21`

The branch was created directly from this exact integrated candidate:

`644da76eb0227be275b8e3448118dac0cc7096ca`

Do not modify that audited integrated object. Any Astra commit above it must be audit mission/evidence/handoff material only unless Blue explicitly issues new authority.

## 1. Exact integrated candidate and CI

Integrated candidate branch:

`blue/gate-b-run-authority-repair-integration-2026-09-21`

Exact candidate SHA:

`644da76eb0227be275b8e3448118dac0cc7096ca`

Exact-head GitHub Actions:

`35598077120 = COMPLETED / SUCCESS`

Exact-head verification artifact:

`sec-p0-verification-644da76eb0227be275b8e3448118dac0cc7096ca`

The integrated CI ran the repository full unit discovery, including both dedicated repair suites, but that CI is only a starting observation. It is not independent correctness evidence.

## 2. Mandatory authority to read first

Read in full:

1. `QUANT_NORTH_STAR.md`
2. `governance/BLUE_GATE_B_RUN_AUTHORITY_REPAIR_SPEC_2026-09-21.md`
3. original independent review:
   `handoff/ASTRA_GATE_B_RUN_AUTHORITY_MECHANISMS_INDEPENDENT_REVIEW_2026-09-21.md`
   from:
   `astra/gate-b-run-authority-mechanisms-independent-review-2026-09-21@02432fae0ceb6440d2aec2182d06756f7151c648`
4. Builder R1 mission and final handoff:
   - `handoff/BUILDER_GATE_B_RUN_AUTHORITY_M1_M3_REPAIR_MISSION_2026-09-21.md`
   - `handoff/BUILDER_GATE_B_RUN_AUTHORITY_M1_M3_REPAIR_2026-09-21.md`
5. Builder R2 mission and final handoff:
   - `handoff/BUILDER_GATE_B_DEPLOYED_BYTE_VERIFIER_M4_REPAIR_MISSION_2026-09-21.md`
   - `handoff/BUILDER_GATE_B_DEPLOYED_BYTE_VERIFIER_M4_REPAIR_2026-09-21.md`

Original audited defective Builder delivery:

`builder/gate-b-run-authority-mechanisms-2026-09-21@845dfa3609a9bbb2f81b76cd4375189a30ec2232`

Original independent Astra review SHA:

`02432fae0ceb6440d2aec2182d06756f7151c648`

Its blocker verdict remains the historical adversarial oracle until this mission independently establishes otherwise.

## 3. Verify mission object before testing

Before replay:

- fetch current repository state;
- verify this Astra branch descends from exact integrated SHA `644da76eb0227be275b8e3448118dac0cc7096ca`;
- verify the integration branch still resolves exactly to that SHA;
- verify GitHub Actions run `35598077120` is `COMPLETED / SUCCESS` and its head SHA is exactly the integrated SHA;
- compare the integrated candidate against shared repair dispatch `58b559767ddbb965c1ab6448dd7ec89dc46ec821`;
- verify the implementation ownership remains:
  - M1/M2/M3: `scripts/quant_gate_b_runctl.py`
  - M4: `scripts/verify_gate_b_deployed_bytes.py`
- verify frozen V4 production `src/` was not changed by the convergence;
- verify the integrated proof inventory is 444 tests and no lane-specific test file was dropped.

If object identity or ancestry differs, stop and classify the discrepancy instead of silently auditing a different candidate.

## 4. Independent adversarial recheck — A1 through A10

You must independently reproduce each relevant negative control. Do not merely read the Builder test and state that it looks correct.

### A1 — short/partial durability-critical writes

Independently attack registry and receipt writes with:

- one short write;
- repeated partial writes;
- EINTR/interrupted write;
- zero-progress write;
- mid-write hard failure.

Prove externally that incomplete authoritative state cannot return reusable consume authority.

### A2 — directory durability / receipt placement

Independently exercise:

- first registry creation and containing-directory durability path;
- existing-registry append;
- receipt final-directory fsync failure;
- placement/link failure;
- pre-existing final receipt collision;
- consumption event committed followed by receipt failure.

The last case must remain consumed and fail closed; no rollback or reusable second consumption is acceptable.

### A3 — freshness under actual lock contention

Use real independent-process contention on the actual lock primitive.

Required attack:

1. process A owns the exclusive lock;
2. process B begins consume while the activation is still fresh;
3. activation expires while B is blocked;
4. A releases;
5. B must reject using post-lock time.

Mock-only contention is insufficient.

### A4 — activation chronology

Independently reject:

- future-issued activation;
- future not-before activation;
- issued > not-before;
- not-before == expires;
- not-before > expires;
- expired activation;
- exact-expiry boundary;
- malformed/non-UTC time.

Retain a valid finite-window positive control.

### A5 — evidence binding to exact consumed activation

Independently attack with:

- another run's activation digest;
- sealed but unconsumed activation;
- digest different from the run's actual consumed activation;
- ordinal `"1"`;
- ordinal `true` / `false`;
- ordinal 0;
- negative ordinal;
- duplicate ordinal;
- unknown authority-relevant schema fields;
- malformed authority-relevant digests/types.

Accepted binding must prove exact run/reservation/candidate/host identity and the exact activation actually consumed.

### A6 — Git object-store indirection

Reproduce foreign/indirected authority attacks, including:

- `.git/objects` symlink to a foreign object store containing expected objects;
- `.git` symlink;
- linked-worktree `.git` file/pointer;
- alternates file;
- `GIT_OBJECT_DIRECTORY`;
- `GIT_ALTERNATE_OBJECT_DIRECTORIES`;
- foreign common-dir/object-dir indirection;
- symlinked release ancestry/path components where relevant.

The verifier must reject before trusting expected-tree bytes.

### A7 — replace/graft authority poisoning

Construct a real replace-ref poisoning attack against expected Git object reads.

Verify:

- unrepaired semantics would permit replacement poisoning;
- repaired authoritative reads are replacement-disabled;
- `refs/replace/*` ambiguity is explicitly rejected;
- relevant legacy graft/replacement mechanisms are dispositioned fail-closed.

Do not accept HEAD/tree identifier equality alone.

### A8 — real frozen candidate positive control

The positive control must genuinely exercise:

- candidate `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`;
- tree `4d15ef6f471213ee6ab56337b555d2906ef9bf16`.

It must use a self-contained disposable local object store, not a linked worktree or alternate authority.

Prove that the old synthetic control did not establish this fact, then prove the repaired control actually does.

### A9 — mandatory proof matrix

Re-run the complete R1 and R2 negative-control matrix from the Blue repair specification, including:

R1:
- independent-process flock;
- partial/short/EINTR/zero-progress writes;
- injected write failure;
- first-create durability;
- receipt collision and post-consumption failure;
- future/not-yet-valid/invalid chronology;
- wrong/unconsumed activation binding;
- ordinal type/range and duplicate bypasses.

R2:
- tracked byte mutation;
- executable-bit mutation;
- regular-file/symlink substitutions;
- missing tracked file;
- critical and noncritical untracked files;
- `.git` file/symlink;
- `.git/objects` symlink;
- alternates and Git object-directory environment overrides;
- common-dir/object-dir indirection;
- replace refs and relevant legacy replacement mechanisms;
- traversal/bad allowed-extra prefixes;
- index bytes/mtime unchanged;
- no new Git lock files;
- exact frozen-candidate positive control.

Do not omit a required attack because static inspection appears sufficient.

### A10 — TOCTOU / pathname-race hardening

Independently attempt:

- concurrent substitution between enumeration and read where feasible;
- file type change race;
- content mutation during inspection;
- static symlink substitution.

Verify the repaired verifier uses the intended no-follow/directory-FD/fstat-style hardening where implemented and fails closed on reproduced ambiguity.

Do **not** convert the irreducible post-verification boundary into repository proof.

The following remains an explicit host-only boundary unless separately proven on the target host:

`TARGET_HOST_ONLY: immutability of the frozen release for the verification-to-first-mutation authority window`

## 5. Search beyond known A1-A10

After replaying the known findings, actively search for new bypasses, especially:

- malformed but canonical-looking registry events;
- duplicate/ambiguous JSON semantics;
- crash boundaries around append/fsync/link/reopen;
- lock-path replacement or aliasing;
- cross-run or cross-attempt evidence laundering;
- timestamp boundary/clock-source inconsistencies;
- symlink or mount/path-component swaps;
- Git config/environment channels not named in the original audit;
- repository index mutation side effects;
- object-format/mode/symlink edge cases;
- report canonicalization or digest ambiguity;
- race windows introduced by the repair itself.

A clean replay of Builder tests alone is insufficient for PASS.

## 6. Required evidence and output

Use disposable local repositories/directories/processes only.

Do not touch the target host.

Do not modify frozen V4 production code.

Record:

- exact audited candidate SHA;
- exact CI run and head binding;
- exact commands/tests used;
- independent results for A1-A10;
- any newly discovered bypass;
- residual repository-only and TARGET_HOST_ONLY boundaries;
- changed paths on the Astra branch.

Required final handoff:

`handoff/ASTRA_GATE_B_RUN_AUTHORITY_MECHANISMS_RECHECK_2026-09-21.md`

Astra may state:

`PASS_REPOSITORY_EVIDENCE`

**only if** no repository defect, test defect, missing repository proof, or newly found repository blocker remains after independent reproduction.

If anything remains, return an explicit blocker classification instead.

Even `PASS_REPOSITORY_EVIDENCE` does not authorize Gate B, does not close target-host-only boundaries, and does not declare t0.

## 7. Safety state

```text
TARGET_HOST_TOUCHED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
INDEPENDENT_REVIEW_REQUIRED = TRUE
```
