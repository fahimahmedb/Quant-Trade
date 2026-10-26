# BLUE — GATE B F11 BRANCH RECONCILIATION + PARENT-PATH IDENTITY CHALLENGE — 2026-09-21

## 0. Purpose

This checkpoint resolves a live branch-authority collision discovered while Blue was receiving the in-progress F11 Builder work, and adds one bounded adversarial challenge before any Builder handoff may be accepted.

No Gate-B, target-host, t0, Product, or real-capital authority is created here.

## 1. Exact objects observed

Audited integrated implementation base:

`644da76eb0227be275b8e3448118dac0cc7096ca`

Final Astra blocker:

`astra/gate-b-run-authority-mechanisms-recheck-2026-09-21@41c3f291f46b7b5849bdb702c09ccefbeecde691`

`F11 = REAL_DEFECT / LOCK_PATH_IDENTITY`

Pre-existing Builder implementation branch discovered live:

`builder/gate-b-lock-path-identity-repair-2026-09-21@ed51cc4251f556482eca18e396cc1c0d932879fb`

This branch descends exactly from the audited integration object:

- base = `644da76eb0227be275b8e3448118dac0cc7096ca`;
- ahead = 9;
- behind = 0;
- merge base = exact audited integration object.

Its first F11 implementation commit is:

`b779da29f32cf8f387eb3909bf8d57a3cc000a23`

which predates Blue's later mission-only branch creation.

Later strengthening observed:

- `e39ce9f670995219743b724450e390d4d5dcc4af` — prior strengthened checkpoint;
- `fa886cfcf627a866a651e076bcb133649b3a16f6` — parent-directory serialization;
- `d4dee9b8fb66ecd5875c91efe144521126acdfa9` — coordinated public-lock + anchor replacement test;
- `ed51cc4251f556482eca18e396cc1c0d932879fb` — proof-inventory refresh.

Exact-head workflow currently associated with `ed51cc42...`:

`35608538693`

At this checkpoint it remains:

`IN_PROGRESS`

The workflow is bound to branch:

`builder/gate-b-lock-path-identity-repair-2026-09-21`

and exact SHA:

`ed51cc4251f556482eca18e396cc1c0d932879fb`.

The full unit-suite step is already `SUCCESS`, but the workflow has not yet completed and therefore is not final CI evidence.

## 2. Branch-authority reconciliation

Blue later created:

`builder/gate-b-f11-lock-identity-repair-2026-09-21@8a30bd385f6f6c04c085bb72cb0c853c5de3c3b8`

from the same audited base after checking only the recommended exact branch name.

That branch contains only Blue spec/mission material and no implementation.

This created an avoidable duplicate mission branch because the implementation branch already existed under the alternate name above.

Blue corrects this now.

### Active implementation authority

`ACTIVE_F11_BUILDER_BRANCH = builder/gate-b-lock-path-identity-repair-2026-09-21`

### Mission-only duplicate disposition

`builder/gate-b-f11-lock-identity-repair-2026-09-21@8a30bd385f6f6c04c085bb72cb0c853c5de3c3b8`

is now:

`SUPERSEDED_MISSION_ONLY / DO_NOT_IMPLEMENT / PRESERVE_UNTIL_F11_CLOSURE`

Do not delete it during the active proof cycle, but do not add implementation commits to it.

No second Builder repair lane is authorized.

## 3. Scope review of ed51cc42...

Observed implementation delta from the audited base is limited to:

- `scripts/quant_gate_b_runctl.py`;
- `tests/test_gate_b_lock_path_identity_repair.py`;
- `tests/test_gate_b_run_authority_m1_m3_repair.py`;
- `STATE.md`.

The modification to `tests/test_gate_b_run_authority_m1_m3_repair.py` at:

`d4b6aa6d4eb10dd3a86aa23c6b585fe2b2a1e307`

is a narrow test-only adaptation that preserves the A2 directory-fsync negative control after the new lock-authority bootstrap introduced an earlier independent directory fsync.

Blue accepts this exact test-only adaptation as a bounded regression-maintenance exception.

No broader edits to A1-A10 test semantics are authorized.

## 4. What ed51cc42 closes so far

The current implementation materially strengthens F11 handling:

