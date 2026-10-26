# ASTRA — GATE B RUN-AUTHORITY MECHANISMS INDEPENDENT REVIEW — 2026-09-21

MISSION_TYPE = TARGETED INDEPENDENT REPOSITORY REVIEW

## Audit object

Builder branch:
`builder/gate-b-run-authority-mechanisms-2026-09-21`

Exact audited HEAD:
`845dfa3609a9bbb2f81b76cd4375189a30ec2232`

Builder exact-head CI:
`35585585066`

Activation condition:
the CI above MUST be `COMPLETED / SUCCESS` and the Builder branch MUST still
resolve exactly to `845dfa3609a9bbb2f81b76cd4375189a30ec2232`.

Until then:
`ASTRA_REVIEW_STATE = PRESTAGED_ONLY`

## Read first

1. `QUANT_NORTH_STAR.md`
2. `governance/BLUE_GATE_B_RUN_AUTHORITY_MECHANISMS_SPEC_2026-09-21.md`
3. `handoff/BUILDER_GATE_B_RUN_AUTHORITY_RETENTION_PRESTAGE_2026-09-21.md`
4. `handoff/BUILDER_GATE_B_RUN_AUTHORITY_MECHANISMS_MISSION_2026-09-21.md`
5. `handoff/BUILDER_GATE_B_RUN_AUTHORITY_MECHANISMS_2026-09-21.md`
6. exact changed files on audited HEAD.

## Independence

Do not start from Builder's verdict.
Do not modify the audited object.
Do not touch the target host.
Do not declare Gate B PASS or t0.

Verify branch/SHA/ancestry and changed-path scope independently.

## Required review

### M1 registry / F2

Independently attack:
- duplicate reservation;
- run-ID collision/reuse;
- monotonic attempts;
- concurrent nonterminal run;
- cross-process locking;
- malformed/truncated ledger;
- digest-chain tampering;
- partial/crash write behavior;
- fsync/atomicity claims;
- FAILED_TERMINAL non-reuse;
- cross-run evidence relabeling;
- registry-inside-checkout rejection;
- stale active/nonterminal state handling.

Look specifically for windows where an append/receipt/lock failure could leave
authority ambiguous or reusable.

### M2/M3 activation / F3

Independently attack:
- consume without reservation;
- wrong run ID;
- wrong candidate triple;
- wrong activation digest;
- noncanonical activation bytes;
- wrong reservation digest;
- stale/not-yet-valid/expired activation;
- revocation epoch/reference drift;
- explicit activation revocation;
- second consumption;
- terminal run consumption;
- receipt collision / pre-existing receipt;
- event committed but receipt failed;
- receipt written but event failed;
- timestamp/timezone edge cases.

Determine whether failure modes are fail-closed and whether any recovery state
could silently permit reuse.

### M4 deployed-byte verifier / F7

Independently attack:
- tracked byte mutation;
- executable-mode mutation;
- symlink substitution;
- missing tracked file;
- critical and noncritical untracked files;
- linked worktree;
- .git symlink/file substitution;
- Git alternates;
- GIT_OBJECT_DIRECTORY / GIT_ALTERNATE_OBJECT_DIRECTORIES;
- common-dir/object-dir indirection;
- index/cache writes despite `GIT_OPTIONAL_LOCKS=0`;
- path traversal / allowed-extra-prefix abuse;
- TOCTOU-sensitive assumptions;
- exact frozen SHA/tree positive control.

Confirm it does not depend on `git status`, cached index cleanliness, or a
foreign object store.

### CI/status correction

Verify the only post-delivery correction at
`845dfa3609a9bbb2f81b76cd4375189a30ec2232` is the mechanical STATE.md proof
inventory refresh required by the added 21 tests. Do not transfer any proof from
the earlier failed exact-head run.

## Required classification

For every finding use one of:
`REAL_DEFECT | TEST_DEFECT | MISSING_PROOF | TARGET_HOST_ONLY | NON_ISSUE`.

A green CI is not independent proof.

## Output

Write:
`handoff/ASTRA_GATE_B_RUN_AUTHORITY_MECHANISMS_INDEPENDENT_REVIEW_2026-09-21.md`

Final status exactly one:

`ASTRA_GATE_B_RUN_AUTHORITY_REVIEW = PASS_REPOSITORY_EVIDENCE`

or a precise blocker.

If PASS, explicitly enumerate remaining TARGET_HOST_ONLY / activation-time proof
that is not closed by repository review.

Commit and push only Astra audit/handoff material to this SAME branch.
Return control to Blue.
