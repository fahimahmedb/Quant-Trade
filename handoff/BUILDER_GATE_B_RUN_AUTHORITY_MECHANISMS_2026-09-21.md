# BUILDER — GATE B RUN AUTHORITY MECHANISMS — 2026-09-21

## 0. Final status

`GATE_B_RUN_AUTHORITY_MECHANISMS = READY_FOR_INDEPENDENT_REVIEW`

Mission branch:

`builder/gate-b-run-authority-mechanisms-2026-09-21`

Verified mission authority at implementation start:

`cf420ee05542e22917b23d712a0de304dd4b4969`

The branch resolved exactly to that commit before implementation. This delivery changes
repository tooling/tests/handoff only.

Safety boundary preserved:

```text
FROZEN_V4_SRC_MODIFIED = FALSE
TARGET_HOST_TOUCHED = FALSE
F5_WORK_PERFORMED = FALSE
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
GATE_B_MUTATION_AUTHORIZED = FALSE
RETURN_CONTROL_TO = BLUE
```

## 1. Delivered mechanisms

### M1 — append-only Gate-B run registry

Implemented:

`scripts/quant_gate_b_runctl.py`

The registry is canonical JSONL and is configured by constructing `Registry(registry_path, source_checkout)`.
The registry path is rejected if it resolves inside the source checkout; Blue must bind the
actual external registry and receipt roots before target-host use.

Durability / anti-ambiguity properties:

- exclusive `flock()` on a non-symlink regular lock file;
- registry append uses `O_APPEND` and `O_NOFOLLOW` where available;
- each append is `fsync()`'d and the containing directory is `fsync()`'d;
- every event has a global previous-registry digest and SHA-256 event digest;
- every run-scoped event also has a per-run previous-event digest;
- a non-empty registry must end in a newline;
- every line must be canonical JSON;
- malformed JSON, unknown fields, broken hash chains, truncated final lines,
  invalid event transitions and non-monotonic attempts fail closed.

Run identity rules:

- the public `Registry.reserve(...)` API generates `gate-b-<RFC4122 UUID-v4>` internally by default;
- callers cannot supply a literal run ID; the optional factory exists only as a deterministic test seam;
- generated IDs are checked against the full authoritative registry;
- attempt number is `1 + max(prior reservation attempt)` for the exact lineage
  `(candidate_sha, git_tree, verified_input_tree_digest, target_host_opaque_id)`;
- attempts are never recycled;
- a second nonterminal run for the same target-host opaque ID is rejected;
- a terminal run ID is never reopened;
- `FAILED_TERMINAL` is an immutable append-only terminal event;
- a retry therefore requires a different run ID and receives the next attempt.

The registry also supports `EVIDENCE_BOUND` events. The same raw artifact digest cannot
be bound to a different run, and an artifact ordinal cannot be reused within a run.
This prevents changing only top-level run metadata from laundering previously owned
evidence into a new run.

### M2 — authority consumer

The same tool implements exact canonical activation parsing plus:

- exact activation byte SHA-256 verification;
- one reservation required for the run;
- reservation digest verification;
- run ID / attempt / candidate SHA / Git tree / verified-input-tree digest /
  target-host opaque ID equality against the reservation;
- sealed activation digest equality against the registry;
- terminal-run rejection;
- first-consumption-only semantics under the same exclusive registry lock;
- durable `ACTIVATION_CONSUMED` append before returning authority;
- hash-addressed consumption receipt.

Receipt bytes are canonical JSON with a trailing newline. The receipt digest is over
those exact bytes and the filename is `<sha256-hex>.json`. The consume event binds both
the receipt digest and reference.

If receipt materialization fails after the registry consumption append, the run remains
consumed and therefore fails closed: the activation cannot be reused to obtain a second
successful consumption.

The consumer performs no Gate-B target mutation beyond its own authority-registry /
receipt state.

Activation schema v1 is intentionally exact and rejects unknown/missing fields:

```text
schema
activation_id
run_id
attempt_number
reservation_digest
candidate_sha
git_tree
verified_input_tree_digest
target_host_opaque_id
issued_at_utc
not_before_utc
expires_at_utc
revocation_epoch
revocation_reference
gate_b_mutation_authorized
```

This mechanism does not claim that the separate full Blue Gate-B activation pack has
been sealed; it supplies the M2/M3 consumption primitive that Blue can independently
review before any activation decision.

### M3 — revocation / freshness

Registry events provide:

- monotonic `REVOCATION_EPOCH_SET`;
- explicit `revocation_reference`;
- explicit `ACTIVATION_REVOKED`;
- activation `issued_at_utc`;
- activation `not_before_utc`;
- finite activation `expires_at_utc`.

Seal/consume requires the activation epoch/reference to equal the current registry
authority. Consumption rejects:

- future `issued_at`;
- not-yet-valid activation;
- expired activation;
- epoch/reference drift;
- explicitly revoked activation ID;
- already-consumed activation;
- any terminal run.

Changing the revocation epoch invalidates every activation sealed under the previous
epoch.

### M4 — index-independent deployed-byte verifier

Implemented:

`scripts/verify_gate_b_deployed_bytes.py`

Authoritative byte proof:

