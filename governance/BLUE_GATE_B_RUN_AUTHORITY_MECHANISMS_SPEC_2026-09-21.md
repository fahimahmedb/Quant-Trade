# BLUE — GATE B RUN AUTHORITY MECHANISMS SPEC — 2026-09-21

## 0. Scope

This spec closes repository/tooling mechanisms identified by:
`handoff/BUILDER_GATE_B_RUN_AUTHORITY_RETENTION_PRESTAGE_2026-09-21.md`.

It does NOT modify frozen V4 production logic.

Target findings:
- F2 run identity / anti-laundering;
- F3 activation consumption / revocation mechanics;
- F7 index-independent deployed-byte verification.

F6 target-host retention observations remain host-only.

## 1. Required mechanisms

### M1 — append-only Gate-B run registry

Provide one minimal repository tool that can:
- reserve a globally unique run ID;
- allocate monotonic attempt number for the same candidate lineage;
- persist reservation/activation/consumption/terminal events append-only;
- use an exclusive lock;
- fsync committed state;
- fail closed on malformed/truncated history;
- reject duplicate run IDs;
- reject a second nonterminal mutating run;
- preserve FAILED_TERMINAL history;
- never relabel prior artifacts as a new run.

Registry storage path is runtime-configurable and MUST be outside source checkout.
The concrete path is later sealed by Blue.

### M2 — authority consumer

Provide one minimal tool/command that:
- receives sealed activation bytes/reference;
- verifies activation digest;
- verifies run reservation exists and is unconsumed;
- verifies candidate triple;
- verifies current revocation epoch/reference;
- atomically consumes the run before the first mutating Gate-B command;
- emits a hash-addressable consumption receipt;
- fails closed if registry/activation/receipt state is ambiguous.

It MUST NOT itself perform target-host mutation beyond its own authority-registry
state transition.

### M3 — revocation/freshness

Provide:
- explicit revocation epoch/reference;
- activation issued-at / expires-at fields or equivalent finite freshness rule;
- consumer rejection on stale/revoked activation.

### M4 — deployed-byte verifier

Provide an index-independent verifier that:
- never relies on `git status` cleanliness;
- uses `GIT_OPTIONAL_LOCKS=0`;
- reads expected tree from Git objects without refreshing index;
- verifies every tracked regular file/symlink against the exact frozen tree;
- detects missing/extra tracked-path substitutions as applicable;
- reports untracked files in execution-critical paths separately;
- proves no alternates/linked-worktree dependency;
- emits canonical JSON + SHA-256;
- performs no writes in the target release.

Target release remains:
`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`.

## 2. Required discriminants

- duplicate run reservation = RED;
- concurrent nonterminal mutating run = RED;
- reuse after FAILED_TERMINAL = RED;
- consume without reservation = RED;
- consume wrong activation digest = RED;
- consume wrong candidate = RED;
- consume stale/revoked activation = RED;
- second consume same activation/run = RED;
- malformed/truncated registry = RED;
- deployed-byte mutation = RED;
- missing tracked file = RED;
- foreign Git alternate/worktree dependency = RED;
- exact frozen tree = GREEN.

Tests may use temporary directories only.

## 3. Boundaries

Do NOT:
- modify frozen V4 `src/`;
- touch target host;
- authorize Gate B;
- declare t0;
- implement F5 synthetic execution;
- invent actual evidence-root location.

Required Builder status:
`GATE_B_RUN_AUTHORITY_MECHANISMS = READY_FOR_INDEPENDENT_REVIEW`.

Independent review required before Blue may seal activation.
