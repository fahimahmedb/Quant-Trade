# ASTRA — GATE-B F11 LOCK IDENTITY TARGETED RECHECK — 2026-09-21

## Identity

```text
AUDITED_INTEGRATION_BRANCH = blue/gate-b-f11-final-integration-2026-09-21
AUDITED_INTEGRATION_SHA = 4f26c1f015efb8c3530aeba8b3f87a81b0361a3f
AUDITED_INTEGRATION_EXACT_HEAD_CI = 35619545254 = COMPLETED/SUCCESS

BUILDER_FINAL_SHA = e600295b2aa7056e8176e0286f9d67f5c65b1c11
BUILDER_FINAL_EXACT_HEAD_CI = 35617257622 = COMPLETED/SUCCESS

ASTRA_START_HEAD = 1340c1e8eefdbbcd11aece6506040336f448d38d
ASTRA_FINAL_HEAD = (this commit)
ASTRA_EXACT_HEAD_CI = not separately re-verified this pass (launch-gate verification declared already done by dispatcher)
```

Scope followed: targeted F11 recheck only, per
`handoff/ASTRA_GATE_B_F11_LOCK_IDENTITY_RECHECK_MISSION_2026-09-21.md`. No redesign, no
target-host action, no edits to `scripts/quant_gate_b_runctl.py` or any test file.

## Method

Independent reproduction only — Builder's own tests in
`tests/test_gate_b_lock_path_identity_repair.py` and
`tests/test_gate_b_run_authority_m1_m3_repair.py` were read for reference but not relied
upon as proof. Real disposable directories under the session scratchpad and real
`multiprocessing` (fork) OS processes drove the actual `Registry` class in
`scripts/quant_gate_b_runctl.py`, calling the real `_locked()` critical section and the
real `reserve()` mutation entrypoint. Driver scripts:
`f11_driver.py` (F11-P1/P2/P3) and `f11_r1_r2_r5.py` (F11-R1/R2/R5), both in the session
scratchpad (not committed — throwaway).

## F11 matrix — real reproduction evidence

**F11-R1** (public `.lock` pathname replacement while A active): B's process blocked on
the outer parent-directory `flock` for the full duration A held it
(`B_BLOCKED_WHILE_A_ACTIVE = True`), then on unblock was rejected:
`AuthorityError('lock pathname identity changed')`. B never entered a concurrent mutation
domain.

**F11-R2** (coordinated `.lock` + authority-anchor replacement while A active): same
blocking behavior, then rejected: `AuthorityError('lock authority anchor malformed')`. No
concurrent entry.

**F11-P1** (whole immediate parent directory replacement): with A confirmed still alive
(`A_ALIVE_WHEN_B_FINISHED = True`), B's `reserve()` call against fresh P2 raised
`AuthorityError('registry parent identity changed')` — rejected before any mutation, while
A was independently still provably active, not merely "eventually erred". A itself,
because its own path identity became ambiguous mid-critical-section from B's parent-swap,
surfaced its own post-mutation revalidation as failure (`lock parent identity changed`)
even though its fd-anchored write had already landed — this is the documented fail-closed
behavior in the code comments ("no public success can escape an ambiguous lock identity"),
not a defect.

**F11-P2** (no partial mutation in rejected P2): `P2_LISTING = []` — the fresh replacement
parent directory contains zero registry/lock/anchor/reservation/evidence artifacts after
B's rejected attempt.

**F11-P3** (fail-closed persistence + recovery continuity): repeated independent attempt
against persisting P2 deterministically rejected again
(`AuthorityError('registry parent identity changed')`). After simulated operator repair
(P2 removed, original P1 restored), a fresh `Registry` against the same configured path
loaded exactly 1 event — A's original `REVOCATION_EPOCH_SET` — confirming continuation of
the original history, not silent bootstrap of a second one.

**F11-R5** (no-attack positive control): 5 independent real processes calling `reserve()`
concurrently against one registry all succeeded (`OK` x5); final registry holds exactly 5
events. No deadlock; normal operation is preserved by the fix.

## Section 3 — grandparent-anchor design review

Read the actual implementation (`_open_lock_parent`, `_validate_lock_parent`,
`_registry_parent_authority_marker_name`, `_read_registry_parent_authority`,
`_bootstrap_registry_parent_authority`, `_validate_registry_parent_authority`,
`_locked`, lines ~568-742).

- A marker named `.{parent_name}.parent-authority` is stored in the *grandparent*
  directory (opened by real fd, `O_DIRECTORY`), hard-link/atomic-rename bootstrapped and
  then read back before a fresh parent (P2) can be trusted (`_validate_registry_parent_authority`).
  A pre-existing parent with no marker is rejected fail-closed
  (`"pre-existing registry parent has no authority marker"`), and a parent whose marker
  identity mismatches the currently open parent's `(dev, ino)` is rejected
  (`"registry parent identity changed"`). This matches the required property: marker
  identity is checked before replacement can bootstrap authority, and both marker
  creation and revalidation are fail-closed (any `OSError`/mismatch raises
  `AuthorityError`, no silent fallthrough observed or reproduced).