- forces `GIT_OPTIONAL_LOCKS=0` for every Git command;
- never uses `git status`, `git diff`, `git ls-files`, or cached-index cleanliness;
- verifies exact `HEAD` and `HEAD^{tree}`;
- obtains expected entries from
  `git ls-tree -r -z --full-tree <EXPECTED_TREE>`;
- walks deployed filesystem bytes independently of the index;
- hashes regular-file bytes with the Git blob-object algorithm without writing objects;
- verifies executable mode semantics;
- hashes symlink target bytes without dereferencing;
- rejects unsupported object types/modes;
- detects missing tracked files;
- reports untracked execution-critical paths separately from other untracked paths;
- rejects all unexpected extras unless an explicit allowed extra prefix is supplied;
- rejects `.git` symlinks and linked worktree `.git` files;
- rejects a common Git dir different from the release-local `.git`;
- rejects nonlocal Git object directories;
- rejects non-empty `.git/objects/info/alternates`;
- rejects `GIT_OBJECT_DIRECTORY` / `GIT_ALTERNATE_OBJECT_DIRECTORIES` overrides;
- snapshots index bytes/mtime and Git lock paths before/after verification and marks
  any metadata change RED;
- emits canonical JSON plus a SHA-256 over the canonical report.

No target release write primitive exists in this verifier.

## 2. Reproducible discriminants

Targeted suite:

```bash
python3 -m unittest -v tests/test_gate_b_run_authority.py
```

Observed during Builder implementation:

`21 tests / PASS`

Required Blue discriminants:

| Required discriminant | Test / disposition |
| --- | --- |
| duplicate run reservation = RED | `test_duplicate_run_reservation_red_and_attempt_monotonic_after_terminal` |
| concurrent nonterminal mutating run = RED | `test_concurrent_nonterminal_run_red` |
| reuse after FAILED_TERMINAL = RED | `test_failed_terminal_is_preserved_and_old_run_cannot_be_reused` |
| consume without reservation = RED | `test_consume_without_reservation_red` |
| consume wrong activation digest = RED | `test_wrong_activation_digest_red` |
| consume wrong candidate = RED | `test_wrong_candidate_red_at_consumer` |
| consume stale activation = RED | `test_expired_activation_red` |
| consume revoked activation = RED | `test_revocation_epoch_change_red`, `test_explicit_activation_revocation_red` |
| second consume same activation/run = RED | `test_second_consume_red_and_receipt_is_hash_addressed` |
| malformed/truncated registry = RED | `test_malformed_and_truncated_registry_red` |
| deployed-byte mutation = RED | `test_deployed_byte_mutation_red_even_without_git_status` |
| missing tracked file = RED | `test_missing_tracked_file_red` |
| foreign Git alternate dependency = RED | `test_foreign_git_alternate_red` |
| linked-worktree dependency = RED | `test_linked_worktree_dependency_red` |
| exact frozen-tree algorithm = GREEN | `test_exact_frozen_tree_green` |

Additional protections exercised:

- registry storage inside checkout = RED;
- registry digest-chain tampering = RED;
- cross-run raw evidence relabeling = RED;
- untracked execution-critical file = RED;
- explicit allowed runtime-prefix exclusion = GREEN.

Tests use temporary directories only. The deployed-byte tests construct disposable Git
repositories and linked worktrees under those temporary directories; they do not touch
the frozen V4 release or target host.

## 3. Repository-only interfaces

M1-M3 are exposed as the importable `Registry` API in
`scripts/quant_gate_b_runctl.py` (`reserve`, `set_revocation_epoch`, `revoke_activation`,
`seal_activation`, `consume_activation`, `bind_evidence`, and `terminal`). The targeted
unit suite exercises those exact methods. This Builder delivery intentionally does not
install the module on a target host and does not invent the final `/usr/local/sbin/...`
operator wrapper or sealed runtime storage paths; Blue may package the reviewed module
only after independent review and activation binding.

M4 is also directly executable for repository/offline verification:

```bash
python3 scripts/verify_gate_b_deployed_bytes.py \
  --release /opt/quant-releases/4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072 \
  --expected-sha 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072 \
  --expected-tree 4d15ef6f471213ee6ab56337b555d2906ef9bf16
```

That M4 command was **not** executed against the target host by Builder.

## 4. Files changed

```text
scripts/quant_gate_b_runctl.py
scripts/verify_gate_b_deployed_bytes.py
tests/test_gate_b_run_authority.py
handoff/BUILDER_GATE_B_RUN_AUTHORITY_MECHANISMS_2026-09-21.md
```

No `src/` file is changed.

## 5. What remains outside this mission

This delivery deliberately does not claim or perform:

- Blue selection of the actual registry/evidence-root/receipt storage locations;
- Blue sealing of one concrete Gate-B activation;
- target-host evidence-root / journald / headroom observations (F6);
- V3 -> V4 transition execution;
- F5 synthetic lifecycle/sanitization;
- target-host deployed-byte execution against the real frozen release;
- Gate B PASS;
- t0 declaration.

Independent Astra review is required before Blue may use these mechanisms as sealed
activation authority.

## 6. Final disposition

```text
GATE_B_RUN_AUTHORITY_MECHANISMS = READY_FOR_INDEPENDENT_REVIEW
TARGET_HOST_MUTATION_PERFORMED = FALSE
FROZEN_V4_PRODUCTION_LOGIC_MODIFIED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
RETURN_CONTROL_TO = BLUE
```
