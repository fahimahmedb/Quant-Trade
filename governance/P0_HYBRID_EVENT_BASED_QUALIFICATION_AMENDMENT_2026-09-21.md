# P0 HYBRID EVENT-BASED QUALIFICATION AMENDMENT — 2026-09-21

## Status

**AUTHORITATIVE — PROMOTED BY BLUE**

`P14D_GOVERNANCE_STATUS = HISTORICAL / SUPERSEDED_FOR_FUTURE_QUALIFICATION`

`t0 = NOT DECLARED`

This document is the authoritative Blue amendment for future P0 continuity qualification.

It incorporates the final Blue Red Team corrections in:
`governance/BLUE_P14D_FINAL_RED_TEAM_2026-09-21.md`.

## 1. Supersession

This amendment replaces for future qualification:

`P0_CONTINUOUS_OBSERVATION_MIN = P14D`

with:

`P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1`

The new rule qualifies explicit properties, not elapsed time for its own sake.

## 2. Gate A — accelerated/fault repository proof

On one exact candidate/evidence lineage, require reproducible proof for:
- scheduler obligations and timing boundaries;
- backoff/cooldown semantics;
- crash/restart boundaries;
- filesystem publication logic;
- malformed/truncated/error source states;
- business calendar including weekend/holiday/DST/unbound-year fail-closed;
- long-history one-obligation-to-one-resolution;
- fingerprint/integrity/firewall semantics;
- the complete durability fault matrix.

Every residual must be classified explicitly as repository-covered, TARGET_HOST_ONLY, LIVE_ONLY or MISSING_PROOF.

No unresolved repository blocker may be laundered into Gate B or Gate C merely to save calendar time.

## 3. Gate B — actual target-host entrance proof

Before t0, on the real target host and exact pinned candidate, require:
- immutable exact release and fixed service view;
- persistent state mount and fail-closed mount absence;
- required filesystem semantics;
- loaded systemd fragment/drop-ins/effective values;
- runtime/interpreter/OpenSSL binding;
- requester identity availability without publication;
- exactly one global requester-budget authority;
- active fingerprint == materialized fingerprint;
- accountable stop/start, child failure, supervisor SIGKILL and controlled reboot;
- no integrity latch or unexplained pre-seeded acquisition-critical authority/state.

Gate B produces one restricted exact-host entrance artifact.

Gate B PASS does not itself declare t0.

## 4. C0 — prospective t0 binding

Use:

`T0_BINDING_MODE = PRECOMMITTED_NEXT_AUTHORIZED_QUALIFYING_LAUNCH`

Before any qualifying outcome exists, Blue must durably precommit:
- exact candidate SHA/tree/input-tree identity;
- acquisition fingerprint/materialization;
- effective service digest;
- persistent-state identity;
- one-use qualifying launch/deployment authority;
- the next single qualifying launch consuming that authority as the unique t0 event;
- the prospectively expected source-calendar events needed by Gate C.

The exact UTC `t0` is the externally attributable timestamp of that precommitted qualifying launch event.

No matching launch, multiple launches, wrong binding or ambiguous provenance => `NO_T0`.

t0 may never be chosen retrospectively from an already-observed good interval.

## 5. Gate C — prospective live event window

The exact pinned target runtime must remain continuously accountable from t0 through all of:

1. one prospectively known ordinary source-closed interval;
2. a subsequent expected live acquisition cycle;
3. one complete weekend source closure;
4. the first required post-weekend acquisition cycle;
5. applicable daily-index reconciliation after the bound settlement rule;
6. every prospective scheduler obligation accounted for;
7. no unexplained heartbeat/attempt hole;
8. stable runtime/service/fingerprint/state-mount bindings;
9. no invalidating intervention;
10. restricted before/after resource-health verdicts.

Gate C is event-based. No shorter or longer number of elapsed days is sufficient by itself.

A holiday may provide additional prospectively declared source-normal silence but does not silently replace the complete-weekend requirement.

## 6. Gate D — retrospective closure

After all Gate C events occur, bind one restricted final artifact containing:
- candidate SHA/tree/input-tree digest;
- CI identity;
- acquisition fingerprint/materialization;
- runtime/interpreter/OpenSSL identity;
- effective configuration/service digest;
- Gate A evidence;
- Gate B entrance artifact;
- t0 event binding;
- full Gate C interval;
- lifecycle/deployment authority evidence;
- final one-obligation-to-one-resolution audit;
- before/after resource-health verdicts.

Gate D must fail closed on any missing or mismatched proof domain.

Only a separate Blue disposition after Gate D may set:

`P0_CONTINUOUS_SERVICE_STATE = QUALIFIED_UNDER_HYBRID_EVENT_BASED_V1`.

## 7. Reset / invalidation semantics during Gate C

Gate C fails/resets on:
- acquisition-critical fingerprint change;
- unbound service/config/runtime change;
- lost/substituted state mount;
- unauthorized acquisition-critical durable-state mutation;
- unauthorized lifecycle replacement;
- unexplained due obligation;
- unexplained heartbeat/attempt hole;
- stale/foreign materialization accepted;
- integrity latch;
- source failure classified as normal silence without prospective authority;
- visibility/firewall leak.

Read-only audit and unrelated Product work remain allowed only when they cannot mutate the qualifying runtime.

## 8. Residual elapsed-time value and post-qualification surveillance

This amendment does not claim that real elapsed time has zero value.

It states that no calibrated evidence supports fourteen days as a unique fixed threshold for the enumerated qualification properties.

After Gate D:

`P0_POST_QUALIFICATION_SURVEILLANCE = ACTIVE`

must remain in force.

A later integrity/liveness/runtime/resource defect is new evidence and requires a new Blue disposition. It may reopen current P0 eligibility without rewriting the historical qualification artifact.

## 9. Separation of proof domains

Qualification under this rule proves only the defined P0 continuity/capture properties for the exact evidence lineage.

It does NOT prove:
- scientific alpha;
- economic eligibility;
- Product integration readiness;
- Gate B for another candidate;
- real-capital authorization.

`REAL_CAPITAL_AUTHORIZED = FALSE` unless separately superseded.

## 10. Promotion evidence binding

Exact promotion evidence:
- V4 SHA: `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`;
- Git tree: `4d15ef6f471213ee6ab56337b555d2906ef9bf16`;
- verified input-tree: `sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2`;
- selected V4 CI: `35536353538 = SUCCESS`;
- independent V4 Astra: `afe25984b0ddd261fda143d858106c3c71e45149`;
- independent V4 CI: `35545297473 = SUCCESS`, `35545297451 = SUCCESS`;
- Builder restart-burst repair: `1fa82a75485661bf9bbb3de10b925126397dfec5`;
- Builder repair CI: `35549017908 = SUCCESS`;
- targeted Astra: `61facacdcdc499bd3e6680644c75c97fcff22656`;
- targeted Astra CI: `35551073229 = SUCCESS`;
- Astra targeted verdict: `PASS_REPOSITORY_EVIDENCE`;
- Blue final reception: `0f4d6227c129a53793fb186db6a618d2a453e3ee`;
- final consistency: `PASS`.

Current state after this amendment:
```text
P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1
P14D_GOVERNANCE_STATUS = HISTORICAL / SUPERSEDED_FOR_FUTURE_QUALIFICATION
TARGET_HOST_READY = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```

This amendment does not prove target-host entrance, economic edge or capital readiness.
