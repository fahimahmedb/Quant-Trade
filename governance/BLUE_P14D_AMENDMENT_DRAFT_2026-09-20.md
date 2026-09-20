# BLUE — Draft Amendment: Replace Fixed P14D With Hybrid P0 Qualification — 2026-09-20

## Status

**DRAFT ONLY — NOT AUTHORITATIVE — DO NOT USE TO DECLARE t0**

Current frozen authority remains:

`P0_CONTINUOUS_OBSERVATION_MIN = P14D`

`t0 = NOT DECLARED`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

This draft may be promoted only after all activation gates below are satisfied.

## Why an amendment is being considered

The fixed P14D rule was introduced as a conservative proxy for:
1. unattended continuity;
2. restart durability;
3. discovery fail-closed;
4. one full weekend;
5. a prospectively declared source-normal silence interval.

Blue's adversarial work has shown that a passive calendar wait does not itself force the important failure surfaces. Deliberate tests have already found calendar defects that a random 14-day period could miss:
- daily-index settlement anchored to UTC calendar date instead of EDGAR 22:00 ET close;
- federal holiday treated as an ordinary weekday reconciliation obligation;
- DST boundaries require exact elapsed-time handling.

Mature-system prior art supports a hybrid proof model:
- deterministic/fault-injected logical coverage;
- real target-host destructive entrance tests;
- bounded prospective real-source observation for environment/source properties simulation cannot prove.

The amendment preserves the evidence objective while removing arbitrary elapsed time as a substitute for direct testing.

## Activation gates

This draft **must not be promoted** unless all are true:

### A — repository/fault-compression gate
- one coherent exact-head branch includes all accepted calendar fixes and proofs;
- full unit suite green;
- explicit SEC P0 lane green;
- V1 E2E green;
- exact-head verification artifact green;
- clean tree;
- holiday authority is prospective and acquisition-fingerprinted;
- unbound future calendar year fails closed;
- business-day source error cannot be laundered as a holiday;
- DST spring/fall regressions green;
- long-history obligation audit green;
- no open repository-side capture/PIT/firewall blocker.

### B — target-host entrance gate
- immutable exact release and fixed service view verified;
- persistent state mount verified and absence fails closed;
- target filesystem primitives proven;
- loaded systemd fragment/drop-ins/effective values bound;
- interpreter/OpenSSL/runtime image bound;
- private requester identity present;
- exactly one global SEC requester-budget authority;
- active fingerprint == materialized fingerprint;
- actual systemctl stop/start, child failure, supervisor SIGKILL and controlled reboot completed pre-t0 with accountable evidence;
- no integrity latch.

### C0 — prospective t0 entrance
After A and B pass:
- candidate exact runtime is frozen;
- required live SEC calendar intervals are predeclared;
- entrance artifact is sealed;
- Blue explicitly declares one UTC timestamp:
  `t0 = <exact UTC instant>`.

No qualifying live evidence before this timestamp counts toward continuity qualification.

## Proposed superseding rule

Replace:

`P0_CONTINUOUS_OBSERVATION_MIN = P14D`

with:

`P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1`

where qualification requires all of:

### Gate A — accelerated/fault evidence
Repository-side deterministic proof over:
- scheduler obligations;
- backoff/cooldown timing;
- crash/restart boundaries;
- filesystem publication boundaries;
- malformed/truncated/error source states;
- source business calendar including weekends, federal holidays and DST;
- long-history one-obligation-to-one-resolution audit;
- fingerprint/integrity/firewall rules.

### Gate B — target-host proof
Actual target-host evidence over:
- mounts;
- filesystem semantics;
- loaded systemd/cgroup behavior;
- lifecycle stop/start/kill/reboot;
- runtime identity;
- private requester configuration;
- active/materialized fingerprint.

### Gate C — prospective live continuity window
The exact pinned target runtime must remain accountable continuously from declared `t0` through all required events:

1. at least one ordinary weekday EDGAR source-closed interval from 22:00 ET through 06:00 ET;
2. the required acquisition cycle after reopening;
3. one complete weekend source closure;
4. the first required post-weekend acquisition cycle after Monday reopening;
5. applicable daily-index reconciliation after the exact EDGAR-close + 30 elapsed-hour rule;
6. no unexplained scheduler obligation;
7. no unexplained heartbeat/attempt hole;
8. stable runtime/service/fingerprint bindings;
9. no invalidating intervention;
10. restricted before/after resource-stability verdict.

The interval stays open until all required events have occurred and been audited.

There is **no arbitrary minimum number of calendar days** once Gates A and B are complete.

A federal holiday may count as an additional prospectively declared source-normal silence event but does not replace the complete-weekend requirement unless a later amendment explicitly changes that requirement.

### Gate D — final retrospective audit
After Gate C events complete:
- run the durable one-obligation-to-one-resolution audit over `[t0, t_end]`;
- bind SHA/tree/input-tree digest/fingerprint/materialization/runtime/effective service/CI/lifecycle evidence;
- require zero integrity/firewall blockers;
- seal one restricted final artifact.

Only after Gate D passes may status become:

`P0_CONTINUOUS_SERVICE_STATE = QUALIFIED_UNDER_HYBRID_EVENT_BASED_V1`

This qualification says nothing by itself about scientific alpha, economic eligibility or real-capital authority.

## Reset / invalidation semantics

After t0, the live window resets or fails on:
- acquisition-critical fingerprint change;
- unbound systemd/config/runtime change;
- lost or substituted persistent state mount;
- manual mutation of acquisition-critical durable state;
- unauthorized/manual lifecycle replacement that invalidates continuity;
- unexplained due obligation;
- stale/foreign materialization accepted;
- integrity latch;
- source failure classified as source-normal silence without prospective calendar authority;
- firewall leak.

Read-only audit and unrelated Product development remain permitted when they cannot mutate the qualifying P0 runtime.

## Calendar authority

EDGAR source-normal closures must come from prospectively frozen SEC authority, not from observed HTTP failure.

Current 2026 authority:
- SEC EDGAR Calendar;
- SEC Accessing EDGAR Data / current filer manual.

The calendar is acquisition-critical and fingerprinted.

An unbound year fails closed until a new official calendar is reviewed, encoded and deployed through an explicit acquisition-critical deployment event.

## Relationship to the North Star

The amendment preserves P0 evidence quality while reducing non-informative calendar waiting.
It does not lower capture integrity, PIT reconstructability or firewall standards.
It frees calendar time for the rest of Quant to progress while the exact P0 runtime still proves the irreducible real-environment events.

The terminal objective remains long-run net wealth growth after real frictions; qualification time is instrumental, not itself a goal.

## Promotion procedure

If activation gates pass:

1. Red Team this draft one final time against the exact coherent Gate A head and target-host contract.
2. Create a new authoritative governance file clearly marked as superseding the P14D clauses.
3. Update every checkpoint that still states fixed P14D as active.
4. Commit the amendment before any t0 declaration.
5. Run exact-head CI on the governance-amended candidate if the amendment changes fingerprinted inputs; otherwise bind the amendment commit separately without pretending it was the tested acquisition SHA.
6. Re-materialize target fingerprint after any acquisition-critical code merge.
7. Only then perform C0 and explicitly declare t0.

Until step 4 is complete, this file has no authority.
