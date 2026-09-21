# BLUE — P0 POST-ASTRA-GREEN EXECUTION CONTROL PLAN — 2026-09-21

## 0. Purpose and status

`PLAN_STATUS = PREPARED / NON_AUTHORIZING`

`ASTRA_FINAL_CI_REQUIRED = 35551073229 -> COMPLETED / SUCCESS`

This is the single Mission-Control execution plan for the phase that starts
when the final targeted Astra CI becomes green.

It consolidates, but does not supersede before activation:
- the final Astra reception;
- the hybrid consistency precheck;
- the atomic promotion dry-run;
- the Gate-B activation presealing;
- the Gate-B entrance contract candidate;
- the Gate-B-to-Gate-C runbook candidate.

No authority changes merely because this plan exists.

## 1. Highest authority / invariants

Architectural authority:
`QUANT_NORTH_STAR.md`

North Star blob rechecked:
`8295041a8d253636d8f8aab941b811dce64939d9`

Terminal objective remains:
real long-run net economic gain after real frictions through repeatable
edge discovery, selection, sizing, execution, monitoring, retirement and
replacement.

Frozen P0 production candidate:
`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Until the relevant phase changes them explicitly:

```text
P14D_PROMOTION_READY = FALSE
P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED
TARGET_HOST_READY = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```

## 2. Roles

### Blue / Mission Control
Owns every state transition, final reception, promotion, activation,
Gate-B disposition, t0 precommit, Gate-D disposition and P0 exit.

### Astra
Targeted independent review is complete substantively.
No new Astra mission is required unless contradictory evidence appears.

Current final Astra delivery:
`61facacdcdc499bd3e6680644c75c97fcff22656`

Substantive verdict:
`ASTRA_RESTART_BURST_RECHECK = PASS_REPOSITORY_EVIDENCE`

### Builder
No implementation mission is active after this point.
Builder re-enters only on a reproduced concrete defect or an explicit
post-P0 Product mission.

### Target-host operator
May mutate the target host only under one sealed Blue activation artifact
with explicit mutation permissions and one unique `GATE_B_RUN_ID`.

### Product / integration work
Remains non-authoritative and must not mutate the qualifying runtime until
P0 exit. Read-only preparation may proceed only under the parallel-prestage
rules defined separately.

## 3. Critical path overview

```text
ASTRA FINAL CI GREEN
        |
        v
P1 BLUE FINAL RECEPTION
        |
        v
P2 FINAL CONSISTENCY CHECK
        |
        v
P3 ATOMIC HYBRID PROMOTION
        |
        v
P4 GATE-B ACTIVATION SEAL
        |
        v
P5 GATE-B TARGET-HOST EXECUTION
        |
        v
P6 BLUE GATE-B RECEPTION
        |
        v
P7 t0 PRECOMMIT + ONE-USE LAUNCH
        |
        v
P8 GATE-C REAL EVENT WINDOW
        |
        v
P9 GATE-D RETROSPECTIVE CLOSURE
        |
        v
P10 P0 EXIT
        |
        v
