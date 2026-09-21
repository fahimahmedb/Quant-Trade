# BLUE — GATE B F11 LOCK-IDENTITY REPAIR SPEC — 2026-09-21

## 0. Authority and exact repair object

Authority: BLUE / Mission Control.

This is a bounded repair specification for the sole repository blocker established by the final independent Astra recheck of the integrated Gate-B run-authority candidate.

Audited integrated candidate:

`blue/gate-b-run-authority-repair-integration-2026-09-21@644da76eb0227be275b8e3448118dac0cc7096ca`

Integrated exact-head CI:

- `35598077120 = COMPLETED / SUCCESS`
- `35598816973 = COMPLETED / SUCCESS`

Independent Astra final review:

`astra/gate-b-run-authority-mechanisms-recheck-2026-09-21@41c3f291f46b7b5849bdb702c09ccefbeecde691`

Astra disposition:

`ASTRA_GATE_B_RUN_AUTHORITY_REVIEW = BLOCKED_REAL_DEFECT_LOCK_PATH_IDENTITY`

`PASS_REPOSITORY_EVIDENCE = NOT_ESTABLISHED`

A1-A10 are independently GREEN / NON_ISSUE after the prior repair. They are regression surfaces only for this mission, not reopened design work.

## 1. F11 finding

Classification:

`F11 = REAL_DEFECT / LOCK_PATH_IDENTITY`

Affected implementation:

`scripts/quant_gate_b_runctl.py :: Registry._locked()`

Independent reproduction established that one process can hold the original lock-file inode, the lock pathname can be replaced, and a second process can open the replacement inode and acquire a distinct `flock` domain essentially immediately.

Observed Astra discriminant:

`ASTRA_LOCK_REPLACEMENT_ACQUIRE_SECONDS = 0.000036`

Required invariant:

> Every registry mutation must serialize on one stable exclusivity domain for the registry identity, or fail closed before mutation whenever that exclusivity identity is ambiguous.

A replacement of the configured lock pathname must never create a second independently usable mutation domain.

## 2. Exact Builder branch and base

Create/use exactly:

`builder/gate-b-f11-lock-identity-repair-2026-09-21`

The branch MUST start from the exact audited integrated candidate:

`644da76eb0227be275b8e3448118dac0cc7096ca`

Do not base this repair on `blue/master-v2-2026-09-20`: that branch is governance authority but is a divergent lineage and does not contain the audited integrated implementation object.

Do not create a second F11 Builder branch.

## 3. Allowed changed paths

Builder implementation changes are limited to:

- `scripts/quant_gate_b_runctl.py`;
- one or more F11-specific test files, preferably `tests/test_gate_b_f11_lock_identity_repair.py`;
- `handoff/BUILDER_GATE_B_F11_LOCK_IDENTITY_REPAIR_2026-09-21.md`;
- `STATE.md` only if repository tooling requires a purely mechanical proof-inventory refresh.

The Blue spec and Builder mission files committed during dispatch are governance/mission authority and are not counted as Builder implementation changes.

No other implementation path is authorized.

## 4. Explicitly forbidden changes

Do NOT modify:

- `scripts/verify_gate_b_deployed_bytes.py` or M4 behavior;
- frozen V4 `src/` production code;
- Gate-B evidence schema semantics;
- activation/evidence-binding schemas unless Blue explicitly reopens scope;
- target-host files or runtime;
- workflows merely to make CI pass;
- Product / Antigravity implementation;
- F1, F5 or V4 prestage artifacts except read-only reference;
- A1-A10 behavior except where strictly necessary to preserve regression compatibility.

Do not weaken any existing fail-closed check.

## 5. Repair semantics

The implementation mechanism is Builder-owned, but it MUST satisfy all of the following:

1. Lock authority must not be defined only by whichever inode happens to be currently reachable through the replaceable `self.lock` pathname.
2. Replacing, unlinking/recreating, or racing that pathname must not permit two Registry mutation contexts to execute concurrently.
3. If stable lock identity cannot be established, the operation must raise `AuthorityError` or an equivalently fail-closed public error before registry mutation.
4. A one-time `O_NOFOLLOW`, `is_symlink()`, `lstat()`, or post-open comparison only to the current pathname is insufficient if it cannot detect a pre-open replacement that already created a second lock domain.
5. Ordinary uncontended locking must remain usable.
6. Process exit/crash must not leave a permanently reusable false authority state.
7. Existing freshness semantics remain post-lock: an activation that expires while waiting must still be rejected after the repaired exclusivity authority is obtained.
8. No repair may depend on target-host permissions as the sole repository proof of F11 closure.

A stable kernel-level exclusivity identity, or a repository-provable fail-closed identity mechanism, is acceptable. Blue does not prescribe the exact primitive.

## 6. Mandatory RED-before / GREEN-after F11 proof

Builder must add a deterministic real-process reproduction that is RED against the pre-implementation object and GREEN after the repair.

At minimum the committed test must exercise:

### F11-R1 — replacement before contender opens

1. process A enters the actual audited `Registry._locked()` context for the same registry;
2. A signals that the mutation lock is held;
3. while A still holds authority, the lock pathname is unlinked/replaced with a different regular-file inode;
4. process B invokes the actual `Registry._locked()` / mutation path;
5. B must either:
   - remain excluded until A releases, then proceed safely; or
   - fail closed before any mutation because identity is ambiguous.

B must never enter the mutation critical section concurrently with A.

### F11-R2 — replacement race while contention exists

Exercise pathname replacement while another Registry contender is blocked/acquiring. The contender must not transition into an independently lockable domain.

### F11-R3 — no-mutation-on-ambiguity

When the repair chooses fail-closed behavior, prove that no registry event, consumption event, evidence binding, or terminal event is appended by the rejected contender.

### F11-R4 — ordinary positive control

Two independent Registry processes with no pathname manipulation serialize correctly and both complete in order.

The RED-before evidence must identify the exact pre-implementation SHA tested. The GREEN-after evidence must identify the exact final Builder SHA tested.

## 7. Mandatory A1-A10 non-regression

The existing repaired A1-A10 suites must remain green.

At minimum run:

`PYTHONPATH=src python3 -m unittest discover -s tests -v`

and any repository status/proof-inventory check already required by the branch workflow.

Do not delete, skip, xfail, weaken or rename away prior negative controls to achieve green status.

Specifically preserve the real independent-process freshness contention behavior from A3 and the exact consumed-activation/evidence semantics from A5.

## 8. Builder handoff requirements

Final handoff:

`handoff/BUILDER_GATE_B_F11_LOCK_IDENTITY_REPAIR_2026-09-21.md`

It must record:

- exact branch;
- exact implementation predecessor SHA;
- exact final Builder SHA;
- changed paths;
- F11 mechanism chosen and why it cannot split on pathname replacement;
- exact RED-before command/result;
- exact GREEN-after command/result;
- full A1-A10 regression result;
- exact-head workflow ID/status once available;
- any residual repository-vs-target-host boundary;
- confirmation that target host was not touched.

Builder final status may be only:

`READY_FOR_INDEPENDENT_REVIEW`

or an explicit blocker.

Builder MUST NOT declare:

- `PASS_REPOSITORY_EVIDENCE`;
- Gate B PASS;
- target-host readiness;
- t0;
- Product readiness;
- real-capital authority.

## 9. Post-Builder flow

Required sequence:

`Builder F11 repair -> exact-head CI SUCCESS -> Blue reception/integration -> fresh independent Astra recheck of F11 + A1-A10 non-regression -> only Astra may establish PASS_REPOSITORY_EVIDENCE -> Blue may then return to Gate-B activation path`.

Green CI alone is not closure.

## 10. Safety state

```text
P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1
GATE_A_V4_REPOSITORY_DISPOSITION = PASS
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