- All name lookups for the remainder of the critical section (registry read/append,
  authority re-checks) are performed relative to the held parent-directory `pfd`
  (`_load_registry_at`, `_append` both take `dir_fd=pfd`), so a whole-parent replacement
  mid-critical-section cannot redirect A's own write into the replacement directory — the
  P1 reproduction confirms A's actual bytes land under the original inode (`P3` recovery
  shows A's event, not B's, survives).
- No competing marker was observed to establish a second history in the immediate-parent
  attack model tested (F11-P1/P2/P3 above).
- Residual risk beyond the immediate parent (grandparent/ancestor ownership, mount/namespace
  control) is out of repository scope and is correctly classified `TARGET_HOST_ONLY`, not a
  repository blocker. The mission explicitly does not require infinite recursive ancestor
  locking, and none is claimed by the implementation's own comments.

## A1-A10 non-regression

- **A1-A5** (targeted smoke/negative controls): covered by the full suite run below,
  including the new F11 test files' 30+ cases (lock/anchor tamper, malformed anchors,
  parent replacement, recovery) which all passed; no separate reduced-scope run needed
  since full suite completed quickly (51s).
- **A6-A8**: `git diff 644da76e..4f26c1f0 -- scripts/verify_gate_b_deployed_bytes.py` is
  empty (byte-identical). Prior proof preserved, not redone.
- **A9-A10**: materially rechecked via the real cross-process F11-R1/R2/R5 reproductions
  above (these are exactly the cross-process/path-race authority properties A9-A10 cover).

## Full suite

```
PYTHONPATH=src python3 -m unittest discover -s tests -v
Ran 460 tests in 50.985s
OK
```

No test skipped, weakened, or xfail'd.

## Section 5 — bounded adjacent-defect search

- **Marker/bootstrap race**: bootstrap uses `tempfile.mkstemp` + `os.link` into the
  grandparent fd, then fsync of the grandparent dir; a concurrent bootstrapper would hit
  `FileExistsError` on `os.link` (already covered by directory-level `flock` serialization
  on `pfd`, since bootstrap only happens inside `_open_lock_parent` before the parent flock
  is released to a second same-parent contender — cross-parent races are exactly the
  F11-P1 scenario, reproduced above as rejected). Classified `NON_ISSUE` given reproduction.
- **Stale marker adoption**: `_read_registry_parent_authority` requires exact
  `(dev, ino)` match to the currently open parent; a stale marker for a removed parent
  cannot be adopted by a new parent with different inode. `NON_ISSUE`.
- **dir_fd/path mismatch**: all critical-section I/O uses `dir_fd=pfd`/`dir_fd=gpfd`
  consistently in the read code path; reproduction confirms A's write lands under the
  original inode even when the live pathname is moved. `NON_ISSUE`.
- **Write escaping to P2**: directly tested by F11-P1/P2; P2 received zero artifacts.
  `NON_ISSUE`.
- **Crash during bootstrap**: not independently reproduced (would need a real
  process-kill mid-`os.link`); code uses tempfile+link+fsync pattern which is the standard
  crash-safe idiom, but this specific fault injection was not executed this pass.
  Classified `MISSING_PROOF` (not a blocker — no evidence of a defect, just no direct
  fault-injection run in this targeted pass).
- **Lock-order deadlock**: F11-R5 positive control (5 concurrent real processes, all
  succeeded, no hang) is direct evidence against a lock-order deadlock. `NON_ISSUE`.
- **Recovery creating two histories**: directly tested by F11-P3; recovery continued the
  single original history. `NON_ISSUE`.

## Result matrix

```text
F11_PUBLIC_LOCK = PASS
F11_LOCK_PLUS_ANCHOR = PASS
F11_PARENT_REPLACEMENT = PASS
F11_PARENT_NO_MUTATION = PASS
F11_PARENT_RECOVERY = PASS
F11_NORMAL_SERIALIZATION = PASS

A1_A5_NON_REGRESSION = PASS
A6_A8_PRIOR_PROOF_PRESERVED = PASS (verify_gate_b_deployed_bytes.py byte-identical)
A9_A10_NON_REGRESSION = PASS

ADJACENT_FINDING = MISSING_PROOF (crash-during-bootstrap fault injection not independently
executed this pass; no evidence of an actual defect, all other adjacent vectors NON_ISSUE
or reproduced PASS)
ASTRA_GATE_B_F11_RECHECK = PASS_REPOSITORY_EVIDENCE
```

## Safety

```text
TARGET_HOST_TOUCHED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```

Return control to Blue.
