# BUILDER — GATE B DEPLOYED-BYTE VERIFIER M4 REPAIR — 2026-09-21

## 0. Final status and safety boundary

`GATE_B_DEPLOYED_BYTE_VERIFIER_M4_REPAIR = READY_FOR_INDEPENDENT_REVIEW`

This Builder repair is repository-only.

```text
TARGET_HOST_TOUCHED = FALSE
FROZEN_V4_SRC_MODIFIED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
```

No claim of independent closure is made. Astra must independently re-run the repaired attacks and search for new bypasses.

## 1. Authority verified before implementation

Assigned branch:

`builder/gate-b-deployed-byte-verifier-m4-repair-2026-09-21`

Audited defective ancestor:

`845dfa3609a9bbb2f81b76cd4375189a30ec2232`

Pre-implementation branch HEAD:

`58b559767ddbb965c1ab6448dd7ec89dc46ec821`

Comparison against the audited delivery was exactly three commits ahead and zero behind. Those three commits were Blue repair authority / mission dispatch only:

1. `c00031cec9897083f662b180e47744d629b90326` — Blue repair specification;
2. `aa5f0dfad24e88c2ed945d7e5699874b8a48136a` — M1-M3 repair dispatch;
3. `58b559767ddbb965c1ab6448dd7ec89dc46ec821` — M4 repair dispatch.

No implementation delta existed above the audited delivery before this Builder started.

Authorities read:

- `QUANT_NORTH_STAR.md`;
- `governance/BLUE_GATE_B_RUN_AUTHORITY_REPAIR_SPEC_2026-09-21.md`;
- `handoff/BUILDER_GATE_B_DEPLOYED_BYTE_VERIFIER_M4_REPAIR_MISSION_2026-09-21.md`;
- Astra review at `02432fae0ceb6440d2aec2182d06756f7151c648`;
- `handoff/BUILDER_GATE_B_RUN_AUTHORITY_RETENTION_PRESTAGE_2026-09-21.md` from its authoritative prestage branch.

Frozen identity preserved:

```text
CANDIDATE_SHA = 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
GIT_TREE      = 4d15ef6f471213ee6ab56337b555d2906ef9bf16
```

## 2. Changed paths and implementation checkpoints

Builder-authored repair paths:

- `scripts/verify_gate_b_deployed_bytes.py`;
- `tests/test_gate_b_deployed_byte_verifier_m4_repair.py`;
- `STATE.md` — mechanical proof-inventory refresh only;
- this handoff.

Implementation commits before this handoff:

- `804035304af0125f4ed2d1b0416b0bcd39f405a9` — hardened M4 verifier;
- `afed5badea606ba2733d37cbde47274c4d507770` — dedicated M4 repair discriminants;
- `2311b855c9692d82dfe463d5f7d004e67b08d3b6` — proof inventory 392 -> 415.

Explicitly not modified:

- `scripts/quant_gate_b_runctl.py`;
- frozen V4 `src/`;
- target-host state;
- Gate-B activation state;
- F1/F5;
- t0 authority.

## 3. A6 — foreign object-store indirection

Classification entering repair: `REAL_DEFECT`.

### Original attack

The old verifier resolved both Git's object path and `.git/objects` before comparing them. Replacing `.git/objects` with a symlink to a foreign object store therefore made both resolved paths equal and allowed the foreign store to appear local.

### Repair

The verifier now fails closed unless all of the following are true:

