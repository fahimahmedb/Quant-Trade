# BUILDER — GATE B F11 LOCK-PATH IDENTITY REPAIR — 2026-09-21

## 0. Delivery status

`GATE_B_LOCK_PATH_IDENTITY_REPAIR = READY_FOR_INDEPENDENT_REVIEW`

This is a bounded Builder repair of Astra finding F11 only.

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
13. stable real independent-process contention positive control.

At least the contention/replacement discriminants use independent OS processes and the real local `flock` primitive.

## 6. A1-A5 preservation

The F11 repair retains the previously repaired M1/M2/M3 semantics.

A2's directory-fsync injection test required a small test-only adjustment because F11 authority bootstrap adds an earlier durable directory-entry fsync. The test now permits that independent F11 durability point and injects failure at the intended registry-entry fsync point.

No A1-A5 authority invariant was intentionally weakened.

The full unit suite and SEC P0 lane suite passed at exact implementation HEAD `ed51cc4251f556482eca18e396cc1c0d932879fb`.

## 7. Changed paths versus audited baseline

Implementation/test delta at pre-handoff implementation HEAD:

- `scripts/quant_gate_b_runctl.py`
- `tests/test_gate_b_lock_path_identity_repair.py`
- `tests/test_gate_b_run_authority_m1_m3_repair.py`
- `STATE.md` — mechanical proof inventory only

No change to:

- `scripts/verify_gate_b_deployed_bytes.py`
- frozen V4 `src/`
- target-host configuration
- systemd
- mounts
- firewall/network state

Proof inventory after the final added F11 tests:

`457 unit tests discovered`

## 8. Exact-head implementation CI evidence

Pre-handoff implementation HEAD:

`ed51cc4251f556482eca18e396cc1c0d932879fb`

Exact-head GitHub Actions run:

`35608538693 = COMPLETED / SUCCESS`

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

Because this handoff itself changes the branch HEAD, the final branch HEAD must receive its own exact-head CI verification before the delivery is handed to Astra.

## 9. Adjacent findings and residual boundary

The coordinated replacement of both the public lock and authority anchor was treated as inseparable from F11 and repaired in this lane.

No new unrelated repository defect is declared by the Builder.

Residual boundary:

`TARGET_HOST_ONLY: stability/ownership/mount identity of the configured external registry parent directory and its ancestor namespace.`

Repository code validates the opened parent directory identity and fails public success on observed substitution. It cannot prove that a same-privilege external actor or mount-namespace authority is unable to replace the configured parent namespace itself throughout the real target-host authority window. That property must be established by target-host ownership/permissions/mount evidence.

This residual does not substitute for F11: the repository-local lock-file replacement and coordinated lock+anchor replacement paths are closed within a stable configured registry parent.

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

After this handoff commit, re-run exact-head CI on the resulting branch HEAD.

If that exact-head run is `COMPLETED / SUCCESS`, the Builder disposition is:

`GATE_B_LOCK_PATH_IDENTITY_REPAIR = READY_FOR_INDEPENDENT_REVIEW`

Return control to Blue/Astra for independent recheck of F11 and adjacent lock-domain assumptions.
