# TARGET-HOST V4 RELEASE MATERIALIZATION — CANDIDATE — 2026-09-21

## Status

`RELEASE_MATERIALIZATION = PREPARED_CANDIDATE / NOT_AUTHORIZED`

`GATE_B_MUTATION_AUTHORIZED = FALSE`

This document closes an operational specification gap: the deployment contract
defines the accepted immutable release topology but not the exact evidence
requirements for creating the SHA-addressed release.

It does not authorize target-host mutation by itself.

## 1. Exact release identity

Target release:

`/opt/quant-releases/4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072/`

Expected commit:

`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Expected Git tree:

`4d15ef6f471213ee6ab56337b555d2906ef9bf16`

Expected verified input-tree digest from exact-head CI:

`sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2`

CI artifact:
- run `35536353538`;
- artifact id `10612758620`;
- archive digest
  `sha256:06c690203d589e389847cd345809480da2b99254fe7fd7f38b82c6bf5d54659a`.

## 2. Source authority

Materialization must start from an exact Git object whose SHA and tree are
independently verified.

A moving branch name is not sufficient.

The admin/development clone may be used as an object source only if the resulting
release is self-contained and does not depend on that clone afterward.

Forbidden final release forms:
- linked worktree;
- `.git` file pointing elsewhere;
- object alternates into the development clone;
- shared mutable working tree;
- source archive without Git metadata;
- moving symlink used as the service root.

## 3. Staging before final SHA-addressed path

Materialize into a fresh staging location first.

Do not partially populate the final SHA-addressed release directory.

Before promotion from staging, require:
- detached HEAD;
- exact expected SHA;
- exact expected Git tree;
- clean status;
- self-contained `.git` directory;
- no object alternates;
- no linked-worktree dependency;
- required repository paths present;
- repository unit present at expected path.

If the final SHA-addressed directory already exists:
- do not overwrite it in place;
- verify it completely;
- if any mismatch exists, classify integrity failure and STOP.

A path named with the expected SHA is not proof that its contents match that SHA.

## 4. Git-tree versus verified-input-tree binding

The exact CI verification artifact binds the repository verification subset to:

`sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2`.

The target release must independently prove the full Git tree equals:

`4d15ef6f471213ee6ab56337b555d2906ef9bf16`.

Given a clean exact Git tree, the source bytes covered by the CI input-tree
digest are transitively fixed by that exact tree.

Do not copy the stale committed
`handoff/SEC_FORM4_P0_VERIFICATION.json`
as if it were the exact-head CI artifact.

## 5. Immutability boundary

After promotion to the final SHA-addressed release path:

- no development task may edit the backing tree;
- no deployment task may patch it in place;
- no Builder/Codex task may use it as a worktree;
- service view outside `var` must be read-only;
- backing release tree must itself be protected against ordinary development
  mutation, not merely hidden behind a read-only bind.

Any required code change means a new candidate SHA and a new release path.

## 6. State separation

Release materialization must not:
- delete P0 state;
- reset P0 journals;
- create a fresh qualifying state reservoir silently;
- consume a qualifying deployment authority;
- start the qualifying service.

Code release and durable state are separate authorities.

## 7. Service-view installation

Only after the release passes all identity checks may the fixed service view
`/opt/quant` be established according to the deployment contract.

The service view must not be a moving symlink.

Before any service start, separately establish/verify:
- code view;
- writable `/opt/quant/var` view;
- durable `/var/lib/quant-p0` identity;
- mount ordering;
- fail-closed missing-state behavior.

These are Gate-B evidence, not release-name assumptions.

## 8. Required materialization artifact

Create a restricted hash-addressable artifact conceptually named:

`TARGET_HOST_V4_RELEASE_MATERIALIZATION_<UTC>.json`

Bind at minimum:
- Gate-B run ID if activation has occurred;
- activation digest;
- target host opaque ID;
- source object authority/reference;
- expected and observed SHA;
- expected and observed Git tree;
- clean-status verdict;
- self-contained Git metadata verdict;
- alternates/worktree verdict;
- final release path;
- final release filesystem identity;
- ownership/permission evidence;
- service-view relationship if established;
- overall PASS/FAIL/UNKNOWN;
- explicit `service_started: false`;
- explicit `t0_declared: false`.

## 9. Failure semantics

Any identity mismatch, dirty tree, foreign alternate, linked-worktree dependency,
or in-place overwrite attempt is:

`RELEASE_MATERIALIZATION = FAIL`

and blocks Gate B progression.

Do not “fix” the same evidence artifact after failure.

Preserve the failed attempt and return to Blue.

## 10. Activation boundary

Actual materialization requires a sealed Blue Gate-B activation artifact with:

`ALLOW_RELEASE_MATERIALIZATION = TRUE`.

Absent that explicit permission:

`RELEASE_MATERIALIZATION = NOT_AUTHORIZED`.
