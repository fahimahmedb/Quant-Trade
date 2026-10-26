# BLUE — TARGET-HOST RUNBOOK RECONCILIATION PLAN — 2026-09-21

## Status

`RUNBOOK_RECONCILIATION = PREPARED / NOT_APPLIED`

`HYBRID_GATE_B_EXECUTION = NOT_AUTHORIZED`

`t0 = NOT DECLARED`

Purpose: identify exactly what must change in the current target-host
contract/runbook after the hybrid amendment is promoted and the final
replacement candidate is Blue-approved.

Do not edit the current operational authority prematurely.

## 1. Why reconciliation is mandatory

Current files:

- `governance/TARGET_HOST_RODAGE_ENTRANCE_CONTRACT_2026-09-20.md`;
- `governance/TARGET_HOST_P0_RODAGE_RUNBOOK_2026-09-20.md`.

They are historically useful but currently contain two stale assumptions:

### STALE-001 — hard-pinned rejected V3 candidate

They pin:
`2da079d8ad75c69eb3fc2990c512735cb4bdc02b`.

That candidate was later rejected for target-host entrance by a REAL_DEFECT.

The replacement candidate currently frozen for independent review is:
`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`.

No operator may substitute V4 into V3 commands informally.
The authoritative runbook must be reissued against the exact Blue-approved
candidate after independent review.

### STALE-002 — old rodage/t0 ordering

The current contract says entrance/rodage completes and Blue later chooses t0.

The hybrid candidate instead requires:

`T0_BINDING_MODE = PRECOMMITTED_NEXT_AUTHORIZED_QUALIFYING_LAUNCH`.

The unique launch identity is fixed before outcomes, and the launch event's
externally attributable UTC timestamp becomes t0.

This eliminates retrospective timestamp selection.

## 2. Sections to preserve substantively

The reconciled runbook should preserve or strengthen:

- immutable release topology;
- persistent state mount;
- fail-closed missing mount;
- SHA/tree/input-tree binding;
- loaded systemd authority;
- runtime/Python/OpenSSL identity;
- durable-state anti-pre-seeding inventory;
- single writer / global SEC requester budget;
- filesystem primitives;
- one-use deployment authority;
- destructive target-host lifecycle tests;
- restricted evidence boundary;
- fail-closed invalidators.

These are still required under the hybrid method.

## 3. Sections to change after promotion

### R1 — candidate variables

Replace every hard-coded V3 branch/SHA/run/audit reference with the exact
Blue-approved replacement lineage.

Do not use branch-head resolution at execution time.

### R2 — Gate B terminology

Rename the pre-t0 target-host qualification phase explicitly to
`GATE_B`.

The Gate-B artifact must remain distinct from the later Gate-C live evidence.

### R3 — destructive-test state hygiene

After destructive/offline Gate-B tests:
- stop qualifying service;
- separate/remove synthetic destructive-test state according to contract;
- rebind the exact future qualifying state reservoir;
- verify no stale deployment authority;
- verify no ambiguous lifecycle records;
- verify no integrity latch;
- seal a final entrance artifact against the actual Gate-C state.

### R4 — precommit before launch

Before service start, record:
- candidate SHA/tree/input-tree digest;
- materialized/active fingerprint;
- effective service digest;
- persistent-state identity;
- Gate-B artifact digest;
- fresh one-use launch authority identity;
- prospective Gate-C source-calendar event plan;
- explicit statement that the next single launch consuming that authority is
  the unique t0 event.

### R5 — t0 materialization

Delete the old semantic:
“rodage succeeds, then Blue later selects t0.”

Replace with:
- exactly one precommitted qualifying launch;
- externally attributable launch timestamp = t0;
- no matching launch / multiple launch / wrong binding / ambiguous provenance
  => NO_T0.

### R6 — Gate C starts immediately

The reconciled runbook must transition immediately from the t0 launch into
the prospective Gate-C event window.

No later good sub-window may be selected after observing results.

### R7 — invalidation/restart

If Gate C invalidates:
- preserve failed interval;
- classify cause;
- do not move t0 forward inside the same interval;
- Blue decides re-entry scope;
- any new t0 requires a new precommit and qualifying launch.

### R8 — Gate D

Add the final retrospective binder:
- Gate A;
- Gate B artifact;
- precommitted t0 event;
- full Gate C interval;
- final obligation audit;
- resource-health verdicts;
- exact runtime/service/fingerprint lineage.

Only separate Blue disposition can then set:
`P0_CONTINUOUS_SERVICE_STATE = QUALIFIED_UNDER_HYBRID_EVENT_BASED_V1`.

### R9 — post-qualification surveillance

After successful Gate D:
`P0_POST_QUALIFICATION_SURVEILLANCE = ACTIVE`.

New late evidence can reopen current eligibility without rewriting the
historical qualification artifact.

## 4. Operator safety

The reconciled runbook must keep a clear split between:

READ-ONLY PREFLIGHT
TARGET-HOST DESTRUCTIVE GATE B
POST-GATE-B SANITIZATION
PRECOMMIT
ONE QUALIFYING LAUNCH / t0
GATE C OBSERVATION
GATE D CLOSURE

No command block should make a destructive action look like a harmless
preflight.

Private requester identity and restricted SEC acquisition evidence must not
be emitted to public logs.

## 5. Current execution prohibition

Until all of the following are true:

- hybrid amendment authoritative;
- final candidate independently reviewed;
- Blue final candidate disposition committed;
- reconciled runbook issued against exact lineage;

the operator must NOT use this plan to declare t0 or shorten P14D.

Current state:

`RUNBOOK_RECONCILIATION = PREPARED / NOT_APPLIED`

`GATE_B = NOT_STARTED_FOR_FINAL_CANDIDATE`

`t0 = NOT DECLARED`