PRODUCT VERTICAL SHADOW LOOP
```

No phase may be skipped.

## 4. P0 — activation condition

Required external event:

`35551073229 = COMPLETED / SUCCESS`

Exact Astra SHA:
`61facacdcdc499bd3e6680644c75c97fcff22656`

If the run fails or the Astra branch moves:
- STOP;
- do not finalize Blue reception;
- do not execute promotion;
- classify the contradiction first.

## 5. P1 — Blue final Astra reception

Owner:
`BLUE`

Input:
- Builder SHA `1fa82a75485661bf9bbb3de10b925126397dfec5`;
- Builder CI `35549017908 = SUCCESS`;
- Astra SHA `61facacdcdc499bd3e6680644c75c97fcff22656`;
- Astra handoff blob `85d989fa3b8d5c7c6bbf4ef0b70361fe608e2124`;
- Astra exact-head CI `35551073229 = SUCCESS`.

Action:
finalize:
`handoff/BLUE_ASTRA_RESTART_BURST_FINAL_RECEPTION_2026-09-21.md`

Required resulting state:
```text
FINAL_INDEPENDENT_FAULT_MATRIX_REVIEW = PASS
RESTART_BURST_LIMIT_REPOSITORY_MISSING_PROOF = CLOSED
UNRESOLVED_REPOSITORY_MISSING_PROOF = 0
```

Preserve explicitly:
- cross-Python-build report-digest limitation;
- harness input-tree digest limitation;
- physical systemd enforcement = TARGET_HOST_ONLY.

STOP on any contradictory same-SHA evidence.

## 6. P2 — final hybrid consistency check

Owner:
`BLUE`

Base document:
`governance/BLUE_HYBRID_PROMOTION_FINAL_CONSISTENCY_PRECHECK_2026-09-21.md`

Action:
rerun every live binding against current blobs and exact immutable refs.

Mandatory checks:
1. North Star unchanged or explicitly reconciled;
2. V4 candidate SHA/tree/input-tree unchanged;
3. Builder and Astra exact refs final;
4. no repository MISSING_PROOF;
5. no repository REAL_DEFECT;
6. all 19 matrix properties covered by hybrid method;
7. fingerprint/calendar authority bound;
8. non-blocking evidence debt preserved;
9. no target-host-only property laundered into repository PASS;
10. no Product/capital authority implied.

Output:
`FINAL_CONSISTENCY_PRECHECK = PASS`

If not PASS:
STOP before promotion.

## 7. P3 — atomic hybrid promotion

Owner:
`BLUE`

Primary execution source:
`governance/BLUE_HYBRID_PROMOTION_ATOMIC_DRY_RUN_2026-09-21.md`

Transaction must create/promote as one coherent authority set:

1. `governance/P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT_2026-09-21.md`
2. `governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md`
3. `governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md`
4. `governance/P0_T0_PRECOMMIT_TEMPLATE_2026-09-21.md`
5. `governance/BLUE_GATE_B_ACTIVATION_TEMPLATE_2026-09-21.md`
6. `governance/TARGET_HOST_GATE_B_EVIDENCE_SCHEMA_2026-09-21.json`
7. `governance/TARGET_HOST_V4_RELEASE_MATERIALIZATION_2026-09-21.md`
8. update `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`
9. update `handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`
10. close applicable promotion-checklist items.

Required post-transaction state:
```text
P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1
P14D_GOVERNANCE_STATUS = HISTORICAL / SUPERSEDED_FOR_FUTURE_QUALIFICATION
GATE_A_V4_REPOSITORY_DISPOSITION = PASS

TARGET_HOST_READY = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED

PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```

Promotion changes method/governance authority only.
It does not touch the target host.

## 8. P4 — Gate-B activation seal

Owner:
`BLUE`

Base:
`governance/BLUE_GATE_B_ACTIVATION_PRESEAL_2026-09-21.md`

Create one NEW sealed activation artifact after promotion.

It must bind:
- authoritative hybrid-amendment ref/digest;
- Gate-B contract ref/digest;
- Gate-B runbook ref/digest;
- evidence-schema ref/digest;
- release-materialization ref/digest;
- exact V4 SHA/tree/input-tree;
- unique `GATE_B_RUN_ID`;
- attempt number;
- target-host identity;
- time/NTP evidence;
- evidence-retention location;
- state-root identity;
- network/proxy/TLS binding;
- resource baseline;
- explicit mutation permissions.

Default deny remains mandatory.

Especially:
`ALLOW_REAL_SEC_NETWORK = FALSE`
unless separately and explicitly required and authorized.

Only this sealed artifact may set:
`GATE_B_MUTATION_AUTHORIZED = TRUE`

## 9. P5 — Gate-B target-host execution

Owner:
target-host operator under Blue activation.

Target runtime:
- immutable release under
  `/opt/quant-releases/4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072/`;
- persistent P0 state authority remains separate;
- admin/Builder clone is not the runtime authority.

One immutable `GATE_B_RUN_ID` for the attempt.

Execute the authoritative runbook exactly.

Evidence domains include:
- release materialization;
- mount/state-root authority;
- filesystem semantics;
- loaded systemd effective configuration;
- restart-burst behavior;
- runtime/interpreter/OpenSSL;
- requester identity availability;
- global budget/writer authority;
- active/materialized fingerprint match;
- stop/start;
- child death;
- supervisor SIGKILL;
- controlled reboot where authorized;
- host time;
- retention;
- network binding;
- resources;
- no unexplained pre-seeded acquisition authority.

First mandatory failure:
`GATE_B_RUN_STATUS = FAILED_TERMINAL`

Retry requires:
- new Blue decision;
- new activation;
- new `GATE_B_RUN_ID`.

No evidence cherry-picking across attempts.

## 10. P6 — Blue Gate-B reception

Owner:
`BLUE`

Input:
one schema-valid restricted Gate-B evidence artifact.

Blue independently verifies:
- correct run ID;
- correct activation digest;
- correct candidate;
- all mandatory domains PASS for overall PASS;
- no hidden failed attempt merged into current evidence;
- no unapproved real-network activity;
- evidence retained and hash-addressable.

Allowed state:
`GATE_B = PASS`
or
`GATE_B = BLOCKED`

Gate-B PASS still means:
`t0 = NOT_DECLARED`

## 11. P7 — t0 precommit and one-use qualifying launch

Owner:
`BLUE`

Only after Gate-B PASS.

Seal a NEW t0 precommit containing:
- exact candidate SHA/tree/input-tree;
- materialized acquisition fingerprint;
- effective service digest;
- persistent-state identity;
- expected source-calendar events;
- one-use launch authority;
- the next unique qualifying launch as the only eligible t0 event.

Required mode:
`T0_BINDING_MODE = PRECOMMITTED_NEXT_AUTHORIZED_QUALIFYING_LAUNCH`

Then execute exactly one matching qualifying launch.

Its externally attributable lifecycle UTC timestamp becomes `t0`.

Wrong, duplicate, missing or ambiguous launch:
`NO_T0`.

No retrospective reselection.

## 12. P8 — Gate-C prospective real-event window

Owner:
runtime + Blue monitoring.

From t0, keep the exact pinned runtime continuously accountable through:

1. a prospectively known ordinary source-closed interval;
2. subsequent expected live acquisition;
3. one complete weekend source closure;
4. first required post-weekend acquisition;
5. applicable daily-index reconciliation under the bound 30h rule;
6. all scheduler obligations accounted for;
7. no unexplained heartbeat/attempt hole;
8. stable runtime/service/fingerprint/state-mount identity;
9. no invalidating intervention;
10. before/after resource-health evidence.

Gate C is event-based, not a fixed-day count.

Any invalidating event:
Gate C fails/resets according to the authoritative amendment.

## 13. P9 — Gate-D retrospective closure

Owner:
`BLUE`, with independent review only if a material ambiguity exists.

Bind one final restricted artifact containing:
- candidate SHA/tree/input-tree;
- CI identities;
- fingerprint/materialization;
- runtime identity;
- effective service digest;
- Gate-A evidence;
- Gate-B artifact;
- t0 binding;
- full Gate-C interval;
- lifecycle/deployment-authority evidence;
- one-obligation-to-one-resolution audit;
- resource verdicts.

Fail closed on missing/mismatched proof domain.

Only Blue may then set:
`P0_CONTINUOUS_SERVICE_STATE = QUALIFIED_UNDER_HYBRID_EVENT_BASED_V1`

## 14. P10 — explicit P0 exit

Owner:
`BLUE`

Create a durable P0-exit checkpoint.

Required conceptual state:
```text
P0_QUALIFICATION = CLOSED
P0_POST_QUALIFICATION_SURVEILLANCE = ACTIVE
PRODUCT_INTEGRATION = UNPAUSED
NEXT_PRIMARY_OBJECTIVE = FIRST_END_TO_END_ECONOMIC_SHADOW_LOOP
REAL_CAPITAL_AUTHORIZED = FALSE
```

P0 becomes maintenance/surveillance, not the primary project frontier.

A new broad P0 hardening program is forbidden unless a concrete reproduced
defect reopens eligibility.

## 15. Parallelization policy

### Before final Astra CI green
Allowed:
- documentation/preparation only.
Forbidden:
- promotion;
- target-host mutation;
- Gate-B activation.

### After promotion but before Gate-B PASS
Allowed:
- read-only Product integration analysis;
- no merge/deploy into qualifying runtime.

### During Gate-C calendar waiting
Allowed and encouraged:
- read-only/prestaged post-P0 Product integration work on non-runtime branches;
- compare canonical Forward/Economic semantics;
- prepare first vertical shadow-loop integration plan;
- prepare tests/fixtures that do not touch qualifying runtime.

Forbidden:
- mutate the qualifying runtime;
- change candidate fingerprint/service/config/state mount;
- merge Product code into the live P0 release;
- let Product work alter t0/Gate-C evidence.

## 16. No-new-P0 rule

After repository closure and especially after P0 exit:

Do not start a new horizontal infrastructure mission merely because an
improvement is desirable.

Require one of:
1. reproduced integrity/runtime defect;
2. concrete false-positive channel;
3. concrete economic blocker;
4. mandatory security/safety defect;
5. explicit owner architecture revision.

Otherwise prioritize the vertical economic loop.

## 17. Critical-path scoreboard

```text
[ ] Astra final exact-head CI green
[ ] P1 Blue final reception
[ ] P2 final consistency PASS
[ ] P3 hybrid promotion
[ ] P4 Gate-B activation sealed
[ ] P5 Gate-B execution
[ ] P6 Gate-B Blue PASS
[ ] P7 t0 precommit + qualifying launch
[ ] P8 Gate-C required events complete
[ ] P9 Gate-D PASS
[ ] P10 P0 EXIT
[ ] Product vertical shadow loop unpaused
```
