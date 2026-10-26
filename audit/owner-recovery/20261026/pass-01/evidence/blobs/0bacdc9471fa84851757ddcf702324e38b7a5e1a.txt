# BUILDER — GATE B F11 LOCK-PATH IDENTITY REPAIR — 2026-09-21

## 0. Delivery status

`GATE_B_LOCK_PATH_IDENTITY_REPAIR = READY_FOR_INDEPENDENT_REVIEW`

This is a bounded Builder repair of Astra finding F11, now including closure
of Blue's follow-on whole-parent-directory identity challenge
(`governance/BLUE_GATE_B_F11_BRANCH_RECONCILIATION_PARENT_PATH_CHALLENGE_2026-09-21.md`,
F11-P1/P2/P3). No further scope was added.

`PASS_REPOSITORY_EVIDENCE` is not declared here. Independent closure of F11
and A1-A10 non-regression remains Astra's authority; Blue reception must
still gate Astra dispatch per
`handoff/BLUE_F11_BUILDER_RECEPTION_PENDING_PARENT_PATH_2026-09-21.md`.

Safety state:

```text
TARGET_HOST_TOUCHED = FALSE
FROZEN_V4_SRC_MODIFIED = FALSE
M4_VERIFIER_MODIFIED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
```

No claim of `PASS_REPOSITORY_EVIDENCE`, Gate B PASS, production readiness, or t0 is made here. Independent closure remains Astra's authority.

## 1. Branch and authority

Builder branch:

`builder/gate-b-lock-path-identity-repair-2026-09-21`

Audited repaired baseline:

`644da76eb0227be275b8e3448118dac0cc7096ca`

Astra blocker branch / final HEAD:

`astra/gate-b-run-authority-mechanisms-recheck-2026-09-21@41c3f291f46b7b5849bdb702c09ccefbeecde691`

Astra blocker:

`ASTRA_GATE_B_RUN_AUTHORITY_REVIEW = BLOCKED_REAL_DEFECT_LOCK_PATH_IDENTITY`

The Builder branch descends directly from the audited baseline and contains only the bounded F11 implementation/tests plus mechanical proof-inventory refresh and this handoff.

## 2. F11 reproduced defect and invariant

Astra independently reproduced the original failure by holding the configured public lock inode in process A, unlinking/replacing the lock pathname, then invoking production `Registry._locked()` from process B. B acquired a different inode immediately while A still held the original inode.

The required invariant is:

> Registry mutations must serialize through one stable lock authority. Replacing the public lock pathname must not create a second valid mutation domain while an existing mutation holder is active. Ambiguous identity fails closed.

The original defect was not a symlink-following bug. It was an object-identity bug: `flock` attaches to the opened file object, so replacing a pathname can create a fresh independently lockable inode.

## 3. Repair design

Primary implementation:

`scripts/quant_gate_b_runctl.py :: Registry._locked()`

The repair has two nested authority layers.

### 3.1 Stable inode authority for the public lock

A fresh registry creates:

- the configured public lock pathname; and
- a deterministic hard-link authority anchor named from the lock inode `st_dev/st_ino`.

The implementation validates:

- regular-file type;
- no symlink substitution;
- FD identity;
- public pathname identity;
- authority-anchor identity;
- expected `(st_dev, st_ino)`;
- hard-link count.

A pre-existing unanchored lock/state is not silently adopted. Ambiguity fails closed.

The authority identity is revalidated before flock acquisition, after acquisition, and before public success leaves the mutation context.

### 3.2 Parent-directory serialization

The first hard-link repair still admitted a stronger coordinated adversarial case: while holder A remained in the mutation window, an attacker could replace both the public lock pathname and its authority anchor with a fresh internally consistent pair. A second process could then otherwise form a new valid inode lock domain.

The final repair therefore opens the real parent directory with no-follow/directory semantics, records its `(st_dev, st_ino)`, and takes an exclusive `flock` on that directory FD for the entire critical section.