- the release path has no symlink component;
- `.git` is a real directory, not a symlink or linked-worktree pointer file;
- `.git/commondir` indirection is absent;
- `.git/objects` is a real directory, not a symlink;
- the complete object-store directory tree is recursively checked with no-follow semantics and contains no symlink indirection;
- `.git/refs` is also checked for symlink indirection;
- `.git/HEAD`, `.git/config`, and `.git/packed-refs`, where present, are real regular files;
- the lexical absolute git-dir is exactly release-local `.git`;
- common-dir is exactly the same release-local `.git`;
- Git's object directory is exactly release-local `.git/objects`;
- `.git/objects/info/alternates` is absent, including an empty file;
- external `GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, and `GIT_REPLACE_REF_BASE` authority overrides are rejected;
- object authority is rechecked after byte inspection and any drift fails closed.

No resolve-equality is used as locality proof.

### Discriminants

Committed tests include:

- `test_objects_symlink_to_foreign_store_red`;
- `test_dotgit_symlink_red`;
- `test_dotgit_text_pointer_red`;
- `test_nested_object_directory_symlink_red`;
- `test_alternates_file_red_even_empty`;
- `test_object_store_environment_overrides_red`;
- `test_foreign_common_dir_indirection_red`;
- `test_linked_worktree_red`.

The exact A6 attack copies a sufficient legitimate object store to a foreign directory, replaces local `.git/objects` with a symlink, proves ordinary Git can still resolve the expected HEAD/tree, then requires the repaired verifier to reject.

### Observed result

All committed A6 discriminants were observed `ok` in the full GitHub Actions unit suite on implementation checkpoint `2311b855...`.

## 4. A7 — replacement-object poisoning

Classification entering repair: `REAL_DEFECT`.

### Original attack

A `refs/replace/<EXPECTED_TREE> -> <MALICIOUS_TREE>` mapping could preserve the apparent expected tree identifier while making ordinary `git ls-tree <EXPECTED_TREE>` return malicious replacement content. Malicious deployed bytes could then match the poisoned listing.

### Repair

Every Git subprocess used by the verifier now executes with:

```text
GIT_OPTIONAL_LOCKS=0
GIT_NO_REPLACE_OBJECTS=1
GIT_CONFIG_NOSYSTEM=1
GIT_CONFIG_GLOBAL=/dev/null
```

Additionally:

- `refs/replace/*` is explicitly enumerated and any entry is RED;
- `.git/info/grafts` is explicitly dispositioned as legacy replacement metadata and is RED if present;
- replacement authority is checked both before and after authoritative object reads.

### Discriminants

- `test_replace_ref_poisoning_is_rejected_before_authoritative_tree_read` first proves the unrepaired Git semantics are poisonable: expected tree ID remains apparent while ordinary `ls-tree` returns the malicious tree; the repaired verifier then rejects the replace ref.
- `test_legacy_grafts_metadata_red` rejects legacy graft metadata.

### Observed result

Both A7 discriminants were observed `ok` in GitHub Actions.

## 5. A8 — real frozen positive control

Classification entering repair: `TEST_DEFECT`.

### Original defect

The legacy test named `test_exact_frozen_tree_green` actually created and verified a new synthetic commit/tree. It did not exercise the frozen candidate/tree.

That legacy synthetic control was not rewritten in the shared M1-M4 test file, avoiding conflict with the parallel M1-M3 Builder. It remains only a synthetic regression. A new dedicated M4 control supplies the required real proof.

### Repair / discriminant

`test_real_frozen_candidate_green_from_self_contained_local_clone`:

1. uses the repository checkout as the local-only object source;
2. creates a disposable clone with `git clone --no-local --no-checkout`;
3. uses no network and no linked worktree;
4. checks that no alternates file exists;
5. checks copied object files are not hardlinked (`st_nlink <= 1`);
6. checks out exactly `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`;
7. asserts its tree is exactly `4d15ef6f471213ee6ab56337b555d2906ef9bf16`;
8. runs the repaired verifier and requires `GREEN`.

### Observed result

GitHub Actions log:

`test_real_frozen_candidate_green_from_self_contained_local_clone ... ok`

Therefore the committed positive control actually exercised the real frozen candidate/tree from self-contained local object storage.

## 6. A9 — M4 proof-gap closure

Classification entering repair: `MISSING_PROOF`.

A dedicated M4 test file adds 23 committed tests. The repository proof inventory increased mechanically from 392 to 415 tests.

Coverage includes:

| Required control | Committed disposition |
| --- | --- |
| tracked byte mutation | RED |
| executable-bit mutation | RED |
| tracked regular -> symlink | RED |
| expected symlink -> regular | RED in synthetic tracked-symlink fixture |
| missing tracked file | RED |
| critical untracked file | RED |
| noncritical untracked file | RED |
| linked worktree | RED |
| `.git` symlink | RED |
| `.git` text pointer | RED |
| `.git/objects` foreign symlink | RED |
| alternates file | RED even empty |
| `GIT_OBJECT_DIRECTORY` | RED |
| `GIT_ALTERNATE_OBJECT_DIRECTORIES` | RED |
| common-dir indirection | RED |
| nested object-dir indirection | RED |
| replace refs | RED |
| legacy graft metadata | RED |
| invalid/traversing allowed-extra prefix | RED |
| index bytes/mtime unchanged | GREEN positive assertion |
| no new Git lock files | GREEN positive assertion |
| exact frozen candidate/tree | GREEN |
| substitution between enumeration/read | fail-closed |
| concurrent content mutation during read | fail-closed |

The full unit suite observed all 415 tests passing.

## 7. A10 — pathname / TOCTOU hardening

Classification entering repair: `MISSING_PROOF`.

### Repair

Tracked-byte inspection is no longer a pathname-only lstat followed by later pathname read.

The verifier now:

- opens and anchors the release root directory FD;
- traverses tracked parent directories with `dir_fd` / openat-style access;
- uses `O_NOFOLLOW` where available;
- compares pathname metadata and opened-object `fstat` identity;
- keeps parent directory FDs open and verifies the parent chain remained the same;
- reads regular-file bytes from the opened FD;
- compares pre-open/opened/post-read/post-path identity and mode/size/mtime/ctime metadata;
- reads tracked symlink target bytes with `readlink(..., dir_fd=...)` without dereferencing;
- verifies symlink metadata before/after;
- validates executable semantics from the opened object;
- anchors filesystem enumeration at the root FD.

### Discriminants

- `test_path_substitution_between_enumeration_and_read_fails_closed`;
- `test_concurrent_content_mutation_during_read_fails_closed`;
- static regular/symlink type substitutions also remain RED.

### Observed result

Both race/path-substitution tests were observed `ok` in GitHub Actions.

### Residual boundary

Repository code does not and cannot claim the release remains immutable after verification.

The unresolved condition is intentionally preserved exactly as:

`TARGET_HOST_ONLY: immutability of the frozen release for the verification-to-first-mutation authority window`

That condition must be established later by Blue activation / target-host mount and immutability controls.

## 8. Index independence and canonical report

Authoritative verification still does not use:

- `git status`;
- `git diff`;
- `git ls-files`;
- cached index cleanliness.

All verifier Git subprocesses use `GIT_OPTIONAL_LOCKS=0`.

The verifier snapshots index bytes/size/mtime plus existing `*.lock` metadata before and after verification. A difference produces RED `git_metadata_write_detected`.

The canonical JSON report is deterministic in key ordering/serialization and remains SHA-256 addressed. It now explicitly reports:

- replacement-object semantics disabled;
- replace refs absent;
- legacy grafts absent;
- object-store locality proof;
- root-FD / no-follow race-hardening method;
- Git metadata unchanged;
- residual target-host-only immutability boundary.

Any object-authority ambiguity raises a verifier precondition failure / RED.

## 9. Observed tests and CI

Disposable Builder-local synthetic M4 run before push:

`22/22 synthetic M4 tests = OK`

The real frozen candidate control was intentionally left to the full repository checkout because the isolated Builder sandbox did not contain the repository object database.

Implementation exact-head:

`2311b855c9692d82dfe463d5f7d004e67b08d3b6`

GitHub Actions:

`35594848962 = COMPLETED / SUCCESS`

Observed workflow evidence:

- status artifact freshness = SUCCESS;
- full unit suite = SUCCESS;
- `Ran 415 tests in 45.356s`;
- `OK`;
- SEC P0 lane suite = SUCCESS;
- V1 end-to-end regression = SUCCESS;
- exact-head verification artifact generation = SUCCESS;
- artifact upload = SUCCESS;
- clean working tree = SUCCESS;
- exact verification record: `415 tests (267 in the SEC P0 lane), all passed`, recorded against `2311b855...`.

A prior run at `afed5b...` failed only because `STATE.md` still stated 392 tests. Its log explicitly generated 415. Commit `2311b855...` made exactly the authorized mechanical 392 -> 415 refresh; the subsequent exact-head run is green.

## 10. Delivery identity note

A Git commit cannot truthfully embed its own final SHA inside the bytes that determine that SHA. Therefore this document records the exact implementation checkpoint immediately before the handoff commit:

`2311b855c9692d82dfe463d5f7d004e67b08d3b6`

The authoritative final delivery identity is the remote branch ref after this handoff is pushed:

`refs/heads/builder/gate-b-deployed-byte-verifier-m4-repair-2026-09-21`

Blue/Astra must pin that ref to its exact SHA at reception. The Builder's final response also reports that exact remote SHA and its exact-head CI only after they are actually observed.

## 11. Final disposition

No target-host mutation occurred. No Gate-B mutation authority was granted. No Gate-B PASS or t0 was declared.

`GATE_B_DEPLOYED_BYTE_VERIFIER_M4_REPAIR = READY_FOR_INDEPENDENT_REVIEW`