1. a durable hard-link anchor binds the public lock pathname to a recorded inode identity;
2. public lock and anchor identity are revalidated before/after acquisition and before success;
3. a parent-directory fd is opened and validated;
4. an exclusive `flock` is held on that parent directory through the mutation window;
5. a coordinated replacement of `.lock + authority anchor` cannot create a concurrent second production caller while both callers use the current implementation;
6. repeated public lock replacement is tested fail-closed;
7. ordinary real-process stable contention remains serialized.

These are useful Builder results, but they are not yet independent closure.

## 5. New bounded Blue adversarial challenge

Blue static review identifies a remaining authority question that must be reproduced before final handoff:

`F11_PARENT_PATH_IDENTITY_CHALLENGE = OPEN`

The current outer serialization primitive is the inode of:

`self.lock.parent`

opened through a pathname.

If process A holds a `flock` on parent-directory inode P1, an external adversary may be able to:

1. rename/move the entire parent directory away from the configured pathname;
2. create a new directory P2 at the original pathname;
3. start process B after the replacement;
4. B opens and locks P2, not P1;
5. B may bootstrap or accept a fresh internally-consistent lock/anchor domain under P2 while A remains inside its critical section under P1.

If reproducible, this is the same exclusivity-domain split one level above the original lock pathname.

A's final parent-identity check would detect that its pathname changed, but that is insufficient if B can already enter concurrently before A exits.

This is an adversarial challenge, not yet an independent Astra classification.

## 6. Mandatory parent-path discriminant before Builder final handoff

Builder must add a deterministic disposable real-process test against the actual `Registry._locked()` implementation.

### F11-P1 — whole-parent replacement during live holder

Required sequence:

1. initialize a valid Registry authority in a temporary parent directory;
2. process A enters the actual `Registry._locked()` critical section and signals `ENTERED_A`;
3. while A is still inside:
   - rename/move the entire registry parent directory to another pathname;
   - create a new real directory at the original parent pathname;
4. process B constructs the same logical Registry path and calls the actual `Registry._locked()`;
5. while A is still active, B MUST NOT enter a second critical section.

Acceptable outcomes:

- B remains serialized until A leaves; or
- B fails closed before entering/mutating.

Unacceptable outcome:

- B enters under the replacement parent-directory inode while A remains inside the original parent-directory inode.

### F11-P2 — no mutation on rejected replacement-parent contender

If the chosen repair fails closed, prove B appends no registry event.

### F11-P3 — post-replacement ordinary recovery

After the adversarial condition is resolved according to the chosen design, demonstrate explicitly whether the Registry:
- recovers under a single stable authority; or
- remains intentionally fail-closed pending operator repair.

Do not silently bootstrap a second logical registry history.

## 7. Repair requirement if F11-P1 is RED

If `ed51cc42...` fails F11-P1, Builder must repair the exclusivity design before final handoff.

Required invariant remains:

> Every Registry mutation for one configured logical registry must share one stable kernel exclusivity domain, or fail closed before a second mutation domain can be entered.

Moving the mutable-path dependency from the lock file to one replaceable ancestor directory does not satisfy this invariant by itself.

The implementation mechanism remains Builder-owned.

Blue does not require one specific primitive, but the final proof must demonstrate that the outermost serialization identity used by production callers cannot itself be split by the tested pathname-replacement attack.

Do not use target-host permissions as the sole repository proof.

## 8. CI and handoff consequences

Even if:

`35608538693 = COMPLETED / SUCCESS`

later, it proves only exact `ed51cc42...`.

It is not sufficient for final Builder reception while `F11_PARENT_PATH_IDENTITY_CHALLENGE = OPEN`.

Any code/test commit added for F11-P1/P2/P3 moves the Builder HEAD and requires a new exact-head CI.

Final handoff remains required:

`handoff/BUILDER_GATE_B_F11_LOCK_IDENTITY_REPAIR_2026-09-21.md`

Builder final status may still be only:

`READY_FOR_INDEPENDENT_REVIEW`

or an explicit blocker.

## 9. Independent review remains later

Astra is NOT relaunched yet.

Required remaining sequence:

`Builder closes F11-P1/P2/P3 -> final Builder handoff -> exact-head CI SUCCESS -> Blue reception/integration -> fresh Astra F11 + A1-A10 non-regression recheck -> only then possible PASS_REPOSITORY_EVIDENCE`.

## 10. Safety

```text
F11_REPAIR_REQUIRED = TRUE
PASS_REPOSITORY_EVIDENCE = FALSE
TARGET_HOST_READY = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```