The parent-directory lock is acquired before resolving/validating the lock authority pair and remains held until after final lock-authority and parent-identity revalidation.

This makes the parent directory inode the outer serialization domain and the lock hardlink pair the inner object-identity authority.

Within one stable configured registry parent directory, replacing the public lock, replacing the anchor, or replacing both names cannot create a concurrently executable production mutation domain.

## 3.3 Whole-parent-directory replacement closure (F11-P1/P2/P3)

Blue's static review identified a remaining gap: the parent-directory `flock`
above serializes on whatever inode the configured parent *pathname*
currently resolves to. An adversary who renames the whole parent directory
away and creates a fresh empty directory at the original pathname while a
holder (A) remains active inside the original directory could previously let
a second process (B) resolve the replacement pathname, treat it as a
legitimately fresh registry, and bootstrap an independent mutation domain
concurrently with A -- reproduced as RED against the pre-fix implementation
(`B_MUTATED`).

Two changes close this:

1. **All name resolution inside the critical section is now anchored to the
   held parent-directory file descriptor**, not the live pathname. The lock
   file, its hard-link authority anchor, and the registry file itself are
   opened, read, and appended via `dir_fd`-relative operations against the
   `pfd` captured when the parent lock was acquired. A holder's own mutation
   can therefore never be silently redirected into a replacement directory
   swapped in during its critical section.
2. **A grandparent-anchored parent-identity marker.** The first legitimate
   bootstrap of a configured registry parent directory records that
   directory's `(st_dev, st_ino)` in a marker file in the *grandparent*
   directory (stable in this attack model; only the immediate parent is
   replaced). Every subsequent `_locked()` call revalidates the current
   parent directory's identity against that marker before doing anything
   else. A replacement directory at the same pathname has a different
   identity and is rejected with `AuthorityError` before any lock authority
   or registry operation is attempted -- before entering a mutation critical
   section, satisfying F11-P2 with zero partial mutation.

Proven with real independent OS processes against disposable temporary
directories in `tests/test_gate_b_lock_path_identity_repair.py`
(`GateBF11ParentPathIdentityTests`):

- **F11-P1**: while process A remains inside the real `Registry._locked()`
  critical section under the original parent directory, the whole parent is
  renamed away and a fresh directory is created at the configured pathname;
  process B constructs the same logical `Registry` and invokes the actual
  production mutation entrypoint (`set_revocation_epoch`). B is rejected
  with `AuthorityError` while A is independently confirmed still active
  (`holder.poll() is None`) at the moment B concludes.
- **F11-P2**: the rejected replacement-parent contender leaves the
  replacement directory empty -- no registry file, no lock file, no
  authority anchor, no reservation, no event of any kind.
- **F11-P3**: while the replacement persists, repeated independent attempts
  deterministically fail closed (no second logical registry history is ever
  bootstrapped under the replacement directory). After operator repair
  (removing the replacement directory and restoring the original directory
  at the configured pathname), a subsequent attempt is rejected only because
  it duplicates the original epoch (non-monotonic) -- proof that recovery
  resumes the single original registry history under the original stable
  authority, not a fresh second one.

Confirmed RED on the pre-fix implementation (checked out at the prior
handoff HEAD `6ec12cd73de24b4a789d6abe9e292d8b616e3da1`) and GREEN after the
repair, for all three new tests.

## 4. Fail-closed behavior

If lock authority cannot be established or remains ambiguous, the implementation does not:

- append registry state;
- return reservation authority;
- return activation-consumption authority;
- bind evidence;
- silently adopt a replacement lock inode.

It raises `AuthorityError`.

Replacement detected after entering the context prevents public success from escaping the context.

## 5. Builder regression suite

Dedicated suite:

`tests/test_gate_b_lock_path_identity_repair.py`

Covered discriminants include:

1. exact Astra public-lock replacement attack;
2. replacement before acquisition;
3. replacement while a waiter is blocked;
4. replacement after acquisition before public success;
5. authority-anchor replacement;
6. coordinated public-lock + authority-anchor replacement while a live holder is inside the critical section;
7. repeated public-lock replacement;
8. public-lock symlink substitution;
9. public-lock directory substitution;
10. FIFO/special-path negative control where supported;
11. unanchored pre-existing lock;
12. fresh bootstrap of exactly one hard-link authority;
13. stable real independent-process contention positive control;
14. F11-P1 whole-parent-directory replacement while a live holder is inside the critical section, blocking a second process's concurrent mutation entry;
15. F11-P2 no mutation of any kind escapes the rejected replacement-parent contender;
16. F11-P3 persistent fail-closed while the replacement persists, then deterministic recovery under the single original stable authority after operator repair.

At least the contention/replacement discriminants use independent OS processes and the real local `flock` primitive.

## 6. A1-A5 preservation

The F11 repair retains the previously repaired M1/M2/M3 semantics.

A2's directory-fsync injection test required a small test-only adjustment because F11 authority bootstrap adds an earlier durable directory-entry fsync. The test now permits that independent F11 durability point and injects failure at the intended registry-entry fsync point.

No A1-A5 authority invariant was intentionally weakened.

The full unit suite and SEC P0 lane suite passed at exact implementation HEAD `ed51cc4251f556482eca18e396cc1c0d932879fb`.

## 7. Changed paths versus audited baseline

Implementation/test delta at the prior handoff HEAD (`ed51cc4251f556482eca18e396cc1c0d932879fb` through `6ec12cd73de24b4a789d6abe9e292d8b616e3da1`):

- `scripts/quant_gate_b_runctl.py`
- `tests/test_gate_b_lock_path_identity_repair.py`
- `tests/test_gate_b_run_authority_m1_m3_repair.py`
- `STATE.md` — mechanical proof inventory only

Additional delta for this parent-path closure (this handoff, on top of `6ec12cd73de24b4a789d6abe9e292d8b616e3da1`):

- `scripts/quant_gate_b_runctl.py` — `Registry` name resolution during the critical section is now `dir_fd`-anchored to the held parent-directory fd, and a grandparent-anchored registry-parent identity marker closes F11-P1/P2/P3 (section 3.3 above). No M1-M5/A1-A10 method signature exposed outside `Registry` changed; `_lock_authority_paths()` keeps its existing zero-argument external call form used by test tooling.
- `tests/test_gate_b_lock_path_identity_repair.py` — added `GateBF11ParentPathIdentityTests` (F11-P1/P2/P3, 3 new tests). All 13 pre-existing tests in this file pass unmodified.
- `STATE.md` — mechanical proof inventory refresh only (`python3 scripts/status_artifacts.py --write`).

No change to:

- `tests/test_gate_b_run_authority_m1_m3_repair.py` (beyond the already-audited prior adaptation) — the two A2 directory-fsync injection tests in this file pass unmodified against the new implementation;
- `scripts/verify_gate_b_deployed_bytes.py`
- frozen V4 `src/`
- target-host configuration
- systemd
- mounts
- firewall/network state

Proof inventory after the added F11-P1/P2/P3 tests:

`460 unit tests discovered`

## 8. Exact-head implementation CI evidence

Pre-handoff implementation HEAD:

`ed51cc4251f556482eca18e396cc1c0d932879fb`

Exact-head GitHub Actions run:

`35608538693 = COMPLETED / SUCCESS`

Prior final handoff HEAD (received but non-authorizing pending this closure):

`6ec12cd73de24b4a789d6abe9e292d8b616e3da1` — exact-head CI `35610033532 = COMPLETED / SUCCESS`.

Verified run head SHA:

`ed51cc4251f556482eca18e396cc1c0d932879fb`

Key successful stages:

- Status artifact freshness = SUCCESS
- Full unit suite = SUCCESS
- SEC P0 lane suite = SUCCESS
- V1 end-to-end regression = SUCCESS
- exact-head verification artifact generation = SUCCESS
- exact-head verification artifact upload = SUCCESS
- clean working tree = SUCCESS

Exact-head artifact:

`sec-p0-verification-ed51cc4251f556482eca18e396cc1c0d932879fb`

Artifact digest:

`sha256:34b73de5a93241250e467f836f4dceab3b58ddaaa4d98a054f585047ddc47da0`

### Final branch HEAD (this handoff)

`54a7dd6ebf8e81d6dec06bd82d150dd7faef44e4`

Exact-head GitHub Actions run:

`35615746802 = COMPLETED / SUCCESS`

Verified run head SHA: `54a7dd6ebf8e81d6dec06bd82d150dd7faef44e4`. All gate stages (status artifact freshness, full unit suite, SEC P0 lane suite, V1 end-to-end regression, exact-head verification artifact generation/upload, clean working tree) succeeded.

`54a7dd6ebf8e81d6dec06bd82d150dd7faef44e4` carries every code/test change for this closure; no further implementation or test delta is pending. This present commit (recording that CI result) is documentation-only and does not reopen F11-P1/P2/P3 or A1-A10.

## 9. Adjacent findings and residual boundary

The coordinated replacement of both the public lock and authority anchor was treated as inseparable from F11 and repaired in this lane. The whole-parent-directory replacement Blue identified (F11-P1/P2/P3) was likewise treated as inseparable from F11 and repaired in this handoff per section 3.3 above.

No new unrelated repository defect is declared by the Builder.

Residual boundary, narrowed by this handoff:

`TARGET_HOST_ONLY: stability/ownership/mount identity of the registry GRANDPARENT directory and its own ancestor namespace above that.`

The repository-local whole-parent-path discriminant Blue required (replacing the immediate configured registry parent directory while a holder is active) is now closed for any actor operating within a stable grandparent directory: the grandparent-anchored identity marker makes a replacement immediate-parent directory ambiguous and rejects it before mutation, as proven in section 3.3. What remains target-host-only is one level further up: whether a same-privilege external actor or mount-namespace authority could also replace the *grandparent* directory (or its own ancestors) itself throughout the real target-host authority window. That property must still be established by target-host ownership/permissions/mount evidence; the grandparent-level anchor file cannot defend against an adversary who controls the grandparent's own namespace.

This residual does not substitute for F11 or for the F11-P1/P2/P3 closure: the repository-local lock-file replacement, coordinated lock+anchor replacement, and whole-immediate-parent-directory replacement paths are all closed within a stable registry grandparent directory.

Other target-host-only properties remain unchanged, including:

- actual registry/receipt-root ownership and permissions;
- actual filesystem durability;
- actual host/boot/mount bindings;
- actual installed authority-consumer digest;
- M4 execution against the actual frozen target release;
- release immutability through the verification-to-first-mutation window;
- Blue sealing/consumption of a concrete activation;
- actual Gate-B execution/reception;
- Gate-B PASS;
- t0.

## 10. Final disposition

```text
F11_PARENT_PATH_IDENTITY_CHALLENGE = CLOSED (repository-local, within a stable grandparent directory)
F11_P1 = GREEN
F11_P2 = GREEN
F11_P3 = GREEN
IMPLEMENTATION_CHANGED = TRUE (scripts/quant_gate_b_runctl.py :: Registry)
A1_A10_NON_REGRESSION = GREEN (460 unit tests discovered; full suite + SEC P0 lane + V1 end-to-end regression all pass)
```

After this handoff commit, re-run exact-head CI on the resulting branch HEAD.

If that exact-head run is `COMPLETED / SUCCESS`, the Builder disposition remains only:

`GATE_B_LOCK_PATH_IDENTITY_REPAIR = READY_FOR_INDEPENDENT_REVIEW`

No `PASS_REPOSITORY_EVIDENCE`, Gate B PASS, production readiness, or t0 claim is made. Return control to Blue for reception, then to Astra for independent recheck of F11, the F11-P1/P2/P3 parent-path closure, and A1-A10 non-regression, per `handoff/BLUE_F11_BUILDER_RECEPTION_PENDING_PARENT_PATH_2026-09-21.md` section 8.
