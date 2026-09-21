# ASTRA — GATE B RUN-AUTHORITY MECHANISMS INDEPENDENT REVIEW — 2026-09-21

## 0. Final status

`ASTRA_GATE_B_RUN_AUTHORITY_REVIEW = BLOCKED_REAL_DEFECTS_M1_DURABILITY_M2_FRESHNESS_BINDING_M4_GIT_INDIRECTION`

Return control to Blue.

This review is repository-only. No target host was touched, no frozen V4 production `src/` object was modified, Gate B was not authorized or started, and t0 was not declared.

## 1. Audit object and preconditions

Mission branch:

`astra/gate-b-run-authority-mechanisms-independent-review-2026-09-21`

Mission HEAD verified immediately before review write:

`ddb8b4bf330969b1e69ea2147fd862f88585e8c5`

Audited Builder branch:

`builder/gate-b-run-authority-mechanisms-2026-09-21`

Audited Builder HEAD verified immediately before review write:

`845dfa3609a9bbb2f81b76cd4375189a30ec2232`

Builder exact-head CI:

`35585585066 = COMPLETED / SUCCESS`

The workflow run reports:

- head branch = `builder/gate-b-run-authority-mechanisms-2026-09-21`;
- head SHA = `845dfa3609a9bbb2f81b76cd4375189a30ec2232`;
- status = `completed`;
- conclusion = `success`.

The audited delivery is exactly five commits ahead of the implementation dispatch `cf420ee05542e22917b23d712a0de304dd4b4969`. The changed paths are limited to:

- `scripts/quant_gate_b_runctl.py`;
- `scripts/verify_gate_b_deployed_bytes.py`;
- `tests/test_gate_b_run_authority.py`;
- `handoff/BUILDER_GATE_B_RUN_AUTHORITY_MECHANISMS_2026-09-21.md`;
- `STATE.md`.

The final `845dfa...` correction modifies only `STATE.md`, refreshing the proof inventory from 371 to 392 tests. No proof is transferred from the earlier failed exact-head state.

The frozen candidate identity was independently re-resolved through repository objects:

- candidate SHA = `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`;
- candidate tree = `4d15ef6f471213ee6ab56337b555d2906ef9bf16`.

The recursive frozen tree contains 247 entries: 215 regular `100644` blobs and 32 trees; no unsupported submodule/special mode appears.

## 2. Review method

Builder conclusions were not accepted as proof.

The review inspected the exact Builder bytes for M1-M4, the Blue mechanism spec, the earlier run-authority prestage contract, the Builder mission, the Builder handoff, the exact changed-path scope and exact-head CI metadata.

The sandbox cannot reach GitHub directly with local `git clone/fetch`; live branch/ref verification therefore used the GitHub connection. Independent attack reproductions that do not require repository network access were executed in disposable local Git repositories only. In particular, the M4 foreign object-store symlink and Git replace-ref attacks below were reproduced against local Git.

## 3. Findings

### A1 — registry / receipt short writes can be reported as success

Classification: `REAL_DEFECT`

Affected: M1 / M2 crash and partial-write safety.

`Registry._append()` performs one `os.write(...)`, ignores the returned byte count, then `fsync()`s and returns success. A regular-file write is permitted to return fewer bytes than requested without raising. In that case the registry can end with a truncated event while the call still returns the event as successfully committed.

For `ACTIVATION_CONSUMED`, that means the consumer can return authority even though the durable registry bytes do not contain the complete consumed event. The next load will detect truncation, but that is after authority may already have been returned.

`_write_once()` has the same defect for receipt bytes: one unchecked `os.write()` can create a hash-addressed receipt path whose contents do not match the receipt digest while the function returns success.

Required repair: use a full-write primitive/loop and fail before returning authority unless the exact intended bytes are durably present.

### A2 — directory durability claimed by Builder is not implemented

Classification: `REAL_DEFECT`

Affected: M1 fsync/atomicity and M2 receipt durability.

The Builder handoff states that each registry append fsyncs the containing directory. The implementation fsyncs the registry file descriptor but never fsyncs the containing directory.

This matters at least for first creation of the authoritative registry path and for crash/power-loss durability of the directory entry.

Receipt materialization fsyncs the temporary receipt file and hard-links it to the hash-addressed final path, but does not fsync the receipt directory after the link. A consume call can therefore return success while the final receipt directory entry is not crash-durable.

This contradicts the prestage requirement to fsync the control record and containing directory before returning success.

### A3 — activation freshness is evaluated before lock acquisition

Classification: `REAL_DEFECT`

Affected: M2/M3 atomic consumption and expiry.

`consume_activation()` captures `now` before `self._mut(...)` acquires the exclusive registry lock. The freshness test inside the locked mutation uses that pre-lock timestamp.

Therefore:

1. consumer A can hold the registry lock;
2. consumer B calls consume while the activation is still valid and captures `now`;
3. B waits for the lock until after `expires_at_utc`;
4. B acquires the lock and still evaluates freshness using the earlier pre-lock time;
5. the expired activation can be consumed.

The consumption event and receipt also use the stale pre-lock timestamp.

Required repair: obtain/recompute authoritative current time after the exclusive lock is acquired and immediately before the consumption append.

### A4 — future `issued_at_utc` is parsed but not enforced

Classification: `REAL_DEFECT`

Affected: M3 freshness / timestamp edge cases.

The activation parser validates that `issued_at_utc` is syntactically a UTC timestamp, but the consumer only checks:

`not_before_utc <= now < expires_at_utc`

It does not check `issued_at_utc <= now`, nor a chronology invariant tying issued/not-before/expiry together.

A canonical activation with `issued_at_utc` in the future, `not_before_utc` in the past and `expires_at_utc` in the future satisfies the current consume predicate.

This directly contradicts the Builder handoff statement that future `issued_at` is rejected.

### A5 — evidence binding does not bind to the activation actually consumed

Classification: `REAL_DEFECT`

Affected: M1 anti-laundering / cross-run evidence binding.

`bind_evidence()` verifies reservation identity and that the run has some `ACTIVATION_CONSUMED` event, but it never verifies that the binding envelope's `activation_digest` equals the activation digest actually consumed for that run.

`validate_registry()` likewise accepts `EVIDENCE_BOUND.activation_digest` without comparing it with the run's sealed/consumed activation.

Consequently a fresh artifact can be bound to run B while the binding names the activation digest from run A, provided the other reservation fields are rewritten for run B and the raw artifact digest has not already been owned by another run.

That violates the prestage requirement that evidence whose activation digest differs be rejected.

Additional weakness: `artifact_ordinal` is not type/range constrained, so semantically equivalent ordinals such as integer `1` and string `"1"` are distinct keys to the duplicate check.

### A6 — foreign object store via `.git/objects` symlink passes M4 independence

Classification: `REAL_DEFECT`

Affected: M4 linked/object-store independence.

`ensure_git_independence()` compares:

- Git's resolved object path; and
- `(expected_git_dir / "objects").resolve()`.

If `.git/objects` itself is a symlink to a foreign object store, both sides resolve to the same foreign path, so the equality check passes.

Independent disposable-repository reproduction:

- `.git` remained a normal local directory;
- `.git/objects` was replaced with a symlink to a foreign directory;
- git-dir comparison passed;
- common-dir comparison passed;
- object-dir comparison passed;
- Git could still read the exact HEAD commit and tree from the foreign store.

The implementation therefore does not prove that the object store is release-local and non-indirected.

### A7 — Git replace refs can poison the expected tree while preserving the expected tree ID

Classification: `REAL_DEFECT`

Affected: M4 exact frozen-tree authority.

The verifier neither rejects `refs/replace/*` nor runs Git with replacement objects disabled.

Independent disposable-repository reproduction:

1. create a frozen commit/tree;
2. create a second tree with malicious deployed bytes;
3. install `refs/replace/<EXPECTED_TREE> -> <MALICIOUS_TREE>`;
4. reset HEAD to the frozen commit;
5. leave the worktree bytes equal to the malicious tree.

Observed behavior:

- `git rev-parse HEAD^{tree}` still returned the expected frozen tree ID;
- `git ls-tree <EXPECTED_TREE>` returned the malicious replacement tree entries;
- hashing the malicious deployed bytes matched the OIDs supplied by `ls-tree`.

Thus the verifier's central byte-comparison conditions can become GREEN for bytes not belonging to the actual frozen tree object.

Required repair: explicitly reject replace refs and/or execute authoritative object reads with replacement-object semantics disabled, then independently verify the absence of replacement indirection.

### A8 — exact frozen-tree positive control is not actually exercised

Classification: `TEST_DEFECT`

The test named `test_exact_frozen_tree_green` creates a new disposable Git repository and verifies that synthetic commit/tree. It does not exercise:

- `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`;
- tree `4d15ef6f471213ee6ab56337b555d2906ef9bf16`.

The repository confirms that exact candidate/tree pair exists and is compatible with the verifier's supported regular-file modes, so this is a repository-test coverage gap rather than a target-host-only impossibility.

### A9 — cross-process locking and several required negative controls are not reproduced by the committed test suite

Classification: `MISSING_PROOF`

The 21-test file checks logical concurrent-run rejection sequentially; it does not spawn independent processes contending on `flock()`.

The committed tests also do not independently exercise all review-mandated attacks, including:

- future-issued and not-yet-valid activations;
- pre-existing receipt collision and injected receipt/event write failures;
- short writes;
- executable-mode mutation;
- tracked-file/symlink substitution;
- noncritical untracked path;
- `.git` symlink substitution;
- `GIT_OBJECT_DIRECTORY` / `GIT_ALTERNATE_OBJECT_DIRECTORIES` environment attacks;
- common/object-dir symlink indirection;
- replace refs;
- invalid/traversing allowed-extra prefixes;
- exact frozen candidate positive control.

Several of these are handled by static code paths, but the missing tests cannot be counted as independent reproduced proof.

### A10 — verifier has an unresolved TOCTOU assumption

Classification: `MISSING_PROOF`

M4 walks paths, then separately `lstat()`s and later opens/reads them by pathname. It does not use directory-FD anchored `openat`/no-follow/fstat verification and does not itself establish an immutable/read-only snapshot for the entire verification window.

A concurrent writer can therefore race pathname/type/byte checks or mutate after verification. Repository code alone does not prove the target release cannot change during or immediately after the check.

This must be closed either by a race-resistant verifier or by independently proven target-host immutability/mount controls that are sealed into activation.

## 4. Discriminant disposition

| Discriminant / attack | Independent disposition |
| --- | --- |
| duplicate run ID | `NON_ISSUE` for single-registry logical path; full cross-process proof still missing |
| monotonic attempt | `NON_ISSUE` under validated registry + exclusive mutation path |
| concurrent nonterminal same host | `NON_ISSUE` logically; cross-process lock proof = `MISSING_PROOF` |
| reuse after `FAILED_TERMINAL` | `NON_ISSUE` |
| malformed/truncated ledger | `NON_ISSUE` on subsequent load, but short-write success window = A1 `REAL_DEFECT` |
| registry digest-chain tamper | `NON_ISSUE` for ordinary in-place modification detection |
| consume without reservation | `NON_ISSUE` |
| wrong activation digest | `NON_ISSUE` |
| wrong candidate / reservation identity | `NON_ISSUE` for activation-vs-reservation consistency |
| stale / expired activation | `REAL_DEFECT` because expiry can age out while waiting for the lock |
| future-issued activation | `REAL_DEFECT` |
| revocation epoch/reference drift | `NON_ISSUE` under the locked registry path |
| explicit activation revocation | `NON_ISSUE` |
| second consume | `NON_ISSUE` |
| terminal-run consume | `NON_ISSUE` |
| receipt written before event failure | `NON_ISSUE`: event append precedes receipt materialization |
| event committed then receipt failure | fail-closed for reuse, but receipt durability/short-write defects remain A1/A2 |
| cross-run artifact digest reuse | `NON_ISSUE` for exact raw digest reuse |
| evidence activation binding | `REAL_DEFECT` A5 |
| tracked byte mutation | `NON_ISSUE` absent object-authority poisoning/TOCTOU |
| executable-mode mutation | static code path appears fail-closed; committed negative test missing |
| static symlink substitution | static code path appears fail-closed; committed negative test missing |
| missing tracked file | `NON_ISSUE` |
| critical untracked file | `NON_ISSUE` |
| noncritical unexpected file | static code path is RED; committed negative test missing |
| linked worktree | `NON_ISSUE` |
| alternates file / explicit alternate env | `NON_ISSUE` for those exact mechanisms |
| foreign object-store indirection | `REAL_DEFECT` A6 |
| replace-object indirection | `REAL_DEFECT` A7 |
| index-write independence | no `git status`/cached-index authority found; metadata snapshot exists, but this does not cure A6/A7/A10 |
| allowed-extra traversal syntax | normalization rejects `..`; broader TOCTOU/path identity remains A10 |
| exact frozen candidate positive control | `TEST_DEFECT` A8 |

## 5. What remains target-host / activation-time only

These items were not and must not be claimed closed by this repository review:

- installation and immutable digest sealing of the reviewed authority consumer on the target host;
- actual external registry path, receipt root, permissions, ownership, filesystem identity and persistence;
- any persistent active-run marker / resume semantics required by the earlier prestage design;
- target-host evidence-root and journald retention / reboot visibility / disk-inode headroom (F6);
- actual M4 execution against the materialized target release;
- proof that the release is immutable/race-free for the whole verification-to-mutation interval;
- activation-critical host/boot/mount/evidence-root bindings;
- Blue sealing of a concrete activation;
- Gate B execution, Gate B PASS, Gate C or t0.

## 6. Required disposition before re-review

Builder must repair at minimum:

1. full-write + durable directory semantics for registry and receipt state;
2. freshness time acquisition under the authority lock and future-issued chronology enforcement;
3. evidence binding equality to the consumed activation digest with strict ordinal/schema typing;
4. rejection of foreign object-store symlink/indirection;
5. rejection/disablement of Git replace-object semantics;
6. exact-candidate positive control and negative tests covering the repaired discriminants.

After a new exact Builder delivery and exact-head green CI, Astra should re-run the targeted independent review. Blue must not seal this delivery as Gate-B mutation authority in its current state.

`RETURN_CONTROL_TO = BLUE`
